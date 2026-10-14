#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Online signup and Stripe billing — two layouts, and the admin side.

THE SPEC. "Aikido Musubi — Online Membership Signup & Stripe Billing Spec",
14 October 2026, a Claude Docs document. Everything drawn here is what that
spec asks for; where a mockup goes further than it, the note beside it says so.

WHAT IS COMPARED. The spec fixes the content and the rules; it leaves the order
and the shape of the page open. The two layouts differ on one question, which
is the one that matters for a household:

    A  plan first      period → rate → people → holder → legal, one page,
                       with a receipt beside the form that totals as you go.
                       Continues straight from /cuotas/, whose buttons
                       preselect the period and the age group.
    B  people first    who trains → how to pay → holder → review. Because the
                       household is known before the period is chosen, every
                       period card shows THIS household's total and saving,
                       which is the comparison somebody is actually making.

    inscripcion-admin  what the dojo receives and does: the three emails,
                       and every manual action the spec leaves to a person.

THE FIGURES ARE REAL. Prices from _data/fees.yml; the household is two people
aged 17 or over and one up to 16, the spec's fourth worked example (77 € a
month). The signup date is 20 January 2027, the month the flow launches, so
the first full charge falls on 5 February.

    python3 docs/mockups/src/build_signup.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, 'docs', 'mockups')

# ---------------------------------------------------------------------------
# Prices, from _data/fees.yml. Family = full minus 15 € a month, per period.
# ---------------------------------------------------------------------------
FULL = {'m': {'a': 39, 'c': 29}, 'q': {'a': 99, 'c': 75}, 'y': {'a': 360, 'c': 270}}
MONTHS = {'m': 1, 'q': 3, 'y': 12}
FAM = 15


def fam(p, c):
    return FULL[p][c] - FAM * MONTHS[p]


# Ana (17+, full), Marc (17+, family), Lía (≤16, family)
def household(p):
    return FULL[p]['a'] + fam(p, 'a') + fam(p, 'c')


H = {p: household(p) for p in 'mqy'}              # 77 / 183 / 630
BASE = {p: H['m'] * MONTHS[p] for p in 'mqy'}     # 77 / 231 / 924
# First charge with create_prorations: 20 Jan 18:00 → 5 Feb 08:00 UTC is
# 15.58 days, over the length of the interval that ends on the anchor.
DAYS = 15.58
PRO = {'m': H['m'] * DAYS / 31, 'q': H['q'] * DAYS / 92, 'y': H['y'] * DAYS / 365}


def eur(x):
    if abs(x - round(x)) < 0.005:
        return '%d €' % round(x)
    return ('%.2f €' % x).replace('.', ',')


