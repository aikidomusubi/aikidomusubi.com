# -*- coding: utf-8 -*-
"""EL REGISTRO — the dark document. Shared by the panel and the standalone page.

Everything in here is the *evidence* behind a claim the light home makes.
The home says "eighteen years"; the record shows the eighteen years.
"""
import _data

PY, TY, ROWS = _data.gallery()
EV = _data.events()

CSS = r"""
/* ── EL REGISTRO ──────────────────────────────────────────────────────────
   A document, not a page. Fixed measure, numbered sections, a colophon.
   Everything is scoped under .rg so the site's prose rules never reach it. */
.rg{--fg:#d5dadc;--hi:#fff;--mute:#9aa2a5;--line:rgba(255,255,255,.13);
    --acc:#FFF200;--bg:#111314;
    background:var(--bg);color:var(--fg);
    font-family:'Noto Sans',system-ui,sans-serif;font-size:16px;line-height:1.6;
    -webkit-font-smoothing:antialiased}
.rg *{box-sizing:border-box}
.rg a{color:inherit;text-decoration:none}
.rg h1,.rg h2,.rg h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
    color:var(--hi);margin:0;letter-spacing:.02em}
.rg p{margin:0}
.rg-w{max-width:1140px;margin:0 auto;padding:0 6rem}
@media(max-width:991.98px){.rg-w{padding:0 4rem}}
@media(max-width:767.98px){.rg-w{padding:0 2rem}}
.rg-mono{font-family:ui-monospace,'SF Mono',Menlo,monospace;font-variant-numeric:tabular-nums}

/* ── document masthead ─────────────────────────────────────────────────── */
.rg-mast{position:sticky;top:0;z-index:5;background:rgba(17,19,20,.94);
    backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.rg-mast-in{display:flex;align-items:center;gap:1.4rem;padding:.85rem 0;min-height:3.4rem}
.rg-seal{font-family:'Noto Sans JP','Noto Sans',sans-serif;font-size:1.35rem;color:var(--hi);
    line-height:1;letter-spacing:.08em}
.rg-mast .ttl{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.72rem;
    letter-spacing:.34em;text-transform:uppercase;color:var(--hi)}
.rg-mast .ed{margin-left:auto;font-size:.66rem;letter-spacing:.1em;color:var(--mute);
    text-transform:uppercase}
.rg-x{width:2.3rem;height:2.3rem;border:1px solid var(--line);background:none;color:var(--fg);
    display:grid;place-items:center;cursor:pointer;font-size:1rem;line-height:1;flex:0 0 auto}
.rg-x:hover{background:var(--acc);color:#111314;border-color:var(--acc)}
.rg-x:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
@media(max-width:575.98px){.rg-mast .ed{display:none}.rg-x{margin-left:auto}}

/* ── section scaffolding ───────────────────────────────────────────────── */
.rg-s{border-top:1px solid var(--line);padding:3.4rem 0}
.rg-s:first-of-type{border-top:0}
.rg-head{display:grid;grid-template-columns:4rem 1fr;gap:1.6rem;margin-bottom:2rem;align-items:start}
.rg-no{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.72rem;letter-spacing:.18em;
    color:var(--acc);padding-top:.45rem}
.rg-head h2{font-size:1.5rem;line-height:1.2}
.rg-head .sub{font-size:.85rem;color:var(--mute);margin-top:.4rem;max-width:52ch}
@media(max-width:575.98px){.rg-head{grid-template-columns:1fr;gap:.5rem}.rg-no{padding:0}}

/* ── 00 identity ───────────────────────────────────────────────────────── */
.rg-id{display:grid;grid-template-columns:auto 1fr;gap:3.4rem;align-items:center;
    padding:4.6rem 0 3.6rem}
.rg-kanji{font-family:'Noto Sans JP','Noto Sans',sans-serif;font-size:7.5rem;line-height:.9;
    color:var(--hi);letter-spacing:.06em}
.rg-kanji small{display:block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
    letter-spacing:.42em;color:var(--acc);margin-top:1.3rem;line-height:1}
.rg-gloss{max-width:42ch}
.rg-gloss p{font-size:1.06rem;line-height:1.65;color:#e4e8ea}
.rg-gloss p+p{margin-top:.9rem;font-size:.88rem;color:var(--mute)}
@media(max-width:767.98px){.rg-id{grid-template-columns:1fr;gap:1.8rem;padding:3rem 0 2.4rem}
    .rg-kanji{font-size:4.8rem}}

/* ── 01 the week ───────────────────────────────────────────────────────── */
.rg-now{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;padding:.95rem 1.1rem;
    border:1px solid var(--line);margin-bottom:1.8rem}
.rg-dot{width:.5rem;height:.5rem;border-radius:50%;background:#E2625E;flex:0 0 auto;
    box-shadow:0 0 0 0 rgba(226,98,94,.6);animation:rgp 2.2s infinite}
@keyframes rgp{70%{box-shadow:0 0 0 .6rem rgba(226,98,94,0)}100%{box-shadow:0 0 0 0 rgba(226,98,94,0)}}
.rg-now .l{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;letter-spacing:.2em;
    text-transform:uppercase;color:var(--mute)}
.rg-now .w{color:var(--hi);font-weight:700;font-size:.98rem}
.rg-now .t{color:var(--mute);font-size:.85rem}
.rg-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:2px;border:1px solid var(--line)}
.rg-day{background:rgba(255,255,255,.02);padding:.7rem .55rem 1rem;min-height:11rem}
.rg-day>.d{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.6rem;letter-spacing:.14em;
    text-transform:uppercase;color:var(--mute);margin-bottom:.7rem}
.rg-day[data-today]{background:rgba(255,242,0,.06)}
.rg-day[data-today]>.d{color:var(--acc)}
.rg-cl{border-left:2px solid var(--c);padding:.25rem 0 .3rem .45rem;margin-bottom:.5rem}
.rg-cl b{display:block;color:var(--hi);font-size:.75rem;font-weight:400}
.rg-cl span{display:block;color:var(--mute);font-size:.66rem}
.rg-empty{color:#8b9497;font-size:.7rem}
@media(max-width:991.98px){.rg-grid{grid-template-columns:repeat(4,1fr)}}
@media(max-width:575.98px){.rg-grid{grid-template-columns:repeat(2,1fr)}.rg-day{min-height:0}}
.rg-tot{display:flex;gap:2.4rem;flex-wrap:wrap;margin-top:1.4rem;padding-top:1.2rem;
    border-top:1px solid var(--line)}
.rg-tot div{min-width:0}
.rg-tot b{display:block;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.7rem;
    color:var(--hi);line-height:1}
.rg-tot span{font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:var(--mute)}

/* ── 02 lineage ────────────────────────────────────────────────────────── */
.rg-node{display:grid;grid-template-columns:8.5rem 1fr auto;gap:1.6rem;padding:.95rem .8rem;
    border-top:1px solid rgba(255,255,255,.08);align-items:baseline}
.rg-node:last-child{border-bottom:1px solid rgba(255,255,255,.08)}
.rg-node .y{font-size:.7rem;letter-spacing:.08em;color:var(--mute)}
.rg-node .n{color:var(--hi);font-size:1.02rem}
.rg-node .n small{display:block;color:var(--mute);font-size:.78rem;margin-top:.15rem}
.rg-node .g{font-size:.68rem;color:var(--mute);text-align:right;white-space:nowrap}
.rg-node[data-us]{background:rgba(255,242,0,.07)}
.rg-node[data-us] .n,.rg-node[data-us] .g{color:var(--acc)}
@media(max-width:767.98px){.rg-node{grid-template-columns:1fr;gap:.15rem}.rg-node .g{text-align:left}}

/* ── 03 eighteen years ─────────────────────────────────────────────────── */
.rg-bars{display:flex;align-items:flex-end;gap:4px;height:150px;
    border-bottom:1px solid rgba(255,255,255,.2)}
.rg-bars>div{flex:1;display:flex;flex-direction:column;justify-content:flex-end;height:100%}
.rg-bars i{display:block;background:rgba(255,255,255,.22);min-height:2px}
.rg-bars>div:hover i{background:var(--acc)}
.rg-xax{display:flex;gap:4px;padding-top:.55rem}
.rg-xax>span{flex:1;text-align:center;font-size:.58rem;color:var(--mute);letter-spacing:.02em}
.rg-note{margin-top:1.3rem;font-size:.82rem;color:var(--mute);max-width:56ch}
@media(max-width:767.98px){.rg-xax>span:nth-child(2n){visibility:hidden}}

/* ── 04 archive ────────────────────────────────────────────────────────── */
.rg-sheet{display:grid;grid-template-columns:repeat(12,1fr);gap:2px}
.rg-sheet a{aspect-ratio:1;overflow:hidden;background:#1b1e1f;display:block}
.rg-sheet img{width:100%;height:100%;object-fit:cover;filter:grayscale(1) contrast(1.05);
    opacity:.72;transition:filter .25s,opacity .25s}
.rg-sheet a:hover img{filter:none;opacity:1}
@media(max-width:991.98px){.rg-sheet{grid-template-columns:repeat(8,1fr)}}
@media(max-width:575.98px){.rg-sheet{grid-template-columns:repeat(4,1fr)}}
.rg-legend{display:flex;gap:2rem;flex-wrap:wrap;margin-top:1.4rem;padding-top:1.2rem;
    border-top:1px solid var(--line)}
.rg-legend b{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.5rem;color:var(--hi);
    display:block;line-height:1}
.rg-legend span{font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:var(--mute)}

/* ── 05 seminar log ────────────────────────────────────────────────────── */
.rg-log{width:100%;border-collapse:collapse;font-size:.85rem}
.rg-log th{text-align:left;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
    font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;color:var(--mute);
    padding:0 .8rem .7rem 0;border-bottom:1px solid var(--line)}
.rg-log td{padding:.55rem .8rem .55rem 0;border-bottom:1px solid rgba(255,255,255,.06);
    vertical-align:baseline}
.rg-log tr:hover td{background:rgba(255,255,255,.035)}
.rg-log .dt{color:var(--mute);white-space:nowrap;font-size:.78rem;width:6.5rem}
.rg-log .nm{color:var(--hi)}
.rg-log tr[data-next] .nm{color:var(--acc)}
.rg-log tr[data-next] .dt{color:var(--acc)}
.rg-more{margin-top:1.2rem;font-size:.78rem;color:var(--mute)}
.rg-yr{padding-top:1.6rem !important;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
    font-size:.68rem;letter-spacing:.2em;color:var(--acc)}
@media(max-width:575.98px){.rg-log .gr{display:none}}

/* ── 06 the three mats ─────────────────────────────────────────────────── */
.rg-ven{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem}
.rg-ven figure{margin:0}
.rg-ven img{width:100%;aspect-ratio:1;object-fit:cover;display:block;filter:grayscale(.35)}
.rg-ven b{display:block;color:var(--hi);margin-top:.8rem;font-size:.95rem}
.rg-ven small{display:block;color:var(--mute);font-size:.76rem;margin-top:.15rem;line-height:1.5}
@media(max-width:767.98px){.rg-ven{grid-template-columns:1fr}}

/* ── 07 grades & affiliation ───────────────────────────────────────────── */
.rg-two{display:grid;grid-template-columns:1.15fr 1fr;gap:3.4rem}
@media(max-width:767.98px){.rg-two{grid-template-columns:1fr;gap:2.2rem}}
.rg-dl{display:grid;grid-template-columns:auto 1fr;gap:.5rem 1.6rem;font-size:.85rem}
.rg-dl dt{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;letter-spacing:.16em;
    text-transform:uppercase;color:var(--mute);padding-top:.18rem}
.rg-dl dd{margin:0;color:var(--fg);line-height:1.5}
.rg-rank{border-top:1px solid rgba(255,255,255,.08);padding:.6rem 0;display:flex;
    justify-content:space-between;gap:1rem;font-size:.88rem}
.rg-rank:last-child{border-bottom:1px solid rgba(255,255,255,.08)}
.rg-rank .p{color:var(--hi)}
.rg-rank .k{color:var(--mute);font-size:.76rem;white-space:nowrap}

/* ── colophon ──────────────────────────────────────────────────────────── */
.rg-colo{border-top:1px solid var(--line);margin-top:1rem;padding:2.6rem 0 4rem;
    display:flex;gap:2rem;flex-wrap:wrap;align-items:flex-end}
.rg-colo p{font-size:.76rem;color:var(--mute);max-width:46ch;line-height:1.7}
.rg-back{margin-left:auto;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.68rem;
    letter-spacing:.16em;text-transform:uppercase;background:var(--acc);color:#111314;
    padding:.75rem 1.3rem;border:0;cursor:pointer;white-space:nowrap}
.rg-back:hover{background:#fff}
"""

