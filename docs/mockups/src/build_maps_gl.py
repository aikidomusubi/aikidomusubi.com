#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The three map palettes as MapLibre GL styles over OpenStreetMap data, plus
a harness that renders a hero image per town at each of the four hero widths.

WHY NOT GOOGLE. Two hard limits, not preferences. The Static Maps API tops out
at 640x640, or 1280 effective with scale=2, and `.lo-hero` asks for 2880x2160 —
so the images simply cannot be produced that way. And Google Maps Platform
requires its attribution to stay visible in the image, which is exactly what a
4:3 crop under an 86% scrim with white type on it destroys. OpenStreetMap has
neither problem: render at any size, and ODbL wants one line of credit that
fits comfortably in the hero.

TILES. OpenFreeMap (https://openfreemap.org), which serves OpenMapTiles-schema
vector tiles of the planet with no key and no quota. The layer names below —
water, landcover, landuse, park, building, transportation, boundary, place —
are that schema's, not invented here.

THE PALETTES ARE NOT RE-TYPED. They are imported from build_maps.py, which owns
them, so the Snazzy Maps JSON and these cannot drift apart.

    python3 docs/mockups/src/build_maps_gl.py
    ./docs/mockups/render.sh      # then open /mockups/maps-render.html
"""
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# HERE is docs/mockups/src, so the repository root is three levels up.
# Two lands on docs/ — the same slip build_maps.py made, which is worth
# noticing: a path that is wrong by one level still writes files and still
# reports success.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, 'docs', 'mockups', 'maps')

_spec = importlib.util.spec_from_file_location('build_maps', os.path.join(HERE, 'build_maps.py'))
BM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BM)

TILES = 'https://tiles.openfreemap.org/planet'

# ---------------------------------------------------------------------------
# The towns.
#
# Centre and zoom are per town because they are different sizes: Barcelona is a
# city and Sant Adrià is 3.8 km². A single zoom would show one of them as a
# smudge and the other as a street corner. `bearing` is 0 everywhere — a
# rotated map is a design flourish that makes a place harder to recognise.
# ---------------------------------------------------------------------------
# The centres are pulled SOUTH of each town centre on purpose. Only rows 30-44%
# of the rendered image survive the crop and the scrim, so whatever should be
# seen has to sit in the upper third of the frame — and content rides higher when
# the map centre is south of it. Centred on the town itself, the readable band
# fell on the hills behind it.
TOWNS = [
    {'id': 'badalona',            'name': 'Badalona',
     'center': [2.2430, 41.4180], 'zoom': 12.6},
    {'id': 'sant-adria-de-besos', 'name': 'Sant Adrià de Besòs',
     'center': [2.2245, 41.4120], 'zoom': 13.2},
    {'id': 'barcelona',           'name': 'Barcelona',
     'center': [2.1700, 41.3350], 'zoom': 11.6},
]

# THE HERO ONLY EVER SHOWS THE MIDDLE THIRD OF THESE, and the framing above is
# set for that. `.lo-hero` is full-bleed at a 26rem min-height, and the image is
# `object-fit: cover` inside it: at 1440x416 from a 2880x2160 file the browser
# scales to the width and crops to 416, which is 38% of the image height. So the
# town has to sit in the vertical middle — the top and bottom thirds are never
# seen on a desktop. On a phone the box is nearly 4:3 and almost all of it shows,
# which is why the file stays 4:3 rather than being rendered as a strip.

# The four widths _includes/preload.html and _layouts/location.html expect, at
# the hero's 4:3.
WIDTHS = [1200, 1920, 2560, 2880]


def style(st):
    """One MapLibre GL style. Same six roles as the Google version, expressed
    in the OpenMapTiles schema."""
    return {
        "version": 8,
        "name": "Musubi %s" % st['name'].split()[-1],
        # ODbL. The credit is data, not decoration: whatever renders this has
        # to surface it, and the hero prints it in `.lo-hero-credit`.
        "sources": {
            "osm": {
                "type": "vector",
                "url": TILES,
                "attribution": "© OpenStreetMap contributors"
            }
        },
        "glyphs": "https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf",
        "layers": [
            {"id": "ground", "type": "background",
             "paint": {"background-color": st['land']}},

            {"id": "landcover", "type": "fill", "source": "osm",
             "source-layer": "landcover",
             "paint": {"fill-color": st['park'], "fill-opacity": 0.55}},

            {"id": "landuse-park", "type": "fill", "source": "osm",
             "source-layer": "landuse",
             "filter": ["in", "class", "park", "cemetery", "pitch"],
             "paint": {"fill-color": st['park'], "fill-opacity": 0.7}},

            {"id": "park", "type": "fill", "source": "osm",
             "source-layer": "park",
             "paint": {"fill-color": st['park'], "fill-opacity": 0.8}},

            {"id": "water", "type": "fill", "source": "osm",
             "source-layer": "water",
             "paint": {"fill-color": st['water']}},

            {"id": "waterway", "type": "line", "source": "osm",
             "source-layer": "waterway",
             "paint": {"line-color": st['water'], "line-width": 1.6}},

            {"id": "building", "type": "fill", "source": "osm",
             "source-layer": "building",
             "minzoom": 13,
             "paint": {"fill-color": st['building'], "fill-opacity": 0.85}},

            # ---- roads, in the same three weights as the Google style -------
            {"id": "road-minor", "type": "line", "source": "osm",
             "source-layer": "transportation",
             "filter": ["in", "class", "minor", "service", "track"],
             "minzoom": 12,
             "paint": {"line-color": st['local'],
                       "line-width": ["interpolate", ["linear"], ["zoom"], 12, 0.4, 16, 2.4]}},

            {"id": "road-secondary", "type": "line", "source": "osm",
             "source-layer": "transportation",
             "filter": ["in", "class", "secondary", "tertiary"],
             "paint": {"line-color": st['arterial'],
                       "line-width": ["interpolate", ["linear"], ["zoom"], 10, 0.5, 16, 4]}},

            {"id": "road-primary", "type": "line", "source": "osm",
             "source-layer": "transportation",
             "filter": ["in", "class", "primary", "trunk"],
             "paint": {"line-color": st['arterial'],
                       "line-width": ["interpolate", ["linear"], ["zoom"], 8, 0.8, 16, 6]}},

            {"id": "road-motorway", "type": "line", "source": "osm",
             "source-layer": "transportation",
             "filter": ["==", "class", "motorway"],
             "paint": {"line-color": st['highway'],
                       "line-width": ["interpolate", ["linear"], ["zoom"], 8, 1.0, 16, 7]}},

            # ---- the municipal boundary -------------------------------------
            # The one piece of information a town hero owes the reader: where
            # this town stops and the next one starts. admin_level 6-8 covers
            # comarca, municipality and district in Catalonia.
            {"id": "boundary", "type": "line", "source": "osm",
             "source-layer": "boundary",
             "filter": ["all", [">=", "admin_level", 4], ["<=", "admin_level", 8]],
             "paint": {"line-color": st['border'], "line-width": 1.1,
                       "line-dasharray": [4, 3], "line-opacity": 0.9}},

            # ---- NO LABELS, and this was decided by looking at the page ----
            #
            # The hero band is 26rem and the scrim is 86% black by 78% of it, so
            # the only part of the map anyone reads is the top third. Place
            # labels landed below that, which meant the Barcelona hero showed
            # Rubí, Cerdanyola, Montcada, La Llagosta, Alella, El Masnou and
            # Premià — every town except Barcelona — and Badalona's showed four
            # neighbours and not Badalona. A hero that names the wrong places is
            # worse than one that names none.
            #
            # The h1 and the eyebrow already say which town this is. Without
            # labels the map is what it should be here: the coastline, the grid
            # and the motorways as texture behind the words.
        ]
    }


HARNESS = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Render the location heroes from OpenStreetMap</title>
<link href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" rel="stylesheet">
<style>
  * { box-sizing: border-box; }
  body { margin:0; background:#F7F7F5; color:#111314;
         font:15px/1.6 "Noto Sans",-apple-system,BlinkMacSystemFont,sans-serif; }
  .wrap { max-width:1140px; margin:0 auto; padding:2.5rem 2rem 4rem; }
  h1 { font-size:1.7rem; letter-spacing:.04em; text-transform:uppercase; margin:0 0 .5rem; }
  p.lede { max-width:43rem; color:#3D4A50; margin:0 0 1.2rem; }
  .note { max-width:43rem; font-size:.9rem; color:#3D4A50; background:#fff;
          border-left:3px solid #FFF200; padding:.7rem 1rem; margin:0 0 1.6rem; }
  .bar { display:flex; flex-wrap:wrap; gap:1rem; align-items:flex-end; margin:0 0 1.4rem; }
  label { display:block; font-size:.68rem; letter-spacing:.14em; text-transform:uppercase;
          color:#5A686E; margin-bottom:.25rem; }
  select, button { font:inherit; padding:.5rem .7rem; border:1px solid rgba(17,19,20,.25);
                   background:#fff; }
  button { background:#111314; color:#fff; border:0; cursor:pointer;
           font-size:.7rem; letter-spacing:.16em; text-transform:uppercase; padding:.7rem 1.1rem; }
  button.alt { background:#FFF200; color:#111314; }
  #stage { position:relative; width:100%; aspect-ratio:4/3; background:#111314;
           border:1px solid rgba(17,19,20,.15); overflow:hidden; }
  #map { position:absolute; inset:0; }
  .scrim { position:absolute; inset:0; pointer-events:none;
           background:linear-gradient(180deg, rgba(17,19,20,.12) 0%, rgba(17,19,20,.86) 78%); }
  .scrim[hidden] { display:none; }
  .hero-in { position:absolute; inset:auto 0 0 0; padding:1.4rem 1.6rem 1.6rem;
             color:#fff; pointer-events:none; }
  .hero-in[hidden] { display:none; }
  .kick { margin:0; font-size:.6rem; letter-spacing:.2em; color:#FFF200; }
  .hero-in h2 { margin:.4rem 0 .5rem; font-size:1.8rem; line-height:1.1;
                letter-spacing:.04em; text-transform:uppercase; }
  .cta { display:flex; gap:.5rem; align-items:center; margin:.8rem 0 0; }
  .btn { padding:.55rem 1rem; background:#FFF200; color:#111314;
         font-size:.6rem; letter-spacing:.16em; text-transform:uppercase; }
  .btn2 { background:transparent; color:#fff; box-shadow:inset 0 0 0 1px rgba(255,255,255,.7); }
  .credit { position:absolute; right:.6rem; bottom:.4rem; font-size:.58rem;
            color:rgba(255,255,255,.72); pointer-events:none; }
  #log { margin-top:1rem; font:.75rem/1.6 ui-monospace,Menlo,monospace; color:#3D4A50;
         white-space:pre-wrap; background:#fff; padding:.8rem 1rem;
         border:1px solid rgba(17,19,20,.12); max-height:16rem; overflow:auto; }
</style></head><body><div class="wrap">
<h1>Render the location heroes from OpenStreetMap</h1>
<p class="lede">MapLibre over OpenFreeMap vector tiles — no key, no quota, and
renderable at any size. The three palettes are the same ones as the Snazzy Maps
styles; they are imported from the file that owns them.</p>
<p class="note"><b>ODbL.</b> The data is OpenStreetMap&rsquo;s and wants one line
of credit. Keep &ldquo;© OpenStreetMap contributors&rdquo; on the page that shows
the image &mdash; the hero prints it bottom-right. It is not optional and it is
not onerous.</p>

<div class="bar">
  <div><label for="sty">Style</label><select id="sty">__STYLE_OPTS__</select></div>
  <div><label for="twn">Town</label><select id="twn">__TOWN_OPTS__</select></div>
  <div><label for="wid">Width</label><select id="wid">__WIDTH_OPTS__</select></div>
  <div><label for="ov">Overlay</label><select id="ov">
    <option value="1">Hero scrim + type</option>
    <option value="0">Map only</option>
  </select></div>
  <button id="dl">Download this one</button>
  <button id="all" class="alt">Render all 36</button>
</div>

<div id="stage">
  <div id="map"></div>
  <div class="scrim"></div>
  <div class="hero-in">
    <p class="kick" id="k">BADALONA · AIKIDO MUSUBI</p>
    <h2 id="h">AIKIDO EN BADALONA</h2>
    <p class="cta"><span class="btn">Ven a probar</span><span class="btn btn2">Ver el horario</span></p>
  </div>
  <p class="credit">© OpenStreetMap contributors</p>
</div>
<div id="log">ready.</div>
</div>

<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
<script>
const STYLES = __STYLES__;
const TOWNS  = __TOWNS__;
const WIDTHS = __WIDTHS__;
const log = m => { const l = document.getElementById('log');
                   l.textContent += '\\n' + m; l.scrollTop = l.scrollHeight; };

// preserveDrawingBuffer is what makes the canvas readable after a frame. Without
// it toDataURL returns a blank image and nothing says why.
let map = new maplibregl.Map({
  container: 'map',
  style: STYLES[document.getElementById('sty').value],
  center: TOWNS[0].center, zoom: TOWNS[0].zoom,
  attributionControl: false, preserveDrawingBuffer: true
});

function idle() {
  return new Promise(res => {
    if (map.loaded() && map.areTilesLoaded()) return setTimeout(res, 350);
    map.once('idle', () => setTimeout(res, 350));
  });
}

async function apply() {
  const t = TOWNS[document.getElementById('twn').value];
  map.setStyle(STYLES[document.getElementById('sty').value]);
  map.jumpTo({ center: t.center, zoom: t.zoom });
  document.getElementById('k').textContent = t.name.toUpperCase() + ' · AIKIDO MUSUBI';
  document.getElementById('h').textContent = 'AIKIDO EN ' + t.name.toUpperCase();
  const on = document.getElementById('ov').value === '1';
  document.querySelector('.scrim').hidden = !on;
  document.querySelector('.hero-in').hidden = !on;
  await idle();
}
['sty','twn','ov'].forEach(id =>
  document.getElementById(id).addEventListener('change', apply));

// The canvas is sized to the requested width, rendered, read back, and put
// straight again. Rendering into the on-screen box and upscaling would give a
// 2880px file with 1200px of detail in it.
async function shot(styleKey, town, width) {
  const stage = document.getElementById('stage');
  const prev = stage.style.cssText;
  stage.style.cssText = 'position:fixed;left:-99999px;top:0;width:' + width +
                        'px;height:' + Math.round(width * 0.75) + 'px;';
  map.setStyle(STYLES[styleKey]);
  map.jumpTo({ center: town.center, zoom: town.zoom });
  map.resize();
  await idle();
  const url = map.getCanvas().toDataURL('image/png');
  stage.style.cssText = prev;
  map.resize();
  return url;
}

document.getElementById('dl').addEventListener('click', async () => {
  const k = document.getElementById('sty').value;
  const t = TOWNS[document.getElementById('twn').value];
  const w = parseInt(document.getElementById('wid').value, 10);
  log('rendering ' + k + ' / ' + t.id + ' / ' + w + '…');
  const url = await shot(k, t, w);
  const a = document.createElement('a');
  a.href = url; a.download = t.id + '-' + k + '-' + w + '.png'; a.click();
  log('  saved ' + a.download);
  await apply();
});

// Everything, for whichever style is selected: three towns times four widths.
document.getElementById('all').addEventListener('click', async () => {
  const k = document.getElementById('sty').value;
  for (const t of TOWNS) {
    for (const w of WIDTHS) {
      log('rendering ' + k + ' / ' + t.id + ' / ' + w + '…');
      const url = await shot(k, t, w);
      const a = document.createElement('a');
      a.href = url; a.download = t.id + '-' + k + '-' + w + '.png'; a.click();
      await new Promise(r => setTimeout(r, 700));
    }
  }
  log('done. ' + (TOWNS.length * WIDTHS.length) + ' files.');
  await apply();
});

map.on('load', () => log('tiles ready — OpenFreeMap / OpenStreetMap'));
window.__shot = shot; window.__STYLES = STYLES; window.__TOWNS = TOWNS;
</script>
</body></html>
"""


def build():
    os.makedirs(OUT, exist_ok=True)
    styles = {}
    for st in BM.STYLES:
        key = st['id']
        styles[key] = style(st)
        io.open(os.path.join(OUT, key + '.gl.json'), 'w', encoding='utf-8').write(
            json.dumps(styles[key], indent=2, ensure_ascii=False) + '\n')

    html = HARNESS
    html = html.replace('__STYLES__', json.dumps(styles, ensure_ascii=False))
    html = html.replace('__TOWNS__', json.dumps(TOWNS, ensure_ascii=False))
    html = html.replace('__WIDTHS__', json.dumps(WIDTHS))
    html = html.replace('__STYLE_OPTS__', ''.join(
        '<option value="%s">%s</option>' % (s['id'], s['name']) for s in BM.STYLES))
    html = html.replace('__TOWN_OPTS__', ''.join(
        '<option value="%d">%s</option>' % (i, t['name']) for i, t in enumerate(TOWNS)))
    html = html.replace('__WIDTH_OPTS__', ''.join(
        '<option value="%d">%d × %d</option>' % (w, w, round(w * 0.75)) for w in WIDTHS))

    path = os.path.join(ROOT, 'docs', 'mockups', 'maps-render.html')
    io.open(path, 'w', encoding='utf-8').write(html)
    print('wrote docs/mockups/maps-render.html')
    for st in BM.STYLES:
        print('      docs/mockups/maps/%s.gl.json' % st['id'])


if __name__ == '__main__':
    build()