CSS = """
@font-face{font-family:'Noto Sans';font-weight:400;font-style:normal;
  src:url(/fonts/noto-sans-400-latin.woff2) format('woff2')}
@font-face{font-family:'Noto Sans';font-weight:700;font-style:normal;
  src:url(/fonts/noto-sans-700-latin.woff2) format('woff2')}
@font-face{font-family:'Noto Sans';font-weight:400;font-style:normal;
  src:url(/fonts/noto-sans-400-latin-ext.woff2) format('woff2');
  unicode-range:U+0100-024F}
:root{
  --Black:#111314; --White:#fff; --Yellow:#FFF200; --YellowInk:#474400;
  --Rust:#ae5224; --Green:#1a7444; --Blue:#064F6E; --Slate:#34454C;
  --Red:#82241f; --Glaucous:#A5C8D1; --Sage:#B7C2A9;
  --Paper:#FBFAF7; --Mute:#5A686E; --Ink:#3D4A50; --Hair:rgba(17,19,20,.14);
  --display:Futura,"Century Gothic","Trebuchet MS",sans-serif;
}
*{box-sizing:border-box}
body{margin:0;background:#F1F1EE;color:var(--Black);
     font:16px/1.65 "Noto Sans",-apple-system,BlinkMacSystemFont,sans-serif}
.wrap{max-width:1500px;margin:0 auto;padding:2.5rem 2rem 6rem}
.pg{font:700 1.8rem/1.2 var(--display);letter-spacing:.04em;text-transform:uppercase;margin:0 0 .6rem}
.top-lede{max-width:50rem;color:var(--Ink);margin:0 0 1rem;font-size:.95rem}
.key{max-width:50rem;font-size:.92rem;color:var(--Ink);background:#fff;
     border-left:3px solid var(--Yellow);padding:.8rem 1.1rem;margin:0 0 1rem}
.warn{max-width:50rem;font-size:.92rem;color:var(--Ink);background:#fff;
      border-left:3px solid var(--Rust);padding:.8rem 1.1rem;margin:0 0 2.4rem}
.key b,.warn b{color:var(--Black)}
.tabs{display:flex;gap:.5rem;flex-wrap:wrap;margin:0 0 2rem}
.tabs a{font:700 .78rem/1 var(--display);letter-spacing:.08em;text-transform:uppercase;
        color:var(--Black);text-decoration:none;padding:.6rem .9rem;border:1px solid var(--Hair);background:#fff}
.tabs a[aria-current]{background:var(--Black);color:#fff;border-color:var(--Black)}
.sec-t{font:700 1.05rem/1.3 var(--display);letter-spacing:.07em;text-transform:uppercase;
       margin:3.2rem 0 1rem;padding-top:1rem;border-top:2px solid var(--Black)}
.row{display:grid;grid-template-columns:1000px 1fr;gap:2.4rem;align-items:start}
.row2{display:grid;grid-template-columns:375px 1fr;gap:2.4rem;align-items:start;margin-top:2.4rem}
@media(max-width:1460px){.row{grid-template-columns:1fr}}
.note h2{font:700 .95rem/1.3 var(--display);letter-spacing:.07em;text-transform:uppercase;margin:1.5rem 0 .45rem}
.note h2:first-child{margin-top:0}
.note p,.note li{max-width:36rem;font-size:.9rem;color:var(--Ink)}
.note p{margin:0 0 .75rem}
.note ul,.note ol{padding-left:1.1rem;margin:0 0 .8rem}
.note li{margin:0 0 .35rem}
.note b{color:var(--Black)}
.note code,.warn code,.key code{font:.8rem ui-monospace,Menlo,monospace;background:rgba(17,19,20,.06);padding:0 .2em}
.tag{display:inline-block;font:700 .66rem/1 var(--display);letter-spacing:.08em;text-transform:uppercase;
     padding:.3rem .45rem;margin-right:.35rem;vertical-align:.12em}
.tag-spec{background:var(--Sage);color:var(--Black)}
.tag-more{background:var(--Yellow);color:var(--Black)}
.tag-q{background:var(--Rust);color:#fff}

/* ---------------- the mocked site ---------------- */
.mk{width:1000px;background:#fff;box-shadow:0 1px 2px rgba(17,19,20,.14),0 12px 34px rgba(17,19,20,.11)}
.ph{width:375px;background:#fff;border:10px solid var(--Black);border-radius:34px;overflow:hidden;
    box-shadow:0 12px 34px rgba(17,19,20,.16)}
.nav{background:var(--Black);color:#fff;padding:.85rem 2.2rem;display:flex;align-items:baseline;gap:1.6rem}
.ph .nav{padding:.8rem 1rem;justify-content:space-between}
.nav b{font:700 1.05rem/1 var(--display);letter-spacing:.03em}
.nav span{font-size:.62rem;letter-spacing:.06em;color:rgba(255,255,255,.62)}
.in{padding:2.2rem 4rem 3rem}
.ph .in{padding:1.4rem 1rem 2rem}
.eyb{font:700 .72rem/1 var(--display);letter-spacing:.14em;text-transform:uppercase;color:var(--Mute);margin:0 0 .5rem}
.h1{font:700 2.1rem/1.15 var(--display);letter-spacing:.02em;margin:0 0 .7rem;text-wrap:balance}
.ph .h1{font-size:1.65rem}
.lede{font-size:.98rem;color:var(--Ink);max-width:40rem;margin:0 0 1rem}
.facts{display:flex;flex-wrap:wrap;gap:.4rem 1.4rem;margin:0 0 1.2rem;padding:0;list-style:none;font-size:.82rem;color:var(--Ink)}
.facts li::before{content:"";display:inline-block;width:.45rem;height:.45rem;background:var(--Green);margin-right:.45rem;vertical-align:.08em}
.member{font-size:.82rem;color:var(--Ink);margin:0 0 1.6rem}
.member a,.mk a,.ph a{color:var(--Black)}
.grid{display:grid;grid-template-columns:1fr 290px;gap:2.6rem;align-items:start}
.h2{font:700 1.2rem/1.25 var(--display);letter-spacing:.03em;margin:0 0 .25rem;display:flex;gap:.6rem;align-items:baseline}
.h2 i{font-style:normal;font-size:.75rem;color:var(--Mute);letter-spacing:.1em}
.sub{font-size:.84rem;color:var(--Ink);margin:0 0 .9rem}
.blk{padding:0 0 1.6rem;margin:0 0 1.6rem;border-bottom:1px solid var(--Hair)}
.blk:last-child{border-bottom:0}
fieldset{border:0;margin:0;padding:0;min-width:0}
legend{padding:0;font-weight:700;font-size:.86rem;margin:0 0 .5rem}
.req{font-weight:400;color:var(--Mute);font-size:.78rem}
.opts{display:grid;grid-template-columns:repeat(3,1fr);gap:.6rem}
.ph .opts{grid-template-columns:1fr}
.opt{position:relative;border:1px solid var(--Hair);border-radius:.3rem;padding:.75rem .85rem .7rem 2.3rem;font-size:.84rem;background:#fff}
.opt::before{content:"";position:absolute;left:.8rem;top:.95rem;width:1rem;height:1rem;border:2px solid var(--Slate);border-radius:50%;background:#fff}
.opt.on{border-color:var(--Black);box-shadow:inset 0 0 0 1px var(--Black)}
.opt.on::before{background:radial-gradient(circle,var(--Black) 0 38%,#fff 42%)}
.opt b{display:block;font-size:.9rem}
.opt .pr{font:700 1.15rem/1.2 var(--display);display:block;margin:.15rem 0}
.opt .pr small{font:400 .74rem "Noto Sans",sans-serif;color:var(--Mute)}
.opt .sv{display:block;font-size:.76rem;color:var(--Green);font-weight:700}
.opt .gift{display:block;font-size:.74rem;color:var(--Ink)}
.opt.box::before{border-radius:.2rem}
.opt.box.on::before{background:var(--Black);box-shadow:inset 0 0 0 2px #fff}
.cond{font-size:.78rem;color:var(--Ink);background:var(--Paper);border-left:3px solid var(--Glaucous);padding:.55rem .8rem;margin:.6rem 0 0}
.person{border:1px solid var(--Hair);border-radius:.3rem;padding:.9rem 1rem 1rem;margin:0 0 .7rem;background:#fff}
.person legend{float:left;width:100%;display:flex;justify-content:space-between;align-items:baseline;margin:0 0 .6rem}
.person legend + *{clear:both}
.rm{font-size:.76rem;font-weight:400;text-decoration:underline;color:var(--Black);min-height:24px;display:inline-flex;align-items:center}
.f2{display:grid;grid-template-columns:1fr 1fr;gap:.6rem .8rem}
.ph .f2{grid-template-columns:1fr}
.fld label{display:block;font-size:.78rem;font-weight:700;margin:0 0 .2rem}
.inp{display:block;width:100%;min-height:2.5rem;border:1px solid #7b878c;border-radius:.25rem;padding:.45rem .6rem;font-size:.9rem;background:#fff;color:var(--Black)}
.inp.ph-t{color:#7b878c}
.inp.sel{background:#fff linear-gradient(45deg,transparent 50%,var(--Black) 50%) no-repeat right .9rem center/.35rem .35rem}
.inp.bad{border-color:var(--Red);border-width:2px}
.err{font-size:.78rem;color:var(--Red);font-weight:700;margin:.25rem 0 0;display:flex;gap:.35rem}
.err::before{content:"!";display:inline-grid;place-items:center;width:1rem;height:1rem;border-radius:50%;background:var(--Red);color:#fff;font-size:.66rem;flex:none;margin-top:.12rem}
.chips{display:flex;gap:.4rem;flex-wrap:wrap;margin:0}
.fld-l{font-size:.78rem;font-weight:700;margin:.7rem 0 .25rem}
.chip{font-size:.8rem;border:1px solid #7b878c;border-radius:1.2rem;padding:.3rem .8rem;min-height:2rem;display:inline-flex;align-items:center;background:#fff}
.chip.on{background:var(--Black);color:#fff;border-color:var(--Black)}
.add{display:inline-flex;align-items:center;gap:.45rem;min-height:2.5rem;padding:.45rem .9rem;border:1px dashed var(--Slate);border-radius:.3rem;font-size:.85rem;font-weight:700;background:#fff}
.add::before{content:"+";font:700 1.1rem/1 var(--display)}
.hint{font-size:.76rem;color:var(--Mute);margin:.35rem 0 0}
.chk{display:grid;grid-template-columns:1.25rem 1fr;gap:.6rem;font-size:.84rem;margin:0 0 .7rem;align-items:start}
.chk::before{content:"";width:1.15rem;height:1.15rem;border:2px solid var(--Slate);border-radius:.2rem;margin-top:.15rem;background:#fff}
.chk.on::before{background:var(--Black);box-shadow:inset 0 0 0 2px #fff}
.chk.bad::before{border-color:var(--Red)}
.chk small{display:block;color:var(--Mute);font-size:.76rem}
.priv{font-size:.74rem;color:var(--Ink);border:1px solid var(--Hair);padding:.65rem .8rem;margin:.4rem 0 1rem;background:var(--Paper)}
.priv b{color:var(--Black)}
.btn{display:flex;width:100%;justify-content:center;align-items:center;gap:.6rem;min-height:3rem;background:var(--Black);color:#fff;
     font:700 .95rem/1 var(--display);letter-spacing:.06em;text-transform:uppercase;border-radius:.25rem;padding:.8rem 1rem}
.btn::after{content:"→"}
.btn-note{font-size:.76rem;color:var(--Mute);text-align:center;margin:.5rem 0 0}
.lock{display:inline-block;width:.7rem;height:.55rem;background:var(--Mute);border-radius:.1rem;position:relative;margin-right:.35rem;vertical-align:0}
.lock::before{content:"";position:absolute;left:.12rem;top:-.32rem;width:.46rem;height:.42rem;border:2px solid var(--Mute);border-bottom:0;border-radius:.3rem .3rem 0 0}

/* the receipt */
.rc{position:sticky;top:1rem;background:var(--Paper);border:1px solid var(--Hair);border-top:4px solid var(--Black);padding:1.1rem 1.1rem 1.2rem;font-size:.84rem}
.rc-t{font:700 .78rem/1 var(--display);letter-spacing:.12em;text-transform:uppercase;margin:0 0 .8rem}
.rc dl{margin:0;display:grid;grid-template-columns:1fr auto;gap:.3rem .8rem;font-variant-numeric:tabular-nums}
.rc dt{color:var(--Ink)}
.rc dt small{display:block;font-size:.72rem;color:var(--Mute)}
.rc dd{margin:0;text-align:right;font-weight:700}
.rc dd s{font-weight:400;color:var(--Mute);margin-right:.3rem;font-size:.76rem}
.rc .tot{border-top:2px solid var(--Black);margin-top:.7rem;padding-top:.6rem;display:flex;justify-content:space-between;align-items:baseline}
.rc .tot b{font:700 1.7rem/1 var(--display)}
.rc .tot span{font-size:.78rem;color:var(--Ink)}
.tl{list-style:none;margin:1rem 0 0;padding:0;border-left:2px solid var(--Black)}
.tl li{position:relative;padding:0 0 .7rem .9rem;font-size:.8rem;color:var(--Ink)}
.tl li::before{content:"";position:absolute;left:-.4rem;top:.35rem;width:.62rem;height:.62rem;border-radius:50%;background:#fff;border:2px solid var(--Black)}
.tl li.now::before{background:var(--Yellow)}
.tl b{color:var(--Black);font-variant-numeric:tabular-nums}
.rc-x{margin:.6rem 0 0;padding:.6rem 0 0;border-top:1px solid var(--Hair);font-size:.76rem;color:var(--Ink)}
.rc-x b{color:var(--Black)}
.gift-l{display:flex;gap:.5rem;align-items:flex-start;font-size:.78rem;margin:.8rem 0 0;padding:.5rem .6rem;background:#fff;border:1px solid var(--Hair)}
.gift-l::before{content:"";flex:none;width:.85rem;height:.85rem;margin-top:.18rem;background:var(--Yellow);border:1px solid var(--YellowInk)}
.live{font-size:.7rem;color:var(--Mute);margin:.6rem 0 0}

details.more{border-top:1px solid var(--Hair);font-size:.84rem}
details.more:last-of-type{border-bottom:1px solid var(--Hair)}
details.more summary{list-style:none;padding:.6rem 0;font-weight:700;display:flex;justify-content:space-between}
details.more summary::after{content:"+";font:700 1rem/1 var(--display)}

/* the error summary */
.esum{border:2px solid var(--Red);border-radius:.3rem;padding:.8rem .9rem;margin:0 0 1.2rem;outline:3px solid var(--Blue);outline-offset:2px}
.esum p{margin:0 0 .35rem;font-weight:700;font-size:.9rem;color:var(--Red)}
.esum ul{margin:0;padding-left:1.1rem;font-size:.82rem}
.esum a{color:var(--Red)}

/* B: the stepper */
.steps{display:flex;list-style:none;margin:0 0 1.8rem;padding:0;counter-reset:s;border-bottom:1px solid var(--Hair)}
.steps li{counter-increment:s;flex:1;padding:.55rem 0 .7rem;font-size:.8rem;color:var(--Mute);border-bottom:3px solid transparent;margin-bottom:-1px}
.steps li::before{content:counter(s);display:inline-grid;place-items:center;width:1.35rem;height:1.35rem;border-radius:50%;border:1.5px solid currentColor;margin-right:.45rem;font:700 .72rem/1 var(--display)}
.steps li.done{color:var(--Black)}
.steps li.done::before{content:"✓";background:var(--Black);color:#fff;border-color:var(--Black)}
.steps li.cur{color:var(--Black);font-weight:700;border-bottom-color:var(--Black)}
.ph .steps li{font-size:0;flex:none;margin-right:.4rem}
.ph .steps li.cur{font-size:.78rem;flex:1}
.ph .steps li::before{font-size:.72rem}
.done-sum{display:flex;justify-content:space-between;align-items:center;gap:1rem;border:1px solid var(--Hair);border-radius:.3rem;padding:.7rem 1rem;margin:0 0 1.4rem;background:var(--Paper);font-size:.84rem}
.done-sum b{font-weight:700}
.done-sum a{font-size:.8rem}
.who{display:flex;gap:.5rem;flex-wrap:wrap;margin:.3rem 0 0}
.who span{font-size:.76rem;background:#fff;border:1px solid var(--Hair);padding:.12rem .5rem;border-radius:1rem}
.opt.big{padding:1rem 1rem 1rem 2.4rem}
.opt.big .pr{font-size:1.55rem}
.opt .per{display:block;font-size:.74rem;color:var(--Mute);margin:.1rem 0 .3rem}
.flag{position:absolute;top:-.6rem;right:.7rem;font:700 .62rem/1 var(--display);letter-spacing:.09em;text-transform:uppercase;background:var(--Yellow);color:var(--Black);padding:.28rem .45rem}
.nav-b{display:flex;justify-content:space-between;align-items:center;margin:1.4rem 0 0}
.nav-b .btn{width:auto;padding:.8rem 1.5rem}
.back{font-size:.84rem}
.later{border:1px solid var(--Hair);border-radius:.3rem;padding:.7rem 1rem;margin:0 0 .5rem;color:var(--Mute);font-size:.84rem;display:flex;gap:.6rem}
.later::before{content:attr(data-n);display:inline-grid;place-items:center;width:1.35rem;height:1.35rem;border-radius:50%;border:1.5px solid currentColor;font:700 .72rem/1 var(--display)}
.rv{display:grid;grid-template-columns:1fr 1fr;gap:2rem}
.rv-t{width:100%;border-collapse:collapse;font-size:.84rem;font-variant-numeric:tabular-nums}
.rv-t th,.rv-t td{text-align:left;padding:.45rem .3rem;border-bottom:1px solid var(--Hair)}
.rv-t th{font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--Mute)}
.rv-t td:last-child,.rv-t th:last-child{text-align:right}
.rv-t tfoot td{border-bottom:0;border-top:2px solid var(--Black);font-weight:700;font-size:1rem}
.rv-edit{font-size:.78rem}

/* admin */
.mail{width:640px;background:#fff;border:1px solid var(--Hair);box-shadow:0 8px 24px rgba(17,19,20,.08);font-size:.88rem}
.mail-h{padding:.8rem 1.2rem;border-bottom:1px solid var(--Hair);font-size:.78rem;color:var(--Mute);background:var(--Paper)}
.mail-h b{color:var(--Black)}
.mail-b{padding:1.2rem 1.4rem 1.4rem}
.mail-b h3{font:700 1.2rem/1.25 var(--display);margin:0 0 .3rem}
.mail-b p{margin:0 0 .8rem;color:var(--Ink)}
.mail-b table{width:100%;border-collapse:collapse;font-size:.84rem;margin:0 0 1rem;font-variant-numeric:tabular-nums}
.mail-b td,.mail-b th{padding:.35rem .2rem;border-bottom:1px solid var(--Hair);text-align:left;vertical-align:top}
.mail-b th{font-size:.7rem;letter-spacing:.06em;text-transform:uppercase;color:var(--Mute)}
.todo{list-style:none;margin:0 0 1rem;padding:0}
.todo li{display:grid;grid-template-columns:1fr auto;gap:.8rem;align-items:center;padding:.55rem .7rem;border:1px solid var(--Hair);border-left:4px solid var(--Rust);margin:0 0 .4rem;font-size:.84rem}
.todo li small{display:block;color:var(--Mute);font-size:.76rem}
.todo .act{font:700 .72rem/1 var(--display);letter-spacing:.06em;text-transform:uppercase;padding:.5rem .7rem;border:1.5px solid var(--Black);white-space:nowrap}
.todo li.prop .act{background:var(--Yellow);border-color:var(--YellowInk)}
.mbtn{display:inline-block;background:var(--Black);color:#fff;font:700 .78rem/1 var(--display);letter-spacing:.06em;text-transform:uppercase;padding:.7rem 1rem}
.inv{width:100%;border-collapse:collapse;font-size:.84rem;background:#fff}
.inv th,.inv td{padding:.6rem .7rem;border-bottom:1px solid var(--Hair);text-align:left;vertical-align:top}
.inv thead th{font:700 .7rem/1.2 var(--display);letter-spacing:.09em;text-transform:uppercase;background:var(--Black);color:#fff}
.inv tbody th{font-weight:700;width:21%}
.inv td:nth-child(3){width:17%;color:var(--Ink)}
.inv tr.grp th{background:var(--Paper);font:700 .76rem/1.2 var(--display);letter-spacing:.1em;text-transform:uppercase;padding:.8rem .7rem .5rem}
.cnt{display:inline-block;min-width:1.5rem;text-align:center;font:700 .72rem/1.5 var(--display);background:var(--Black);color:#fff;border-radius:1rem;margin-left:.3rem}
.risk{color:var(--Rust);font-weight:700}
.stack{display:grid;grid-template-columns:640px 1fr;gap:2.4rem;align-items:start;margin:0 0 2.4rem}
@media(max-width:1200px){.stack{grid-template-columns:1fr}}
"""


