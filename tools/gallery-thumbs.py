#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the contact-sheet thumbnails Ura's archive draws.

WHY THIS EXISTS. The archive in Ura is a 16-column grid of 57px squares, and
it was drawing them from the gallery's full images — 960x720 WebP, about 40 KB
each. Sixty-four of those is 2.4 MB downloaded to paint a strip of thumbnails
the size of postage stamps, and the images are lazy so the cost lands exactly
when the reader scrolls to the section.

This writes a `-t` variant at 160px (a little over 2x the rendered size, so it
stays sharp on a retina screen) next to each original. The sheet uses those;
the modal, which opens one image at a time on demand, uses the original.

Only entries named by `thumb:` in _data/gallery.yml are converted, not every
file in /images/ — the album contents are never shown at this size.

    python3 tools/gallery-thumbs.py           # write what is missing
    python3 tools/gallery-thumbs.py --force   # rewrite everything

Needs `cwebp`, which ships with libwebp (`brew install webp`). It is not a
project dependency for the same reason fonttools is not: it runs when the
gallery changes, which is rarely, and never on a build.
"""
import os
import re
import subprocess
import sys

SIZE = 160
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.join(ROOT, 'images')
DATA = os.path.join(ROOT, '_data', 'gallery.yml')


def thumbs():
    names = []
    for line in open(DATA, encoding='utf-8'):
        m = re.match(r'\s*thumb:\s*"([^"]+)"', line)
        if m:
            names.append(m.group(1))
    return names


def main():
    force = '--force' in sys.argv
    if subprocess.call(['which', 'cwebp'], stdout=subprocess.DEVNULL):
        sys.exit('cwebp not found — brew install webp')

    names = thumbs()
    made = skipped = missing = 0
    saved = 0
    for n in names:
        src = os.path.join(IMAGES, n + '.webp')
        dst = os.path.join(IMAGES, n + '-t.webp')
        if not os.path.exists(src):
            missing += 1
            continue
        if os.path.exists(dst) and not force:
            skipped += 1
            continue
        r = subprocess.run(['cwebp', '-quiet', '-q', '72', '-resize', str(SIZE), '0',
                            src, '-o', dst], capture_output=True)
        if r.returncode:
            missing += 1
            continue
        made += 1
        saved += os.path.getsize(src) - os.path.getsize(dst)

    print('  %d thumbnails written, %d already there, %d skipped'
          % (made, skipped, missing))
    if made:
        print('  %.1f MB smaller than the originals they replace in the sheet'
              % (saved / 1024 / 1024))


if __name__ == '__main__':
    main()
