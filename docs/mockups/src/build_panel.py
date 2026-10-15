#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The membership panel: the dojo's back office, for a volunteer.

WHO IT IS FOR. Not the person who built it. Somebody at the dojo who receives
the paper forms, hands over the keikogi and checks a sports-centre card, on a
phone at the edge of the mat as often as on a laptop at home. Spanish, plain
words, one obvious button per thing to do, and nothing they can break by
pressing the wrong one: every quick action can be undone, and the two that
change what a family pays ask first.

THREE QUESTIONS, THREE SCREENS:

    Pendiente   what do I have to do?          the to-do list, grouped
    Miembros    who are our members?           search, filters, one card each
    a family    what is going on with them?    people, plan, history, actions

Money (payments, refunds, the card or account) stays in Stripe, one click away
on each family, because that is where it is done properly.

Every figure is from _data/fees.yml; the people are invented.

    python3 docs/mockups/src/build_panel.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'panel-cuotas.html')

CSS = r"""
@font-face{font-family:'Noto Sans';font-weight:400;src:url(/fonts/noto-sans-400-latin.woff2) format('woff2')}
@font-face{font-family:'Noto Sans';font-weight:700;src:url(/fonts/noto-sans-700-latin.woff2) format('woff2')}
@font-face{font-family:'Noto Sans';font-weight:400;src:url(/fonts/noto-sans-400-latin-ext.woff2) format('woff2');unicode-range:U+0100-024F}
:root{
  --black:#111314; --ink:#3D4A50; --mute:#5A686E; --line:rgba(17,19,20,.12); --line2:rgba(17,19,20,.07);
  --paper:#F6F5F1; --card:#FFFFFF; --yellow:#FFF200; --yink:#474400;
  --green:#1a7444; --greenbg:#E8F2EC; --rust:#ae5224; --rustbg:#FBEFE8; --blue:#064F6E; --bluebg:#E6EFF3;
  --red:#82241f; --redbg:#F7E9E8;
  --display:Futura,"Century Gothic","Trebuchet MS",sans-serif;
}
*{box-sizing:border-box}
body{margin:0;background:#E9E8E3;color:var(--black);font:15px/1.55 "Noto Sans",-apple-system,BlinkMacSystemFont,sans-serif}
.wrap{max-width:1560px;margin:0 auto;padding:2.5rem 2rem 6rem}
.pg{font:700 1.8rem/1.2 var(--display);letter-spacing:.04em;text-transform:uppercase;margin:0 0 .6rem}
.lede{max-width:52rem;color:var(--ink);margin:0 0 1rem}
.key{max-width:52rem;font-size:.92rem;color:var(--ink);background:#fff;border-left:3px solid var(--yellow);padding:.8rem 1.1rem;margin:0 0 1rem}
.key b{color:var(--black)}
.sec{font:700 1.05rem/1.3 var(--display);letter-spacing:.07em;text-transform:uppercase;margin:3.2rem 0 1rem;padding-top:1rem;border-top:2px solid var(--black)}
.row{display:grid;grid-template-columns:1180px 1fr;gap:2.4rem;align-items:start}
.row2{display:grid;grid-template-columns:repeat(2,390px) 1fr;gap:2rem;align-items:start}
@media(max-width:1500px){.row,.row2{grid-template-columns:1fr}}
.note h3{font:700 .92rem/1.3 var(--display);letter-spacing:.07em;text-transform:uppercase;margin:1.3rem 0 .4rem}
.note h3:first-child{margin-top:0}
.note p,.note li{font-size:.88rem;color:var(--ink);max-width:34rem}
.note ul{padding-left:1.1rem;margin:0 0 .6rem}
.note b{color:var(--black)}
.note code{font:.78rem ui-monospace,Menlo,monospace;background:rgba(17,19,20,.06);padding:0 .2em}

/* ---------- the app ---------- */
.app{width:1180px;background:var(--paper);box-shadow:0 1px 2px rgba(17,19,20,.15),0 14px 40px rgba(17,19,20,.12);border-radius:10px;overflow:hidden}
.phone{width:390px;background:var(--paper);border:10px solid var(--black);border-radius:40px;overflow:hidden;box-shadow:0 14px 40px rgba(17,19,20,.18);position:relative}
.top{display:flex;align-items:center;gap:1rem;background:var(--black);color:#fff;padding:.85rem 1.6rem}
.top .mark{width:32px;height:32px;display:block;border-radius:7px;box-shadow:0 0 0 1px rgba(255,255,255,.2)}
.top .mark svg{width:32px;height:32px;display:block}
.top b{font:700 1rem/1 var(--display);letter-spacing:.06em;text-transform:uppercase}
.top .sp{flex:1}
.top .who{font-size:.8rem;color:rgba(255,255,255,.7)}
.nav{display:flex;gap:.3rem;padding:0 1.6rem;background:var(--black)}
.nav a{color:rgba(255,255,255,.72);text-decoration:none;font-size:.9rem;padding:.65rem .9rem .75rem;border-bottom:3px solid transparent;display:flex;gap:.45rem;align-items:center}
.nav a.on{color:#fff;font-weight:700;border-bottom-color:var(--yellow)}
.nav .n{font:700 .72rem/1 var(--display);background:var(--yellow);color:var(--black);border-radius:1rem;padding:.2rem .45rem}
.nav a:not(.on) .n{background:rgba(255,255,255,.18);color:#fff}
.body{padding:1.6rem 1.6rem 2rem}
.phone .body{padding:1.1rem 1rem 6rem}
.hello{font:700 1.55rem/1.2 var(--display);margin:0 0 .2rem}
.sub{color:var(--ink);margin:0 0 1.3rem;font-size:.93rem}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:.8rem;margin:0 0 1.6rem}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.85rem 1rem}
.stat b{display:block;font:700 1.6rem/1.1 var(--display)}
.stat span{font-size:.8rem;color:var(--mute)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:1.1rem}
.group{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:0 0 1.1rem}
.gh{display:flex;align-items:center;gap:.7rem;padding:.85rem 1.1rem;border-bottom:1px solid var(--line2)}
.gh .ic{width:34px;height:34px;border-radius:9px;display:grid;place-items:center;flex:none}
.gh .ic svg{width:19px;height:19px}
.gh h2{margin:0;font:700 1rem/1.25 var(--display);letter-spacing:.02em}
.gh p{margin:0;font-size:.78rem;color:var(--mute)}
.gh .cnt{margin-left:auto;font:700 .8rem/1 var(--display);border-radius:1rem;padding:.3rem .55rem;background:var(--rustbg);color:var(--rust)}
.task{display:flex;align-items:center;gap:.9rem;padding:.8rem 1.1rem;border-bottom:1px solid var(--line2)}
.task:last-child{border-bottom:0}
.av{width:38px;height:38px;border-radius:50%;flex:none;display:grid;place-items:center;font:700 .85rem/1 var(--display);color:var(--black);background:#ECEAE3}
.tx{flex:1;min-width:0}
.tx b{display:block;font-size:.95rem}
.tx span{display:block;font-size:.8rem;color:var(--mute)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:.4rem;min-height:40px;padding:.5rem .95rem;border-radius:8px;font:700 .85rem/1 "Noto Sans",sans-serif;white-space:nowrap;border:1.5px solid var(--black);background:var(--black);color:#fff}
.btn.sec2{background:#fff;color:var(--black)}
.btn.ghost{background:transparent;border-color:transparent;color:var(--black);text-decoration:underline;padding-inline:.4rem}
.btn.warn{background:#fff;color:var(--red);border-color:rgba(130,36,31,.45)}
.btn svg{width:16px;height:16px}
.btn.big{min-height:48px;font-size:.95rem;padding:.6rem 1.2rem}
.btns{display:flex;gap:.45rem;flex-wrap:wrap;justify-content:flex-end}
.chip{display:inline-flex;align-items:center;gap:.3rem;font-size:.74rem;font-weight:700;border-radius:1rem;padding:.2rem .55rem;white-space:nowrap}
.chip.ok{background:var(--greenbg);color:var(--green)}
.chip.todo{background:var(--rustbg);color:var(--rust)}
.chip.wait{background:#EFEEEA;color:var(--mute)}
.chip.info{background:var(--bluebg);color:var(--blue)}
.chip.bad{background:var(--redbg);color:var(--red)}
.chip::before{content:"";width:.5rem;height:.5rem;border-radius:50%;background:currentColor}
.done{display:flex;align-items:center;gap:.9rem;padding:.75rem 1.1rem;background:var(--greenbg);color:var(--green);font-size:.88rem;font-weight:700}
.done .btn{margin-left:auto;border-color:var(--green);color:var(--green);background:transparent;min-height:34px}
.toast{position:absolute;left:12px;right:12px;bottom:76px;background:var(--black);color:#fff;border-radius:12px;padding:.8rem 1rem;display:flex;align-items:center;gap:.8rem;font-size:.88rem;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.toast b{color:var(--yellow);margin-left:auto;font-size:.88rem}
.tabbar{position:absolute;left:0;right:0;bottom:0;background:#fff;border-top:1px solid var(--line);display:grid;grid-template-columns:repeat(3,1fr);padding:.45rem 0 .9rem}
.tabbar a{display:flex;flex-direction:column;align-items:center;gap:.15rem;font-size:.72rem;color:var(--mute);text-decoration:none}
.tabbar a.on{color:var(--black);font-weight:700}
.tabbar svg{width:22px;height:22px}
.search{display:flex;gap:.7rem;align-items:center;margin:0 0 1rem}
.search .in{flex:1;display:flex;align-items:center;gap:.6rem;background:#fff;border:1.5px solid var(--line);border-radius:10px;padding:.65rem .9rem;color:var(--mute);font-size:.92rem}
.search svg{width:18px;height:18px}
.filters{display:flex;gap:.4rem;flex-wrap:wrap;margin:0 0 1.1rem}
.filters span{font-size:.82rem;border:1px solid var(--line);background:#fff;border-radius:2rem;padding:.4rem .85rem}
.filters span.on{background:var(--black);color:#fff;border-color:var(--black);font-weight:700}
.fam{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:.95rem 1.1rem;margin:0 0 .7rem;display:grid;grid-template-columns:1fr auto;gap:.4rem 1rem;align-items:center}
.fam h3{margin:0;font-size:1rem}
.fam .meta{font-size:.82rem;color:var(--mute)}
.fam .chips{display:flex;gap:.35rem;flex-wrap:wrap;grid-column:1/-1}
.fam .ppl{font-size:.85rem;color:var(--ink)}
.fam.sel{outline:2px solid var(--black)}
.split{display:grid;grid-template-columns:1fr 470px;gap:1.2rem;align-items:start}
.panel{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.ph{padding:1.1rem 1.3rem;border-bottom:1px solid var(--line2)}
.ph h2{margin:0 0 .15rem;font:700 1.3rem/1.2 var(--display)}
.ph p{margin:0;font-size:.85rem;color:var(--mute)}
.pb{padding:1rem 1.3rem}
.pb h4{font:700 .72rem/1 var(--display);letter-spacing:.12em;text-transform:uppercase;color:var(--mute);margin:1rem 0 .6rem}
.pb h4:first-child{margin-top:0}
.person{display:grid;grid-template-columns:auto 1fr;gap:.2rem .8rem;padding:.7rem 0;border-bottom:1px solid var(--line2)}
.person:last-of-type{border-bottom:0}
.person .av{grid-row:span 2}
.person b{font-size:.95rem}
.person .chips{display:flex;gap:.3rem;flex-wrap:wrap}
.kv{display:grid;grid-template-columns:auto 1fr;gap:.35rem 1rem;font-size:.88rem;margin:0}
.kv dt{color:var(--mute)}
.kv dd{margin:0;font-weight:700;text-align:right}
.tl{list-style:none;margin:0;padding:0;border-left:2px solid var(--line);font-size:.84rem}
.tl li{position:relative;padding:0 0 .6rem .9rem;color:var(--ink)}
.tl li::before{content:"";position:absolute;left:-.38rem;top:.4rem;width:.6rem;height:.6rem;border-radius:50%;background:#fff;border:2px solid var(--black)}
.tl li.g::before{background:var(--green);border-color:var(--green)}
.tl b{color:var(--black)}
.tl small{color:var(--mute);margin-right:.35rem}
.actions{display:grid;gap:.5rem;padding:1rem 1.3rem;border-top:1px solid var(--line2);background:#FBFAF7}
.actions .btn{width:100%;justify-content:flex-start}
.actions p{margin:.2rem 0 0;font-size:.78rem;color:var(--mute)}
.modal-bg{position:absolute;inset:0;background:rgba(17,19,20,.45);display:flex;align-items:flex-end}
.modal{background:#fff;border-radius:18px 18px 0 0;padding:1.3rem 1.2rem 1.6rem;width:100%}
.modal h3{margin:0 0 .5rem;font:700 1.2rem/1.25 var(--display)}
.modal p{margin:0 0 .8rem;font-size:.9rem;color:var(--ink)}
.modal .sum{background:var(--paper);border-radius:10px;padding:.7rem .9rem;font-size:.88rem;margin:0 0 1rem}
.modal .sum div{display:flex;justify-content:space-between;padding:.15rem 0}
.modal .btn{width:100%;margin:0 0 .5rem}
.empty{text-align:center;padding:2.2rem 1rem}
.empty .ok{width:64px;height:64px;border-radius:50%;background:var(--greenbg);display:grid;place-items:center;margin:0 auto .9rem}
.empty .ok svg{width:30px;height:30px;color:var(--green)}
.empty h2{font:700 1.3rem/1.2 var(--display);margin:0 0 .3rem}
.empty p{color:var(--mute);font-size:.9rem;margin:0}
.login{background:#fff;padding:2rem 1.4rem 4rem}
.login .card{border:1px solid var(--line);border-radius:12px;padding:1.3rem}
.login h3{font:700 1.15rem/1.25 var(--display);margin:0 0 .4rem}
.login p{font-size:.88rem;color:var(--ink)}
.login .in{border:1.5px solid #7b878c;border-radius:8px;padding:.7rem .8rem;margin:.3rem 0 .8rem;font-size:.95rem}
.cf{font-size:.72rem;color:var(--mute);text-align:center;margin-top:1rem}
.phone .task{flex-wrap:wrap;row-gap:.55rem}
.phone .task .btns{flex-basis:100%;justify-content:flex-start;padding-left:calc(38px + .9rem)}
.phone .gh{align-items:flex-start}
.help{display:flex;gap:.6rem;align-items:flex-start;background:var(--bluebg);color:var(--blue);border-radius:10px;padding:.7rem .9rem;font-size:.84rem;margin:0 0 1rem}
.help svg{flex:none;width:18px;height:18px;margin-top:.1rem}
"""

