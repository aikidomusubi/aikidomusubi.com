# -*- coding: utf-8 -*-
"""Three ways to fix Ura's archive.

The problem: the section renders 91 of 462 entries (eight per year) and offers
a year strip, which promises navigation of the whole archive and delivers a
slice of it. The mosaic itself is the good part and stays in all three.

Measured, not guessed:

  462 entries have a thumbnail; per year 2008:2 … 2024:96, 2025:43, 2026:9
  thumbnails average 3.5 KB, 1.59 MB for all of them
  Ura today            91 KB raw / 15.3 KB gzipped
  Ura with all 462    269 KB raw / 36.9 KB gzipped   (+21.6 KB gz)

A hidden tile costs no image bytes: `loading="lazy"` never fetches an image
that is not in the viewport, and a display:none image never is.
"""
import os
import re

ROOT = '/Applications/MAMP/htdocs/aikidomusubi.com'
OUT = os.path.join(ROOT, '_site', 'mockups')
DOCS = os.path.join(ROOT, 'docs', 'mockups')

YEARS = [(2026, 9), (2025, 43), (2024, 96), (2023, 91), (2022, 52), (2021, 79),
         (2020, 50), (2019, 5), (2016, 5), (2015, 5), (2014, 3), (2013, 3),
         (2012, 15), (2011, 2), (2010, 1), (2009, 1), (2008, 2)]


def thumbs(n):
    """Real thumbnail paths, taken from the built page."""
    p = os.path.join(ROOT, '_site', 'ura', 'index.html')
    src = re.findall(r'<img src="(/images/gallery-[^"]+-t\.webp)"', open(p, encoding='utf-8').read())
    if not src:
        src = ['/images/placeholder.webp']
    return [src[i % len(src)] for i in range(n)]


CSS = """
:root{--fg:#d5dadc;--hi:#fff;--mute:#9ba3a6;--line:rgba(255,255,255,.13);
      --acc:#FFF200;--bg:#111314;--card:#191b1c;--rust:#AE5224}
html,body{margin:0;background:var(--bg);color:var(--fg);
  font-family:'Noto Sans',system-ui,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased}
*{box-sizing:border-box}
h1,h2,h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;margin:0;color:var(--hi);letter-spacing:.02em}
p{margin:0}
a{color:inherit;text-decoration:none}
.w{max-width:1140px;margin:0 auto;padding:0 6rem}
@media(max-width:991.98px){.w{padding:0 4rem}}
@media(max-width:767.98px){.w{padding:0 2rem}}
.mast{position:sticky;top:0;z-index:6;background:rgba(17,19,20,.95);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--line)}
.mast-in{display:flex;align-items:center;gap:1rem;min-height:3.3rem;padding:.8rem 0}
.seal{font-family:'Hiragino Sans','Noto Sans JP',sans-serif;font-size:1.4rem;color:var(--acc)}
.ttl{font-family:Futura,sans-serif;font-size:.72rem;letter-spacing:.3em;text-transform:uppercase;color:var(--hi)}
.sub{font-size:.72rem;color:var(--mute)}
.sec{padding-top:3.2rem}
.sh{display:flex;align-items:baseline;gap:1rem;flex-wrap:wrap;margin-bottom:1.6rem}
.sh h2{font-size:1.65rem}
.sh .note{font-size:.8rem;color:var(--mute)}
.lab{font-family:Futura,sans-serif;font-size:.6rem;letter-spacing:.2em;text-transform:uppercase;
  color:var(--mute);margin-bottom:.9rem}
.sheet{display:grid;grid-template-columns:repeat(16,1fr);gap:2px}
.sheet a,.sheet span{display:block;position:relative}
.sheet img{display:block;width:100%;aspect-ratio:1;object-fit:cover}
@media(max-width:991.98px){.sheet{grid-template-columns:repeat(10,1fr)}}
@media(max-width:575.98px){.sheet{grid-template-columns:repeat(6,1fr)}}
.counts{display:flex;gap:2.6rem;flex-wrap:wrap;margin-top:1.6rem}
.counts b{font-family:Futura,sans-serif;font-size:1.4rem;color:var(--hi);display:block;line-height:1}
.counts i{font-style:normal;font-family:Futura,sans-serif;font-size:.56rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--mute);display:block;margin-top:.4rem}
.note-link{margin-top:1.6rem;font-size:.82rem}
.note-link a{color:var(--acc);border-bottom:1px solid rgba(255,242,0,.4);padding-bottom:.1rem}
.badge{position:fixed;top:0;left:0;z-index:99;background:var(--acc);color:#111314;
  font-family:Futura,sans-serif;font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;padding:.5rem .9rem}
footer.end{margin-top:3.4rem;padding:2.4rem 0 4rem;border-top:1px solid var(--line);
  font-size:.78rem;color:var(--mute)}
footer.end b{color:var(--hi);font-weight:400}
.cost{margin-top:.8rem;font-family:ui-monospace,Menlo,monospace;font-size:.72rem;color:var(--acc)}
"""


