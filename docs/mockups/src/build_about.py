# -*- coding: utf-8 -*-
"""Las cuatro páginas de Sobre nosotros, ampliadas."""
import io, os
OUT = '/Applications/MAMP/htdocs/aikidomusubi.com/_site/mockups'

NAV = [('El dojo', 'about-dojo.html'), ('Aikido', 'about-aikido.html'),
       ('La asociación', 'about-asociacion.html'), ('Preguntas frecuentes', 'about-faq.html')]

CSS = """
:root{--ink:#111314;--mute:#5c6a70;--line:rgba(17,19,20,.13);--acc:#FFF200}
html,body{margin:0;background:#fff;color:var(--ink);
  font-family:'Noto Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
*{box-sizing:border-box}
h1,h2,h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;margin:0;
  letter-spacing:.04em}
p{margin:0}
.w{max-width:1140px;margin:0 auto;padding:0 6rem}
@media(max-width:991.98px){.w{padding:0 4rem}}
@media(max-width:767.98px){.w{padding:0 2rem}}
.jp{font-family:'Hiragino Sans','Noto Sans JP','Yu Gothic',sans-serif}

.ab-nav{display:flex;flex-wrap:wrap;gap:1.4rem;padding:1.6rem 0 1rem;
  border-bottom:1px solid var(--line)}
.ab-nav a{font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:#425055;
  text-decoration:none;padding:.2rem 0}
.ab-nav a:hover{color:var(--ink)}
.ab-nav a[aria-current]{color:var(--ink);font-weight:700;box-shadow:inset 0 -2px 0 var(--ink)}

.top{padding:2.6rem 0 2rem}
.top h1{font-size:2.4rem;text-transform:uppercase;letter-spacing:.06em}
.top .lede{margin-top:1rem;max-width:42rem;font-size:1.05rem;line-height:1.75;color:#2c3437}
@media(max-width:575.98px){.top h1{font-size:1.8rem}}

.body{padding-bottom:5rem;max-width:43.25rem}
.body h2{font-size:1.2rem;text-transform:uppercase;letter-spacing:.09em;margin:2.8rem 0 1rem;
  padding-top:1.5rem;border-top:1px solid var(--line)}
.body h3{font-size:1rem;margin:1.6rem 0 .5rem}
.body p{font-size:.98rem;line-height:1.85;color:#2c3437;margin-bottom:1rem}
.body a{color:var(--ink);text-decoration:underline;text-underline-offset:.18em}
.body em{font-style:italic}
.new{display:inline-block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.5rem;
  letter-spacing:.18em;text-transform:uppercase;background:var(--acc);color:var(--ink);
  padding:.16rem .42rem;vertical-align:.3em;margin-left:.6rem}

/* numbered etiquette list */
.steps{counter-reset:s;margin:0 0 1rem;padding:0;list-style:none}
.steps li{counter-increment:s;position:relative;padding:.75rem 0 .75rem 3.2rem;
  border-bottom:1px solid var(--line);font-size:.95rem;line-height:1.75;color:#2c3437}
.steps li::before{content:counter(s,decimal-leading-zero);position:absolute;left:0;top:.95rem;
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.66rem;letter-spacing:.14em;
  color:#B04E17}
.steps li b{font-weight:400;color:var(--ink)}

/* timeline */
.tl{margin:0 0 1rem;border-top:1px solid var(--line)}
.tl-i{display:grid;grid-template-columns:4.6rem 1fr;gap:1.4rem;padding:.85rem 0;
  border-bottom:1px solid var(--line);align-items:baseline}
.tl-i .y{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.95rem;color:#B04E17}
.tl-i .t{font-size:.95rem;line-height:1.7;color:#2c3437}
.tl-i .t small{display:block;color:var(--mute);font-size:.82rem;margin-top:.15rem}
.tl-i[data-q] .y{color:var(--mute)}
.tl-i[data-q] .t::after{content:'por confirmar';display:inline-block;margin-left:.5rem;
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.5rem;letter-spacing:.14em;
  text-transform:uppercase;color:#fff;background:#B04E17;padding:.1rem .38rem;vertical-align:.18em}
@media(max-width:575.98px){.tl-i{grid-template-columns:1fr;gap:.1rem}}

/* people */
.ppl{display:grid;grid-template-columns:1fr 1fr;gap:0 2.4rem;margin-bottom:1rem}
.ppl div{padding:.7rem 0;border-bottom:1px solid var(--line);display:flex;
  justify-content:space-between;gap:1rem;align-items:baseline}
.ppl b{font-weight:400;font-size:.95rem}
.ppl span{font-size:.78rem;color:var(--mute);white-space:nowrap}
@media(max-width:575.98px){.ppl{grid-template-columns:1fr}}

/* venues */
.ven{display:grid;grid-template-columns:repeat(3,1fr);gap:1.2rem;margin:1.4rem 0}
.ven figure{margin:0}
.ven img{width:100%;aspect-ratio:1;object-fit:cover;display:block}
.ven b{display:block;margin-top:.6rem;font-size:.92rem;font-weight:400}
.ven small{display:block;font-size:.78rem;color:var(--mute);line-height:1.5}
@media(max-width:575.98px){.ven{grid-template-columns:1fr}}

/* weapons */
.wep{display:grid;grid-template-columns:repeat(3,1fr);gap:2px;background:var(--line);
  margin:1.2rem 0}
.wep div{background:#fff;padding:1rem 1.05rem 1.15rem}
.wep .k{font-size:1.5rem;line-height:1.2}
.wep .r{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;letter-spacing:.18em;
  text-transform:uppercase;color:#B04E17;margin:.35rem 0 .45rem}
.wep p{font-size:.82rem;line-height:1.65;color:var(--mute);margin:0}
@media(max-width:575.98px){.wep{grid-template-columns:1fr}}

/* faq */
.faq{border-top:1px solid var(--line);max-width:43.25rem}
.faq details{border-bottom:1px solid var(--line)}
.faq summary{list-style:none;cursor:pointer;padding:1rem 2.2rem 1rem 0;position:relative;
  font-size:1.02rem;line-height:1.5;color:var(--ink)}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:'+';position:absolute;right:.3rem;top:.95rem;color:var(--mute);
  font-size:1.1rem;transition:transform .2s}
.faq details[open] summary::after{transform:rotate(45deg);color:#B04E17}
.faq summary:hover{color:#B04E17}
.faq .a{padding:0 0 1.1rem}
.faq .a p{font-size:.94rem;line-height:1.8;color:#2c3437;margin-bottom:.8rem}
.faq .a p:last-child{margin-bottom:0}
"""


