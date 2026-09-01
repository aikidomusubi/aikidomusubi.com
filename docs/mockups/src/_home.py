# -*- coding: utf-8 -*-
"""The light home, in two layouts.

Same words, two ways of setting them. The title and the opening paragraph are
the most important space on the page in both, and Aikido carries the weight:
the other three arts get one sentence, far down, and no detail. The dynamic
things (this week, what's coming, the seminar log) have moved to the aside, so
the home does not go stale on its own.
"""

# ═══════════════════════════════════════════════════════════════════════════
# shared: the trigger band, the inline cross-references, the panel plumbing
# ═══════════════════════════════════════════════════════════════════════════
CSS_SHARED = r"""
.page main h2,.page main h3{text-align:left}
.hw{--ink:#111314;--mute:#5c6a70;--line:rgba(17,19,20,.12)}
.page main .hw p{max-width:none;margin:0}
.page main .hw a{background:none}
.page main{padding-bottom:0 !important}

/* ── the inline cross-reference: a whisper, not a button ────────────────── */
.page main a.hx{display:inline-flex;align-items:baseline;gap:.45rem;
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.63rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--mute);text-decoration:none;
  border-bottom:1px solid rgba(17,19,20,.2);padding-bottom:.2rem;margin-top:1.4rem}
.page main a.hx:hover{color:var(--ink);border-bottom-color:var(--ink);background:none}
.page main a.hx i{font-family:'Noto Sans JP','Noto Sans',sans-serif;font-style:normal;
  font-size:.8rem;color:#111314;line-height:1}

/* ── the door: full bleed, flush into the footer ────────────────────────── */
.hdoor{position:relative;margin:4rem -100vw 0;padding:0 100vw;background:#111314;overflow:hidden}
.hdoor-mid{position:relative;max-width:1140px;margin:0 auto}
.hdoor-in{max-width:44rem;padding:3.4rem 0 3.6rem;position:relative;z-index:1}
.hdoor .ghost{position:absolute;right:0;top:50%;transform:translateY(-50%);
  font-family:'Noto Sans JP','Noto Sans',sans-serif;font-size:13rem;line-height:.78;
  color:rgba(255,242,0,.075);pointer-events:none;user-select:none;z-index:0}
.page main .hdoor .k{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.26em;text-transform:uppercase;color:#FFF200;margin-bottom:.9rem}
.page main .hdoor h2{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  font-size:2rem;letter-spacing:.02em;color:#fff;margin:0 0 .9rem;text-transform:none;
  display:flex;align-items:center;gap:.9rem}
.page main .hdoor h2 em{font-family:'Noto Sans JP','Noto Sans',sans-serif;font-style:normal;
  color:#FFF200;font-size:1.7rem}
.page main .hdoor p{color:#aeb6b8;font-size:.95rem;line-height:1.75;max-width:46ch}
.hdoor-list{display:flex;gap:.5rem;flex-wrap:wrap;margin:1.6rem 0 1.9rem}
.page main .hdoor-list span{font-size:.68rem;letter-spacing:.06em;color:#c9cfd1;
  border:1px solid rgba(255,255,255,.2);padding:.35rem .7rem}
.page main .hdoor button{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.68rem;
  letter-spacing:.16em;text-transform:uppercase;background:#FFF200;color:#111314;border:0;
  padding:.9rem 1.6rem;cursor:pointer}
.page main .hdoor button:hover{background:#fff}
@media(max-width:575.98px){.hdoor .ghost{font-size:7rem}
  .page main .hdoor h2{font-size:1.5rem}}

/* ── the nav entry: a place, not a setting ──────────────────────────────── */
.nv-list .nv-bside{margin-left:.4rem}
.nv-list .nv-bside > .nv-top{display:inline-flex;align-items:center;gap:.42rem;
  font-size:.82rem;letter-spacing:.01em;padding:.55rem 0;color:rgba(255,255,255,.85);
  text-decoration:none;background:none;border:0}
.nv-list .nv-bside > .nv-top:hover{color:#fff;background:none}
.nv-list .nv-bside > .nv-top:focus-visible{outline:2px solid #FFF200;outline-offset:2px}
.nv-list .nv-bside i{font-family:'Noto Sans JP','Noto Sans',sans-serif;font-style:normal;
  color:#FFF200;font-size:1rem;line-height:1}
"""

