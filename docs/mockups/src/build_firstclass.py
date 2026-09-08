#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""/como-es-una-clase/ — the three earlier proposals folded into one page.

WHY THE PAGE EXISTS. Asked what it could not verify about this dojo, an
outside reader's answer was: "las instalaciones y la experiencia real sobre el
tatami: tamaño, número de practicantes, calidad del tatami y cómo se desarrolla
una clase normal". Nothing on the site answers that. /clases/ says what the
four disciplines are, /horarios/ when, /cuotas/ how much, /visitantes/ is
written for aikidoka passing through Barcelona. Nobody says what an hour on the
mat is like.

WHAT THIS IS. Three separate proposals — the clock, the objections, the room —
in one page, in the order somebody actually asks them:

    hero          what the page is
    lo-figs       the four numbers, which is the half nobody could verify
    Lo esencial   the same fact table every location page opens with
    La primera hora   the clock. The part that exists nowhere else.
    El tatami     the room, and the sentence that matters most:
                  it is ours, permanently laid, shared with nobody
    Lo que te frena   the six doubts, short, over an accordion
    CTA

THE SHAPE IS _layouts/location.html's, deliberately. Same hero, same .lo-figs
band, same .lo-sec rhythm, same fact list, same accordion. A reader arriving
from /badalona/ should not feel they have left the site, and the CSS already
exists.

WHAT KEEPS IT OFF THE DOORWAY-PAGE SIDE OF THE LINE. CLAUDE.md is blunt about
pages that rearrange words the site already has under a new heading. The clock
and the room are new — the clock cannot be duplicated anywhere because it is a
description rather than a fact, and the room's numbers are not published
anywhere today. "Lo que te frena" IS mostly the FAQ, and it is deliberately the
short version with a link to the long one, not a second copy.

    python3 docs/mockups/src/build_firstclass.py
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, 'docs', 'mockups', 'firstclass.html')

PHOTO = '/images/access-information-NdxqmVbV-aikido-musubi-room'

# Every figure is real. 120 m² is the dojo's own number and the only one
# published: the 9 x 13 that produced it multiplies out to 117, and a page that
# invites somebody to check the room with a tape measure should not print two
# figures that disagree. The area is what a reader wants anyway.
# THE 40 IS NOT IN THIS BAND, AND THAT IS THE POINT. As a naked figure it reads
# as a limit and cuts both ways — "qué lleno" for one reader, "qué grande" for
# another. In the prose below it sits next to the 120 m² and next to "en una
# clase normal sois bastantes menos", where it can only be read one way.
FIGS = [
    ('120 m²', 'De tatami, solo nuestro'),
    ('6',      'Días de entrenamiento a la semana'),
    ('2',      'Clases de prueba, sin coste'),
    ('2008',   'Entrenando sin parar desde'),
]

FACTS = [
    ('Cuándo', 'La clase de principiantes es los <b>martes de 19:30 a 20:30</b> '
               'en Aikido Musubi, con Pablo Martín.'),
    ('Dónde', '<b>Aikido Musubi</b>, Av. d\'Alfons XIII, 351, 08918 Badalona. '
              'Vestuarios y aparcamiento gratuito.'),
    ('Para quién', 'Adultos y jóvenes desde 12 años, con o sin experiencia previa. '
                   'No hay pruebas físicas ni mínimos.'),
    ('Qué llevar', 'Ropa cómoda de manga y pantalón largos y chanclas para pisar '
                   'fuera del tatami. Nada más.'),
    ('Cuánto', 'Las dos primeras clases no cuestan nada y la inscripción es '
               'gratuita. Después, 35 € al mes.'),
]

