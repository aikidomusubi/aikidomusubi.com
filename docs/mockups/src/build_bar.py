# -*- coding: utf-8 -*-
"""Two proposals for the sticky search-and-filter bar, on both pages that have one.

Renders four files into docs/mockups/:

    bar-glosario-a.html   proposal A on the glossary
    bar-glosario-b.html   proposal B on the glossary
    bar-recursos-a.html   proposal A on Resources
    bar-recursos-b.html   proposal B on Resources

A and B are the same two ideas both times, deliberately: whichever wins should
win on both pages, because the two bars are the same component with different
labels and a reader who learns one has learnt the other.

The content is real. The glossary terms come from _gloss.py — the same 123 the
approved mockup used — and the Resources rows are read straight out of
_data/resources.yml by the small parser below, so the chip counts and the label
lengths are the ones that actually have to wrap.
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _gloss as G
import _bar as B

HERE = os.path.dirname(os.path.abspath(__file__))          # docs/mockups/src
OUT = os.path.dirname(HERE)                                # docs/mockups
ROOT = os.path.dirname(os.path.dirname(OUT))               # the repo


# ---------------------------------------------------------------------------
# Resources, read out of the YAML rather than copied into this file
#
# No PyYAML: it is deliberately not a project dependency (see CLAUDE.md), and a
# mockup builder is the last place that should be the thing to introduce it.
# The shape here is regular enough that a line reader is honest about it.
# ---------------------------------------------------------------------------
def read_resources():
    src = io.open(os.path.join(ROOT, '_data', 'resources.yml'), encoding='utf-8')
    groups, g, it, want_desc = [], None, None, False
    for raw in src:
        line = raw.rstrip('\n')
        m = re.match(r'^  - id: (\S+)', line)
        if m:
            g = {'id': m.group(1), 'name': '', 'sub': '', 'items': []}
            groups.append(g)
            it = None
            continue
        if g is None:
            continue
        m = re.match(r'^    name: \{ es: "([^"]+)"', line)
        if m:
            g['name'] = m.group(1)
            continue
        m = re.match(r'^      es: "([^"]+)"', line)
        if m and not g['sub']:
            g['sub'] = m.group(1)
            continue
        m = re.match(r'^      - kind: (\S+)', line)
        if m:
            it = {'kind': m.group(1), 'title': '', 'desc': '', 'draft': False}
            g['items'].append(it)
            want_desc = False
            continue
        if it is None:
            continue
        if re.match(r'^        draft: true', line):
            it['draft'] = True
            continue
        m = re.match(r'^        title: \{ es: "([^"]+)"', line)
        if m:
            it['title'] = m.group(1)
            continue
        if re.match(r'^        desc:', line):
            want_desc = True
            continue
        m = re.match(r'^          es: "?(.+?)"?$', line)
        if m and want_desc and not it['desc']:
            it['desc'] = m.group(1)
            want_desc = False
    for grp in groups:
        grp['items'] = [i for i in grp['items'] if not i['draft'] and i['title']]
    return [g for g in groups if g['items']]


KINDS = {'form': 'Formulario', 'doc': 'Documento', 'page': 'Página',
         'book': 'Libro', 'video': 'Vídeo'}


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))


# ---------------------------------------------------------------------------
# The two datasets, normalised to one shape:
#   cats  [(id, name, sub, [row-html, …])]
# ---------------------------------------------------------------------------
def gloss_data():
    cats = []
    for cid, name, sub, terms in G.CATS:
        rows = []
        for k, r, d in terms:
            hay = esc('%s %s %s' % (k, r, d))
            rows.append('<div class="t" data-cat="%s" data-s="%s">'
                        '<p class="k jp">%s</p><p class="r">%s</p>'
                        '<p class="d">%s</p></div>'
                        % (cid, hay, esc(k), esc(r), esc(d)))
        cats.append((cid, name, sub, rows))
    return cats


def res_data():
    cats = []
    for g in read_resources():
        rows = []
        for i in g['items']:
            hay = esc('%s %s' % (i['title'], i['desc']))
            rows.append('<div class="t" data-cat="%s" data-s="%s">'
                        '<p class="kind">%s</p><p class="r">%s</p>'
                        '<p class="d">%s</p></div>'
                        % (g['id'], hay, KINDS.get(i['kind'], 'Recurso'),
                           esc(i['title']), esc(i['desc'])))
        cats.append((g['id'], g['name'], g['sub'], rows))
    return cats


def lists(cats):
    out = []
    for cid, name, sub, rows in cats:
        out.append('<section class="grp" id="g-%s"><div class="gh"><h3>%s</h3>'
                   '<span>%s</span></div>%s</section>'
                   % (cid, esc(name), esc(sub), ''.join(rows)))
    out.append('<p class="empty" id="empty" hidden>Nada coincide con la búsqueda.</p>')
    out.append('<div class="tail">El pie de página va aquí.</div>')
    return ''.join(out)


# ===========================================================================
# PROPOSAL A — one line, and a drawer
# ===========================================================================
A_CSS = """
.bar{position:sticky;top:49px;z-index:8;background:rgba(255,255,255,.97);
  border-bottom:1px solid var(--hair)}
