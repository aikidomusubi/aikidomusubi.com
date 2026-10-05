#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Three proposals for a page per venue, drawn for CxEM Espronceda.

THE RISK THE BRIEF NAMES, AND HOW EACH PROPOSAL MEETS IT. /barcelona/ already
covers Espronceda, and /sant-adria-de-besos/ is nothing but Marina-Besòs. A
venue page that repeats its town page is two URLs with one answer, which is
the duplicate and the doorway Google acts on. So the venue page has to carry
what only the venue has, and the town page has to step back to being the
town's hub:

  venue page   the room: its own fee and the sports-centre member fee, its
               photographs, the way in from the street, its one class and its
               one teacher, the questions people ask about that building
  town page    which rooms there are in that town, a card for each linking
               down, and the questions about the town

The three proposals share every component with the location pages: the hero,
the figures strip, `.lo-sec`, `.lo-facts`, `.lo-tt`, `.ab-faq`. What differs is
the order and what leads.

The page shell (nav, footer, scripts) is lifted from the BUILT /barcelona/
page, so the mockup is the real thing around the new middle. Build first:

    npx gulp build && python3 docs/mockups/src/build_venuepage.py
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import build_venuephotos as VP  # the photo layouts and their CSS

SRC = os.path.join(ROOT, '_site', 'barcelona', 'index.html')
OUT = os.path.join(ROOT, 'docs', 'mockups', 'venue-espronceda-{}.html')
fig = VP.fig

# ---------------------------------------------------------------------------
# copy, in Spanish
# ---------------------------------------------------------------------------
PENDING = '<mark class="tbc">por confirmar</mark>'

def hero(img_html, figs):
    return f'''<div class="lo-hero">{img_html}
    <div class="lo-hero-in">
      <p class="lo-kick">Barcelona · Complejo Deportivo Municipal Espronceda</p>
      <h1>Aikido en el CxEM Espronceda</h1>
      <p class="lo-line">Lunes y miércoles de 20:00 a 21:00, en la sala de tatami del complejo deportivo. Sin experiencia previa y sin competición.</p>
      <p class="lo-cta">
        <a class="lo-btn" href="/contacto/">Ven a probar</a>
        <a class="lo-btn lo-btn-2" href="#esp-horario">Ver el horario</a>
        <small>Dos clases de prueba · inscripción gratuita</small>
      </p>
    </div>
  </div>{figs}'''

MAP = '''<picture>
      <source type="image/webp" sizes="100vw" srcset="/images/barcelona-Nq8pL3xB-map-slate-lit-1200.webp 1200w, /images/barcelona-Nq8pL3xB-map-slate-lit-1920.webp 1920w">
      <img src="/images/barcelona-Nq8pL3xB-map-slate-lit-1200.jpg" alt="" width="1200" height="900" fetchpriority="high" decoding="sync">
    </picture>'''

PHOTO = f'<picture class="hero-photo"><img src="{VP.IMG}E04.jpg" alt="" width="1500" height="1000" fetchpriority="high" style="object-position: 62% 40%"></picture>'

FIGS_STD = '''<div class="lo-figs">
    <div><b>2008</b><span>Entrenando desde</span></div>
    <div><b>9</b><span>Instructores titulados</span></div>
    <div><b>50</b><span>Cursos desde 2020</span></div>
    <div><b>Aikikai</b><span>Hombu Dojo, Tokio</span></div>
  </div>'''

# The venue's own figures: what somebody deciding whether to come needs, and
# the four things this page has that /barcelona/ does not.
FIGS_VENUE = '''<div class="lo-figs">
    <div><b>Lun · Mié</b><span>Días de clase</span></div>
    <div><b>20:00</b><span>Hasta las 21:00</span></div>
    <div><b>39 €</b><span>Cuota general al mes</span></div>
    <div><b>19 €</b><span>Abonados del CxEM</span></div>
  </div>'''

CRUMB = '''<p class="lo-crumb">
    <a href="/">Inicio</a> <span aria-hidden="true">·</span>
    <a href="/barcelona/">Aikido en Barcelona</a> <span aria-hidden="true">·</span> CxEM Espronceda
  </p>'''

def sec(lab, h, inner, sid='', n=''):
    num = f'<span class="vj-n">{n}</span>' if n else ''
    i = f' id="{sid}"' if sid else ''
    return f'<section class="lo-sec"{i}><p class="lo-lab">{num}{lab}</p><h2>{h}</h2>{inner}</section>'