# ---------------------------------------------------------------------------
WEEK = [
    ('Lun', False, [('#B7C2A9', 'Iaijutsu', '20:00 · 90 min'),
                    ('#A5C8D1', 'Judo', '18:30 · 90 min'),
                    ('#E2625E', 'Aikido', '19:00 · UB'),
                    ('#E2625E', 'Aikido', '20:00 · Sant Adrià')]),
    ('Mar', False, [('#E2625E', 'Aikido', '18:30 · todos'),
                    ('#E2625E', 'Aikido', '19:30 · principiantes'),
                    ('#E2625E', 'Aikido', '20:30 · todos'),
                    ('#FBE6A0', 'Karate', '21:30 · 60 min')]),
    ('Mié', False, [('#A5C8D1', 'Judo', '18:30 · 90 min'),
                    ('#E2625E', 'Aikido', '19:00 · UB'),
                    ('#E2625E', 'Aikido', '20:00 · 90 min'),
                    ('#E2625E', 'Aikido', '20:15 · Sant Adrià')]),
    ('Jue', False, [('#E2625E', 'Aikido', '18:30 · todos'),
                    ('#E2625E', 'Aikido', '19:30 · armas'),
                    ('#E2625E', 'Aikido', '20:30 · todos')]),
    ('Vie', False, [('#E2625E', 'Aikido', '19:00 · 60 min'),
                    ('#FBE6A0', 'Karate', '20:00 · 60 min')]),
    ('Sáb', True, [('#E2625E', 'Aikido', '07:30 · 90 min'),
                   ('#B7C2A9', 'Iaijutsu', '08:00 · mensual'),
                   ('#FBE6A0', 'Karate', '11:00 · 120 min')]),
    ('Dom', False, []),
]