@supports (backdrop-filter:blur(10px)){.bar{backdrop-filter:blur(10px)}}
.bar-row{display:flex;align-items:center;gap:.45rem;padding:.5rem 1rem}
.bar-row input{flex:1;min-width:7.5rem;height:38px;padding:0 .7rem;border:1px solid var(--line);
  border-radius:0;background:#fff;font:inherit;font-size:.88rem;color:var(--ink)}
.bar-row input:focus{outline:2px solid var(--acc);outline-offset:-1px;border-color:var(--ink)}
.tally{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.1em;color:var(--mute);font-variant-numeric:tabular-nums;
  white-space:nowrap}
.fbtn{display:inline-flex;align-items:center;gap:.4rem;height:38px;padding:0 .7rem;
  border:1px solid var(--line);background:#fff;cursor:pointer;
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.14em;text-transform:uppercase;color:var(--mute);white-space:nowrap}
.fbtn svg{width:13px;height:13px;flex:none}
.fbtn[aria-expanded="true"]{border-color:var(--ink);color:var(--ink)}
.fbtn[data-active]{background:var(--ink);border-color:var(--ink);color:#fff;
  max-width:8.5rem}
.fbtn span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.drawer{padding:.15rem 1rem .8rem}
.drawer[hidden]{display:none}
.chips{display:flex;flex-wrap:wrap;gap:.35rem}
.chips button{display:inline-flex;align-items:center;gap:.4rem;min-height:2rem;
  padding:.25rem .75rem;border:1px solid rgba(17,19,20,.08);border-radius:2rem;
  background:#fff;font:inherit;font-size:.78rem;line-height:1.2;color:var(--mute);
  cursor:pointer}
.chips button i{font-style:normal;font-size:.66rem;font-variant-numeric:tabular-nums}
.chips button[data-on]{background:var(--ink);border-color:var(--ink);color:#fff}
.chips button[data-on] i{color:var(--acc)}
"""

A_HTML = """
<div class="stick-wrap">
  <div class="mnav"><b>MUSUBI</b><i></i></div>
  <div class="bar">
    <div class="bar-row">
      <input id="q" type="search" placeholder="%(ph)s" aria-label="%(lab)s" autocomplete="off">
      <p class="tally" id="count">%(total)d</p>
      <button class="fbtn" id="fbtn" type="button" aria-expanded="false" aria-controls="drawer">
        <svg viewBox="0 0 16 16" aria-hidden="true"><path fill="currentColor"
          d="M1 3h14v2H1zM3.5 7h9v2h-9zM6 11h4v2H6z"/></svg>
        <span id="fbtn-l">Filtrar</span>
      </button>
    </div>
    <div class="drawer" id="drawer" hidden>
      <div class="chips" role="group" aria-label="Filtrar por categoría">%(chips)s</div>
    </div>
  </div>
</div>
<div class="head"><h2>%(h)s</h2><p>%(sub)s</p></div>
%(list)s
"""

A_JS = """<script>
(function(){
  var q=document.getElementById('q'), fb=document.getElementById('fbtn'),
      fl=document.getElementById('fbtn-l'), dr=document.getElementById('drawer'),
      chips=[].slice.call(document.querySelectorAll('.chips button')),
      items=[].slice.call(document.querySelectorAll('.t')),
      groups=[].slice.call(document.querySelectorAll('.grp')),
      count=document.getElementById('count'), cat='all', TOTAL=%(total)d;
  function norm(s){return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();}
  function run(){
    var term=norm(q.value.trim()), n=0;
    items.forEach(function(it){
      var on=(cat==='all'||it.dataset.cat===cat)&&(!term||norm(it.dataset.s).indexOf(term)>-1);
      it.hidden=!on; if(on)n++;
    });
    groups.forEach(function(g){g.hidden=!g.querySelector('.t:not([hidden])');});
    count.textContent=n;
    document.getElementById('empty').hidden=n>0;
  }
  fb.addEventListener('click',function(){
    var open=fb.getAttribute('aria-expanded')==='true';
    fb.setAttribute('aria-expanded',String(!open)); dr.hidden=open;
  });
  chips.forEach(function(c){c.addEventListener('click',function(){
    chips.forEach(function(x){x.removeAttribute('data-on');});
    c.setAttribute('data-on',''); cat=c.dataset.cat;
    if(cat==='all'){fl.textContent='Filtrar'; fb.removeAttribute('data-active');}
    else{fl.textContent=c.dataset.label; fb.setAttribute('data-active','');}
    dr.hidden=true; fb.setAttribute('aria-expanded','false');
    run();
  });});
  q.addEventListener('input',run);
  run();
})();
</script>"""


# ===========================================================================
# PROPOSAL B — the bar shrinks when it sticks
# ===========================================================================
B_CSS = """
.sentinel{height:1px}
.bar{position:sticky;top:49px;z-index:8;background:rgba(255,255,255,.97);
  border-bottom:1px solid var(--hair)}
@supports (backdrop-filter:blur(10px)){.bar{backdrop-filter:blur(10px)}}
.bar-in{padding:.75rem 1rem .7rem}
.search{display:flex;gap:.4rem;margin-bottom:.55rem}
.search input{flex:1;min-width:0;height:38px;padding:0 .7rem;border:1px solid var(--line);
  border-radius:0;background:#fff;font:inherit;font-size:.88rem;color:var(--ink)}
.search input:focus{outline:2px solid var(--acc);outline-offset:-1px;border-color:var(--ink)}
.search button{padding:0 .8rem;border:1px solid var(--line);background:none;cursor:pointer;
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.6rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--mute)}
.rail{display:flex;gap:.35rem;flex-wrap:wrap}
.rail button{display:inline-flex;align-items:center;gap:.4rem;min-height:2rem;
  padding:.25rem .75rem;border:1px solid rgba(17,19,20,.08);border-radius:2rem;
  background:#fff;font:inherit;font-size:.78rem;line-height:1.2;color:var(--mute);
  cursor:pointer;white-space:nowrap;flex:none}
.rail button i{font-style:normal;font-size:.66rem;font-variant-numeric:tabular-nums}
.rail button[data-on]{background:var(--ink);border-color:var(--ink);color:#fff}
.rail button[data-on] i{color:var(--acc)}
.tally{margin-top:.5rem;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.6rem;
  letter-spacing:.16em;text-transform:uppercase;color:var(--mute)}

/* ---- stuck ------------------------------------------------------------- */
.bar.is-stuck .bar-in{padding:.45rem 0 .4rem}
.bar.is-stuck .search{margin:0 1rem .4rem}
.bar.is-stuck .search input{height:34px;font-size:.84rem}
.bar.is-stuck .search button{display:none}
.bar.is-stuck .tally{display:none}
.bar.is-stuck .rail{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;
  padding:0 1rem .1rem;scroll-padding-left:1rem;
  -webkit-mask-image:linear-gradient(90deg,#000 calc(100% - 2.2rem),transparent);
  mask-image:linear-gradient(90deg,#000 calc(100% - 2.2rem),transparent)}
.bar.is-stuck .rail::-webkit-scrollbar{display:none}
.bar.is-stuck .rail button:first-child{position:sticky;left:0;z-index:1;
  box-shadow:0 0 0 4px rgba(255,255,255,.97)}
.bar.is-stuck .rail .stuck-tally{display:inline-flex}
.rail .stuck-tally{display:none;border:0;background:none;color:var(--mute);
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.6rem;letter-spacing:.14em;
  text-transform:uppercase;cursor:default;padding-right:1.6rem}
"""

B_HTML = """
<div class="stick-wrap">
  <div class="mnav"><b>MUSUBI</b><i></i></div>
</div>
<div class="head"><h2>%(h)s</h2><p>%(sub)s</p></div>
<div class="sentinel" id="sentinel"></div>
<div class="bar" id="bar">
  <div class="bar-in">
    <div class="search">
      <input id="q" type="search" placeholder="%(ph)s" aria-label="%(lab)s" autocomplete="off">
      <button id="clear" type="button">Limpiar</button>
    </div>
    <div class="rail" role="group" aria-label="Filtrar por categoría">%(chips)s
      <span class="stuck-tally" aria-hidden="true"><span id="count2">%(total)d</span></span>
    </div>
    <p class="tally" id="count">%(total)d %(unit)s</p>
  </div>
</div>
%(list)s
"""

B_JS = """<script>
(function(){
  var q=document.getElementById('q'), bar=document.getElementById('bar'),
      chips=[].slice.call(document.querySelectorAll('.rail button')),
      items=[].slice.call(document.querySelectorAll('.t')),
      groups=[].slice.call(document.querySelectorAll('.grp')),
      count=document.getElementById('count'), count2=document.getElementById('count2'),
      cat='all', UNIT='%(unit)s';
  function norm(s){return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();}
  function run(){
    var term=norm(q.value.trim()), n=0;
    items.forEach(function(it){
      var on=(cat==='all'||it.dataset.cat===cat)&&(!term||norm(it.dataset.s).indexOf(term)>-1);
      it.hidden=!on; if(on)n++;
    });
    groups.forEach(function(g){g.hidden=!g.querySelector('.t:not([hidden])');});
    count.textContent=n+' '+UNIT; count2.textContent=n;
    document.getElementById('empty').hidden=n>0;
  }
  chips.forEach(function(c){c.addEventListener('click',function(){
    chips.forEach(function(x){x.removeAttribute('data-on');});
    c.setAttribute('data-on',''); cat=c.dataset.cat; run();
  });});
  q.addEventListener('input',run);
  document.getElementById('clear').addEventListener('click',function(){
    q.value=''; cat='all'; chips.forEach(function(x){x.removeAttribute('data-on');});
    chips[0].setAttribute('data-on',''); run(); q.focus();
  });
  // A 1px sentinel above the bar, watched inside the phone's own scroller.
  // No scroll listener: the observer fires twice per journey, on the way in
  // and on the way out.
  var root=document.querySelector('.phone');
  new IntersectionObserver(function(es){
    bar.classList.toggle('is-stuck', !es[0].isIntersecting);
  },{root:root,rootMargin:'-50px 0px 0px 0px',threshold:0}
  ).observe(document.getElementById('sentinel'));
  run();
})();
</script>"""


# ---------------------------------------------------------------------------
def chips_html(cats, total, cls_attr=''):
    out = ['<button data-cat="all" data-label="Todas" data-on%s>Todas <i>%d</i></button>'
           % (cls_attr, total)]
    for cid, name, sub, rows in cats:
        out.append('<button data-cat="%s" data-label="%s">%s <i>%d</i></button>'
                   % (cid, esc(name), esc(name), len(rows)))
    return ''.join(out)


def build(kind, cats, meta):
    total = sum(len(r) for _, _, _, r in cats)
    body = lists(cats)
    chips = chips_html(cats, total)
    common = dict(meta, chips=chips, list=body, total=total)

    # ---- A ----
    a = B.page(
        meta['title_a'], meta['kicker'], meta['h1_a'], meta['lede_a'],
        A_HTML % common, notes_a(meta, total, len(cats)),
        A_CSS, A_JS % {'total': total})
    io.open(os.path.join(OUT, 'bar-%s-a.html' % kind), 'w', encoding='utf-8').write(a)

    # ---- B ----
    b = B.page(
        meta['title_b'], meta['kicker'], meta['h1_b'], meta['lede_b'],
        B_HTML % common, notes_b(meta, total, len(cats)),
        B_CSS, B_JS % {'unit': meta['unit']})
    io.open(os.path.join(OUT, 'bar-%s-b.html' % kind), 'w', encoding='utf-8').write(b)


def notes_a(m, total, ncat):
    return """
<section>
  <h2>La medida</h2>
  <div class="fig">
    <div><b>%(now)dpx</b><span>Barra actual</span></div>
    <div class="down"><b>55px</b><span>Propuesta A</span></div>
    <div class="down"><b>&minus;%(cut)d%%</b><span>De alto</span></div>
  </div>
  <p>En una pantalla de 667px de alto, la barra de %(name)s ocupa hoy
     <strong>%(now)dpx, el %(pct)d%% de la ventana</strong>: %(chips)d chips repartidos
     en %(rows)d filas, más el buscador y el recuento. Con los 49px de la
     navegación encima, la mayor parte del móvil es mobiliario.</p>
</section>
<section>
  <h2>Qué hace</h2>
  <p>La barra fija es siempre <strong>una sola línea</strong>: buscador, recuento y un
     botón de filtro. Los chips viven en un cajón que se abre debajo y empuja la
     lista, no la tapa. Al elegir uno, el cajón se cierra y el botón pasa a llevar
     el nombre de la categoría activa, así que el estado se ve sin abrir nada.</p>
  <ul>
    <li><span class="tick">&#10003;</span> Nada se esconde tras un borde: al abrir el cajón están los %(chips)d.</li>
    <li><span class="tick">&#10003;</span> El recuento sigue a la vista mientras escribes.</li>
    <li><span class="tick">&#10003;</span> Sin JavaScript la barra no se muestra, igual que ahora.</li>
    <li><span class="cross">&#10007;</span> Filtrar cuesta dos toques en vez de uno.</li>
    <li><span class="cross">&#10007;</span> El conjunto de categorías deja de verse de un vistazo.</li>
    <li><span class="cross">&#10007;</span> Un nombre largo en el botón se corta: «Programa de exam…».</li>
  </ul>
</section>
<section>
  <h2>En el escritorio</h2>
  <p>No cambia. Por encima de 768px los chips caben en una o dos filas y la barra
     completa es mejor que un cajón: el botón y el cajón son una regla de móvil,
     no un modo nuevo.</p>
</section>
<section>
  <h2>Lo que costaría</h2>
  <p>El marcado ya existe. Los chips se envuelven en el cajón, se añade el botón
     y unas quince líneas de LESS bajo el punto de ruptura. El script gana una
     función: abrir, cerrar y escribir la etiqueta activa.</p>
</section>
""" % dict(now=m['now'], pct=m['pct'], cut=round((m['now'] - 55) * 100.0 / m['now']),
           chips=ncat + 1, rows=m['rows'], name=m['name'])


def notes_b(m, total, ncat):
    return """
<section>
  <h2>La medida</h2>
  <div class="fig">
    <div><b>%(now)dpx</b><span>Barra actual</span></div>
    <div class="down"><b>89px</b><span>Propuesta B</span></div>
    <div class="down"><b>&minus;%(cut)d%%</b><span>De alto</span></div>
  </div>
  <p>Mismo punto de partida que la propuesta A: %(now)dpx, el %(pct)d%% de la
     ventana, %(chips)d chips en %(rows)d filas.</p>
</section>
<section>
  <h2>Qué hace</h2>
  <p>Arriba del todo, mientras eliges, la barra es la de siempre: buscador,
     todos los chips y el recuento. <strong>En cuanto se pega bajo la navegación se
     encoge</strong> a dos líneas cortas, y los chips pasan a una fila que se
     desplaza en horizontal con <em>Todas</em> anclada a la izquierda.</p>
  <ul>
    <li><span class="tick">&#10003;</span> Filtrar sigue siendo un solo toque.</li>
    <li><span class="tick">&#10003;</span> Al llegar a la página se ven las %(chips)d categorías enteras.</li>
    <li><span class="tick">&#10003;</span> Sin modos: no hay nada que abrir ni que cerrar.</li>
    <li><span class="cross">&#10007;</span> Una vez pegada, hay chips escondidos tras el borde derecho.</li>
    <li><span class="cross">&#10007;</span> La barra cambia de forma sola, y eso hay que hacerlo bien para que no sobresalte.</li>
  </ul>
</section>
<section>
  <h2>El borde derecho</h2>
  <p>Es justo lo que <code>styles/%(less)s</code> descartó al construir la página:
     un carrusel esconde opciones sin decir que están ahí. Aquí se compensa con
     tres cosas &mdash; el degradado que corta la fila a la derecha, <em>Todas</em>
     anclada para volver siempre, y el hecho de que arriba se han visto todas.
     Aun así es el punto flojo de esta propuesta, y conviene decirlo.</p>
</section>
<section>
  <h2>Cómo se sabe que está pegada</h2>
  <p>Con un <code>IntersectionObserver</code> sobre un centinela de 1px encima de
     la barra. No hay escucha de <em>scroll</em>: el observador salta dos veces por
     viaje, al entrar y al salir. Es la misma técnica que encoge la navegación.</p>
</section>
""" % dict(now=m['now'], pct=m['pct'], cut=round((m['now'] - 89) * 100.0 / m['now']),
           chips=ncat + 1, rows=m['rows'], less=m['less'])


GLOSS = {
    'kicker': 'Propuesta &middot; barra fija en móvil',
    'title_a': 'Glosario · barra A — Aikido Musubi',
    'title_b': 'Glosario · barra B — Aikido Musubi',
    'h1_a': 'Glosario &middot; A',
    'h1_b': 'Glosario &middot; B',
    'lede_a': 'Una línea fija y un cajón de filtros. La barra deja de ocupar '
              'media pantalla y los chips siguen estando todos.',
    'lede_b': 'La barra completa arriba y encogida en cuanto se pega. Filtrar '
              'sigue costando un toque.',
    'h': 'Glosario',
    'sub': 'Las palabras que se oyen en el tatami, ordenadas por dónde te las '
           'encuentras y no por el alfabeto.',
    'ph': 'Buscar en kanji, rōmaji o significado…',
    'lab': 'Buscar en el glosario',
    'unit': 'entradas',
    'name': 'Glosario',
    'now': 389, 'pct': 58, 'rows': 5, 'less': 'glossary.less',
}

RES = {
    'kicker': 'Propuesta &middot; barra fija en móvil',
    'title_a': 'Recursos · barra A — Aikido Musubi',
    'title_b': 'Recursos · barra B — Aikido Musubi',
    'h1_a': 'Recursos &middot; A',
    'h1_b': 'Recursos &middot; B',
    'lede_a': 'La misma línea fija y el mismo cajón que en el glosario. Una '
              'decisión, dos páginas.',
    'lede_b': 'El mismo encogido al pegarse que en el glosario. Una decisión, '
              'dos páginas.',
    'h': 'Recursos',
    'sub': 'Los papeles, los programas de examen, las guías de armas y lo que '
           'hay para leer.',
    'ph': 'Buscar un documento o un vídeo…',
    'lab': 'Buscar en los recursos',
    'unit': 'recursos',
    'name': 'Recursos',
    'now': 274, 'pct': 41, 'rows': 4, 'less': 'resources.less',
}


if __name__ == '__main__':
    build('glosario', gloss_data(), GLOSS)
    build('recursos', res_data(), RES)
    print('bar mockups → docs/mockups/bar-{glosario,recursos}-{a,b}.html')