# Icons: simple strokes, drawn here so the mockup needs nothing external.
def I(name):
    p = {
        'paper': '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 16h5"/>',
        'gi': '<path d="M8 3l4 3 4-3 4 4-3 3v11H7V10L4 7z"/><path d="M12 6v15"/>',
        'card': '<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18M7 15h4"/>',
        'cake': '<path d="M4 21h16v-7H4zM4 17h16M12 14V9M12 5v.01"/>',
        'euro': '<path d="M17 6a7 7 0 1 0 0 12M5 10h9M5 14h9"/>',
        'check': '<path d="M5 12l4 4 10-10"/>',
        'search': '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
        'list': '<path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01"/>',
        'people': '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M16 11a3 3 0 1 0 0-6M17 14c2.3.5 4 2.6 4 5"/>',
        'help': '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.5V14M12 17h.01"/>',
        'ext': '<path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6"/>',
        'undo': '<path d="M9 14L4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 0 12h-3"/>',
        'door': '<path d="M5 21V4h10v17M15 12h.01M15 4l4 1v16"/>',
        'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/>',
    }[name]
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{p}</svg>')

# The mark is the site's own favicon, read from the file, not redrawn.
with open(os.path.join(HERE, '..', '..', '..', 'icons', 'musubi2-knot.svg'), encoding='utf-8') as f:
    KNOT = f.read().strip().replace('<svg ', '<svg aria-hidden="true" ', 1)

