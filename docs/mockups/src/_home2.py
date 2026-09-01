# -*- coding: utf-8 -*-
"""The home, one column, extended from _data/about.yml.

Aikido carries the whole page. The other three arts are not mentioned at all.
Nothing explains how the site works: the door at the foot shows a fragment of
what is behind it and lets the reader draw the conclusion.
"""

CSS = r"""
.page main h2,.page main h3{text-align:left}
.hw{--ink:#111314;--mute:#5c6a70;--line:rgba(17,19,20,.12)}
.page main .hw p{max-width:none;margin:0}
.page main .hw a{background:none}
.page main{padding-bottom:0 !important}
/* On the home only. In the real build this is a Liquid guard in
   _includes/footer.html, not CSS: {% unless page.i18n-ref contains 'index-' %} */
body.index-8oGCaMDs .ft-invite,body.index-8oGCaMDs .ft-band{display:none !important}

/* ── title: the most important space on the page ────────────────────────── */
.ha-top{text-align:center;padding:1rem 0 0}
.page main .ha-top .ha-kanji{font-family:'Noto Sans JP','Noto Sans',sans-serif;font-size:3.4rem;
  line-height:1;color:var(--ink);letter-spacing:.08em;margin:0 0 1.1rem;text-align:center}
@media(max-width:767.98px){.page main .ha-top .ha-kanji{font-size:2.6rem}}
.page main .ha-top h1{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  text-transform:uppercase;letter-spacing:.06em;font-size:2.9rem;line-height:1.1;
  margin:0 0 1.6rem;color:var(--ink);text-align:center}
.page main .ha-top p{max-width:36rem;margin:0 auto;font-size:1.16rem;line-height:1.72;
  color:#2c3437;text-align:center}
.page main .ha-top hr{margin:3.4rem 0;border:0;border-top:1px solid var(--line)}
@media(max-width:767.98px){.page main .ha-top h1{font-size:2.1rem}
  .page main .ha-top p{font-size:1.02rem}}

/* ── a section ──────────────────────────────────────────────────────────── */
.ha-sec{margin:0 0 3.4rem}
.page main .ha-lab{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.26em;text-transform:uppercase;color:var(--mute);margin:0 0 .8rem;
  padding-top:1.4rem;border-top:1px solid var(--line)}
.page main .ha-lab.bare{border-top:0;padding-top:0}
.page main .ha-sec h2{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  text-transform:uppercase;letter-spacing:.07em;font-size:1.6rem;color:var(--ink);
  margin:0 0 1.3rem;padding:0}
.ha-fig{margin:0 0 1.7rem}
.ha-fig img{width:100%;height:auto;display:block;aspect-ratio:16/9;object-fit:cover}
.ha-prose{max-width:43.25rem}
.page main .ha-prose p{font-size:1rem;line-height:1.85;color:#2c3437;margin:0 0 1.05rem}
.page main .ha-prose p:last-child{margin-bottom:0}
.page main .ha-prose a{color:var(--ink);text-decoration:underline;text-underline-offset:.18em}
.page main .ha-prose em{font-style:italic}

/* ── venues ─────────────────────────────────────────────────────────────── */
.ha-ven{display:grid;grid-template-columns:repeat(3,1fr);gap:1.4rem;margin-top:1.8rem}
.ha-ven figure{margin:0}
.ha-ven img{width:100%;aspect-ratio:1;object-fit:cover;display:block}
.page main .ha-ven b{display:block;margin-top:.8rem;font-size:.95rem;color:var(--ink)}
.page main .ha-ven small{display:block;font-size:.8rem;color:var(--mute);line-height:1.55}
@media(max-width:767.98px){.ha-ven{grid-template-columns:1fr}}

/* ── steps ──────────────────────────────────────────────────────────────── */
.ha-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem}
.ha-step{border-top:1px solid var(--ink);padding-top:.95rem}
.page main .ha-step .n{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.66rem;
  letter-spacing:.2em;color:var(--mute);margin-bottom:.6rem}
.page main .ha-step h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  font-size:1.05rem;text-transform:uppercase;letter-spacing:.05em;margin:0 0 .45rem;color:var(--ink)}
.page main .ha-step p{font-size:.88rem;line-height:1.7;color:var(--mute)}
@media(max-width:767.98px){.ha-steps{grid-template-columns:1fr;gap:1.6rem}}

/* ── dojo-cho ───────────────────────────────────────────────────────────── */
.ha-cho{display:grid;grid-template-columns:.62fr 1.38fr;gap:2.4rem;align-items:start}
.ha-cho img{width:100%;aspect-ratio:3/4;object-fit:cover;display:block}
.page main .ha-cho h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  font-size:1.5rem;letter-spacing:.02em;margin:0 0 .25rem;color:var(--ink)}
.page main .ha-cho .r{font-size:.78rem;color:var(--mute);margin-bottom:1.1rem;
  padding-bottom:1rem;border-bottom:1px solid var(--line)}
.page main .ha-cho p{font-size:.95rem;line-height:1.85;color:#2c3437;margin:0 0 1rem}
.page main .ha-cho p:last-child{margin-bottom:0}
.page main .ha-cho em{font-style:italic}
@media(max-width:767.98px){.ha-cho{grid-template-columns:1fr;gap:1.4rem}
  .ha-cho img{aspect-ratio:3/2}}

/* ── facts ──────────────────────────────────────────────────────────────── */
.ha-facts{display:grid;grid-template-columns:auto 1fr;gap:.55rem 2rem;font-size:.9rem;
  max-width:43.25rem;margin-top:1.8rem;padding-top:1.4rem;border-top:1px solid var(--line)}
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

/* ══ the door ════════════════════════════════════════════════════════════
   C3's rows of real data, with C1's left column: mark, name, line, button. */
.hdoor{position:relative;margin:4rem -100vw 0;padding:0 100vw;background:#111314;overflow:hidden}
.hdoor-mid{position:relative;max-width:1140px;margin:0 auto;
  display:grid;grid-template-columns:19rem 1fr;gap:4rem;align-items:center;
  padding:3.4rem 0 3.6rem}
.hdoor-in{max-width:none}
.page main .hdoor .mk{display:flex;align-items:baseline;gap:.7rem;margin-bottom:.9rem}
.page main .hdoor .mk i{font-family:'Noto Sans JP','Noto Sans',sans-serif;font-style:normal;
  color:#FFF200;font-size:1.5rem;line-height:1}
.page main .hdoor h2{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  font-size:2rem;letter-spacing:.02em;color:#fff;margin:0;text-transform:none;line-height:1}
.page main .hdoor p{color:#aeb6b8;font-size:.95rem;line-height:1.7;max-width:30ch}
.page main .hdoor button{margin-top:1.7rem;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
  font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;background:#FFF200;
  color:#111314;border:0;padding:.9rem 1.7rem;cursor:pointer}
.page main .hdoor button:hover{background:#fff}
.page main .hdoor button:focus-visible{outline:2px solid #fff;outline-offset:3px}

.hrows{display:grid;gap:0}
.hrows > div{display:grid;grid-template-columns:8rem 1fr;gap:1.4rem;align-items:baseline;
  padding:.8rem 0;border-top:1px solid rgba(255,255,255,.13)}
.hrows > div:last-child{border-bottom:1px solid rgba(255,255,255,.13)}
.page main .hrows .k{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.58rem;
  letter-spacing:.16em;text-transform:uppercase;color:var(--c)}
.page main .hrows .v{color:#fff;font-size:.95rem;line-height:1.4}
.page main .hrows .v small{display:block;color:#a6adb0;font-size:.78rem;margin-top:.15rem}
@media(max-width:991.98px){.hdoor-mid{grid-template-columns:1fr;gap:2.2rem}}
@media(max-width:575.98px){.page main .hdoor h2{font-size:1.6rem}
  .hrows > div{grid-template-columns:1fr;gap:.1rem}}
.page main .hpk .d{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.58rem;
  letter-spacing:.14em;text-transform:uppercase;color:#8f9698;margin-bottom:.25rem}
.page main .hpk .t{color:#fff;font-size:.88rem;line-height:1.35}
@media(max-width:991.98px){.hdoor-mid{grid-template-columns:1fr;gap:2.2rem}
  .hpeek{max-width:24rem}}
@media(max-width:575.98px){.page main .hdoor h2{font-size:1.6rem}
  .page main .hdoor p{font-size:.95rem}
  .hpk:nth-child(2){margin-left:.6rem}.hpk:nth-child(3){margin-left:1.2rem}}

/* ── the nav entry ──────────────────────────────────────────────────────── */
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
    <div class="hdoor-in">
      <p class="mk"><i>裏</i></p>
      <h2>Ura</h2>
      <p style="margin-top:.9rem">Lo que pasa en el dojo esta semana, y todo lo que ha
         pasado antes.</p>
      <button data-rg-open>Entrar</button>
    </div>
    <div class="hrows">
      <div style="--c:#FFF200"><p class="k">Esta semana</p>
        <p class="v">Martes y jueves, de 18:30 a 20:30<small>Horario de agosto hasta el día 31</small></p></div>
      <div style="--c:#E2625E"><p class="k">Lo próximo</p>
        <p class="v">29 de agosto, preparación de exámenes<small>Cada sábado hasta el 5 de diciembre</small></p></div>
      <div style="--c:#A5C8D1"><p class="k">El archivo</p>
        <p class="v">462 momentos guardados<small>49 álbumes, 236 publicaciones, 177 vídeos</small></p></div>
    </div>
  </div>
</section>
"""

