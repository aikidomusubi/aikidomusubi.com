# -*- coding: utf-8 -*-
"""Two ways to build a location page, on the one that matters most: Barcelona.

    loc-barcelona-a.html   "La respuesta primero" — reference entry
    loc-barcelona-b.html   "La visita" — landing page

THE SAME FACTS IN BOTH. What differs is the order they arrive in and what the
page looks like it is FOR. Everything on both pages is true and came out of
_data/venues.yml, _data/schedule.yml and _data/fees.yml — no lorem, no invented
prices, no invented policies. If a fact is not in this repo it is not on these
pages.

WHY BARCELONA AND NOT THE OTHER TWO. Whichever wins is meant to be the template
for /badalona/ and /sant-adria-de-besos/ as well, and Barcelona is the hardest
case: two rooms, two teachers, two timetables, and a town where the dojo
currently ranks tenth. If a layout can carry Barcelona it can carry the others.

WHAT MAKES THESE NOT DOORWAY PAGES, which is the thing to get right:

  * Every fact on the page is specific to these two rooms. The addresses, the
    hours, the teachers, the way in, the floor plans.
  * Nothing is copied from /clases/ or /cuotas/. Where the reader needs the
    long version they get a link, which is also the internal linking these
    pages need in order to be crawled at all.
  * The FAQ answers "how is this different from Badalona", honestly, which is
    the question a real reader has and the one a doorway page cannot answer.
  * The children's classes are in Badalona only, and both pages say so rather
    than implying a Barcelona class that does not exist.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

# ---------------------------------------------------------------------------
# The facts. All of them out of _data/.
# ---------------------------------------------------------------------------
VENUES = [
    dict(
        name="CxEM Espronceda",
        facility="Complejo Deportivo Municipal Espronceda",
        street="C/ Espronceda, 326",
        post="08027 Barcelona",
        room="Sala de tatami",
        days="Lunes y miércoles",
        time="20:00 – 21:00",
        level="Todos los niveles",
        teacher="Daniil Mikhaylov",
        grade="3.er dan Aikikai",
        plan="/images/access-information-NdxqmVbV-03-480.webp",
        door="Entrada principal por la calle de Espronceda.",
        gmaps="https://maps.app.goo.gl/xE1cHD7zRygTG78z9",
        amaps="https://maps.apple/p/czWeasADhbQc~p",
    ),
    dict(
        name="Facultat de Dret de la UB",
        facility="Facultad de Derecho, Universitat de Barcelona",
        street="Av. Diagonal, 684",
        post="08034 Barcelona",
        room="Sala polivalente «La Capella»",
        days="Lunes y miércoles",
        time="19:00 – 20:00",
        level="Principiantes",
        teacher="Pablo Martín",
        grade="4.º dan Aikikai",
        plan="/images/access-information-NdxqmVbV-02-480.webp",
        door="Sube la escalinata hasta la entrada principal; «La Capella» está dentro del edificio.",
        gmaps="https://www.google.com/maps/search/?api=1&query=Facultat+de+Dret+Universitat+de+Barcelona",
        amaps="https://maps.apple/p/WpkTJqkJdjE~RE",
    ),
]

FAQ = [
    ("¿Necesito experiencia previa?",
     "No. La clase de la Facultad de Derecho es de principiantes y la de Espronceda es de "
     "todos los niveles, lo que significa que quien empieza entrena junto a quien lleva años. "
     "En aikido no hay competición, así que nadie está midiéndose contigo."),
    ("¿Tengo que comprar un keikogi para empezar?",
     "No. Para las primeras clases basta con ropa cómoda de manga larga y pantalón largo. "
     "Si después te matriculas por trimestre, semestre o año, el keikogi lo pone el dojo."),
    ("¿Puedo probar antes de apuntarme?",
     "Sí: dos clases de prueba, y la inscripción no cuesta nada. Escríbenos y te decimos "
     "qué día venir."),
    ("¿Cuánto cuesta?",
     "35 € al mes para adultos, 25 € para menores de 12 años, con descuentos por trimestre, "
     "semestre y año y una cuota familiar. El detalle completo está en la página de cuotas."),
    ("¿Hay clases para niños en Barcelona?",
     "Todavía no. La clase infantil se imparte en el dojo de Badalona. En Barcelona las clases "
     "son para mayores de 12 años."),
    ("¿En qué se diferencia de las clases de Badalona?",
     "Es la misma asociación, el mismo programa y los mismos exámenes; cambia la sala y el "
     "horario. Badalona es el dojo principal y abre de lunes a sábado, con aikido, judo, "
     "iaijutsu y karate. En Barcelona hay aikido los lunes y los miércoles. Muchas personas "
     "entrenan en las dos."),
]

STEPS = [
    ("Escríbenos", "Un correo o un WhatsApp. Te decimos qué día viene mejor y quién te va a recibir."),
    ("Ven quince minutos antes", "Te enseñamos el vestuario y la sala, y te presentamos a quien va a entrenar contigo."),
    ("Ropa cómoda y nada más", "Manga larga, pantalón largo, pies descalzos. No hace falta keikogi ni material."),
    ("Entrena", "Una hora. Nadie te va a poner a prueba el primer día."),
]

# ---------------------------------------------------------------------------
CSS = """
:root{
  --ink:#111314; --mute:#4f5d63; --line:rgba(17,19,20,.13);
  --hair:rgba(17,19,20,.08); --acc:#FFF200; --aik:#E2625E;
  --paper:#fff; --tint:#f6f6f4; --deep:#064F6E;
}
*{box-sizing:border-box}
html,body{margin:0;background:#e9e9e6;color:var(--ink);
  font-family:'Noto Sans',system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}
