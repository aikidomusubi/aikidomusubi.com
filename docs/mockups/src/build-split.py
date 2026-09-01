# -*- coding: utf-8 -*-
"""Home (light, editorial) + El Registro (dark, documentary) as a sliding panel.

Built on the REAL page shell — _site/index.html — so the hero, nav, footer and
all.min.css are the actual ones. Only what is inside <main> is new, plus the
panel, which is injected as a sibling of .page so none of the site's prose
rules can reach it.
"""
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _registro as RG

ROOT = '/Applications/MAMP/htdocs/aikidomusubi.com'
SITE = os.path.join(ROOT, '_site')
OUT = os.path.join(SITE, 'mockups')
shell = io.open(os.path.join(SITE, 'index.html'), encoding='utf-8').read()

i = shell.index('<main'); i_end = shell.index('>', i) + 1; j = shell.index('</main>')
HEAD, MAIN_OPEN, TAIL = shell[:i], shell[i:i_end], shell[j:]

# ═══════════════════════════════════════════════════════════════════════════
# THE LIGHT HOME — large images, prose, the site's own vocabulary
# ═══════════════════════════════════════════════════════════════════════════
CSS_HOME = r"""
.page main h2,.page main h3{text-align:left}
.page main .h-w p{max-width:none;margin:0}
.h-w{--ink:#111314;--mute:#5c6a70;--line:rgba(17,19,20,.12)}

/* ── title block: the one centred thing on the page ─────────────────────── */
.h-top{text-align:center;padding-top:.5rem}
.page main .h-top h1{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  text-transform:uppercase;letter-spacing:.06em;font-size:2.25rem;line-height:1.16;
  margin:0 0 1.1rem;color:var(--ink);text-align:center}
.page main .h-top p{max-width:40rem;margin:0 auto;font-size:1.02rem;line-height:1.75;
  color:var(--mute);text-align:center}
.page main .h-top hr{margin:2.6rem 0;border:0;border-top:1px solid var(--line)}
@media(max-width:575.98px){.page main .h-top h1{font-size:1.7rem}}

/* ── the week, as pills. Four facts, scannable in a second. ─────────────── */
.h-week{display:flex;gap:0;flex-wrap:wrap;border:1px solid var(--line);margin-bottom:3.2rem}
.h-week>a,.h-week>div{flex:1 1 8rem;padding:1.05rem 1.2rem;border-right:1px solid var(--line);
  min-width:0}
.h-week>*:last-child{border-right:0}
.page main .h-week b{display:block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
  font-size:1.55rem;line-height:1;color:var(--ink);margin-bottom:.3rem}
.page main .h-week span{font-size:.68rem;letter-spacing:.13em;text-transform:uppercase;
  color:var(--mute)}
.page main a.h-week-go{background:var(--ink);color:#fff;text-decoration:none;
  display:flex;align-items:center;flex:0 1 11rem}
.page main a.h-week-go:hover{background:#000}
.page main a.h-week-go span{color:#fff;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
  font-size:.68rem;letter-spacing:.13em}
@media(max-width:767.98px){.h-week>a,.h-week>div{flex:1 1 45%;border-bottom:1px solid var(--line)}}

/* ── an editorial block: big picture, then prose ────────────────────────── */
.h-blk{margin:0 0 3.6rem}
.h-blk figure{margin:0 0 1.6rem}
.h-blk img{width:100%;height:auto;display:block;aspect-ratio:3/2;object-fit:cover}
.page main .h-blk h2{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  text-transform:uppercase;letter-spacing:.08em;font-size:1.28rem;color:var(--ink);
  margin:0 0 1rem;padding:0}
.h-body{max-width:43.25rem}
.page main .h-body p{font-size:.97rem;line-height:1.85;color:#2c3437;margin:0 0 1rem}
.page main .h-body p:last-child{margin-bottom:0}
.page main .h-body a{color:var(--ink);text-decoration:underline;text-underline-offset:.18em}
.h-kicker{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.64rem;
  letter-spacing:.24em;text-transform:uppercase;color:var(--mute);margin-bottom:.7rem}

/* two-column variant for the big ones */
@media(min-width:992px){
  .h-blk.wide{display:grid;grid-template-columns:1fr 1fr;gap:2.6rem;align-items:center}
  .h-blk.wide figure{margin:0}
  .h-blk.wide img{aspect-ratio:4/5}
}

/* ── the other three disciplines ────────────────────────────────────────── */
.h-tri{display:grid;grid-template-columns:repeat(3,1fr);gap:1.4rem}
.page main .h-tri a{display:block;text-decoration:none;border-top:3px solid var(--c);
  padding:1rem 0 0;color:inherit;background:none}
.page main .h-tri a:hover{background:none}
.page main .h-tri a:hover b{text-decoration:underline;text-underline-offset:.18em}
.page main .h-tri b{display:block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
  font-size:1.05rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink);
  margin-bottom:.45rem}
.page main .h-tri p{font-size:.87rem;line-height:1.7;color:var(--mute)}
@media(max-width:767.98px){.h-tri{grid-template-columns:1fr;gap:1.6rem}}

/* ── venues ─────────────────────────────────────────────────────────────── */
.h-ven{display:grid;grid-template-columns:repeat(3,1fr);gap:1.4rem}
.h-ven figure{margin:0}
.h-ven img{width:100%;aspect-ratio:1;object-fit:cover;display:block}
.page main .h-ven b{display:block;margin-top:.8rem;font-size:.95rem;color:var(--ink)}
.page main .h-ven small{display:block;font-size:.8rem;color:var(--mute);line-height:1.55;
  margin-top:.15rem}
@media(max-width:767.98px){.h-ven{grid-template-columns:1fr}}

/* ── how to start ───────────────────────────────────────────────────────── */
.h-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:1.4rem}
.h-step{border-top:1px solid var(--ink);padding-top:1rem}
.page main .h-step .n{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.68rem;
  letter-spacing:.2em;color:var(--mute);margin-bottom:.7rem}
.page main .h-step h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  font-size:1.08rem;text-transform:uppercase;letter-spacing:.05em;margin:0 0 .5rem;
  color:var(--ink)}
.page main .h-step p{font-size:.88rem;line-height:1.7;color:var(--mute)}
@media(max-width:767.98px){.h-steps{grid-template-columns:1fr;gap:1.7rem}}

/* ── seminars ───────────────────────────────────────────────────────────── */
.h-sem{display:grid;grid-template-columns:repeat(3,1fr);gap:1.4rem}
.page main .h-sem a{display:block;border:1px solid var(--line);border-top:3px solid #E2625E;
  padding:1.15rem;text-decoration:none;color:inherit;background:none}
.page main .h-sem a:hover{border-color:var(--ink);background:none}
.page main .h-sem .d{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.66rem;
  letter-spacing:.14em;text-transform:uppercase;color:var(--mute);margin-bottom:.6rem}
.page main .h-sem b{display:block;font-size:1rem;color:var(--ink);margin-bottom:.15rem}
.page main .h-sem small{font-size:.8rem;color:var(--mute)}
@media(max-width:767.98px){.h-sem{grid-template-columns:1fr}}

/* ── dojo-cho ───────────────────────────────────────────────────────────── */
.h-cho{display:grid;grid-template-columns:.72fr 1.28fr;gap:2.4rem;align-items:start}
.h-cho img{width:100%;aspect-ratio:1;object-fit:cover;display:block}
.page main .h-cho h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  font-size:1.35rem;letter-spacing:.03em;margin:0 0 .2rem;color:var(--ink)}
.page main .h-cho .r{font-size:.78rem;color:var(--mute);margin-bottom:1rem}
.page main .h-cho p{font-size:.92rem;line-height:1.8;color:#2c3437;margin-bottom:.9rem}
.page main .h-cho .cr{font-size:.82rem;color:var(--mute);border-top:1px solid var(--line);
  padding-top:.9rem}
@media(max-width:767.98px){.h-cho{grid-template-columns:1fr;gap:1.4rem}
  .h-cho img{aspect-ratio:3/2}}

/* ── facts ──────────────────────────────────────────────────────────────── */
.h-facts{display:grid;grid-template-columns:auto 1fr;gap:.55rem 2rem;font-size:.9rem;
  max-width:43.25rem}
.page main .h-facts dt{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.64rem;
  letter-spacing:.16em;text-transform:uppercase;color:var(--mute);padding-top:.22rem}
.page main .h-facts dd{margin:0;color:var(--ink);line-height:1.6}
@media(max-width:575.98px){.h-facts{grid-template-columns:1fr;gap:.1rem 0}
  .page main .h-facts dd{margin-bottom:.8rem}}

/* ── a plain rule + section head ────────────────────────────────────────── */
.page main .h-w hr{border:0;border-top:1px solid var(--line);margin:3.4rem 0}
.page main .h-h2{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  text-transform:uppercase;letter-spacing:.09em;font-size:1.18rem;color:var(--ink);
  margin:0 0 1.5rem;padding:0}
.page main .h-btn{display:inline-block;margin-top:1.4rem;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
  font-size:.68rem;letter-spacing:.15em;text-transform:uppercase;color:var(--ink);
  text-decoration:none;border-bottom:2px solid #FFF200;padding-bottom:.25rem;background:none}
.page main .h-btn:hover{background:none;border-bottom-color:var(--ink)}
"""

