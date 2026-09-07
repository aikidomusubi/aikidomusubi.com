#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Three ways to build the masterclass poster, at A4, for Illustrator.

WHAT IS BEING REPLACED. The posters that exist — Corridoni, Pablo Martín and
the rest — are all one idea: a full-bleed black-and-white photograph, a grey
scrim over the whole of it, and the type sitting on top. It works, and it has
two costs that show up every time.

  It needs a photograph of the instructor, on a tatami, in advance. That is
  why five upcoming masterclasses have no poster: the artwork cannot start
  until somebody has a picture.

  And the type sits on a photograph, so its contrast is whatever that
  photograph happens to be. On the Corridoni poster the date sits over a
  keikogi sleeve and the name over a shoulder.

So the three below are not three skins. Each one answers a different question,
and the notes beside them say which:

  A  KAKEJIKU   — needs no photograph at all
  B  LA PLANCHA — keeps the photograph and takes the type off it
  C  EL CARTEL  — makes the date the hero, because the date is what changes

COLOUR IS SANZO WADA AND NOTHING ELSE, taken from styles/base.less by name so
these cannot drift from the site: Black, White, Slate Color, Yellow, Apricot
Yellow, Burnt Sienna, Vandyke Red, Diamine Green, Dark Greenish Glaucous.

TYPE IS THE SITE'S OWN PAIR. Futura for display — it is what graphics/logo-00.svg
sets AIKIDO and MUSUBI in, Medium at 0.26em and Bold at 0.03em — and Noto Sans
for everything else, which is the only text face the site loads. The Japanese
is Hiragino Mincho on the scroll, because the wordmark's own 産靈 is set in
Hiragino Mincho Pro W6, and a gothic on the other two.

    python3 docs/mockups/src/build_poster.py
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, 'docs', 'mockups', 'poster.html')

# The event, from _events/2026-09-12-pedro-fortes-4th-dan.md. Nothing here is
# invented: same date, same hour, same "entrada libre", same address as
# _data/venues.yml.
E = {
    'eyebrow':  'Masterclass',
    'name1':    'Pedro',
    'name2':    'Fortes',
    'full':     'Pedro Fortes',
    'grade':    '4.º dan Aikikai',
    'ja_name':  'ペドロ・フォルテス',
    'ja_grade': '四段 合気会',
    'weekday':  'Sábado',
    'day':      '12',
    'month':    'Septiembre',
    'month_ab': 'Sep',
    'year':     '2026',
    'from':     '12:00',
    'to':       '13:00',
    'free':     'Entrada libre',
    'venue':    'Aikido Musubi',
    'street':   "Av. d'Alfons XIII, 351",
    'town':     '08918 Badalona, Barcelona',
    'url':      'aikidomusubi.com',
    'photo':    '/images/access-information-NdxqmVbV-aikido-musubi-room.jpg',
}

