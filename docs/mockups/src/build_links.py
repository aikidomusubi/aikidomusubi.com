#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Two internal-linking proposals, drawn before either is built.

Both come out of the Search Console export of 17 September 2026, and both are
about the same defect: a page nothing points at is a page Google does not come
back to.

WHAT WAS MEASURED, on the built site, counting distinct pages that carry an
`href` to each URL:

    /badalona/, /barcelona/, /sant-adria-de-besos/      9 to 11 inbound links
    the 24 video watch pages                            6 inbound links
    everything else of consequence                     37 to 38

And of a watch page's six, exactly ONE was editorial. The other five were the
language switcher naming its three translations and itself, plus the pager's
one neighbour. The site map now adds a second (commit 90c5e49); this is about
the rest.

WHY IT IS DRAWN AND NOT SHIPPED. Both touch something a reader sees on every
page or on twenty-four pages, and the standing instruction on this project is
that the footer and anything like it gets a mockup first.

WHAT THIS IS NOT. It is not a fix for the crawl. Google's own internal-links
report still lists 32 URLs, all of them belonging to the site as it was before
1 September, every one with exactly 12 links. It has not recrawled the
navigation, and no amount of internal linking makes it come back sooner. These
are worth doing because the links are missing, which is true whatever Google
does next.

    python3 docs/mockups/src/build_links.py
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT_FT = os.path.join(ROOT, 'docs', 'mockups', 'footer-venues.html')
OUT_PV = os.path.join(ROOT, 'docs', 'mockups', 'video-siblings.html')


# ── real data ───────────────────────────────────────────────────────────────
def footer_where():
    """The `where` column of _data/footer.yml, in order, Spanish labels.

    The block ends at the next TOP-LEVEL key, not at the next `- id:`. It is
    the last column in the file, so a lookahead for `\\n  - id:` alone runs
    straight on into `legal:` and the mockup drew the legal strip's four links
    inside the venue column. Caught by looking at the rendered page, which is
    what the mockup is for.
    """
    s = io.open(os.path.join(ROOT, '_data/footer.yml'), encoding='utf-8').read()
    block = re.search(r'\n  - id: where\n(.*?)(?=\n  - id: |\n[a-z_]+:|\Z)',
                      s, re.S).group(1)
    out = []
    for m in re.finditer(r'- label: \{ es: "([^"]+)".*?url:\s*\{ es: "([^"]+)"',
                         block, re.S):
        out.append((m.group(1), m.group(2)))
    assert len(out) == 5, 'expected the five venue rows, got %d' % len(out)
    return out


def videos():
    """The six records in _videos/, newest first: (date, title_es, thumb)."""
    d = os.path.join(ROOT, '_videos')
    rows = []
    for f in sorted(os.listdir(d)):
        if not f.endswith('.md'):
            continue
        s = io.open(os.path.join(d, f), encoding='utf-8').read()
        t = re.search(r'title_es:\s*"([^"]+)"', s)
        th = re.search(r'thumb:\s*"?([^"\n]+)', s)
        dt = re.search(r'date:\s*(\d{8})', s)
        slug = f[:-3]
        rows.append((dt.group(1), t.group(1), th.group(1).strip() if th else '', slug))
    rows.sort(reverse=True)
    return rows


FT = footer_where()
VIDS = videos()

# The three town pages, and the fact that the UB is a room inside one of them.
TOWNS = [
    ('Badalona',            '/badalona/',            'aikido-musubi'),
    ('Barcelona',           '/barcelona/',           'cxem-espronceda'),
    ('Sant Adrià de Besòs', '/sant-adria-de-besos/', 'sant-adria-de-besos'),
]