TOP = (f'<div class="top"><span class="mark">{KNOT}</span><b>Cuotas</b><span class="sp"></span>'
       '<span class="who">Marta R. · Salir</span></div>')


def nav(on, n=7, m=41):
    tabs = [('Pendiente', n), ('Miembros', m), ('Ayuda', None)]
    out = ''.join(f'<a class="{"on" if t == on else ""}">{t}{f" <span class=n>{c}</span>" if c else ""}</a>' for t, c in tabs)
    return f'<div class="nav">{out}</div>'


def tabbar(on):
    t = [('Pendiente', 'list'), ('Miembros', 'people'), ('Ayuda', 'help')]
    return '<div class="tabbar">' + ''.join(f'<a class="{"on" if a == on else ""}">{I(i)}{a}</a>' for a, i in t) + '</div>'


def group(icon, colour, bg, title, sub, n, tasks):
    return (f'<section class="group"><div class="gh"><span class="ic" style="background:{bg};color:{colour}">{I(icon)}</span>'
            f'<div><h2>{title}</h2><p>{sub}</p></div><span class="cnt">{n}</span></div>{tasks}</section>')


def task(initials, who, what, buttons):
    return f'<div class="task"><span class="av">{initials}</span><div class="tx"><b>{who}</b><span>{what}</span></div><div class="btns">{buttons}</div></div>'