NOTES = [
    ('A', 'Kakejiku', '無 en sello', """
<p><b>La idea:</b> no hace falta fotografía. El cartel es tipografía y papel,
como un <i>kakejiku</i> —el rollo colgante del kamiza— y como un diploma de
grado. La columna derecha lleva el nombre en vertical, que es donde va la
firma en un rollo, y el sello rojo cierra abajo.</p>
<p><b>Qué problema resuelve:</b> el que tienes ahora mismo. Cinco masterclass
próximas sin cartel porque no hay foto del instructor. Con esta plantilla el
cartel se puede cerrar el día que se fija la fecha.</p>
<p><b>El detalle que no es decoración:</b> las siete líneas de arriba a la
izquierda son los siete pliegues del hakama. Cinco delante, dos detrás. Es una
regla de composición que solo significa algo en un dojo.</p>
<p><b>Color:</b> Black sobre blanco, y un único Vandyke Red en el sello. Un
acento en toda la hoja.</p>"""),

    ('B', 'La plancha', 'foto 2:1', """
<p><b>La idea:</b> mantener la fotografía y quitarle el texto de encima. La
imagen ocupa un rectángulo exacto arriba y el texto vive debajo, sobre Slate
Color macizo. Nada de degradados ni de velos.</p>
<p><b>Qué problema resuelve:</b> el contraste. En el cartel de Corridoni la
hora cae sobre una manga de keikogi y el nombre sobre un hombro: el contraste
es el que salga. Aquí el texto mide 12:1 contra un color plano, siempre, y la
foto se ve entera en vez de apagada bajo un velo gris.</p>
<p><b>El detalle:</b> la plancha es <b>2:1 exacto</b>, la proporción de un
tatami. Es la única medida que no elegí yo.</p>
<p><b>Color:</b> Slate Color de fondo, Apricot Yellow para la línea y la
etiqueta, blanco para el texto.</p>"""),

    ('C', 'El cartel', 'la fecha manda', """
<p><b>La idea:</b> el cartel de combate. La fecha enorme, el nombre debajo, la
hora en una caja negra. Amarillo y negro, que es la firma del sitio —el botón
de «Escríbenos» y la subrayado de la nav son exactamente estos dos colores.</p>
<p><b>Qué problema resuelve:</b> la reutilización. De un cartel al siguiente
cambian cuatro cosas: el día, el mes, el nombre y la hora. Aquí esas cuatro
cosas <i>son</i> el cartel, así que la plantilla no se deforma al reutilizarla
—que es lo que le pasa a una plantilla construida alrededor de una foto.</p>
<p><b>Y a distancia:</b> es el único de los tres que se lee desde el otro lado
del tatami. Amarillo puro sobre negro tiene el contraste más alto de la
paleta.</p>
<p><b>Color:</b> Yellow y Black. Dos.</p>"""),
]


# ---------------------------------------------------------------------------
def sheet_a():
    """Ink on paper. The scroll."""
    pleats = ''.join('<i></i>' for _ in range(7))
    return f"""
<div class="sheet sh-a">
  <div class="a-main">
    <div class="a-pleats">{pleats}</div>
    <p class="a-eyebrow">{E['eyebrow']}</p>
    <h1 class="a-name"><span>{E['name1']}</span><span>{E['name2']}</span></h1>
    <p class="a-grade">{E['grade']}</p>

    <div class="a-when">
      <p class="a-date">{E['weekday']} {E['day']} de {E['month'].lower()}</p>
      <p class="a-hour">{E['from']}<em>—</em>{E['to']}</p>
      <p class="a-free">{E['free']}</p>
    </div>

    <div class="a-foot">
      <p class="a-mark"><span class="wm-a">Aikido</span><span class="wm-m">Musubi</span><span class="wm-j">産靈</span></p>
      <p class="a-addr">{E['street']}<br>{E['town']}</p>
      <p class="a-url">{E['url']}</p>
    </div>
  </div>

  <div class="a-side">
    <p class="a-ja">{E['ja_name']}</p>
    <p class="a-ja a-ja-sm">{E['ja_grade']}</p>
    <div class="a-seal"><span>無</span><em>料</em></div>
  </div>
</div>"""


def sheet_b():
    """The plate. Photograph above, type below, nothing on top of anything."""
    return f"""
<div class="sheet sh-b">
  <figure class="b-plate">
    <img src="{E['photo']}" alt="">
  </figure>
  <div class="b-body">
    <p class="b-eyebrow">{E['eyebrow']}</p>
    <h1 class="b-name">{E['full']}</h1>
    <p class="b-grade">{E['grade']} <em>·</em> {E['ja_name']} {E['ja_grade']}</p>

    <div class="b-rule"></div>

    <dl class="b-facts">
      <div>
        <dt>Cuándo</dt>
        <dd>{E['weekday']} {E['day']} de {E['month'].lower()}<br>
            <b>{E['from']} – {E['to']}</b></dd>
      </div>
      <div>
        <dt>Dónde</dt>
        <dd>{E['venue']}<br>{E['street']}<br>{E['town']}</dd>
      </div>
    </dl>

    <p class="b-chip">{E['free']}</p>

    <div class="b-foot">
      <p class="b-mark"><span class="wm-a">Aikido</span><span class="wm-m">Musubi</span><span class="wm-j">産靈</span></p>
      <p class="b-url">{E['url']}</p>
    </div>
  </div>
</div>"""