BODY_HOME = """
<div class="h-w">

<header class="h-top">
  <h1>Aikido en Badalona<br>desde 2008</h1>
  <p>La Associació Cultural Musubi Aikido es una asociación autogestionada y sin ánimo
     de lucro. Enseñamos aikido, iaijutsu, judo y karate en tres espacios de Barcelona
     y su área, todos los días de la semana menos el domingo.</p>
  <hr>
</header>

<div class="h-week">
  <div><b>20</b><span>sesiones</span></div>
  <div><b>4</b><span>disciplinas</span></div>
  <div><b>3</b><span>espacios</span></div>
  <div><b>6</b><span>días a la semana</span></div>
  <a class="h-week-go" href="/horarios/"><span>Ver el horario &rarr;</span></a>
</div>

<section class="h-blk wide">
  <figure><img src="/images/index-8oGCaMDs-01.webp" alt="" loading="lazy"></figure>
  <div>
    <p class="h-kicker">Bienvenidos</p>
    <h2>Una práctica sincera y constante</h2>
    <div class="h-body">
      <p>Aikido Musubi promueve el aikido como un camino de mejora personal a través de
         una práctica sincera y constante basada en el respeto a los demás. A través de
         las técnicas contribuimos al desarrollo físico, mental y espiritual, a la
         confianza en uno mismo y a la compasión hacia el oponente.</p>
      <p>Es nuestro deseo que quien practica aquí pueda experimentar la profundidad y el
         disfrute del aikido a través del entrenamiento diario, en un espacio compartido
         por estudiantes y aikidoka visitantes.</p>
      <p>Si quieres empezar, <a href="/contacto/">escríbenos</a> o
         <a href="/acceso/">ven a ver el dojo</a>. La inscripción es gratuita y está
         abierta todo el año.</p>
    </div>
  </div>
</section>

<hr>

<section class="h-blk">
  <figure><img src="/images/index-8oGCaMDs-02.webp" alt="" loading="lazy"></figure>
  <p class="h-kicker">La disciplina principal</p>
  <h2>Aikido</h2>
  <div class="h-body">
    <p>El aikido es un arte marcial japonés moderno, fundado por Morihei Ueshiba, que
       no busca vencer al oponente sino neutralizar su intención sin dañarlo. No hay
       competición. Se practica siempre con un compañero, y ese compañero cambia varias
       veces en cada clase.</p>
    <p>Once clases semanales, de principiantes a armas, en los tres espacios. Es lo que
       más enseñamos y lo que da nombre a la asociación.</p>
    <a class="h-btn" href="/clases/">Las cuatro disciplinas</a>
  </div>
</section>

<hr>

<h2 class="h-h2">También enseñamos</h2>
<div class="h-tri">
  <a href="/clases/" style="--c:#B7C2A9"><b>Iaijutsu</b>
    <p>El arte del sable envainado. Lunes por la tarde, y una mañana de sábado al mes
       con Xavi Serra.</p></a>
  <a href="/clases/" style="--c:#A5C8D1"><b>Judo</b>
    <p>Lunes y miércoles a primera hora, en el tatami de Badalona. Con Àlex Molina.</p></a>
  <a href="/clases/" style="--c:#FBE6A0"><b>Karate</b>
    <p>Tres clases por semana, incluida la sesión larga del sábado por la mañana.
       Con Pau Llorens.</p></a>
</div>

<hr>

<section class="h-blk wide">
  <figure><img src="/images/index-8oGCaMDs-09.webp" alt="" loading="lazy"></figure>
  <div>
    <p class="h-kicker">Nuestro dojo</p>
    <h2>Un espacio para las artes marciales</h2>
    <div class="h-body">
      <p>El dojo es un espacio grande y diáfano destinado exclusivamente a la práctica y
         la enseñanza de las artes marciales. Lo supervisa el director técnico junto a los
         instructores, pero cuidarlo es responsabilidad de todos: son los estudiantes
         quienes lo mantienen.</p>
      <p>Es un buen lugar para estudiar artes marciales en serio y para conocer a todo tipo
         de personas, sea cual sea su edad, su sexo o su ocupación.</p>
    </div>
  </div>
</section>

<hr>

<h2 class="h-h2">Dónde entrenamos</h2>
<div class="h-ven">
  <figure><img src="/images/access-information-NdxqmVbV-00.webp" alt="" loading="lazy">
    <b>Badalona</b><small>Av. d'Alfons XIII, 351 · el dojo<br>Lunes a sábado</small></figure>
  <figure><img src="/images/access-information-NdxqmVbV-01.webp" alt="" loading="lazy">
    <b>Sant Adrià de Besòs</b><small>Poliesportiu Marina-Besòs<br>Lunes y miércoles</small></figure>
  <figure><img src="/images/access-information-NdxqmVbV-02.webp" alt="" loading="lazy">
    <b>Universitat de Barcelona</b><small>Facultat de Dret<br>Lunes y miércoles</small></figure>
</div>
<a class="h-btn" href="/acceso/">Cómo llegar a cada uno</a>

<hr>

<h2 class="h-h2">Cómo empezar</h2>
<div class="h-steps">
  <div class="h-step"><p class="n">01</p><h3>Escríbenos</h3>
    <p>Con un día de aviso basta. Dinos qué clase te interesa y te decimos cuándo venir.</p></div>
  <div class="h-step"><p class="n">02</p><h3>Ven a probar</h3>
    <p>Dos clases de prueba, sin compromiso. Ropa cómoda de manga larga; el keikogi ya
       llegará.</p></div>
  <div class="h-step"><p class="n">03</p><h3>Únete</h3>
    <p>La inscripción es gratuita y está abierta todo el año.</p></div>
</div>
<a class="h-btn" href="/visitantes/">Entrenar como visitante</a>

<hr>

<h2 class="h-h2">Próximos seminarios</h2>
<div class="h-sem">
  <a href="/seminarios/"><p class="d">12 marzo 2026</p><b>Simone Corridoni</b>
    <small>4.º dan Aikikai</small></a>
  <a href="/seminarios/"><p class="d">16 marzo 2026</p><b>Koji Watanabe</b>
    <small>5.º dan Aikikai</small></a>
  <a href="/seminarios/"><p class="d">24–26 abril 2026</p><b>Emilio Cardia Shihan</b>
    <small>6.º dan Aikikai</small></a>
</div>
<a class="h-btn" href="/calendario/">Todo el calendario</a>

<hr>

<h2 class="h-h2">Dirección técnica</h2>
<div class="h-cho">
  <img src="/images/index-8oGCaMDs-05_.webp" alt="" loading="lazy">
  <div>
    <h3>Pablo Martín</h3>
    <p class="r">4.º dan · shidoin · Aikikai · dojo-cho</p>
    <p>Empezó a practicar en Badalona en 1999 con Ricard Coll y fundó la asociación en
       2008. Ha entrenado en el Hombu Dojo de Tokio con Ueshiba Moriteru Doshu, Miyamoto
       T. Shihan, Yokota Y. Shihan, Osawa Hayato Shihan y Kuribayashi T. Shihan.</p>
    <p class="cr">Con Pedro Fortes, José Luis Zafra y Alberto Sancho (4.º dan) ·
       Juanma Pérez, Andreu Villar y Guanlong Zheng (3.<sup>er</sup> dan)</p>
  </div>
</div>

<hr>

<h2 class="h-h2">La asociación</h2>
<dl class="h-facts">
  <dt>Fundada</dt><dd>2008, en Badalona</dd>
  <dt>Forma</dt><dd>Asociación cultural autogestionada y sin ánimo de lucro</dd>
  <dt>Dirección técnica</dt><dd>Pablo Martín, 4.º dan, shidoin</dd>
  <dt>Vínculo</dt><dd>Aikido Arashi Group → Hombu Dojo, vía Miyamoto Tsuruzo, 8.º dan</dd>
</dl>
<a class="h-btn" href="/sobre-nosotros/la-asociacion/">Sobre nosotros</a>

</div>
"""