def page(fname, title, lede, body):
    nav = ''.join('<a href="%s"%s>%s</a>' % (u, ' aria-current="page"' if u == fname else '', t)
                  for t, u in NAV)
    html = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s — Aikido Musubi</title><link rel="stylesheet" href="/styles/all.min.css">
<style>%s</style></head><body>
<div class="w"><nav class="ab-nav">%s</nav>
<header class="top"><h1>%s</h1><p class="lede">%s</p></header>
<div class="body">%s</div></div></body></html>""" % (title, CSS, nav, title, lede, body)
    io.open(os.path.join(OUT, fname), 'w', encoding='utf-8').write(html)
    print('  ' + fname)


# ═══════════════════════════════════════════════════════════════════════════
DOJO = """
<h2>Un espacio para las artes marciales</h2>
<p>Nuestro dojo es un espacio grande y diáfano destinado exclusivamente a la práctica y la
   enseñanza de las artes marciales. Está supervisado y gestionado por el director técnico y
   los instructores de la asociación; pero siendo responsabilidad de todos, y no sólo de los
   instructores o del profesor, lo mantienen y lo cuidan los estudiantes.</p>
<p>El dojo es un lugar ideal para profundizar en el estudio y la comprensión de las artes
   marciales, y para conocer todo tipo de personas independientemente de su edad, sexo y
   ocupación.</p>

<h2>Cómo se entra y cómo se sale<span class="new">Nuevo</span></h2>
<p>La etiqueta del dojo, el <em class="jp">礼法</em> <em>reihō</em>, no es ceremonia: es la
   manera de que cuarenta personas descalzas compartan un suelo sin estorbarse. Nadie espera
   que la sepas el primer día, y nadie te va a corregir con mala cara. Esto es todo lo que
   hay que saber.</p>
