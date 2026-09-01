# -*- coding: utf-8 -*-
"""Three ways to put Resources into Ura.

Ura is the dark side of the site: everything on it is generated from data and
nothing is written by hand. So the question is not "how do we show a list of
downloads" but "what does Ura know about the resources that no other page
does". Each approach answers that differently.

  1  A SECTION of its own, in Ura's own idiom — a compact index.
  2  NO section. The resources are attached to the sections that already
     exist, where the reader is already asking the question they answer.
  3  A DRAWER — one line in the digest that expands into the whole index.
"""
import os

ROOT = '/Applications/MAMP/htdocs/aikidomusubi.com'
OUT = os.path.join(ROOT, '_site', 'mockups')
DOCS = os.path.join(ROOT, 'docs', 'mockups')

CSS = """
:root{--fg:#d5dadc;--hi:#fff;--mute:#9ba3a6;--line:rgba(255,255,255,.13);
      --acc:#FFF200;--bg:#111314;--card:#191b1c;--rust:#AE5224}
html,body{margin:0;background:var(--bg);color:var(--fg);
  font-family:'Noto Sans',system-ui,sans-serif;font-size:16px;line-height:1.6;
  -webkit-font-smoothing:antialiased}
*{box-sizing:border-box}
h1,h2,h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;margin:0;
  color:var(--hi);letter-spacing:.02em}
p{margin:0}
a{color:inherit;text-decoration:none}
.w{max-width:1140px;margin:0 auto;padding:0 6rem}
@media(max-width:991.98px){.w{padding:0 4rem}}
@media(max-width:767.98px){.w{padding:0 2rem}}
.mast{position:sticky;top:0;z-index:6;background:rgba(17,19,20,.95);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--line)}
.mast-in{display:flex;align-items:center;gap:1rem;min-height:3.3rem;padding-top:.8rem;padding-bottom:.8rem}
.seal{font-family:'Hiragino Sans','Noto Sans JP',sans-serif;font-size:1.4rem;line-height:1;color:var(--acc)}
.ttl{font-family:Futura,sans-serif;font-size:.72rem;letter-spacing:.3em;text-transform:uppercase;color:var(--hi)}
.sub{font-size:.72rem;color:var(--mute)}
.sec{padding-top:3.2rem;border-top:1px solid var(--line);margin-top:3.2rem}
.sec:first-of-type{border-top:0;margin-top:0}
.sh{display:flex;align-items:baseline;gap:1rem;flex-wrap:wrap;margin-bottom:1.6rem}
.sh h2{font-size:1.65rem}
.sh .note{font-size:.8rem;color:var(--mute)}
.lab{font-family:Futura,sans-serif;font-size:.6rem;letter-spacing:.2em;text-transform:uppercase;
  color:var(--mute);margin-bottom:.9rem;padding-bottom:.6rem;border-bottom:1px solid var(--line)}
.note-link{margin-top:1.4rem;font-size:.82rem}
.note-link a{color:var(--acc);border-bottom:1px solid rgba(255,242,0,.4);padding-bottom:.1rem}
.badge{position:fixed;top:0;left:0;z-index:99;background:var(--acc);color:#111314;
  font-family:Futura,sans-serif;font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;padding:.5rem .9rem}
.k{display:inline-block;font-family:Futura,sans-serif;font-size:.5rem;letter-spacing:.16em;
  text-transform:uppercase;padding:.14rem .4rem;color:#111314}
.k-form{background:var(--rust);color:#fff}
.k-page{background:var(--hi)}
.k-doc{background:var(--rust);color:#fff}
footer.end{margin-top:4rem;padding:2.4rem 0 4rem;border-top:1px solid var(--line);
  font-size:.78rem;color:var(--mute)}
footer.end b{color:var(--hi);font-weight:400}
"""