# ═══════════════════════════════════════════════════════════════════════════
# THE DOOR — trigger B, the band at the foot of the home
# ═══════════════════════════════════════════════════════════════════════════
CSS_DOOR = r"""
.page main{padding-bottom:0 !important}
.h-door{position:relative;margin:4rem -100vw 0;padding:0 100vw;background:#111314;
  overflow:hidden}
.h-door-mid{position:relative;max-width:1140px;margin:0 auto}
.h-door-in{max-width:43.25rem;padding:3.6rem 0 3.8rem;position:relative;z-index:1}
.h-door .ghost{position:absolute;right:0;top:50%;transform:translateY(-50%);
  font-family:'Noto Sans JP','Noto Sans',sans-serif;font-size:12rem;line-height:.8;
  color:rgba(255,255,255,.055);pointer-events:none;user-select:none;z-index:0}
.page main .h-door .k{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.64rem;
  letter-spacing:.26em;text-transform:uppercase;color:#FFF200;margin-bottom:1rem}
.page main .h-door h2{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  font-size:1.9rem;letter-spacing:.03em;color:#fff;margin:0 0 1rem;text-transform:none}
.page main .h-door p{color:#aeb6b8;font-size:.95rem;line-height:1.75;max-width:44ch}
.h-door-n{display:flex;gap:2.4rem;flex-wrap:wrap;margin:1.9rem 0 2rem}
.page main .h-door-n b{display:block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
  font-size:1.6rem;color:#fff;line-height:1}
.page main .h-door-n span{font-size:.62rem;letter-spacing:.14em;text-transform:uppercase;
  color:#9aa2a5}
.page main .h-door button{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.7rem;
  letter-spacing:.16em;text-transform:uppercase;background:#FFF200;color:#111314;border:0;
  padding:.95rem 1.6rem;cursor:pointer}
.page main .h-door button:hover{background:#fff}
@media(max-width:575.98px){.h-door .ghost{font-size:7rem}
  .page main .h-door h2{font-size:1.5rem}}
"""

