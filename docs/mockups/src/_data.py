# -*- coding: utf-8 -*-
"""Real numbers, pulled from the real data files. Nothing here is invented."""
import re, io, os, collections

ROOT = '/Applications/MAMP/htdocs/aikidomusubi.com'


def gallery():
    s = io.open(os.path.join(ROOT, '_data/gallery.yml'), encoding='utf-8').read()
    blocks = re.findall(r'\n  - type:\s*(\w+)(.*?)(?=\n  - type:|\Z)', s, re.S)
    per_year, types, rows = collections.Counter(), collections.Counter(), []
    for t, b in blocks:
        if re.search(r'show:\s*false', b):
            continue
        d = re.search(r'date_iso:\s*"?([\d-]+)', b)
        th = re.search(r'thumb:\s*"?([^"\n]+)', b)
        if not d:
            continue
        per_year[d.group(1)[:4]] += 1
        types[t] += 1
        if th and os.path.isfile(os.path.join(ROOT, 'images/%s.webp' % th.group(1).strip())):
            rows.append((d.group(1), th.group(1).strip(), t))
    rows.sort(reverse=True)
    return per_year, types, rows


def events():
    out = []
    for f in sorted(os.listdir(os.path.join(ROOT, '_events'))):
        if not f.endswith('.md'):
            continue
        s = io.open(os.path.join(ROOT, '_events', f), encoding='utf-8').read()
        t = re.search(r'^title_es:\s*"([^"]+)"', s, re.M)
        out.append((f[:10], t.group(1) if t else f))
    return out