h1,h2,h3,h4,.fut{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
  letter-spacing:.03em;margin:0}
p{margin:0}
a{color:inherit}

/* ---- the wrapper around the prototype --------------------------------- */
.sheet{max-width:1240px;margin:0 auto;padding:2.5rem 1.5rem 5rem}
.sheet > header{margin-bottom:1.5rem}
.kick{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--mute)}
.sheet > header h1{font-size:2rem;text-transform:uppercase;margin:.6rem 0 .5rem}
.sheet > header p{font-size:1rem;line-height:1.7;color:#2c3437;max-width:46rem}
.frame{background:var(--paper);border-radius:8px;overflow:hidden;
  box-shadow:0 20px 50px rgba(0,0,0,.13)}

/* ---- the page itself --------------------------------------------------- */
.nv{background:#111314;color:#fff;padding:0 2rem;height:56px;display:flex;
  align-items:center;justify-content:space-between}
.nv b{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.1rem;letter-spacing:.1em}
.nv nav{display:flex;gap:1.5rem;font-size:.78rem;color:#b9bec0}
.nv nav span[data-on]{color:#fff;border-bottom:2px solid var(--acc);padding-bottom:2px}
.wrap{max-width:1140px;margin:0 auto;padding:0 4rem}
@media(max-width:900px){.wrap{padding:0 2rem}}
.crumb{font-size:.72rem;color:var(--mute);padding:1.4rem 0 0}
.crumb a{text-decoration:none;border-bottom:1px solid var(--line)}
h2{font-size:1.3rem;text-transform:uppercase;letter-spacing:.07em;
  padding-bottom:.6rem;border-bottom:2px solid var(--ink);margin:3rem 0 1.4rem}
h3{font-size:1rem;letter-spacing:.05em}
.lede{font-size:1.12rem;line-height:1.75;color:#2c3437;max-width:43rem}
.body p{font-size:.95rem;line-height:1.8;color:#2c3437;max-width:43rem;margin-bottom:1rem}
.tail{background:#111314;color:#8b9296;padding:2.5rem 4rem;font-size:.75rem;margin-top:3rem}

.btn{display:inline-flex;align-items:center;gap:.5rem;padding:.75rem 1.4rem;
  background:var(--ink);color:#fff;text-decoration:none;
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.72rem;letter-spacing:.16em;
  text-transform:uppercase}
.btn-2{background:none;color:var(--ink);box-shadow:inset 0 0 0 1px var(--line)}
.cta{display:flex;gap:.7rem;flex-wrap:wrap;align-items:center;margin-top:1.6rem}
.cta small{font-size:.75rem;color:var(--mute)}

/* the quotable fact block */
.ficha{border:1px solid var(--ink);margin-top:2rem}
.ficha-h{background:var(--ink);color:#fff;padding:.55rem 1.2rem;
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;letter-spacing:.2em;
  text-transform:uppercase}
.ficha dl{margin:0;display:grid;grid-template-columns:11rem 1fr}
@media(max-width:640px){.ficha dl{grid-template-columns:1fr}}
.ficha dt{padding:.85rem 1.2rem;border-bottom:1px solid var(--hair);
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.65rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--mute);background:var(--tint)}
.ficha dd{margin:0;padding:.85rem 1.2rem;border-bottom:1px solid var(--hair);
  font-size:.9rem;line-height:1.7}
.ficha dd b{font-weight:600}
.ficha dl > :nth-last-child(-n+2){border-bottom:0}

/* venue cards */
.vens{display:grid;grid-template-columns:1fr 1fr;gap:1.6rem}
@media(max-width:820px){.vens{grid-template-columns:1fr}}
.ven{border:1px solid var(--line);display:flex;flex-direction:column}
.ven img{display:block;width:100%;height:170px;object-fit:cover;background:var(--tint)}
.ven-in{padding:1.2rem;display:flex;flex-direction:column;gap:.55rem;flex:1}
.ven h3{font-size:1.05rem}
.ven .addr{font-size:.85rem;line-height:1.6;color:var(--mute)}
.ven .when{display:flex;align-items:baseline;gap:.5rem;padding:.5rem 0;
  border-top:1px solid var(--hair);border-bottom:1px solid var(--hair);
  font-size:.85rem}
.ven .when b{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.95rem}
.tag{display:inline-block;padding:.15rem .5rem;background:var(--aik);color:#fff;
  font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.55rem;letter-spacing:.14em;
  text-transform:uppercase;vertical-align:middle}
.who{font-size:.85rem;color:var(--mute)}
.who b{color:var(--ink);font-weight:600}
.maps{display:flex;gap:.5rem;margin-top:auto;padding-top:.6rem}
.maps a{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.6rem;letter-spacing:.13em;
  text-transform:uppercase;text-decoration:none;padding:.45rem .8rem;
  box-shadow:inset 0 0 0 1px var(--line);color:var(--mute)}

/* faq */
.faq{border-top:1px solid var(--line)}
.faq-q{border-bottom:1px solid var(--line);padding:1.05rem 0}
.faq-q h3{font-size:.95rem;margin-bottom:.45rem}
.faq-q p{font-size:.9rem;line-height:1.75;color:var(--mute);max-width:46rem}

/* hero, approach B */
.hero{position:relative;min-height:400px;display:flex;align-items:flex-end;
  background:#111314 center/cover no-repeat}
.hero::after{content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(17,19,20,.15),rgba(17,19,20,.86))}
.hero-in{position:relative;z-index:1;padding:2.5rem 4rem;color:#fff;max-width:44rem}
.hero-in .kick{color:var(--acc)}
.hero-in h1{font-size:2.6rem;text-transform:uppercase;margin:.5rem 0 .7rem}
.hero-in p{font-size:1.05rem;line-height:1.7;color:#dfe2e3}
.hero .btn{background:var(--acc);color:var(--ink)}
.hero .btn-2{background:none;color:#fff;box-shadow:inset 0 0 0 1px rgba(255,255,255,.4)}
.hero .cta small{color:#b9bec0}

.strip{display:grid;grid-template-columns:repeat(4,1fr);background:var(--ink);color:#fff}
@media(max-width:760px){.strip{grid-template-columns:1fr 1fr}}
.strip div{padding:1.1rem 1rem;text-align:center;border-left:1px solid rgba(255,255,255,.12)}
.strip div:first-child{border-left:0}
.strip b{display:block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.25rem}
.strip span{display:block;margin-top:.3rem;font-size:.63rem;letter-spacing:.14em;
  text-transform:uppercase;color:#9aa1a4}

.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:1.4rem}
@media(max-width:820px){.steps{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.steps{grid-template-columns:1fr}}
.step{border-top:2px solid var(--ink);padding-top:.85rem}
.step b{display:block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.6rem;
  line-height:1;color:var(--aik)}
.step h3{margin:.5rem 0 .35rem;font-size:.95rem}
.step p{font-size:.85rem;line-height:1.7;color:var(--mute)}

/* small timetable */
.tt{width:100%;border-collapse:collapse;font-size:.88rem}
.tt th{text-align:left;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
  letter-spacing:.15em;text-transform:uppercase;color:var(--mute);
  padding:.5rem .8rem .5rem 0;border-bottom:1px solid var(--ink)}
.tt td{padding:.75rem .8rem .75rem 0;border-bottom:1px solid var(--hair);vertical-align:top}
.tt td:first-child{font-family:Futura,'Trebuchet MS',Arial,sans-serif;white-space:nowrap}

/* the authority strip, approach C */
.auth{display:grid;grid-template-columns:repeat(4,1fr);background:var(--ink);color:#fff}
@media(max-width:760px){.auth{grid-template-columns:1fr 1fr}}
.auth div{padding:1.15rem 1rem;text-align:center;border-left:1px solid rgba(255,255,255,.12)}
.auth div:first-child{border-left:0}
.auth b{display:block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.35rem;
  color:var(--acc)}
.auth span{display:block;margin-top:.3rem;font-size:.62rem;letter-spacing:.14em;
  text-transform:uppercase;color:#9aa1a4}

/* related */
.rel{display:flex;gap:.7rem;flex-wrap:wrap;margin-top:1rem}
.rel a{text-decoration:none;padding:.7rem 1.1rem;box-shadow:inset 0 0 0 1px var(--line);
  font-size:.85rem}
.rel a b{font-family:Futura,'Trebuchet MS',Arial,sans-serif;display:block;font-size:.95rem}
.rel a span{font-size:.75rem;color:var(--mute)}

/* ---- the rationale panel ---------------------------------------------- */
.why{max-width:1240px;margin:2.5rem auto 0;padding:0 1.5rem}
.why-in{background:#111314;color:#c9cdcf;border-radius:8px;padding:2rem 2.2rem}
.why h2{color:#fff;border-bottom-color:rgba(255,255,255,.25);margin-top:2rem;font-size:1rem}
.why h2:first-child{margin-top:0}
.why p,.why li{font-size:.88rem;line-height:1.75}
.why ul{margin:.4rem 0 0;padding-left:1.1rem}
.why li{margin-bottom:.4rem}
.why code{font-family:ui-monospace,Menlo,monospace;font-size:.8rem;color:var(--acc)}
.why .two{display:grid;grid-template-columns:1fr 1fr;gap:2rem}
@media(max-width:820px){.why .two{grid-template-columns:1fr}}
"""


def faq_html():
    out = ['<div class="faq">']
    for q, a in FAQ:
        out.append('<div class="faq-q"><h3>%s</h3><p>%s</p></div>' % (q, a))
    out.append('</div>')
    return ''.join(out)


def venue_cards():
    out = ['<div class="vens">']
    for v in VENUES:
        out.append("""
        <article class="ven">
          <img src="%(plan)s" alt="Plano de acceso a %(name)s" loading="lazy">
          <div class="ven-in">
            <h3>%(name)s</h3>
            <p class="addr">%(facility)s<br>%(street)s · %(post)s<br>%(room)s</p>
            <p class="when"><b>%(days)s</b> %(time)s <span class="tag">%(level)s</span></p>
            <p class="who">Con <b>%(teacher)s</b>, %(grade)s</p>
            <p class="who">%(door)s</p>
            <p class="maps"><a href="%(gmaps)s">Google Maps</a><a href="%(amaps)s">Apple Maps</a></p>
          </div>
        </article>""" % v)
    out.append('</div>')
    return ''.join(out)


def timetable():
    rows = ''.join(
        '<tr><td>%s<br><span style="color:var(--mute)">%s</span></td>'
        '<td>%s</td><td>%s</td><td>%s</td></tr>'
        % (v['time'], v['days'], v['name'], v['level'], v['teacher'])
        for v in VENUES)
    return ('<table class="tt"><thead><tr><th>Cuándo</th><th>Dónde</th>'
            '<th>Nivel</th><th>Quién</th></tr></thead><tbody>%s</tbody></table>' % rows)


RELATED = """
<div class="rel">
  <a href="/badalona/"><b>Badalona</b><span>El dojo principal · aikido, judo, iaijutsu y karate</span></a>
  <a href="/sant-adria-de-besos/"><b>Sant Adrià de Besòs</b><span>Marina-Besòs · aikido los lunes y miércoles</span></a>
  <a href="/horarios/"><b>Horario completo</b><span>Las cuatro salas, semana a semana</span></a>
</div>"""

NAV = """<div class="nv"><b>MUSUBI</b><nav><span>Clases y horarios</span>
<span data-on>Dónde entrenamos</span><span>Eventos</span><span>Contacto</span></nav></div>"""


FICHA = """
    <div class="ficha">
      <div class="ficha-h">Aikido en Barcelona · lo esencial</div>
      <dl>
        <dt>Dónde</dt><dd><b>CxEM Espronceda</b>, C/ Espronceda 326, 08027 Barcelona<br>
          <b>Facultat de Dret de la UB</b>, Av. Diagonal 684, 08034 Barcelona</dd>
        <dt>Cuándo</dt><dd>Lunes y miércoles. De 19:00 a 20:00 en la Facultad de Derecho
          (principiantes) y de 20:00 a 21:00 en Espronceda (todos los niveles).</dd>
        <dt>Para quién</dt><dd>Adultos y jóvenes desde 12 años, con o sin experiencia previa.
          Las clases infantiles se imparten en Badalona.</dd>
        <dt>Cuánto</dt><dd>35 € al mes para adultos. Inscripción gratuita y dos clases de prueba.</dd>
        <dt>Qué llevar</dt><dd>Ropa cómoda de manga y pantalón largos. El keikogi no hace
          falta para empezar.</dd>
        <dt>Quién enseña</dt><dd>Daniil Mikhaylov, 3.er dan Aikikai, y Pablo Martín, 4.º dan
          Aikikai y responsable del dojo.</dd>
        <dt>Quién lo organiza</dt><dd>Aikido Musubi, asociación cultural sin ánimo de lucro
          fundada en 2008, miembro de Aikikai Foundation (Hombu Dojo, Tokio).</dd>
      </dl>
    </div>"""


# ===========================================================================
# A — la respuesta primero
# ===========================================================================
def page_a():
    ficha = FICHA
    return """
%(nav)s
<div class="wrap">
  <p class="crumb"><a href="/">Inicio</a> · <a href="/acceso/">Dónde entrenamos</a> · Barcelona</p>
  <h1 style="font-size:2.4rem;text-transform:uppercase;margin:.8rem 0 1rem">Aikido en Barcelona</h1>
  <p class="lede">Entrenamos aikido en dos salas de Barcelona, los lunes y los miércoles:
     el complejo deportivo municipal de Espronceda y la Facultad de Derecho de la
     Universitat de Barcelona. Somos el mismo dojo que abre cada día en Badalona desde 2008.</p>
  %(ficha)s

  <h2>Las dos salas</h2>
  %(vens)s

  <h2>Cómo es una clase</h2>
  <div class="body">
    <p>Una hora. Se empieza y se termina saludando, se calienta, y después se trabaja por
       parejas: uno ataca, el otro responde, y a los pocos minutos se cambia. No hay
       combate ni competición, así que quien lleva un mes entrena con quien lleva veinte
       años sin que ninguno de los dos pierda la clase.</p>
    <p>Se practica descalzo sobre tatami. Lo que se aprende primero no son técnicas sino
       cómo caer, porque es lo que permite todo lo demás.</p>
    <p><a href="/clases/">La descripción completa del programa está en la página de clases</a>,
       junto con el judo, el iaijutsu y el karate que se imparten en Badalona.</p>
  </div>

  <h2>Preguntas frecuentes</h2>
  %(faq)s

  <h2>Ven a probar</h2>
  <div class="body">
    <p>Dos clases de prueba y la inscripción no cuesta nada. Escríbenos y te decimos qué
       día viene mejor.</p>
    <p class="cta"><a class="btn" href="/contacto/">Escríbenos</a>
       <a class="btn btn-2" href="/horarios/">Ver el horario</a>
       <small>Respondemos el mismo día.</small></p>
  </div>

  <h2>También entrenamos en</h2>
  %(rel)s
</div>
<div class="tail">Pie de página.</div>""" % dict(nav=NAV, ficha=ficha, vens=venue_cards(),
                                                faq=faq_html(), rel=RELATED)


# ===========================================================================
# B — la visita
# ===========================================================================
def page_b():
    steps = ''.join(
        '<div class="step"><b>%d</b><h3>%s</h3><p>%s</p></div>' % (i + 1, t, d)
        for i, (t, d) in enumerate(STEPS))

    return """
%(nav)s
<div class="hero" style="background-image:url('/images/index-8oGCaMDs-00-1200.webp')">
  <div class="hero-in">
    <p class="kick">Barcelona · Espronceda y Universitat</p>
    <h1>Aikido en Barcelona</h1>
    <p>Lunes y miércoles, en dos salas. Sin experiencia previa, sin competición
       y sin comprar nada para empezar.</p>
    <p class="cta"><a class="btn" href="/contacto/">Ven a probar</a>
       <a class="btn btn-2" href="#horario">Ver el horario</a>
       <small>Dos clases de prueba · inscripción gratuita</small></p>
  </div>
</div>
<div class="strip">
  <div><b>Lun · Mié</b><span>Dos días</span></div>
  <div><b>2 salas</b><span>Espronceda y UB</span></div>
  <div><b>Desde 12</b><span>Años</span></div>
  <div><b>35 €</b><span>Al mes</span></div>
</div>
<div class="wrap">
  <p class="crumb"><a href="/">Inicio</a> · <a href="/acceso/">Dónde entrenamos</a> · Barcelona</p>

  <h2>Tu primera clase, paso a paso</h2>
  <div class="steps">%(steps)s</div>

  <h2 id="horario">El horario en Barcelona</h2>
  %(tt)s
  <div class="body" style="margin-top:1rem">
    <p>Estas son las clases de Barcelona.
       <a href="/horarios/">El horario completo de las cuatro salas</a> incluye el dojo de
       Badalona, que abre de lunes a sábado.</p>
  </div>

  <h2>Dónde entrenamos</h2>
  %(vens)s

  <h2>Quién enseña</h2>
  <div class="body">
    <p><b>Daniil Mikhaylov</b>, 3.er dan Aikikai, lleva la clase de Espronceda.
       <b>Pablo Martín</b>, 4.º dan Aikikai y responsable del dojo, lleva la de la Facultad
       de Derecho. Los dos se formaron en Aikido Musubi y siguen la línea del
       Aikikai Hombu Dojo de Tokio.</p>
    <p><a href="/sobre-nosotros/la-asociacion/">Los nueve instructores de la asociación</a>.</p>
  </div>

  <h2>Preguntas frecuentes</h2>
  %(faq)s

  <h2>También entrenamos en</h2>
  %(rel)s

  <div class="body" style="margin-top:2.5rem">
    <p class="cta"><a class="btn" href="/contacto/">Escríbenos</a>
       <a class="btn btn-2" href="/cuotas/">Ver las cuotas</a>
       <small>Respondemos el mismo día.</small></p>
  </div>
</div>
<div class="tail">Pie de página.</div>""" % dict(nav=NAV, steps=steps, tt=timetable(),
                                                vens=venue_cards(), faq=faq_html(), rel=RELATED)


# ===========================================================================
# C — la visita, con la ficha
# ===========================================================================
def page_c():
    steps = ''.join(
        '<div class="step"><b>%d</b><h3>%s</h3><p>%s</p></div>' % (i + 1, t, d)
        for i, (t, d) in enumerate(STEPS))

    return """
%(nav)s
<div class="hero" style="background-image:url('/images/index-8oGCaMDs-00-1200.webp')">
  <div class="hero-in">
    <p class="kick">Barcelona &middot; Espronceda y Universitat</p>
    <h1>Aikido en Barcelona</h1>
    <p>Lunes y miércoles, en dos salas. Sin experiencia previa, sin competición
       y sin comprar nada para empezar.</p>
    <p class="cta"><a class="btn" href="/contacto/">Ven a probar</a>
       <a class="btn btn-2" href="#horario">Ver el horario</a>
       <small>Dos clases de prueba &middot; inscripción gratuita</small></p>
  </div>
</div>
<div class="auth">
  <div><b>2008</b><span>Entrenando desde</span></div>
  <div><b>8</b><span>Instructores titulados</span></div>
  <div><b>49</b><span>Cursos desde 2020</span></div>
  <div><b>Aikikai</b><span>Hombu Dojo, Tokio</span></div>
</div>
<div class="wrap">
  <p class="crumb"><a href="/">Inicio</a> &middot; <a href="/acceso/">Dónde entrenamos</a> &middot; Barcelona</p>
  %(ficha)s

  <h2>Tu primera clase, paso a paso</h2>
  <div class="steps">%(steps)s</div>

  <h2 id="horario">El horario en Barcelona</h2>
  %(tt)s
  <div class="body" style="margin-top:1rem">
    <p>Estas son las clases de Barcelona.
       <a href="/horarios/">El horario completo de las cuatro salas</a> incluye el dojo de
       Badalona, que abre de lunes a sábado.</p>
  </div>

  <h2>Dónde entrenamos</h2>
  %(vens)s

  <h2>Quién enseña</h2>
  <div class="body">
    <p><b>Daniil Mikhaylov</b>, 3.er dan Aikikai, lleva la clase de Espronceda.
       <b>Pablo Martín</b>, 4.º dan Aikikai y responsable del dojo, lleva la de la Facultad
       de Derecho. Los dos se formaron en Aikido Musubi y siguen la línea del
       Aikikai Hombu Dojo de Tokio.</p>
    <p><a href="/sobre-nosotros/la-asociacion/">Los ocho instructores de la asociación</a>.</p>
  </div>

  <h2>Preguntas frecuentes</h2>
  %(faq)s

  <h2>También entrenamos en</h2>
  %(rel)s

  <div class="body" style="margin-top:2.5rem">
    <p class="cta"><a class="btn" href="/contacto/">Escríbenos</a>
       <a class="btn btn-2" href="/cuotas/">Ver las cuotas</a>
       <small>Respondemos el mismo día.</small></p>
  </div>
</div>
<div class="tail">Pie de página.</div>""" % dict(nav=NAV, ficha=FICHA, steps=steps,
                                                tt=timetable(), vens=venue_cards(),
                                                faq=faq_html(), rel=RELATED)


# ---------------------------------------------------------------------------
WHY_SHARED = """
<h2>Lo que las dos comparten</h2>
<div class="two">
  <div>
    <p><b>Por qué no es una doorway page.</b> Google penaliza la página que existe sólo
       para capturar un término y devuelve al lector al mismo sitio de siempre. La prueba
       que hay que pasar es simple: <em>si Google no existiera, ¿valdría la pena tener
       esta página?</em> Aquí sí, porque hoy quien quiere entrenar en Barcelona no tiene
       dónde mirar el horario de Espronceda sin recorrer tres páginas.</p>
    <ul>
      <li>Todo dato es de estas dos salas: dirección, hora, profesor, cómo se entra, plano.</li>
      <li>Nada se copia de <code>/clases/</code> ni de <code>/cuotas/</code>: se enlaza.</li>
      <li>El FAQ responde «¿en qué se diferencia de Badalona?», que es la pregunta real.</li>
      <li>Dice que no hay clase infantil en Barcelona en vez de insinuar que sí.</li>
    </ul>
  </div>
  <div>
    <p><b>Enlaces internos: obligatorios.</b> Una página que sólo está en el sitemap se
       rastrea poco, posiciona mal y parece exactamente lo que no queremos que parezca.
       Estas tres se enlazan desde la tarjeta de cada espacio en la portada, desde
       <code>/acceso/</code>, desde <code>/horarios/</code> y entre ellas.</p>
    <p><b>Schema.org.</b> Cada página emite un <code>SportsClub</code> por sala con
       <code>address</code>, <code>geo</code> y <code>openingHoursSpecification</code>, más un
       <code>FAQPage</code> y un <code>BreadcrumbList</code>. Es la misma información que lee
       el humano, en la forma que leen la máquina y los buscadores generativos.</p>
    <p><b>URLs.</b> <code>/barcelona/</code>, <code>/badalona/</code>,
       <code>/sant-adria-de-besos/</code> — el topónimo completo, como en
       <code>_data/venues.yml</code>. Subcarpetas, nunca subdominios.</p>
  </div>
</div>"""

WHY_A = """
<h2>Enfoque A · la respuesta primero</h2>
<p>La página abre con una ficha de datos duros antes que con nada más. Está pensada para
   que un lector resuelva en cinco segundos si le sirve, y para que un buscador generativo
   pueda citarla entera sin interpretar nada: cada fila es una frase completa y autónoma.</p>
<ul>
  <li><b>A favor:</b> lo mejor para GEO/AEO. Es la forma que ChatGPT, Perplexity o AI
      Overviews pueden extraer literalmente. También la mejor para quien ya sabe lo que
      busca y sólo quiere el horario.</li>
  <li><b>A favor:</b> imposible que parezca publicidad. Parece una entrada de referencia,
      que es el registro de la asociación.</li>
  <li><b>En contra:</b> pide más al recién llegado. No hay foto grande ni promesa; hay
      datos. Convierte peor a quien todavía no sabe si el aikido le interesa.</li>
</ul>"""

WHY_B = """
<h2>Enfoque B · la visita</h2>
<p>Abre con la sala y una sola frase, y con el botón. Después cuenta qué pasa el primer día
   antes de dar ningún dato, porque la duda de quien no ha entrenado nunca no es el horario
   sino si va a hacer el ridículo.</p>
<ul>
  <li><b>A favor:</b> convierte mejor. El paso a paso responde el miedo real y la banda de
      cuatro cifras da los datos esenciales sin pedir que se lea nada.</li>
  <li><b>A favor:</b> la foto de la sala es la prueba de que el sitio existe.</li>
  <li><b>En contra:</b> peor para GEO. Los datos están repartidos por la página en vez de
      juntos, y una máquina que quiera citar «cuándo y dónde» tiene que recomponerlos.</li>
  <li><b>En contra:</b> se parece más a una landing, y eso hay que compensarlo con
      sustancia para que no lo parezca por dentro también.</li>
</ul>
<p><b>Se pueden combinar.</b> La ficha de A cabe en B justo debajo de la banda de cifras,
   y entonces B gana casi todo lo que le falta a cambio de una pantalla más de altura.</p>"""


WHY_C = """
<h2>Enfoque C &middot; la estructura de B con la ficha de A</h2>
<p>La sala y el botón primero, porque quien no ha entrenado nunca decide con la foto y no
   con la tabla. Después la ficha completa, para quien ya sabe lo que busca y para que un
   buscador generativo tenga los datos juntos y citables. Y sólo entonces el relato.</p>
<ul>
  <li><b>La banda oscura cambió de trabajo.</b> En B llevaba las cifras logísticas
      (Lun&middot;Mié, 2 salas, desde 12, 35 &euro;) y con la ficha debajo las repetía a
      trescientos píxeles de distancia. Ahora lleva las cifras de la asociación: 2008, ocho
      instructores, cuarenta y nueve cursos, Aikikai. No duplica nada y hace el trabajo que
      B no hacía: dar credibilidad antes de pedir nada.</li>
  <li><b>Es el único de los tres que sirve a los dos objetivos a la vez.</b> La banda habla
      al que compara dojos; la ficha, al que ya ha decidido y busca el horario; el paso a
      paso, al que nunca ha pisado un tatami.</li>
  <li><b>Cuesta una pantalla más de alto</b> que B antes de llegar al relato. Es el precio,
      y es el motivo por el que la ficha va después de la banda y no antes del botón.</li>
  <li><b>Las cuatro cifras tienen que ser verdad y verificables.</b> 2008 es la fundación,
      ocho son los instructores listados en <code>_data/about.yml</code>, cuarenta y nueve
      son los archivos de <code>_events/</code>, y la pertenencia a Aikikai está en el pie
      desde siempre. Si una cifra deja de ser cierta hay que cambiarla el mismo día: una
      cifra inflada en una página de localidad es exactamente el tipo de señal que convierte
      una página legítima en una sospechosa.</li>
</ul>"""


def build(name, title, kick, h1, lede, page, why):
    html = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<link rel="stylesheet" href="/styles/all.min.css">
<style>%s</style></head><body>
<div class="sheet">
  <header>
    <p class="kick">%s</p>
    <h1>%s</h1>
    <p>%s</p>
  </header>
  <div class="frame">%s</div>
</div>
<div class="why"><div class="why-in">%s%s</div></div>
</body></html>""" % (title, CSS, kick, h1, lede, page, why, WHY_SHARED)
    io.open(os.path.join(OUT, name), 'w', encoding='utf-8').write(html)
    print('  ->', name)


if __name__ == '__main__':
    build('loc-barcelona-a.html',
          'Barcelona · enfoque A — Aikido Musubi',
          'Página de localidad · propuesta A',
          'Barcelona &middot; la respuesta primero',
          'Ficha de datos arriba del todo, después las salas. Pensada para que la citen '
          'los buscadores generativos y para quien ya sabe lo que busca.',
          page_a(), WHY_A)
    build('loc-barcelona-b.html',
          'Barcelona · enfoque B — Aikido Musubi',
          'Página de localidad · propuesta B',
          'Barcelona &middot; la visita',
          'La sala, una frase y el botón. Después el primer día paso a paso, y luego los '
          'datos. Pensada para convertir a quien nunca ha entrenado.',
          page_b(), WHY_B)
    build('loc-barcelona-c.html',
          'Barcelona · enfoque C — Aikido Musubi',
          'Página de localidad · propuesta C · recomendada',
          'Barcelona &middot; la visita, con la ficha',
          'La estructura de B con el bloque de datos de A debajo de la banda. La banda pasa '
          'a llevar las cifras de la asociación para no repetir lo que dice la ficha.',
          page_c(), WHY_C)
    print('location mockups -> docs/mockups/loc-barcelona-{a,b,c}.html')