B = lambda label, cls='', icon='check': f'<span class="btn {cls}">{I(icon) if icon else ""}{label}</span>'

PAPER = group('paper', 'var(--rust)', 'var(--rustbg)', 'Hojas de inscripción por recoger',
              'En papel y firmadas, una por persona. Las de menores, con la firma de madre, padre o tutor.', 3,
              task('LG', 'Lía García Ruiz', 'Familia García · menor de edad · inscrita el 20 ene', B('Recibida'))
              + task('MG', 'Marc García López', 'Familia García · inscrito el 20 ene', B('Recibida'))
              + task('JP', 'Joan Puig Ferrer', 'Inscrito el 12 ene · hace 2 semanas', B('Recibida')))
GI = group('gi', 'var(--blue)', 'var(--bluebg)', 'Keikogi para entregar',
           'Ya se ha cobrado el primer trimestre o año y han pasado los 14 días.', 2,
           task('AG', 'Ana García López', 'Familia García · listo desde el 8 feb', B('Entregado'))
           + task('NS', 'Nil Soler Vidal', 'Listo desde el 6 feb', B('Entregado')))
SC = group('card', 'var(--green)', 'var(--greenbg)', 'Abonos municipales por comprobar',
           'Pide el abono del polideportivo en la primera clase.', 1,
           task('JP', 'Joan Puig Ferrer', 'CxEM Espronceda · 19 € al mes', B('Comprobado') + B('No es válido', 'warn', None)))