def page(title, badge, body, note, extra=''):
    return """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s — Ura</title><link rel="stylesheet" href="/styles/all.min.css">
<style>%s%s</style></head><body>
<div class="badge">%s</div>
<header class="mast"><div class="w mast-in"><span class="seal">裏</span>
<span class="ttl">Ura</span><span class="sub">el dojo por detrás</span></div></header>
<div class="w">%s<footer class="end">%s</footer></div></body></html>""" % (
        title, CSS, extra, badge, body, note)


# ---------------------------------------------------------------------------
# 1 · a section of its own
# ---------------------------------------------------------------------------
ONE_CSS = """
.r-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:0 2.4rem}
.r-grid a{display:block;padding:.7rem 0;border-bottom:1px solid rgba(255,255,255,.08)}
.r-grid b{display:block;font-weight:400;font-size:.87rem;line-height:1.35;color:var(--hi)}
.r-grid a:hover>b{color:var(--acc)}
.r-grid span{display:flex;gap:.5rem;align-items:baseline;margin-top:.2rem;font-size:.68rem;color:var(--mute)}
@media(max-width:991.98px){.r-grid{grid-template-columns:1fr 1fr}}
@media(max-width:575.98px){.r-grid{grid-template-columns:1fr}}
.r-kyu{display:grid;grid-template-columns:repeat(5,1fr);gap:2px;margin-bottom:2.4rem}
.r-kyu a{background:var(--card);padding:1rem .9rem 1.1rem}
.r-kyu a:hover{background:#1f2223}
.r-kyu .g{font-family:Futura,sans-serif;font-size:1.15rem;color:var(--hi)}
.r-kyu .n{font-family:Futura,sans-serif;font-size:.56rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--acc);margin-top:.5rem}
@media(max-width:767.98px){.r-kyu{grid-template-columns:1fr 1fr}}
"""

KYU = [('5.º kyū', '8 técnicas'), ('4.º kyū', '14 técnicas'), ('3.er kyū', '21 técnicas'),
       ('2.º kyū', '27 técnicas'), ('1.er kyū', '34 técnicas')]
ROWS = [('Hoja de inscripción', 'form', 'PDF · ES CA EN JA'),
        ('Autorización de uso de imagen', 'form', 'PDF · ES CA EN JA'),
        ('Autorización para menores', 'form', 'PDF · ES CA'),
        ('Orden de domiciliación SEPA', 'form', 'PDF · ES CA'),
        ('36 técnicas básicas de jō', 'doc', 'PDF · ES CA EN JA'),
        ('31 no jō kata', 'doc', 'PDF · ES EN'),
        ('Etiqueta del dojo · reihō', 'page', 'En la web'),
        ('Normas de la sala', 'form', 'PDF · ES CA'),
        ('Guía de la primera clase', 'page', 'En la web')]


def build_one():
    kyu = ''.join('<a href="#"><p class="g">%s</p><p class="n">%s</p></a>' % k for k in KYU)
    rows = ''.join("""<a href="#"><b>%s</b><span><span class="k k-%s">%s</span>%s</span></a>"""
                   % (t, k, {'form': 'Impreso', 'doc': 'PDF', 'page': 'Web'}[k], m)
                   for t, k, m in ROWS)
    body = """
<section class="sec">
  <div class="sh"><h2>Recursos</h2><p class="note">Lo que hay que firmar y lo que hay que saber</p></div>
  <p class="lab">Programa de examen</p>
  <div class="r-kyu">%s</div>
  <p class="lab">Impresos y documentos</p>
  <div class="r-grid">%s</div>
  <p class="note-link"><a href="/recursos/">Todos los recursos</a></p>
</section>""" % (kyu, rows)
    return page('Ura · Recursos como sección', 'Enfoque 1 · sección propia', body,
                '<b>Enfoque 1.</b> Una sección más, entre «Palabras del tatami» y «Enlaces». '
                'Ura ya es el sitio donde está todo junto, y esto encaja sin inventar nada: '
                'la rejilla de los enlaces y las pastillas del archivo, reutilizadas. '
                'El coste es una sección más en una página que ya tiene ocho, y duplicar '
                'un índice que existe entero en /recursos/.', ONE_CSS)


