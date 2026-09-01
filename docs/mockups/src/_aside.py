# -*- coding: utf-8 -*-
"""The dark aside, in two layouts.

NOT a report. The tone is b-sides: the things that change every week, plus
shorter and odder ways of saying what the other pages say at length. It is
deliberately lighter than the home — no long prose, no argument, no case being
made. Both layouts render the same content.
"""
import _dat as D

PY, TY, ROWS = D.gallery()
EV = D.events()
NAME_KANJI = '裏'
NAME = 'Ura'
HOME_KANJI = '表'

# ═══════════════════════════════════════════════════════════════════════════
CSS_BASE = r"""
.ab{--fg:#d5dadc;--hi:#fff;--mute:#9aa2a5;--line:rgba(255,255,255,.13);
    --acc:#FFF200;--bg:#111314;--card:#181b1c;
    background:var(--bg);color:var(--fg);font-family:'Noto Sans',system-ui,sans-serif;
    font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
.ab *{box-sizing:border-box}
.ab a{color:inherit;text-decoration:none}
.ab h1,.ab h2,.ab h3{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-weight:400;
    color:var(--hi);margin:0;letter-spacing:.02em}
.ab p{margin:0}
.ab-w{max-width:1140px;margin:0 auto;padding:0 6rem}
@media(max-width:991.98px){.ab-w{padding:0 4rem}}
@media(max-width:767.98px){.ab-w{padding:0 2rem}}
.ab-mono{font-family:ui-monospace,'SF Mono',Menlo,monospace;font-variant-numeric:tabular-nums}
.ab-kick{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;letter-spacing:.24em;
    text-transform:uppercase;color:var(--mute)}

/* ── masthead ───────────────────────────────────────────────────────────── */
.ab-mast{position:sticky;top:0;z-index:6;background:rgba(17,19,20,.95);
    backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.ab-mast-in{display:flex;align-items:center;gap:1rem;padding:.8rem 0;min-height:3.3rem}
.ab-seal{font-family:'Noto Sans JP','Noto Sans',sans-serif;font-size:1.4rem;color:var(--acc);
    line-height:1}
.ab-mast .ttl{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.72rem;
    letter-spacing:.3em;text-transform:uppercase;color:var(--hi)}
.ab-mast .sub{font-size:.72rem;color:var(--mute);margin-left:.4rem}
.ab-x{margin-left:auto;display:inline-flex;align-items:center;gap:.55rem;
    border:1px solid var(--line);background:none;color:var(--fg);cursor:pointer;
    font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;letter-spacing:.14em;
    text-transform:uppercase;padding:.55rem .9rem;line-height:1}
.ab-x:hover{background:var(--acc);color:#111314;border-color:var(--acc)}
.ab-x:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.ab-x i{font-family:'Noto Sans JP','Noto Sans',sans-serif;font-style:normal;font-size:.95rem;
    color:var(--acc);line-height:1}
.ab-x:hover i{color:#111314}
@media(max-width:575.98px){.ab-mast .sub{display:none}.ab-x span{display:none}}

/* ── this week ──────────────────────────────────────────────────────────── */
.ab-flag{display:flex;gap:.8rem;align-items:flex-start;padding:.9rem 1.1rem;
    background:rgba(255,242,0,.08);border-left:2px solid var(--acc);margin-bottom:1.5rem}
.ab-flag b{color:var(--acc);font-weight:400;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
    font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;white-space:nowrap;
    padding-top:.15rem}
.ab-flag p{font-size:.87rem;color:#e2e6e8}
.ab-days{display:grid;grid-template-columns:repeat(7,1fr);gap:2px}
.ab-day{background:var(--card);padding:.75rem .6rem 1rem;min-height:8.5rem}
.ab-day .dn{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.58rem;
    letter-spacing:.14em;text-transform:uppercase;color:var(--mute)}
.ab-day .dd{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.25rem;
    color:var(--hi);line-height:1;margin:.15rem 0 .7rem}
.ab-day[data-off]{background:rgba(255,255,255,.02)}
.ab-day[data-off] .dd{color:#5f696c}
.ab-day[data-now]{background:rgba(255,242,0,.1)}
.ab-day[data-now] .dn,.ab-day[data-now] .dd{color:var(--acc)}
.ab-cl{border-left:2px solid var(--c);padding:.2rem 0 .25rem .45rem;margin-bottom:.45rem}
.ab-cl b{display:block;color:var(--hi);font-size:.72rem;font-weight:400;line-height:1.3}
.ab-cl span{display:block;color:var(--mute);font-size:.64rem}
.ab-rest{color:#5f696c;font-size:.68rem}
@media(max-width:991.98px){.ab-days{grid-template-columns:repeat(4,1fr)}}
@media(max-width:575.98px){.ab-days{grid-template-columns:repeat(2,1fr)}.ab-day{min-height:0}}
.ab-usual{margin-top:1.1rem;font-size:.82rem;color:var(--mute)}
.ab-usual a{color:var(--acc);border-bottom:1px solid rgba(255,242,0,.4)}

/* ── what's coming ──────────────────────────────────────────────────────── */
.ab-next{display:grid;gap:2px}
.ab-nx{display:grid;grid-template-columns:6.5rem 1fr auto;gap:1.2rem;align-items:baseline;
    background:var(--card);padding:.85rem 1.1rem}
.ab-nx .d{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.72rem;color:var(--acc);
    letter-spacing:.06em;white-space:nowrap}
.ab-nx .t{color:var(--hi);font-size:.95rem}
.ab-nx .n{color:var(--mute);font-size:.8rem;text-align:right}
.ab-nx[data-cl] .d{color:#E2625E}
@media(max-width:767.98px){.ab-nx{grid-template-columns:1fr;gap:.15rem}
    .ab-nx .n{text-align:left}}

/* ── archive ────────────────────────────────────────────────────────────── */
.ab-jump{display:flex;gap:2px;margin-bottom:1rem;flex-wrap:wrap}
.ab-jump a{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
    letter-spacing:.06em;color:var(--mute);padding:.3rem .5rem;background:var(--card)}
.ab-jump a:hover{background:var(--acc);color:#111314}
.ab-jump a[data-on]{color:var(--hi)}
.ab-sheet{display:grid;grid-template-columns:repeat(16,1fr);gap:2px}
.ab-sheet a{aspect-ratio:1;overflow:hidden;background:#1b1e1f;display:block}
.ab-sheet img{width:100%;height:100%;object-fit:cover;filter:grayscale(1) contrast(1.04);
    opacity:.7;transition:filter .25s,opacity .25s,transform .25s}
.ab-sheet a:hover img{filter:none;opacity:1;transform:scale(1.06)}
@media(max-width:991.98px){.ab-sheet{grid-template-columns:repeat(8,1fr)}}
@media(max-width:575.98px){.ab-sheet{grid-template-columns:repeat(4,1fr)}}
.ab-count{display:flex;gap:2rem;flex-wrap:wrap;margin-top:1.2rem}
.ab-count b{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.4rem;color:var(--hi);
    display:block;line-height:1}
.ab-count span{font-size:.62rem;letter-spacing:.14em;text-transform:uppercase;color:var(--mute)}

/* ── seminars, as an accordion ──────────────────────────────────────────── */
.ab-acc{border-top:1px solid var(--line)}
.ab-acc details{border-bottom:1px solid var(--line)}
.ab-acc summary{list-style:none;cursor:pointer;display:flex;align-items:baseline;gap:1.2rem;
    padding:.95rem 0}
.ab-acc summary::-webkit-details-marker{display:none}
.ab-acc summary .y{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.15rem;
    color:var(--hi);min-width:4rem}
.ab-acc summary .c{font-size:.75rem;color:var(--mute)}
.ab-acc summary .ch{margin-left:auto;color:var(--mute);font-size:.8rem;transition:transform .2s}
.ab-acc details[open] summary .y{color:var(--acc)}
.ab-acc details[open] summary .ch{transform:rotate(45deg)}
.ab-acc summary:hover .y{color:var(--acc)}
.ab-ev{display:grid;grid-template-columns:5rem 1fr;gap:1.2rem;padding:.5rem 0 .8rem 0;
    align-items:baseline}
.ab-ev .d{font-size:.75rem;color:var(--mute);white-space:nowrap}
.ab-ev .t{color:var(--fg);font-size:.9rem;line-height:1.45}
.ab-ev .t small{display:block;color:var(--mute);font-size:.72rem;margin-top:.1rem}
.ab-ev-list{padding-bottom:.7rem}
@media(max-width:575.98px){.ab-ev{grid-template-columns:1fr;gap:.1rem}}

/* ── where it comes from ────────────────────────────────────────────────── */
.ab-chain{display:grid;gap:0}
.ab-link{display:grid;grid-template-columns:8rem 1fr;gap:1.5rem;padding:1rem .9rem;
    border-top:1px solid rgba(255,255,255,.08);align-items:baseline}
.ab-link:last-child{border-bottom:1px solid rgba(255,255,255,.08)}
.ab-link .y{font-size:.7rem;color:var(--mute)}
.ab-link .n{color:var(--hi);font-size:1.02rem}
.ab-link .n small{display:block;color:var(--mute);font-size:.78rem;margin-top:.2rem;
    line-height:1.5;max-width:52ch}
.ab-link .det{display:block;margin-top:.5rem;padding-top:.5rem;font-size:.76rem;
    color:#c2c8ca;border-top:1px solid rgba(255,255,255,.09);max-width:52ch}
.ab-link[data-us]{background:rgba(255,242,0,.07)}
.ab-link[data-us] .n{color:var(--acc)}
@media(max-width:575.98px){.ab-link{grid-template-columns:1fr;gap:.15rem}}

/* ── words ──────────────────────────────────────────────────────────────── */
.ab-words{display:grid;grid-template-columns:repeat(3,1fr);gap:2px}
.ab-word{background:var(--card);padding:1.2rem 1.1rem 1.3rem}
.ab-word .k{font-family:'Noto Sans JP','Noto Sans',sans-serif;font-size:1.7rem;color:var(--hi);
    line-height:1;letter-spacing:.05em}
.ab-word .r{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.66rem;
    letter-spacing:.2em;text-transform:uppercase;color:var(--acc);margin:.5rem 0 .55rem}
.ab-word p{font-size:.82rem;line-height:1.65;color:var(--mute)}
@media(max-width:767.98px){.ab-words{grid-template-columns:1fr 1fr}}
@media(max-width:479.98px){.ab-words{grid-template-columns:1fr}}

/* the second six sit behind a control rather than lengthening the panel */
.ab-more{display:grid;grid-template-rows:0fr;transition:grid-template-rows .35s ease}
.ab-more>div{overflow:hidden;min-height:0}
.ab-more[data-open]{grid-template-rows:1fr}
.ab-more .ab-words{margin-top:2px}
@media(prefers-reduced-motion:reduce){.ab-more{transition:none}}
.ab-morebar{display:flex;align-items:center;gap:1.4rem;flex-wrap:wrap;margin-top:1.1rem}
.ab-morebtn{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.64rem;
    letter-spacing:.15em;text-transform:uppercase;background:none;color:var(--fg);
    border:1px solid var(--line);padding:.6rem 1.1rem;cursor:pointer}
.ab-morebtn:hover{border-color:var(--acc);color:var(--acc)}
.ab-morebtn:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.ab-morebtn[aria-expanded="true"]{border-color:var(--acc);color:var(--acc)}
.ab-gloss{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.64rem;
    letter-spacing:.15em;text-transform:uppercase;color:var(--mute);
    border-bottom:1px solid rgba(255,255,255,.2);padding-bottom:.2rem}
.ab-gloss:hover{color:var(--acc);border-bottom-color:var(--acc)}

/* ── links: eighteen of them, so three tiers rather than one grid ───────── */
.ab-lk-main{display:grid;grid-template-columns:repeat(3,1fr);gap:2px;margin-bottom:2rem}
.ab-lk-main a{background:var(--card);padding:1.15rem 1.1rem 1.25rem;display:block}
.ab-lk-main a:hover{background:#1f2223}
.ab-lk-main b{display:block;font-weight:400;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
    color:var(--hi);font-size:1.02rem;letter-spacing:.02em;line-height:1.3}
.ab-lk-main a:hover b{color:var(--acc)}
.ab-lk-main span{display:block;color:var(--mute);font-size:.72rem;margin-top:.4rem}
@media(max-width:767.98px){.ab-lk-main{grid-template-columns:1fr}}

.ab-lk-h{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.6rem;letter-spacing:.2em;
    text-transform:uppercase;color:var(--mute);margin-bottom:.9rem;padding-bottom:.6rem;
    border-bottom:1px solid var(--line)}
/* Eighteen dojos across eight countries: the country rides on the row, because
   a column per country would be eight columns of one or two entries. */
.ab-lk-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:0 2.4rem}
.ab-lk-grid a{display:block;padding:.6rem 0;border-bottom:1px solid rgba(255,255,255,.08)}
.ab-lk-grid b{display:block;font-weight:400;color:var(--hi);font-size:.87rem;line-height:1.35}
.ab-lk-grid a:hover b{color:var(--acc)}
.ab-lk-grid span{display:flex;gap:.5rem;align-items:baseline;color:var(--mute);font-size:.68rem;
    margin-top:.15rem}
.ab-lk-grid i{font-style:normal;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
    font-size:.58rem;letter-spacing:.12em;text-transform:uppercase;color:var(--acc);
    flex:0 0 auto;min-width:4.6rem}
.ab-lk-tail{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:2.4rem;margin-top:2.4rem}
.ab-lk-tail a{display:block;padding:.55rem 0;border-bottom:1px solid rgba(255,255,255,.08)}
.ab-lk-tail b{display:block;font-weight:400;color:var(--hi);font-size:.87rem;line-height:1.35}
.ab-lk-tail a:hover b{color:var(--acc)}
.ab-lk-tail em{display:block;font-style:normal;color:#c2c8ca;font-size:.76rem;margin-top:.12rem}
.ab-lk-tail span{display:block;color:var(--mute);font-size:.68rem;margin-top:.12rem}
@media(max-width:991.98px){.ab-lk-grid{grid-template-columns:1fr 1fr}
    .ab-lk-tail{grid-template-columns:1fr 1fr}}
@media(max-width:575.98px){.ab-lk-grid,.ab-lk-tail{grid-template-columns:1fr;gap:0}
    .ab-lk-tail>div{margin-top:1.6rem}}

/* ── the digest ─────────────────────────────────────────────────────────── */
.ab-ess{display:grid;grid-template-columns:repeat(3,1fr);gap:2px}
.ab-cell{background:var(--card);padding:1.3rem 1.2rem 1.5rem}
.ab-cell h3{font-size:.95rem;margin-bottom:.8rem;letter-spacing:.05em;text-transform:uppercase}
.ab-cell dl{display:grid;grid-template-columns:auto 1fr;gap:.35rem .9rem;margin:0;font-size:.82rem}
.ab-cell dt{color:var(--mute)}
.ab-cell dd{margin:0;color:var(--fg)}
.ab-cell p{font-size:.82rem;line-height:1.65;color:var(--mute)}
.ab-cell a.go{display:inline-block;margin-top:.9rem;font-family:Futura,'Trebuchet MS',Arial,sans-serif;
    font-size:.62rem;letter-spacing:.14em;text-transform:uppercase;color:var(--acc);
    border-bottom:1px solid rgba(255,242,0,.45);padding-bottom:.2rem}
@media(max-width:767.98px){.ab-ess{grid-template-columns:1fr}}

/* ── foot ───────────────────────────────────────────────────────────────── */
.ab-foot{border-top:1px solid var(--line);padding:2.4rem 0 3.4rem;display:flex;gap:2rem;
    flex-wrap:wrap;align-items:flex-end}
.ab-foot p{font-size:.76rem;color:var(--mute);max-width:48ch;line-height:1.7}
.ab-back{margin-left:auto;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.66rem;
    letter-spacing:.16em;text-transform:uppercase;background:var(--acc);color:#111314;border:0;
    padding:.8rem 1.4rem;cursor:pointer;white-space:nowrap}
.ab-back:hover{background:#fff}
"""