<ol class="steps">
  <li><b>El calzado se queda en el borde.</b> Al tatami se entra descalzo, siempre. Deja los
    zapatos con las puntas hacia fuera, para poder ponértelos sin girarte.</li>
  <li><b>Saluda al entrar y al salir del tatami.</b> De pie, mirando al frente del dojo, una
    inclinación breve. Es lo que separa la calle del sitio donde vas a entrenar.</li>
  <li><b>Saluda a tu compañero antes y después.</b> Antes se dice
    <em class="jp">お願いします</em> <em>onegaishimasu</em>; después,
    <em class="jp">ありがとうございました</em> <em>arigatō gozaimashita</em>.</li>
  <li><b>Si llegas tarde</b>, cámbiate, siéntate en <em>seiza</em> en el borde del tatami y
    espera a que el instructor te haga una señal. No cruces por delante de él.</li>
  <li><b>Nada de anillos, relojes ni pendientes</b>, y las uñas de manos y pies cortas. Las
    dos cosas hacen daño, y no a quien las lleva.</li>
  <li><b>El keikogi limpio</b>, cada día. Se entrena muy cerca de otra persona.</li>
  <li><b>No se come ni se bebe en el tatami</b>, y el móvil se queda en el vestuario.</li>
  <li><b>Al final se limpia entre todos.</b> Lleva cinco minutos y no es tarea de los
    principiantes: es de todos, y el director técnico también barre.</li>
</ol>

<h2>La primera vez, paso a paso<span class="new">Nuevo</span></h2>
<p>Llegas quince minutos antes. Te enseñamos dónde está el vestuario, te cambias con ropa
   cómoda de manga larga y sales al borde del tatami. Alguien te explicará las dos o tres
   cosas de la lista de arriba: nadie espera que las sepas.</p>
<p>La clase empieza sentados en <em>seiza</em>, con un saludo al frente del dojo y otro entre
   el instructor y el grupo. Después hay un calentamiento y unos ejercicios de
   <em>ukemi</em>, la caída, que es lo primero que se aprende y lo que más se repite. Luego el
   instructor muestra una técnica y se practica por parejas, cambiando de compañero varias
   veces. Se cierra con un ejercicio de respiración y otro saludo.</p>
<p>Dura una hora. No hay marcador y no gana nadie. Si algo te molesta, se para y ya está:
   se dice y se para.</p>

<h2>El shōmen<span class="new">Nuevo</span></h2>
<p>El frente del dojo, el <em class="jp">正面</em> <em>shōmen</em>, es la pared hacia la que se
   saluda. En la nuestra hay una caligrafía y un retrato del fundador, Morihei Ueshiba. El
   saludo no va dirigido a una persona ni a una religión: reconoce que lo que se practica
   aquí lo construyeron otros antes, y que uno lo recibe prestado.</p>
<p>A la entrada del tatami hay además una frase que no es japonesa de origen:
   <strong class="jp">唱えよ、友、そして入れ</strong>, «habla, amigo, y entra». Quien la
   reconozca sabrá de dónde viene. Quien no, tiene la traducción justo debajo.</p>

<h2>Los tres espacios</h2>
<p>Además de nuestra actividad en el dojo, <strong>Aikido Musubi</strong> ofrece clases en
   otros espacios de Barcelona y sus alrededores, acercando la práctica del aikido a nuevos
   entornos y comunidades.</p>
<div class="ven">
  <figure><img src="/images/access-information-NdxqmVbV-00.webp" alt="" loading="lazy">
    <b>Badalona</b><small>Av. d'Alfons XIII, 351<br>El dojo propio. Lunes a sábado.</small></figure>
  <figure><img src="/images/access-information-NdxqmVbV-01.webp" alt="" loading="lazy">
    <b>Sant Adrià de Besòs</b><small>Poliesportiu Marina-Besòs<br>Lunes y miércoles.</small></figure>
  <figure><img src="/images/access-information-NdxqmVbV-02.webp" alt="" loading="lazy">
    <b>Universitat de Barcelona</b><small>Facultat de Dret<br>Lunes y miércoles, principiantes.</small></figure>