LINEAGE = [
    ('1883–1969', 'Morihei Ueshiba', 'Ō-Sensei · fundador del aikido', 'Aikikai'),
    ('desde 1931', 'Aikikai Hombu Dojo', 'Tokio · casa madre', 'Aikikai Foundation'),
    ('', 'Miyamoto Tsuruzo', 'Shihan · Hombu Dojo', '8.º dan'),
    ('', 'Aikido Arashi Group', 'la línea que seguimos', 'IAF'),
    ('desde 2008', 'Aikido Musubi', 'Badalona · Barcelona', 'nuestro dojo'),
]

RANKS = [('Pablo Martín', '4.º dan · shidoin · dojo-cho'),
         ('Pedro Fortes', '4.º dan'), ('José Luis Zafra', '4.º dan'),
         ('Alberto Sancho', '4.º dan'), ('Juanma Pérez', '3.er dan'),
         ('Andreu Villar', '3.er dan'), ('Guanlong Zheng', '3.er dan')]

VENUES = [('access-information-NdxqmVbV-00', 'Badalona',
           "Av. d'Alfons XIII, 351 · Instalaciones Deportivas Badalona Sur<br>lunes a sábado · parking gratuito"),
          ('access-information-NdxqmVbV-01', 'Sant Adrià de Besòs',
           'Poliesportiu Municipal Marina-Besòs<br>lunes y miércoles · parking gratuito'),
          ('access-information-NdxqmVbV-02', 'Universitat de Barcelona',
           'Facultat de Dret · Av. Diagonal, 684<br>lunes y miércoles · principiantes')]