def page(title, badge, body, note, cost, extra=''):
    return """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><link rel="stylesheet" href="/styles/all.min.css">
<style>%s%s</style></head><body>
<div class="badge">%s</div>
<header class="mast"><div class="w mast-in"><span class="seal">裏</span>
<span class="ttl">Ura</span><span class="sub">el dojo por detrás</span></div></header>
<div class="w">%s<footer class="end">%s<p class="cost">%s</p></footer></div></body></html>""" % (
        title, CSS, extra, badge, body, note, cost)


COUNTS = """<div class="counts">
  <div><b>462</b><i>momentos guardados</i></div><div><b>49</b><i>álbumes</i></div>
  <div><b>236</b><i>publicaciones</i></div><div><b>177</b><i>vídeos</i></div></div>"""


def grid(n, hidden_from=None):
    out = []
    for i, t in enumerate(thumbs(n)):
        hid = ' hidden' if hidden_from is not None and i >= hidden_from else ''
        out.append('<a href="#"%s><img src="%s" alt="" loading="lazy" width="160" height="160"></a>' % (hid, t))
    return '<div class="sheet">%s</div>' % ''.join(out)


# ---------------------------------------------------------------------------
# A · the mosaic is a picture, not a navigator
# ---------------------------------------------------------------------------
def build_a():
    body = """<section class="sec">
  <div class="sh"><h2>El archivo</h2><p class="note">Lo más reciente, y cuánto hay detrás</p></div>
  %s
  %s
  <p class="note-link"><a href="/galeria/">Ver la galería completa &rarr;</a></p>
</section>""" % (grid(64), COUNTS)
    return page('Ura · Archivo A', 'Enfoque A · lámina, sin filtro', body,
                '<b>Enfoque A.</b> El mosaico deja de fingir que es un navegador. Son los 64 más '
                'recientes y nada más: una lámina del archivo, los cuatro recuentos debajo, y una '
                'salida a la galería. No hay tira de años, así que no hay promesa que incumplir. '
                'Es lo más ligero y lo más honesto, y pierde la posibilidad de asomarse a 2012 '
                'desde Ura.',
                'peso: 64 miniaturas ≈ 220 KB · página 15,3 KB gz (igual que hoy)')


# ---------------------------------------------------------------------------
# B · everything, revealed by year
# ---------------------------------------------------------------------------
B_CSS = """
.rail{display:flex;flex-wrap:wrap;gap:.35rem;margin-bottom:1.1rem}
.rail a{font-family:Futura,sans-serif;font-size:.62rem;letter-spacing:.1em;padding:.32rem .55rem;
  background:var(--card);color:var(--fg);display:inline-flex;gap:.4rem;align-items:baseline}
.rail a i{font-style:normal;font-size:.54rem;color:var(--mute)}
.rail a[data-on]{background:var(--acc);color:#111314}
.rail a[data-on] i{color:#111314}
"""


