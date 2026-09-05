#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Where the facility photographs go on the three location pages.

THE QUESTION IS NOT "WHERE DO WE PUT A GALLERY". "Dónde entrenamos" already
exists on every location page and already carries an image per room — an
aerial plan, cropped to an 11rem strip. That image answers nothing. A satellite
view at that size is a grey rectangle with a road through it: it does not tell
you what the room is like, and it does not help you recognise the building when
you are standing in front of it.

So the proposal is a SWAP, not a new section. The plan is the right image on
/acceso/, where it carries the entrance letters and the floor overlay and
answers "how do I get in". On the location page the same slot should carry the
photograph, because the question there is "what is this place".

The mockup shows the current card and the proposed card side by side for each
town, so the swap can be judged rather than described.

    python3 docs/mockups/src/build_venuepics.py
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, 'docs', 'mockups', 'venuepics.html')

# What exists, per room. The counts are lopsided and that shapes the answer:
# one photograph of the dojo, several of Espronceda and Marina-Besòs, three of
# the UB. A gallery would look starved on Badalona and padded on Barcelona.
TOWNS = [
    {
        'town': 'Badalona', 'page': '/badalona/',
        'venues': [
            {'name': 'Aikido Musubi',
             'facility': 'Instalaciones Deportivas Badalona Sur',
             'plan': 'plan-00.jpg', 'photo': 'musubi.jpg',
             'caption': 'El tatami y el kamiza del dojo.',
             'have': 'una fotografía'},
        ],
        'note': 'Una sola fotografía, y es la mejor de todas: el tatami, el '
                'kamiza con la caligrafía, los armeros. Es exactamente lo que '
                'alguien quiere ver antes de escribir un correo.',
    },
    {
        'town': 'Sant Adrià de Besòs', 'page': '/sant-adria-de-besos/',
        'venues': [
            {'name': 'Marina-Besòs',
             'facility': 'Polideportivo Municipal Marina-Besòs',
             'plan': 'plan-01.jpg', 'photo': 'marina-sala.jpg',
             'caption': 'La sala de tatami del polideportivo.',
             'have': 'dos fotografías'},
        ],
        'note': 'La sala dice lo que el plano no puede: que el tatami está '
                'montado sobre parqué, en una sala grande y con luz. Reconocible.',
    },
    {
        'town': 'Barcelona', 'page': '/barcelona/',
        'venues': [
            {'name': 'CxEM Espronceda',
             'facility': 'Complejo Deportivo Municipal Espronceda',
             'plan': 'plan-03.jpg', 'photo': 'espronceda-sala.jpg',
             'caption': 'La sala de tatami, dentro del complejo.',
             'have': 'cuatro fotografías'},
            {'name': 'Facultad de Derecho de la UB',
             'facility': 'Facultad de Derecho de la Universidad de Barcelona',
             'plan': 'plan-02.jpg', 'photo': 'ub.jpg',
             'caption': 'La entrada a la facultad, desde la Diagonal.',
             'have': 'tres fotografías'},
        ],
        'note': 'Los dos espacios de Barcelona son los más difíciles de '
                'encontrar y los que más ganan. La fachada del CxEM lleva el '
                'nombre escrito en el edificio; la de la UB es la rampa por la '
                'que se entra.',
    },
]


def card(v, kind):
    img = v['plan'] if kind == 'plan' else v['photo']
    cap = ('Vista aérea, recortada a 11rem.' if kind == 'plan' else v['caption'])
    return f"""
    <article class="ven">
      <img src="venuepics/{img}" alt="">
      <div class="ven-in">
        <h4>{v['name']}</h4>
        <p class="addr">{v['facility']}<br>Dirección · CP Población</p>
        <p class="addr"><b>Cómo se entra:</b> …</p>
        <p class="maps"><span>Google Maps</span><span>Apple Maps</span></p>
      </div>
      <p class="cap">{cap}</p>
    </article>"""


def build():
    blocks = []
    for t in TOWNS:
        now = ''.join(card(v, 'plan') for v in t['venues'])
        new = ''.join(card(v, 'photo') for v in t['venues'])
        have = ', '.join('%s: %s' % (v['name'], v['have']) for v in t['venues'])
        blocks.append(f"""
<section class="block">
  <h2>{t['town']} <code>{t['page']}</code></h2>
  <p class="note">{t['note']}</p>
  <p class="have"><b>Lo que hay:</b> {have}.</p>
  <div class="pair">
    <div>
      <p class="lab">Ahora — el plano aéreo</p>
      <div class="vens">{now}</div>
    </div>
    <div>
      <p class="lab lab-y">Propuesta — la fotografía</p>
      <div class="vens">{new}</div>
    </div>
  </div>
</section>""")

    html = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Las fotos de los espacios en las páginas de ciudad</title>