DOOR = """
<section class="h-door">
  <div class="h-door-mid">
  <span class="ghost" aria-hidden="true">産靈</span>
  <div class="h-door-in">
    <p class="k">Segunda lectura</p>
    <h2>El registro</h2>
    <p>Todo lo que esta página afirma, documentado: la semana entera hora por hora,
       el linaje completo, dieciocho años de archivo y las treinta y nueve fichas de
       seminario. Se abre encima; no pierdes el sitio.</p>
    <div class="h-door-n">
      <div><b>18</b><span>años</span></div>
      <div><b>462</b><span>entradas</span></div>
      <div><b>39</b><span>seminarios</span></div>
      <div><b>20</b><span>sesiones</span></div>
    </div>
    <button data-rg-open>Abrir el registro &rarr;</button>
  </div>
  </div>
</section>
"""

# ═══════════════════════════════════════════════════════════════════════════
# THE PANEL — a sibling of .page, so no prose rule can reach inside it
# ═══════════════════════════════════════════════════════════════════════════
CSS_PANEL = r"""
.rg-scrim{position:fixed;inset:0;background:rgba(0,0,0,.55);opacity:0;visibility:hidden;
  transition:opacity .38s ease,visibility .38s;z-index:1400}
.rg-panel{position:fixed;top:0;right:0;bottom:0;width:100%;z-index:1401;
  transform:translateX(100%);transition:transform .52s cubic-bezier(.16,.84,.28,1);
  overflow-y:auto;overscroll-behavior:contain;visibility:hidden;
  box-shadow:-2rem 0 5rem rgba(0,0,0,.5)}
html.rg-on .rg-scrim{opacity:1;visibility:visible}
html.rg-on .rg-panel{transform:none;visibility:visible}
html.rg-on{overflow:hidden}
html.rg-on body{overflow:hidden}
@media(prefers-reduced-motion:reduce){.rg-panel{transition:none}.rg-scrim{transition:none}}

/* trigger C — the switch in the nav's utility strip */
.nv-reg{display:inline-flex;align-items:center;gap:.4rem;border:1px solid rgba(255,255,255,.28);
  background:none;color:inherit;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
  font-size:.6rem;letter-spacing:.16em;text-transform:uppercase;padding:.24rem .6rem;
  cursor:pointer;line-height:1.5}
.nv-reg:hover{background:#FFF200;color:#111314;border-color:#FFF200}
.nv-reg i{font-family:'Noto Sans JP','Noto Sans',sans-serif;font-style:normal;font-size:.8rem}
"""