DOOR = """
<section class="hdoor">
  <div class="hdoor-mid">
  <span class="ghost" aria-hidden="true">裏</span>
  <div class="hdoor-in">
    <p class="k">Contenido extra</p>
    <h2><em>裏</em> Cara B</h2>
    <p>La otra cara del dojo: lo que hay en el tatami esta semana, lo que viene, el
       archivo entero y unas cuantas cosas que no caben en esta página. Se abre encima;
       no pierdes el sitio.</p>
    <div class="hdoor-list">
      <span>Esta semana</span><span>Lo que viene</span><span>El archivo</span>
      <span>Seminarios y masterclases</span><span>Palabras del tatami</span>
    </div>
    <button data-rg-open>Abrir la Cara B</button>
  </div>
  </div>
</section>
"""

XLINK = '<a class="hx" href="/cara-b/" data-rg-open><i>裏</i> %s</a>'

JS = r"""
(function(){
  var h=document.documentElement, p=document.getElementById('bside'), last=null;
  function open(e){ if(e)e.preventDefault(); last=document.activeElement;
    h.classList.add('rg-on'); p.setAttribute('aria-hidden','false'); p.scrollTop=0;
    var x=p.querySelector('.ab-x'); if(x)setTimeout(function(){x.focus();},60);
    if(history.pushState)history.pushState({b:1},'','#cara-b'); }
  function close(){ h.classList.remove('rg-on'); p.setAttribute('aria-hidden','true');
    if(last)last.focus();
    if(history.pushState&&location.hash==='#cara-b')history.pushState({},'',location.pathname); }
  document.addEventListener('click',function(e){
    if(e.target.closest('[data-rg-open]'))open(e);
    else if(e.target.closest('[data-rg-close]')||e.target.closest('.rg-scrim'))close(); });
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'&&h.classList.contains('rg-on'))close(); });
  var list=document.querySelector('.nv-list');
  if(list){ var li=document.createElement('li');
    li.className='nv-item nv-bside';
    li.innerHTML='<a class="nv-top" href="/cara-b/" data-rg-open><i>裏</i> Cara B</a>';
    list.appendChild(li); }
  if(location.hash==='#cara-b')open();
})();
"""

CSS_PANEL = r"""
.rg-scrim{position:fixed;inset:0;background:rgba(0,0,0,.6);opacity:0;visibility:hidden;
  transition:opacity .38s ease,visibility .38s;z-index:1400}
.rg-panel{position:fixed;top:0;right:0;bottom:0;width:100%;z-index:1401;
  transform:translateX(100%);transition:transform .52s cubic-bezier(.16,.84,.28,1);
  overflow-y:auto;overscroll-behavior:contain;visibility:hidden;
  box-shadow:-2rem 0 5rem rgba(0,0,0,.55)}
html.rg-on .rg-scrim{opacity:1;visibility:visible}
html.rg-on .rg-panel{transform:none;visibility:visible}
html.rg-on,html.rg-on body{overflow:hidden}
@media(prefers-reduced-motion:reduce){.rg-panel,.rg-scrim{transition:none}}
"""