<style>
  * { box-sizing:border-box; }
  body { margin:0; background:#F7F7F5; color:#111314;
         font:15px/1.65 "Noto Sans",-apple-system,BlinkMacSystemFont,sans-serif; }
  .wrap { max-width:1180px; margin:0 auto; padding:2.5rem 2rem 5rem; }
  h1 { font-size:1.8rem; letter-spacing:.04em; text-transform:uppercase; margin:0 0 .6rem; }
  .lede { max-width:44rem; color:#3D4A50; margin:0 0 1rem; }
  .key { max-width:44rem; font-size:.93rem; color:#3D4A50; background:#fff;
         border-left:3px solid #FFF200; padding:.75rem 1rem; margin:0 0 2.6rem; }
  .block { margin:0 0 3rem; padding:0 0 2.4rem; border-bottom:1px solid rgba(17,19,20,.12); }
  .block h2 { font-size:1.2rem; letter-spacing:.05em; text-transform:uppercase; margin:0 0 .4rem; }
  .block h2 code { font:.72rem ui-monospace,Menlo,monospace; color:#5A686E;
                   text-transform:none; letter-spacing:0; }
  .note { max-width:44rem; color:#3D4A50; font-size:.93rem; margin:0 0 .5rem; }
  .have { max-width:44rem; color:#5A686E; font-size:.82rem; margin:0 0 1.4rem; }
  .pair { display:grid; grid-template-columns:1fr 1fr; gap:1.8rem; }
  @media (max-width:900px) { .pair { grid-template-columns:1fr; } }
  .lab { font-size:.62rem; letter-spacing:.18em; text-transform:uppercase;
         color:#5A686E; margin:0 0 .6rem; padding-bottom:.35rem;
         border-bottom:2px solid rgba(17,19,20,.15); }
  .lab-y { border-bottom-color:#FFF200; color:#111314; }
  .vens { display:grid; grid-template-columns:1fr; gap:1.2rem; }
  .ven { border:1px solid rgba(17,19,20,.13); background:#fff; margin:0; }
  .ven img { display:block; width:100%; height:11rem; object-fit:cover;
             background:rgba(17,19,20,.04); }
  .ven-in { padding:1.1rem 1.2rem .6rem; }
  .ven h4 { margin:0 0 .5rem; font-size:1.02rem; letter-spacing:.04em; font-weight:600; }
  .addr { margin:0 0 .5rem; font-size:.83rem; line-height:1.55; color:#5A686E; }
  .addr b { color:#111314; }
  .maps { display:flex; gap:.5rem; margin:.4rem 0 0; }
  .maps span { padding:.4rem .75rem; box-shadow:inset 0 0 0 1px rgba(17,19,20,.13);
               font-size:.56rem; letter-spacing:.13em; text-transform:uppercase; color:#5A686E; }
  .cap { margin:0; padding:.7rem 1.2rem 1rem; font-size:.72rem; color:#5A686E;
         border-top:1px solid rgba(17,19,20,.07); }
</style></head><body><div class="wrap">
<h1>Las fotos de los espacios en las páginas de ciudad</h1>
<p class="lede">No hace falta una sección nueva. «Dónde entrenamos» ya existe en
las tres páginas y ya lleva una imagen por espacio: el plano aéreo, recortado a
una tira de 11rem. Esa imagen no responde a nada.</p>
<p class="key"><b>La propuesta es un cambio, no una adición.</b> El plano es la
imagen correcta en <code>/acceso/</code>, donde lleva las letras de las entradas
y la planta encima y responde a «por dónde entro». En la página de ciudad la
pregunta es otra —&nbsp;«qué sitio es este»&nbsp;— y la respuesta es la
fotografía. Cero secciones nuevas, cero peso de página añadido: una imagen
sustituye a otra.</p>
""" + '\n'.join(blocks) + """
<section class="block" style="border:0">
  <h2>Lo que NO propongo, y por qué</h2>
  <p class="note"><b>Una galería por ciudad.</b> Hay una foto del dojo y cuatro
  del CxEM. Una galería se vería famélica en Badalona y rellena en Barcelona, y
  la asimetría no significa nada sobre los espacios: significa que ese día había
  cámara en un sitio y no en otro.</p>
  <p class="note"><b>Una banda a sangre con la foto del dojo.</b> Es la mejor
  imagen de las cinco y tienta, pero la página ya abre con un hero a sangre. Dos
  bandas de ancho completo en la misma página convierten el hero en una de dos
  en vez de en la entrada.</p>
  <p class="note"><b>Segunda foto donde la haya.</b> Es lo único que dejaría
  abierto: en CxEM Espronceda y en la UB la fachada ayuda de verdad a reconocer
  el sitio, y cabría como una miniatura pequeña bajo la tarjeta. Lo dejo fuera
  de esta propuesta porque solo dos de los cuatro espacios podrían tenerla.</p>
</section>
</div></body></html>
"""
    io.open(OUT, 'w', encoding='utf-8').write(html)
    print('wrote docs/mockups/venuepics.html')


if __name__ == '__main__':
    build()