</div>
<p><a href="/acceso/">Cómo llegar a cada uno</a> · <a href="/horarios/">Qué se da en cada uno</a></p>
"""

AIKIDO = """
<h2>El arte</h2>
<p>El aikido es un arte marcial japonés no competitivo desarrollado a principios del siglo XX
   por Morihei Ueshiba (1883-1969). Se basa en otras artes marciales tradicionales de Japón,
   principalmente <em>Daitō-ryū Aiki-jūjutsu</em>, y utiliza movimientos flexibles, naturales
   y altamente efectivos para evadir, redirigir o neutralizar los ataques utilizando la fuerza
   del oponente.</p>
<p>La práctica del aikido es un entrenamiento físico arduo que se basa en la repetición de
   ejercicios, manteniendo un buen balance entre la izquierda y la derecha, y alternando entre
   la realización de técnicas y su aceptación. El aikido no sólo es bueno para la salud, sino
   que también desarrolla la autoconfianza de forma natural para la vida diaria.</p>
<p>Se puede empezar a practicar aikido en cualquier momento, independientemente de la edad o
   de la condición física; tanto hombres como mujeres, desde adultos hasta niños.</p>

<h2>Una clase por dentro<span class="new">Nuevo</span></h2>
<p>Una hora, con la misma estructura casi siempre. Se empieza y se termina sentados, y en
   medio se repite mucho.</p>
<ol class="steps">
  <li><b>Saludo.</b> En <em>seiza</em>, al frente del dojo y entre el instructor y el grupo.</li>
  <li><b>Calentamiento.</b> Movilidad de muñecas, hombros y caderas. Las muñecas se calientan
    mucho porque muchas técnicas trabajan sobre ellas.</li>
  <li><b>Ukemi.</b> Caídas hacia atrás, hacia delante, rodando. Es la mitad del aikido y lo
    primero que aprende quien llega.</li>
  <li><b>Técnica.</b> El instructor la muestra dos o tres veces y se practica por parejas,
    alternando quien la hace y quien la recibe, y cambiando de compañero varias veces.</li>
  <li><b>Kokyū hō.</b> Un ejercicio de respiración sentados, que cierra la sesión.</li>
  <li><b>Saludo y limpieza.</b> Cinco minutos entre todos.</li>
</ol>

<h2>Las armas<span class="new">Nuevo</span></h2>
<p>Un arte que no compite estudia armas por una razón concreta: el aikido nace del trabajo
   con el sable, y muchos movimientos de mano vacía se entienden mejor cuando se han hecho
   antes con un <em>bokken</em> en las manos. Las tres son de madera y nunca se usan con
   filo.</p>
<div class="wep">
  <div><p class="k jp">木刀</p><p class="r">Bokken</p>
    <p>El sable de madera. De él vienen los cortes <em>shōmen</em> y <em>yokomen</em>, que son
      la base de medio programa.</p></div>
  <div><p class="k jp">杖</p><p class="r">Jō</p>
    <p>El bastón, de metro y pico. Enseña la distancia y el trabajo con las dos manos
      separadas.</p></div>
  <div><p class="k jp">短刀</p><p class="r">Tantō</p>
    <p>El cuchillo. Se usa para las técnicas de desarme, siempre despacio y siempre con el
      compañero avisado.</p></div>
</div>
<p>En Aikido Musubi hay una clase semanal dedicada a armas.
   <a href="/horarios/">Ver cuándo</a>.</p>

<h2>Grados y exámenes</h2>
<p>Los grados <em>kyu</em> los examina el dojo. Los grados <em>dan</em> se presentan y quedan
   registrados en la Aikikai Foundation de Tokio, que los reconoce internacionalmente a través
   de la International Aikido Federation.</p>
<p>No hay una fecha fija para presentarse: se propone cuando el instructor considera que el
   trabajo está hecho. Cada examen tiene un programa concreto de ataques y técnicas, y un
   número mínimo de días de práctica desde el grado anterior. Antes de cada convocatoria hay
   clases de preparación abiertas a todo el que se vaya a examinar.</p>
<p>Los programas completos están en <a href="/recursos/">Recursos</a>.</p>

<h2>Una historia breve<span class="new">Nuevo</span></h2>
<p>Morihei Ueshiba nace en Tanabe en 1883 y estudia varias escuelas tradicionales antes de
   encontrar el <em>Daitō-ryū Aiki-jūjutsu</em> de Sokaku Takeda, que sería la base técnica
   de lo que vino después. En los años treinta abre en Tokio el dojo que acabaría llamándose
   Aikikai Hombu Dojo, y va desplazando el arte desde la eficacia marcial pura hacia la idea
   que le da nombre: unirse a la fuerza del otro en lugar de chocar con ella.</p>