# ═══════════════════════════════════════════════════════════════════════════
# A · LA COLUMNA — one measured column, print brochure
# ═══════════════════════════════════════════════════════════════════════════
CSS_A = r"""
.ha-top{text-align:center;padding:1rem 0 0}
.page main .ha-top h1{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  text-transform:uppercase;letter-spacing:.06em;font-size:2.9rem;line-height:1.1;
  margin:0 0 1.6rem;color:var(--ink);text-align:center}
.page main .ha-top p{max-width:36rem;margin:0 auto;font-size:1.16rem;line-height:1.72;
  color:#2c3437;text-align:center}
.page main .ha-top hr{margin:3.4rem 0;border:0;border-top:1px solid var(--line)}
@media(max-width:767.98px){.page main .ha-top h1{font-size:2.1rem}
  .page main .ha-top p{font-size:1.02rem}}

.ha-sec{margin:0 0 3.4rem}
.page main .ha-lab{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.26em;text-transform:uppercase;color:var(--mute);margin:0 0 .8rem;
  padding-top:1.4rem;border-top:1px solid var(--line)}
.page main .ha-sec h2{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  text-transform:uppercase;letter-spacing:.07em;font-size:1.6rem;color:var(--ink);
  margin:0 0 1.3rem;padding:0}
.ha-fig{margin:0 0 1.7rem}
.ha-fig img{width:100%;height:auto;display:block;aspect-ratio:16/9;object-fit:cover}
.ha-prose{max-width:43.25rem}
.page main .ha-prose p{font-size:1rem;line-height:1.85;color:#2c3437;margin:0 0 1.05rem}
.page main .ha-prose p:last-child{margin-bottom:0}
.page main .ha-prose a{color:var(--ink);text-decoration:underline;text-underline-offset:.18em}
.ha-quote{max-width:38rem;margin:2rem 0 0;padding:1.4rem 0 0;border-top:2px solid var(--ink)}
.page main .ha-quote p{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.3rem;
  line-height:1.5;color:var(--ink)}

.ha-three{display:grid;grid-template-columns:repeat(3,1fr);gap:2rem}
.page main .ha-three h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  font-size:1.05rem;text-transform:uppercase;letter-spacing:.05em;margin:0 0 .5rem;
  color:var(--ink);border-top:1px solid var(--ink);padding-top:.9rem}
.page main .ha-three p{font-size:.9rem;line-height:1.72;color:var(--mute)}
@media(max-width:767.98px){.ha-three{grid-template-columns:1fr;gap:1.6rem}}

.ha-ven{display:grid;grid-template-columns:repeat(3,1fr);gap:1.4rem}
.ha-ven figure{margin:0}
.ha-ven img{width:100%;aspect-ratio:1;object-fit:cover;display:block}
.page main .ha-ven b{display:block;margin-top:.8rem;font-size:.95rem;color:var(--ink)}
.page main .ha-ven small{display:block;font-size:.8rem;color:var(--mute);line-height:1.55}
@media(max-width:767.98px){.ha-ven{grid-template-columns:1fr}}

.ha-also{display:flex;gap:2.2rem;flex-wrap:wrap;align-items:baseline;
  padding:1.3rem 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.page main .ha-also b{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.95rem;
  letter-spacing:.06em;text-transform:uppercase;color:var(--ink);
  border-bottom:3px solid var(--c);padding-bottom:.2rem}
.page main .ha-also p{font-size:.9rem;color:var(--mute);flex:1 1 20rem;line-height:1.7}

.ha-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem}
.ha-step{border-top:1px solid var(--ink);padding-top:.95rem}
.page main .ha-step .n{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.66rem;
  letter-spacing:.2em;color:var(--mute);margin-bottom:.6rem}
.page main .ha-step h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  font-size:1.05rem;text-transform:uppercase;letter-spacing:.05em;margin:0 0 .45rem;color:var(--ink)}
.page main .ha-step p{font-size:.88rem;line-height:1.7;color:var(--mute)}
@media(max-width:767.98px){.ha-steps{grid-template-columns:1fr;gap:1.6rem}}

.ha-cho{display:grid;grid-template-columns:.62fr 1.38fr;gap:2.4rem;align-items:center}
.ha-cho img{width:100%;aspect-ratio:1;object-fit:cover;display:block}
.page main .ha-cho h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  font-size:1.5rem;letter-spacing:.02em;margin:0 0 .25rem;color:var(--ink)}
.page main .ha-cho .r{font-size:.78rem;color:var(--mute);margin-bottom:1rem}
.page main .ha-cho p{font-size:.93rem;line-height:1.8;color:#2c3437}
@media(max-width:767.98px){.ha-cho{grid-template-columns:1fr;gap:1.4rem}}

.ha-facts{display:grid;grid-template-columns:auto 1fr;gap:.55rem 2rem;font-size:.9rem;
  max-width:43.25rem}
.page main .ha-facts dt{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.16em;text-transform:uppercase;color:var(--mute);padding-top:.24rem}
.page main .ha-facts dd{margin:0;color:var(--ink);line-height:1.6}
@media(max-width:575.98px){.ha-facts{grid-template-columns:1fr;gap:.1rem}
  .page main .ha-facts dd{margin-bottom:.8rem}}
.page main .ha-btn{display:inline-block;margin-top:1.4rem;
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.66rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--ink);text-decoration:none;border-bottom:2px solid #FFF200;
  padding-bottom:.25rem}
.page main .ha-btn:hover{border-bottom-color:var(--ink)}
"""

