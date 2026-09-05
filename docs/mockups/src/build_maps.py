#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Three Google Maps / Snazzy Maps styles in the site's own palette, and a
preview that shows each one as it would actually be used: behind the location
hero's scrim, with the real h1, eyebrow and buttons on top.

WHY A PREVIEW AT ALL. Snazzy Maps will show you the style on a real map the
moment you paste it in, which is the thing this cannot do. What it cannot show
you is the only question that matters here — whether the map still reads as a
map once `.lo-hero`'s two-stop scrim is over it and there is white type in the
bottom third. So the preview draws a synthetic city (water, park, blocks, a
road hierarchy) rather than pretending to be Badalona, and puts the real hero
furniture on top of it.

COLOURS. Sanzo Wada dictionary entries where a colour is chosen, and LESS-style
`darken`/`lighten` of those entries where a ramp is needed — the same rule
styles/base.less already follows for @YellowInk and @RustInk, and for the same
reason: a ramp has to satisfy a relationship, not resemble an entry.

    python3 docs/mockups/src/build_maps.py
"""
import colorsys
import io
import json
import os

# Four levels up from docs/mockups/src/build_maps.py is the repository
# root. Three lands on docs/, which is where this quietly wrote its first
# run — the script reported success the whole time.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
OUT_HTML = os.path.join(ROOT, 'docs', 'mockups', 'maps.html')
OUT_JSON = os.path.join(ROOT, 'docs', 'mockups', 'maps')

# ---------------------------------------------------------------------------
# The dictionary entries this uses, copied from styles/base.less with their
# names so a reader can check them against it.
BLACK        = '#111314'   # Sanzo Wada "Black"
DARK         = '#34454C'   # Sanzo Wada "Slate Color"
BLUE         = '#064F6E'   # Sanzo Wada "Vandar Poel's Blue"
YELLOW       = '#FFF200'   # Sanzo Wada "Yellow"
GREEN        = '#1a7444'   # Sanzo Wada "Diamine Green"
RUST         = '#ae5224'   # Sanzo Wada "Burnt Sienna"
GLAUCOUS_G   = '#B7C2A9'   # Sanzo Wada "Dark Greenish Glaucous"
GLAUCOUS_B   = '#A5C8D1'   # Sanzo Wada "Light Glaucous Blue"
WHITE        = '#ffffff'


def _hsl(hexv):
    hexv = hexv.lstrip('#')
    r, g, b = (int(hexv[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, s, l


def _hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h, max(0.0, min(1.0, l)), s)
    return '#%02X%02X%02X' % (round(r * 255), round(g * 255), round(b * 255))


def darken(hexv, pct):
    """LESS `darken`: subtract `pct` percentage points of HSL lightness."""
    h, s, l = _hsl(hexv)
    return _hex(h, s, l - pct / 100.0)


def lighten(hexv, pct):
    h, s, l = _hsl(hexv)
    return _hex(h, s, l + pct / 100.0)


def desaturate(hexv, pct):
    h, s, l = _hsl(hexv)
    return _hex(h, max(0.0, s - pct / 100.0), l)


def lum(hexv):
    hexv = hexv.lstrip('#')
    ch = []
    for i in (0, 2, 4):
        c = int(hexv[i:i + 2], 16) / 255.0
        ch.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def over_black(hexv, alpha):
    """The colour a map pixel becomes under the hero scrim: `alpha` of black
    composited over it. The scrim runs 12% at the top to 86% at the text."""
    hexv = hexv.lstrip('#')
    out = []
    for i in (0, 2, 4):
        c = int(hexv[i:i + 2], 16)
        out.append(round(c * (1 - alpha)))
    return '#%02X%02X%02X' % tuple(out)


# ---------------------------------------------------------------------------
# THE THREE STYLES
#
# Each is a dict of the roles a map has to fill. The Google Maps JSON is
# generated from it below, so the two cannot disagree, and the preview draws
# from the same dict.
#
# The labelling policy is IDENTICAL in all three on purpose: locality names
# only, everything else off. These are heroes, not wayfinding — street names,
# business pins and transit lines are noise at 1200px behind a scrim, and
# keeping the policy fixed means the three differ by colour alone and can
# actually be compared. Turn labels back on in Snazzy Maps if you want them.
# ---------------------------------------------------------------------------
STYLES = [
    {
        'id': 'musubi-sumi',
        'name': 'Musubi Sumi',
        'jp': '墨',
        'blurb': 'Ink wash. One hue — Sanzo Wada Black — stepped from the ground '
                 'up to the arterials, and nothing else. The only colour in the '
                 'hero is then the yellow eyebrow and the yellow button, which '
                 'is how the rest of the site behaves.',
        'land':      BLACK,
        'water':     darken(DARK, 10),
        'park':      lighten(BLACK, 7),
        'building':  lighten(BLACK, 3),
        'highway':   lighten(BLACK, 30),
        'arterial':  lighten(BLACK, 20),
        'local':     lighten(BLACK, 11),
        'border':    lighten(BLACK, 16),
        'label':     lighten(BLACK, 55),
        'halo':      BLACK,
    },
    {
        'id': 'musubi-slate',
        'name': 'Musubi Slate',
        'jp': '青',
        'blurb': "Slate Color for the land and Vandar Poel's Blue for the water, "
                 'both straight from the dictionary, with the parks in a darkened '
                 'Greenish Glaucous. The most map-like of the three: it still '
                 'reads as a place rather than a graphic.',
        'land':      DARK,
        'water':     BLUE,
        'park':      darken(GLAUCOUS_G, 34),
        'building':  darken(DARK, 5),
        'highway':   lighten(DARK, 26),
        'arterial':  lighten(DARK, 15),
        'local':     lighten(DARK, 7),
        'border':    lighten(DARK, 12),
        'label':     lighten(GLAUCOUS_B, 8),
        'halo':      darken(DARK, 18),
    },
    {
        'id': 'musubi-kuroki',
        'name': 'Musubi Kuroki',
        'jp': '黒黄',
        'blurb': 'Black ground, yellow arterials. The site\'s own pairing put on '
                 'a map: unmistakably this dojo, and the boldest of the three. '
                 'Worth knowing that the yellow competes with the hero button, '
                 'which is also yellow.',
        'land':      BLACK,
        'water':     darken(BLUE, 9),
        'park':      darken(GREEN, 13),
        'building':  lighten(BLACK, 4),
        'highway':   YELLOW,
        # NEUTRAL, and this was decided by rendering it. The arterial was a
        # darkened Yellow, which looked fine on a synthetic map carrying two of
        # them and was unusable on Badalona, which has dozens: the whole frame
        # went yellow and there was nothing left for the motorways — or for the
        # hero button, which is also Yellow. The signature of this style is
        # yellow motorways on black, and it only reads if everything else is not
        # yellow.
        'arterial':  lighten(BLACK, 22),
        'local':     lighten(BLACK, 12),
        'border':    darken(RUST, 12),
        'label':     lighten(BLACK, 52),
        'halo':      BLACK,
    },
]


def to_google(st):
    """The Snazzy Maps / Google Maps JSON array for one style."""
    return [
        # ---- the ground -----------------------------------------------------
        {"featureType": "all", "elementType": "geometry",
         "stylers": [{"color": st['land']}]},
        {"featureType": "landscape.natural", "elementType": "geometry",
         "stylers": [{"color": st['land']}]},
        {"featureType": "landscape.man_made", "elementType": "geometry",
         "stylers": [{"color": st['building']}]},
        {"featureType": "water", "elementType": "geometry",
         "stylers": [{"color": st['water']}]},
        {"featureType": "poi.park", "elementType": "geometry",
         "stylers": [{"color": st['park']}]},
        {"featureType": "poi", "elementType": "geometry",
         "stylers": [{"color": st['park']}]},

        # ---- roads, in three weights ---------------------------------------
        {"featureType": "road.highway", "elementType": "geometry.fill",
         "stylers": [{"color": st['highway']}]},
        {"featureType": "road.highway", "elementType": "geometry.stroke",
         "stylers": [{"color": st['land']}]},
        {"featureType": "road.arterial", "elementType": "geometry.fill",
         "stylers": [{"color": st['arterial']}]},
        {"featureType": "road.arterial", "elementType": "geometry.stroke",
         "stylers": [{"visibility": "off"}]},
        {"featureType": "road.local", "elementType": "geometry.fill",
         "stylers": [{"color": st['local']}]},
        {"featureType": "road.local", "elementType": "geometry.stroke",
         "stylers": [{"visibility": "off"}]},

        # ---- the municipal boundary ----------------------------------------
        # ON, and it is the one piece of information a town hero owes the
        # reader: where Badalona stops and Sant Adrià starts.
        {"featureType": "administrative", "elementType": "geometry.stroke",
         "stylers": [{"color": st['border']}, {"weight": 1.2}]},
        {"featureType": "administrative.land_parcel", "elementType": "all",
         "stylers": [{"visibility": "off"}]},
        {"featureType": "administrative.neighborhood", "elementType": "all",
         "stylers": [{"visibility": "off"}]},

        # ---- labels ---------------------------------------------------------
        {"featureType": "all", "elementType": "labels",
         "stylers": [{"visibility": "off"}]},
        {"featureType": "administrative.locality", "elementType": "labels.text.fill",
         "stylers": [{"visibility": "on"}, {"color": st['label']}]},
        {"featureType": "administrative.locality", "elementType": "labels.text.stroke",
         "stylers": [{"visibility": "on"}, {"color": st['halo']}, {"weight": 3}]},
        {"featureType": "administrative.locality", "elementType": "labels.icon",
         "stylers": [{"visibility": "off"}]},

        # ---- everything a hero does not want -------------------------------
        {"featureType": "poi.business", "elementType": "all",
         "stylers": [{"visibility": "off"}]},
        {"featureType": "transit", "elementType": "all",
         "stylers": [{"visibility": "off"}]},
    ]


# ---------------------------------------------------------------------------
# The preview
# ---------------------------------------------------------------------------
def synthetic_map(st, uid):
    """A small invented city, drawn from the style's own roles.

    Deliberately NOT a real map: showing a fake Badalona would invite the
    reader to judge the geography instead of the palette, and the geography is
    Google's job. What this has to answer is how the six roles sit together.
    """
    return f'''
<svg class="mapsvg" viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice"
     role="img" aria-label="Synthetic map preview of the {st['name']} style">
  <rect width="400" height="300" fill="{st['land']}"/>
  <path d="M0 232 C 70 224, 120 250, 190 246 C 268 241, 320 262, 400 254 L400 300 L0 300 Z"
        fill="{st['water']}"/>
  <path d="M243 34 C 292 24, 330 46, 336 76 C 342 108, 306 128, 272 120 C 238 112, 226 62, 243 34 Z"
        fill="{st['park']}"/>
  <path d="M28 132 C 58 120, 84 134, 82 156 C 80 178, 44 186, 28 170 Z" fill="{st['park']}"/>
  <g fill="{st['building']}">
    <rect x="104" y="52" width="34" height="26"/><rect x="150" y="46" width="26" height="32"/>
    <rect x="104" y="92" width="26" height="30"/><rect x="146" y="96" width="34" height="24"/>
    <rect x="196" y="146" width="30" height="26"/><rect x="240" y="152" width="28" height="22"/>
    <rect x="60" y="196" width="34" height="22"/><rect x="112" y="192" width="26" height="28"/>
    <rect x="300" y="176" width="32" height="26"/><rect x="346" y="184" width="24" height="22"/>
  </g>
  <g stroke="{st['local']}" stroke-width="1.6" fill="none">
    <path d="M0 66 H400 M0 110 H400 M0 178 H400 M0 214 H400"/>
    <path d="M56 0 V232 M140 0 V240 M228 0 V246 M312 0 V250 M370 0 V252"/>
  </g>
  <g stroke="{st['arterial']}" stroke-width="3.2" fill="none">
    <path d="M0 140 H400"/><path d="M186 0 V244"/>
  </g>
  <path d="M-10 20 C 90 42, 150 96, 214 130 C 280 166, 340 190, 410 196"
        stroke="{st['highway']}" stroke-width="4.6" fill="none"/>
  <path d="M0 250 C 90 244, 150 236, 214 240 C 280 244, 330 236, 400 240"
        stroke="{st['border']}" stroke-width="1.2" stroke-dasharray="5 4" fill="none"/>
  <text x="196" y="96" text-anchor="middle" class="maplabel"
        fill="{st['label']}" stroke="{st['halo']}" stroke-width="3"
        paint-order="stroke">BADALONA</text>
</svg>'''


def build():
    os.makedirs(OUT_JSON, exist_ok=True)
    for st in STYLES:
        path = os.path.join(OUT_JSON, st['id'] + '.json')
        io.open(path, 'w', encoding='utf-8').write(
            json.dumps(to_google(st), indent=2, ensure_ascii=False) + '\n')

    cards = []
    for st in STYLES:
        roles = [('Land', 'land'), ('Water', 'water'), ('Parks', 'park'),
                 ('Built-up', 'building'), ('Motorway', 'highway'),
                 ('Arterial', 'arterial'), ('Streets', 'local'),
                 ('Boundary', 'border'), ('Label', 'label')]
        swatches = ''.join(
            '<li><i style="background:%s"></i><b>%s</b><code>%s</code></li>'
            % (st[k], nm, st[k].upper()) for nm, k in roles)

        # The two numbers that decide whether it works as a hero.
        top = over_black(st['land'], 0.12)
        bottom = over_black(st['land'], 0.86)
        r_white = ratio(WHITE, bottom)
        r_yellow = ratio(YELLOW, bottom)

        cards.append(f'''
<section class="card">
  <header class="card-h">
    <p class="jp">{st['jp']}</p>
    <h2>{st['name']}</h2>
    <p class="blurb">{st['blurb']}</p>
  </header>

  <div class="shots">
    <figure>
      <div class="plain">{synthetic_map(st, st['id'])}</div>
      <figcaption>The style on its own</figcaption>
    </figure>
    <figure>
      <div class="hero">
        {synthetic_map(st, st['id'] + '-h')}
        <div class="scrim"></div>
        <div class="hero-in">
          <p class="kick">BADALONA · AIKIDO MUSUBI</p>
          <h3>AIKIDO EN BADALONA</h3>
          <p class="line">De lunes a sábado, en el dojo. Aikido, iaijutsu, judo
            y karate, sin experiencia previa.</p>
          <p class="cta">
            <a class="btn">Ven a probar</a>
            <a class="btn btn2">Ver el horario</a>
            <small>Dos clases de prueba · inscripción gratuita</small>
          </p>
        </div>
      </div>
      <figcaption>Under the hero scrim, with the real furniture</figcaption>
    </figure>
  </div>

  <ul class="sw">{swatches}</ul>

  <p class="meas">Ground under the scrim: <code>{top}</code> at the top,
     <code>{bottom}</code> where the type sits. White on that measures
     <b>{r_white:.1f}:1</b>, the yellow button <b>{r_yellow:.1f}:1</b>.</p>

  <details>
    <summary>Google Maps / Snazzy Maps JSON — <code>{st['id']}.json</code></summary>
    <pre>{json.dumps(to_google(st), indent=2, ensure_ascii=False)}</pre>
  </details>
</section>''')

    # ---- the same three on real OpenStreetMap data ----------------------
    # The synthetic city above compares palettes. This compares STYLES, which
    # is not the same thing and is the comparison that actually decides it:
    # Badalona has dozens of arterials and two big wooded ranges, and both
    # facts changed the answer. Rendered by docs/mockups/src/build_maps_gl.py.
    real = []
    for st in STYLES:
        short = st['id'].split('-')[-1]
        real.append(f"""
  <figure class="real">
    <div class="hero">
      <img src="maps/samples/badalona-{short}.jpg" alt="Badalona in the {st['name']} style">
      <div class="scrim"></div>
      <div class="hero-in">
        <p class="kick">BADALONA · AIKIDO MUSUBI</p>
        <h3>AIKIDO EN BADALONA</h3>
        <p class="cta"><a class="btn">Ven a probar</a><a class="btn btn2">Ver el horario</a></p>
      </div>
      <p class="osm">© OpenStreetMap contributors</p>
    </div>
    <figcaption>{st['name']}</figcaption>
  </figure>""")

    realblock = ('<h2 class="h2">The three on real data</h2>'
                 '<p class="lede">Badalona, rendered through MapLibre over '
                 'OpenFreeMap tiles, under the hero scrim. Two things only this '
                 'view could say: <b>Kuroki\u2019s arterials had to go neutral</b> '
                 '\u2014 as a darkened yellow they swamped the frame and left '
                 'nothing for the motorways or the yellow button \u2014 and '
                 '<b>Slate is far greener here than the swatches suggest</b>, '
                 'because Collserola and the Serralada de Marina are most of the '
                 'picture.</p>'
                 '<div class="reals">' + ''.join(real) + '</div>')

    html = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Three map styles for the location heroes</title>
<style>
  :root { --ink:#111314; --mute:#5A686E; }
  * { box-sizing: border-box; }
  body { margin:0; background:#F7F7F5; color:#111314;
         font:15px/1.65 "Noto Sans",-apple-system,BlinkMacSystemFont,sans-serif; }
  .wrap { max-width: 1140px; margin: 0 auto; padding: 3rem 2rem 5rem; }
  h1 { font-size: 1.9rem; letter-spacing:.04em; text-transform:uppercase; margin:0 0 .6rem; }
  .lede { max-width: 43rem; color:#3D4A50; margin:0 0 1rem; }
  .note { max-width: 43rem; color:#3D4A50; font-size:.92rem;
          border-left:3px solid #FFF200; padding:.6rem 0 .6rem 1rem; margin:0 0 3rem; background:#fff; }
  .card { background:#fff; border:1px solid rgba(17,19,20,.12); padding:1.6rem; margin:0 0 2.4rem; }
  .card-h { max-width: 43rem; }
  .jp { margin:0; font-size:1.5rem; color:#AE5224; line-height:1; }
  .card h2 { margin:.3rem 0 .5rem; font-size:1.35rem; letter-spacing:.05em; text-transform:uppercase; }
  .blurb { margin:0 0 1.4rem; color:#3D4A50; font-size:.95rem; }
  .shots { display:grid; grid-template-columns:1fr 1fr; gap:1.4rem; }
  @media (max-width: 820px) { .shots { grid-template-columns:1fr; } }
  figure { margin:0; }
  figcaption { font-size:.72rem; letter-spacing:.14em; text-transform:uppercase;
               color:#5A686E; margin-top:.5rem; }
  .plain, .hero { position:relative; aspect-ratio: 4/3; overflow:hidden; background:#111314; }
  .mapsvg { position:absolute; inset:0; width:100%; height:100%; display:block; }
  .maplabel { font: 700 11px/1 "Noto Sans",sans-serif; letter-spacing:.18em; }
  .scrim { position:absolute; inset:0;
           background:linear-gradient(180deg, rgba(17,19,20,.12) 0%, rgba(17,19,20,.86) 78%); }
  .hero-in { position:absolute; inset:auto 0 0 0; padding:1.2rem 1.2rem 1.3rem; color:#fff; }
  .kick { margin:0; font-size:.55rem; letter-spacing:.2em; color:#FFF200; }
  .hero-in h3 { margin:.35rem 0 .45rem; font-size:1.45rem; line-height:1.1;
                letter-spacing:.04em; text-transform:uppercase; }
  .line { margin:0 0 .8rem; font-size:.78rem; line-height:1.55; color:rgba(255,255,255,.88); max-width:26rem; }
  .cta { display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; margin:0; }
  .btn { display:inline-block; padding:.5rem .95rem; background:#FFF200; color:#111314;
         font-size:.58rem; letter-spacing:.16em; text-transform:uppercase; }
  .btn2 { background:transparent; color:#fff; box-shadow:inset 0 0 0 1px rgba(255,255,255,.7); }
  .cta small { font-size:.62rem; color:#E4E6E7; }
  .sw { list-style:none; margin:1.4rem 0 0; padding:0; display:grid;
        grid-template-columns:repeat(auto-fill,minmax(158px,1fr)); gap:.4rem 1rem; }
  .sw li { display:flex; align-items:center; gap:.5rem; font-size:.78rem; }
  .sw i { width:1.05rem; height:1.05rem; flex:none; box-shadow:inset 0 0 0 1px rgba(17,19,20,.2); }
  .sw b { font-weight:600; }
  .sw code, .meas code { font:.72rem/1 ui-monospace,Menlo,monospace; color:#5A686E; }
  .meas { margin:1.1rem 0 0; font-size:.85rem; color:#3D4A50; }
  details { margin-top:1.1rem; }
  summary { cursor:pointer; font-size:.8rem; color:#AE5224; }
  pre { background:#111314; color:#E4E6E7; padding:1rem; overflow:auto; font-size:.72rem;
        line-height:1.5; max-height:22rem; }
  .h2 { font-size:1.35rem; letter-spacing:.05em; text-transform:uppercase; margin:3rem 0 .6rem; }
  .reals { display:grid; grid-template-columns:repeat(3,1fr); gap:1.2rem; margin-top:1.6rem; }
  @media (max-width: 900px) { .reals { grid-template-columns:1fr; } }
  .real { margin:0; }
  .real .hero { position:relative; aspect-ratio:4/3; overflow:hidden; background:#111314; }
  .real img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
  .osm { position:absolute; right:.4rem; bottom:.3rem; margin:0; font-size:.5rem;
         color:rgba(255,255,255,.7); }
</style></head><body><div class="wrap">
<h1>Three map styles for the location heroes</h1>
<p class="lede">Sanzo Wada dictionary entries where a colour is chosen, and
LESS-style <code>darken</code>/<code>lighten</code> of those entries where a
ramp is needed &mdash; the rule <code>styles/base.less</code> already follows.
Each is shown on its own and again behind the real <code>.lo-hero</code> scrim
with the real furniture, because the second is the only view that matters.</p>
<p class="note"><b>The synthetic city is not Badalona.</b> Drawing a fake one
would invite you to judge the geography instead of the palette, and the
geography is Google&rsquo;s. Paste the JSON into
<code>snazzymaps.com/editor</code> to see each style on the real place.</p>
''' + '\n'.join(cards) + realblock + '''
</div></body></html>
'''
    io.open(OUT_HTML, 'w', encoding='utf-8').write(html)
    print('wrote %s' % os.path.relpath(OUT_HTML, ROOT))
    for st in STYLES:
        print('      %s' % os.path.relpath(os.path.join(OUT_JSON, st['id'] + '.json'), ROOT))


if __name__ == '__main__':
    build()