<p>Tras la Segunda Guerra Mundial, y con la ocupación levantando la prohibición sobre las
   artes marciales, sus alumnos empiezan a enseñar fuera de Japón. Llega a Europa en los años
   cincuenta y sesenta, y a España en los setenta. Hoy la Aikikai Foundation, dirigida por el
   nieto del fundador, coordina el reconocimiento de grados en todo el mundo a través de la
   International Aikido Federation.</p>
"""

ASOC = """
<h2>La asociación</h2>
<p><strong>Aikido Musubi</strong> (CIF: G-64799554) es una asociación cultural fundada en
   2008. Es la primera asociación en Barcelona autogestionada y sin ánimo de lucro cuyo
   objetivo es promover la práctica del aikido y los valores de las artes marciales
   tradicionales de Japón. Desde entonces somos un actor principal en el área metropolitana de
   Barcelona ofreciendo un espacio 100 % dedicado a las artes marciales y la cultura
   japonesa.</p>
<p><strong>Aikido Musubi</strong> no aboga, apoya ni practica la discriminación ilegal basada
   en la edad, el origen étnico, el género, el origen nacional, la discapacidad, la raza, la
   religión, la orientación sexual o los antecedentes socioeconómicos.</p>

<h2>Desde 2008<span class="new">Nuevo</span></h2>
<p>Empezamos con un tatami en Badalona y desde entonces no hemos parado ningún curso. Por el
   camino se abrieron las clases de Sant Adrià de Besòs y las de la Facultad de Derecho de la
   Universidad de Barcelona, salieron los primeros grados dan de la casa, y el dojo pasó de
   recibir maestros de vez en cuando a traer varios seminarios cada año.</p>
<p>No llevamos la cuenta con solemnidad, pero sí la llevamos: en el archivo hay
   <a href="/galeria/">462 momentos guardados</a> y el <a href="/seminarios/">registro de
   seminarios</a> arranca en 2020 y va por treinta y nueve. Es una historia mejor contada en
   fotos que en fechas.</p>

<h2>Cómo funciona<span class="new">Nuevo</span></h2>
<p>La Junta Directiva está constituida por el Presidente, el Secretario y el Tesorero, que a
   su vez asumen el rol de director técnico e instructores respectivamente. Son miembros
   fundadores activos con experiencia significativa dentro de la asociación que han sido
   elegidos por la Asamblea General, compuesta por todos los miembros de la asociación.</p>
<p>La Asamblea se reúne una vez al año, aprueba las cuentas y decide lo que hay que decidir.
   Cualquier socio puede asistir, hablar y votar. <strong>Nadie cobra por enseñar</strong>: las
   cuotas cubren el alquiler del espacio, el mantenimiento del tatami, los seguros, las
   licencias federativas y los seminarios que traemos. Lo que sobra se queda en el dojo.</p>
<p>Los estatutos y las cuentas están a disposición de cualquier socio que los pida.</p>

<h2>Quién enseña<span class="new">Nuevo</span></h2>
<div class="ppl">
  <div><b>Pablo Martín</b><span>4.º dan / shidoin</span></div>
  <div><b>Pedro Fortes</b><span>4.º dan</span></div>
  <div><b>José Luis Zafra</b><span>4.º dan</span></div>
  <div><b>Alberto Sancho</b><span>4.º dan</span></div>
  <div><b>Juanma Pérez</b><span>3.<sup>er</sup> dan</span></div>
  <div><b>Andreu Villar</b><span>3.<sup>er</sup> dan</span></div>
  <div><b>Guanlong Zheng</b><span>3.<sup>er</sup> dan</span></div>
</div>
<p><a href="/horarios/">Quién da cada clase</a></p>

