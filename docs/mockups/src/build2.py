# -*- coding: utf-8 -*-
"""Two homes, two asides, all on the real page shell."""
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _home as H
import _aside as A

ROOT = '/Applications/MAMP/htdocs/aikidomusubi.com'
SITE = os.path.join(ROOT, '_site')
OUT = os.path.join(SITE, 'mockups')
shell = io.open(os.path.join(SITE, 'index.html'), encoding='utf-8').read()
i = shell.index('<main'); i_end = shell.index('>', i) + 1; j = shell.index('</main>')
HEAD, MAIN_OPEN, TAIL = shell[:i], shell[i:i_end], shell[j:]
os.makedirs(OUT, exist_ok=True)


def home(name, css, body, aside_css, aside_body):
    head = HEAD.replace('</head>', '<style>%s</style></head>' % (
        H.CSS_SHARED + css + H.CSS_PANEL + A.CSS_BASE + aside_css))
    panel = ('<div class="rg-scrim"></div>'
             '<div class="rg-panel ab" id="bside" role="dialog" aria-modal="true"'
             ' aria-label="Cara B" aria-hidden="true">%s%s</div><script>%s</script>'
             % (A.mast(), aside_body, H.JS))
    html = head + MAIN_OPEN + body.replace('__DOOR__', H.DOOR) + TAIL.replace('</body>', panel + '</body>')
    io.open(os.path.join(OUT, name), 'w', encoding='utf-8').write(html)
    print('  %-18s %5d KB' % (name, len(html) // 1024))


def standalone(name, css, body):
    html = ("""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cara B — Aikido Musubi</title>
<link rel="stylesheet" href="/styles/all.min.css">
<style>html,body{margin:0;background:#111314}%s%s</style></head>
<body class="ab">%s%s</body></html>""" % (A.CSS_BASE, css, A.mast(False), body))
    io.open(os.path.join(OUT, name), 'w', encoding='utf-8').write(html)
    print('  %-18s %5d KB' % (name, len(html) // 1024))


home('home-a.html', H.CSS_A, H.BODY_A, A.CSS_A, A.body_a())
home('home-b.html', H.CSS_B, H.BODY_B, A.CSS_B, A.body_b())
standalone('aside-a.html', A.CSS_A, A.body_a())
standalone('aside-b.html', A.CSS_B, A.body_b())