CSS = """
  /* `all.min.css` paints `html` @Black, for the overscroll at the end of a
     dark footer, and constrains `body` to the viewport for the scroll lock the
     Ura panel uses. A mockup has no `.page` wrapper, so the body stopped at
     900px and the black canvas showed through everything below the first
     screen: two proposals and all their reasoning were dark grey on near
     black. Found by looking at it, which is the point of rendering these. */
  html, body { background: #fff; height: auto; min-height: 100%; }
  .mk { max-width: 60rem; margin: 0 auto; padding: 3rem 2rem 6rem; }
  .mk h1 { font-size: 2rem; margin: 0 0 .4rem; }
  .mk > p.lede { max-width: 42rem; color: #444; margin: 0 0 2.4rem; }
  .mk h2 { font-size: 1.15rem; margin: 3.2rem 0 .3rem; }
  .mk h2 .tag { font-size: .68rem; letter-spacing: .1em; text-transform: uppercase;
                padding: .18rem .45rem; margin-left: .5rem; vertical-align: .18em;
                border: 1px solid currentColor; }
  .mk h2 .now  { color: #6b6b6b; }
  .mk h2 .rec  { color: #1A7444; }
  .mk > p.note { max-width: 42rem; color: #444; font-size: .92rem; margin: .5rem 0 1.2rem; }
  .mk table { border-collapse: collapse; margin: 1rem 0 0; font-size: .88rem; width: 100%; }
  .mk th, .mk td { text-align: left; padding: .45rem .7rem .45rem 0;
                   border-bottom: 1px solid rgba(0,0,0,.08); vertical-align: top; }
  .mk th { font-weight: 700; color: #333; }
  .mk td.n { font-variant-numeric: tabular-nums; white-space: nowrap; }
  .mk .frame { border: 1px solid rgba(0,0,0,.14); padding: 1.6rem;
               background: #111; color: #fff; }
  .mk .frame.light { background: #fff; color: #111; }
  .mk .why { max-width: 42rem; margin: 1rem 0 0; font-size: .92rem; color: #444; }
  .mk .why b { color: #111; }
  .mk hr { border: 0; border-top: 1px solid rgba(0,0,0,.12); margin: 3.6rem 0 0; }

  /* the footer column, lifted out of footer.less so the mockup can stand alone */
  .mkft { display: flex; gap: 4rem; flex-wrap: wrap; }
  .mkft nav { min-width: 13rem; }
  .mkft h3 { font-family: Futura, 'Noto Sans', sans-serif; font-size: .82rem;
             letter-spacing: .06em; text-transform: uppercase;
             color: rgba(255,255,255,.62); margin: 0 0 .8rem; }
  .mkft ul { list-style: none; margin: 0; padding: 0; }
  .mkft li { margin: 0 0 .42rem; }
  .mkft a { color: #fff; text-decoration: none; font-size: .95rem;
            border-bottom: 1px solid transparent; }
  .mkft a:hover { border-bottom-color: rgba(255,255,255,.5); }
  .mkft .u { display: block; font-size: .7rem; color: #FFF200;
             font-variant-numeric: tabular-nums; letter-spacing: .01em; }
  .mkft .gone { opacity: .38; text-decoration: line-through; }

  /* the watch-page tail */
  .mkpv { max-width: 44rem; }
  .mkpv .pager { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;
                 padding-top: 1.4rem; border-top: 1px solid rgba(0,0,0,.12); }
  .mkpv .step { display: flex; align-items: center; gap: .8rem; padding: .6rem;
                border: 1px solid rgba(0,0,0,.10); text-decoration: none; color: #111; }
  .mkpv .step img { width: 160px; height: 90px; object-fit: cover; flex: none; }
  .mkpv .step small { display: block; font-size: .7rem; letter-spacing: .08em;
                      text-transform: uppercase; color: #6b6b6b; }
  .mkpv .step b { font-size: .92rem; line-height: 1.25; }
  .mkpv .sibs { display: grid; grid-template-columns: repeat(auto-fill, minmax(11rem, 1fr));
                gap: 1rem; margin: 1rem 0 0; }
  .mkpv .sib { text-decoration: none; color: #111; display: block; }
  .mkpv .sib img { width: 100%; aspect-ratio: 16/9; object-fit: cover; display: block; }
  .mkpv .sib b { display: block; font-size: .86rem; line-height: 1.25; margin: .4rem 0 0; }
  .mkpv .sib span { font-size: .72rem; color: #6b6b6b; font-variant-numeric: tabular-nums; }
  .mkpv .sib:hover b { color: #AE5224; }
  .mkpv .lab { font-family: Futura, 'Noto Sans', sans-serif; font-size: .82rem;
               letter-spacing: .06em; text-transform: uppercase; color: #6b6b6b;
               margin: 1.8rem 0 0; padding-top: 1.4rem;
               border-top: 1px solid rgba(0,0,0,.12); }
  .mkpv .back { margin: 1.4rem 0 0; font-size: .9rem; }
"""


def head(title, extra_css=''):
    return (
        '<!DOCTYPE html>\n<html lang="es">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>%s</title>\n'
        '<link rel="stylesheet" href="/styles/all.min.css">\n'
        '%s'
        '<style>%s</style>\n</head>\n<body>\n<div class="mk">\n'
        % (title, extra_css, CSS)
    )