TABS = (('inscripcion-pasos.html', '1 · The steps'),
        ('inscripcion-paginas.html', '2 · Members area, withdrawal, site'),
        ('inscripcion-correos.html', '3 · Member emails'),
        ('inscripcion-admin.html', '4 · Admin'),
        ('inscripcion-a.html', 'A · not chosen'))


def page(fname, title, active, body, extra=''):
    tabs = ''.join(
        '<a href="%s"%s>%s</a>' % (f, ' aria-current="page"' if f == active else '', t)
        for f, t in TABS)
    html = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<title>%s</title>\n<style>%s</style></head><body><div class="wrap">\n'
            '<nav class="tabs">%s</nav>\n%s\n</div></body></html>\n') % (title, CSS + extra, tabs, body)
    with open(os.path.join(OUT, fname), 'w', encoding='utf-8') as f:
        f.write(html)
    print('  docs/mockups/' + fname)


NAV = ('<div class="nav"><b>MUSUBI</b><span>Clases y horarios · Sobre nosotros · '
       'Cuotas · Calendario · Contacto</span></div>')
NAV_PH = '<div class="nav"><b>MUSUBI</b><span>MENÚ ☰</span></div>'

HEAD = """
<p class="eyb">Cuotas · Inscripción</p>
<h1 class="h1">Inscríbete y paga la cuota en línea</h1>
<p class="lede">Normalmente te inscribes después de las dos clases de prueba.
La inscripción es gratuita y la cuota se cobra sola el día 5, con tarjeta o
domiciliación SEPA, en una página segura de Stripe.</p>
<ul class="facts"><li>Sin matrícula</li><li>Todas las clases, en todos los espacios</li>
<li>Te das de baja cuando quieras</li><li>14 días de desistimiento</li></ul>
<p class="member">¿Ya eres miembro? <a href="#">Ve a tu área de miembros</a> para cambiar la tarjeta, descargar recibos o darte de baja.</p>
"""