def build_b():
    rail = ''.join('<a href="#"%s>%s <i>%d</i></a>' % (' data-on' if i == 0 else '', y, n)
                   for i, (y, n) in enumerate([('Recientes', 64)] + YEARS))
    body = """<section class="sec">
  <div class="sh"><h2>El archivo</h2><p class="note">462 momentos, desde 2008</p></div>
  <p class="lab">Salta a un año</p>
  <div class="rail">%s</div>
  %s
  %s
  <p class="note-link"><a href="/galeria/">Ver la galería completa &rarr;</a></p>
</section>""" % (rail, grid(96, hidden_from=64), COUNTS)
    return page('Ura · Archivo B', 'Enfoque B · todo, por años', body,
                '<b>Enfoque B.</b> Están los 462. El marcado de todos va en la página, oculto salvo '
                'los 64 recientes; al pulsar un año se revela el suyo y sólo entonces se descargan '
                'sus imágenes, porque <code>loading="lazy"</code> no pide una imagen que no está en '
                'pantalla. La tira de años dice cuántos hay en cada uno, así que la cifra no '
                'engaña. Completo y honesto; el precio es el marcado.',
                'peso: +21,6 KB gz de marcado en cada carga de Ura (15,3 → 36,9 KB gz) · '
                'imágenes sólo al abrir un año')


# ---------------------------------------------------------------------------
# C · mosaic as texture, years as a real index that leaves
# ---------------------------------------------------------------------------
C_CSS = """
.yr{display:grid;grid-template-columns:repeat(auto-fill,minmax(5.2rem,1fr));gap:2px;margin-top:1.8rem}
.yr a{background:var(--card);padding:.7rem .7rem .8rem;display:block}
.yr a:hover{background:#1f2223}
.yr a:hover .n{color:var(--acc)}
.yr .y{font-family:Futura,sans-serif;font-size:.62rem;letter-spacing:.12em;color:var(--mute)}
.yr .n{font-family:Futura,sans-serif;font-size:1.05rem;color:var(--hi);line-height:1;margin-top:.3rem}
.yr .bar{height:2px;background:var(--acc);margin-top:.5rem;opacity:.55}
"""


def build_c():
    mx = max(n for _, n in YEARS)
    yr = ''.join("""<a href="/galeria/?y=%d"><p class="y">%d</p><p class="n">%d</p>
<div class="bar" style="width:%.0f%%"></div></a>""" % (y, y, n, max(6, n / mx * 100))
                 for y, n in YEARS)
    body = """<section class="sec">
  <div class="sh"><h2>El archivo</h2><p class="note">Lo más reciente, y todo lo demás por años</p></div>
  %s
  %s
  <p class="lab" style="margin-top:2.4rem">Todo lo publicado, por año</p>
  <div class="yr">%s</div>
  <p class="note-link"><a href="/galeria/">Ver la galería completa &rarr;</a></p>
</section>""" % (grid(64), COUNTS, yr)
    return page('Ura · Archivo C', 'Enfoque C · lámina + índice de años', body,
                '<b>Enfoque C.</b> El mosaico es textura: los 64 recientes, sin filtro. Debajo, un '
                'índice de años que dice cuántos hay en cada uno y lleva a la galería filtrada por '
                'ese año. La navegación es explícita y sale del sitio donde no está el contenido, '
                'así que no promete nada que no cumpla — y de paso enseña la forma del archivo: '
                '96 en 2024, dos en 2008.',
                'peso: 64 miniaturas ≈ 220 KB · página ≈ 16 KB gz')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, fn, css in (('ura-arch-a', build_a, ''), ('ura-arch-b', build_b, B_CSS),
                          ('ura-arch-c', build_c, C_CSS)):
        html = fn()
        if css:
            html = html.replace('</style>', css + '</style>', 1)
        open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(html)
        open(os.path.join(DOCS, name + '.html'), 'w', encoding='utf-8').write(html)
        print('  %s.html' % name)