TIMELINE = [
    ('19:15', 'Llegas',
     'Vestuario a la izquierda. No hace falta venir con el keikogi puesto.'),
    ('19:25', 'Entras al tatami',
     'Las chanclas se quedan en el borde, con las puntas hacia fuera. Se entra '
     'descalzo y se saluda: una inclinación breve mirando al frente del dojo.'),
    ('19:30', 'Empieza',
     'Todos en <em>seiza</em>, de rodillas y en línea. Un saludo al kamiza y '
     'otro al profesor. Dura veinte segundos.'),
    ('19:33', 'Calentamiento',
     'Movilidad de muñecas, hombros y cadera —en aikido las muñecas trabajan '
     'mucho, así que se preparan a conciencia— y después desplazamientos: '
     'moverse desde el centro, girar sin cruzar los pies, entrar y salir de la '
     'línea del ataque.'),
    ('19:45', 'Ukemi',
     'Aprender a caer. Es lo primero y durante meses es lo principal. Se '
     'empieza rodando desde el suelo, sin altura y sin prisa.'),
    ('19:55', 'La primera técnica',
     'Por parejas. Uno ataca, el otro responde, y a los cuatro intentos se '
     'cambia el papel. Tu pareja llevará años practicando y ajustará su '
     'práctica a la tuya.'),
    ('20:10', 'Y las siguientes',
     'En una clase se trabajan varias técnicas, casi siempre emparentadas entre '
     'sí o partiendo del mismo ataque. Ahí es donde se empieza a ver que no son '
     'técnicas sueltas sino variaciones de una misma idea.'),
    ('20:25', 'Se cierra',
     'Seiza otra vez, saludo, y entre todos se pasa la mopa al tatami. Eso '
     'también es la clase.'),
    ('20:35', 'Después',
     'Alguien te va a preguntar qué tal. Es el momento de decir que no has '
     'entendido nada: todos empezamos ahí.'),
]

ROOM = [
    ('El tatami es solo nuestro',
     'No compartimos la sala con otras asociaciones. Nuestro dojo es un espacio '
     'independiente dedicado al 100&nbsp;% a las artes marciales y gestionado '
     'únicamente por la asociación, así que el tatami está montado siempre: no '
     'hay que montarlo ni recogerlo para entrenar.'),
    ('120 m², techos altos y aire acondicionado',
     'La sala es alta y está bien ventilada, y en verano hay aire acondicionado. '
     'Sobre el tatami caben 40 personas; en una clase normal sois bastantes '
     'menos, así que hay sitio para caer sin calcular dónde está el de al lado.'),
    ('Antes y después de la clase',
     'Además del tatami hay una sala con sofás, nevera y bebidas frías donde se '
     'acaba casi siempre. El dojo está entero renovado y en revisión constante, '
     'y esa parte —la de después— es la mitad de lo que hace que la gente vuelva.'),
    ('Vestuarios, parking y cómo llegar',
     'Vestuarios en el propio recinto y aparcamiento gratuito. El dojo está '
     'dentro de las Instalaciones Deportivas Badalona Sur y cuesta encontrarlo '
     'la primera vez: hay un plano con las tres entradas en Acceso.'),
]

# ---------------------------------------------------------------------------
# "¿Quepo yo aquí?" is one question with two halves, so it is one section.
#
# THE ACCESSIBILITY SENTENCE IS DELIBERATELY NOT A CLAIM OF ADAPTATION. The
# dojo is on one floor with no steps, so a wheelchair gets in and moves around;
# there is no adapted equipment and nobody said there is an adapted toilet.
# "Accesible" and "adaptado" are different words and the difference matters to
# the person reading it, so both are said and neither is stretched.
# ---------------------------------------------------------------------------
SAFE = [
    ('Se llega en silla de ruedas',
     'El dojo está en una sola planta y no hay ni un escalón, ni en las '
     'instalaciones ni en la sala. No está <em>adaptado</em> —no hay mecanismos '
     'específicos— pero es accesible: se entra y se circula sin ayuda. Si '
     'necesitas saber algo concreto antes de venir, pregúntanos y te lo '
     'contamos tal cual es.'),
    ('Aquí cabe todo el mundo',
     'Se entrena con quien te toque, y toca de todo: edades, cuerpos, orígenes '
     'y maneras de vivir. Este es un espacio seguro para las personas LGTBI+ y '
     'para cualquiera, y no como un lema: es la condición para practicar aquí. '
     'Si alguien no lo entiende, el problema lo tiene con nosotros y no contigo.'),
]


DOUBTS = [
    ('No estoy en forma',
     'No hace falta estarlo. Se empieza por caer y por desplazarse, y la forma '
     'llega de practicar, no al revés.'),
    ('Me voy a hacer daño',
     'Los primeros meses son <em>ukemi</em>: aprender a caer sin hacerte daño, '
     'desde el suelo y sin altura. Nadie te va a lanzar el primer día ni el primer mes.'),
    ('No conozco a nadie',
     'Se practica por parejas y se cambia varias veces por clase. En una hora '
     'habrás entrenado con media clase, quieras o no.'),
    ('Voy a ser el mayor, o el más joven',
     'Desde 12 años y sin tope. En el mismo tatami hay gente que empezó este mes '
     'y gente que lleva veinte años, y eso es deliberado.'),
    ('No sé japonés',
     'Las palabras se aprenden oyéndolas. Y si quieres ir por delante, el '
     'glosario tiene todas las que se dicen en clase.'),
    ('¿Y si no vuelvo?',
     'Dos clases de prueba sin coste, inscripción gratuita y sin permanencia. '
     'Lo raro sería saber si te gusta antes de probarlo.'),
]