BODY_A = """<div class="hw">

<header class="ha-top">
  <h1>Aikido en Badalona<br>desde 2008</h1>
  <p>Somos una asociación cultural sin ánimo de lucro dedicada a la enseñanza del aikido.
     Entrenamos en Badalona, en Sant Adrià de Besòs y en la Universitat de Barcelona,
     y recibimos a quien quiera empezar en cualquier momento del año.</p>
  <hr>
</header>

<section class="ha-sec">
  <figure class="ha-fig"><img src="/images/index-8oGCaMDs-02.webp" alt="" loading="lazy"></figure>
  <p class="ha-lab" style="border-top:0;padding-top:0">Lo que enseñamos</p>
  <h2>Aikido</h2>
  <div class="ha-prose">
    <p>El aikido es un arte marcial japonés moderno, fundado por Morihei Ueshiba. No busca
       vencer al oponente sino neutralizar su intención sin dañarlo, y por eso no tiene
       competición. Se practica siempre con un compañero, y ese compañero cambia varias
       veces en cada clase.</p>
    <p>Lo promovemos como un camino de mejora personal a través de una práctica sincera y
       constante basada en el respeto a los demás. A través de las técnicas contribuimos al
       desarrollo físico, mental y espiritual, a la confianza en uno mismo y a la compasión
       hacia el oponente.</p>
    <p>Hay clases para principiantes, clases generales y clases de armas. No hace falta
       experiencia previa ni una forma física particular: se empieza donde se está.</p>
  </div>
  <blockquote class="ha-quote"><p>Es nuestro deseo que quien practica aquí pueda experimentar
     la profundidad y el disfrute del aikido a través del entrenamiento diario.</p></blockquote>
  <a class="hx" href="/cara-b/" data-rg-open><i>裏</i> Qué hay en el tatami esta semana</a>
</section>

<section class="ha-sec">
  <p class="ha-lab">Una clase por dentro</p>
  <div class="ha-three">
    <div><h3>Una hora</h3><p>Se calienta, se estudia una técnica por parejas y se cierra
      sentados en silencio. No hay marcador y nadie gana.</p></div>
    <div><h3>Vas a caer</h3><p>El ukemi, la caída, es la mitad del aikido. Se aprende
      despacio, desde el suelo y sin prisa.</p></div>
    <div><h3>Manga larga</h3><p>Para las primeras clases basta ropa cómoda que cubra los
      brazos. El keikogi ya llegará.</p></div>
  </div>
</section>

<section class="ha-sec">
  <figure class="ha-fig"><img src="/images/index-8oGCaMDs-09.webp" alt="" loading="lazy"></figure>
  <p class="ha-lab" style="border-top:0;padding-top:0">Nuestro espacio</p>
  <h2>El dojo</h2>
  <div class="ha-prose">
    <p>Un espacio grande y diáfano destinado exclusivamente a la práctica y la enseñanza de
       las artes marciales. Lo supervisa el director técnico junto a los instructores, pero
       cuidarlo es responsabilidad de todos: son los estudiantes quienes lo mantienen.</p>
    <p>Es un buen lugar para estudiar artes marciales en serio y para conocer a todo tipo de
       personas, sea cual sea su edad, su sexo o su ocupación.</p>
  </div>
</section>

<section class="ha-sec">
  <p class="ha-lab">Dónde entrenamos</p>
  <div class="ha-ven">
    <figure><img src="/images/access-information-NdxqmVbV-00.webp" alt="" loading="lazy">
      <b>Badalona</b><small>Av. d'Alfons XIII, 351<br>El dojo</small></figure>
    <figure><img src="/images/access-information-NdxqmVbV-01.webp" alt="" loading="lazy">
      <b>Sant Adrià de Besòs</b><small>Poliesportiu Marina-Besòs</small></figure>
    <figure><img src="/images/access-information-NdxqmVbV-02.webp" alt="" loading="lazy">
      <b>Universitat de Barcelona</b><small>Facultat de Dret</small></figure>
  </div>
  <a class="ha-btn" href="/acceso/">Cómo llegar a cada uno</a>
</section>

<section class="ha-sec">
  <div class="ha-also">
    <b style="--c:#B7C2A9">Iaijutsu</b><b style="--c:#A5C8D1">Judo</b><b style="--c:#FBE6A0">Karate</b>
    <p>El mismo tatami acoge otras tres artes. Están todas en la página de
       <a href="/clases/" style="color:#111314;text-decoration:underline">clases</a>.</p>
  </div>
</section>

<section class="ha-sec">
  <p class="ha-lab">Cómo empezar</p>
  <div class="ha-steps">
    <div class="ha-step"><p class="n">01</p><h3>Escríbenos</h3>
      <p>Con un día de aviso basta. Dinos qué clase te interesa y te decimos cuándo venir.</p></div>
    <div class="ha-step"><p class="n">02</p><h3>Ven a probar</h3>
      <p>Dos clases de prueba, sin compromiso ni coste.</p></div>
    <div class="ha-step"><p class="n">03</p><h3>Únete</h3>
      <p>La inscripción es gratuita y está abierta todo el año.</p></div>
  </div>
  <a class="ha-btn" href="/contacto/">Escríbenos</a>
</section>

<section class="ha-sec">
  <p class="ha-lab">Dirección técnica</p>
  <div class="ha-cho">
    <img src="/images/index-8oGCaMDs-05_.webp" alt="" loading="lazy">
    <div>
      <h3>Pablo Martín</h3>
      <p class="r">4.º dan · shidoin · Aikikai · dojo-cho</p>
      <p>Empezó a practicar en Badalona en 1999 con Ricard Coll y fundó la asociación en
         2008. Ha entrenado en el Hombu Dojo de Tokio con Ueshiba Moriteru Doshu,
         Yokota Y. Shihan, Osawa Hayato Shihan y Kuribayashi T. Shihan.</p>
    </div>
  </div>
</section>

<section class="ha-sec">
  <p class="ha-lab">La asociación</p>
  <dl class="ha-facts">
    <dt>Fundada</dt><dd>2008, en Badalona</dd>
    <dt>Forma</dt><dd>Asociación cultural autogestionada y sin ánimo de lucro</dd>
    <dt>Dirección técnica</dt><dd>Pablo Martín, 4.º dan, shidoin</dd>
    <dt>Vínculo</dt><dd>Aikido Arashi Group, organización reconocida por la Aikikai Foundation</dd>
  </dl>
  <a class="ha-btn" href="/sobre-nosotros/la-asociacion/">Sobre nosotros</a>
</section>

__DOOR__
</div>"""