# ═══════════════════════════════════════════════════════════════════════════
# A · CUADERNILLO — full-width bands, one idea per band, lots of air
CSS_A = r"""
.ab-a .ab-band{border-top:1px solid var(--line);padding:3.2rem 0}
.ab-a .ab-band:first-of-type{border-top:0}
.ab-a .ab-h{display:flex;align-items:baseline;gap:1.1rem;flex-wrap:wrap;margin-bottom:1.6rem}
.ab-a .ab-h h2{font-size:1.65rem}
.ab-a .ab-h .note{font-size:.85rem;color:var(--mute)}
.ab-a .ab-lead{padding:3.6rem 0 2.6rem;max-width:44ch}
.ab-a .ab-lead p{font-size:1.24rem;line-height:1.55;color:#e6eaec}
.ab-a .ab-lead p+p{margin-top:.8rem;font-size:.9rem;color:var(--mute)}
.ab-a .ab-lead p.ab-one{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:1.6rem;
    line-height:1.45;color:#fff;max-width:31ch}
@media(max-width:575.98px){.ab-a .ab-lead p.ab-one{font-size:1.25rem}}
"""

# B · EL PLIEGO — a sticky index rail on the left, denser content on the right
CSS_B = r"""
.ab-b .ab-sheetwrap{display:grid;grid-template-columns:9rem 1fr;gap:0}
.ab-b .ab-rail{position:sticky;top:3.3rem;align-self:start;padding:3rem 0;height:min-content}
.ab-b .ab-rail ol{list-style:none;margin:0;padding:0}
.ab-b .ab-rail li{margin-bottom:.75rem}
.ab-b .ab-rail a{font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:.62rem;
    letter-spacing:.12em;text-transform:uppercase;color:var(--mute);display:block;line-height:1.4}
.ab-b .ab-rail a:hover{color:var(--acc)}
.ab-b .ab-rail a i{font-style:normal;color:#5f696c;display:block;font-size:.58rem}
.ab-b .ab-col{border-left:1px solid var(--line);padding-left:2.6rem;min-width:0}
.ab-b .ab-band{padding:2.6rem 0;border-bottom:1px solid var(--line)}
.ab-b .ab-band:last-child{border-bottom:0}
.ab-b .ab-h{display:grid;grid-template-columns:1fr auto;gap:1rem;align-items:baseline;
    margin-bottom:1.3rem}
.ab-b .ab-h h2{font-size:1.3rem}
.ab-b .ab-h .note{font-size:.8rem;color:var(--mute);text-align:right}
.ab-b .ab-lead{padding:3rem 0 0}
.ab-b .ab-lead p{font-size:1.08rem;line-height:1.6;color:#e6eaec;max-width:52ch}
.ab-b .ab-lead p+p{margin-top:.7rem;font-size:.85rem;color:var(--mute)}
.ab-b .ab-two{display:grid;grid-template-columns:1fr 1fr;gap:2.2rem}
@media(max-width:991.98px){.ab-b .ab-sheetwrap{grid-template-columns:1fr}
    .ab-b .ab-rail{display:none}
    .ab-b .ab-col{border-left:0;padding-left:0}
    .ab-b .ab-two{grid-template-columns:1fr;gap:1.6rem}}
/* the two-up column is half width, so the grids inside it have to give up
   their own columns rather than squeeze */
.ab-b .ab-two .ab-words{grid-template-columns:1fr}
.ab-b .ab-two .ab-word{padding:.85rem 1rem .95rem}
.ab-b .ab-two .ab-word .k{font-size:1.35rem}
.ab-b .ab-two .ab-link{grid-template-columns:1fr;gap:.2rem;padding:.85rem .8rem}
"""