def page():
    figs = ''.join(f'<div><b>{n}</b><span>{t}</span></div>' for n, t in FIGS)
    facts = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in FACTS)
    tl = ''.join(f"""
        <li class="fc-row">
          <span class="fc-h">{h}</span>
          <div class="fc-b"><b>{t}</b><p>{d}</p></div>
        </li>""" for h, t, d in TIMELINE)
    room = ''.join(f'<div class="lo-step"><h3>{t}</h3><p>{d}</p></div>'
                   for t, d in ROOM)
    safe = ''.join(f'<div class="lo-step"><h3>{t}</h3><p>{d}</p></div>'
                   for t, d in SAFE)
    doubts = ''.join(f"""
        <details class="ab-faq"{' open' if i == 0 else ''}>
          <summary>«{q}»</summary>
          <div><p>{a}</p></div>
        </details>""" for i, (q, a) in enumerate(DOUBTS))

    return f"""
<div class="mock">
  <div class="mock-nav"><b>MUSUBI</b><span>Clases y Horarios · Sobre nosotros ·
    Eventos · Media y Recursos · Contacto y Acceso</span></div>

  <div class="lo-hero">
    <picture><img src="{PHOTO}.jpg" alt=""></picture>
    <div class="lo-hero-in">
      <p class="lo-kick">Empezar · Aikido Musubi</p>
      <h1>Cómo es una clase</h1>
      <p class="lo-line">Una hora en el tatami, de principio a fin y sin
      adornos: a qué hora llegas, qué pasa en los primeros quince minutos y
      cómo es la sala. Si nunca has hecho aikido, esta es la página.</p>
      <p class="lo-cta">
        <a class="lo-btn" href="#">Ven a probar</a>
        <a class="lo-btn lo-btn-2" href="#">Ver horarios</a>
        <small>Dos clases de prueba · inscripción gratuita</small>
      </p>
    </div>
  </div>

  <div class="lo-figs">{figs}</div>

  <div class="body">
    <p class="lo-crumb"><a href="#">Inicio</a> <span>·</span> Cómo es una clase</p>

    <section class="lo-sec">
      <p class="lo-lab">Lo esencial</p>
      <h2>Lo esencial</h2>
      <dl class="lo-facts">{facts}</dl>
    </section>

    <section class="lo-sec">
      <p class="lo-lab">Minuto a minuto</p>
      <h2>La primera hora</h2>
      <p class="lo-p">Esta es la clase de principiantes de los martes, de 19:30
      a 20:30, en el dojo de Badalona. Las otras se parecen bastante.</p>
      <ol class="fc-tl">{tl}</ol>
    </section>

    <section class="lo-sec">
      <p class="lo-lab">La sala</p>
      <h2>El dojo</h2>
      <div class="lo-steps lo-steps-4">{room}</div>
    </section>

    <section class="lo-sec">
      <p class="lo-lab">¿Quepo yo aquí?</p>
      <h2>Un espacio seguro</h2>
      <div class="lo-steps lo-steps-2">{safe}</div>
    </section>

    <section class="lo-sec">
      <p class="lo-lab">Dudas</p>
      <h2>Lo que te frena</h2>
      <div class="fc-faq">{doubts}</div>
      <p class="lo-p lo-more"><a href="#">Todas las preguntas frecuentes</a></p>
    </section>

    <section class="lo-sec lo-end">
      <h2>Te esperamos</h2>
      <p class="lo-p">Escríbenos con un día de antelación, dinos qué clase te
      interesa y te decimos cuándo venir.</p>
      <p class="lo-cta">
        <a class="lo-btn" href="#">Escríbenos</a>
        <a class="lo-btn lo-btn-2" href="#">Cómo llegar</a>
      </p>
    </section>
  </div>
</div>"""