# ═══════════════════════════════════════════════════════════════════════════
# B · EL PLIEGO — a label rail on the left, content on the right
# ═══════════════════════════════════════════════════════════════════════════
CSS_B = r"""
.hb-top{padding:1rem 0 0;max-width:52rem}
.page main .hb-top h1{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  text-transform:uppercase;letter-spacing:.04em;font-size:3.4rem;line-height:1.06;
  margin:0 0 1.8rem;color:var(--ink);text-align:left}
.page main .hb-top p{font-size:1.22rem;line-height:1.68;color:#2c3437;max-width:40rem}
.hb-rule{height:0;border-top:1px solid var(--ink);margin:3.2rem 0 0}
@media(max-width:767.98px){.page main .hb-top h1{font-size:2.1rem}
  .page main .hb-top p{font-size:1.02rem}}

.hb-sec{display:grid;grid-template-columns:9.5rem 1fr;gap:2.4rem;padding:2.8rem 0;
  border-bottom:1px solid var(--line);align-items:start}
.hb-lab{position:sticky;top:7.5rem}
.page main .hb-lab .n{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.2em;color:#B04E17;margin-bottom:.5rem}
.page main .hb-lab h2{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  font-size:.86rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink);
  margin:0;padding:0;line-height:1.4}
.hb-body{min-width:0}
@media(max-width:767.98px){.hb-sec{grid-template-columns:1fr;gap:1rem;padding:2.2rem 0}
  .hb-lab{position:static}}

/* the aikido spread: one tall image beside the prose, one wide beneath */
.hb-spread{display:grid;grid-template-columns:1fr 1.15fr;gap:1.8rem;align-items:start}
.hb-spread img{width:100%;display:block;aspect-ratio:3/4;object-fit:cover}
.page main .hw .hb-p{font-size:1rem;line-height:1.85;color:#2c3437;margin:0 0 1.05rem}
.page main .hw .hb-p:last-child{margin-bottom:0}
.hb-wide{margin-top:1.8rem}
.hb-wide img{width:100%;display:block;aspect-ratio:21/9;object-fit:cover}
.page main .hb-pull{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.22rem;
  line-height:1.5;color:var(--ink);margin-top:1.6rem;padding-top:1.3rem;
  border-top:2px solid var(--ink);max-width:34rem}
@media(max-width:767.98px){.hb-spread{grid-template-columns:1fr}
  .hb-spread img{aspect-ratio:3/2}}

/* the black step band: the one strong contrast moment before the door */
.hb-start{background:#111314;margin:0 -100vw;padding:2.4rem 100vw 2.6rem}
.hb-start-mid{max-width:1140px;margin:0 auto}
.hb-start-g{display:grid;grid-template-columns:9.5rem repeat(3,1fr);gap:2.4rem}
.page main .hb-start h2{color:#fff;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
  font-weight:400;font-size:.86rem;letter-spacing:.14em;text-transform:uppercase;margin:0}
.page main .hb-start .n{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.2em;color:#FFF200;margin-bottom:.5rem}
.page main .hb-start h3{color:#fff;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
  font-weight:400;font-size:1.05rem;text-transform:uppercase;letter-spacing:.05em;
  margin:0 0 .45rem;border-top:1px solid rgba(255,255,255,.25);padding-top:.9rem}
.page main .hb-start p{color:#aeb6b8;font-size:.88rem;line-height:1.72}
.page main .hb-start a.go{display:inline-block;margin-top:1.2rem;color:#FFF200;
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.66rem;letter-spacing:.15em;
  text-transform:uppercase;border-bottom:1px solid rgba(255,242,0,.5);padding-bottom:.2rem}
@media(max-width:991.98px){.hb-start-g{grid-template-columns:1fr;gap:1.4rem}}

.hb-ven{display:grid;grid-template-columns:repeat(3,1fr);gap:1.2rem}
.hb-ven figure{margin:0}
.hb-ven img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}
.page main .hb-ven b{display:block;margin-top:.7rem;font-size:.92rem;color:var(--ink)}
.page main .hb-ven small{display:block;font-size:.78rem;color:var(--mute);line-height:1.5}
@media(max-width:575.98px){.hb-ven{grid-template-columns:1fr}}

.hb-chips{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1rem}
.page main .hb-chips span{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.72rem;
  letter-spacing:.08em;text-transform:uppercase;color:var(--ink);padding:.35rem .75rem;
  border:1px solid var(--line);border-left:3px solid var(--c)}

.hb-cho{display:grid;grid-template-columns:.5fr 1.5fr;gap:1.8rem;align-items:start}
.hb-cho img{width:100%;aspect-ratio:3/4;object-fit:cover;display:block}
.page main .hb-cho h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  font-size:1.45rem;margin:0 0 .25rem;color:var(--ink)}
.page main .hb-cho .r{font-size:.78rem;color:var(--mute);margin-bottom:1rem}
@media(max-width:575.98px){.hb-cho{grid-template-columns:1fr}}

.hb-facts{display:grid;grid-template-columns:auto 1fr;gap:.55rem 1.8rem;font-size:.9rem}
.page main .hb-facts dt{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.16em;text-transform:uppercase;color:var(--mute);padding-top:.24rem}
.page main .hb-facts dd{margin:0;color:var(--ink);line-height:1.6}
@media(max-width:575.98px){.hb-facts{grid-template-columns:1fr;gap:.1rem}
  .page main .hb-facts dd{margin-bottom:.8rem}}
.page main .hb-btn{display:inline-block;margin-top:1.3rem;
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.66rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--ink);text-decoration:none;border-bottom:2px solid #FFF200;
  padding-bottom:.25rem}
.page main .hb-btn:hover{border-bottom-color:var(--ink)}
"""