AGE = group('cake', 'var(--yink)', '#FFFBC2', 'Cumplen 17', 'Pasan a la cuota de 17 años o más desde el próximo cobro.', 1,
            task('PS', 'Pol Serra Mas', 'Familia Serra · cumple en febrero · 14 € → 24 € al mes', B('Aplicar y avisar', 'sec2', None)))
MONEY = group('euro', 'var(--red)', 'var(--redbg)', 'Cobros que no han pasado', 'Stripe lo reintenta solo. Si no se resuelve, habla con la familia.', 1,
              task('FR', 'Familia Roca', 'El banco devolvió el cargo del 5 feb · 77 €', B('Ver en Stripe', 'sec2', 'ext')))


def screen_pending():
    return f"""<div class="app">{TOP}{nav('Pendiente')}<div class="body">
<p class="hello">Buenos días, Marta</p>
<p class="sub">Tienes <b>7 cosas</b> pendientes. Lo más urgente, arriba.</p>
<div class="stats"><div class="stat"><b>41</b><span>cuotas activas</span></div><div class="stat"><b>58</b><span>personas entrenando</span></div>
<div class="stat"><b>3</b><span>inscripciones este mes</span></div><div class="stat"><b>1</b><span>baja en curso</span></div></div>
<div class="grid2"><div>{PAPER}{SC}</div><div>{GI}{AGE}{MONEY}</div></div>
</div></div>"""