HEAD_PH = """
<p class="eyb">Cuotas · Inscripción</p>
<h1 class="h1">Inscríbete y paga la cuota en línea</h1>
<p class="lede" style="font-size:.88rem">Después de las dos clases de prueba. Sin matrícula; la cuota se cobra el día 5 con tarjeta o SEPA, en una página segura de Stripe.</p>
"""


def period_opts(chosen='m', household=False, big=False):
    out = []
    labels = {'m': ('Mensual', 'al mes'), 'q': ('Trimestral', 'al trimestre'), 'y': ('Anual', 'al año')}
    for p in 'mqy':
        name, unit = labels[p]
        cls = 'opt' + (' on' if p == chosen else '') + (' big' if big else '')
        if household:
            price = eur(H[p])
            per = '' if p == 'm' else '<span class="per">%s al mes</span>' % eur(H[p] / MONTHS[p])
            save = '' if p == 'm' else '<span class="sv">Ahorras %s frente a mes a mes</span>' % eur(BASE[p] - H[p])
            gift = '' if p == 'm' else '<span class="gift">+ 3 keikogi de regalo</span>'
            flag = '<span class="flag">El que más ahorra</span>' if p == 'y' else ''
            out.append('<label class="%s">%s<b>%s</b><span class="pr">%s <small>%s</small></span>%s%s%s</label>'
                       % (cls, flag, name, price, unit, per, save, gift))
        else:
            price = eur(FULL[p]['a'])
            save = '' if p == 'm' else '<span class="sv">Ahorras %s</span>' % eur(FULL['m']['a'] * MONTHS[p] - FULL[p]['a'])
            gift = '' if p == 'm' else '<span class="gift">+ keikogi de regalo</span>'
            out.append('<label class="%s"><b>%s</b><span class="pr">%s <small>%s · 17+</small></span>%s%s</label>'
                       % (cls, name, price, unit, save, gift))
    return '<div class="opts">%s</div>' % ''.join(out)