CSS = """
:root{
  --Black:#111314; --White:#fff; --Yellow:#FFF200; --Rust:#ae5224;
  --Paper:#FBFAF7; --Mute:#5A686E; --Ink:#3D4A50; --Hair:rgba(17,19,20,.14);
}
*{box-sizing:border-box}
body{margin:0;background:#F7F7F5;color:#111314;
     font:16px/1.7 "Noto Sans",-apple-system,BlinkMacSystemFont,sans-serif}
.wrap{max-width:1500px;margin:0 auto;padding:2.5rem 2rem 6rem}
.pg{font-size:1.8rem;letter-spacing:.04em;text-transform:uppercase;margin:0 0 .6rem}
.top-lede{max-width:46rem;color:var(--Ink);margin:0 0 1rem;font-size:.95rem}
.key{max-width:46rem;font-size:.93rem;color:var(--Ink);background:#fff;
     border-left:3px solid var(--Yellow);padding:.8rem 1.1rem;margin:0 0 1rem}
.warn{max-width:46rem;font-size:.93rem;color:var(--Ink);background:#fff;
      border-left:3px solid var(--Rust);padding:.8rem 1.1rem;margin:0 0 2.4rem}
.row{display:grid;grid-template-columns:1000px 1fr;gap:2.6rem;align-items:start}
@media(max-width:1460px){.row{grid-template-columns:1fr}}
.note h2{font-size:1.1rem;letter-spacing:.05em;text-transform:uppercase;margin:1.6rem 0 .5rem}
.note h2:first-child{margin-top:0}
.note p{max-width:34rem;font-size:.92rem;color:var(--Ink);margin:0 0 .8rem}
.note b{color:var(--Black)}
.note code{font:.8rem ui-monospace,Menlo,monospace}
.note ol{max-width:34rem;font-size:.92rem;color:var(--Ink);padding-left:1.1rem}
.note li{margin:0 0 .35rem}

/* ------------------------------------------------------------------ */
/* The mocked page. Class names and values are _layouts/location.html's */
/* and styles/locations.less's, so this reads as the same site.         */
/* ------------------------------------------------------------------ */
.mock{width:1000px;background:#fff;overflow:hidden;
      box-shadow:0 1px 2px rgba(17,19,20,.14),0 12px 34px rgba(17,19,20,.11)}
.mock-nav{background:var(--Black);color:#fff;padding:.9rem 2.2rem;
          display:flex;align-items:baseline;gap:1.6rem}
.mock-nav b{font-family:Futura,"Century Gothic",sans-serif;letter-spacing:.03em;
            font-size:1.05rem}
.mock-nav span{font-size:.62rem;letter-spacing:.06em;color:rgba(255,255,255,.6)}

.lo-hero{position:relative;display:flex;align-items:flex-end;min-height:26rem;
         overflow:hidden;background:var(--Black)}
.lo-hero picture,.lo-hero img{position:absolute;inset:0;display:block;
         width:100%;height:100%;object-fit:cover}
.lo-hero::after{content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(17,19,20,.12) 0%,rgba(17,19,20,.86) 78%)}
.lo-hero-in{position:relative;z-index:1;padding:3rem 2.2rem 2.5rem;color:#fff;
            max-width:46rem}
.lo-kick{margin:0;font-family:Futura,"Century Gothic",sans-serif;font-size:.62rem;
         letter-spacing:.2em;text-transform:uppercase;color:var(--Yellow)}
.lo-hero-in h1{margin:.5rem 0 .7rem;font-size:2.6rem;line-height:1.1;
   letter-spacing:.04em;text-transform:uppercase;color:#fff;
   font-family:Futura,"Century Gothic",sans-serif;font-weight:700}
.lo-line{margin:0;max-width:34rem;font-size:1.05rem;line-height:1.7;
         color:rgba(255,255,255,.88)}
.lo-cta{display:flex;align-items:center;gap:.7rem;flex-wrap:wrap;margin:1.4rem 0 0}
.lo-btn{display:inline-block;background:var(--Yellow);color:var(--Black);
        text-decoration:none;font-weight:700;font-size:.68rem;letter-spacing:.16em;
        text-transform:uppercase;padding:.85rem 1.4rem}
.lo-btn-2{background:transparent;color:#fff;box-shadow:inset 0 0 0 1px rgba(255,255,255,.5)}
.lo-cta small{font-size:.66rem;letter-spacing:.1em;color:rgba(255,255,255,.7)}
.lo-end .lo-btn-2{color:var(--Black);box-shadow:inset 0 0 0 1px var(--Hair)}

.lo-figs{display:grid;grid-template-columns:repeat(4,1fr);background:var(--Black);
         color:#fff}
.lo-figs>div{padding:1.5rem 1.6rem;border-left:1px solid rgba(255,255,255,.14)}
.lo-figs>div:first-child{border-left:0}
.lo-figs b{display:block;font-family:Futura,"Century Gothic",sans-serif;
           font-size:2.1rem;line-height:1;letter-spacing:-.01em}
.lo-figs span{display:block;margin-top:.45rem;font-size:.7rem;line-height:1.4;
              color:rgba(255,255,255,.7)}

.body{padding:0 2.2rem 3rem}
.lo-crumb{margin:1.4rem 0 0;font-size:.72rem;color:var(--Mute)}
.lo-crumb a{color:inherit}
.lo-sec{margin:3.2rem 0 0}
.lo-lab{margin:0 0 .5rem;font-family:Futura,"Century Gothic",sans-serif;
        font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;color:var(--Mute)}
.lo-sec h2{margin:0 0 1.1rem;font-size:1.6rem;letter-spacing:.01em;line-height:1.2}
.lo-p{max-width:43.25rem;color:var(--Ink);margin:0 0 1.2rem}
.lo-more{margin-top:1.2rem;font-size:.9rem}

.lo-facts{display:grid;grid-template-columns:11rem 1fr;max-width:43.25rem;margin:0;
          border-top:1px solid var(--Black)}
.lo-facts dt{padding:.95rem 1.5rem .95rem 0;border-bottom:1px solid var(--Hair);
             font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;
             color:var(--Mute);font-weight:700}
.lo-facts dd{margin:0;padding:.95rem 0;border-bottom:1px solid var(--Hair);
             color:var(--Ink);font-size:.95rem}

/* the clock — the one component this page adds */
.fc-tl{list-style:none;margin:0;padding:0;max-width:43.25rem}
.fc-row{display:grid;grid-template-columns:4.4rem 1fr;gap:1.2rem;
        padding:0 0 1.4rem;position:relative}
.fc-row::before{content:"";position:absolute;left:4.7rem;top:.6rem;bottom:0;
                width:1px;background:var(--Hair)}
.fc-row:last-child{padding-bottom:0}
.fc-row:last-child::before{display:none}
.fc-row::after{content:"";position:absolute;left:4.45rem;top:.45rem;width:.5rem;
               height:.5rem;background:var(--Rust);border-radius:50%}
.fc-h{font-weight:700;font-size:.8rem;letter-spacing:.05em;text-align:right;
      font-variant-numeric:tabular-nums;line-height:1.6}
.fc-b{padding-left:.9rem}
.fc-b b{display:block;font-size:1rem;margin-bottom:.1rem}
.fc-b p{margin:0;font-size:.92rem;color:var(--Ink)}

.lo-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;
          max-width:none}
.lo-steps-4{grid-template-columns:repeat(2,1fr);gap:1.5rem 2.4rem}
.lo-steps-2{grid-template-columns:repeat(2,1fr);gap:1.5rem 2.4rem}
.lo-step{border-top:1px solid var(--Black);padding-top:.9rem}
.lo-step h3{margin:0 0 .45rem;font-size:1rem}
.lo-step p{margin:0;font-size:.9rem;color:var(--Ink)}

.fc-faq{max-width:43.25rem;border-top:1px solid var(--Black)}
.ab-faq{border-bottom:1px solid var(--Hair)}
.ab-faq summary{cursor:pointer;padding:.9rem 0;font-size:.98rem;font-weight:600;
                list-style:none;position:relative;padding-right:2rem}
.ab-faq summary::-webkit-details-marker{display:none}
.ab-faq summary::after{content:"+";position:absolute;right:.3rem;top:.85rem;
                       color:var(--Rust);font-weight:700}
.ab-faq[open] summary::after{content:"–"}
.ab-faq div{padding:0 0 1rem}
.ab-faq p{margin:0;font-size:.93rem;color:var(--Ink);max-width:40rem}

.lo-end{border-top:2px solid var(--Black);padding-top:1.6rem}
"""