# ═══════════════════════════════════════════════════════════════════════════
# content primitives — identical in both layouts
# ═══════════════════════════════════════════════════════════════════════════
def week():
    o = ['<div class="ab-flag"><b>Agosto</b><p>Estamos en <strong>horario de agosto</strong>: '
         'solo martes y jueves, de 18:30 a 20:30. El horario habitual vuelve el 1 de '
         'septiembre.</p></div>',
         '<div class="ab-days">']
    for name, num, today, cl in D.NEXT_SEVEN:
        att = ' data-now' if today else ('' if cl else ' data-off')
        o.append('<div class="ab-day"%s><p class="dn">%s</p><p class="dd">%s</p>' % (att, name, num))
        if not cl:
            o.append('<p class="ab-rest">%s</p>' % ('Hoy, descanso' if today else 'Descanso'))
        for c, n, t in cl:
            o.append('<div class="ab-cl" style="--c:%s"><b>%s</b><span>%s</span></div>' % (c, n, t))
        o.append('</div>')
    o.append('</div><p class="ab-usual">A partir del 1 de septiembre vuelven las veinte sesiones '
             'semanales de aikido, iaijutsu, judo y karate. '
             '<a href="/horarios/">Ver el horario completo</a></p>')
    return ''.join(o)


def ahead():
    o = ['<div class="ab-next">']
    kind = {'extra': 'Clase extra', 'change': 'Cambio', 'closure': 'Cierre'}
    for d, k, t, n in D.AHEAD:
        cl = ' data-cl' if k == 'closure' else ''
        o.append('<div class="ab-nx"%s><p class="d">%s %s</p><p class="t">%s</p>'
                 '<p class="n">%s</p></div>'
                 % (cl, d[8:10].lstrip('0'), D.MON3[d[5:7]], t, n))
    o.append('</div>')
    return ''.join(o)