def person(n, name, last, cat, full, removable=True, kid=False, ph=False, rate_row=False):
    rm = ('<a class="rm" href="#">Quitar a la persona %d: %s</a>' % (n, name)) if removable else ''
    cats = ('<p class="fld-l">Edad</p><div class="chips" role="radiogroup" aria-label="Edad">'
            '<span class="chip%s">17 años o más</span><span class="chip%s">Hasta 16 años</span></div>'
            % ('' if kid else ' on', ' on' if kid else ''))
    bday = ''
    if kid:
        bday = ('<div class="f2" style="margin-top:.6rem"><div class="fld"><label>Mes de nacimiento</label>'
                '<span class="inp sel">Marzo</span></div><div class="fld"><label>Año de nacimiento</label>'
                '<span class="inp sel">2014</span></div></div>'
                '<p class="hint">Solo el mes y el año, para aplicar la cuota hasta 16 y pasar a la de 17 o más a su tiempo.</p>')
    rate = ''
    if rate_row:
        rate = ('<p class="fld-l">Cuota</p><div class="chips" style="margin-top:0"><span class="chip on">General · todos los espacios</span>'
                '<span class="chip">Con abono municipal</span></div>')
    return ('<fieldset class="person"><legend><span>Persona %d</span>%s</legend>'
            '<div class="f2"><div class="fld"><label>Nombre</label><span class="inp">%s</span></div>'
            '<div class="fld"><label>Apellidos</label><span class="inp">%s</span></div></div>%s%s%s</fieldset>'
            % (n, rm, name, last, cats, bday, rate))


def receipt(p='m', tl=True):
    unit = {'m': 'al mes', 'q': 'al trimestre', 'y': 'al año'}[p]
    lines = (
        ('Ana García', '17 o más · cuota completa', None, FULL[p]['a']),
        ('Marc García', '17 o más · familia', FULL[p]['a'], fam(p, 'a')),
        ('Lía García', 'hasta 16 · familia', FULL[p]['c'], fam(p, 'c')),
    )
    dl = ''.join('<dt>%s<small>%s</small></dt><dd>%s%s</dd>'
                 % (n, s, ('<s>%s</s>' % eur(o)) if o else '', eur(v)) for n, s, o, v in lines)
    out = ('<aside class="rc" aria-labelledby="rc-t"><p class="rc-t" id="rc-t">Tu cuota</p><dl>%s</dl>'
           '<div class="tot"><span>Total %s</span><b>%s</b></div>' % (dl, unit, eur(H[p])))
    if tl:
        out += ('<ol class="tl"><li class="now"><b>Hoy, %s</b> · del 20 de enero al 4 de febrero</li>'
                '<li><b>5 de febrero, %s</b> · primera cuota completa</li>'
                '<li>Después, <b>%s</b> cada día 5%s</li></ol>'
                % (eur(PRO[p]), eur(H[p]), eur(H[p]),
                   '' if p == 'm' else (' de mayo, agosto y noviembre' if p == 'q' else ' de febrero')))
    if p != 'm':
        out += '<p class="gift-l"><span>3 keikogi de regalo, uno por persona. Los recogéis en el dojo.</span></p>'
    out += ('<p class="rc-x"><b>No incluido:</b> licencia federativa y seguro, 45 € al año por persona, '
            'que se pagan aparte en marzo.</p>'
            '<p class="live">La zona del total se anuncia al lector de pantalla cuando dejas de escribir.</p></aside>')
    return out


LEGAL = """
<div class="chk on"><span>Soy mayor de edad.</span></div>
<div class="chk on"><span>Soy madre, padre o tutor legal de las personas menores de 18 que he indicado.
<small>Aparece solo si hay alguien menor de 18.</small></span></div>
<div class="chk on"><span>He leído y acepto las <a href="#">condiciones de la cuota</a>.</span></div>
<div class="chk on"><span>Quiero empezar a entrenar antes de que acaben los 14 días de desistimiento.
<small>Si desisto, pagaré solo la parte de las clases ya disfrutada.</small></span></div>
<p class="priv"><b>Protección de datos.</b> Responsable: Associació Cultural Musubi Aikido.
Finalidad: gestionar tu inscripción y cobrar la cuota. Base: el contrato. Destinatarios:
Stripe, que procesa el pago (con transferencia a EE. UU. bajo el Data Privacy Framework).
Puedes ejercer tus derechos en info@aikidomusubi.com. <a href="#">Más información</a>.</p>
"""

LEGAL_SHORT = """
<div class="chk on"><span>Soy mayor de edad.</span></div>
<div class="chk on"><span>Soy madre, padre o tutor legal de las personas menores de 18 que he indicado.</span></div>
<div class="chk on"><span>Acepto las <a href="#">condiciones de la cuota</a>.</span></div>
<div class="chk on"><span>Quiero empezar antes de que acaben los 14 días de desistimiento.
<small>Si desisto, pagaré solo la parte ya disfrutada.</small></span></div>
"""

MORE = """
<details class="more"><summary>Cómo se calcula el primer cobro</summary></details>
<details class="more"><summary>Descuento familiar, con ejemplos</summary></details>
<details class="more"><summary>Cuota con abono municipal</summary></details>
<details class="more"><summary>Tarjeta o domiciliación SEPA</summary></details>
<details class="more"><summary>Cambiar la tarjeta, darte de baja, desistir</summary></details>
<details class="more"><summary>Lo que no está en la cuota</summary></details>
"""