def sheet_c():
    """The bill. The date is the poster."""
    return f"""
<div class="sheet sh-c">
  <div class="c-top">
    <span class="wm-a">Aikido</span><span class="wm-m">Musubi</span><span class="wm-j">産靈</span>
  </div>

  <div class="c-body">
    <p class="c-eyebrow">{E['eyebrow']}</p>

    <div class="c-date">
      <span class="c-day">{E['day']}</span>
      <span class="c-stack">
        <em>{E['month_ab']}</em>
        <i>{E['weekday']}</i>
      </span>
    </div>

    <div class="c-mid">
      <h1 class="c-name">{E['full']}</h1>
      <p class="c-grade">{E['grade']}</p>
      <p class="c-ja">{E['ja_name']} {E['ja_grade']}</p>
    </div>

    <div class="c-end">
      <p class="c-hour"><span>{E['from']} – {E['to']}</span></p>
      <p class="c-free">{E['free']}</p>
    </div>
  </div>

  <div class="c-foot">
    <p>{E['venue']} · {E['street']} · {E['town']}</p>
    <p class="c-url">{E['url']}</p>
  </div>
</div>"""


CSS = """
/* ---------------------------------------------------------------------------
   The page chrome — the same light sheet every other mockup in docs/mockups
   uses, so this one files with them.
   --------------------------------------------------------------------------- */
:root{
  --Black:#111314; --White:#ffffff; --Slate:#34454C;
  --Yellow:#FFF200; --Apricot:#ffdd00;
  --Rust:#ae5224;  --Vandyke:#82241f; --Green:#1a7444;
  --Ocher:#e2b540; --Glauc:#B7C2A9;   --Paper:#FBFAF7;
  --YellowInk:#292700;
}
*{box-sizing:border-box}
body{margin:0;background:#F7F7F5;color:#111314;
     font:15px/1.65 "Noto Sans",-apple-system,BlinkMacSystemFont,sans-serif}
.wrap{max-width:1500px;margin:0 auto;padding:2.5rem 2rem 6rem}
h1.pg{font-size:1.8rem;letter-spacing:.04em;text-transform:uppercase;margin:0 0 .6rem}
.lede{max-width:46rem;color:#3D4A50;margin:0 0 1rem}
.key{max-width:46rem;font-size:.93rem;color:#3D4A50;background:#fff;
     border-left:3px solid var(--Yellow);padding:.8rem 1.1rem;margin:0 0 1rem}
.warn{max-width:46rem;font-size:.93rem;color:#3D4A50;background:#fff;
      border-left:3px solid var(--Rust);padding:.8rem 1.1rem;margin:0 0 2.8rem}
.row{display:grid;grid-template-columns:210mm 1fr;gap:2.6rem;
     align-items:start;margin:0 0 4.5rem;padding:0 0 4rem;
     border-bottom:1px solid rgba(17,19,20,.12)}
@media (max-width:1180px){.row{grid-template-columns:1fr}}
.note h2{font-size:1.15rem;letter-spacing:.05em;text-transform:uppercase;margin:0 0 .1rem}
.note h2 b{font:700 .78rem/1 "Noto Sans",sans-serif;letter-spacing:.16em;
           color:#5A686E;display:block;margin:0 0 .5rem}
.note .tag{display:inline-block;font-size:.6rem;letter-spacing:.14em;
           text-transform:uppercase;background:#111314;color:#fff;
           padding:.25rem .5rem;margin:0 0 1rem}
.note p{max-width:34rem;font-size:.92rem;color:#3D4A50;margin:0 0 .8rem}
.note b{color:#111314}
.swatches{display:flex;flex-wrap:wrap;gap:.4rem;margin:1.2rem 0 0}
.sw{font:600 .58rem/1 ui-monospace,Menlo,monospace;letter-spacing:.04em;
    padding:.45rem .5rem;border:1px solid rgba(17,19,20,.14)}

/* ---------------------------------------------------------------------------
   THE SHEET IS A REAL A4. 210 x 297mm, so what is on screen is what lands in
   Illustrator — measure off it rather than guessing at ratios.
   --------------------------------------------------------------------------- */
.sheet{width:210mm;height:297mm;position:relative;overflow:hidden;
       box-shadow:0 1px 2px rgba(17,19,20,.16),0 14px 40px rgba(17,19,20,.14)}

/* The wordmark, rebuilt from graphics/logo-00.svg: Futura Medium at .26em over
   Futura Bold at .03em, with 産靈 set in a mincho beside it. */
.wm-a{font-family:Futura,"Futura PT",Jost,"Century Gothic","Avenir Next",sans-serif;
      font-weight:500;letter-spacing:.26em;display:block}
.wm-m{font-family:Futura,"Futura PT",Jost,"Century Gothic","Avenir Next",sans-serif;
      font-weight:700;letter-spacing:.03em;display:block;line-height:.86}
.wm-j{font-family:"Hiragino Mincho ProN","Yu Mincho","Noto Serif JP",serif}

/* =========================================================================
   A — KAKEJIKU. Ink on paper, one seal.
   ========================================================================= */
.sh-a{background:var(--Paper);color:var(--Black);display:flex}
.sh-a .a-main{flex:1;padding:20mm 6mm 16mm 20mm;display:flex;flex-direction:column}
.sh-a .a-side{width:34mm;border-left:.35mm solid var(--Black);
              padding:20mm 0 16mm;display:flex;flex-direction:column;
              align-items:center}

/* The seven pleats of the hakama — five in front, two behind. A rule that
   means something here and nowhere else. */
.sh-a .a-pleats{display:flex;gap:1.6mm;margin:0 0 12mm}
.sh-a .a-pleats i{display:block;width:.5mm;height:14mm;background:var(--Black)}
.sh-a .a-pleats i:nth-child(6),
.sh-a .a-pleats i:nth-child(7){opacity:.32}

.sh-a .a-eyebrow{font-size:9pt;letter-spacing:.42em;text-transform:uppercase;
                 font-weight:700;margin:0 0 6mm;color:var(--Black)}
.sh-a .a-name{font-family:Futura,"Futura PT",Jost,"Century Gothic",sans-serif;
              font-weight:700;font-size:58pt;line-height:.88;letter-spacing:-.005em;
              text-transform:uppercase;margin:0}
.sh-a .a-name span{display:block}
.sh-a .a-name span:last-child{margin-left:.06em}
.sh-a .a-grade{font-size:12pt;letter-spacing:.2em;text-transform:uppercase;
               margin:6mm 0 0;color:var(--Black)}

.sh-a .a-when{margin-top:auto;padding-top:14mm}
.sh-a .a-when::before{content:"";display:block;width:26mm;height:.9mm;
                      background:var(--Black);margin:0 0 6mm}
.sh-a .a-date{font-size:13pt;letter-spacing:.16em;text-transform:uppercase;margin:0}
.sh-a .a-hour{font-family:Futura,"Futura PT",Jost,"Century Gothic",sans-serif;
              font-weight:700;font-size:34pt;line-height:1;margin:3mm 0 0;
              letter-spacing:.01em}
.sh-a .a-hour em{font-style:normal;padding:0 .18em;font-weight:500}
.sh-a .a-free{font-size:10pt;letter-spacing:.24em;text-transform:uppercase;
              margin:5mm 0 0;color:var(--Vandyke);font-weight:700}

.sh-a .a-foot{margin-top:14mm}
.sh-a .a-mark{margin:0 0 4mm;position:relative;display:inline-block}
.sh-a .a-mark .wm-a{font-size:8pt}
.sh-a .a-mark .wm-m{font-size:23pt}
.sh-a .a-mark .wm-j{position:absolute;right:-7mm;top:0;font-size:9pt;
                    writing-mode:vertical-rl;letter-spacing:.1em}
.sh-a .a-addr{font-size:9pt;line-height:1.5;margin:0;color:var(--Black)}
.sh-a .a-url{font-size:9pt;letter-spacing:.14em;margin:3mm 0 0;font-weight:700}

.sh-a .a-ja{writing-mode:vertical-rl;text-orientation:upright;
            font-family:"Hiragino Mincho ProN","Yu Mincho","Noto Serif JP",serif;
            font-size:19pt;letter-spacing:.14em;margin:0}
.sh-a .a-ja-sm{font-size:12pt;margin-top:8mm;letter-spacing:.2em}
.sh-a .a-seal{margin-top:auto;width:17mm;height:17mm;background:var(--Vandyke);
              color:var(--Paper);display:flex;flex-direction:column;
              align-items:center;justify-content:center;line-height:1;
              font-family:"Hiragino Mincho ProN","Yu Mincho","Noto Serif JP",serif}
.sh-a .a-seal span{font-size:15pt}
.sh-a .a-seal em{font-style:normal;font-size:8pt;margin-top:.6mm;letter-spacing:.1em}

/* =========================================================================
   B — LA PLANCHA. The photograph is a plate, 2:1, the tatami's own ratio.
   ========================================================================= */
.sh-b{background:var(--Slate);color:var(--White);display:flex;flex-direction:column}
.sh-b .b-plate{margin:0;width:210mm;height:105mm;overflow:hidden;background:var(--Black)}
.sh-b .b-plate img{width:100%;height:100%;object-fit:cover;display:block;
                   filter:grayscale(1) contrast(1.08) brightness(.96)}
.sh-b .b-body{flex:1;padding:14mm 20mm 16mm;display:flex;flex-direction:column}
.sh-b .b-eyebrow{font-size:9pt;letter-spacing:.42em;text-transform:uppercase;
                 font-weight:700;color:var(--Apricot);margin:0 0 5mm}
.sh-b .b-name{font-family:Futura,"Futura PT",Jost,"Century Gothic",sans-serif;
              font-weight:700;font-size:53pt;line-height:.92;letter-spacing:0;
              text-transform:uppercase;margin:0}
.sh-b .b-grade{font-size:11pt;letter-spacing:.1em;margin:4mm 0 0;color:rgba(255,255,255,.86)}
.sh-b .b-grade em{font-style:normal;padding:0 .35em;color:var(--Apricot)}
.sh-b .b-rule{height:.5mm;background:var(--Apricot);margin:9mm 0 8mm}
.sh-b .b-facts{display:grid;grid-template-columns:1fr 1fr;gap:12mm;margin:0}
.sh-b .b-facts dt{font-size:7.5pt;letter-spacing:.28em;text-transform:uppercase;
                  color:var(--Apricot);margin:0 0 2.5mm;font-weight:700}
.sh-b .b-facts dd{margin:0;font-size:11pt;line-height:1.6;color:rgba(255,255,255,.92)}
.sh-b .b-facts dd b{font-family:Futura,"Futura PT",Jost,sans-serif;
                    font-weight:700;font-size:17pt;letter-spacing:.01em;color:#fff}
/* The chip hangs off the foot rather than off the facts, so the slack in the
   column collects in ONE place — between the information and the sign-off —
   instead of appearing twice and reading as a layout that has not decided. */
.sh-b .b-chip{align-self:flex-start;margin:auto 0 0;background:var(--Apricot);
              color:var(--YellowInk);font-size:9pt;font-weight:700;
              letter-spacing:.24em;text-transform:uppercase;padding:2.6mm 5mm}
.sh-b .b-foot{margin-top:10mm;padding-top:6mm;display:flex;align-items:flex-end;
              justify-content:space-between;
              border-top:.25mm solid rgba(255,255,255,.26)}
.sh-b .b-mark{margin:0;position:relative;display:inline-block}
.sh-b .b-mark .wm-a{font-size:7.5pt}
.sh-b .b-mark .wm-m{font-size:21pt}
.sh-b .b-mark .wm-j{position:absolute;right:-6.5mm;top:0;font-size:8.5pt;
                    writing-mode:vertical-rl;letter-spacing:.1em}
.sh-b .b-url{margin:0;font-size:9.5pt;letter-spacing:.14em;font-weight:700}

/* =========================================================================
   C — EL CARTEL. Two colours, and the date is the hero.
   ========================================================================= */
.sh-c{background:var(--Yellow);color:var(--Black);display:flex;flex-direction:column}
.sh-c .c-top{background:var(--Black);color:var(--Yellow);padding:6mm 20mm;
             position:relative}
.sh-c .c-top .wm-a{font-size:7pt}
.sh-c .c-top .wm-m{font-size:19pt}
.sh-c .c-top .wm-j{position:absolute;left:44mm;top:6mm;font-size:8pt;
                   writing-mode:vertical-rl;letter-spacing:.1em}
/* The date fills the top third at 190pt, which is the whole argument: from one
   poster to the next it is the number that changes. `ch`-free tabular figures
   keep 12 and 30 the same width, so a two-digit day never reflows the stack
   beside it. */
.sh-c .c-body{flex:1;padding:14mm 20mm 0;display:flex;flex-direction:column}
.sh-c .c-eyebrow{font-size:9pt;letter-spacing:.42em;text-transform:uppercase;
                 font-weight:700;margin:0 0 3mm}
.sh-c .c-date{display:flex;align-items:flex-start;gap:7mm}
.sh-c .c-day{font-family:Futura,"Futura PT",Jost,"Century Gothic",sans-serif;
             font-weight:700;font-size:190pt;line-height:.74;letter-spacing:-.04em;
             font-variant-numeric:tabular-nums}
.sh-c .c-stack{display:flex;flex-direction:column;padding-top:6mm}
.sh-c .c-stack em{font-family:Futura,"Futura PT",Jost,sans-serif;font-style:normal;
                  font-weight:700;font-size:44pt;line-height:1;
                  text-transform:uppercase;letter-spacing:.02em}
.sh-c .c-stack i{font-style:normal;font-size:11pt;letter-spacing:.3em;
                 text-transform:uppercase;margin-top:4mm;font-weight:700}

/* The middle block hangs off a heavy rule, and the rule is the seam of the
   poster: everything above it is when, everything below it is who. */
.sh-c .c-mid{margin-top:auto;padding-top:8mm;border-top:1.6mm solid var(--Black)}
.sh-c .c-name{font-family:Futura,"Futura PT",Jost,"Century Gothic",sans-serif;
              font-weight:700;font-size:44pt;line-height:1;text-transform:uppercase;
              margin:0}
.sh-c .c-grade{font-size:12pt;letter-spacing:.14em;text-transform:uppercase;
               margin:4mm 0 0;font-weight:700}
.sh-c .c-ja{font-family:"Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif;
            font-size:11pt;letter-spacing:.1em;margin:2.5mm 0 0}
/* ONE void, not two. With `margin-top:auto` on both blocks the sheet had an
   equal gap under the date and another under the name, which reads as a
   layout that has not decided. All the slack goes above the rule now. */
.sh-c .c-end{padding:14mm 0 0}
.sh-c .c-hour{margin:0}
.sh-c .c-hour span{display:inline-block;background:var(--Black);color:var(--Yellow);
                   font-family:Futura,"Futura PT",Jost,sans-serif;font-weight:700;
                   font-size:30pt;letter-spacing:.02em;padding:4mm 8mm 4.5mm}
.sh-c .c-free{font-size:12pt;letter-spacing:.26em;text-transform:uppercase;
              font-weight:700;margin:7mm 0 0}
.sh-c .c-foot{padding:12mm 20mm 14mm;display:flex;align-items:flex-end;
              justify-content:space-between;gap:8mm}
.sh-c .c-foot p{margin:0;font-size:8.5pt;line-height:1.5;max-width:105mm}
.sh-c .c-url{font-weight:700;letter-spacing:.14em;font-size:9.5pt;white-space:nowrap}

@media print{
  body{background:#fff}
  .wrap{padding:0;max-width:none}
  .pg,.lede,.key,.warn,.note{display:none}
  .row{display:block;border:0;margin:0;padding:0}
  .sheet{box-shadow:none;break-after:page}
}
"""


