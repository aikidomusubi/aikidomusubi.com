#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Three ways to show the new venue photographs on /barcelona/ and
/sant-adria-de-besos/, for approval before anything is built.

THE BRIEF, AND THE PROBLEM IN IT. Two sets of photographs taken on 5 October
2026: the rooms empty, and two instructors (Dani and Elia) training in them.
The rooms are new to the association, so there is no photograph yet of a full
class, and several of the training shots are two people in a large empty room.
Printed whole, that reads as "nobody comes here".

The photographs are NOT edited. Every crop is done in CSS: the <img> fills its
<figure>, `object-position` picks the focal point, and `transform: scale()`
around that same point pushes the empty floor and ceiling outside the frame.
The file stays whole, so the day there is a better photograph of a full class,
the crop is one line of data and not a re-export.

    python3 docs/mockups/src/build_venuephotos.py

Writes docs/mockups/venue-photos.html. The photographs it reads are web copies
in docs/mockups/venuephotos/, named by contact-sheet id (E = Espronceda,
M = Marina-Besòs); the originals are in temp/ and are not in git.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, 'docs', 'mockups', 'venue-photos.html')
IMG = 'venuephotos/'  # relative: works from docs/mockups/ and from <dest>/mockups/

# id -> (focus x %, focus y %, zoom). The focal point is where the people are;
# the zoom is how much of the empty room is pushed outside the frame.
F = {
    'E01': (42, 44, 2.3),  # the pair, far away in the whole room
    'E02': (55, 80, 1.0),  # overhead: hands and a jō, the jō at the bottom
    'E03': (50, 34, 1.0),  # the pair, close, standing
    'E04': (62, 52, 1.25), # a throw, mid-air
    'E05': (50, 58, 1.0),  # the corridor to the room
    'E06': (40, 70, 1.9),  # the room with the clock, a fall bottom-left
    'E08': (56, 58, 1.2),  # a pin on the mat
    'E10': (58, 50, 1.15), # a throw, low angle
    'M02': (50, 42, 1.0),  # Elia pinning, portrait
    'M03': (50, 55, 1.0),  # the room, empty
    'M04': (50, 55, 1.0),  # the room, empty, the other wall
    'M05': (60, 62, 2.0),  # a throw, small in the room
    'M07': (40, 40, 1.05), # Elia close
    'M09': (52, 60, 1.15), # a throw, mid-air
    'M10': (64, 62, 1.6),  # a fall, Dani standing
    'M14': (42, 56, 1.4),  # Dani with a jō, mirror behind
    'M15': (50, 44, 1.0),  # Dani, jō strike, facing the camera
    'M19': (50, 50, 1.0),  # Dani's hands, close
}

def fig(pid, cap='', cls='', style='', x=None, y=None, z=None):
    fx, fy, fz = F[pid]
    if x is not None: fx = x
    if y is not None: fy = y
    if z is not None: fz = z
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    return (f'<figure class="vp {cls}" style="--x:{fx}%;--y:{fy}%;--z:{fz};{style}">'
            f'<span class="vp-f"><img src="{IMG}{pid}.jpg" alt="" loading="lazy"></span>{c}</figure>')

# ---- copy, in Spanish as the page would carry it --------------------------
B = {  # Barcelona page, Espronceda only (the UB has its own photographs already)
    'lab': 'El espacio por dentro',
    'h':   'CxEM Espronceda, por dentro',
    'room': 'La sala de tatami',
    'way':  'El pasillo que lleva a la sala',
    'pair': 'Práctica por parejas',
    'throw': 'Una proyección',
    'pin':  'Una inmovilización',
    'jo':   'Trabajo con jō',
    'fall': 'Ukemi, la caída',
}
S = {  # Sant Adrià page, Marina-Besòs
    'lab': 'El espacio por dentro',
    'h':   'Marina-Besòs, por dentro',
    'room': 'La sala de tatami',
    'room2': 'Espejos y luz natural',
    'pair': 'Práctica por parejas',
    'throw': 'Una proyección',
    'pin':  'Una inmovilización',
    'jo':   'Trabajo con jō',
    'hands': 'Detalle: el agarre',
    'fall': 'Ukemi, la caída',
}

def section(t, inner):
    return (f'<section class="lo-sec"><p class="lo-lab">{t["lab"]}</p>'
            f'<h2>{t["h"]}</h2>{inner}</section>')

