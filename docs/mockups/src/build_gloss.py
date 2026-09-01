# -*- coding: utf-8 -*-
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _gloss as G

ROOT = '/Applications/MAMP/htdocs/aikidomusubi.com'
OUT = os.path.join(ROOT, '_site', 'mockups')

HEAD = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Glosario — Aikido Musubi</title>
<link rel="stylesheet" href="/styles/all.min.css">
<style>
:root{--ink:#111314;--mute:#5c6a70;--line:rgba(17,19,20,.13);--acc:#FFF200}
html,body{margin:0;background:#fff;color:var(--ink);
  font-family:'Noto Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
*{box-sizing:border-box}
.w{max-width:1140px;margin:0 auto;padding:0 6rem}
@media(max-width:991.98px){.w{padding:0 4rem}}
@media(max-width:767.98px){.w{padding:0 2rem}}
h1,h2,h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;margin:0;
  letter-spacing:.04em}
p{margin:0}
.jp{font-family:'Hiragino Sans','Noto Sans JP','Yu Gothic',sans-serif}
mark{background:#FFF200;color:inherit;padding:0 .1em}
%s
</style></head><body>"""

TOP = """
<header class="g-top w">
  <h1>Glosario</h1>
  <p class="lede">Las palabras que se oyen en el tatami: japonés de dojo, términos de aikido
     y vocabulario de artes marciales. %d entradas, ordenadas por dónde te las encuentras
     y no por el alfabeto.</p>
</header>""" % G.TOTAL

TOP_CSS = """
.g-top{padding:3.2rem 0 2rem}
.g-top h1{font-size:2.6rem;text-transform:uppercase;letter-spacing:.06em}
.g-top .lede{margin-top:1.1rem;max-width:44rem;font-size:1.05rem;line-height:1.75;color:#2c3437}
@media(max-width:575.98px){.g-top h1{font-size:1.9rem}}
"""

JS = """
<script>
(function(){
  var q=document.getElementById('q'), chips=[].slice.call(document.querySelectorAll('[data-cat]')),
      items=[].slice.call(document.querySelectorAll('.t')),
      groups=[].slice.call(document.querySelectorAll('.grp')),
      count=document.getElementById('count'), cat='all';
  function norm(s){return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();}
  function run(){
    var term=norm(q.value.trim()), n=0;
    items.forEach(function(it){
      var okC = cat==='all' || it.dataset.cat===cat;
      var okQ = !term || norm(it.dataset.s).indexOf(term)>-1;
      var on = okC && okQ;
      it.hidden = !on; if(on) n++;
    });
    groups.forEach(function(g){
      g.hidden = !g.querySelector('.t:not([hidden])');
    });
    count.textContent = n===%d ? '%d entradas' : (n===1 ? '1 entrada' : n+' entradas');
    document.getElementById('empty').hidden = n>0;
  }
  q.addEventListener('input',run);
  chips.forEach(function(c){c.addEventListener('click',function(){
    chips.forEach(function(x){x.removeAttribute('data-on');});
    c.setAttribute('data-on',''); cat=c.dataset.cat; run();
    if(cat!=='all'){var g=document.getElementById('g-'+cat); if(g)g.scrollIntoView({block:'start'});}
  });});
  document.getElementById('clear').addEventListener('click',function(){
    q.value=''; cat='all'; chips.forEach(function(x){x.removeAttribute('data-on');});
    chips[0].setAttribute('data-on',''); run(); q.focus();
  });
})();
</script>""" % (G.TOTAL, G.TOTAL)


def controls():
    ch = ['<button data-cat="all" data-on>Todas</button>']
    for cid, name, _, items in G.CATS:
        ch.append('<button data-cat="%s">%s <i>%d</i></button>' % (cid, name, len(items)))
    return """
<div class="g-bar"><div class="w g-bar-in">
  <div class="g-search">
    <input id="q" type="search" placeholder="Buscar en kanji, rōmaji o significado…"
           aria-label="Buscar en el glosario" autocomplete="off">
    <button id="clear" type="button">Limpiar</button>
  </div>
  <div class="g-chips">%s</div>
  <p class="g-count"><span id="count">%d entradas</span></p>
</div></div>""" % (''.join(ch), G.TOTAL)


BAR_CSS = """
.g-bar{position:sticky;top:0;z-index:5;background:rgba(255,255,255,.96);
  backdrop-filter:blur(10px);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.g-bar-in{padding:1rem 6rem}
@media(max-width:991.98px){.g-bar-in{padding:1rem 4rem}}
@media(max-width:767.98px){.g-bar-in{padding:.9rem 2rem}}
.g-search{display:flex;gap:.5rem;margin-bottom:.85rem}
.g-search input{flex:1;min-width:0;font:inherit;font-size:.95rem;padding:.65rem .9rem;
  border:1px solid var(--line);background:#fff;color:var(--ink);border-radius:0}
.g-search input:focus{outline:2px solid var(--acc);outline-offset:-1px;border-color:var(--ink)}
.g-search button{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.14em;text-transform:uppercase;border:1px solid var(--line);background:none;
  color:var(--mute);padding:0 1rem;cursor:pointer}
.g-search button:hover{border-color:var(--ink);color:var(--ink)}
.g-chips{display:flex;gap:.4rem;flex-wrap:wrap}
.g-chips button{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.6rem;
  letter-spacing:.12em;text-transform:uppercase;border:1px solid var(--line);background:none;
  color:var(--mute);padding:.4rem .7rem;cursor:pointer;display:inline-flex;gap:.4rem;
  align-items:baseline}
.g-chips button i{font-style:normal;color:#98a2a6;font-size:.56rem}
.g-chips button:hover{border-color:var(--ink);color:var(--ink)}
.g-chips button[data-on]{background:var(--ink);color:#fff;border-color:var(--ink)}
.g-chips button[data-on] i{color:var(--acc)}
.g-count{margin-top:.8rem;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.6rem;
  letter-spacing:.16em;text-transform:uppercase;color:var(--mute)}
#empty{padding:3rem 0;color:var(--mute);font-size:.95rem}
"""

# ═══════════════════════════════════════════════════════════════════════════
# A · EL ÍNDICE — dense two-column list, search-first
# ═══════════════════════════════════════════════════════════════════════════
CSS_A = TOP_CSS + BAR_CSS + """
.ga{padding:2.4rem 0 5rem}
.ga .grp{margin-bottom:2.8rem}
.ga .gh{display:flex;align-items:baseline;gap:1rem;padding-bottom:.7rem;
  border-bottom:2px solid var(--ink);margin-bottom:.2rem}
.ga .gh h2{font-size:1.15rem;text-transform:uppercase;letter-spacing:.1em}
.ga .gh span{font-size:.82rem;color:var(--mute)}
.ga .list{columns:2;column-gap:3.4rem}
.ga .t{break-inside:avoid;display:grid;grid-template-columns:7.5rem 1fr;gap:1.2rem;
  padding:.85rem 0;border-bottom:1px solid var(--line);align-items:baseline}
.ga .k{font-size:1.15rem;color:var(--ink);line-height:1.3}
.ga .r{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.95rem;color:var(--ink);
  letter-spacing:.02em}
.ga .d{font-size:.87rem;line-height:1.65;color:var(--mute);margin-top:.2rem}
@media(max-width:991.98px){.ga .list{columns:1}}
@media(max-width:575.98px){.ga .t{grid-template-columns:1fr;gap:.15rem}}
"""


def body_a():
    o = [TOP, controls(), '<div class="ga w">']
    for cid, name, sub, items in G.CATS:
        o.append('<section class="grp" id="g-%s"><div class="gh"><h2>%s</h2>'
                 '<span>%s</span></div><div class="list">' % (cid, name, sub))
        for k, r, d in items:
            s = '%s %s %s' % (k, r, d)
            o.append('<div class="t" data-cat="%s" data-s="%s">'
                     '<p class="k jp">%s</p><div><p class="r">%s</p><p class="d">%s</p></div>'
                     '</div>' % (cid, s.replace('"', ''), k, r, d))
        o.append('</div></section>')
    o.append('<p id="empty" hidden>Ninguna palabra coincide. Prueba con otra cosa, o '
             '<a href="/contacto/">escríbenos</a> y la añadimos.</p>')
    o.append('</div>')
    return ''.join(o)


# ═══════════════════════════════════════════════════════════════════════════
# B · LAS FICHAS — sticky rail + cards, browsable
# ═══════════════════════════════════════════════════════════════════════════
CSS_B = TOP_CSS + BAR_CSS + """
.gb{padding:2.4rem 0 5rem;display:grid;grid-template-columns:11rem 1fr;gap:3.4rem;
  align-items:start}
.gb-rail{position:sticky;top:11rem;align-self:start}
.gb-rail ol{list-style:none;margin:0;padding:0}
.gb-rail li{margin-bottom:.6rem}
.gb-rail a{display:block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.12em;text-transform:uppercase;color:var(--mute);text-decoration:none;
  line-height:1.4}
.gb-rail a:hover{color:var(--ink)}
.gb-rail a i{font-style:normal;display:block;font-size:.56rem;color:#98a2a6}
.gb-col{min-width:0}
.gb .grp{margin-bottom:3rem}
.gb .gh{margin-bottom:1.2rem}
.gb .gh h2{font-size:1.5rem}
.gb .gh span{display:block;font-size:.85rem;color:var(--mute);margin-top:.3rem}
.gb .cards{display:grid;grid-template-columns:repeat(3,1fr);gap:2px;background:var(--line)}
.gb .t{background:#fff;padding:1.15rem 1.1rem 1.25rem}
.gb .k{font-size:1.6rem;color:var(--ink);line-height:1.2}
.gb .r{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.66rem;letter-spacing:.18em;
  text-transform:uppercase;color:#B04E17;margin:.45rem 0 .5rem}
.gb .d{font-size:.83rem;line-height:1.65;color:var(--mute)}
@media(max-width:991.98px){.gb{grid-template-columns:1fr;gap:0}.gb-rail{display:none}
  .gb .cards{grid-template-columns:1fr 1fr}}
@media(max-width:575.98px){.gb .cards{grid-template-columns:1fr}}
"""


def body_b():
    rail = ''.join('<li><a href="#g-%s">%s<i>%d</i></a></li>' % (c[0], c[1], len(c[3]))
                   for c in G.CATS)
    o = [TOP, controls(), '<div class="gb w">',
         '<nav class="gb-rail" aria-label="Categorías"><ol>%s</ol></nav>' % rail,
         '<div class="gb-col">']
    for cid, name, sub, items in G.CATS:
        o.append('<section class="grp" id="g-%s"><div class="gh"><h2>%s</h2>'
                 '<span>%s</span></div><div class="cards">' % (cid, name, sub))
        for k, r, d in items:
            s = '%s %s %s' % (k, r, d)
            o.append('<div class="t" data-cat="%s" data-s="%s">'
                     '<p class="k jp">%s</p><p class="r">%s</p><p class="d">%s</p></div>'
                     % (cid, s.replace('"', ''), k, r, d))
        o.append('</div></section>')
    o.append('<p id="empty" hidden>Ninguna palabra coincide. Prueba con otra cosa, o '
             '<a href="/contacto/">escríbenos</a> y la añadimos.</p>')
    o.append('</div></div>')
    return ''.join(o)


for name, css, body in (('glosario-a.html', CSS_A, body_a()),
                        ('glosario-b.html', CSS_B, body_b())):
    io.open(os.path.join(OUT, name), 'w', encoding='utf-8').write(
        (HEAD % css) + body + JS + '</body></html>')
    print('  %-18s' % name)