<h2>Dirección técnica</h2>
<p><strong>Pablo Martín</strong> (Badalona, 1977) empezó a practicar aikido en Badalona en el
   año 1999 con Ricard Coll. Después ha continuado su práctica al mismo tiempo que ejerce como
   instructor en <strong>Aikido Musubi</strong>. A lo largo de su trayectoria ha participado en
   numerosos cursos y seminarios de maestros reputados como Yamada Y. Shihan, Sugano S. Shihan,
   Shibata I. Shihan, M. Flynn Shihan, D. Waite Shihan y P. Bernath Shihan, entre otros.</p>
<p>También ha viajado a Japón para entrenar en la sede mundial del aikido, el Aikido Hombu
   Dojo, con Ueshiba Moriteru Doshu, Miyamoto T. Shihan, Yokota Y. Shihan, Osawa Hayato Shihan,
   Kuribayashi T. Shihan, Kanazawa T. Shihan y Suzuki T. Shihan, entre otros.</p>
<p>Con el propósito de promover el aikido en Barcelona y sus alrededores, estableció la
   Asociación Cultural Musubi Aikido en el año 2008, y más tarde asumió los roles de presidente
   de la asociación y director técnico.</p>
<p>Actualmente tiene el grado de 4.º dan y el título de <em>shidoin</em>, instructor titulado
   por la Aikikai, otorgado por Aikido Doshu Ueshiba Moriteru y reconocido a nivel mundial por
   la <em>Aikikai Foundation</em> y la <em>International Aikido Federation</em>.</p>