JS_PANEL = r"""
(function(){
  var h=document.documentElement, p=document.getElementById('registro'), last=null;
  function open(e){ if(e)e.preventDefault(); last=document.activeElement;
    h.classList.add('rg-on'); p.setAttribute('aria-hidden','false');
    var x=p.querySelector('.rg-x'); if(x)setTimeout(function(){x.focus();},60);
    if(history.pushState)history.pushState({rg:1},'','#registro'); }
  function close(){ h.classList.remove('rg-on'); p.setAttribute('aria-hidden','true');
    if(last)last.focus();
    if(history.pushState&&location.hash==='#registro')history.pushState({},'',location.pathname); }
  document.addEventListener('click',function(e){
    if(e.target.closest('[data-rg-open]'))open(e);
    else if(e.target.closest('[data-rg-close]')||e.target.closest('.rg-scrim'))close(); });
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'&&h.classList.contains('rg-on'))close(); });
  // trigger C, dropped into the nav's utility strip
  var strip=document.querySelector('.nv-strip .nv-strip-in')||document.querySelector('.nv-strip');
  if(strip){ var b=document.createElement('button');
    b.className='nv-reg'; b.setAttribute('data-rg-open','');
    b.innerHTML='<i>産</i> El registro';
    var lang=strip.querySelector('.nv-lang'); if(lang)strip.insertBefore(b,lang); else strip.appendChild(b); }
  if(location.hash==='#registro')open();
})();
"""