BODY_B = """<div class="hw">

<header class="hb-top">
  <h1>Aikido en Badalona<br>desde 2008</h1>
  <p>Somos una asociación cultural sin ánimo de lucro dedicada a la enseñanza del aikido.
     Entrenamos en Badalona, en Sant Adrià de Besòs y en la Universitat de Barcelona,
     y recibimos a quien quiera empezar en cualquier momento del año.</p>
  <div class="hb-rule"></div>
</header>

<section class="hb-sec">
  <div class="hb-lab"><p class="n">01</p><h2>Lo que<br>enseñamos</h2></div>
  <div class="hb-body">
    <div class="hb-spread">
      <img src="/images/index-8oGCaMDs-02.webp" alt="" loading="lazy">
      <div>
        <p class="hb-p">El aikido es un arte marcial japonés moderno, fundado por Morihei
           Ueshiba. No busca vencer al oponente sino neutralizar su intención sin dañarlo,
           y por eso no tiene competición. Se practica siempre con un compañero, y ese
           compañero cambia varias veces en cada clase.</p>
        <p class="hb-p">Lo promovemos como un camino de mejora personal a través de una
           práctica sincera y constante basada en el respeto a los demás. A través de las
           técnicas contribuimos al desarrollo físico, mental y espiritual, a la confianza
           en uno mismo y a la compasión hacia el oponente.</p>
        <p class="hb-p">Hay clases para principiantes, clases generales y clases de armas.
           No hace falta experiencia previa ni una forma física particular: se empieza
           donde se está.</p>
      </div>
    </div>
    <p class="hb-pull">Es nuestro deseo que quien practica aquí pueda experimentar la
       profundidad y el disfrute del aikido a través del entrenamiento diario.</p>
    <a class="hx" href="/cara-b/" data-rg-open><i>裏</i> Qué hay en el tatami esta semana</a>
  </div>
</section>

<section class="hb-sec">
  <div class="hb-lab"><p class="n">02</p><h2>Una clase<br>por dentro</h2></div>
  <div class="hb-body">
    <p class="hb-p">Una hora. Se calienta, se estudia una técnica por parejas y se cierra
       sentados en silencio. No hay marcador y nadie gana. El ukemi, la caída, es la mitad
       del aikido y se aprende despacio, desde el suelo. Para las primeras clases basta
       ropa cómoda que cubra los brazos: el keikogi ya llegará.</p>
    <div class="hb-wide"><img src="/images/index-8oGCaMDs-01.webp" alt="" loading="lazy"></div>
  </div>
</section>

<div class="hb-start"><div class="hb-start-mid"><div class="hb-start-g">
  <div><p class="n">03</p><h2>Cómo<br>empezar</h2>
    <a class="go" href="/contacto/">Escríbenos</a></div>
  <div><h3>Escríbenos</h3><p>Con un día de aviso basta. Dinos qué clase te interesa y te
    decimos cuándo venir.</p></div>
  <div><h3>Ven a probar</h3><p>Dos clases de prueba, sin compromiso ni coste.</p></div>
  <div><h3>Únete</h3><p>La inscripción es gratuita y está abierta todo el año.</p></div>
</div></div></div>

<section class="hb-sec">
  <div class="hb-lab"><p class="n">04</p><h2>El dojo<br>y los tatamis</h2></div>
  <div class="hb-body">
    <p class="hb-p">El dojo es un espacio grande y diáfano destinado exclusivamente a la
       práctica y la enseñanza de las artes marciales. Lo supervisa el director técnico
       junto a los instructores, pero cuidarlo es responsabilidad de todos: son los
       estudiantes quienes lo mantienen. Además del dojo entrenamos en dos espacios más.</p>
    <div class="hb-ven" style="margin-top:1.5rem">
      <figure><img src="/images/access-information-NdxqmVbV-00.webp" alt="" loading="lazy">
        <b>Badalona</b><small>Av. d'Alfons XIII, 351 · el dojo</small></figure>
      <figure><img src="/images/access-information-NdxqmVbV-01.webp" alt="" loading="lazy">
        <b>Sant Adrià de Besòs</b><small>Poliesportiu Marina-Besòs</small></figure>
      <figure><img src="/images/access-information-NdxqmVbV-02.webp" alt="" loading="lazy">
        <b>Universitat de Barcelona</b><small>Facultat de Dret</small></figure>
    </div>
    <a class="hb-btn" href="/acceso/">Cómo llegar</a>
  </div>
</section>

<section class="hb-sec">
  <div class="hb-lab"><p class="n">05</p><h2>También<br>en el tatami</h2></div>
  <div class="hb-body">
    <div class="hb-chips"><span style="--c:#B7C2A9">Iaijutsu</span>
      <span style="--c:#A5C8D1">Judo</span><span style="--c:#FBE6A0">Karate</span></div>
    <p class="hb-p">El mismo tatami acoge otras tres artes marciales. Están todas en la
       página de <a href="/clases/" style="color:#111314;text-decoration:underline">clases</a>.</p>
  </div>
</section>

<section class="hb-sec">
  <div class="hb-lab"><p class="n">06</p><h2>Dirección<br>técnica</h2></div>
  <div class="hb-body">
    <div class="hb-cho">
      <img src="/images/index-8oGCaMDs-05_.webp" alt="" loading="lazy">
      <div>
        <h3>Pablo Martín</h3>
        <p class="r">4.º dan · shidoin · Aikikai · dojo-cho</p>
        <p class="hb-p">Empezó a practicar en Badalona en 1999 con Ricard Coll y fundó la
           asociación en 2008. Ha entrenado en el Hombu Dojo de Tokio con Ueshiba Moriteru
           Doshu, Yokota Y. Shihan, Osawa Hayato Shihan y Kuribayashi T. Shihan.</p>
      </div>
    </div>
  </div>
</section>

<section class="hb-sec" style="border-bottom:0">
  <div class="hb-lab"><p class="n">07</p><h2>La<br>asociación</h2></div>
  <div class="hb-body">
    <dl class="hb-facts">
      <dt>Fundada</dt><dd>2008, en Badalona</dd>
      <dt>Forma</dt><dd>Asociación cultural autogestionada y sin ánimo de lucro</dd>
      <dt>Dirección técnica</dt><dd>Pablo Martín, 4.º dan, shidoin</dd>
      <dt>Vínculo</dt><dd>Aikido Arashi Group, organización reconocida por la Aikikai Foundation</dd>
    </dl>
    <a class="hb-btn" href="/sobre-nosotros/la-asociacion/">Sobre nosotros</a>
    <a class="hx" href="/cara-b/" data-rg-open style="display:block;width:max-content">
      <i>裏</i> De dónde viene, en cuatro eslabones</a>
  </div>
</section>

__DOOR__
</div>"""
