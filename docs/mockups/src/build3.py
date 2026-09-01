# -*- coding: utf-8 -*-
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _home2 as H
import _home as HH          # panel plumbing (CSS_PANEL, JS) is reused verbatim
import _aside as A

ROOT = '/Applications/MAMP/htdocs/aikidomusubi.com'
SITE = os.path.join(ROOT, '_site')
OUT = os.path.join(SITE, 'mockups')
shell = io.open(os.path.join(SITE, 'index.html'), encoding='utf-8').read()
i = shell.index('<main'); i_end = shell.index('>', i) + 1; j = shell.index('</main>')
HEAD, MAIN_OPEN, TAIL = shell[:i], shell[i:i_end], shell[j:]
os.makedirs(OUT, exist_ok=True)

JS = (HH.JS.replace('Cara B', 'Ura')
              .replace('/cara-b/', '/ura/').replace('#cara-b', '#ura'))

head = HEAD.replace('</head>', '<style>%s</style></head>' % (
    H.CSS + HH.CSS_PANEL + A.CSS_BASE + A.CSS_A))
panel = ('<div class="rg-scrim"></div>'
         '<div class="rg-panel ab" id="bside" role="dialog" aria-modal="true"'
         ' aria-label="Ura" aria-hidden="true">%s%s</div>'
         '<script>%s</script><script>%s</script>'
         % (A.mast(), A.body_a(), JS, A.JS_WORDS))
html = (head + MAIN_OPEN + H.BODY.replace('__DOOR__', H.DOOR)
        + TAIL.replace('</body>', panel + '</body>'))
io.open(os.path.join(OUT, 'home.html'), 'w', encoding='utf-8').write(html)
print('  home.html   %5d KB' % (len(html) // 1024))

st = ("""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ura — Aikido Musubi</title>
<link rel="stylesheet" href="/styles/all.min.css">
<style>html,body{margin:0;background:#111314}%s%s</style></head>
<body class="ab">%s%s<script>%s</script></body></html>"""
      % (A.CSS_BASE, A.CSS_A, A.mast(False), A.body_a(), A.JS_WORDS))
io.open(os.path.join(OUT, 'ura.html'), 'w', encoding='utf-8').write(st)
print('  ura.html    %5d KB' % (len(st) // 1024))