BODY = """<div class="hw">

<header class="ha-top">
  <p class="ha-kanji" lang="ja">産靈</p>
  <h1>Aikido desde 2008<br>en el área de Barcelona</h1>
  <p>Una asociación cultural sin ánimo de lucro dedicada a la enseñanza del aikido.
     Entrenamos en Badalona, en Sant Adrià de Besòs y en la Universitat de Barcelona.
     La inscripción está abierta todo el año.</p>
  <hr>
</header>

<section class="ha-sec">
  <figure class="ha-fig"><img src="/images/index-8oGCaMDs-02.webp" alt="" loading="lazy"></figure>
  <p class="ha-lab bare">El arte</p>
  <h2>Aikido</h2>
  <div class="ha-prose">
    <p>El aikido es un arte marcial japonés no competitivo desarrollado a principios del
       siglo XX por Morihei Ueshiba. Utiliza movimientos flexibles y naturales para evadir,
       redirigir o neutralizar los ataques aprovechando la fuerza del oponente.</p>
    <p>Se puede empezar a practicar aikido en cualquier momento, independientemente de la
       edad o de la condición física; tanto hombres como mujeres, desde adultos hasta
       niños.</p>
  </div>
  <a class="ha-btn" href="/sobre-nosotros/aikido/">Sobre el aikido</a>
</section>

<section class="ha-sec">
  <figure class="ha-fig"><img src="/images/index-8oGCaMDs-09.webp" alt="" loading="lazy"></figure>
  <p class="ha-lab bare">Nuestro espacio</p>
  <h2>El dojo</h2>
  <div class="ha-prose">
    <p>Un espacio grande y diáfano destinado exclusivamente a la práctica y la enseñanza de
       las artes marciales. Lo supervisan el director técnico y los instructores, pero
       cuidarlo es responsabilidad de todos: son los estudiantes quienes lo mantienen.</p>
  </div>
  <a class="ha-btn" href="/sobre-nosotros/el-dojo/">Sobre el dojo</a>
</section>

<section class="ha-sec">
  <p class="ha-lab">Dónde entrenamos</p>
  <h2>Tres tatamis</h2>
  <div class="ha-prose">
    <p>Además del dojo, <strong>Aikido Musubi</strong> imparte clases en el Polideportivo
       Municipal Marina-Besòs y en la Facultad de Derecho de la Universidad de Barcelona.</p>
  </div>
  <div class="ha-ven">
    <figure><img src="/images/access-information-NdxqmVbV-00.webp" alt="" loading="lazy">
      <b>Badalona</b><small>Av. d'Alfons XIII, 351<br>Instalaciones Deportivas Badalona Sur</small></figure>
    <figure><img src="/images/access-information-NdxqmVbV-01.webp" alt="" loading="lazy">
      <b>Sant Adrià de Besòs</b><small>Poliesportiu Municipal Marina-Besòs</small></figure>
    <figure><img src="/images/access-information-NdxqmVbV-02.webp" alt="" loading="lazy">
      <b>Universitat de Barcelona</b><small>Facultat de Dret</small></figure>
  </div>
  <a class="ha-btn" href="/acceso/">Cómo llegar a cada uno</a>
</section>

<section class="ha-sec">
  <p class="ha-lab">Cómo empezar</p>
  <h2>Ven a probar</h2>
  <div class="ha-steps">
    <div class="ha-step"><p class="n">01</p><h3>Escríbenos</h3>
      <p>Con un día de aviso basta. Dinos qué clase te interesa y te decimos cuándo
         venir.</p></div>
    <div class="ha-step"><p class="n">02</p><h3>Dos clases</h3>
      <p>Sin compromiso ni coste. Ropa cómoda de manga larga; el keikogi ya llegará.</p></div>
    <div class="ha-step"><p class="n">03</p><h3>Únete</h3>
      <p>La inscripción es gratuita y está abierta todo el año.</p></div>
  </div>
  <a class="ha-btn" href="/contacto/">Escríbenos</a>
</section>

<section class="ha-sec">
  <p class="ha-lab">Dirección técnica</p>
  <h2>Pablo Martín</h2>
  <div class="ha-cho">
    <img src="/images/index-8oGCaMDs-05_.webp" alt="" loading="lazy">
    <div>
      <p class="r" style="margin-top:.2rem">Badalona, 1977 · 4.º dan · <em>shidoin</em>,
         instructor titulado por la Aikikai · presidente y director técnico</p>
      <p>Empezó a practicar en Badalona en 1999 con Ricard Coll y fundó la asociación en
         2008. Ha entrenado en el Aikido Hombu Dojo de Tokio con Ueshiba Moriteru Doshu y con
         varios de sus shihan.</p>
      <a class="ha-btn" href="/sobre-nosotros/la-asociacion/">Su trayectoria</a>
    </div>
  </div>
</section>

<section class="ha-sec">
  <p class="ha-lab">Quiénes somos</p>
  <h2>La asociación</h2>
  <div class="ha-prose">
    <p><strong>Aikido Musubi</strong> es una asociación cultural fundada en 2008, la primera
       de Barcelona autogestionada y sin ánimo de lucro dedicada a promover la práctica del
       aikido y los valores de las artes marciales tradicionales de Japón.</p>
    <p>No aboga, apoya ni practica la discriminación ilegal basada en la edad, el origen
       étnico, el género, el origen nacional, la discapacidad, la raza, la religión, la
       orientación sexual o los antecedentes socioeconómicos.</p>
  </div>
  <dl class="ha-facts">
    <dt>Denominación</dt><dd>Associació Cultural Musubi Aikido</dd>
    <dt>CIF</dt><dd>G-64799554</dd>
    <dt>Fundación</dt><dd>2008, Badalona</dd>
    <dt>Afiliación</dt><dd>Arashi Group, Aikikai Foundation (Aikido Hombu Dojo, Tokio)</dd>
  </dl>
  <a class="ha-btn" href="/sobre-nosotros/la-asociacion/">Sobre la asociación</a>
</section>

__DOOR__
</div>"""