def phone_pending():
    gi_done = ('<section class="group"><div class="gh"><span class="ic" style="background:var(--bluebg);color:var(--blue)">'
               f'{I("gi")}</span><div><h2>Keikogi para entregar</h2><p>Primer periodo cobrado y 14 días pasados.</p></div>'
               '<span class="cnt">1</span></div>'
               '<div class="done">' + I('check').replace('<svg', '<svg width="18" height="18"') + 'Ana García: keikogi entregado</div>'
               + task('NS', 'Nil Soler Vidal', 'Listo desde el 6 feb', B('Entregado')) + '</section>')
    return f"""<div class="phone">{TOP}<div class="body">
<p class="hello" style="font-size:1.3rem">Pendiente</p>
<p class="sub">6 cosas por hacer</p>
{gi_done}{PAPER}
</div>
<div class="toast">{I('check').replace('<svg', '<svg width="18" height="18"')} Keikogi de Ana: entregado <b>Deshacer</b></div>
{tabbar('Pendiente')}</div>"""


def fam(name, meta, ppl, chips, sel=False):
    return (f'<div class="fam{" sel" if sel else ""}"><div><h3>{name}</h3><div class="meta">{meta}</div></div>'
            f'<span class="btn ghost">Abrir</span><div class="ppl">{ppl}</div><div class="chips">{chips}</div></div>')


C = lambda cls, t: f'<span class="chip {cls}">{t}</span>'


def detail():
    return f"""<aside class="panel">
<div class="ph"><h2>Familia García</h2><p>Titular: Ana García López · ana.garcia@example.com · 600 000 000</p></div>
<div class="pb">
<h4>Quién entrena</h4>
<div class="person"><span class="av">AG</span><b>Ana García López</b><div class="chips">{C('ok','17 o más · completa')}{C('ok','Hoja recibida')}{C('todo','Keikogi por entregar')}</div></div>
<div class="person"><span class="av">MG</span><b>Marc García López</b><div class="chips">{C('ok','17 o más · familia')}{C('todo','Hoja por recoger')}{C('ok','Keikogi entregado')}</div></div>
<div class="person"><span class="av">LG</span><b>Lía García Ruiz</b><div class="chips">{C('ok','Hasta 16 · familia')}{C('todo','Hoja por recoger')}{C('ok','Keikogi entregado')}</div></div>
<h4>Cuota</h4>
<dl class="kv"><dt>Periodo</dt><dd>Trimestral · 183 €</dd><dt>Próximo cobro</dt><dd>5 de mayo</dd><dt>Pago</dt><dd>Domiciliación SEPA</dd><dt>Estado</dt><dd><span class="chip ok">Al día</span></dd></dl>
<h4>Historia</h4>
<ul class="tl"><li class="g"><small>20 ene</small><b>Inscripción en línea</b> · 32,53 € hasta el 5 feb</li>
<li class="g"><small>25 ene</small>Hoja de Ana recibida</li>
<li class="g"><small>5 feb</small>Cobrado el primer trimestre · 183 €</li>
<li class="g"><small>8 feb</small>Keikogi listos para entregar</li>
<li class="g"><small>10 feb</small>Keikogi de Marc y Lía entregados</li>
<li><small>hoy</small>Falta el keikogi de Ana y dos hojas</li></ul>
</div>
<div class="actions">
<span class="btn sec2">{I('paper')}Marcar hojas recibidas…</span>
<span class="btn sec2">{I('gi')}Keikogi entregado…</span>
<span class="btn sec2">{I('ext')}Pagos y recibos en Stripe</span>
<span class="btn warn">{I('door')}Dar de baja al final del trimestre…</span>
<p>Para añadir o quitar personas, o cambiar de periodo, escribe a info@ con lo que pide la familia.</p>
</div></aside>"""