FACTS = '''<dl class="lo-facts">
      <dt>Dónde</dt><dd><b>CxEM Espronceda</b>, C/ Espronceda, 326, 08027 Barcelona. En la sala de tatami del complejo.</dd>
      <dt>Cuándo</dt><dd>Lunes y miércoles, de 20:00 a 21:00.</dd>
      <dt>Para quién</dt><dd>Adultos y jóvenes desde 12 años, con o sin experiencia previa.</dd>
      <dt>Cuánto</dt><dd>39 € al mes, o 19 € si eres abonado del CxEM Espronceda. Inscripción gratuita y dos clases de prueba.</dd>
      <dt>Qué llevar</dt><dd>Ropa cómoda de manga y pantalón largos. El keikogi no hace falta para empezar.</dd>
      <dt>Quién enseña</dt><dd>Daniil Mikhaylov (3.er dan).</dd>
      <dt>Quién lo organiza</dt><dd>Aikido Musubi, asociación cultural sin ánimo de lucro fundada en 2008. Formamos parte de Aikido Arashi Group, reconocido por la Aikikai Foundation (Hombu Dojo, Tokio).</dd>
    </dl>'''

FEES = f'''<div class="vf">
      <div class="vf-card">
        <p class="vf-k">Cuota general</p>
        <dl><dt>Adultos</dt><dd>39 €<small>al mes</small></dd>
            <dt>Menores de 12 años</dt><dd>29 €<small>al mes</small></dd></dl>
      </div>
      <div class="vf-card vf-m">
        <p class="vf-k">Cuota para abonados del CxEM Espronceda</p>
        <dl><dt>Adultos</dt><dd>19 €<small>al mes</small></dd>
            <dt>Menores de 12 años</dt><dd>9 €<small>al mes</small></dd></dl>
      </div>
    </div>
    <ul class="vf-notes">
      <li><b>Abonados:</b> la cuota reducida es para quien ya tiene el abono del Complejo Deportivo Municipal Espronceda; basta con enseñarlo al apuntarse.</li>
      <li><b>Sin coste:</b> la inscripción y las dos clases de prueba.</li>
      <li><b>Aparte:</b> la licencia federativa y el seguro deportivo, {PENDING} si pasan a estar incluidos.</li>
      <li><b>Acceso a otros espacios:</b> {PENDING}.</li>
    </ul>'''

TT = '''<table class="lo-tt">
      <thead><tr><th>Cuándo</th><th>Nivel</th><th>Quién</th></tr></thead>
      <tbody><tr><td><small>Lun · Mié</small>20:00–21:00</td><td>Aikido · Todos los niveles</td>
      <td>Daniil Mikhaylov<small>3.er dan</small></td></tr></tbody>
    </table>
    <p class="lo-note"><a class="lo-more" href="/horarios/?location=cxem-espronceda">Esta clase en el horario completo</a></p>'''

STEPS = '''<div class="lo-steps">
      <div class="lo-step"><p class="n">01</p><h3>Escríbenos</h3><p>Un correo o un WhatsApp. Te decimos qué día viene mejor y quién te va a recibir.</p></div>
      <div class="lo-step"><p class="n">02</p><h3>Ven quince minutos antes</h3><p>La sala está dentro del complejo: entra por la calle de Espronceda y pregunta por la sala de tatami.</p></div>
      <div class="lo-step"><p class="n">03</p><h3>Ropa cómoda y nada más</h3><p>Manga larga, pantalón largo y pies descalzos. Una hora, y nadie te va a poner a prueba el primer día.</p></div>
    </div>'''

def arrive(with_photo=True):
    ph = fig('E05', 'El pasillo que lleva a la sala', 'arr-ph') if with_photo else ''
    return f'''<div class="arr">
      <div class="arr-txt">
        <p><b>Complejo Deportivo Municipal Espronceda</b><br>C/ Espronceda, 326 · 08027 Barcelona</p>
        <p><b>Cómo se entra:</b> por la entrada principal de la calle de Espronceda. La sala de tatami está dentro del complejo; la primera vez, ven con tiempo.</p>
        <p class="lo-cta arr-maps"><a class="lo-btn lo-btn-2" href="https://maps.app.goo.gl/xE1cHD7zRygTG78z9">Google Maps</a>
           <a class="lo-btn lo-btn-2" href="https://maps.apple/p/czWeasADhbQc~p">Apple Maps</a></p>
        <p class="lo-note"><a class="lo-more" href="/acceso/#cxem-espronceda">El plano con la entrada marcada</a></p>
      </div>
      {ph}
    </div>'''