def jump():
    years = sorted(PY, reverse=True)
    return ('<div class="ab-jump">'
            + ''.join('<a href="/galeria/"%s>%s</a>' % (' data-on' if i < 3 else '', y)
                      for i, y in enumerate(years)) + '</div>')


def sheet(n=64):
    return ('<div class="ab-sheet">' + ''.join(
        '<a href="/galeria/" title="%s"><img src="/images/%s.webp" alt="" loading="lazy"></a>'
        % (d, t) for d, t, _ in ROWS[:n]) + '</div>')


def counts():
    return ('<div class="ab-count">'
            '<div><b>462</b><span>momentos guardados</span></div>'
            '<div><b>49</b><span>álbumes</span></div>'
            '<div><b>236</b><span>publicaciones</span></div>'
            '<div><b>177</b><span>vídeos</span></div></div>')


def seminars():
    by = {}
    for e in EV:
        by.setdefault(e['date'][:4], []).append(e)
    o = ['<div class="ab-acc">']
    for i, y in enumerate(sorted(by, reverse=True)):
        rows = sorted(by[y], key=lambda e: e['date'], reverse=True)
        o.append('<details%s><summary><span class="y">%s</span>'
                 '<span class="c">%d %s</span><span class="ch">+</span></summary>'
                 '<div class="ab-ev-list">'
                 % (' open' if i == 0 else '', y, len(rows),
                    'sesión' if len(rows) == 1 else 'sesiones'))
        for e in rows:
            sub = ('<small>%s</small>' % e['grade']) if e['grade'] else ''
            o.append('<div class="ab-ev"><p class="d">%s %s</p>'
                     '<p class="t">%s%s</p></div>'
                     % (e['date'][8:10].lstrip('0'), D.MON3[e['date'][5:7]], e['label'], sub))
        o.append('</div></details>')
    o.append('</div>')
    return ''.join(o)