def build():
    html = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cómo es una clase — maqueta</title>
<style>""" + CSS + """</style></head><body><div class="wrap">
<h1 class="pg">Cómo es una clase</h1>
<p class="top-lede">Las tres propuestas anteriores en una sola página, con la
forma de <code>/badalona/</code>: mismo hero, misma banda de cifras, mismo
ritmo de <code>.lo-sec</code>, misma lista de datos y mismo acordeón. Quien
llegue desde una página de ciudad no debe notar que ha cambiado de sitio, y el
CSS ya existe.</p>

<p class="key"><b>El orden es el de las preguntas que se hace alguien que no ha
entrenado nunca:</b> qué es esto → cuánto y cuándo → qué pasa durante una hora
→ cómo es la sala → lo que me frena → cómo vengo. El reloj va antes que la
sala porque es el título de la página; la sala va antes que las dudas porque
media duda se disuelve al saber que hay 120&nbsp;m² y cuarenta personas de
aforo.</p>

<p class="warn"><b>Lo que queda por decidir es una sola cosa.</b> Cuánta gente
hay de verdad un martes. Dijiste 20 o 25 y no lo he puesto, porque compartes la
duda y creo que tienes razón: un número exacto invita a compararlo con el aforo
y a sacar conclusiones que no controlas. «Bastantes menos» dice lo único que le
importa a quien lee —que hay sitio— sin abrir esa puerta. Si prefieres el
número, se cambia en una línea.</p>