# ---- proposal 1: the mosaic -----------------------------------------------
def mosaic_b():
    return ('<div class="m1">'
            + fig('E03', B['pair'], 't1')
            + fig('E06', B['fall'], 't2')
            + fig('E02', B['jo'], 't3')
            + fig('E08', B['pin'], 't4')
            + fig('E05', B['way'], 't5')
            + '</div>')

def mosaic_s():
    return ('<div class="m1">'
            + fig('M15', S['jo'], 't1')
            + fig('M03', S['room'], 't2')
            + fig('M19', S['hands'], 't3')
            + fig('M09', S['throw'], 't4', z=1.35)
            + fig('M02', S['pin'], 't5', y=46)
            + '</div>')

# ---- proposal 2: the strip --------------------------------------------------
def strip(items):
    tiles = ''.join(fig(p, cap, 'w-' + w, **kw) for p, cap, w, kw in items)
    n = len(items)
    return (f'<div class="m2"><div class="m2-track" tabindex="0" '
            f'aria-label="Fotografías, desliza para ver más">{tiles}</div>'
            f'<div class="m2-ctl"><button type="button" class="m2-prev" aria-label="Anterior">←</button>'
            f'<span class="m2-n">1 / {n}</span>'
            f'<button type="button" class="m2-next" aria-label="Siguiente">→</button></div></div>')

def strip_b():
    return strip([
        ('E05', B['way'],  'p', {}),
        ('E01', B['room'], 'l', {'z': 1.5, 'y': 46}),
        ('E03', B['pair'], 'p', {}),
        ('E04', B['throw'], 'l', {}),
        ('E02', B['jo'],   'p', {}),
        ('E08', B['pin'],  'l', {}),
        ('E06', B['fall'], 'l', {}),
    ])

def strip_s():
    return strip([
        ('M04', S['room2'], 'l', {}),
        ('M09', S['throw'], 'l', {}),
        ('M02', S['pin'],   'p', {}),
        ('M15', S['jo'],    'p', {}),
        ('M05', S['throw'], 'l', {}),
        ('M19', S['hands'], 'p', {}),
        ('M10', S['fall'],  'l', {}),
        ('M07', S['pair'],  'p', {}),
    ])

# ---- proposal 3: the room, then the practice --------------------------------
def dip(room, room_cap, room_note, quad, room_kw=None):
    room_kw = room_kw or {}
    q = ''.join(fig(p, cap, '', **kw) for p, cap, kw in quad)
    return (f'<div class="m3"><div class="m3-room">'
            f'<p class="m3-tag">El espacio</p>{fig(room, room_cap, "", **room_kw)}'
            f'<p class="m3-note">{room_note}</p></div>'
            f'<div class="m3-prac"><p class="m3-tag">La práctica</p><div class="m3-q">{q}</div></div></div>')

def dip_b():
    return dip('E01', B['room'],
               'La sala de tatami del Complejo Deportivo Municipal Espronceda, donde entrenamos los lunes y los miércoles.',
               [('E03', B['pair'], {'z': 1.35, 'y': 30}),
                ('E04', B['throw'], {'z': 1.5}),
                ('E08', B['pin'], {'z': 1.45}),
                ('E02', B['jo'], {'z': 1.2})],
               {'z': 1.45, 'y': 46})

def dip_s():
    return dip('M03', S['room'],
               'Una sala amplia dentro del polideportivo, con espejos y luz natural.',
               [('M15', S['jo'], {'z': 1.3, 'y': 40}),
                ('M09', S['throw'], {'z': 1.4}),
                ('M19', S['hands'], {'z': 1.1}),
                ('M02', S['pin'], {'z': 1.3, 'y': 44})])