def chain():
    out = []
    for i, (y, n, sub, det) in enumerate(D.LINE):
        d = ('<span class="det">%s</span>' % det) if det else ''
        out.append('<div class="ab-link"%s><p class="y">%s</p>'
                   '<p class="n">%s<small>%s</small>%s</p></div>'
                   % (' data-us' if i == len(D.LINE) - 1 else '', y or '·', n, sub, d))
    return '<div class="ab-chain">%s</div>' % ''.join(out)


def words():
    cell = ('<div class="ab-word"><p class="k">%s</p><p class="r">%s</p><p>%s</p></div>')
    first = ''.join(cell % w for w in D.WORDS)
    more = ''.join(cell % w for w in D.WORDS_MORE)
    return ('<div class="ab-words">%s</div>'
            '<div class="ab-more" id="ab-more"><div class="ab-words">%s</div></div>'
            '<div class="ab-morebar">'
            '<button class="ab-morebtn" aria-expanded="false" aria-controls="ab-more">'
            'Seis palabras más</button>'
            '<a class="ab-gloss" href="/glosario/">Glosario completo &rarr;</a>'
            '</div>' % (first, more))


def links():
    o = ['<div class="ab-lk-main">']
    for name, host, url in D.LINKS_MAIN:
        o.append('<a href="%s" rel="noopener"><b>%s</b><span>%s</span></a>' % (url, name, host))
    o.append('</div><p class="ab-lk-h">Dojos amigos</p><div class="ab-lk-grid">')
    for name, place, host, url in sorted(D.LINKS_DOJOS, key=lambda r: r[0].lower()):
        o.append('<a href="%s" rel="noopener"><b>%s</b>'
                 '<span><i>%s</i>%s</span></a>' % (url, name, place, host))
    o.append('</div><div class="ab-lk-tail">')
    for head, rows in D.LINKS_TAIL:
        o.append('<div><p class="ab-lk-h">%s</p>' % head)
        for r in rows:
            note = ('<em>%s</em>' % r[3]) if len(r) > 3 else ''
            o.append('<a href="%s" rel="noopener"><b>%s</b>%s<span>%s</span></a>'
                     % (r[2], r[0], note, r[1]))
        o.append('</div>')
    o.append('</div>')
    return ''.join(o)


