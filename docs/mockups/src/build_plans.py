#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The venue plans on /acceso/, as OpenStreetMap maps instead of orthophotos —
and the calibration page that has to come before they can be switched on.

THE PROBLEM IN ONE LINE. The overlay in _data/venues.yml is percentages of the
ORTHOPHOTO's frame: `points` for the dojo and parking polygons, `label_at` for
their labels, `at` for each lettered door. The orthophoto is a JPEG and carries
no geographic bounds, so nothing in the repository says what those percentages
are percentages OF. Put a different picture behind them and every door moves.

WHAT WAS DONE. Aikido Musubi's framing was matched to its orthophoto by eye in
four passes — the sports ground, the C-31 down the right side, the street grid
top-left — and the numbers are recorded in build_maps_gl.py. It is close, not
exact, and it cannot be made exact from that feature: OSM's polygon is the whole
sports ground where the orthophoto's green is the pitch alone.

WHAT IS DELIBERATELY NOT DONE. /acceso/ still shows the orthophotos. Shipping
the map with the old percentages would put lettered doors at the wrong doors,
which is worse than a satellite photo — that page exists to get somebody who is
already late to the right entrance.

This page shows each pair at the same size so the overlay can be re-drawn on the
map and the percentages read back off it.

    python3 docs/mockups/src/build_plans.py
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, 'docs', 'mockups', 'plans.html')

VENUES = [
    ('aikido-musubi', 'Aikido Musubi', 'Badalona',
     'El único encuadre calibrado contra su ortofoto. El recinto deportivo '
     'queda centrado, la C-31 baja por la derecha y la trama de calles está '
     'arriba a la izquierda, igual que en la foto.'),
    ('sant-adria-de-besos', 'Marina-Besòs', 'Sant Adrià de Besòs',
     'Centrado en las coordenadas del espacio, sin calibrar contra la ortofoto.'),
    ('cxem-espronceda', 'CxEM Espronceda', 'Barcelona',
     'Centrado en las coordenadas del espacio, sin calibrar contra la ortofoto.'),
    ('university-of-barcelona', 'Facultad de Derecho de la UB', 'Barcelona',
     'Centrado en las coordenadas que estaban en el mapa de _includes/map.html; '
     '_data/venues.yml no tiene lat/lng para este espacio.'),
]


def build():
    cards = []
    for vid, name, town, note in VENUES:
        cards.append(f"""
<section class="card">
  <h2>{name} <small>{town}</small></h2>
  <p class="note">{note}</p>
  <div class="pair">
    <figure>
      <img src="plans/ortho-{vid}.jpg" alt="Ortofoto de {name}">
      <figcaption>Ahora — la ortofoto, con la capa calibrada sobre ella</figcaption>
    </figure>
    <figure>
      <img src="plans/map-{vid}.jpg" alt="Mapa OSM de {name}">
      <figcaption class="y">Propuesta — el mapa, mismo tamaño, misma proporción</figcaption>
    </figure>
  </div>
  <p class="file"><code>images/access-information-NdxqmVbV-{vid}-plan-slate-lit.jpg</code>
     &middot; 1600 &times; 1600</p>
</section>""")

    html = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Los planos de acceso, como mapa de OpenStreetMap</title>
<style>
 *{box-sizing:border-box}
 body{margin:0;background:#F7F7F5;color:#111314;
      font:15px/1.65 "Noto Sans",-apple-system,sans-serif}
 .wrap{max-width:1180px;margin:0 auto;padding:2.5rem 2rem 5rem}
 h1{font-size:1.8rem;letter-spacing:.04em;text-transform:uppercase;margin:0 0 .6rem}
 .lede{max-width:44rem;color:#3D4A50;margin:0 0 1rem}
 .key{max-width:44rem;font-size:.92rem;color:#3D4A50;background:#fff;
      border-left:3px solid #FFF200;padding:.75rem 1rem;margin:0 0 1rem}
 .warn{max-width:44rem;font-size:.92rem;color:#3D4A50;background:#fff;
       border-left:3px solid #AE5224;padding:.75rem 1rem;margin:0 0 2.6rem}
 .card{margin:0 0 3rem;padding:0 0 2rem;border-bottom:1px solid rgba(17,19,20,.12)}
 .card h2{font-size:1.2rem;letter-spacing:.04em;margin:0 0 .3rem}
 .card h2 small{font-weight:400;color:#5A686E;font-size:.8rem;letter-spacing:.1em;
                text-transform:uppercase;margin-left:.5rem}
 .note{max-width:44rem;color:#3D4A50;font-size:.9rem;margin:0 0 1.2rem}
 .pair{display:grid;grid-template-columns:1fr 1fr;gap:1.4rem}
 @media(max-width:860px){.pair{grid-template-columns:1fr}}
 figure{margin:0}
 figure img{display:block;width:100%;aspect-ratio:1;object-fit:cover;
            border:1px solid rgba(17,19,20,.14);background:#111314}
 figcaption{font-size:.66rem;letter-spacing:.15em;text-transform:uppercase;
            color:#5A686E;margin-top:.5rem;padding-bottom:.3rem;
            border-bottom:2px solid rgba(17,19,20,.14)}
 figcaption.y{border-bottom-color:#FFF200;color:#111314}
 .file{margin:1rem 0 0;font-size:.75rem;color:#5A686E}
 .file code{font:.72rem ui-monospace,Menlo,monospace}
</style></head><body><div class="wrap">
<h1>Los planos de acceso, como mapa de OpenStreetMap</h1>
<p class="lede">Los cuatro espacios renderizados cuadrados a 1600&nbsp;px, en la
misma paleta que el resto y con el mismo generador. Al lado, la ortofoto que
sustituirían, al mismo tamaño.</p>
<p class="key"><b>La capa está en porcentajes de la ortofoto.</b>
<code>points</code> para los polígonos del dojo y el parking,
<code>label_at</code> para sus etiquetas y <code>at</code> para cada puerta con
su letra. La ortofoto es un JPEG y no lleva sus coordenadas, así que en el
repositorio no hay nada que diga de qué son porcentajes esos números. Cambiar la
imagen de debajo mueve todas las puertas.</p>
<p class="warn"><b>Por eso /acceso/ sigue mostrando las ortofotos.</b> Publicar
el mapa con los porcentajes actuales pondría las letras en puertas equivocadas,
que es peor que una foto de satélite: esa página existe para llevar a alguien
que ya va tarde a la entrada correcta. Dibuja encima del mapa y con esas marcas
regenero la capa.</p>
""" + '\n'.join(cards) + """
</div></body></html>
"""
    io.open(OUT, 'w', encoding='utf-8').write(html)
    print('wrote docs/mockups/plans.html')


if __name__ == '__main__':
    build()