WHO = '''<div class="lo-prose"><p><b>Daniil Mikhaylov</b>, 3.er dan Aikikai, lleva la clase del CxEM Espronceda. Se formó en Aikido Musubi y sigue la línea del Aikikai Hombu Dojo de Tokio, con el mismo programa y los mismos exámenes que el dojo de Badalona.</p>
      <p class="lo-note"><a class="lo-more" href="/sobre-nosotros/la-asociacion/">Los instructores de la asociación</a></p></div>'''

def faq(items):
    return '<div class="ab-faq">' + ''.join(
        f'<details name="esp-faq"><summary>{q}</summary><div class="a"><p>{a}</p></div></details>' for q, a in items) + '</div>'

FAQ = faq([
    ('¿Tengo que ser abonado del CxEM Espronceda?',
     'No. Cualquiera puede apuntarse con la cuota general. Si ya tienes el abono del complejo, pagas la cuota de abonados.'),
    ('¿Cómo encuentro la sala?',
     'Entra por la entrada principal de la calle de Espronceda y pregunta por la sala de tatami. Arriba tienes una foto del pasillo que lleva a ella y, en la página de acceso, el plano con la entrada marcada.'),
    ('¿En qué se diferencia de la clase de la Universidad de Barcelona?',
     'La de la UB es la clase de principiantes, a las 19:00 y con Pablo Martín. La del CxEM Espronceda es para todos los niveles, a las 20:00 y con Daniil Mikhaylov. Mismo programa y mismos exámenes.'),
    ('¿Puedo entrenar también en Badalona o en la UB?',
     f'Sí, puedes venir a probar a cualquiera de los espacios. Si la cuota da acceso a todos ellos está {PENDING}.'),
    ('¿Necesito experiencia previa?',
     'No. Quien empieza entrena junto a quien lleva años, y en aikido no hay competición.'),
])

ALSO = '''<div class="also">
      <a class="also-c" href="/barcelona/"><b>Aikido en Barcelona</b><span>Los dos espacios de la ciudad, con su horario conjunto.</span></a>
      <a class="also-c" href="/acceso/#university-of-barcelona"><b>Facultad de Derecho de la UB</b><span>Principiantes, lunes y miércoles a las 19:00.</span></a>
      <a class="also-c" href="/badalona/"><b>El dojo de Badalona</b><span>Clases de lunes a sábado, de mañana y de tarde.</span></a>
    </div>'''
END = '''<p class="lo-cta lo-end"><a class="lo-btn" href="/contacto/">Ven a probar</a>
      <a class="lo-btn lo-btn-2" href="/cuotas/">Todas las cuotas</a></p>'''

# ---------------------------------------------------------------------------
# the three proposals
# ---------------------------------------------------------------------------
def prop_a():
    return (hero(MAP, FIGS_STD) + CRUMB
            + sec('Lo esencial', 'Lo esencial', FACTS)
            + sec('Cuotas', 'Lo que cuesta, sin letra pequeña', FEES)
            + sec('Cómo empezar', 'Tu primera clase, paso a paso', STEPS)
            + sec('Horario', 'Las clases en el CxEM Espronceda', TT, 'esp-horario')
            + sec('El espacio por dentro', 'CxEM Espronceda, por dentro', VP.mosaic_b())
            + sec('Cómo llegar', 'Cómo llegar y cómo entrar', arrive(False))
            + sec('Quién enseña', 'El instructor', WHO)
            + sec('Dudas', 'Preguntas sobre este espacio', FAQ)
            + sec('Y también', 'Más cerca de ti', ALSO) + END)

def prop_b():
    return (hero(PHOTO, FIGS_VENUE) + CRUMB
            + sec('El espacio por dentro', 'Así es una clase en el CxEM Espronceda', VP.strip_b())
            + sec('Lo esencial', 'Lo esencial y lo que cuesta',
                  f'<div class="two">{FACTS}<div>{FEES}</div></div>')
            + sec('Horario', 'Lunes y miércoles a las 20:00', TT, 'esp-horario')
            + sec('Cómo llegar', 'Cómo llegar y cómo entrar', arrive(True))
            + sec('Quién enseña', 'El instructor', WHO)
            + sec('Dudas', 'Preguntas sobre este espacio', FAQ)
            + sec('Y también', 'Más cerca de ti', ALSO) + END)