"""

QA = [
    ("¿Sirve el aikido para defenderse?",
     "<p>Sí, pero no es la razón por la que la mayoría se queda. El aikido enseña a no estar "
     "donde llega el golpe, a mantener la distancia y a controlar a alguien sin hacerle daño, "
     "y todo eso sirve. Lo que no hace es prepararte para una pelea en dos meses: es un "
     "estudio largo y lo dice de entrada.</p>"),
    ("¿Es peligroso? ¿Me van a hacer daño?",
     "<p>Se practica por parejas y con contacto, así que hay que tener cuidado, y eso es "
     "exactamente lo que se entrena. No hay competición ni golpes al contacto, la intensidad "
     "la ponen los dos y basta con decir que algo molesta para que se pare.</p>"
     "<p>Lo primero que se aprende, antes que cualquier técnica, es a caer.</p>"),
    ("¿Tengo que ser flexible o estar en forma?",
     "<p>No. Se empieza donde se está, y el calentamiento y el ukemi construyen la movilidad "
     "que hace falta. Si tienes una lesión o una limitación concreta, dilo antes de empezar y "
     "se adapta.</p>"),
    ("¿Desde qué edad? ¿Hay clases para niños?",
     "<p>Escríbenos y te decimos qué grupo encaja. Hay adultos de todas las edades practicando "
     "a la vez, que es una de las cosas buenas de que no haya categorías por peso ni por "
     "edad.</p>"),
    ("¿Cuánto cuesta empezar?",
     "<p>Las dos primeras clases no cuestan nada y la inscripción es gratuita todo el año. "
     "A partir de ahí hay una cuota mensual según la actividad: está toda en "
     "<a href=\"/cuotas/\">Cuotas</a>.</p>"),
    ("¿Qué me pongo el primer día?",
     "<p>Ropa cómoda que cubra los brazos y las piernas, del tipo chándal y camiseta de manga "
     "larga. Al tatami se entra descalzo. El keikogi ya llegará cuando decidas quedarte.</p>"),
    ("¿Cuándo puedo empezar?",
     "<p>Cualquier semana del año. No hay curso ni temporada: los grupos son abiertos y se "
     "entra cuando se puede.</p>"),
    ("¿Cuánto se tarda en llevar hakama?",
     "<p>Depende del dojo y de la línea. En la nuestra el hakama va asociado al grado, no al "
     "tiempo, y el grado llega cuando el trabajo está hecho. Nadie te va a dar una fecha, y "
     "esa es parte de la respuesta.</p>"),
    ("¿Hay competiciones?",
     "<p>No. El aikido no tiene competición por decisión de su fundador, y eso cambia bastante "
     "cómo se practica: tu compañero no es un rival, es la persona con la que estás "
     "aprendiendo.</p>"),
    ("¿Puedo ir a mirar antes de apuntarme?",
     "<p>Sí. Avísanos con un día y te decimos cuándo venir. Dicho esto, mirar aikido dice "
     "bastante menos que probarlo, y probarlo tampoco cuesta nada.</p>"),
    ("Estoy de paso por Barcelona y practico aikido. ¿Puedo entrenar?",
     "<p>Claro. Escríbenos antes con tu grado y tu dojo de origen y te decimos qué clases hay "
     "esos días. Está explicado en <a href=\"/visitantes/\">Visitantes</a>.</p>"),
    ("¿Hay que saber japonés?",
     "<p>No, pero se oye japonés en cada clase: los nombres de las técnicas, los saludos y los "
     "números. Se aprende solo, por repetición. Y si quieres adelantarte, está el "
     "<a href=\"/glosario/\">glosario</a>.</p>"),
    ("¿Tengo que federarme?",
     "<p>Sí, la licencia federativa incluye el seguro deportivo, que es obligatorio. Se "
     "tramita desde el dojo una vez al año.</p>"),
    ("¿Cuántos días a la semana hay que ir?",
     "<p>Con dos ya se avanza. Con uno se mantiene, y con tres o cuatro se nota mucho. No hay "
     "un mínimo obligatorio: la cuota da acceso a todas las clases de tu actividad y vas las "
     "que puedas.</p>"),
    ("Tengo una lesión antigua. ¿Puedo practicar?",
     "<p>Casi siempre sí, y hay gente entrenando con rodillas, hombros y espaldas de todo "
     "tipo. Cuéntanoslo antes de la primera clase y el instructor te dirá qué adaptar. Lo que "
     "no hacemos es decidir por ti: si tu médico te ha dicho algo, hazle caso a él.</p>"),
    ("¿Saludar es una cosa religiosa?",
     "<p>No. El saludo al frente del dojo reconoce que lo que se practica aquí lo "
     "construyeron otros antes; el saludo al compañero es agradecerle que preste su cuerpo "
     "para que aprendas. No hay culto, ni oración, ni se pide creer en nada.</p>"),
    ("¿Hay vestuarios y duchas? ¿Dónde aparco?",
     "<p>En Badalona hay vestuarios y el aparcamiento es gratuito. Los otros dos espacios son "
     "instalaciones municipales y universitarias con sus propias condiciones: están "
     "detalladas en <a href=\"/acceso/\">Acceso</a>.</p>"),
    ("¿Se para en agosto o en vacaciones?",
     "<p>En agosto el horario se reduce y en los festivos el dojo cierra. Todo eso está, con "
     "fechas, en el <a href=\"/calendario/\">calendario</a>.</p>"),
    ("Si dejo de venir unos meses, ¿pierdo algo?",
     "<p>No. Se puede pausar y volver, y volver después de años también. El grado no caduca y "
     "el sitio sigue estando.</p>"),
    ("¿Tengo que comprar armas?",
     "<p>Al principio no. Hay bokken y jō del dojo para usar. Cuando decidas comprarte los "
     "tuyos te decimos dónde y qué medida te conviene.</p>"),
    ("¿Puedo hacer fotos o vídeo en clase?",
     "<p>Pregunta antes. En el tatami hay menores y hay gente que no quiere salir, y eso "
     "manda por encima de cualquier foto.</p>"),
    ("¿Y las otras artes que se dan en el dojo?",
     "<p>El mismo tatami acoge iaijutsu, judo y karate, cada uno con su instructor y su "
     "horario. Están en <a href=\"/clases/\">Clases</a>.</p>"),
]

FAQ = '<div class="faq">' + ''.join(
    '<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        ' open' if i == 0 else '', q, a) for i, (q, a) in enumerate(QA)) + '</div>'

page('about-dojo.html', 'El dojo',
     'Dónde entrenamos, cómo se cuida el espacio y qué encontrarás cuando llegues.', DOJO)
page('about-aikido.html', 'Aikido',
     'Qué es, de dónde viene y cómo se practica aquí.', AIKIDO)
page('about-asociacion.html', 'La asociación',
     'Quiénes somos, cómo nos organizamos y con quién estamos afiliados.', ASOC)
page('about-faq.html', 'Preguntas frecuentes',
     'Lo que nos preguntan por correo, por teléfono y en el borde del tatami. Si tu pregunta '
     'no está, <a href="/contacto/" style="color:inherit">mándanosla</a> y la añadimos.', FAQ)