MONTH = {'01': 'ene', '02': 'feb', '03': 'mar', '04': 'abr', '05': 'may', '06': 'jun',
         '07': 'jul', '08': 'ago', '09': 'sep', '10': 'oct', '11': 'nov', '12': 'dic'}
TODAY = '2026-08-22'


def week_html():
    o = []
    for name, today, cl in WEEK:
        o.append('<div class="rg-day"%s><p class="d">%s</p>' % (' data-today' if today else '', name))
        if not cl:
            o.append('<p class="rg-empty">—</p>')
        for c, n, t in cl:
            o.append('<div class="rg-cl" style="--c:%s"><b>%s</b><span>%s</span></div>' % (c, n, t))
        o.append('</div>')
    return ''.join(o)


def bars_html():
    years = [str(y) for y in range(2008, 2027)]
    mx = max(PY.values())
    bars = ''.join('<div title="%s — %d"><i style="height:%.1f%%"></i></div>'
                   % (y, PY.get(y, 0), 100.0 * PY.get(y, 0) / mx) for y in years)
    ax = ''.join('<span>%s</span>' % y[2:] for y in years)
    return '<div class="rg-bars">%s</div><div class="rg-xax">%s</div>' % (bars, ax)


def sheet_html(n=48):
    return ''.join(
        '<a href="/galeria/" title="%s"><img src="/images/%s.webp" alt="" loading="lazy"></a>'
        % (d, t) for d, t, _ in ROWS[:n])