def essentials():
    return """<div class="ab-ess">
  <div class="ab-cell"><h3>Dónde</h3>
    <dl><dt>Badalona</dt><dd>Av. d'Alfons XIII, 351</dd>
        <dt>Sant Adrià</dt><dd>Poliesportiu Marina-Besòs</dd>
        <dt>Barcelona</dt><dd>UB, Facultat de Dret</dd></dl>
    <a class="go" href="/acceso/">Cómo llegar</a></div>
  <div class="ab-cell"><h3>Cuánto</h3>
    <dl><dt>Inscripción</dt><dd>Gratuita, todo el año</dd>
        <dt>Prueba</dt><dd>Dos clases, sin coste</dd>
        <dt>Cuota</dt><dd>Mensual, según la actividad</dd></dl>
    <a class="go" href="/cuotas/">Ver las cuotas</a></div>
  <div class="ab-cell"><h3>Cómo empezar</h3>
    <p>Escríbenos con un día de antelación, dinos qué clase te interesa y te decimos
       cuándo venir. Ropa cómoda de manga larga; el keikogi ya llegará.</p>
    <a class="go" href="/contacto/">Escríbenos</a></div>
</div>"""


def mast(closeable=True):
    x = ('<button class="ab-x" data-rg-close><i>%s</i> <span>Volver a la portada</span></button>'
         % HOME_KANJI if closeable else '')
    return ('<header class="ab-mast"><div class="ab-w"><div class="ab-mast-in">'
            '<span class="ab-seal">%s</span><span class="ttl">%s</span>'
            '<span class="sub">el dojo por detrás</span>%s'
            '</div></div></header>' % (NAME_KANJI, NAME, x))