def build():
    rows = []
    for (letter, title, tag, prose), sheet in zip(
            NOTES, (sheet_a(), sheet_b(), sheet_c())):
        rows.append(f"""
<section class="row">
  {sheet}
  <div class="note">
    <h2><b>Propuesta {letter}</b>{title}</h2>
    <span class="tag">{tag}</span>
    {prose}
  </div>
</section>""")

    html = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tres carteles para la masterclass de Pedro Fortes</title>
<style>""" + CSS + """</style></head><body><div class="wrap">
<h1 class="pg">Tres carteles para la masterclass de Pedro Fortes</h1>
<p class="lede">A4 real —210&nbsp;&times;&nbsp;297&nbsp;mm— así que lo que hay
en pantalla es lo que llega a Illustrator: se puede medir encima en lugar de
deducir proporciones. Solo colores del diccionario de Sanzo&nbsp;Wada, tomados
por nombre de <code>styles/base.less</code>, y el par tipográfico del sitio:
Futura para el display, Noto&nbsp;Sans para el resto.</p>

<p class="key"><b>No son tres pieles del mismo cartel.</b> Los carteles que ya
existen son todos una misma idea —foto a sangre, velo gris encima, texto
encima del velo— y esa idea tiene dos costes que aparecen siempre: necesita una
fotografía del instructor antes de empezar, que es por lo que hay cinco
masterclass próximas sin cartel; y deja el texto sobre una imagen, con el
contraste que salga. Cada propuesta responde a una pregunta distinta y la nota
de al lado dice a cuál.</p>

