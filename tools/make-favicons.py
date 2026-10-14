#!/usr/bin/env python3
"""Every favicon and app icon the site serves, from one image.

    python3 tools/make-favicons.py

SOURCE. tools/favicon-source/logo-15.png: the knot, white on #111314, 4500px
square. The knot is cut out of it by luminance, so its own antialiasing is
kept, and every PNG below is rendered DOWN from that: nothing is ever scaled
up. The SVGs are a potrace tracing of the same cut-out.

COLOURS. The knot in White on the brand Black #111314, everywhere. Not a
transparent icon with a knot that changes colour for light and dark: browsers
do not reliably report the tab's real colour (Chrome can draw a light tab bar
under a dark system theme), and a dark knot on a dark bar disappears. The tile
reads on any background.

WHAT EACH ONE IS FOR, and why they are not all the same picture (N is the
generation number, GEN below):

  musubiN-knot.svg            the browser tab, every modern browser. A rounded
                             black tile, the knot zoomed in to fill it
  musubiN-knot-{16..192}.png  the same tile for browsers and crawlers that want
                             a bitmap; Google's results page takes the 48/96/192
  musubiN-knot.ico            16, 32 and 48 in one file; /favicon.ico is a copy,
                             for anything that asks for that path blindly
  musubiN-apple-touch.png     iOS home screen, 180px. FULL BLEED and square: iOS
                             rounds the corners itself, and a tile that is
                             already rounded shows a black ring inside the mask
  musubiN-app-{192,512}.png   installed web app ("any"): the rounded tile
  musubiN-maskable-{192,512}  installed web app on Android ("maskable"): full
                             bleed, the knot inside the 80% safe circle, since
                             the launcher may cut the icon to any shape
  musubiN-tile-*.png          Windows Start tiles: the knot alone, transparent,
                             on the tile colour browserconfig.xml sets
  musubiN-knot-mask.svg       Safari's pinned-tab icon: one colour, no tile

THE 16PX ONE IS SHARPENED. Scaled down as it is, the knot's band and the gaps
between them come to about a pixel each at 16px and average into a grey
checkerboard. Thickening the band was tried and turned the knot into a yellow
blob. What works is stretching the reduced alpha so each edge pixel commits to
yellow or to black (`levels`); 32px gets a gentler version of the same, and the
larger sizes are left exactly as drawn. The SVG is what modern browsers use for
the tab anyway, and on a Retina screen the 16 is never drawn.

The site's own references live in _includes/icons.html, icons/musubi.webmanifest
and icons/browserconfig.xml. The file names are new rather than the old ones
reused: a favicon is cached hard, and a browser holding the old picture under
the old name would keep showing it.

Needs Pillow, numpy and potracer, which are deliberately not project
dependencies; install them into a throwaway venv, as tools/subset-ja-fonts.py
explains for fontTools.
"""
import io
import os
import shutil
import sys

try:
    import numpy as np
    from PIL import Image, ImageDraw
    import potrace
except ImportError as e:
    sys.exit(f"needs Pillow, numpy and potracer in a throwaway venv ({e})")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "favicon-source", "logo-15.png")
OUT = os.path.join(ROOT, "icons")

BLACK = (0x11, 0x13, 0x14)

# THE GENERATION NUMBER IS IN EVERY FILE NAME. Favicons are cached hard, so a
# changed picture under an unchanged name would stay in browsers for months.
# Bump GEN whenever the picture changes, re-run, update _includes/icons.html,
# icons/musubi*.webmanifest and icons/browserconfig.xml, and `git rm` the old set.
#   gen 1  October 2026: the knot in Yellow on Black, close to the edges
#   gen 2  October 2026: the knot in White on Black, with more room around it
GEN = 2
PFX = "musubi" if GEN == 1 else f"musubi{GEN}"
WHITE = (0xFF, 0xFF, 0xFF)
SS = 8            # supersampling factor for every raster


