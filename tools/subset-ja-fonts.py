#!/usr/bin/env python3
"""
Subset the Japanese webfonts to the glyphs this site actually uses.

Why this exists
---------------
Noto Sans JP and M PLUS 1p are CJK faces. Served whole they are ~6 MB across
~250 unicode-range chunks, and the @font-face CSS describing those chunks is
~300 KB on its own — which is a render-blocking stylesheet bigger than most
sites' entire payload. The site's Japanese copy is a few pages, so almost all
of that is glyphs no visitor will ever see.

This script reads every built Japanese page, collects the characters that
actually appear, and cuts the fonts down to them.

Coverage and its one failure mode
---------------------------------
The subset is the union of:

  * every character on a built /ja/ page, plus the Japanese schedule JSON the
    calendar injects at runtime (it is not in the HTML, so scanning pages
    alone would miss it)
  * all hiragana and katakana, CJK punctuation, and ASCII, whether used or not

The kana are insurance. They are cheap — a couple of hundred glyphs — and they
mean ordinary copy edits do not need a re-subset. New *kanji* are the failure
mode: a kanji not in the subset falls back to the reader's system Japanese
font, which is a visible mismatch rather than tofu, but a mismatch all the
same.

So: re-run this after adding or editing Japanese copy.

    RUBYOPT="-E utf-8:utf-8" bundle exec jekyll build   # refresh _site first
    python3 tools/subset-ja-fonts.py

It needs fonttools and brotli, which are not project dependencies — install
them into a throwaway venv rather than the system Python. The script prints
what it wrote and how much it saved, and rewrites styles/fonts-ja.css.
"""

import glob
import html
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "ja-font-sources")
OUT = os.path.join(ROOT, "fonts")
CSS = os.path.join(ROOT, "_includes", "fonts-ja.css")

FACES = [
    # (source file,               output name,            family,         weight)
    ("noto-sans-jp-400.woff2", "noto-sans-jp-400.woff2", "Noto Sans JP", 400),
    ("noto-sans-jp-700.woff2", "noto-sans-jp-700.woff2", "Noto Sans JP", 700),
    ("m-plus-1p-900.woff2",    "m-plus-1p-900.woff2",    "M PLUS 1p",    900),
]


def ranges(*pairs):
    out = set()
    for lo, hi in pairs:
        out |= {chr(c) for c in range(lo, hi + 1)}
    return out


def collect_chars():
    """Characters on Japanese pages, plus the always-included safety margin."""
    chars = set()
    sources = glob.glob(os.path.join(ROOT, "_site", "ja", "**", "*.html"), recursive=True)

    # _data/*.yml too: the timetable, calendar, venue and fee pages render their
    # Japanese from data, and a label that only appears in a hidden panel or is
    # written by script would otherwise be missed by an HTML-only scan. This
    # replaced training-schedule-ja.json, a FullCalendar-era file that no longer
    # matched the live schedule.
    #
    # Two of them are generated and must be skipped. `imgw.yml` holds image
    # paths, and a gallery filename can carry Japanese — those are URL bytes,
    # never glyphs on a page, and subsetting for them grows all three faces to
    # draw kanji nothing displays. `assets.yml` is hex.
    GENERATED = {"imgw.yml", "assets.yml"}
    sources += sorted(p for p in glob.glob(os.path.join(ROOT, "_data", "*.yml"))
                      if os.path.basename(p) not in GENERATED)

    scanned = 0
    for path in sources:
        if not os.path.exists(path):
            continue
        scanned += 1
        text = open(path, encoding="utf-8", errors="replace").read()
        if path.endswith(".html"):
            text = re.sub(r"<(script|style)\b.*?</\1>", "", text, flags=re.S | re.I)
            text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        chars |= set(text)

    if scanned == 0:
        sys.exit("No Japanese pages found. Build the site first (jekyll build).")

    used = {c for c in chars if ord(c) >= 0x20}
    chars |= ranges(
        (0x0020, 0x007E),  # ASCII
        (0x00A0, 0x00FF),  # Latin-1, for the romanised Japanese
        (0x2000, 0x206F),  # general punctuation — en/em dashes, ellipsis
        (0x3000, 0x303F),  # CJK punctuation
        (0x3041, 0x309F),  # hiragana
        (0x30A0, 0x30FF),  # katakana
        (0xFF01, 0xFF5E),  # fullwidth forms
        (0xFF61, 0xFF9F),  # halfwidth kana
    )
    chars = {c for c in chars if ord(c) >= 0x20}
    return chars, used, scanned