CSS = r'''
html, body { background: #fff; height: auto; min-height: 100%; }
/* the strip bleeds to the viewport edge; on the site that is .full-bleed() in base.less */
.mk { overflow-x: clip; }
.mk { max-width: 72rem; margin: 0 auto; padding: 2.4rem 1rem 5rem; font-size: 1rem; }
.mk-intro h1 { font-family: Futura, 'Noto Sans', sans-serif; font-size: 2rem; margin: 0 0 .5rem; }
.mk-intro p, .mk-why p, .mk-why li { max-width: 46rem; color: #34454C; line-height: 1.55; }
.mk-bar { position: sticky; top: 0; z-index: 30; background: #fff; border-bottom: 1px solid #ddd;
          display: flex; flex-wrap: wrap; gap: .6rem 1.4rem; align-items: center; padding: .7rem 1rem; }
.mk-bar b { font-family: Futura, sans-serif; font-weight: 500; font-size: .74rem; letter-spacing: .12em; text-transform: uppercase; color: #34454C; }
.mk-bar button { font: 500 .8rem/1 Futura, sans-serif; letter-spacing: .06em; border: 1.5px solid #111314; background: #fff; padding: .45rem .7rem; cursor: pointer; }
.mk-bar button[aria-pressed="true"] { background: #111314; color: #FFF200; }
.mk-bar a { color: #064F6E; font-size: .9rem; }
.mk-p { margin-top: 4rem; border-top: 4px solid #111314; padding-top: 1rem; }
.mk-p > h2 { font-family: Futura, sans-serif; font-size: 1.6rem; margin: 0; }
.mk-p > h2 small { font-size: .7rem; letter-spacing: .12em; text-transform: uppercase; border: 1px solid #1A7444; color: #1A7444; padding: .15rem .4rem; vertical-align: .3em; margin-left: .5rem; }
.mk-why { margin: .6rem 0 0; }
.mk-why ul { padding-left: 1.2rem; margin: .4rem 0; }
.mk-town { margin: 2rem 0 0; font: 500 .75rem/1 Futura, sans-serif; letter-spacing: .14em; text-transform: uppercase; color: #ae5224; }
/* the sample sits inside the site's own page shell, so .lo-sec, .lo-lab and
   the h2 render exactly as they do on /barcelona/ */
.mk .page { position: static; }
.mk .sample { border: 1px dashed #c9d1d3; margin-top: .6rem; }
.mk .sample .container > main { padding-top: 0; padding-bottom: 1.5rem; }

/* ---- the crop: the file is whole, the frame decides what shows ---- */
figure.vp { position: relative; margin: 0; }
figure.vp .vp-f { position: absolute; inset: 0; overflow: hidden; background: #1d2122; isolation: isolate; }
figure.vp img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;
                object-position: var(--x) var(--y); transform: scale(var(--z, 1));
                transform-origin: var(--x) var(--y); transition: filter .2s; }
figure.vp figcaption { position: absolute; left: 0; right: 0; bottom: 0; z-index: 2;
                padding: 2.2rem .8rem .6rem; color: #fff;
                font: 500 .72rem/1.3 Futura, 'Noto Sans', sans-serif; letter-spacing: .1em; text-transform: uppercase;
                background: linear-gradient(to top, rgba(17,19,20,.72), rgba(17,19,20,0)); }

/* ---- the four grades ---- */
body.g-0 figure.vp img { filter: none; }
body.g-a figure.vp img { filter: saturate(.86) contrast(1.06) sepia(.09); }
body.g-b figure.vp img { filter: saturate(.68) sepia(.18) contrast(1.08) brightness(1.03); }
body.g-c figure.vp img { filter: saturate(.55) contrast(1.1) brightness(1.06); }
body.g-c figure.vp .vp-f::after { content: ""; position: absolute; inset: 0; z-index: 1; pointer-events: none;
                background: #34454C; mix-blend-mode: soft-light; opacity: .55; }

/* ---- 1 · mosaic ---- */
.m1 { display: grid; gap: .5rem; grid-template-columns: repeat(6, 1fr); grid-template-rows: repeat(3, 9.5rem); }
.m1 .t1 { grid-column: 1 / 4; grid-row: 1 / 4; }
.m1 .t2 { grid-column: 4 / 7; grid-row: 1 / 3; }
.m1 .t3 { grid-column: 4 / 5; grid-row: 3; }
.m1 .t4 { grid-column: 5 / 6; grid-row: 3; }
.m1 .t5 { grid-column: 6 / 7; grid-row: 3; }
@media (max-width: 767px) {
  .m1 { grid-template-columns: 1fr 1fr; grid-template-rows: 14rem 10rem 10rem; }
  .m1 .t1 { grid-column: 1 / 3; grid-row: 1; }
  .m1 .t2 { grid-column: 1 / 3; grid-row: 2; }
  .m1 .t3 { grid-column: 1; grid-row: 3; } .m1 .t4 { grid-column: 2; grid-row: 3; }
  .m1 .t5 { display: none; }
}

/* ---- 2 · strip ---- */
.m2-track { display: flex; gap: .5rem; overflow-x: auto; scroll-snap-type: x mandatory;
            scrollbar-width: none; margin-right: calc(50% - 50vw); padding-right: 2rem; }
.m2-track::-webkit-scrollbar { display: none; }
.m2-track figure.vp { flex: none; height: 24rem; scroll-snap-align: start; }
.m2-track .w-p { width: 18rem; } .m2-track .w-l { width: 34rem; }
.m2-track figure.vp { display: flex; flex-direction: column; }
.m2-track figure.vp .vp-f { position: relative; flex: 1; }
.m2-track figure.vp figcaption { background: none; position: static; color: #34454C; padding: .5rem 0 0; }
.m2-ctl { display: flex; align-items: center; gap: 1rem; margin-top: .9rem; }
.m2-ctl button { width: 2.6rem; height: 2.6rem; border: 1.5px solid #111314; background: #fff; font-size: 1.1rem; cursor: pointer; }
.m2-ctl button:focus-visible, .m2-track:focus-visible { outline: 3px solid #064F6E; outline-offset: 2px; }
.m2-n { font: 500 .8rem/1 Futura, sans-serif; letter-spacing: .1em; font-variant-numeric: tabular-nums; }
@media (max-width: 767px) {
  .m2-track figure.vp { height: 17rem; } .m2-track .w-p { width: 12.5rem; } .m2-track .w-l { width: 21rem; }
}

/* ---- 3 · the room, then the practice ---- */
.m3 { display: grid; grid-template-columns: 7fr 5fr; gap: 1.6rem; align-items: start; }
.m3-tag { font: 500 .72rem/1 Futura, sans-serif !important; letter-spacing: .16em; text-transform: uppercase;
          color: #ae5224 !important; margin: 0 0 .6rem !important; max-width: none !important; }
.m3-room figure.vp { aspect-ratio: 4 / 3; }
.m3-note { font-size: .92rem !important; color: #34454C !important; margin: .7rem 0 0 !important; max-width: none !important; }
.m3-q { display: grid; grid-template-columns: 1fr 1fr; gap: .5rem; }
.m3-q figure.vp { aspect-ratio: 1; }
.m3-q figure.vp figcaption { font-size: .62rem; padding: 1.6rem .6rem .5rem; }
@media (max-width: 767px) { .m3 { grid-template-columns: 1fr; } }
'''