def knot_alpha():
    """The knot as an 8-bit alpha mask, cropped to its own bounding box."""
    a = np.asarray(Image.open(SRC).convert("RGB")).astype(float)
    lum = a.mean(axis=2)
    bg = np.median(lum[:50, :50])
    alpha = np.clip((lum - bg) / (255 - bg), 0, 1)
    ys, xs = np.where(alpha > 0.5)
    crop = alpha[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return Image.fromarray((crop * 255).round().astype("uint8"), "L")


KNOT = knot_alpha()
KW, KH = KNOT.size


def render(w, h, *, knot_w, tile, radius=0.0, levels=None):
    """One icon, w x h px. knot_w is the knot's width as a share of the
    shorter side; tile is 'rounded', 'square' or None (transparent).
    `levels` (lo, hi) stretches the knot's reduced alpha so that edge pixels
    commit to yellow or to black: at 16px the knot's band and its gaps are
    each about a pixel, and left soft they average into a grey checkerboard."""
    W, H = w * SS, h * SS
    side = min(w, h)
    kw = knot_w * side
    kh = kw * KH / KW
    big = KNOT.resize((round(kw * SS), round(kh * SS)), Image.LANCZOS)
    mask = Image.new("L", (W, H), 0)
    mask.paste(big, ((W - big.size[0]) // 2, (H - big.size[1]) // 2))
    alpha = mask.resize((w, h), Image.LANCZOS)
    if levels:
        lo, hi = levels
        a = np.asarray(alpha).astype(float) / 255
        alpha = Image.fromarray((np.clip((a - lo) / (hi - lo), 0, 1) * 255).round().astype("uint8"), "L")

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if tile:
        shape = Image.new("L", (W, H), 0)
        r = radius * min(W, H) if tile == "rounded" else 0
        ImageDraw.Draw(shape).rounded_rectangle((0, 0, W - 1, H - 1), radius=r, fill=255)
        out.paste(Image.new("RGBA", (w, h), BLACK + (255,)), (0, 0), shape.resize((w, h), Image.LANCZOS))
    out.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (w, h), WHITE).split(), alpha)))
    return out


def save(img, name, opaque=False):
    if opaque:
        flat = Image.new("RGB", img.size, BLACK)
        flat.paste(img, (0, 0), img)
        img = flat
    p = os.path.join(OUT, name)
    img.save(p, optimize=True)
    print(f"  {name:<34} {img.size[0]}x{img.size[1]}  {os.path.getsize(p) / 1024:5.1f} KB")


# --- the browser tab ---------------------------------------------------------
TAB = dict(tile="rounded", radius=0.22)
TAB_KNOT = {16: 0.86, 32: 0.78, 48: 0.74, 96: 0.70, 192: 0.70}
TAB_LEVELS = {16: (0.3, 0.7), 32: (0.15, 0.85)}


def tab(size):
    return render(size, size, knot_w=TAB_KNOT[size], levels=TAB_LEVELS.get(size), **TAB)


# --- the vector ---------------------------------------------------------------
def traced_path(scale, dx, dy):
    """The knot as an SVG path, traced from the 4500px cut-out."""
    # potracer fills what is BELOW its black level, so the knot goes in as
    # False: passed the other way round it traces the background instead.
    bm = potrace.Bitmap(np.asarray(KNOT) <= 127)
    plist = bm.trace(turdsize=50, alphamax=1.0, opticurve=True, opttolerance=0.2)

    def pt(p):
        return f"{p.x * scale + dx:.2f} {p.y * scale + dy:.2f}"

    d = []
    for curve in plist:
        d.append(f"M{pt(curve.start_point)}")
        for seg in curve.segments:
            if seg.is_corner:
                d.append(f"L{pt(seg.c)}L{pt(seg.end_point)}")
            else:
                d.append(f"C{pt(seg.c1)} {pt(seg.c2)} {pt(seg.end_point)}")
        d.append("Z")
    return "".join(d)