def uncovered(font_path, chars):
    """Visible characters the built face has no glyph for."""
    from fontTools.ttLib import TTFont

    font = TTFont(font_path)
    cmap = set()
    for table in font["cmap"].tables:
        cmap |= set(table.cmap.keys())
    # U+202C and friends are invisible bidi controls; fonts legitimately omit
    # them and nothing is drawn either way.
    invisible = {0x200B, 0x200E, 0x200F, 0x202A, 0x202B, 0x202C, 0x202D, 0x202E, 0xFEFF}
    return sorted(
        c for c in chars
        if ord(c) not in cmap and ord(c) not in invisible and ord(c) > 0x20
    )


def main():
    try:
        from fontTools import subset  # noqa: F401
        import brotli  # noqa: F401
    except ImportError:
        sys.exit(
            "Needs fonttools and brotli:\n"
            "  python3 -m venv /tmp/fontenv && /tmp/fontenv/bin/pip install fonttools brotli\n"
            "  /tmp/fontenv/bin/python tools/subset-ja-fonts.py"
        )

    chars, used, scanned = collect_chars()
    print(f"scanned {scanned} Japanese sources -> {len(used)} characters in use, "
          f"{len(chars)} requested (the rest is the kana safety margin)")

    unicodes = ",".join(f"U+{ord(c):04X}" for c in sorted(chars))
    before = after = 0
    blocks = []

    for src_name, out_name, family, weight in FACES:
        src = os.path.join(SRC, src_name)
        dst = os.path.join(OUT, out_name)
        if not os.path.exists(src):
            sys.exit(f"Missing source font {src}. See the README in {SRC}.")

        subprocess.run(
            [sys.executable, "-m", "fontTools.subset", src,
             f"--unicodes={unicodes}",
             "--layout-features=*",
             "--flavor=woff2",
             f"--output-file={dst}"],
            check=True,
        )
        b, a = os.path.getsize(src), os.path.getsize(dst)
        before += b
        after += a

        # Report anything the page needs that the face cannot draw. Usually
        # this means the source font has no such glyph rather than that the
        # subset dropped it — U+2715 (the ✕ in the collaboration course
        # titles) is not in Noto Sans JP at all, and never was, so it falls
        # back to a system font here exactly as it did before subsetting.
        # Only characters genuinely present on a page are reported; the kana
        # safety margin is not, since a font lacking a glyph nobody uses is
        # not a problem. A character appearing here that you expected to
        # render is the signal to widen the source subsets — see the README
        # in ja-font-sources/.
        gaps = uncovered(dst, used)
        note = f"  [no glyph for {''.join(gaps)}]" if gaps else ""
        print(f"  {out_name:<26} {b/1024/1024:>6.2f} MB -> {a/1024:>7.1f} KB{note}")

        blocks.append(
            "@font-face {\n"
            f"  font-family: '{family}';\n"
            "  font-style: normal;\n"
            f"  font-weight: {weight};\n"
            "  font-display: swap;\n"
            f"  src: url(/fonts/{out_name}) format('woff2');\n"
            "}"
        )

    header = (
        "/* Japanese webfaces, self-hosted and subset to the glyphs this site\n"
        "   uses. GENERATED by tools/subset-ja-fonts.py — do not hand-edit, and\n"
        "   re-run that script after changing Japanese copy.\n"
        "\n"
        "   Inlined into the <head> of /ja/ pages by _includes/header.html. At\n"
        "   well under a kilobyte it is cheaper in the document than as a file:\n"
        "   as a separate stylesheet it was render-blocking and cost a round\n"
        "   trip to deliver three @font-face rules. */\n\n"
    )
    open(CSS, "w", encoding="utf-8").write(header + "\n\n".join(blocks) + "\n")

    print(f"\nfonts:  {before/1024/1024:.2f} MB -> {after/1024:.1f} KB")
    print(f"wrote   {os.path.relpath(CSS, ROOT)} ({os.path.getsize(CSS)} bytes, {len(FACES)} faces)")


if __name__ == "__main__":
    main()