def screen_members():
    fams = (fam('Familia García', 'Trimestral · 183 € · 3 personas · próximo cobro 5 may',
                'Ana, Marc y Lía', C('todo', '2 hojas por recoger') + C('todo', '1 keikogi por entregar') + C('ok', 'Al día'), True)
            + fam('Joan Puig Ferrer', 'Mensual · 19 € con abono CxEM · próximo cobro 5 feb', 'Joan',
                  C('todo', 'Abono por comprobar') + C('todo', 'Hoja por recoger') + C('ok', 'Al día'))
            + fam('Familia Roca', 'Mensual · 77 € · 3 personas · cobro pendiente', 'Pere, Laia y Bru',
                  C('bad', 'Cobro devuelto') + C('ok', 'Hojas recibidas'))
            + fam('Nil Soler Vidal', 'Anual · 360 € · próximo cobro 5 ene 2028', 'Nil',
                  C('todo', 'Keikogi por entregar') + C('ok', 'Al día'))
            + fam('Carla Vidal Puig', 'Mensual · 39 € · termina el 5 mar', 'Carla',
                  C('info', 'Baja el 5 mar') + C('ok', 'Al día')))
    return f"""<div class="app">{TOP}{nav('Miembros')}<div class="body">
<div class="split"><div>
<div class="search"><div class="in">{I('search')} Busca por nombre, apellido o correo</div></div>
<div class="filters"><span class="on">Todos · 41</span><span>Con algo pendiente · 6</span><span>Cobros pendientes · 1</span><span>Bajas en curso · 1</span><span>Con abono municipal · 4</span></div>
{fams}
</div>{detail()}</div>
</div></div>"""


def phone_confirm():
    return f"""<div class="phone">{TOP}<div class="body">
<p class="hello" style="font-size:1.3rem">Pendiente</p>{AGE}{SC}</div>
<div class="modal-bg"><div class="modal">
<h3>¿Pasar a Pol a la cuota de 17 o más?</h3>
<p>Desde el próximo cobro, el <b>5 de marzo</b>. La familia recibe un correo que se lo explica, y se borra su fecha de nacimiento.</p>
<div class="sum"><div><span>Pol</span><b>14 € → 24 € al mes</b></div><div><span>Total de la familia</span><b>53 € → 63 € al mes</b></div></div>
<span class="btn big">Sí, aplicar y avisar</span>
<span class="btn big sec2">Ahora no</span>
</div></div></div>"""


def phone_empty():
    return f"""<div class="phone">{TOP}<div class="body">
<div class="empty"><div class="ok">{I('check')}</div><h2>Todo al día</h2>
<p>No hay nada pendiente. Las inscripciones nuevas aparecerán aquí.</p></div>
<div class="help">{I('info')}<span>Cada mañana se revisan los keikogi listos y los cumpleaños. Si algo cambia, lo verás aquí y en el correo.</span></div>
</div>{tabbar('Pendiente')}</div>"""


def phone_login():
    return f"""<div class="phone"><div class="top"><span class="mark">{KNOT}</span><b>Cuotas</b></div>
<div class="login"><div class="card"><h3>Entrar en el panel de cuotas</h3>
<p>Escribe tu correo. Te enviamos un código de 6 cifras; no hay contraseña.</p>
<div class="in">marta@example.com</div><span class="btn big" style="width:100%">Enviar código</span></div>
<p class="cf">Acceso protegido por Cloudflare. Solo pueden entrar los correos autorizados.</p></div></div>"""