# ===========================================================================
# A — plan first
# ===========================================================================
def build_a():
    desk = """
<div class="mk">%s<div class="in">%s
<div class="grid"><form>
<section class="blk"><h2 class="h2"><i>1</i>Cómo quieres pagar</h2>
<p class="sub">Elegido desde <a href="#">/cuotas/</a>: puedes cambiarlo aquí.</p>
<fieldset><legend>Periodo <span class="req">(obligatorio)</span></legend>%s</fieldset>
<fieldset style="margin-top:1.1rem"><legend>Cuota</legend>
<div class="opts" style="grid-template-columns:1fr 1fr">
<label class="opt on"><b>General</b>Todas las clases, en todos los espacios</label>
<label class="opt"><b>Con abono municipal</b>CxEM Espronceda o Marina-Besòs, solo ese espacio, mes a mes</label></div>
</fieldset></section>

<section class="blk"><h2 class="h2"><i>2</i>Quién entrena</h2>
<p class="sub">Personas del mismo núcleo familiar, hasta seis. Quien paga no tiene por qué entrenar.</p>
%s%s%s
<span class="add">Añadir otra persona</span>
</section>

<section class="blk"><h2 class="h2"><i>3</i>Quién paga</h2>
<p class="sub">Recibirás aquí los recibos y el código para entrar en tu área de miembros.
El nombre y la tarjeta o el IBAN los pide Stripe en el paso siguiente.</p>
<div class="f2"><div class="fld"><label>Correo electrónico <span class="req">(obligatorio)</span></label><span class="inp">ana.garcia@example.com</span></div>
<div class="fld"><label>Teléfono <span class="req">(opcional)</span></label><span class="inp">+34 600 000 000</span></div></div>
</section>

<section class="blk"><h2 class="h2"><i>4</i>Antes de pagar</h2>%s
<span class="btn">Continuar al pago seguro</span>
<p class="btn-note"><span class="lock"></span>Confirmarás el pago en Stripe. Hasta entonces no se cobra nada.</p>
</section>
<section>%s</section>
</form>
%s
</div></div></div>
""" % (NAV, HEAD, period_opts('m'),
       person(1, 'Ana', 'García López', 'a', True, removable=False),
       person(2, 'Marc', 'García López', 'a', False),
       person(3, 'Lía', 'García Ruiz', 'c', False, kid=True),
       LEGAL, MORE, receipt('m'))

    phone = """
<div class="ph">%s<div class="in">%s
<div class="esum" tabindex="-1"><p>Hay 2 cosas que corregir</p>
<ul><li><a href="#">Persona 3: el año de nacimiento da 17 años. Elige «17 años o más».</a></li>
<li><a href="#">Marca que eres madre, padre o tutor legal de Lía.</a></li></ul></div>
<h2 class="h2"><i>2</i>Quién entrena</h2>
<fieldset class="person"><legend><span>Persona 3</span><a class="rm" href="#">Quitar a la persona 3: Lía</a></legend>
<div class="f2"><div class="fld"><label>Nombre</label><span class="inp">Lía</span></div></div>
<div class="chips"><span class="chip">17 años o más</span><span class="chip on">Hasta 16 años</span></div>
<div class="f2" style="margin-top:.6rem"><div class="fld"><label>Año de nacimiento</label>
<span class="inp sel bad">2009</span>
<p class="err">Con este año Lía tiene 17. Elige «17 años o más».</p></div></div>
</fieldset>
<div style="height:1rem"></div>
<h2 class="h2"><i>4</i>Antes de pagar</h2>
<div class="chk bad"><span>Soy madre, padre o tutor legal de las personas menores de 18 que he indicado.</span></div>
<p class="err" style="margin-top:-.4rem">Marca esta casilla: Lía es menor de 18.</p>
<div style="height:1.2rem"></div>
%s
<div style="height:1.2rem"></div>
<span class="btn">Continuar al pago seguro</span>
</div></div>
""" % (NAV_PH, HEAD_PH, receipt('m', tl=True))

    body = """
<h1 class="pg">A · Plan first (not chosen: B was, on 14 October 2026)</h1>
<p class="top-lede">The order of <code>/cuotas/</code>, continued: the fee page's buttons
preselect the period and the age group, so the person lands with the first question already
answered and carries on down one page. A receipt beside the form totals every line as it
changes and shows exactly what is charged and when.</p>
<p class="key"><b>Household shown:</b> two people aged 17 or over and one up to 16, monthly:
39 + 24 + 14 = <b>77 € a month</b>, the spec's fourth worked example. Signing up on
20 January 2027, so today's charge is the 16 days to the 5th and the first full fee is on
5 February.</p>
<p class="warn"><b>Without JavaScript</b> the page is the same form with no live total:
the period and the people are submitted, the server prices them, and Stripe's last screen
states the amount. The six person blocks are <code>&lt;details&gt;</code> elements, so
"add another person" works with no script at all. The spec allows this; the mockup shows the
enhanced state.</p>

<div class="row">%s
<div class="note">
<h2>What it gets right</h2>
<ul>
<li><span class="tag tag-spec">spec</span><b>Continuity with /cuotas/.</b> The person chose a plan there; here it is already chosen.</li>
<li><span class="tag tag-spec">spec</span><b>Everything visible at once.</b> Nothing hides behind a "next", which is the easiest shape for keyboard, screen reader and 200 %% zoom.</li>
<li><span class="tag tag-more">more</span><b>The timeline in the receipt.</b> With proration the first month is two charges: <b>%s today</b>, then <b>77 € on 5 February</b>. A single "77 €" would be the first surprise on a bank statement. The spec asks for "the date and amount of the first charge"; this shows both charges.</li>
<li><span class="tag tag-more">more</span><b>Struck-through full price</b> beside each discounted line, so the family discount is seen being applied, not just stated.</li>
</ul>
<h2>Where it is weak</h2>
<ul>
<li><b>The period is chosen before the household is known.</b> The cards can only show the price for one person aged 17 or over. A family of three compares 39 € against 99 € and has to work out the rest itself, or watch the receipt.</li>
<li><b>The rate is per household.</b> The spec's form asks for it once, which cannot express a household where one person holds a CxEM membership and the others pay the general fee. Its own pricing rule (section 3.2) says that household exists.</li>
<li><b>The receipt is a second column.</b> On a phone it moves to the end, so the total is out of sight while the form is filled in.</li>
</ul>
<h2>Phone, after a failed submit</h2>
<p>The error summary takes focus and links to each field; every error sits next to its own
field. The same messages come back from the server when JavaScript is off (spec 5.5).</p>
</div></div>
<div class="row2">%s
<div class="note">
<h2>On a phone</h2>
<p>One column. The receipt comes after the people and before the button, so it is read
at the moment of deciding. It is <b>not</b> sticky: a sticky total on a 667px screen
covers the field being typed into, which WCAG 2.2 forbids (2.4.11), and the spec says so.</p>
<p>All targets are at least 24px; the chips and checkboxes are 32 to 40px.</p>
</div></div>
""" % (desk, eur(PRO['m']), phone)
    page('inscripcion-a.html', 'Signup A', 'inscripcion-a.html', body)