JS = r'''
document.querySelectorAll('[data-grade]').forEach(function (b) {
  b.addEventListener('click', function () {
    document.body.className = document.body.className.replace(/\bg-\w\b/, '') + ' g-' + b.dataset.grade;
    document.querySelectorAll('[data-grade]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
  });
});
document.querySelectorAll('.m2').forEach(function (m) {
  var t = m.querySelector('.m2-track'), n = m.querySelector('.m2-n'), items = t.children;
  function idx() { var best = 0, d = 1e9; for (var i = 0; i < items.length; i++) { var k = Math.abs(items[i].offsetLeft - t.scrollLeft); if (k < d) { d = k; best = i; } } return best; }
  function go(k) { k = Math.max(0, Math.min(items.length - 1, k)); t.scrollTo({ left: items[k].offsetLeft, behavior: 'smooth' }); }
  m.querySelector('.m2-prev').onclick = function () { go(idx() - 1); };
  m.querySelector('.m2-next').onclick = function () { go(idx() + 1); };
  t.addEventListener('scroll', function () { n.textContent = (idx() + 1) + ' / ' + items.length; }, { passive: true });
});
'''

def sample(inner):
    return f'<div class="sample"><div class="page"><div class="container"><main>{inner}</main></div></div></div>'

def proposal(n, name, rec, why, b_html, s_html):
    tag = ' <small>Recommended</small>' if rec else ''
    return (f'<div class="mk-p" id="p{n}"><h2>{n} · {name}{tag}</h2><div class="mk-why">{why}</div>'
            f'<p class="mk-town">/barcelona/ · CxEM Espronceda</p>{sample(section(B, b_html))}'
            f'<p class="mk-town">/sant-adria-de-besos/ · Marina-Besòs</p>{sample(section(S, s_html))}</div>')

WHY1 = '''<p><b>An editorial mosaic, five photographs, no interaction.</b> One tall
photograph of people carries the block; the room and three details sit beside
it. Every tile is a crop chosen for it, so the two people fill their frame and
the empty floor stays outside. On a phone it becomes two columns and drops the
fifth tile.</p><ul><li>Fastest to read, no JavaScript, nothing to operate.</li>
<li>Shows five of the photographs; the rest wait for a lightbox (GLightbox is
already self-hosted for the seminars page) or stay unpublished.</li></ul>'''

WHY2 = '''<p><b>A strip that runs off the right edge of the page.</b> Portraits and
landscapes keep their own shapes at one height, the strip snaps to each
photograph, and the arrows and the count make it operable with a keyboard. It
opens on the room, then the practice.</p><ul><li>Shows seven or eight
photographs in the height of one.</li><li>The cost: what is off-screen is easy
to never see, and it is the one proposal with a control to build and test
(keyboard, screen reader, reduced motion).</li></ul>'''