JS_WORDS = """
(function(){
  var b=document.querySelector('.ab-morebtn'); if(!b)return;
  var box=document.getElementById('ab-more');
  b.addEventListener('click',function(){
    var on=box.hasAttribute('data-open');
    if(on){box.removeAttribute('data-open');b.setAttribute('aria-expanded','false');
           b.textContent='Seis palabras más';}
    else{box.setAttribute('data-open','');b.setAttribute('aria-expanded','true');
         b.textContent='Menos palabras';}
  });
})();
"""

FOOT = """<div class="ab-foot"><p>Esto no se escribe a mano. Sale del horario, del calendario,
de la galería y de las fichas de seminario, así que no puede quedarse atrás.
<br><span class="ab-mono">23.08.2026 · Associació Cultural Musubi Aikido</span></p>
<button class="ab-back" data-rg-close>Volver a la portada</button></div>"""


# ═══════════════════════════════════════════════════════════════════════════
def body_a():
    B = lambda h, note, inner: (
        '<section class="ab-band"><div class="ab-h"><h2>%s</h2>'
        '<p class="note">%s</p></div>%s</section>' % (h, note, inner))
    return """<div class="ab-a"><div class="ab-w">
  <div class="ab-lead">
    <p class="ab-one">Lo que pasa esta semana, y todo lo que ha pasado desde 2008.</p>
  </div>
  %s %s %s %s %s %s %s %s
  %s
</div></div>""" % (
        B('Los próximos siete días', 'Del domingo 23 al sábado 29 de agosto', week()),
        B('Lo que viene', 'Próximas cinco cosas en el calendario', ahead()),
        B('El archivo', 'Las 64 entradas más recientes', jump() + sheet() + counts()),
        B('Seminarios y clases especiales', '39 sesiones desde 2020', seminars()),
        B('De Tokio a Barcelona', 'La línea, sin saltos', chain()),
        B('Palabras del tatami', 'Seis que oirás el primer día', words()),
        B('Enlaces', 'Con quién compartimos el tatami', links()),
        B('Lo esencial', 'Tres páginas en una pantalla', essentials()),
        FOOT)