<div class="row">
""" + page() + """
  <div class="note">
    <h2>Qué viene de dónde</h2>
    <ol>
      <li><b>Hero + cifras</b> — la foto del tatami, como pediste, y las cuatro
      cifras de la propuesta C. Es literalmente la mitad que nadie podía
      verificar desde fuera.</li>
      <li><b>Lo esencial</b> — el mismo <code>dl</code> con el que abren las
      páginas de ciudad. Todo sale de <code>_data/</code>.</li>
      <li><b>La primera hora</b> — la propuesta A entera. El corazón de la
      página y lo único que no está en ninguna otra parte del sitio.</li>
      <li><b>El tatami</b> — la prosa de la propuesta C, en los tres
      <code>.lo-step</code> que ya usan las páginas de ciudad.</li>
      <li><b>Lo que te frena</b> — la propuesta B, acortada y en acordeón, con
      enlace a la FAQ completa debajo.</li>
    </ol>

    <h2>Por qué B va en acordeón y no abierta</h2>
    <p>Cinco de sus seis respuestas existen ya en la FAQ. Plegadas y con enlace
    a la versión larga son un resumen; desplegadas y a la misma longitud serían
    una segunda copia compitiendo por la misma consulta. La FAQ sigue siendo el
    sitio con la respuesta larga.</p>

    <h2>Lo que cambió respecto al anterior</h2>
    <p><b>El 40 sale de la banda de cifras y se queda solo en la prosa.</b> Era
    tu duda y tiene fundamento: suelto y en grande, «40 de aforo» se lee como un
    límite y corta en las dos direcciones. Junto a los 120&nbsp;m² y a
    «bastantes menos» solo se puede leer de una manera. En su lugar va 2008, que
    es la cifra que más confianza da y que ya usan las páginas de ciudad.</p>
    <p><b>No se publica el 9 × 13.</b> Multiplica 117 y la página invita a
    medir la sala. Se publica el área, que además es lo que se quiere saber.</p>
    <p><b>«Un espacio seguro» es sección propia</b> y junta accesibilidad y
    LGTBI+, porque las dos contestan la misma pregunta: «¿quepo yo aquí?».
    Sobre la silla de ruedas digo <i>accesible</i> y digo que no está
    <i>adaptado</i>, que no es lo mismo y a quien lo lee le importa la
    diferencia. No menciono aseo adaptado porque no me has dicho que lo haya.</p>
    <p><b>El calentamiento</b> es movilidad de muñecas, hombros y cadera más
    desplazamientos. Si no es así, corrígeme: lo he escrito desde lo que es
    habitual en aikido, no desde lo que me hayas contado.</p>

    <h2>Forma técnica</h2>
    <p>Como <code>/badalona/</code>: un <code>_layouts/firstclass.html</code>,
    la prosa en <code>_data/firstclass.yml</code>, las horas leídas de
    <code>_data/schedule.yml</code> para que la página siga al horario sola,
    cuatro idiomas con su <code>i18n-ref</code>, entrada en el sitemap y enlace
    desde <code>/clases/</code>, <code>/cuotas/</code> y la portada.</p>
    <p><b>El slug.</b> <code>/como-es-una-clase/</code> en castellano,
    <code>/com-es-una-classe/</code>, <code>/what-a-class-is-like/</code> y
    <code>/ja/what-a-class-is-like/</code>. A diferencia de las páginas de
    ciudad, aquí el slug no es un nombre propio y sí se traduce.</p>
  </div>
</div>
</div></body></html>
"""
    io.open(OUT, 'w', encoding='utf-8').write(html)
    print('wrote docs/mockups/firstclass.html')


if __name__ == '__main__':
    build()
