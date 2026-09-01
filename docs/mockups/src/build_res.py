# -*- coding: utf-8 -*-
"""Three proposals for the Resources section.

Same content in all three — see _res.py — so the comparison is about structure
and reading experience, not copy.

  A  one page, a filing cabinet     /recursos/
  B  a hub and five pages           /recursos/ + /recursos/<grupo>/
  C  the dojo handbook              one long document, read in place

Writes into _site/mockups/, which `npx gulp build` wipes. The source lives in
docs/ and is in git; see docs/mockups/README.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _res as R                                          # noqa: E402

ROOT = '/Applications/MAMP/htdocs/aikidomusubi.com'
OUT = os.path.join(ROOT, '_site', 'mockups')

BASE = """
:root{--ink:#111314;--mute:#4f5c62;--line:rgba(17,19,20,.13);--rule:rgba(17,19,20,.30);
      --acc:#FFF200;--rust:#AE5224;--green:#1A7444;--panel:#f6f7f7}
html,body{margin:0;background:#fff;color:var(--ink);
  font-family:'Noto Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased;line-height:1.7}
*{box-sizing:border-box}
h1,h2,h3,h4{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;margin:0;letter-spacing:.04em}
p{margin:0}
a{color:inherit}
.w{max-width:1140px;margin:0 auto;padding-left:6rem;padding-right:6rem}
@media(max-width:991.98px){.w{padding-left:4rem;padding-right:4rem}}
@media(max-width:767.98px){.w{padding-left:2rem;padding-right:2rem}}
.mono{font-family:ui-monospace,'SF Mono',Menlo,monospace;font-variant-numeric:tabular-nums}

/* the shared page header, as the real site now renders it */
.top{padding:3.4rem 0 0;text-align:center}
.top h1{font-size:2rem;letter-spacing:1px;text-transform:uppercase;margin:2rem 0}
.top .lede{max-width:none;font-size:.9rem;color:var(--mute);margin:0 0 5.4rem}
.strip{display:flex;flex-wrap:wrap;gap:1.4rem;padding:1.6rem 0 1rem;border-bottom:1px solid var(--line)}
.strip a{font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:#425055;text-decoration:none}
.strip a[aria-current]{color:var(--ink);font-weight:700;box-shadow:inset 0 -2px 0 var(--ink)}

/* the badge that says what a thing IS */
.k{display:inline-block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.52rem;
   letter-spacing:.16em;text-transform:uppercase;padding:.16rem .44rem;vertical-align:.14em}
.k-pdf{background:var(--rust);color:#fff}
.k-html{background:var(--ink);color:#fff}
.k-book{background:var(--green);color:#fff}
.k-link{background:none;color:var(--mute);box-shadow:inset 0 0 0 1px var(--line)}
.lg{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.56rem;letter-spacing:.14em;color:var(--mute)}
.note{font-size:.88rem;color:var(--mute)}
footer.end{margin-top:4rem;padding:2rem 0 4rem;border-top:1px solid var(--line);
  font-size:.78rem;color:var(--mute)}
.badge{position:fixed;top:0;left:0;z-index:99;background:var(--ink);color:#fff;
  font-family:Futura,sans-serif;font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;
  padding:.5rem .9rem}
"""


def head(title, css=''):
    return ("""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s — Aikido Musubi</title>
<link rel="stylesheet" href="/styles/all.min.css">
<style>%s%s</style></head><body>""" % (title, BASE, css))


def kind_badge(k):
    label = {'pdf': 'PDF', 'html': 'En la web', 'book': 'Libro', 'link': 'Enlace'}[k]
    return '<span class="k k-%s">%s</span>' % (k, label)


def strip(active):
    items = [('recursos', 'Recursos'), ('clases', 'Clases'), ('horarios', 'Horarios'),
             ('cuotas', 'Cuotas'), ('visitantes', 'Visitantes')]
    return '<nav class="strip">%s</nav>' % ''.join(
        '<a href="#"%s>%s</a>' % (' aria-current="page"' if i == active else '', n)
        for i, n in items)


def top(title, lede):
    return """<div class="w">%s<header class="top"><h1>%s</h1>
<p class="lede">%s</p></header></div>""" % (strip('recursos'), title, lede)


def end(note):
    return ('<div class="w"><footer class="end">%s</footer></div></body></html>' % note)


# ===========================================================================
# A — one page, a filing cabinet
# ===========================================================================
A_CSS = """
.a-bar{padding:1.15rem 0;margin-bottom:2.2rem}
.a-search{display:flex;gap:.5rem;margin-bottom:.75rem}
.a-search input{flex:1;min-width:0;font:inherit;font-size:.95rem;padding:.5rem .8rem;
  border:1px solid var(--line);border-radius:0;background:#fff}
.a-search button{font-family:Futura,sans-serif;font-size:.62rem;letter-spacing:.14em;
  text-transform:uppercase;border:1px solid var(--line);background:none;color:var(--mute);padding:0 1rem;cursor:pointer}
.a-chips{display:flex;gap:.4rem;flex-wrap:wrap}
.a-chips button{display:inline-flex;align-items:center;gap:.45rem;min-height:2rem;padding:.25rem .8rem;
  border:1px solid rgba(17,19,20,.12);border-radius:2rem;background:#fff;font:inherit;font-size:.8rem;
  color:var(--mute);cursor:pointer;opacity:.55}
.a-chips button[data-on]{opacity:1;background:var(--ink);border-color:var(--ink);color:#fff}
.a-chips button i{font-style:normal;font-size:.68rem}
.a-chips button[data-on] i{color:var(--acc)}
.a-grp{margin-bottom:2.8rem}
.a-gh{display:flex;align-items:baseline;gap:1rem;padding-bottom:.7rem;border-bottom:2px solid var(--ink);margin-bottom:.2rem}
.a-gh h2{font-size:1.15rem;text-transform:uppercase;letter-spacing:.1em}
.a-gh span{font-size:.82rem;color:var(--mute)}
.a-row{display:grid;grid-template-columns:1fr auto;gap:1rem 1.6rem;align-items:start;
  padding:.95rem 0;border-bottom:1px solid var(--line)}
.a-row b{font-weight:400;font-size:.98rem;display:block}
.a-row .d{font-size:.86rem;color:var(--mute);margin-top:.15rem}
.a-row .m{margin-top:.35rem;display:flex;gap:.7rem;align-items:center;flex-wrap:wrap}
.a-get{align-self:center;white-space:nowrap;font-family:Futura,sans-serif;font-size:.62rem;
  letter-spacing:.14em;text-transform:uppercase;padding:.5rem .9rem;background:var(--ink);color:#fff;text-decoration:none}
.a-get.o{background:none;color:var(--ink);box-shadow:inset 0 0 0 1px var(--rule)}
@media(max-width:575.98px){.a-row{grid-template-columns:1fr}}
"""


def row_a(title, desc, kind, size, langs, action='Descargar'):
    meta = '%s <span class="lg">%s</span>' % (kind_badge(kind), langs)
    if size != '—':
        meta += ' <span class="lg mono">%s</span>' % size
    cls = 'a-get' if kind in ('pdf', 'html') else 'a-get o'
    return ("""<div class="a-row"><div><b>%s</b><p class="d">%s</p>
<p class="m">%s</p></div><a class="%s" href="#">%s</a></div>"""
            % (title, desc, meta, cls, action))


def build_a():
    counts = [('Todos', R.TOTAL), ('Trámites', len(R.TRAMITES)), ('Examen', len(R.EXAMEN)),
              ('Armas', len(R.ARMAS)), ('Etiqueta', len(R.ETIQUETA)), ('Lecturas', len(R.LECTURAS))]
    chips = ''.join('<button%s>%s <i>%d</i></button>' % (' data-on' if i == 0 else '', n, c)
                    for i, (n, c) in enumerate(counts))
    out = [head('Recursos · A'), '<div class="badge">Propuesta A · una página</div>',
           top('Recursos',
               'Los documentos del dojo en un sitio: los papeles que hay que firmar, el programa '
               'de cada examen, los programas de armas y unas cuantas lecturas. %d entradas.' % R.TOTAL),
           '<div class="w"><div class="a-bar">',
           '<div class="a-search"><input type="search" placeholder="Buscar en los recursos…">'
           '<button>Limpiar</button></div>',
           '<div class="a-chips">%s</div></div>' % chips]

    for gid, name, sub, blurb, items in R.GROUPS:
        out.append('<section class="a-grp"><div class="a-gh"><h2>%s</h2><span>%s</span></div>' % (name, sub))
        if gid == 'examen':
            for t, d, days, n in R.EXAMEN:
                out.append(row_a('Programa de %s' % t, d, 'html', '—',
                                 '%d técnicas · %s' % (n, days), 'Ver'))
        elif gid == 'lecturas':
            for t, author, d, kind, where in R.LECTURAS:
                out.append(row_a('%s <span class="lg">· %s</span>' % (t, author), d, kind, '—',
                                 where, 'Buscarlo'))
        else:
            for t, d, kind, size, langs in items:
                out.append(row_a(t, d, kind, size, langs,
                                 'Ver' if kind == 'html' else 'Descargar'))
        out.append('</section>')

    out.append('</div>')
    out.append(end('<b>Propuesta A.</b> Una sola página, filtrada como el glosario. '
                   'Todo se encuentra en un scroll y en un marcador. El precio es que un '
                   'formulario para firmar y un libro para leer viven en la misma lista.'))
    return ''.join(out).replace('<style>', '<style>' + A_CSS, 1) if False else \
        head('Recursos · A', A_CSS) + ''.join(out[1:])


# ===========================================================================
# B — a hub and five pages
# ===========================================================================
B_CSS = """
.b-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:2px;background:var(--line);margin-bottom:3rem}
.b-card{background:#fff;padding:1.6rem 1.5rem 1.7rem;display:flex;flex-direction:column;
  text-decoration:none;min-height:13rem}
.b-card:hover{background:var(--panel)}
.b-card .n{font-family:Futura,sans-serif;font-size:.56rem;letter-spacing:.18em;color:var(--rust)}
.b-card h2{font-size:1.15rem;text-transform:uppercase;letter-spacing:.09em;margin:.5rem 0 .5rem}
.b-card p{font-size:.86rem;color:var(--mute);line-height:1.65}
.b-card .c{margin-top:auto;padding-top:1rem;font-family:Futura,sans-serif;font-size:.6rem;
  letter-spacing:.14em;text-transform:uppercase;color:var(--mute)}
@media(max-width:991.98px){.b-grid{grid-template-columns:1fr 1fr}}
@media(max-width:575.98px){.b-grid{grid-template-columns:1fr}}

.b-featured{border-top:2px solid var(--ink);padding-top:1.2rem;margin-bottom:3rem}
.b-featured h3{font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;color:var(--mute);margin-bottom:1rem}
.b-kyu{display:grid;grid-template-columns:repeat(5,1fr);gap:2px;background:var(--line)}
.b-kyu a{background:#fff;padding:1.1rem 1rem 1.2rem;text-decoration:none;display:block}
.b-kyu a:hover{background:var(--panel)}
.b-kyu .g{font-family:Futura,sans-serif;font-size:1.3rem;letter-spacing:.02em}
.b-kyu .t{font-size:.72rem;color:var(--mute);margin-top:.5rem;line-height:1.5}
.b-kyu .w2{font-family:Futura,sans-serif;font-size:.56rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--rust);margin-top:.6rem}
@media(max-width:767.98px){.b-kyu{grid-template-columns:1fr 1fr}}

.b-recent{display:grid;grid-template-columns:1fr 1fr;gap:0 3rem}
.b-recent a{display:flex;justify-content:space-between;gap:1rem;align-items:baseline;
  padding:.7rem 0;border-bottom:1px solid var(--line);text-decoration:none;font-size:.9rem}
.b-recent span{font-size:.72rem;color:var(--mute);white-space:nowrap}
@media(max-width:767.98px){.b-recent{grid-template-columns:1fr}}
"""


def build_b():
    cards = []
    for i, (gid, name, sub, blurb, items) in enumerate(R.GROUPS, 1):
        n = len(R.EXAMEN) if gid == 'examen' else (len(R.LECTURAS) if gid == 'lecturas' else len(items))
        cards.append("""<a class="b-card" href="#"><p class="n">%02d</p><h2>%s</h2>
<p>%s</p><p class="c">%d %s &rarr;</p></a>"""
                     % (i, name, blurb, n, 'documento' if n == 1 else 'documentos'))

    kyu = ''.join("""<a href="#"><p class="g">%s</p><p class="t">%s</p>
<p class="w2">%d técnicas</p></a>""" % (t, d.split('.')[0] + '.', n)
                  for t, d, days, n in R.EXAMEN)

    recent = ''.join('<a href="#">%s <span>%s · %s</span></a>' % (t, k.upper(), s)
                     for t, d, k, s, l in (R.TRAMITES[:2] + R.ARMAS[:2] + R.ETIQUETA[:2]))

    body = """<div class="w">
<div class="b-grid">%s</div>

<section class="b-featured">
  <h3>Programa de examen · de 5.º a 1.er kyū</h3>
  <div class="b-kyu">%s</div>
  <p class="note" style="margin-top:1rem">Cada uno es una página en la web, no un PDF:
     se busca, se enlaza a una técnica concreta y se imprime igual que el horario.</p>
</section>

<section>
  <h3 style="font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;color:var(--mute);
      border-top:1px solid var(--line);padding-top:1.2rem;margin-bottom:1rem">Lo último</h3>
  <div class="b-recent">%s</div>
</section>
</div>""" % (''.join(cards), kyu, recent)

    return (head('Recursos · B', B_CSS) +
            '<div class="badge">Propuesta B · hub y páginas</div>' +
            top('Recursos',
                'Cinco secciones, cada una con su página. Los papeles por un lado, el programa '
                'de examen por otro, y las lecturas donde no estorban a quien busca un impreso.') +
            body +
            end('<b>Propuesta B.</b> Un índice y cinco páginas reales, cada una con su URL. '
                'El programa de examen deja de ser cinco PDFs y pasa a ser cinco páginas '
                'buscables, enlazables e imprimibles. Más piezas que mantener.'))


# ===========================================================================
# C — the dojo handbook
# ===========================================================================
C_CSS = """
.c-wrap{display:grid;grid-template-columns:15rem 1fr;gap:4rem;align-items:start}
@media(max-width:991.98px){.c-wrap{grid-template-columns:1fr;gap:2rem}}
.c-toc{position:sticky;top:1.5rem}
.c-toc p{font-family:Futura,sans-serif;font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;
  color:var(--mute);padding-bottom:.6rem;border-bottom:1px solid var(--line);margin-bottom:.5rem}
.c-toc a{display:block;padding:.4rem 0;font-size:.88rem;text-decoration:none;color:var(--mute)}
.c-toc a[aria-current]{color:var(--ink);box-shadow:inset 2px 0 0 var(--rust);padding-left:.7rem}
.c-toc .dl{margin-top:1.4rem;display:block;font-family:Futura,sans-serif;font-size:.6rem;
  letter-spacing:.14em;text-transform:uppercase;padding:.6rem .9rem;background:var(--ink);color:#fff;text-align:center}
.c-sec{padding-top:1.5rem;border-top:1px solid var(--line);margin-bottom:3rem}
.c-sec h2{font-size:1.2rem;text-transform:uppercase;letter-spacing:.09em;margin-bottom:.9rem}
.c-sec > p{font-size:.95rem;line-height:1.85;color:#2c3437;margin-bottom:1rem;max-width:43.25rem}
.c-steps{counter-reset:s;list-style:none;margin:0 0 1.2rem;padding:0}
.c-steps li{counter-increment:s;position:relative;padding:.7rem 0 .7rem 3rem;
  border-bottom:1px solid var(--line);font-size:.93rem;line-height:1.75;color:#2c3437}
.c-steps li::before{content:counter(s,decimal-leading-zero);position:absolute;left:0;top:.9rem;
  font-family:Futura,sans-serif;font-size:.64rem;letter-spacing:.14em;color:var(--rust)}
.c-tbl{width:100%;border-collapse:collapse;font-size:.88rem;margin-bottom:1.2rem}
.c-tbl th{text-align:left;font-family:Futura,sans-serif;font-size:.58rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--mute);padding:.5rem .8rem .5rem 0;border-bottom:1px solid var(--rule)}
.c-tbl td{padding:.6rem .8rem .6rem 0;border-bottom:1px solid var(--line);vertical-align:top}
.c-tbl td:first-child{font-family:Futura,sans-serif;white-space:nowrap}
.c-att{display:flex;flex-wrap:wrap;gap:.5rem;margin:1.2rem 0 0}
.c-att a{display:inline-flex;align-items:center;gap:.5rem;padding:.5rem .8rem;
  box-shadow:inset 0 0 0 1px var(--line);text-decoration:none;font-size:.82rem}
.c-att a:hover{box-shadow:inset 0 0 0 1px var(--rule)}
"""


def build_c():
    toc = ''.join('<a href="#"%s>%s</a>' % (' aria-current="true"' if i == 0 else '', n)
                  for i, (gid, n, s, b, it) in enumerate(R.GROUPS))

    etiq = ''.join('<li><b>%s.</b> %s</li>' % (t.split('·')[0].strip(), d)
                   for t, d, k, s, l in R.ETIQUETA)

    kyu_rows = ''.join('<tr><td>%s</td><td>%s</td><td class="mono">%d</td><td>%s</td></tr>'
                       % (t, d, n, days) for t, d, days, n in R.EXAMEN)

    att = lambda items: '<div class="c-att">%s</div>' % ''.join(
        '<a href="#">%s %s</a>' % (kind_badge(k), t) for t, d, k, s, l in items)

    body = """<div class="w"><div class="c-wrap">
<nav class="c-toc"><p>En esta página</p>%s<a class="dl" href="#">Descargar todo · PDF</a></nav>
<div>

<section class="c-sec"><h2>Trámites</h2>
<p>Cuatro documentos, una vez. Se rellenan, se firman y se entregan en el dojo o por
correo; después no vuelves a mirarlos.</p>
%s
</section>

<section class="c-sec"><h2>Programa de examen</h2>
<p>El contenido de cada examen de kyū y los días mínimos de práctica desde el grado
anterior. No hay fecha fija: se propone cuando el instructor considera que el trabajo
está hecho.</p>
<table class="c-tbl"><thead><tr><th>Grado</th><th>Qué entra</th><th>Técnicas</th><th>Mínimo</th></tr></thead>
<tbody>%s</tbody></table>
<p class="note">Cada grado tiene además su propia página con las técnicas nombradas una
a una, en japonés y en castellano.</p>
</section>

<section class="c-sec"><h2>Etiqueta y normas</h2>
<p>La etiqueta del dojo, el <em>礼法 reihō</em>, no es ceremonia: es la manera de que
cuarenta personas descalzas compartan un suelo sin estorbarse.</p>
<ol class="c-steps">%s</ol>
%s
</section>

<section class="c-sec"><h2>Armas</h2>
<p>Los programas que se siguen en el dojo, con la numeración que se usa en clase.</p>
%s
</section>

<section class="c-sec"><h2>Lecturas</h2>
<p>Nada de esto lo publicamos nosotros. Está en la biblioteca pública o se compra.</p>
%s
</section>

</div></div></div>""" % (toc, att(R.TRAMITES), kyu_rows, etiq,
                         att(R.ETIQUETA), att(R.ARMAS),
                         '<div class="c-att">%s</div>' % ''.join(
                             '<a href="#">%s %s <span class="lg">· %s</span></a>'
                             % (kind_badge(k), t, a) for t, a, d, k, w in R.LECTURAS))

    return (head('Recursos · C', C_CSS) +
            '<div class="badge">Propuesta C · manual del dojo</div>' +
            top('Recursos',
                'El manual del dojo: se lee aquí, entero, y cada sección lleva sus impresos '
                'colgados debajo. Se imprime completo o por secciones.') +
            body +
            end('<b>Propuesta C.</b> Un documento, no una lista de descargas. Lo que se puede '
                'leer, se lee en la página; los PDFs cuelgan de la sección a la que pertenecen. '
                'Los trámites encajan peor: un impreso no es lectura.'))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (('recursos-a', build_a), ('recursos-b', build_b), ('recursos-c', build_c)):
        p = os.path.join(OUT, name + '.html')
        open(p, 'w', encoding='utf-8').write(fn())
        # keep the durable copy in git as well
        open(os.path.join(ROOT, 'docs', 'mockups', name + '.html'), 'w',
             encoding='utf-8').write(fn())
        print('  %s.html' % name)
