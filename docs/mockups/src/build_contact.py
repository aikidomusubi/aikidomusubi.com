#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""/contacto/ — what to add, and nothing else.

WHAT IS ALREADY THERE AND STAYS. _includes/contact.html is better than the
word count suggests: three channel rows with WhatsApp leading, social pills
that are present without competing, a map, the address from venues.yml and a
directions button that knows about Apple Maps. None of that is touched.

WHAT IS MISSING. The page says HOW to reach the dojo and never says what
happens next, which is the only thing somebody hesitating actually wants. Five
facts answer it and every one came from the dojo:

    reply time    the same day
    languages     es / ca / en / ja
    who answers   the association
    walk-ins      you can just turn up, but writing first is better
    channels      the phone and WhatsApp are answered by a person

WHY IT MATTERS HERE RATHER THAN SOMEWHERE ELSE. Search Console, 90 days to
2026-09-10: /contacto/ at position 20.48 with 63 impressions and 0 clicks, and
/en/contact/ at 20.20 with 35 and 0. It is also the page every fee card's
button points at, and the page a parent asking about the suspended children's
group arrives on. It is the last step before somebody writes, and it currently
ends in a phone number with no reassurance attached.

WHY NO NAME. Juanma answers in practice and asked whether his name should be
on it. It should not: nothing else on this site carries a personal byline, the
association is the accurate answer, and a page that names a person has to be
edited the day somebody else takes over.

THE THREE LINKS AT THE FOOT are the other half of the same job. /acceso/
answers how to get there, /horarios/ when, /como-es-una-clase/ what happens on
the mat. They exist, they are good, and this page never points at them.

    python3 docs/mockups/src/build_contact.py
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, 'docs', 'mockups', 'contacto.html')

# Every line is the dojo's own answer, given 2026-09-13. Nothing is inferred.
ANSWERS = [
    ('Respondemos el mismo día',
     'Escribas por donde escribas. Si es fin de semana puede caer más tarde, '
     'pero no se queda para el lunes.'),
    ('En cuatro idiomas',
     'Puedes escribirnos en <b>español</b>, <b>català</b>, <b>English</b> o '
     '<b>日本語</b>. Contesta la asociación, no un formulario.'),
    ('El teléfono se coge',
     'El número es real y lo contestamos, igual que el WhatsApp. No es un '
     'buzón ni un desvío a nada.'),
    ('Puedes venir sin avisar',
     'Las clases están abiertas y nadie va a pedirte cita. Aun así, escribir '
     'antes es mejor: te decimos qué clase te encaja y te esperamos.'),
]

NEXT = [
    ('Cómo llegar', '/acceso/',
     'Las cuatro salas, con plano, puerta y transporte.'),
    ('Horarios', '/horarios/',
     'Qué hay cada día, en qué sala y con quién.'),
    ('Cómo es una clase', '/como-es-una-clase/',
     'La primera hora sobre el tatami, minuto a minuto.'),
]

CSS = """
:root{
  --Black:#111314; --Ink:#34454C; --White:#fff; --Paper:#faf9f7;
  --Yellow:#FFF200; --Green:#1a7444; --Line:rgba(17,19,20,.12);
}
*{box-sizing:border-box}
body{margin:0;background:var(--Paper);color:var(--Black);
     font:16px/1.55 "Noto Sans",system-ui,sans-serif}
.wrap{max-width:1140px;margin:0 auto;padding:2.5rem 2rem 5rem}
h1.pg{font:700 2.1rem/1.15 "Futura",system-ui,sans-serif;letter-spacing:.01em;
      margin:0 0 .6rem;text-transform:uppercase}
.top-lede{max-width:43rem;color:var(--Ink);margin:0 0 2.5rem}
.top-lede code{background:rgba(17,19,20,.06);padding:.1rem .3rem;border-radius:.2rem;
               font-size:.88em}
.note{border-left:3px solid var(--Yellow);background:rgba(255,242,0,.10);
      padding:.85rem 1.1rem;margin:0 0 2.5rem;max-width:43rem;font-size:.92rem}
.note b{font-weight:700}

.frame{background:var(--White);border:1px solid var(--Line);border-radius:.5rem;
       padding:2.5rem;margin:0 0 2rem}
.tag{display:inline-block;font:700 .68rem/1 "Noto Sans",sans-serif;
     letter-spacing:.13em;text-transform:uppercase;color:var(--Ink);
     margin:0 0 1.4rem;padding:.32rem .6rem;border:1px solid var(--Line);
     border-radius:.2rem}
.tag.new{color:#0d5c36;border-color:rgba(26,116,68,.35);background:rgba(26,116,68,.07)}

h2.pt{font:700 1.5rem/1.2 "Futura",system-ui,sans-serif;margin:0 0 .35rem;
      text-transform:uppercase;letter-spacing:.01em}
.sub{color:var(--Ink);margin:0 0 1.8rem;max-width:40rem;font-size:.95rem}

/* the new band */
.ct-when{display:grid;grid-template-columns:repeat(2,1fr);gap:1.6rem 2.4rem;
         border-top:2px solid var(--Black);padding-top:1.6rem}
.ct-when > div{}
.ct-when h3{font:700 1.02rem/1.3 "Noto Sans",sans-serif;margin:0 0 .3rem}
.ct-when p{margin:0;color:var(--Ink);font-size:.92rem;line-height:1.5}

/* existing, shown greyed so it is clear nothing changes */
.keep{border:1px dashed var(--Line);border-radius:.4rem;padding:1.4rem 1.6rem;
      background:rgba(17,19,20,.02);margin:1.8rem 0 0}
.keep .kl{font:700 .68rem/1 "Noto Sans",sans-serif;letter-spacing:.13em;
          text-transform:uppercase;color:#8a8f92;margin:0 0 .8rem}
.keep ul{margin:0;padding:0 0 0 1.1rem;color:#8a8f92;font-size:.9rem}
.keep li{margin:.2rem 0}

/* next steps */
.ct-next{display:grid;grid-template-columns:repeat(3,1fr);gap:1.2rem;
         border-top:2px solid var(--Black);padding-top:1.6rem;margin-top:2.2rem}
.ct-next a{display:block;text-decoration:none;color:inherit;
           border:1px solid var(--Line);border-radius:.4rem;padding:1.1rem 1.2rem;
           background:var(--White)}
.ct-next a:hover{border-color:var(--Black)}
.ct-next strong{display:block;font:700 1rem/1.25 "Noto Sans",sans-serif;
                margin:0 0 .25rem}
.ct-next strong::after{content:" →";color:var(--Green)}
.ct-next span{color:var(--Ink);font-size:.88rem;line-height:1.45}

.why{max-width:43rem;margin:2.5rem 0 0}
.why h2{font:700 1.1rem/1.2 "Futura",system-ui,sans-serif;margin:0 0 .6rem;
        text-transform:uppercase;letter-spacing:.02em}
.why p{color:var(--Ink);font-size:.93rem;margin:0 0 .7rem}
.why b{color:var(--Black)}

@media (max-width:760px){
  .wrap{padding:2rem 1.2rem 4rem}
  .frame{padding:1.5rem}
  .ct-when,.ct-next{grid-template-columns:1fr}
}
"""