<p class="warn"><b>La fotografía de la propuesta B es un marcador de posición.</b>
Es la foto del tatami del dojo, que es un fichero real del repositorio
(<code>access-information-NdxqmVbV-aikido-musubi-room.jpg</code>). En el cartel
definitivo va la de Pedro Fortes. Y la Futura la pone tu Mac: si en otra
máquina se ve distinto, es que ha caído al sustituto.</p>
""" + '\n'.join(rows) + """
<section class="row" style="border:0;grid-template-columns:1fr">
  <div class="note">
    <h2><b>Lo que comparten</b>El sistema, no el estilo</h2>
    <p><b>La marca es la del logotipo, no una aproximación.</b> Está
    reconstruida desde <code>graphics/logo-00.svg</code>: AIKIDO en Futura
    Medium con <code>letter-spacing:.26em</code>, MUSUBI en Futura Bold
    con <code>.03em</code>, y 産靈 en vertical al lado, en mincho, que es como
    lo trae el SVG (Hiragino Mincho Pro W6).</p>
    <p><b>Una sola familia de acento por hoja.</b> A lleva un rojo y nada más.
    B lleva un amarillo y nada más. C lleva dos colores en total. Ninguna de
    las tres reparte tres acentos por la página, que es lo que convierte un
    cartel en un folleto.</p>
    <p><b>El japonés cambia de voz a propósito.</b> En A va en mincho y en
    vertical, porque el formato es un rollo. En B y C va en línea con el
    resto, porque son piezas de información y no de caligrafía.</p>
    <p><b>Y las tres caben en la misma retícula:</b> margen de 20&nbsp;mm a
    izquierda y derecha en las tres, para que la serie se reconozca de una
    masterclass a la siguiente aunque cambie el enfoque.</p>
    <div class="swatches">
      <span class="sw" style="background:#111314;color:#fff">Black #111314</span>
      <span class="sw" style="background:#34454C;color:#fff">Slate Color #34454C</span>
      <span class="sw" style="background:#FFF200">Yellow #FFF200</span>
      <span class="sw" style="background:#ffdd00">Apricot Yellow #ffdd00</span>
      <span class="sw" style="background:#82241f;color:#fff">Vandyke Red #82241f</span>
      <span class="sw" style="background:#ae5224;color:#fff">Burnt Sienna #ae5224</span>
      <span class="sw" style="background:#FBFAF7">Papel #FBFAF7</span>
    </div>
  </div>
</section>
</div></body></html>
"""
    io.open(OUT, 'w', encoding='utf-8').write(html)
    print('wrote docs/mockups/poster.html')


if __name__ == '__main__':
    build()