def body_b():
    RAIL = [('sem', 'Esta semana', 'agosto'), ('vie', 'Lo que viene', '5 fechas'),
            ('arc', 'El archivo', '462'), ('sem2', 'Seminarios', '39'),
            ('ori', 'De dónde viene', '4'), ('pal', 'Palabras', '6'),
            ('ese', 'Lo esencial', '3')]
    rail = ''.join('<li><a href="#ab-%s">%s<i>%s</i></a></li>' % (i, t, n) for i, t, n in RAIL)
    B = lambda i, h, note, inner: (
        '<section class="ab-band" id="ab-%s"><div class="ab-h"><h2>%s</h2>'
        '<p class="note">%s</p></div>%s</section>' % (i, h, note, inner))
    return """<div class="ab-b"><div class="ab-w"><div class="ab-sheetwrap">
  <nav class="ab-rail"><ol>%s</ol></nav>
  <div class="ab-col">
    <div class="ab-lead">
      <p>Lo que cambia cada semana, lo que se guarda y unas cuantas cosas que no caben
         en la portada.</p>
      <p>Nada de esto es imprescindible para venir a entrenar. Está aquí porque nos gusta.</p>
    </div>
    %s %s %s %s
    <section class="ab-band" id="ab-ori"><div class="ab-two">
      <div><div class="ab-h"><h2>De dónde viene</h2></div>%s</div>
      <div><div class="ab-h"><h2>Palabras del tatami</h2></div>%s</div>
    </div></section>
    %s
    %s
  </div>
</div></div></div>""" % (
        rail,
        B('sem', 'Esta semana', 'Sábado 22 de agosto', week()),
        B('vie', 'Lo que viene', '5 fechas', ahead()),
        B('arc', 'El archivo', '64 más recientes', jump() + sheet() + counts()),
        B('sem2', 'Seminarios y masterclases', '39 desde 2020', seminars()),
        chain(), words(),
        B('ese', 'Lo esencial', 'Tres páginas en una pantalla', essentials()),
        FOOT)