# ---------------------------------------------------------------------------
# 2 · no section; attached where the question is asked
# ---------------------------------------------------------------------------
TWO_CSS = """
.att{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1.2rem}
.att a{display:inline-flex;align-items:center;gap:.5rem;padding:.5rem .8rem;
  box-shadow:inset 0 0 0 1px var(--line);font-size:.8rem}
.att a:hover{box-shadow:inset 0 0 0 1px rgba(255,255,255,.35);color:var(--hi)}
.ev{display:grid;grid-template-columns:5rem 1fr auto;gap:1.2rem;align-items:baseline;
  padding:.75rem 0;border-bottom:1px solid var(--line)}
.ev .d{font-family:Futura,sans-serif;font-size:.62rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--acc)}
.ev .t{font-size:.9rem;color:var(--hi)}
.ev .t small{display:block;font-size:.72rem;color:var(--mute);margin-top:.1rem}
.ev .r{font-family:Futura,sans-serif;font-size:.58rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--acc);border-bottom:1px solid rgba(255,242,0,.4);white-space:nowrap}
.cells{display:grid;grid-template-columns:repeat(3,1fr);gap:2px}
.cell{background:var(--card);padding:1.3rem 1.2rem 1.5rem}
.cell h3{font-size:.95rem;letter-spacing:.05em;text-transform:uppercase;margin-bottom:.9rem}
.cell p{font-size:.82rem;line-height:1.65;color:#c9d0d3}
@media(max-width:767.98px){.cells{grid-template-columns:1fr}}
"""


def build_two():
    att = lambda items: '<div class="att">%s</div>' % ''.join(
        '<a href="#"><span class="k k-%s">%s</span>%s</a>'
        % (k, {'form': 'Impreso', 'doc': 'PDF', 'page': 'Web'}[k], t) for t, k in items)

    body = """
<section class="sec">
  <div class="sh"><h2>Lo que viene</h2><p class="note">Cierres, cambios y clases extra</p></div>
  <div class="ev"><p class="d">29 ago</p>
    <p class="t">Preparación de exámenes<small>Cada sábado, 10:00, hasta el 5 de diciembre</small></p>
    <p class="r">Programa de 4.º kyū &rarr;</p></div>
  <div class="ev"><p class="d">11 sep</p>
    <p class="t">Diada de Catalunya<small>El dojo cierra</small></p><p></p></div>
  <div class="ev"><p class="d">24 abr</p>
    <p class="t">Seminario de Emilio Cardia Shihan<small>6.º dan Aikikai</small></p>
    <p class="r">Ficha del seminario &rarr;</p></div>
</section>

<section class="sec">
  <div class="sh"><h2>Palabras del tatami</h2><p class="note">Seis que oirás el primer día</p></div>
  <p class="note" style="font-size:.87rem;line-height:1.6;color:#c9d0d3;max-width:43rem">
    礼法 <em>reihō</em> es la etiqueta del dojo, y no es ceremonia: es cómo cuarenta personas
    descalzas comparten un suelo sin estorbarse.</p>
  %s
</section>

<section class="sec">
  <div class="sh"><h2>Lo esencial</h2><p class="note">Tres páginas en una pantalla</p></div>
  <div class="cells">
    <div class="cell"><h3>Dónde</h3><p>Badalona, Sant Adrià y la Universidad de Barcelona.</p></div>
    <div class="cell"><h3>Cuánto</h3><p>Inscripción gratuita. Dos clases de prueba sin coste.</p>
      %s</div>
    <div class="cell"><h3>Cómo empezar</h3><p>Escríbenos con un día de antelación y te decimos
      cuándo venir.</p>%s</div>
  </div>
</section>""" % (att([('Etiqueta del dojo · reihō', 'page'), ('Guía de la primera clase', 'page')]),
                 att([('Hoja de inscripción', 'form'), ('Domiciliación SEPA', 'form')]),
                 att([('Autorización de imagen', 'form')]))

    return page('Ura · Recursos repartidos', 'Enfoque 2 · sin sección', body,
                '<b>Enfoque 2.</b> Ninguna sección nueva. Cada recurso cuelga de la sección que '
                'ya plantea la pregunta que responde: el programa de kyū junto a la clase de '
                'preparación, la etiqueta junto a las palabras, los impresos dentro de «Lo '
                'esencial». Ura no crece y cada enlace aparece cuando hace falta. El coste es '
                'que no hay un sitio en Ura donde estén todos.', TWO_CSS)