# ===========================================================================
# Admin
# ===========================================================================
INVENTORY = [
    ('Once, before launch (Juanma)', [
        ('Cloudflare', 'Create the Worker, the KV store and the cron; point <code>api.aikidomusubi.com</code> at it; store the secrets, test and live separately.', 'Cloudflare dashboard', 'Once. I can write every config file; the clicks and the secrets are yours.'),
        ('Email provider', 'Choose one (EU hosting, DPA), verify aikidomusubi.com with SPF, DKIM and DMARC, create the <code>admin@</code> mailbox and the no-reply sender.', 'Provider + Cloudflare DNS', 'Once.'),
        ('Stripe account', 'The 7.2 checklist: public details, branding, card and SEPA on (SEPA needs extra identity checks, which take days), customer emails, renewal events at 15 days, Smart Retries ending in past due, invoice footer, portal and its login link, 2FA for everyone, webhooks, restricted key.', 'Stripe dashboard', 'Once per mode. About an hour, plus SEPA verification.'),
        ('Products and prices', 'Run <code>npm run stripe:setup -- --mode test</code>, later <code>--mode live</code>, with the full secret key on your own machine.', 'Terminal', 'Twice.'),
        ('Advisors', 'Legal review of the terms, privacy, cookies, accessibility statement and the email wording. Tax: the VAT-exemption reference for the invoice footer and the open Verifactu question.', 'Email', '<span class="risk">Blocks launch.</span>'),
        ('Records of processing', 'Add the new processing activity and run the AEPD self-assessment.', 'Your documents', 'Once.'),
    ]),
    ('Moving existing members, December 2026 to January 2027', [
        ('Written notice', 'Tell every member about the 2027 prices and the move to Stripe, by 1 December.', 'Email', 'Once. I can draft it in four languages.'),
        ('One invite per member', '<code>npm run invite -- --email … --proration none</code>, then send each link.', 'Terminal + email', '× number of members. Could be a CSV in, emails out.'),
        ('Leave them out of the bank remittance', 'From the first month Stripe charges them. Until then they stay on the bank remittance.', 'Your bank\'s remittance', '<span class="risk">The riskiest step: forget one and they pay twice that month.</span> The third email lists them.'),
        ('Chase the stragglers', 'Members who have not used their invite by their next bank debit.', 'Phone, in person', 'Per member.'),
    ]),
    ('Every new signup', [
        ('Read the notification', 'Who, which plan, first charge, flags.', 'admin@ mailbox', 'Every signup.'),
        ('Paper registration form', 'Collect it at the dojo, with the guardian\'s signature for a minor and the image-use form. It is the only place that holds the ID number, the date of birth and the health information.', 'At the dojo', 'Every signup. Unchanged from today.'),
        ('Sports-centre membership', 'Check the card in person; set <code>sc_verification</code> to <code>verified</code>. If it is not valid, change that person\'s price and tell the family.', 'Stripe metadata', 'Some signups. <span class="risk">Hand-editing metadata.</span>'),
        ('Keikogi', 'Hand them over once the first full quarter or year is paid (an email says when); mark them delivered.', 'Stripe metadata', 'Quarterly and annual signups. <span class="risk">Hand-editing a list in a text field</span>, unless the email button is approved.'),
    ]),
    ('When something happens', [
        ('Failed payment', 'Stripe retries and emails the member. After the last retry the subscription stays past due, and the dojo follows up in person.', 'Email, then Stripe', 'Occasional.'),
        ('Cancellation by email, phone or at the dojo', 'Cancel at the end of the paid period in the dashboard. In the portal it happens by itself.', 'Stripe', 'Occasional.'),
        ('Withdrawal (14 days)', 'Cancel at once and refund what is owed, minus the classes already given, within 14 days, by the same payment method.', 'Stripe', 'Rare. <span class="risk">The proportional amount is calculated by hand.</span>'),
        ('Change of plan or people', 'Print the line items with the small CLI and apply them from the next billing date.', 'Terminal + Stripe', 'Occasional. <span class="risk">Changing the period in the dashboard moves the billing date off the 5th.</span>'),
        ('Change of email', 'Edit the customer in Stripe: the no-code portal cannot.', 'Stripe', 'Rare.'),
        ('Data requests', 'Answer within a month.', 'info@', 'Rare.'),
    ]),
    ('Every month, from the digest on the 20th', [
        ('Turning 17', 'Move that person to the 17-and-over price from the next charge, tell the family, then delete their <code>mN_birth_ym</code>.', 'Stripe', 'A few a year. <span class="risk">Hand-editing line items and metadata.</span>'),
        ('Pending sports-centre checks', 'Any still pending after 30 days: ask for the card.', 'At the dojo', 'Rare.'),
    ]),
    ('Every year', [
        ('Licence and insurance', 'Still collected outside Stripe in March, 45 € each, as today.', 'As today', 'Once. Moves into Stripe in a later version.'),
        ('Price change', 'New catalogue version, the setup script, the migration dry run and the real run, then a written notice at least a month ahead.', 'Terminal + email', 'When prices change.'),
        ('Retention clean-up', 'Delete the customers the yearly script lists.', 'Stripe', 'Once.'),
        ('Keys and compliance', 'Rotate the keys; confirm SAQ A in Stripe.', 'Stripe, Cloudflare', 'Once.'),
    ]),
]


