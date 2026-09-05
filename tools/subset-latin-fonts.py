#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Subset the four Noto Sans `latin-ext` faces to the characters the site uses.

WHY. These are Google's originals and they carry the whole of Latin Extended-A
and B, IPA extensions, Latin Extended Additional and a run of currency signs —
62 to 66 KB each, against 13 KB for the corresponding `latin` face. The site
uses FOUR characters out of all of it: ō ū Ō ī, the macrons in the romanised
Japanese. A page pays for the whole face the moment it paints one of them in
that style, so Lighthouse measured 106 KB of font on the home page and 88 KB on
/ura/ against 26 KB everywhere else.

This is the same trick `tools/subset-ja-fonts.py` plays on the CJK faces, for
the same reason and with the same safety margin: keep what is in use, then keep
a great deal more than that, so an ordinary copy edit never has to think about
fonts.

WHAT IS KEPT

  * every character the built site and _data/*.yml actually use from the range
  * ALL of Latin Extended-A, U+0100-017F — 128 codepoints covering the accented
    letters of every language written in Latin script in Europe. If somebody
    writes a Polish surname or a Czech place name into the copy tomorrow, it is
    already there.
  * the handful of spacing modifiers and combining marks Google's own
    unicode-range for this face names outside that block, so the declaration in
    styles/base.less stays honest about what the file contains.

The `latin` faces are NOT touched. They are 13 KB, they are the ones every page
loads, and there is nothing in them to remove.

USAGE

    RUBYOPT="-E utf-8:utf-8" bundle exec jekyll build
    python3 tools/subset-latin-fonts.py

It needs `fonttools` and `brotli`, which are deliberately not project
dependencies — install them into a throwaway venv:

    python3 -m venv /tmp/fenv && /tmp/fenv/bin/pip install fonttools brotli
    /tmp/fenv/bin/python tools/subset-latin-fonts.py

The unsubset originals live in tools/latin-font-sources/ and are the input; the
script never reads the files it is about to overwrite. `tools/` is in
`exclude:`, so the sources are versioned and never deployed.
"""
import glob
import io
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, '_site')
FONTS = os.path.join(ROOT, 'fonts')
SOURCES = os.path.join(ROOT, 'tools', 'latin-font-sources')

FACES = [
    'noto-sans-400-latin-ext.woff2',
    'noto-sans-700-latin-ext.woff2',
    'noto-sans-400-italic-latin-ext.woff2',
    'noto-sans-700-italic-latin-ext.woff2',
]

# The range styles/base.less declares for these faces. Anything outside it is
# served by the `latin` face instead, so it is not this file's business.
DECLARED = [
    (0x0100, 0x02BA), (0x02BD, 0x02C5), (0x02C7, 0x02CC), (0x02CE, 0x02D7),
    (0x02DD, 0x02FF), (0x0304, 0x0304), (0x0308, 0x0308), (0x0329, 0x0329),
    (0x1D00, 0x1DBF), (0x1E00, 0x1E9F), (0x1EF2, 0x1EFF), (0x2020, 0x2020),
    (0x20A0, 0x20AB), (0x20AD, 0x20C0), (0x2113, 0x2113),
    (0x2C60, 0x2C7F), (0xA720, 0xA7FF),
]

# The margin. Latin Extended-A entire, plus the marks the declaration names
# outside it, so what the file holds and what the CSS claims agree.
MARGIN = set(range(0x0100, 0x0180)) | {0x0304, 0x0308, 0x0329, 0x2020, 0x2113}


def in_declared(cp):
    return any(lo <= cp <= hi for lo, hi in DECLARED)


def used_characters():
    """Every declared-range codepoint that appears in the built site or the data."""
    found = set()
    files = glob.glob(os.path.join(SITE, '**', '*.html'), recursive=True)
    files += glob.glob(os.path.join(ROOT, '_data', '*.yml'))
    if not glob.glob(os.path.join(SITE, '**', '*.html'), recursive=True):
        sys.exit('no built site — run `npx gulp build` first')
    for f in files:
        text = io.open(f, encoding='utf-8', errors='ignore').read()
        if f.endswith('.html'):
            text = re.sub(r'<(script|style)\b.*?</\1>', ' ', text, flags=re.S)
            text = re.sub(r'<[^>]+>', ' ', text)
        for ch in text:
            cp = ord(ch)
            if in_declared(cp):
                found.add(cp)
    return found


def main():
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
        import brotli  # noqa: F401  — fontTools needs it for woff2
    except ImportError:
        sys.exit(__doc__.split('USAGE')[1])

    # THE SOURCES ARE THE INPUT AND THEY MUST BE THE ORIGINALS.
    #
    # On the very first run there is no sources directory and the files in
    # /fonts/ are still Google's, so seeding from there is right. On every run
    # after that /fonts/ holds the SUBSET, and seeding from it would subset a
    # subset — narrowing the coverage a little more each time, silently, until
    # a macron one day fails to paint. The size check is the guard: an original
    # latin-ext face is 60 KB and up, a subset is under 10.
    if not os.path.isdir(SOURCES):
        seed = [os.path.join(FONTS, f) for f in FACES]
        if any(os.path.getsize(f) < 30 * 1024 for f in seed):
            sys.exit('tools/latin-font-sources/ is missing and the faces in /fonts/ are\n'
                     'already subset, so there is nothing to subset FROM. Restore the\n'
                     'directory from git, or re-fetch the four originals from\n'
                     'fonts.google.com/noto/specimen/Noto+Sans (weights 400 and 700,\n'
                     'roman and italic, the latin-ext unicode-range).')
        os.makedirs(SOURCES)
        for face in FACES:
            shutil.copy2(os.path.join(FONTS, face), os.path.join(SOURCES, face))
        print('first run: copied the four originals into tools/latin-font-sources/')

    used = used_characters()
    keep = sorted(used | MARGIN)
    print('scanned the built site -> %d characters in use from the latin-ext range '
          '(%s), %d kept with the margin'
          % (len(used), ' '.join(chr(c) for c in sorted(used)), len(keep)))

    total_before = total_after = 0
    for face in FACES:
        src = os.path.join(SOURCES, face)
        dst = os.path.join(FONTS, face)
        before = os.path.getsize(src)

        font = TTFont(src)
        opts = subset.Options()
        opts.layout_features = ['*']       # keep kerning and the rest
        opts.name_IDs = ['*']
        opts.notdef_outline = True
        opts.recalc_bounds = True
        subsetter = subset.Subsetter(options=opts)
        subsetter.populate(unicodes=keep)
        subsetter.subset(font)
        font.flavor = 'woff2'
        font.save(dst)
        font.close()

        after = os.path.getsize(dst)
        total_before += before
        total_after += after
        print('  %-38s %6.1f KB -> %6.1f KB' % (face, before / 1024.0, after / 1024.0))

        missing = [chr(c) for c in sorted(used)
                   if c not in TTFont(dst).getBestCmap()]
        if missing:
            print('     NOT COVERED: %s' % ' '.join(missing))

    print('\nfonts: %.1f KB -> %.1f KB  (%.0f%% smaller)'
          % (total_before / 1024.0, total_after / 1024.0,
             100 - (total_after * 100.0 / total_before)))


if __name__ == '__main__':
    main()