def build(name, css, body, panel=True):
    head = HEAD.replace('</head>', '<style>%s</style></head>' % css)
    tail = TAIL
    if panel:
        pan = ('<div class="rg-scrim" hidden-decorative></div>'
               '<div class="rg-panel rg" id="registro" role="dialog" aria-modal="true"'
               ' aria-label="El registro" aria-hidden="true">%s%s</div>'
               '<script>%s</script>' % (RG.masthead(), RG.body(), JS_PANEL))
        tail = tail.replace('</body>', pan + '</body>')
    html = head + MAIN_OPEN + body + tail
    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, name), 'w', encoding='utf-8').write(html)
    print('  %-20s %5d KB' % (name, len(html) // 1024))


# 1 — the light home, with the panel wired in
build('home-3.html', CSS_HOME + CSS_DOOR + CSS_PANEL + RG.CSS,
      BODY_HOME.replace('</div>\n', DOOR + '</div>\n', 0) if False else BODY_HOME.rstrip()[:-6] + DOOR + '</div>')

# 2 — the record, standalone, so it can be read at length
STANDALONE = ("""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>El registro — Aikido Musubi</title>
<link rel="stylesheet" href="/styles/all.min.css">
<style>html,body{margin:0;background:#111314}%s
.rg-standalone{min-height:100vh}</style></head>
<body class="rg rg-standalone">%s%s</body></html>""")
io.open(os.path.join(OUT, 'home-2.html'), 'w', encoding='utf-8').write(
    STANDALONE % (RG.CSS, RG.masthead(close=False), RG.body('Volver a la portada')))
print('  %-20s standalone' % 'home-2.html')