def build():
    out = io.StringIO()
    out.write("""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Contacto — maqueta</title>
<style>""" + CSS + """</style></head><body><div class="wrap">
<h1 class="pg">Contacto</h1>
<p class="top-lede">Maqueta de lo que se <b>añade</b> a <code>/contacto/</code>.
Lo que ya existe —las tres vías de contacto, los perfiles sociales, el mapa, la
dirección y el botón de cómo llegar— no se toca y se muestra en gris para que
quede claro.</p>

<div class="note"><b>Por qué.</b> La página dice cómo contactar y no dice qué
pasa después, que es lo único que quiere saber quien está dudando. Está en la
posición 20,5 con 98 impresiones y <b>cero clics</b> entre español e inglés, es
la página a la que apuntan todos los botones de <code>/cuotas/</code>, y es
donde aterriza quien pregunta por el grupo infantil.</div>

<div class="frame">
  <span class="tag new">Nuevo · va justo debajo del título</span>
  <h2 class="pt">Cuando escribes</h2>
  <p class="sub">Las cinco respuestas que diste, tal cual. Nada aquí está
  inventado ni redondeado.</p>
  <div class="ct-when">""")

    for h, p in ANSWERS:
        out.write(f'\n    <div><h3>{h}</h3><p>{p}</p></div>')

    out.write("""
  </div>

  <div class="keep">
    <p class="kl">Debajo, sin cambios</p>
    <ul>
      <li>WhatsApp · la vía más rápida — +34 717 171 177</li>
      <li>Email — info@aikidomusubi.com</li>
      <li>Teléfono — +34 717 171 177</li>
      <li>Instagram · Facebook · YouTube</li>
      <li>Mapa, dirección de Badalona y botón «Cómo llegar»</li>
    </ul>
  </div>

  <div class="ct-next">""")

    for t, u, d in NEXT:
        out.write(f'\n    <a href="{u}"><strong>{t}</strong><span>{d}</span></a>')

    out.write("""
  </div>
</div>

<div class="why">
  <h2>Tres decisiones que conviene que veas</h2>
  <p><b>No lleva tu nombre.</b> Preguntaste si hacía falta. No: en todo el sitio
  no hay ni una firma personal, «la asociación» es la respuesta exacta, y una
  página que nombra a alguien hay que editarla el día que conteste otra
  persona.</p>
  <p><b>«Puedes venir sin avisar» va entero, con el matiz.</b> Dijiste que se
  puede, pero que es mejor escribir antes. Poner solo la primera mitad haría la
  página más comercial y menos cierta; poner solo la segunda pondría una puerta
  donde no la hay.</p>
  <p><b>Los tres enlaces del final no son relleno.</b> <code>/acceso/</code>,
  <code>/horarios/</code> y <code>/como-es-una-clase/</code> responden las tres
  preguntas siguientes y esta página no apunta hoy a ninguna. Son además enlaces
  contextuales desde una página que Google ya rastrea.</p>
</div>

</div></body></html>""")

    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write(out.getvalue())
    print(f'→ {os.path.relpath(OUT, ROOT)}')


if __name__ == '__main__':
    build()