def prop_c():
    return (hero(MAP, FIGS_VENUE) + CRUMB
            + sec('Antes de venir', 'Lo esencial y lo que cuesta', FACTS + FEES, n='01')
            + sec('Llegar', 'Cómo llegar y cómo entrar', arrive(True), n='02')
            + sec('La sala', 'CxEM Espronceda, por dentro', VP.dip_b(), n='03')
            + sec('La clase', 'Lunes y miércoles a las 20:00',
                  TT + f'<div class="gap">{STEPS}</div><div class="gap">{WHO}</div>', 'esp-horario', n='04')
            + sec('Dudas', 'Preguntas sobre este espacio', FAQ, n='05')
            + sec('Y también', 'Más cerca de ti', ALSO) + END)

PROPS = [
    ('a', 'A · Twin', prop_a, False,
     'The town page with the town taken out: the same sections in the same order, the map hero and the association figures, plus the fees and the photographs. The safest choice, and the closest to /barcelona/, which is also its weakness for search.'),
    ('b', 'B · Photo first', prop_b, False,
     'The photograph of the room is the hero, the strip follows straight after, and the facts sit beside the fees. The venue figures replace the association ones. Most attractive on a phone; leans hardest on photographs that are still two people in a large room.'),
    ('c', 'C · Arrival guide', prop_c, True,
     'Ordered as the visit happens: before you come, getting there, the room, the class, questions. The numbers are a real sequence. It is the least like /barcelona/ in structure as well as in content, which is what keeps the two pages from competing, and it answers the questions a first visit actually raises.'),
]

CSS = VP.CSS.replace('html, body { background: #fff; height: auto; min-height: 100%; }', '') + r'''
/* the photo grade, B, fixed: on the page there is no switch */
body figure.vp img { filter: saturate(.68) sepia(.18) contrast(1.08) brightness(1.03); }
.page main figure.vp img { height: 100%; }
.page main .lo-hero .hero-photo img { filter: saturate(.68) sepia(.18) contrast(1.08) brightness(1.03); object-fit: cover; }
.gap { margin-top: 2.6rem; }
.vj-n { display: inline-block; min-width: 2.2em; color: #ae5224; font-variant-numeric: tabular-nums; }
mark.tbc { background: #FFF200; color: #111314; padding: 0 .3em; font-size: .85em; letter-spacing: .02em; }

.vf { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1.4rem; }
.vf-card { border: 1px solid rgba(17,19,20,.16); padding: 1.2rem 1.4rem; }
.vf-m { background: #111314; color: #fff; border-color: #111314; }
.page main .vf-k { font: 500 .74rem/1.3 Futura, sans-serif; letter-spacing: .14em; text-transform: uppercase; margin: 0 0 .9rem; max-width: none; color: inherit; }
.vf-m .vf-k { color: #FFF200 !important; }
.page main .vf dl { display: grid; grid-template-columns: 1fr auto; gap: .5rem 1rem; margin: 0; max-width: none; align-items: baseline; }
.page main .vf dt { font-weight: 400; }
.page main .vf dd { margin: 0; font: 500 1.9rem/1 Futura, sans-serif; text-align: right; font-variant-numeric: tabular-nums; }
.page main .vf dd small { display: block; font: 400 .72rem/1.3 'Noto Sans', sans-serif; opacity: .7; letter-spacing: 0; }
.page main ul.vf-notes { margin: 1.2rem 0 0; padding-left: 1.1rem; max-width: none; font-size: .95rem; }
@media (max-width: 767px) { .vf { grid-template-columns: 1fr; } }

.two { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start; }
.two .vf { grid-template-columns: 1fr; margin-top: 0; }
@media (max-width: 991px) { .two { grid-template-columns: 1fr; } }

.arr { display: grid; grid-template-columns: 1fr 18rem; gap: 2rem; align-items: start; }
.page main .arr-txt p { max-width: none; margin: 0 0 1rem; }
.arr-maps { gap: .6rem; }
figure.arr-ph { aspect-ratio: 3 / 4; }
@media (max-width: 767px) { .arr { grid-template-columns: 1fr; } figure.arr-ph { aspect-ratio: 4 / 3; } }

.also { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.page main a.also-c { display: block; border: 1px solid rgba(17,19,20,.16); padding: 1rem 1.2rem; text-decoration: none; color: #111314; }
.page main a.also-c b { display: block; font-family: Futura, sans-serif; font-weight: 500; margin-bottom: .3rem; }
.page main a.also-c span { font-size: .92rem; color: #34454C; }
.page main a.also-c:hover b { text-decoration: underline; }
@media (max-width: 767px) { .also { grid-template-columns: 1fr; } }

/* the mockup's own furniture, outside the page */
.mk-dock { position: fixed; right: 1rem; bottom: 3rem; z-index: 2000; width: 21rem; max-width: calc(100vw - 2rem);
           background: #fff; border: 2px solid #111314; padding: .9rem 1rem; font: 400 .85rem/1.45 'Noto Sans', sans-serif;
           color: #111314; box-shadow: 0 8px 30px rgba(17,19,20,.25); }
.mk-dock b.t { font-family: Futura, sans-serif; font-weight: 500; letter-spacing: .1em; text-transform: uppercase; font-size: .72rem; }
.mk-dock nav { display: flex; gap: .4rem; margin: .5rem 0; }
.mk-dock nav a { flex: 1; text-align: center; border: 1.5px solid #111314; padding: .35rem 0; color: #111314; text-decoration: none; font: 500 .8rem/1 Futura, sans-serif; }
.mk-dock nav a[aria-current] { background: #111314; color: #FFF200; }
.mk-dock .rec { color: #1A7444; font-weight: 700; }
.mk-dock details { margin-top: .4rem; }
.mk-dock summary { cursor: pointer; font-weight: 700; }
.mk-dock ul { padding-left: 1rem; margin: .4rem 0 0; }
.mk-dock .x { position: absolute; top: .3rem; right: .5rem; border: 0; background: none; font-size: 1.1rem; cursor: pointer; }
'''