def log_html():
    rows, cur = [], None
    for d, title in reversed(EV):
        y = d[:4]
        if y != cur:
            cur = y
            rows.append('<tr><td class="rg-yr" colspan="3">%s</td></tr>' % y)
        nxt = ' data-next' if d >= TODAY else ''
        name = title.replace(' Aikikai', '').replace(' Birankai', '')
        grade = 'Aikikai'
        for g in ('7.º Dan', '6.º Dan', '5.º Dan', '4.º Dan'):
            if g in title:
                grade = g.replace('.º Dan', '.º dan')
                name = name.replace(' ' + g, '')
                break
        if 'Birankai' in title:
            grade += ' · Birankai'
        rows.append('<tr%s><td class="dt">%s %s</td><td class="nm">%s</td>'
                    '<td class="gr rg-mono" style="color:var(--mute);font-size:.72rem">%s</td></tr>'
                    % (nxt, d[8:10].lstrip('0'), MONTH[d[5:7]], name, grade))
    return ''.join(rows)


BODY = """
<div class="rg-w">

  <!-- 00 ─────────────────────────────────────────────────────────────── -->
  <section class="rg-id">
    <p class="rg-kanji">産靈<small>MUSUBI</small></p>
    <div class="rg-gloss">
      <p>Musubi es el nudo: aquello que une dos cosas y las deja unidas. En el aikido
         nombra el instante en que dos movimientos dejan de ser dos.</p>
      <p>Le pusimos el nombre a la asociación en 2008 y desde entonces no hemos
         encontrado una palabra mejor para lo que hacemos cada tarde en el tatami.</p>
    </div>
  </section>

  <!-- 01 ─────────────────────────────────────────────────────────────── -->
  <section class="rg-s" id="rg-semana">
    <div class="rg-head"><p class="rg-no">01</p>
      <div><h2>La semana</h2>
        <p class="sub">Veinte sesiones, seis días, tres espacios. Lo que hay en el tatami
           ahora mismo y lo que habrá el resto de la semana.</p></div></div>
    <div class="rg-now"><span class="rg-dot"></span>
      <span class="l">Ahora en el tatami</span>
      <span class="w">Karate</span>
      <span class="t">sábado 11:00–13:00 · Badalona · Pau Llorens</span></div>
    <div class="rg-grid">__WEEK__</div>
    <div class="rg-tot">
      <div><b>20</b><span>sesiones semanales</span></div>
      <div><b>17</b><span>clases en el horario</span></div>
      <div><b>4</b><span>disciplinas</span></div>
      <div><b>3</b><span>espacios</span></div>
      <div><b>11</b><span>instructores</span></div>
    </div>
  </section>

  <!-- 02 ─────────────────────────────────────────────────────────────── -->
  <section class="rg-s" id="rg-linaje">
    <div class="rg-head"><p class="rg-no">02</p>
      <div><h2>Linaje</h2>
        <p class="sub">De dónde viene lo que se enseña aquí. Cinco eslabones, sin saltos.</p></div></div>
    __LINEAGE__
  </section>

  <!-- 03 ─────────────────────────────────────────────────────────────── -->
  <section class="rg-s" id="rg-anos">
    <div class="rg-head"><p class="rg-no">03</p>
      <div><h2>Dieciocho años</h2>
        <p class="sub">Cada barra es un año; su altura, lo que quedó registrado de él.
           462 entradas entre álbumes, publicaciones y vídeos.</p></div></div>
    __BARS__
    <p class="rg-note">El salto de 2020 no es una casualidad: es el año en que el dojo
       empezó a documentar en serio lo que pasaba dentro. Los años flacos del principio
       no fueron años flacos de entrenamiento.</p>
  </section>

  <!-- 04 ─────────────────────────────────────────────────────────────── -->
  <section class="rg-s" id="rg-archivo">
    <div class="rg-head"><p class="rg-no">04</p>
      <div><h2>El archivo</h2>
        <p class="sub">Las cuarenta y ocho entradas más recientes. Pasa el cursor para
           verlas en color; haz clic para abrir la galería completa.</p></div></div>
    <div class="rg-sheet">__SHEET__</div>
    <div class="rg-legend">
      <div><b>49</b><span>álbumes</span></div>
      <div><b>236</b><span>publicaciones</span></div>
      <div><b>177</b><span>vídeos</span></div>
      <div><b>462</b><span>en total</span></div>
    </div>
  </section>

  <!-- 05 ─────────────────────────────────────────────────────────────── -->
  <section class="rg-s" id="rg-seminarios">
    <div class="rg-head"><p class="rg-no">05</p>
      <div><h2>Registro de seminarios</h2>
        <p class="sub">Treinta y nueve seminarios y clases abiertas desde 2020.
           En amarillo, los que aún no han ocurrido.</p></div></div>
    <table class="rg-log">
      <thead><tr><th>Fecha</th><th>Profesor o acto</th><th class="gr">Grado</th></tr></thead>
      <tbody>__LOG__</tbody>
    </table>
    <p class="rg-more"><a href="/seminarios/" style="border-bottom:1px solid var(--acc);
       color:var(--acc)">Ver las fichas completas →</a></p>
  </section>

  <!-- 06 ─────────────────────────────────────────────────────────────── -->
  <section class="rg-s" id="rg-tatamis">
    <div class="rg-head"><p class="rg-no">06</p>
      <div><h2>Los tres tatamis</h2>
        <p class="sub">El dojo propio en Badalona y dos espacios prestados.
           Los planos son los mismos que encontrarás en la página de acceso.</p></div></div>
    <div class="rg-ven">__VENUES__</div>
  </section>

  <!-- 07 ─────────────────────────────────────────────────────────────── -->
  <section class="rg-s" id="rg-grados">
    <div class="rg-head"><p class="rg-no">07</p>
      <div><h2>Grados y afiliación</h2>
        <p class="sub">Quién enseña, con qué grado, y de qué federaciones cuelga el dojo.</p></div></div>
    <div class="rg-two">
      <div>__RANKS__</div>
      <dl class="rg-dl">
        <dt>Fundada</dt><dd>2008, en Badalona</dd>
        <dt>Forma</dt><dd>Asociación cultural autogestionada y sin ánimo de lucro</dd>
        <dt>Dirección</dt><dd>Pablo Martín · 4.º dan · shidoin</dd>
        <dt>Vía</dt><dd>Aikido Arashi Group → Hombu Dojo, a través de Miyamoto Tsuruzo, 8.º dan</dd>
        <dt>Enlaces</dt><dd>Aikikai Foundation · International Aikido Federation ·
            Aikido Arashi Group · Real Federación Española de Judo y D.A.</dd>
        <dt>Inscripción</dt><dd>Gratuita y abierta todo el año</dd>
      </dl>
    </div>
  </section>

  <!-- colophon ───────────────────────────────────────────────────────── -->
  <div class="rg-colo">
    <p>Este registro se compone a partir de los mismos datos que el resto del sitio:
       el horario, el calendario, la galería y las fichas de seminarios. No se escribe
       a mano, así que no puede quedarse atrás.<br>
       <span class="rg-mono">Edición 22.08.2026 · Associació Cultural Musubi Aikido ·
       CIF G65500340</span></p>
    <button class="rg-back" data-rg-close>Volver a la portada</button>
  </div>
</div>
"""