# ---------------------------------------------------------------------------
# 3 · a drawer in the digest
# ---------------------------------------------------------------------------
THREE_CSS = TWO_CSS + """
.dr{border-top:1px solid var(--line);margin-top:2px}
.dr summary{list-style:none;cursor:pointer;display:flex;align-items:baseline;gap:1rem;
  padding:1.1rem 0;font-size:.95rem;color:var(--hi)}
.dr summary::-webkit-details-marker{display:none}
.dr summary .c{margin-left:auto;font-family:Futura,sans-serif;font-size:.6rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--mute)}
.dr summary .ch{color:var(--acc);font-size:1.1rem;line-height:1;transition:transform .2s}
.dr[open] summary .ch{transform:rotate(45deg)}
.dr .in{padding:0 0 1.6rem}
.dr-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:0 2.4rem}
.dr-grid a{display:block;padding:.6rem 0;border-bottom:1px solid rgba(255,255,255,.08)}
.dr-grid b{display:block;font-weight:400;font-size:.85rem;color:var(--hi)}
.dr-grid span{display:block;margin-top:.15rem;font-size:.66rem;color:var(--mute)}
@media(max-width:767.98px){.dr-grid{grid-template-columns:1fr}}
"""


def build_three():
    grid = ''.join('<a href="#"><b>%s</b><span>%s</span></a>' % (t, m) for t, k, m in ROWS)
    kyu = ''.join('<a href="#"><b>Programa de %s</b><span>%s</span></a>' % k for k in KYU)
    body = """
<section class="sec">
  <div class="sh"><h2>Lo esencial</h2><p class="note">Tres páginas en una pantalla</p></div>
  <div class="cells">
    <div class="cell"><h3>Dónde</h3><p>Badalona, Sant Adrià y la Universidad de Barcelona.</p></div>
    <div class="cell"><h3>Cuánto</h3><p>Inscripción gratuita. Dos clases de prueba sin coste.</p></div>
    <div class="cell"><h3>Cómo empezar</h3><p>Escríbenos con un día de antelación.</p></div>
  </div>

  <details class="dr" name="ura-dr">
    <summary>Programa de examen<span class="c">5 grados</span><span class="ch">+</span></summary>
    <div class="in"><div class="dr-grid">%s</div></div>
  </details>
  <details class="dr" name="ura-dr" open>
    <summary>Impresos y documentos<span class="c">9 recursos</span><span class="ch">+</span></summary>
    <div class="in"><div class="dr-grid">%s</div>
      <p class="note-link"><a href="/recursos/">Todos los recursos</a></p></div>
  </details>
</section>""" % (kyu, grid)

    return page('Ura · Recursos en un cajón', 'Enfoque 3 · cajón en «Lo esencial»', body,
                '<b>Enfoque 3.</b> Dos cajones al pie de «Lo esencial», cerrados por defecto. '
                'Ura no gana una sección ni pierde el sitio donde están todos; quien los busca '
                'los abre y quien no, no los ve. Usa el mismo acordeón exclusivo que el registro '
                'de seminarios, así que no hay un mecanismo nuevo. El coste es que un cajón '
                'cerrado es un enlace que nadie encuentra por accidente.', THREE_CSS)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (('ura-res-1', build_one), ('ura-res-2', build_two), ('ura-res-3', build_three)):
        html = fn()
        open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(html)
        open(os.path.join(DOCS, name + '.html'), 'w', encoding='utf-8').write(html)
        print('  %s.html' % name)