TAIL = '</div>\n</body>\n</html>\n'


# ── 1. the footer venue column ──────────────────────────────────────────────
def build_footer():
    h = [head('Mockup · La columna de salas del pie')]
    h.append('<h1>El pie: «Dónde entrenamos»</h1>')
    h.append(
        '<p class="lede">La columna ya existe y ya nombra los cuatro sitios. '
        'Lo que hace es llevar a <code>/acceso/</code> con un ancla, no a las '
        'páginas de cada ciudad. Cambiarlo son tres URL en '
        '<code>_data/footer.yml</code>: ni una etiqueta nueva, ni una línea de '
        'marcado, ni una cadena que traducir cuatro veces.</p>')

    h.append('<p class="note"><b>Por qué importa.</b> El pie sale en las 136 '
             'páginas del sitio. <code>/badalona/</code> tiene hoy <b>9</b> '
             'enlaces internos entrantes y es la página que aparece en '
             'posición 5,64 con 88 impresiones y <b>cero clics</b>; '
             '<code>/barcelona/</code> es la que persigue las 405 impresiones '
             'de «aikido barcelona». Son las dos páginas peor enlazadas del '
             'sitio y las dos que más tráfico tienen delante.</p>')

    # ── current ──
    h.append('<h2>Ahora <span class="tag now">actual</span></h2>')
    h.append('<p class="note">Cinco filas. Las cuatro primeras van al selector '
             'de <code>/acceso/</code>, que responde «por dónde se entra». '
             'Ninguna lleva a la página de la ciudad.</p>')
    h.append('<div class="frame"><div class="mkft"><nav>'
             '<h3>Dónde entrenamos</h3><ul>')
    for label, url in FT:
        h.append('<li><a href="#">%s<span class="u">%s</span></a></li>' % (label, url))
    h.append('</ul></nav></div></div>')

    # ── A ──
    h.append('<h2>Propuesta A · mínima <span class="tag">3 URL</span></h2>')
    h.append('<p class="note">Las mismas cinco filas y las mismas etiquetas. '
             'Sólo cambian tres destinos: cada ciudad va a su página. La '
             'Universidad de Barcelona mantiene su ancla porque es una sala '
             'dentro de Barcelona, y «Cómo llegar» sigue yendo a '
             '<code>/acceso/</code>, que es donde están las puertas.</p>')
    h.append('<div class="frame"><div class="mkft"><nav>'
             '<h3>Dónde entrenamos</h3><ul>')
    amap = {'Badalona': '/badalona/',
            'Sant Adrià de Besòs': '/sant-adria-de-besos/',
            'Barcelona': '/barcelona/'}
    for label, url in FT:
        h.append('<li><a href="#">%s<span class="u">%s</span></a></li>'
                 % (label, amap.get(label, url)))
    h.append('</ul></nav></div></div>')
    h.append('<p class="why"><b>A favor.</b> Es el cambio más pequeño que '
             'existe y no toca nada que un lector reconozca. '
             '<b>En contra.</b> El pie deja de llevar directamente a la ficha '
             'de la sala: quien quiera la puerta tiene que pasar por «Cómo '
             'llegar». Y la columna se queda con cinco filas, una de las '
             'cuales nombra una sala y no una ciudad.</p>')

    # ── B ──
    h.append('<h2>Propuesta B · cuatro filas <span class="tag rec">recomendada</span></h2>')
    h.append('<p class="note">Tres ciudades y una salida. La Universidad de '
             'Barcelona deja de tener fila propia: es una sala dentro de '
             'Barcelona y <code>/barcelona/</code> la nombra, con su horario y '
             'su dirección. Coincide además con el criterio que ya seguimos en '
             'todo lo demás: <b>se nombran las ciudades donde hay presencia, '
             'no todas las salas</b>. Barcelona va primero.</p>')
    h.append('<div class="frame"><div class="mkft"><nav>'
             '<h3>Dónde entrenamos</h3><ul>')
    for label, url in [('Barcelona', '/barcelona/'),
                       ('Badalona', '/badalona/'),
                       ('Sant Adrià de Besòs', '/sant-adria-de-besos/'),
                       ('Cómo llegar a cada sala', '/acceso/')]:
        h.append('<li><a href="#">%s<span class="u">%s</span></a></li>' % (label, url))
    h.append('<li class="gone"><a href="#">Universidad de Barcelona'
             '<span class="u">se pliega dentro de /barcelona/</span></a></li>')
    h.append('</ul></nav></div></div>')
    h.append('<p class="why"><b>A favor.</b> La columna dice lo que su título '
             'promete: dónde entrenamos, por ciudades. Una fila menos, y la '
             'última es explícita sobre a qué lleva. '
             '<b>En contra.</b> Quien entrena en la UB pierde el atajo a su '
             'propia sala desde el pie. Sigue estando en <code>/acceso/</code> '
             'y en <code>/barcelona/</code>, a un clic más.</p>')

    # ── the numbers ──
    h.append('<h2>Lo que cambia, en números</h2>')
    h.append('<table><tr><th>Página</th><th class="n">Enlaces entrantes hoy</th>'
             '<th class="n">Con A o con B</th></tr>')
    for label, url, _ in TOWNS:
        h.append('<tr><td><code>%s</code></td><td class="n">9</td>'
                 '<td class="n">~140</td></tr>' % url)
    h.append('<tr><td><code>/acceso/</code></td><td class="n">~140</td>'
             '<td class="n">~140 (A) · ~140 (B)</td></tr>')
    h.append('</table>')
    h.append('<p class="why">El pie está en las 136 páginas, así que cualquiera '
             'de las dos lleva las tres páginas de ciudad de 9 enlaces a todas '
             'las del sitio. <code>/acceso/</code> no pierde nada: conserva su '
             'fila en las dos propuestas, y las tres páginas de ciudad enlazan '
             'a <code>/acceso/</code> desde su propio cuerpo.</p>')
    h.append('<p class="why"><b>Un aviso honesto.</b> Un enlace repetido en '
             'todas las páginas vale menos, para Google, que un enlace escrito '
             'dentro de un texto. Esto no sustituye a enlazar las ciudades '
             'desde donde vengan a cuento; lo que hace es que dejen de ser las '
             'páginas peor conectadas del sitio.</p>')

    h.append(TAIL)
    io.open(OUT_FT, 'w', encoding='utf-8').write('\n'.join(h))