def body(close_label='Volver a la portada'):
    lin = ''.join(
        '<div class="rg-node"%s><p class="y">%s</p><p class="n">%s<small>%s</small></p>'
        '<p class="g">%s</p></div>'
        % (' data-us' if i == len(LINEAGE) - 1 else '', y or '·', n, s, g)
        for i, (y, n, s, g) in enumerate(LINEAGE))
    ven = ''.join(
        '<figure><img src="/images/%s.webp" alt="" loading="lazy"><b>%s</b><small>%s</small></figure>'
        % v for v in VENUES)
    rk = ''.join('<div class="rg-rank"><span class="p">%s</span><span class="k">%s</span></div>'
                 % r for r in RANKS)
    return (BODY.replace('__WEEK__', week_html())
                .replace('__LINEAGE__', lin)
                .replace('__BARS__', bars_html())
                .replace('__SHEET__', sheet_html())
                .replace('__LOG__', log_html())
                .replace('__VENUES__', ven)
                .replace('__RANKS__', rk)
                .replace('Volver a la portada', close_label))


def masthead(close=True):
    x = ('<button class="rg-x" data-rg-close aria-label="Cerrar el registro">&#10005;</button>'
         if close else '')
    return ('<header class="rg-mast"><div class="rg-w"><div class="rg-mast-in">'
            '<span class="rg-seal">産靈</span>'
            '<span class="ttl">El registro</span>'
            '<span class="ed rg-mono">Ed. 22.08.2026 &nbsp;·&nbsp; 08 secciones</span>'
            '%s</div></div></header>' % x)