def build_admin():
    mail1 = """
<div class="mail"><div class="mail-h">De: <b>Inscripciones</b> &lt;no-reply@aikidomusubi.com&gt; · Para: admin@aikidomusubi.com<br>
Asunto: <b>Nueva inscripción · 3 personas · trimestral · primer cobro 5 feb</b></div>
<div class="mail-b"><h3>Nueva inscripción</h3>
<p>20 de enero de 2027, 18:04. Pago con domiciliación SEPA.</p>
<table><thead><tr><th>Persona</th><th>Edad</th><th>Cuota</th><th>Al trimestre</th></tr></thead><tbody>
<tr><td>Ana García</td><td>17 o más</td><td>Completa</td><td>99 €</td></tr>
<tr><td>Marc García</td><td>17 o más</td><td>Familia</td><td>54 €</td></tr>
<tr><td>Lía García</td><td>Hasta 16</td><td>Familia</td><td>30 €</td></tr>
<tr><td colspan="3"><b>Total</b></td><td><b>183 €</b></td></tr></tbody></table>
<p><b>Pendiente en el dojo</b></p>
<ul class="todo">
<li>Recoger la hoja de inscripción en papel<small>Lía es menor: con la firma de su madre, padre o tutor, y la autorización de imagen.</small><span></span></li>
<li class="prop">3 keikogi: Ana, Marc y Lía<small>Cuando se cobre el trimestre del 5 de febrero. Ese día os llega otro aviso, y a la familia también.</small><span class="act">Entregados</span></li>
</ul>
<span class="mbtn">Abrir en Stripe</span>
<p style="margin-top:1rem;font-size:.76rem;color:var(--Mute)">Sin teléfonos, fechas de nacimiento ni datos de pago, a propósito.</p>
</div></div>"""

    mail2 = """
<div class="mail"><div class="mail-h">Para: admin@aikidomusubi.com · 20 de febrero de 2027<br>
Asunto: <b>Cuotas: 3 cosas antes del cobro del 5 de marzo</b></div>
<div class="mail-b"><h3>Antes del cobro del 5 de marzo</h3>
<p><b>Cumplen 17</b></p>
<ul class="todo">
<li class="prop">Pol Serra cumple 17 en febrero<small>Familia Serra, mensual. Su cuota pasa de 14 € a 24 € al mes desde el cobro del 5 de marzo. Total de la familia: 53 € → 63 €.</small><span class="act">Aplicar y avisar</span></li>
</ul>
<p><b>Abono municipal sin comprobar desde hace más de 30 días</b></p>
<ul class="todo">
<li class="prop">Joan Puig · CxEM Espronceda · desde el 12 de enero<span class="act">Comprobado</span></li>
</ul>
<p><b>Cobros pendientes</b></p>
<ul class="todo">
<li>Familia Roca · 77 € · el banco rechazó la domiciliación del 5 de febrero<small>Stripe lo reintentó 4 veces. La cuota sigue activa, pendiente de pago.</small><span class="act">Abrir</span></li>
</ul>
</div></div>"""

    mail3 = """
<div class="mail"><div class="mail-h">Para: admin@aikidomusubi.com · 25 de enero de 2027<br>
Asunto: <b>Remesa del banco de febrero: no incluyas a estas 35 personas</b></div>
<div class="mail-b"><h3>Antes de la remesa de febrero</h3>
<p>Estas personas ya pagan por Stripe: su primer cobro es el 5 de febrero. <b>No las incluyas en la
remesa del banco de febrero</b>, o pagarán dos veces ese mes.</p>
<table><thead><tr><th>Persona</th><th>Primer cobro por Stripe</th></tr></thead><tbody>
<tr><td>Marta Vidal</td><td>5 feb · programado</td></tr>
<tr><td>Familia Serra (2)</td><td>5 feb · programado</td></tr>
<tr><td colspan="2" style="color:var(--Mute)">… 32 más</td></tr></tbody></table>
<p style="font-size:.84rem">(Cifras de ejemplo.) Quedan <b>11</b> sin pasar a Stripe: esas siguen en la remesa.
<b>4</b> no han abierto la invitación.</p>
<span class="mbtn">Ver la lista completa</span>
</div></div>"""

    rows = []
    total = 0
    for grp, items in INVENTORY:
        rows.append('<tr class="grp"><th colspan="4">%s <span class="cnt">%d</span></th></tr>' % (grp, len(items)))
        for k, what, where, often in items:
            total += 1
            rows.append('<tr><th>%s</th><td>%s</td><td>%s</td><td>%s</td></tr>' % (k, what, where, often))
    inv = ('<table class="inv"><thead><tr><th>Task</th><th>What it involves</th><th>Where</th>'
           '<th>How often, and the catch</th></tr></thead><tbody>%s</tbody></table>' % ''.join(rows))

    body = """
<h1 class="pg">Admin · what the dojo receives, and what it does by hand</h1>
<p class="top-lede">In the spec, the admin side is the Stripe dashboard, the <code>admin@</code>
mailbox and a few terminal commands. There is no back office to build, because Stripe is the
record. These are the three emails that arrive, and below them every task the spec leaves
to a person.</p>
<p class="key"><b>Buttons in yellow are a proposal, not the spec.</b> The spec has the dojo mark
keikogi, sports-centre checks and age changes by editing Stripe metadata by hand, in a
text field, one subscription at a time. The proposal is to put a button in the email for each.
Each button opens a confirmation page on the Worker, signed and expiring, and the change is
made only when that page's own button is pressed. That second press matters, because mail
scanners open every link in an email. No login and no database, and nobody types
<code>keikogi_due=m1,m3</code> into a box.</p>

<h2 class="sec-t">Every signup</h2>
<div class="stack">%s
<div class="note">
<h2>The notification</h2>
<p><span class="tag tag-spec">spec</span>Names, plan, first charge, the flags, a link to Stripe.
No phone numbers, no dates of birth, no payment details (spec 8.1).</p>
<p><span class="tag tag-more">more</span>The flags as a to-do list with a button each. In the spec they are a
reminder line, and resolving them means finding the subscription in Stripe and editing
metadata.</p>
<p>The paper form has no button: there is nothing to record online, because the online
side deliberately does not hold what that form holds.</p>
</div></div>

<h2 class="sec-t">Every month, on the 20th</h2>
<div class="stack">%s
<div class="note">
<h2>The digest</h2>
<p><span class="tag tag-spec">spec</span>Who turns 17 before the next charge; sports-centre
checks pending for over 30 days.</p>
<p><span class="tag tag-more">more</span>The new amounts are already worked out by the
pricing engine, so "apply" is one press and the family's email goes with it. The spec's
alternative is an <code>AUTO_AGE_UPGRADE</code> flag that does it unattended. This sits
between the two: the dojo still decides, but nobody edits line items.</p>
<p><span class="tag tag-more">more</span>Past-due subscriptions listed here as well, so
nothing depends on remembering an email from three weeks ago.</p>
</div></div>

<h2 class="sec-t">January 2027 only: the move from the bank remittance</h2>
<div class="stack">%s
<div class="note">
<h2>Not in the spec, and the one I would insist on</h2>
<p>The spec says to cancel each member's bank debit "only after their first Stripe charge
succeeds". If the bank debit for February goes out before the Stripe charge on 5 February, that
rule makes the member pay twice for February.</p>
<p>The safe rule is the other way round: <b>a member leaves the bank remittance for the first
month that Stripe charges</b>. If that first Stripe charge then fails, the dojo chases it, as it
would any failed payment.</p>
<p><span class="tag tag-more">more</span>A few days before each remittance, this list: who
to leave out, and who is still on the bank. <span class="tag tag-q">confirm</span> On what day
does the dojo send its remittance to the bank?</p>
</div></div>

<h2 class="sec-t">Every manual task, %d of them</h2>
<p class="top-lede">Orange is where a person editing Stripe by hand can get it wrong. The
spec's architecture is sound; these are where its admin experience is thin.</p>
%s
""" % (mail1, mail2, mail3, total, inv)
    page('inscripcion-admin.html', 'Signup admin', 'inscripcion-admin.html', body)


if __name__ == '__main__':
    build_a()
    build_admin()