def svg_tile():
    # 100x100 viewBox: the knot at about the 48px tab proportion, which reads
    # at every size a browser draws an SVG favicon.
    kw = 72.0
    s = kw / KW
    kh = KH * s
    d = traced_path(s, (100 - kw) / 2, (100 - kh) / 2)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<rect width="100" height="100" rx="22" fill="#111314"/>'
            f'<path fill="#FFFFFF" fill-rule="evenodd" d="{d}"/></svg>\n')


def svg_mask():
    # Safari's pinned tab: one colour, the knot alone, square viewBox.
    s = 16.0 / KW
    kh = KH * s
    d = traced_path(s, 0, (16 - kh) / 2)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
            f'<path fill-rule="evenodd" d="{d}"/></svg>\n')


def main():
    os.makedirs(OUT, exist_ok=True)
    print(f"\nknot {KW}x{KH} from {os.path.relpath(SRC, ROOT)}\n")

    for size in (16, 32, 48, 96, 192):
        save(tab(size), f"{PFX}-knot-{size}.png")

    # /favicon.ico at the site root: the three classic sizes in one file.
    # Written by hand, PNG payload per size: Pillow's ICO writer resamples
    # every size from one image, which would undo the tuned 16px render.
    # Two copies: icons/musubi-knot.ico is the one the pages link, under a
    # name no browser has cached; /favicon.ico is the same file for anything
    # that asks for that path without reading the page, and it already held
    # the old picture, so it cannot be the one linked.
    ico = os.path.join(OUT, f"{PFX}-knot.ico")
    with open(ico, "wb") as f:
        imgs = [tab(16), tab(32), tab(48)]
        blobs = []
        for im in imgs:
            b = io.BytesIO()
            im.save(b, format="PNG", optimize=True)
            blobs.append(b.getvalue())
        f.write((0).to_bytes(2, "little") + (1).to_bytes(2, "little") + len(imgs).to_bytes(2, "little"))
        offset = 6 + 16 * len(imgs)
        for im, blob in zip(imgs, blobs):
            w = im.size[0]
            f.write(bytes([w % 256, w % 256, 0, 0]) + (1).to_bytes(2, "little") + (32).to_bytes(2, "little")
                    + len(blob).to_bytes(4, "little") + offset.to_bytes(4, "little"))
            offset += len(blob)
        for blob in blobs:
            f.write(blob)
    shutil.copyfile(ico, os.path.join(ROOT, "favicon.ico"))
    print(f"  {PFX + '-knot.ico + /favicon.ico':<34} 16+32+48  {os.path.getsize(ico) / 1024:5.1f} KB")

    save(render(180, 180, knot_w=0.62, tile="square"), f"{PFX}-apple-touch.png", opaque=True)
    for size in (192, 512):
        save(render(size, size, knot_w=0.68, **TAB), f"{PFX}-app-{size}.png")
        save(render(size, size, knot_w=0.54, tile="square"), f"{PFX}-maskable-{size}.png", opaque=True)

    save(render(70, 70, knot_w=0.62, tile=None), f"{PFX}-tile-70.png")
    save(render(150, 150, knot_w=0.46, tile=None), f"{PFX}-tile-150.png")
    save(render(310, 310, knot_w=0.44, tile=None), f"{PFX}-tile-310.png")
    save(render(310, 150, knot_w=0.56, tile=None), f"{PFX}-tile-310x150.png")

    for name, body in ((f"{PFX}-knot.svg", svg_tile()), (f"{PFX}-knot-mask.svg", svg_mask())):
        with open(os.path.join(OUT, name), "w") as f:
            f.write(body)
        print(f"  {name:<34} vector    {os.path.getsize(os.path.join(OUT, name)) / 1024:5.1f} KB")
    print()


if __name__ == "__main__":
    main()