def build():
    body = f"""
<h1 class="pg">Panel de cuotas · the dojo's back office</h1>
<p class="lede">For the person at the dojo who looks after memberships, who is not the person who built them.
Three questions, three screens: <b>what do I have to do</b>, <b>who are our members</b>,
<b>what is going on with this family</b>. Spanish, plain words, one obvious button per thing to do.</p>
<p class="key"><b>Nothing here can break anything.</b> The everyday actions (form received, keikogi handed over,
card checked) are one tap with <b>Deshacer</b> for a few seconds after. The three that change what a family pays
or whether they stay (card not valid, moving to 17+, cancelling) open a confirmation that says exactly what will
happen, with the amounts. Money itself (payments, refunds, the card or account) stays in Stripe, one button away.</p>

<h2 class="sec">1 · Pendiente: what do I have to do?</h2>
<div class="row">{screen_pending()}
<div class="note"><h3>The first screen</h3>
<p>A greeting and the number of things to do, then four figures for orientation, then the to-do list grouped by
kind, each group with its colour, an icon, one line saying what it means, and a count.</p>
<h3>Each task says who and what</h3>
<p>The person, the family, how long it has been waiting, and one button that says what it does:
<b>Recibida</b>, <b>Entregado</b>, <b>Comprobado</b>. Nothing to type.</p>
<h3>New: the paper forms</h3>
<p>Today nothing records them. Each signup now creates a "form to collect" per person, and the panel and the
monthly digest list the ones still missing.</p>
<h3>Payment problems are information, not tasks</h3>
<p>Stripe retries on its own. The panel shows the family and the amount and links to Stripe; it does not ask the
volunteer to do anything with money.</p></div></div>

<h2 class="sec">2 · Miembros: who are our members, and one family</h2>
<div class="row">{screen_members()}
<div class="note"><h3>Search first</h3>
<p>By name, surname or email: at the dojo the question is always "is <i>this</i> person paid up?". Filters below
for the lists people ask for: anything pending, payments pending, cancellations, sports-centre rate.</p>
<h3>One card per membership</h3>
<p>The plan in words ("Trimestral · 183 € · 3 personas"), the next charge, who trains, and coloured chips: green
for done, orange for something to do, red for a payment problem, blue for information.</p>
<h3>The family, on the right</h3>
<p>Each person with their own status; the plan; a short history in plain words; and the actions, safest first.
Contact details are here because this is a logged-in tool for the dojo; they never go into emails.</p>
<h3>What it does not do</h3>
<p>Adding people or changing the period stays a request to info@, because the family price has to be
recalculated. It says so, rather than hiding the option.</p></div></div>

<h2 class="sec">3 · On a phone, at the dojo</h2>
<div class="row2">{phone_pending()}{phone_confirm()}
<div class="note"><h3>Left: done, with undo</h3>
<p>Pressing <b>Entregado</b> turns the row green, and a bar at the bottom offers <b>Deshacer</b> for a few
seconds. The tab bar keeps the three screens under the thumb.</p>
<h3>Right: the ones that cost money ask first</h3>
<p>Moving to the 17+ fee, or turning down a sports-centre card, changes what the family pays and emails them. A
sheet from the bottom says when, how much before and after, and what the family will receive.</p>
<h3>Buttons are 40 to 48px tall</h3>
<p>Easy to hit with a thumb, over the 24px minimum of WCAG 2.2.</p></div></div>

<h2 class="sec">4 · Getting in, and nothing to do</h2>
<div class="row2">{phone_login()}{phone_empty()}
<div class="note"><h3>No password to remember</h3>
<p>Cloudflare Access guards the panel: the volunteer types their email and gets a 6-digit code. Only the
addresses you list can get in; adding or removing a volunteer is one line in Cloudflare. We store no password.</p>
<h3>An empty list is good news</h3>
<p>"Todo al día", and one line on when the panel checks for new things, so an empty screen never looks broken.</p>
<h3>Ayuda</h3>
<p>The third tab: short answers to "a family wants to leave", "someone says they paid twice", "how do I add
someone", in the panel's own words, each ending with who to ask.</p></div></div>
"""
    html = ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Panel de cuotas</title>'
            f'<style>{CSS}</style></head><body><div class="wrap">{body}</div></body></html>\n')
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print('  docs/mockups/panel-cuotas.html')


if __name__ == '__main__':
    build()