SEO = '''<details><summary>Search: what the page carries</summary><ul>
<li><b>URL</b> <code>/barcelona/cxem-espronceda/</code> (and <code>/sant-adria-de-besos/marina-besos/</code>): under its town, so the breadcrumb, the hierarchy and the internal links all say "this room is in this town".</li>
<li><b>Title</b> Aikido en el CxEM Espronceda, Barcelona<br><b>Description</b> Aikido para adultos los lunes y miércoles de 20:00 a 21:00 en el Complejo Deportivo Municipal Espronceda, Barcelona. 39 € al mes, 19 € para abonados. Dos clases de prueba.</li>
<li><b>Structured data</b> a <code>SportsActivityLocation</code> for the room, <code>containedInPlace</code> the municipal complex, <code>parentOrganization</code> the club, with address, geo, its opening hours, <code>photo</code> as ImageObjects with credit and licence; a three-level BreadcrumbList; FAQPage for the venue questions only.</li>
<li><b>Not duplicated</b> /barcelona/ keeps the town and gets a card per room linking down; the venue questions live here and not there; the fees and photographs live here.</li>
<li><b>Linked from</b> the town page, /acceso/, the timetable's location filter, the footer's "Dónde entrenamos" column and the home page's venue cards, so it is never an orphan.</li>
</ul></details>'''

def main():
    if not os.path.exists(SRC):
        sys.exit('build the site first: npx gulp build')
    page = open(SRC, encoding='utf-8').read()
    a = page.index('<main'); a = page.index('>', a) + 1
    b = page.index('</main>')
    head, tail = page[:a], page[b:]
    head = re.sub(r'<title>[^<]*</title>', '<title>Mockup · CxEM Espronceda</title>', head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
    tail = re.sub(r'<script type="application/ld\+json">.*?</script>', '', tail, flags=re.S)
    head = head.replace('</head>', f'<style>{CSS}</style></head>')
    for key, name, fn, rec, why in PROPS:
        nav = ''.join(f'<a href="venue-espronceda-{k}.html"{" aria-current=\"page\"" if k == key else ""}>{k.upper()}</a>' for k, *_ in PROPS)
        dock = (f'<aside class="mk-dock" id="mkdock"><button class="x" type="button" aria-label="Hide" '
                f'onclick="this.parentNode.hidden=true">×</button><b class="t">Mockup · venue page</b>'
                f'<nav>{nav}</nav><p><b>{name}</b>{" <span class=rec>· recommended</span>" if rec else ""}</p>'
                f'<p>{why}</p><p>Fees in <mark class="tbc">yellow</mark> are waiting on a decision.</p>{SEO}</aside>')
        html = head + prop_fn_wrap(fn()) + tail.replace('</body>', dock + '</body>')
        with open(OUT.format(key), 'w', encoding='utf-8') as fh:
            fh.write(html)
        print('wrote', os.path.relpath(OUT.format(key), ROOT))

def prop_fn_wrap(s):
    return s

if __name__ == '__main__':
    main()