# ── 2. the watch-page siblings ──────────────────────────────────────────────
def build_video():
    # the page we are drawing: the third of six, so it has a neighbour on both
    # sides and three videos the pager cannot reach.
    me = 2
    others = [v for i, v in enumerate(VIDS) if i != me]
    prev_v, next_v = VIDS[me - 1], VIDS[me + 1]
    far = [v for v in others if v not in (prev_v, next_v)]

    def thumb(v):
        return '/images/%s.jpg' % v[2]

    def year(v):
        return v[0][:4]

    h = [head('Mockup · Vídeos hermanos en la página de un vídeo',
              '<link rel="stylesheet" href="/styles/press.min.css">\n')]
    h.append('<h1>La página de un vídeo: qué va al final</h1>')
    h.append(
        '<p class="lede">Hay seis vídeos y cada uno tiene su página en cuatro '
        'idiomas: veinticuatro páginas. Hoy cada una enlaza a <b>una</b> '
        'hermana por el paginador y al índice. Veintiuna de las veinticuatro '
        'están entre las cuarenta y cinco páginas que Google ha descubierto y '
        'no ha rastreado nunca: es el grupo más grande de esa lista.</p>')
    h.append('<p class="note">Se dibuja el final de <i>%s</i>, que es el '
             'tercero de seis y por tanto tiene vecino a los dos lados y tres '
             'vídeos que el paginador no alcanza.</p>' % VIDS[me][1])

    # ── current ──
    h.append('<h2>Ahora <span class="tag now">actual</span></h2>')
    h.append('<div class="frame light"><div class="mkpv">')
    h.append('<div class="pager">')
    for lab, v in (('Más reciente', prev_v), ('Anterior', next_v)):
        h.append('<a class="step" href="#"><img src="%s" alt="">'
                 '<span><small>%s</small><b>%s</b></span></a>' % (thumb(v), lab, v[1]))
    h.append('</div>')
    h.append('<p class="back"><a href="#">Ver todos los vídeos</a></p>')
    h.append('</div></div>')
    h.append('<p class="why">Dos hermanas nombradas, tres invisibles, y un '
             'enlace al índice. <b>Dos enlaces editoriales entrantes por '
             'página</b>, contando el mapa del sitio que se añadió el 18 de '
             'septiembre.</p>')

    # ── A ──
    h.append('<h2>Propuesta A · el paginador se queda <span class="tag">+3</span></h2>')
    h.append('<p class="note">El paginador sigue igual y debajo aparecen los '
             'vídeos que no alcanza.</p>')
    h.append('<div class="frame light"><div class="mkpv">')
    h.append('<div class="pager">')
    for lab, v in (('Más reciente', prev_v), ('Anterior', next_v)):
        h.append('<a class="step" href="#"><img src="%s" alt="">'
                 '<span><small>%s</small><b>%s</b></span></a>' % (thumb(v), lab, v[1]))
    h.append('</div>')
    h.append('<p class="lab">Los demás vídeos</p><div class="sibs">')
    for v in far:
        h.append('<a class="sib" href="#"><img src="%s" alt="">'
                 '<b>%s</b><span>%s</span></a>' % (thumb(v), v[1], year(v)))
    h.append('</div>')
    h.append('<p class="back"><a href="#">Ver todos los vídeos</a></p>')
    h.append('</div></div>')
    h.append('<p class="why"><b>A favor.</b> No quita nada. '
             '<b>En contra.</b> Dos componentes haciendo el mismo trabajo, uno '
             'encima del otro, y el lector tiene que entender por qué dos de '
             'los cinco están arriba con marco y los otros tres abajo sin él. '
             'La respuesta —que uno es cronológico y el otro no— es verdadera '
             'y no se ve.</p>')

    # ── B ──
    h.append('<h2>Propuesta B · una sola rejilla <span class="tag rec">recomendada</span></h2>')
    h.append('<p class="note">El paginador se retira y en su lugar van los '
             'cinco, del más reciente al más antiguo, cada uno con su año. El '
             'orden sigue siendo cronológico; lo que desaparece es la pareja '
             'de flechas, no la cronología.</p>')
    h.append('<div class="frame light"><div class="mkpv">')
    h.append('<p class="lab">Los otros cinco vídeos</p><div class="sibs">')
    for v in others:
        h.append('<a class="sib" href="#"><img src="%s" alt="">'
                 '<b>%s</b><span>%s</span></a>' % (thumb(v), v[1], year(v)))
    h.append('</div>')
    h.append('<p class="back"><a href="#">Ver todos los vídeos</a></p>')
    h.append('</div></div>')
    h.append('<p class="why"><b>A favor.</b> Un componente en lugar de dos, la '
             'colección entera visible, y el año hace el trabajo que hacían '
             '«Más reciente» y «Anterior». '
             '<b>En contra.</b> Retira algo que se decidió a conciencia: '
             'CLAUDE.md explica que el paginador dice «Más reciente / Anterior» '
             'y no «Anterior / Siguiente» porque una flecha en una lista '
             'ordenada por fecha es ambigua. Esa decisión sigue siendo buena; '
             'lo que cambia es que con cinco fechas a la vista ya no hay nada '
             'ambiguo que resolver.</p>')
    h.append('<p class="why"><b>Dónde deja de servir.</b> Con seis vídeos '
             '«todos los demás» son cinco y caben. Con veinte no. Si la '
             'colección crece, la rejilla se recorta a los cinco más recientes '
             'y «Ver todos los vídeos» pasa a ser la salida de verdad. No hay '
             'que decidirlo hoy, pero conviene que esté escrito.</p>')

    # ── numbers ──
    h.append('<h2>Lo que cambia, en números</h2>')
    h.append('<table><tr><th>Por página de vídeo</th>'
             '<th class="n">Hoy</th><th class="n">A</th><th class="n">B</th></tr>'
             '<tr><td>Enlaces editoriales entrantes</td>'
             '<td class="n">2</td><td class="n">7</td><td class="n">7</td></tr>'
             '<tr><td>Enlaces hermanos salientes</td>'
             '<td class="n">2</td><td class="n">5</td><td class="n">5</td></tr>'
             '<tr><td>Componentes al final de la página</td>'
             '<td class="n">2</td><td class="n">3</td><td class="n">2</td></tr>'
             '</table>')
    h.append('<p class="why">Las dos dan el mismo resultado de enlaces: seis '
             'vídeos enlazándose entre todos son treinta enlaces hermanos, '
             'vengan en uno o en dos componentes. La diferencia entre A y B es '
             'de diseño, no de SEO.</p>')

    h.append(TAIL)
    io.open(OUT_PV, 'w', encoding='utf-8').write('\n'.join(h))


if __name__ == '__main__':
    build_footer()
    build_video()
    print('wrote %s' % os.path.relpath(OUT_FT, ROOT))
    print('wrote %s' % os.path.relpath(OUT_PV, ROOT))