WHY3 = '''<p><b>The room as the room, the people as details.</b> The empty room is
not a weakness to hide, it is the answer to "what is this place like", so it
gets the large frame and a label that says so. The training photographs are
cropped square and tight, on hands, faces and the top of a throw, where two
people look like a practice and not like an empty hall.</p><ul><li>Solves the
"two people in a large room" problem by design rather than by luck of
cropping.</li><li>Survives the day there are photographs of a full class: the
quad simply gets better pictures.</li><li>Five photographs, no JavaScript.</li></ul>'''

SEO = '''<div class="mk-p" id="seo"><h2>Search and images, whichever is chosen</h2>
<div class="mk-why"><ul>
<li><b>Real &lt;img&gt; elements</b>, never CSS backgrounds: a background image is invisible to Google Images.</li>
<li><b>Descriptive file names</b> under the site convention, e.g. <code>access-information-NdxqmVbV-cxem-espronceda-practice-01.jpg</code> and <code>.webp</code>, generated at 480/800/base by <code>tools/image-widths.py</code>.</li>
<li><b>Alt text in four languages</b> that says what is in the photograph and where ("Dos aikidokas practican una proyección en la sala de tatami del CxEM Espronceda, Barcelona"), plus the short visible caption.</li>
<li><b>width and height</b> on every image (from <code>_data/imgdim.yml</code>) so nothing shifts, <code>loading="lazy"</code> on all of them since they sit below the fold.</li>
<li><b><code>sizes</code> multiplied by the zoom.</b> A tile drawn at 300px with a 1.5x crop needs a 450px file; a <code>sizes</code> that ignores the zoom fetches one size too small and the crop goes soft.</li>
<li><b>The photographs join the sitemap's image entries</b> for the page they appear on, and the venue's schema.org <code>Place</code> gets a <code>photo</code> list of <code>ImageObject</code>s with <code>creditText</code>, <code>creator</code> and <code>copyrightNotice</code>, which is what Google Images uses for its "Licensable" details.</li>
<li><b>One list in data, not in templates:</b> the photographs, their focal points and their alt texts live once in <code>_data/venues.yml</code> under each venue, so the town page and the new venue page read the same list and cannot drift.</li>
</ul></div></div>'''

def main():
    html = f'''<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mockup · Venue photographs</title>
<link rel="stylesheet" href="/styles/all.min.css">
<link rel="stylesheet" href="/styles/locations.min.css">
<style>{CSS}</style></head>
<body class="g-b">
<div class="mk-bar"><b>Colour grade</b>
<button type="button" data-grade="0" aria-pressed="false">None</button>
<button type="button" data-grade="a" aria-pressed="false">A · the site's venue grade</button>
<button type="button" data-grade="b" aria-pressed="true">B · warm, desaturated</button>
<button type="button" data-grade="c" aria-pressed="false">C · slate wash</button>
<a href="#p1">1 Mosaic</a><a href="#p2">2 Strip</a><a href="#p3">3 Room and practice</a><a href="#seo">SEO</a></div>
<div class="mk">
<div class="mk-intro"><h1>The new photographs on /barcelona/ and /sant-adria-de-besos/</h1>
<p>Three layouts for one new section, placed after "Dónde entrenamos". Each is
shown on both pages with the real section heading and styles. <b>No photograph
is edited:</b> every crop is CSS on the whole file, a focal point plus a zoom,
so the empty part of a large room stays outside the frame and the file can be
re-cropped later in one line of data.</p>
<p><b>The colour grade</b> at the top applies to everything. Espronceda is a
black room under cold light and Marina-Besòs is pink tatami and orange brick,
so one filter has to pull a cold and a warm set towards each other. B is my
recommendation: it takes the pink down to a dusty rose and gives the black room
some warmth, and the two pages then read as one association. A is the grade the
site already uses on its venue cards, and is too weak for the pink. C is the
strongest and the most "designed".</p></div>
{proposal(1, 'Mosaic', False, WHY1, mosaic_b(), mosaic_s())}
{proposal(2, 'Strip', False, WHY2, strip_b(), strip_s())}
{proposal(3, 'The room, then the practice', True, WHY3, dip_b(), dip_s())}
{SEO}
</div>
<script>{JS}</script>
</body></html>
'''
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write(html)
    print('wrote', os.path.relpath(OUT, ROOT))

if __name__ == '__main__':
    main()
