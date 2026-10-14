#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Online signup, layout B (chosen 14 October 2026): every screen and every email.

    inscripcion-pasos.html    the four steps, Stripe's checkout, the way back
                              from it, and the thank-you page, desktop and phone
    inscripcion-paginas.html  the members area, Stripe's portal, the withdrawal
                              function, the terms page and what changes on the
                              pages that already exist
    inscripcion-correos.html  every email a member receives, ours and Stripe's

The admin side is still drawn by build_signup.py, which owns the shared CSS and
the price helpers this file imports.

ONE HOUSEHOLD THROUGHOUT, so every screen can be checked against the others:
Ana García (17 or over, full fee), Marc García (17 or over, family rate) and
Lía García (up to 16, family rate), quarterly, signing up on Wednesday
20 January 2027 at 18:04. Today they pay the 16 days to the 5th; on 5 February
the first full quarter; then every 5 May, August, November and February. The
withdrawal period runs to 3 February.

    python3 docs/mockups/src/build_signup_b.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_signup import (FULL, H, BASE, PRO, MONTHS, fam, eur, page,  # noqa: E402
                          NAV, NAV_PH, person)

Q = 'q'
SC_TOTAL = FULL['m']['a'] + fam('m', 'a') + 9      # Lía on the Marina-Besòs rate: 72

EXTRA = """
.pair{display:grid;grid-template-columns:1000px 375px;gap:2.2rem;align-items:start}
.pair.one{grid-template-columns:1000px}
@media(max-width:1460px){.pair{grid-template-columns:1fr}}
.notes{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1.6rem;margin:1.4rem 0 0;max-width:1415px}
@media(max-width:1100px){.notes{grid-template-columns:1fr}}
.notes .note h2{margin-top:0}
.lbl{font:700 .7rem/1 var(--display);letter-spacing:.12em;text-transform:uppercase;color:var(--Mute);margin:0 0 .5rem}
.side{background:var(--Paper);border:1px solid var(--Hair);padding:1rem 1.1rem;font-size:.82rem;color:var(--Ink)}
.side h3{font:700 .78rem/1.2 var(--display);letter-spacing:.1em;text-transform:uppercase;color:var(--Black);margin:0 0 .6rem}
.side ul{margin:0;padding-left:1rem}
.side li{margin:0 0 .35rem}
.side p{margin:.7rem 0 0}
.opt.off{opacity:1;background:repeating-linear-gradient(135deg,#fff 0 6px,#f3f3f0 6px 12px);color:var(--Mute)}
.opt.off::before{border-color:#b9c1c4}
.opt.off b,.opt.off .pr{color:var(--Mute)}
.why{font-size:.78rem;color:var(--Black);background:#fff;border:1px solid var(--Hair);border-left:3px solid var(--Rust);padding:.6rem .8rem;margin:.7rem 0 0}
.chip.dis{color:#8b9599;border-style:dashed;background:#fafaf8}
.mini{width:100%;border-collapse:collapse;font-size:.8rem;font-variant-numeric:tabular-nums;margin:.3rem 0 .6rem}
.mini td{padding:.3rem .2rem;border-bottom:1px solid var(--Hair)}
.mini td:last-child{text-align:right}
.mini tr:last-child td{border-bottom:0;font-weight:700}
details.more[open] summary::after{content:"−"}
.notice{display:flex;gap:.7rem;border:1px solid var(--Hair);border-left:4px solid var(--Blue);background:#fff;padding:.8rem 1rem;font-size:.86rem;margin:0 0 1.4rem}
.notice b{display:block}
.compact{display:flex;justify-content:space-between;align-items:baseline;margin:0 0 .6rem}
.compact .eyb{margin:0}
.compact a{font-size:.78rem}

/* Stripe-hosted pages, drawn after Stripe's standard layout */
.stp{width:1000px;background:#fff;box-shadow:0 1px 2px rgba(17,19,20,.14),0 12px 34px rgba(17,19,20,.11);display:grid;grid-template-columns:1fr 1fr;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;min-height:620px}
.stp-l{background:#fafafa;padding:3rem 3rem 2rem 4rem;border-right:1px solid #ececec}
.stp-r{padding:3rem 4rem 2rem 3rem}
.stp-brand{display:flex;align-items:center;gap:.6rem;font-weight:600;font-size:.9rem;margin:0 0 2rem}
.stp-brand i{width:1.6rem;height:1.6rem;border-radius:50%;background:var(--Black);display:inline-block;position:relative}
.stp-brand i::after{content:"";position:absolute;inset:.45rem;border-radius:50%;background:var(--Yellow)}
.stp-k{font-size:.86rem;color:#6b7280;margin:0}
.stp-big{font-size:2.1rem;font-weight:600;margin:.2rem 0 .1rem;letter-spacing:-.01em}
.stp-then{font-size:.84rem;color:#6b7280;margin:0 0 1.6rem}
.stp-li{display:grid;grid-template-columns:1fr auto;gap:.15rem 1rem;font-size:.84rem;padding:.6rem 0;border-bottom:1px solid #ececec}
.stp-li small{color:#6b7280;grid-column:1}
.stp-sum{display:flex;justify-content:space-between;font-size:.86rem;font-weight:600;padding:.7rem 0}
.stp-h{font-size:1.05rem;font-weight:600;margin:0 0 1rem}
.stp-f{font-size:.78rem;color:#30313d;margin:0 0 .3rem;display:block}
.stp-i{border:1px solid #e0e0e0;border-radius:.4rem;padding:.6rem .7rem;font-size:.86rem;margin:0 0 .9rem;color:#30313d;box-shadow:0 1px 1px rgba(0,0,0,.03)}
.stp-i.ro{background:#f6f6f6;color:#6b7280}
.stp-tabs{display:grid;grid-template-columns:1fr 1fr;gap:.6rem;margin:0 0 1rem}
.stp-tabs span{border:1px solid #e0e0e0;border-radius:.4rem;padding:.6rem .7rem;font-size:.82rem}
.stp-tabs span.on{border:2px solid var(--Black)}
.stp-cb{display:grid;grid-template-columns:1rem 1fr;gap:.6rem;font-size:.78rem;color:#30313d;margin:.4rem 0 .9rem}
.stp-cb::before{content:"";width:.95rem;height:.95rem;border:1px solid #c9c9c9;border-radius:.2rem;margin-top:.1rem}
.stp-msg{font-size:.78rem;color:#30313d;background:#fffde0;border:1px solid #ece58a;border-radius:.4rem;padding:.6rem .7rem;margin:0 0 1rem}
.stp-btn{background:var(--Black);color:#fff;border-radius:.4rem;text-align:center;padding:.8rem;font-weight:600;font-size:.92rem}
.stp-legal{font-size:.7rem;color:#8a8f98;margin:.9rem 0 0;line-height:1.5}
.stp-pw{font-size:.72rem;color:#8a8f98;margin:2.4rem 0 0}
.stp-badge{display:inline-block;font:700 .66rem/1 var(--display);letter-spacing:.1em;text-transform:uppercase;background:var(--Rust);color:#fff;padding:.35rem .5rem;margin:0 0 .6rem}
.portal{width:1000px;background:#fff;box-shadow:0 1px 2px rgba(17,19,20,.14),0 12px 34px rgba(17,19,20,.11);display:grid;grid-template-columns:330px 1fr;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;min-height:520px}
.portal-l{background:var(--Black);color:#fff;padding:2.6rem 2.2rem}
.portal-l p{font-size:.84rem;color:rgba(255,255,255,.72)}
.portal-l a{color:#fff;font-size:.82rem}
.portal-r{padding:2.6rem 3rem}
.portal-r h3{font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:#6b7280;margin:1.6rem 0 .6rem;font-weight:600}
.portal-r h3:first-child{margin-top:0}
.prow{display:flex;justify-content:space-between;align-items:center;gap:1rem;font-size:.86rem;padding:.55rem 0;border-bottom:1px solid #ececec}
.prow small{display:block;color:#6b7280}
.pbtn{font-size:.8rem;border:1px solid #d6d6d6;border-radius:.35rem;padding:.35rem .7rem;white-space:nowrap}

/* our own small pages */
.lead-btn{display:inline-flex;align-items:center;gap:.6rem;min-height:3.1rem;padding:.8rem 1.6rem;background:var(--Black);color:#fff;font:700 .95rem/1 var(--display);letter-spacing:.06em;text-transform:uppercase;border-radius:.25rem}
.lead-btn::after{content:"↗"}
.two{display:grid;grid-template-columns:1fr 1fr;gap:2rem;margin:1.6rem 0 0}
.ph .two{grid-template-columns:1fr;gap:1rem}
.can li{list-style:none;padding:.35rem 0 .35rem 1.5rem;position:relative;font-size:.86rem;border-bottom:1px solid var(--Hair)}
.can li::before{content:"✓";position:absolute;left:0;font-weight:700;color:var(--Green)}
.cant li::before{content:"✉";color:var(--Slate)}
.can{margin:0;padding:0}
.howto{counter-reset:h;list-style:none;margin:0;padding:0}
.howto li{counter-increment:h;display:grid;grid-template-columns:2rem 1fr;gap:.6rem;font-size:.86rem;margin:0 0 .7rem}
.howto li::before{content:counter(h);display:grid;place-items:center;width:1.7rem;height:1.7rem;border-radius:50%;background:var(--Yellow);font:700 .8rem/1 var(--display)}
.links{display:flex;flex-wrap:wrap;gap:.4rem 1.2rem;font-size:.82rem;margin:1.6rem 0 0;padding:1rem 0 0;border-top:1px solid var(--Hair)}
.area{display:block;width:100%;min-height:7rem;border:1px solid #7b878c;border-radius:.25rem;padding:.55rem .65rem;font-size:.86rem;color:var(--Black);background:#fff}
.ok-h{display:flex;gap:.8rem;align-items:center}
.ok-h::before{content:"✓";display:grid;place-items:center;flex:none;width:2.4rem;height:2.4rem;border-radius:50%;background:var(--Green);color:#fff;font:700 1.2rem/1 var(--display)}
.stamp{display:inline-block;font:.82rem ui-monospace,Menlo,monospace;background:var(--Paper);border:1px solid var(--Hair);padding:.4rem .7rem;margin:.2rem 0 1rem}
.toc{columns:2;column-gap:2rem;font-size:.84rem;padding-left:1.2rem;margin:0 0 1.4rem}
.toc li{margin:0 0 .3rem;break-inside:avoid}
.draft{display:inline-block;font:700 .66rem/1 var(--display);letter-spacing:.1em;text-transform:uppercase;background:var(--Rust);color:#fff;padding:.35rem .5rem;margin:0 0 .8rem}
.fee-mini{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem}
.fee-c{border:1px solid var(--Hair);border-radius:.375rem;padding:1rem;font-size:.8rem;display:flex;flex-direction:column;gap:.3rem}
.fee-c.deal{border-left:4px solid var(--Green)}
.fee-c b{font:700 1.4rem/1.1 var(--display)}
.fee-c .fee-b{margin-top:.5rem;background:var(--Black);color:#fff;text-align:center;padding:.55rem;border-radius:.25rem;font-weight:700;font-size:.8rem}
.foot{background:var(--Black);color:rgba(255,255,255,.78);padding:1.4rem 2.2rem;font-size:.78rem;display:grid;grid-template-columns:1fr 1fr;gap:1rem}
.foot b{color:#fff;display:block;margin:0 0 .4rem;font:700 .72rem/1 var(--display);letter-spacing:.1em;text-transform:uppercase}
.foot span{display:block;margin:0 0 .25rem}
.foot .new{color:var(--Yellow)}
.qr-card{width:375px;height:264px;background:#fff;box-shadow:0 8px 24px rgba(17,19,20,.12);display:grid;grid-template-columns:1fr 120px;gap:1rem;padding:1.3rem;align-items:center}
.qr-card h3{font:700 1.35rem/1.15 var(--display);margin:.3rem 0 .6rem}
.qr-card p{font-size:.78rem;color:var(--Ink);margin:0 0 .5rem}
.qr-card code{font:700 .82rem ui-monospace,Menlo,monospace}
.qr{display:grid;grid-template-columns:repeat(21,1fr);width:120px;height:120px;border:8px solid #fff;outline:1px solid var(--Hair)}
.qr i{background:#fff}
.qr i.b{background:var(--Black)}
.chg{width:100%;border-collapse:collapse;font-size:.84rem;background:#fff}
.chg th,.chg td{padding:.55rem .7rem;border-bottom:1px solid var(--Hair);text-align:left;vertical-align:top}
.chg thead th{font:700 .7rem/1.2 var(--display);letter-spacing:.09em;text-transform:uppercase;background:var(--Black);color:#fff}
.chg tbody th{width:22%}
.chg code{font:.78rem ui-monospace,Menlo,monospace}
.nw{font:700 .62rem/1 var(--display);letter-spacing:.08em;text-transform:uppercase;background:var(--Yellow);padding:.2rem .35rem;margin-left:.3rem;vertical-align:.1em}

/* emails */
.em-row{display:grid;grid-template-columns:600px 1fr;gap:2.4rem;align-items:start;margin:0 0 2.6rem}
@media(max-width:1200px){.em-row{grid-template-columns:1fr}}
.em{width:600px;background:#fff;box-shadow:0 8px 24px rgba(17,19,20,.09);font-size:.88rem;line-height:1.6}
.em-meta{font-size:.74rem;color:var(--Mute);background:#ECECE8;padding:.6rem 1rem;border-bottom:1px solid var(--Hair)}
.em-meta b{color:var(--Black)}
.em-top{background:var(--Black);color:#fff;padding:1rem 1.6rem;display:flex;justify-content:space-between;align-items:baseline}
.em-top b{font:700 1rem/1 var(--display);letter-spacing:.04em}
.em-top span{font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.65)}
.em-bar{height:4px;background:var(--Yellow)}
.em-b{padding:1.6rem 1.6rem 1.2rem}
.em-b h3{font:700 1.35rem/1.2 var(--display);margin:0 0 .8rem;text-wrap:balance}
.em-b p{margin:0 0 .85rem;color:var(--Ink)}
.em-b p b{color:var(--Black)}
.em-b h4{font:700 .74rem/1.2 var(--display);letter-spacing:.12em;text-transform:uppercase;margin:1.3rem 0 .5rem}
.em-t{width:100%;border-collapse:collapse;font-size:.84rem;font-variant-numeric:tabular-nums;margin:0 0 1rem}
.em-t td{padding:.4rem .2rem;border-bottom:1px solid var(--Hair)}
.em-t td:last-child{text-align:right}
.em-t tr.t td{border-top:2px solid var(--Black);border-bottom:0;font-weight:700}
.em-dates{list-style:none;margin:0 0 1rem;padding:0;border-left:2px solid var(--Black)}
.em-dates li{padding:0 0 .45rem .8rem;font-size:.84rem;color:var(--Ink)}
.em-dates b{color:var(--Black)}
.em-btn{display:inline-block;background:var(--Black);color:#fff;font:700 .8rem/1 var(--display);letter-spacing:.07em;text-transform:uppercase;padding:.8rem 1.2rem;margin:.2rem 0 1rem}
.em-box{background:var(--Paper);border:1px solid var(--Hair);padding:.8rem 1rem;font-size:.82rem;color:var(--Ink);margin:0 0 1rem}
.em-box b{color:var(--Black)}
.em-big{font:700 1.7rem/1.1 var(--display);color:var(--Black);margin:0 0 .2rem}
.em-att{display:inline-flex;gap:.5rem;align-items:center;font-size:.78rem;border:1px solid var(--Hair);padding:.4rem .7rem;margin:0 .4rem .6rem 0}
.em-att::before{content:"PDF";font:700 .6rem/1 var(--display);background:var(--Rust);color:#fff;padding:.25rem .3rem}
.em-foot{border-top:1px solid var(--Hair);padding:1rem 1.6rem 1.3rem;font-size:.7rem;color:var(--Mute);line-height:1.55}
.em-foot a{color:var(--Mute)}
.stripe-list{width:100%;border-collapse:collapse;font-size:.84rem;background:#fff;max-width:1100px}
.stripe-list th,.stripe-list td{padding:.6rem .7rem;border-bottom:1px solid var(--Hair);text-align:left;vertical-align:top}
.stripe-list thead th{font:700 .7rem/1.2 var(--display);letter-spacing:.09em;text-transform:uppercase;background:var(--Slate);color:#fff}
"""


def steps(cur, ph=False):
    names = ('Quién entrena', 'Cómo pagáis', 'Quién paga', 'Revisar y pagar')
    lis = []
    for i, n in enumerate(names, 1):
        cls = 'done' if i < cur else ('cur' if i == cur else '')
        label = n if (not ph or i == cur) else str(i)
        lis.append('<li class="%s">%s</li>' % (cls, label))
    return '<ol class="steps" aria-label="Pasos de la inscripción">%s</ol>' % ''.join(lis)


def head(cur, ph=False):
    if cur == 1:
        if ph:
            return ('<p class="eyb">Cuotas · Inscripción</p><h1 class="h1">Inscripción</h1>'
                    '<p class="lede" style="font-size:.88rem">Después de tus dos clases de prueba. Sin matrícula; '
                    'la cuota se cobra el día 5, con tarjeta o domiciliación, en una página segura de Stripe.</p>'
                    + steps(1, ph))
        return ("""<p class="eyb">Cuotas · Inscripción</p>
<h1 class="h1">Inscripción</h1>
<p class="lede">Normalmente te inscribes después de las dos clases de prueba. No hay matrícula,
y la cuota se cobra sola el día 5, con tarjeta o domiciliación bancaria, en una página segura de
Stripe. Son cuatro pasos y unos tres minutos.</p>
<p class="member">¿Ya tienes cuota? <a href="#">Ve a tu área de miembros</a> para cambiar la tarjeta,
descargar recibos o darte de baja.</p>""" + steps(1))
    return ('<div class="compact"><p class="eyb">Inscripción</p><a href="#">Área de miembros</a></div>'
            + steps(cur, ph))


def family_line(ph=False):
    return ('<div class="done-sum"><div><b>3 personas</b><div class="who"><span>Ana · 17 o más</span>'
            '<span>Marc · 17 o más</span><span>Lía · hasta 16</span></div></div><a href="#">Cambiar</a></div>')


def pair(desk, phone, notes):
    return ('<div class="pair">%s%s</div><div class="notes">%s</div>'
            % (desk, phone, ''.join('<div class="note">%s</div>' % n for n in notes)))


def mk(inner, ph=False):
    if ph:
        return '<div class="ph">%s<div class="in">%s</div></div>' % (NAV_PH, inner)
    return '<div class="mk">%s<div class="in">%s</div></div>' % (NAV, inner)


# ---------------------------------------------------------------------------
# Step 1 — who trains
# ---------------------------------------------------------------------------
def step1():
    desk = mk(head(1) + """
<div class="grid" style="grid-template-columns:1fr 260px"><div>
<h2 class="h2">Quién entrena</h2>
<p class="sub">Las personas del mismo núcleo familiar que van a entrenar, hasta seis. Quien paga
no tiene por qué entrenar: lo dirás en el paso 3.</p>
%s%s%s
<span class="add">Añadir otra persona</span>
<div class="nav-b"><span></span><span class="btn">Continuar</span></div>
</div>
<aside class="side"><h3>Antes de empezar</h3><ul>
<li>Primero, las dos clases de prueba. Son gratis.</li>
<li>Sin matrícula.</li>
<li>En una familia, la primera persona paga la cuota completa y cada una de las siguientes, 15 € menos al mes.</li>
<li>Pagas en Stripe con tarjeta o con domiciliación SEPA. Aquí no se escribe ningún dato bancario.</li>
<li>Te das de baja cuando quieras, desde tu área de miembros.</li></ul>
<p>¿Dudas? <a href="#">info@aikidomusubi.com</a> · WhatsApp <a href="#">717 171 177</a></p></aside>
</div>""" % (person(1, 'Ana', 'García López', 'a', True, removable=False, rate_row=True),
             person(2, 'Marc', 'García López', 'a', False, rate_row=True),
             person(3, 'Lía', 'García Ruiz', 'c', False, kid=True, rate_row=True)))

    phone = mk(head(1, True) + """
<h2 class="h2">Quién entrena</h2>
<fieldset class="person"><legend><span>Persona 3</span><a class="rm" href="#">Quitar a la persona 3: Lía</a></legend>
<div class="f2"><div class="fld"><label>Nombre</label><span class="inp">Lía</span></div>
<div class="fld"><label>Apellidos</label><span class="inp">García Ruiz</span></div></div>
<p class="fld-l">Edad</p><div class="chips"><span class="chip">17 años o más</span><span class="chip on">Hasta 16 años</span></div>
<div class="f2" style="margin-top:.6rem;grid-template-columns:1fr 1fr"><div class="fld"><label>Mes de nacimiento</label><span class="inp sel">Marzo</span></div><div class="fld"><label>Año</label><span class="inp sel">2014</span></div></div>
<p class="fld-l">Cuota de Lía</p>
<div class="chips"><span class="chip">General · todos los espacios</span><span class="chip on">Con abono municipal</span></div>
<div class="f2" style="margin-top:.6rem"><div class="fld"><label>¿De qué polideportivo?</label><span class="inp sel">Marina-Besòs</span></div></div>
<p class="cond">9 € al mes, solo las clases de Marina-Besòs, y solo mes a mes. Trae el abono a la
primera clase. No cuenta para el descuento familiar.</p>
</fieldset>
<span class="add">Añadir otra persona</span>
<div style="height:1.2rem"></div><span class="btn">Continuar</span>""", True)

    return pair(desk, phone, [
        """<h2>What it asks</h2><p>Name, surnames and the age group, per person. Month and year of
birth only for "up to 16", because that is what the age change at 17 needs and nothing more.</p>
<p>The <b>rate is chosen per person</b>: general for everybody unless someone holds a sports-centre
membership. Ana and Marc are on the general fee.</p>""",
        """<h2>On the phone: the other path</h2><p>Lía is drawn with the sports-centre rate picked, to
show what it asks: which centre, then its conditions right there.</p>
<p>The choices follow the facts: Marina-Besòs is offered only to "up to 16", because its only class is
for up to 16, and CxEM Espronceda only from 12. The validation on the server says the same.</p>""",
        """<h2>Accessibility</h2><p>Each person is a <code>fieldset</code> with its own legend.
"Add another person" moves focus to the new person's first field; "remove" names who it removes.</p>
<p>Without JavaScript, persons 2 to 6 are closed <code>&lt;details&gt;</code> blocks, "Add person 2" and
so on, and the four steps are one page.</p>"""])


# ---------------------------------------------------------------------------
# Step 2 — how you pay
# ---------------------------------------------------------------------------
def opts_household(chosen, disabled=False):
    labels = {'m': ('Mensual', 'al mes'), 'q': ('Trimestral', 'al trimestre'), 'y': ('Anual', 'al año')}
    out = []
    for p in 'mqy':
        name, unit = labels[p]
        off = disabled and p != 'm'
        cls = 'opt big' + (' on' if p == chosen else '') + (' off' if off else '')
        total = SC_TOTAL if disabled and p == 'm' else H[p]
        per = '' if p == 'm' else '<span class="per">%s al mes</span>' % eur(H[p] / MONTHS[p])
        save = '' if p == 'm' else '<span class="sv">Ahorráis %s</span>' % eur(BASE[p] - H[p])
        gift = '' if p == 'm' else '<span class="gift">+ 3 keikogi de regalo</span>'
        flag = '<span class="flag">El que más ahorra</span>' if p == 'y' and not off else ''
        if off:
            per, save, gift = '<span class="per">No disponible con abono municipal</span>', '', ''
            out.append('<label class="%s"><b>%s</b><span class="pr">— </span>%s</label>' % (cls, name, per))
            continue
        out.append('<label class="%s">%s<b>%s</b><span class="pr">%s <small>%s</small></span>%s%s%s</label>'
                   % (cls, flag, name, eur(total), unit, per, save, gift))
    return '<div class="opts">%s</div>' % ''.join(out)


def step2():
    lines = ''.join('<tr><td>%s</td><td>%s</td></tr>' % (a, eur(b)) for a, b in (
        ('Ana · 17 o más · cuota completa', FULL[Q]['a']),
        ('Marc · 17 o más · familia (−45 €)', fam(Q, 'a')),
        ('Lía · hasta 16 · familia (−45 €)', fam(Q, 'c')),
        ('Total al trimestre', H[Q])))
    desk = mk(head(2) + family_line() + """
<h2 class="h2">Cómo pagáis</h2>
<p class="sub">Precios para vuestra familia. Se paga toda junta, en el mismo periodo.</p>
<fieldset><legend>Periodo <span class="req">(obligatorio)</span></legend>%s</fieldset>
<p class="cond">Con trimestral o anual, cada persona recibe un keikogi en su primera inscripción.
Lo damos en el dojo cuando se ha cobrado el primer trimestre o año completo.</p>
<details class="more" open style="margin-top:1.2rem"><summary>Cómo sale este precio</summary>
<table class="mini"><tbody>%s</tbody></table>
<p class="hint" style="margin:0 0 .6rem">Pagando mes a mes serían %s al trimestre: ahorráis %s.</p></details>
<details class="more"><summary>Cuándo se cobra</summary></details>
<div class="nav-b"><a class="back" href="#">← Quién entrena</a><span class="btn">Continuar</span></div>
""" % (opts_household('q'), lines, eur(BASE[Q]), eur(BASE[Q] - H[Q])))

    phone = mk(head(2, True) + family_line(True) + """
<h2 class="h2">Cómo pagáis</h2>
<fieldset><legend>Periodo</legend>%s</fieldset>
<p class="why"><b>Por qué solo mensual:</b> Lía tiene la cuota con abono municipal, que es mes a mes, y una
familia paga toda junta en el mismo periodo. Para pagar por trimestre o por año, elige la cuota general
para Lía. <a href="#">Cambiar</a></p>
<div style="height:1rem"></div><span class="btn">Continuar</span>""" % opts_household('m', disabled=True), True)

    return pair(desk, phone, [
        """<h2>The household's own numbers</h2><p>Each card is the family's total, its monthly equivalent,
the saving against paying monthly and the keikogi. Open "how this price is worked out" and it is
the three lines, with the family discount named.</p>""",
        """<h2>On the phone: the case that would confuse</h2><p>With Lía on the Marina-Besòs rate the
family total is 39 + 24 + 9 = <b>72 €</b>, and quarterly and annual are unavailable: one Stripe
subscription has one billing interval, and the sports-centre rate is monthly only. The cards stay
visible with the reason beside them, rather than disappearing without explanation.</p>""",
        """<h2>The keikogi, decided here</h2><p>The spec gives it on enrolment. That has a hole: sign
up quarterly on the 20th, pay the 16 days, cancel before the 5th, and the dojo has handed over a keikogi
for 31 €. So it is given <b>once the first full quarter or year has been paid</b>, which in this
example is also after the 14 days. <span class="tag tag-q">confirm</span></p>"""])


# ---------------------------------------------------------------------------
# Step 3 — who pays
# ---------------------------------------------------------------------------
def step3():
    desk = mk(head(3) + family_line() + """
<h2 class="h2">Quién paga</h2>
<p class="sub">La persona titular recibe los recibos y los avisos, y es quien entra en el área de miembros.</p>
<fieldset><legend>¿Quién es titular de la cuota? <span class="req">(obligatorio)</span></legend>
<div class="opts">
<label class="opt on"><b>Ana García López</b>Entrena</label>
<label class="opt"><b>Marc García López</b>Entrena</label>
<label class="opt"><b>Otra persona</b>Paga, pero no entrena</label></div></fieldset>
<p class="hint">Lía no aparece: tiene que ser una persona mayor de edad.</p>
<div class="f2" style="margin-top:1.2rem"><div class="fld"><label>Correo electrónico <span class="req">(obligatorio)</span></label><span class="inp">ana.garcia@example.com</span>
<p class="hint">Con este correo entrarás en tu área de miembros. Sin contraseña.</p></div>
<div class="fld"><label>Teléfono <span class="req">(opcional)</span></label><span class="inp">+34 600 000 000</span>
<p class="hint">Solo por si hay que avisarte de algo.</p></div></div>
<div style="height:1rem"></div>
<p class="fld-l" style="margin-top:0">Lo declara quien rellena esto, Ana García López:</p>
<div class="chk on"><span>Soy mayor de edad.</span></div>
<div class="chk on"><span>Soy madre, padre, tutora o tutor legal de Lía García Ruiz.
<small>Aparece porque hay una persona menor de 18.</small></span></div>
<p class="hint">El nombre del titular de la tarjeta o de la cuenta lo pedirá Stripe en el último paso.
Puede ser otro: una cuenta a nombre de otra persona de la familia también vale.</p>
<div class="nav-b"><a class="back" href="#">← Cómo pagáis</a><span class="btn">Continuar</span></div>
""")

    phone = mk(head(3, True) + """
<h2 class="h2">Quién paga</h2>
<fieldset><legend>¿Quién es titular de la cuota?</legend>
<div class="opts"><label class="opt"><b>Ana García López</b>Entrena</label>
<label class="opt"><b>Marc García López</b>Entrena</label>
<label class="opt on"><b>Otra persona</b>Paga, pero no entrena</label></div></fieldset>
<div class="f2" style="margin-top:.8rem"><div class="fld"><label>Nombre</label><span class="inp">Rosa</span></div>
<div class="fld"><label>Apellidos</label><span class="inp">López Martí</span></div>
<div class="fld"><label>Correo electrónico</label><span class="inp">rosa.lopez@example.com</span></div>
<div class="fld"><label>Teléfono <span class="req">(opcional)</span></label><span class="inp ph-t">+34</span></div></div>
<div style="height:.8rem"></div>
<div class="chk on"><span>Soy mayor de edad.</span></div>
<div class="chk on"><span>Soy madre, padre, tutora o tutor legal de Lía García Ruiz.</span></div>
<span class="btn">Continuar</span>""", True)

    return pair(desk, phone, [
        """<h2>The name, asked once</h2><p>The payer is <b>picked from the people already listed</b>,
so our page never asks a name twice. Only "Otra persona", somebody who pays and does not train, gets
name fields, because that name has not been typed yet.</p>
<p>The declarations stay in the first person and name who is making them, because the person
filling this in is the payer: "I am an adult", "I am Lía's parent or guardian".</p>""",
        """<h2>What Stripe will still ask</h2><p>Stripe's own page asks for the <b>name on the card</b>,
or the account holder for SEPA. We cannot fill it in. Stripe only fills it from a card the customer has
saved before, and loading Stripe's script on our page to do it would break the no-third-party rule.
It is also a different fact: the account may be in somebody else's name. We stop Stripe asking for
the <i>customer's</i> name separately, because we already send it.</p>""",
        """<h2>On the phone</h2><p>A grandparent paying for the family: "Otra persona", then their own name,
email and phone, and the same two declarations.</p>
<p>Catalan pages add one line here: Stripe has no Catalan, so its page and its receipts are in Spanish.</p>"""])


# ---------------------------------------------------------------------------
# Step 4 — review and pay
# ---------------------------------------------------------------------------
def step4():
    rows = (('Ana García', '17 o más', 'Completa', FULL[Q]['a']),
            ('Marc García', '17 o más', 'Familia', fam(Q, 'a')),
            ('Lía García', 'Hasta 16', 'Familia', fam(Q, 'c')))
    trs = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (a, b, c, eur(d)) for a, b, c, d in rows)
    legal = """
<div class="chk on"><span>He leído y acepto las <a href="#">condiciones de la cuota</a>.</span></div>
<div class="chk on"><span>Quiero empezar a entrenar ya, antes de que acaben los 14 días para desistir.
<small>Si desisto en ese plazo, pagaré solo los días transcurridos hasta que lo comunique.</small></span></div>
<p class="priv"><b>Protección de datos.</b> Responsable: Associació Cultural Musubi Aikido. Finalidad:
tu inscripción y el cobro de la cuota. Base: el contrato. Destinatarios: Stripe, que procesa el pago,
con transferencia a EE. UU. bajo el Data Privacy Framework. Derechos: info@aikidomusubi.com.
<a href="#">Más información</a>.</p>"""
    desk = mk(head(4) + """
<div class="notice"><span><b>No se ha cobrado nada.</b>Has vuelto de la página de pago sin terminar. Todo sigue
como lo dejaste: revísalo y vuelve a intentarlo cuando quieras.</span></div>
<div class="rv"><div>
<h2 class="h2">Revisad antes de pagar</h2>
<table class="rv-t"><thead><tr><th>Persona</th><th>Edad</th><th>Cuota</th><th>Al trimestre</th></tr></thead>
<tbody>%s</tbody><tfoot><tr><td colspan="3">Total trimestral</td><td>%s</td></tr></tfoot></table>
<p class="rv-edit"><a href="#">Cambiar personas</a> · <a href="#">Cambiar periodo</a> · Titular: Ana García López, ana.garcia@example.com · <a href="#">Cambiar</a></p>
<ol class="tl"><li class="now"><b>Hoy, %s</b> · los 16 días hasta el 5 de febrero</li>
<li><b>3 de febrero</b> · último día para desistir</li>
<li><b>5 de febrero, %s</b> · primer trimestre completo. Después, los keikogi</li>
<li>Después, <b>%s</b> cada 5 de mayo, agosto, noviembre y febrero</li></ol>
<p class="rc-x"><b>No incluido:</b> licencia federativa y seguro, 45 € al año por persona, en marzo.
Te avisaremos 15 días antes de cada renovación. Te das de baja cuando quieras y se aplica al final
del periodo pagado.</p>
</div><div>
<h2 class="h2">Antes de pagar</h2>%s
<span class="btn">Ir al pago seguro</span>
<p class="btn-note"><span class="lock"></span>En Stripe eliges tarjeta o domiciliación y confirmas. Hasta entonces no se cobra nada.</p>
</div></div>""" % (trs, eur(H[Q]), eur(PRO[Q]), eur(H[Q]), eur(H[Q]), legal))

    phone = mk(head(4, True) + """
<div class="esum" tabindex="-1"><p>Con este correo ya hay una cuota</p>
<ul style="list-style:none;padding:0"><li>ana.garcia@example.com ya paga una cuota con nosotros. Para añadir a
alguien, <a href="#">escríbenos</a> y lo sumamos a esa cuota, con el descuento familiar. Así no pagáis dos cuotas
completas.</li></ul></div>
<h2 class="h2">Revisad antes de pagar</h2>
<table class="rv-t"><tbody>%s</tbody><tfoot><tr><td colspan="3">Al trimestre</td><td>%s</td></tr></tfoot></table>
<ol class="tl"><li class="now"><b>Hoy, %s</b></li><li><b>3 feb</b> · último día para desistir</li>
<li><b>5 feb, %s</b>, y cada trimestre</li></ol>
<div style="height:.8rem"></div>
<div class="chk on"><span>Acepto las <a href="#">condiciones de la cuota</a>.</span></div>
<div class="chk on"><span>Quiero empezar antes de que acaben los 14 días.<small>Si desisto, pago solo los días transcurridos.</small></span></div>
<span class="btn">Ir al pago seguro</span>""" % (
        ''.join('<tr><td>%s</td><td>%s</td><td></td><td>%s</td></tr>' % (a, c, eur(d)) for a, b, c, d in rows),
        eur(H[Q]), eur(PRO[Q]), eur(H[Q])), True)

    return pair(desk, phone, [
        """<h2>The last screen that is ours</h2><p>Every line, every date in order, what the fee does not
cover, the renewal and cancellation promises, then the two checkboxes, the first layer of the privacy
notice and the button. This is what consumer law wants in front of somebody before they pay (spec 11.1).</p>
<p>The <b>last day to withdraw</b> is in the timeline, as a date, not as "14 days".</p>""",
        """<h2>Coming back from Stripe</h2><p>The blue notice is the cancel return: somebody pressed
"back" on Stripe's page. Nothing was charged; the answers come back from <code>sessionStorage</code>, never
from the URL, and are cleared after a successful payment.</p>""",
        """<h2>On the phone: an email that already pays</h2><p>Without this check a parent adding a second child
would open a <b>second</b> subscription, both at full price, and the family discount would be lost. The
server checks the email against active subscriptions and stops there.</p>
<p>It does tell anyone who types that address that it has a membership. That is a small disclosure,
and I think it is the right trade. <span class="tag tag-q">confirm</span></p>"""])


# ---------------------------------------------------------------------------
# Stripe's checkout, and the thank-you page
# ---------------------------------------------------------------------------
def stripe_checkout():
    li = ''.join('<div class="stp-li"><span>%s</span><span>%s</span><small>%s</small></div>' % (a, eur(b), c)
                 for a, b, c in (('Cuota general · 17 o más', FULL[Q]['a'], 'Cada 3 meses · Cantidad 1'),
                                 ('Cuota general · 17 o más · familia', fam(Q, 'a'), 'Cada 3 meses · Cantidad 1'),
                                 ('Cuota general · hasta 16 · familia', fam(Q, 'c'), 'Cada 3 meses · Cantidad 1')))
    return """
<p class="stp-badge">Stripe's page · illustrative, Stripe draws it</p>
<div class="stp"><div class="stp-l">
<div class="stp-brand"><i></i>Aikido Musubi</div>
<p class="stp-k">Suscribirse a Cuota general</p>
<p class="stp-big">%s <span style="font-size:.9rem;font-weight:400;color:#6b7280">hoy</span></p>
<p class="stp-then">Después, %s cada 3 meses a partir del 5 de febrero de 2027</p>
%s
<div class="stp-sum"><span>Total a pagar hoy</span><span>%s</span></div>
<p class="stp-pw">Powered by stripe · Condiciones · Privacidad</p>
</div><div class="stp-r">
<p class="stp-h">Información de contacto</p>
<span class="stp-f">Correo electrónico</span><div class="stp-i ro">ana.garcia@example.com</div>
<p class="stp-h">Método de pago</p>
<div class="stp-tabs"><span class="on">Tarjeta</span><span>Débito SEPA</span></div>
<span class="stp-f">Información de la tarjeta</span><div class="stp-i">1234 1234 1234 1234 &nbsp;&nbsp; MM / AA &nbsp; CVC</div>
<span class="stp-f">Nombre del titular de la tarjeta</span><div class="stp-i" style="color:#a3a3a3">Nombre completo</div>
<span class="stp-f">País</span><div class="stp-i">España</div>
<div class="stp-cb"><span>Acepto las <u>condiciones del servicio</u> de Aikido Musubi.</span></div>
<p class="stp-msg">Al confirmar te comprometes a pagar una cuota periódica: hoy %s y, desde el 5 de febrero de 2027,
%s cada trimestre, hasta que te des de baja. Puedes desistir hasta el 3 de febrero.</p>
<div class="stp-btn">Suscribirse</div>
<p class="stp-legal">Al confirmar tu suscripción, permites que Aikido Musubi efectúe cargos en tu tarjeta por este pago y
por pagos futuros de conformidad con sus condiciones.</p>
</div></div>""" % (eur(PRO[Q]), eur(H[Q]), li, eur(PRO[Q]), eur(PRO[Q]), eur(H[Q]))


def thanks():
    body = """
<p class="eyb">Inscripción</p>
<h1 class="h1 ok-h">Inscripción hecha</h1>
<p class="lede">Gracias. Ya tenéis cuota y podéis entrenar desde hoy en todos los espacios. Esto es lo que queda:</p>
<ol class="howto">
<li><span><b>Mira tu correo.</b> Te llegan dos mensajes: el recibo de Stripe y nuestra confirmación, con las
condiciones y las fechas de cobro. Si no los ves en unos minutos, revisa el correo no deseado.</span></li>
<li><span><b>Trae al dojo la hoja de inscripción firmada</b>, una por persona, y la autorización de uso de
imagen. Para menores de 14, también la autorización para menores. Están en <a href="#">Recursos</a>.</span></li>
<li><span><b>Si has pagado con domiciliación</b>, el cargo tarda unos días en confirmarse. No tienes que hacer nada:
si el banco lo rechaza, te escribimos.</span></li>
<li><span><b>Si has elegido trimestre o año</b>, el keikogi os espera en el dojo en cuanto se cobre el primer
periodo completo. Te avisamos por correo.</span></li>
</ol>
<div class="two"><div class="side"><h3>Tu área de miembros</h3><p style="margin:0 0 .8rem">Para cambiar la tarjeta o la cuenta,
descargar recibos o darte de baja. Entras con tu correo y un código.</p><a href="#">Ir al área de miembros →</a></div>
<div class="side"><h3>¿Has cambiado de idea?</h3><p style="margin:0 0 .8rem">Tienes 14 días para desistir, sin dar
explicaciones. Pagas solo los días transcurridos.</p><a href="#">Desistir del contrato →</a></div></div>
"""
    desk = mk(body)
    phone = mk(body.replace('class="two"', 'class="two"'), True)
    return pair(desk, phone, [
        """<h2>One page for every case</h2><p>The return URL carries no session ID and no personal data (spec 6.5),
so the page cannot know who arrived or what they chose. It says what happens next in a form that is
true for everybody: SEPA "if", keikogi "if". The personal details are in the confirmation email.</p>""",
        """<h2>The paper still matters</h2><p>The registration form is the only place the ID number, the date
of birth, health information and the image consent live, by design. So it is step 2 here, and it links
to the forms already on <code>/recursos/</code>.</p><p>That form may need a change: its description on
<code>/recursos/</code> says it covers the fee. Anything about choosing the fee or giving bank details goes,
now that both happen online. See tab 2.</p>""",
        """<h2>Not indexed</h2><p>The thank-you page carries <code>sitemap: false</code>, so it is out of
the sitemap and <code>noindex</code>. Analytics is not loaded on it or on the signup page (spec 10.3);
the four steps stay indexable.</p>"""])


def build_steps():
    body = """
<h1 class="pg">Signup, layout B: every screen</h1>
<p class="top-lede">Four steps on our site, then Stripe's page, then back. Desktop at 1000px on the left and a phone
at 375px on the right; the phone often shows a <b>different state</b> of the same step, an error or the
other path, so one mockup covers two cases.</p>
<p class="key"><b>The household throughout:</b> Ana and Marc, 17 or over, and Lía, up to 16, quarterly:
99 + 54 + 30 = <b>183 € a quarter</b>. They sign up on Wednesday 20 January 2027, pay <b>%s</b> today for the
16 days to the 5th, and <b>183 €</b> every quarter from 5 February. Their 14 days to withdraw end on
<b>3 February</b>.</p>
<p class="warn"><b>Orange tags</b> mark a decision I took that the spec does not, or that changes it.
Each one is in the list in my reply.</p>

<h2 class="sec-t">Step 1 · Who trains</h2>%s
<h2 class="sec-t">Step 2 · How you pay</h2>%s
<h2 class="sec-t">Step 3 · Who pays</h2>%s
<h2 class="sec-t">Step 4 · Review and pay, after coming back from Stripe</h2>%s
<h2 class="sec-t">Stripe Checkout</h2>
<div class="pair one">%s</div>
<div class="notes"><div class="note"><h2>Not ours, but configured by us</h2><p>Stripe draws this page. We set the
logo and colours, the language (es, en, ja; Catalan falls back to Spanish), the lines, the date of the first
full charge, and the yellow message, which is the spec's <code>custom_text</code>. It states that confirming
creates a recurring payment and gives the dates.</p></div>
<div class="note"><h2>What the payer types here</h2><p>The card, or the IBAN and the account holder's name for SEPA,
and the country. The email arrives already filled in and cannot be edited. The customer's name is not asked,
because we have sent it.</p></div>
<div class="note"><h2>The checkbox</h2><p>Stripe's own terms-of-service checkbox, required by the spec, points at
our membership terms page. Combined with ours on step 4, the acceptance is recorded twice, which is what
evidence wants.</p></div></div>
<h2 class="sec-t">Thank-you page</h2>%s
""" % (eur(PRO[Q]), step1(), step2(), step3(), step4(), stripe_checkout(), thanks())
    page('inscripcion-pasos.html', 'Signup steps', 'inscripcion-pasos.html', body, EXTRA)


# ---------------------------------------------------------------------------
# Members area, portal, withdrawal, terms, site changes
# ---------------------------------------------------------------------------
def qr_svg():
    # A drawing of a QR code, not a real one: the real one is generated from the final URL.
    import hashlib
    cells = []
    h = hashlib.sha256(b'aikidomusubi.com/inscripcion/').digest() * 14
    for y in range(21):
        for x in range(21):
            finder = any(x0 <= x < x0 + 7 and y0 <= y < y0 + 7 for x0, y0 in ((0, 0), (14, 0), (0, 14)))
            if finder:
                xx, yy = (x % 14 if x >= 14 else x), (y % 14 if y >= 14 else y)
                b = xx in (0, 6) or yy in (0, 6) or (2 <= xx <= 4 and 2 <= yy <= 4)
            else:
                b = h[y * 21 + x] % 2 == 0
            cells.append('<i class="b"></i>' if b else '<i></i>')
    return '<div class="qr" aria-hidden="true">%s</div>' % ''.join(cells)


def build_pages():
    members = """
<p class="eyb">Cuotas</p>
<h1 class="h1">Área de miembros</h1>
<p class="lede">Tu cuota se gestiona en una página segura de Stripe. Entras con el correo con el que te
inscribiste y un código que te llega en ese momento. No hay contraseña que recordar.</p>
<span class="lead-btn">Ir a mi cuota</span>
<div class="two"><div><h2 class="h2" style="font-size:1rem">Lo haces tú, al momento</h2>
<ul class="can"><li>Cambiar la tarjeta o la cuenta bancaria</li><li>Actualizar el nombre, la dirección o el teléfono</li>
<li>Descargar los recibos</li><li>Darte de baja, al final del periodo pagado</li></ul></div>
<div><h2 class="h2" style="font-size:1rem">Escríbenos y lo hacemos</h2>
<ul class="can cant"><li>Añadir o quitar personas</li><li>Pasar de mensual a trimestral o anual</li>
<li>Cambiar el correo de la cuota</li><li>La cuota con abono municipal</li></ul></div></div>
<h2 class="h2" style="font-size:1rem;margin-top:1.8rem">Cómo se entra</h2>
<ol class="howto"><li><span>Pulsa <b>Ir a mi cuota</b> y escribe tu correo.</span></li>
<li><span>Stripe te envía un código de seis cifras. Cópialo o pégalo.</span></li>
<li><span>Ya estás dentro. ¿No te llega? Mira el correo no deseado, o escríbenos: puede que te inscribieras con otro correo.</span></li></ol>
<p class="links"><a href="#">Desistir del contrato</a><a href="#">Condiciones de la cuota</a><a href="#">Cuotas</a><a href="#">Privacidad</a><a href="#">Contacto</a></p>
"""
    portal = """
<p class="stp-badge">Stripe's portal · illustrative, Stripe draws it</p>
<div class="portal"><div class="portal-l"><div class="stp-brand" style="color:#fff"><i></i>Aikido Musubi</div>
<p>Gestiona tu cuota de la Associació Cultural Musubi Aikido.</p>
<p style="margin-top:2rem"><a href="#">← Volver a aikidomusubi.com</a></p>
<p style="margin-top:6rem;font-size:.72rem">Powered by stripe · Condiciones · Privacidad</p></div>
<div class="portal-r">
<h3>Suscripción actual</h3>
<div class="prow"><span><b>Cuota general</b> · 3 personas<small>183,00 € cada 3 meses · Próximo cobro el 5 de mayo de 2027</small></span><span class="pbtn">Cancelar suscripción</span></div>
<h3>Métodos de pago</h3>
<div class="prow"><span>Débito SEPA •••• 3000<small>Predeterminado</small></span><span class="pbtn">Añadir método de pago</span></div>
<h3>Información de facturación</h3>
<div class="prow"><span>Ana García López<small>ana.garcia@example.com · +34 600 000 000</small></span><span class="pbtn">Actualizar información</span></div>
<h3>Historial de facturas</h3>
<div class="prow"><span>5 feb 2027<small>183,00 € · Pagado</small></span><span class="pbtn">Cuota general ↓</span></div>
<div class="prow"><span>20 ene 2027<small>30,99 € · Pagado</small></span><span class="pbtn">Cuota general ↓</span></div>
</div></div>"""

    withdraw = """
<p class="eyb">Cuotas</p>
<h1 class="h1">Desistir del contrato</h1>
<p class="lede">Durante los 14 días siguientes a tu inscripción puedes desistir sin dar explicaciones.
Te devolvemos lo pagado en 14 días como máximo, por el mismo medio, menos los días transcurridos hasta hoy si
pediste empezar a entrenar enseguida.</p>
<p class="sub">¿Pasados los 14 días? Entonces es una baja: <a href="#">hazla en tu área de miembros</a>.</p>
<div class="f2"><div class="fld"><label>Nombre y apellidos <span class="req">(obligatorio)</span></label><span class="inp">Ana García López</span></div>
<div class="fld"><label>Correo con el que te inscribiste <span class="req">(obligatorio)</span></label><span class="inp">ana.garcia@example.com</span></div></div>
<div class="fld" style="margin-top:.8rem"><label>Tu declaración</label>
<span class="area">Por la presente comunico que desisto de mi contrato de cuota de entrenamiento con la Associació Cultural Musubi Aikido, celebrado el 20 de enero de 2027.</span>
<p class="hint">Ya viene escrita; puedes cambiarla o añadir lo que quieras.</p></div>
<div style="height:1rem"></div>
<span class="btn" style="width:auto;display:inline-flex;padding:.8rem 1.6rem">Confirmar desistimiento</span>
<p class="hint">Al confirmar, te enviamos un acuse con el contenido, la fecha y la hora.</p>
"""
    withdraw_ok = """
<p class="eyb">Cuotas</p>
<h1 class="h1 ok-h">Desistimiento recibido</h1>
<p class="lede">Lo hemos recibido. Te hemos enviado un acuse a <b>ana.garcia@example.com</b> con esta misma información.</p>
<span class="stamp">Recibido el 27 de enero de 2027 a las 21:14 (hora peninsular)</span>
<ol class="howto"><li><span>Cancelamos tu cuota hoy mismo: no habrá más cobros.</span></li>
<li><span>Te devolvemos lo pagado menos los 7 días transcurridos, antes del <b>10 de febrero</b>, por el mismo medio de pago.</span></li>
<li><span>¿Ha sido un error? Escríbenos hoy a <a href="#">info@aikidomusubi.com</a>.</span></li></ol>
"""
    terms = """
<p class="eyb">Cuotas</p>
<h1 class="h1">Condiciones de la cuota</h1>
<p class="draft">Text pending the legal advisor's review</p>
<p class="lede">Versión 2027-01, en vigor desde el 1 de enero de 2027. <a href="#">Versiones anteriores</a>.</p>
<ol class="toc"><li>Quiénes somos</li><li>Qué cubre la cuota y qué no</li><li>Cuotas, descuento familiar y cuota con abono</li>
<li>El cobro, el día 5, y el primer cobro</li><li>Medios de pago</li><li>Duración y renovación automática</li>
<li>Baja</li><li>Devoluciones</li><li>Cambios de personas o de periodo</li><li>El paso a la cuota de 17 años o más</li>
<li>Cambios de precio</li><li>Derecho de desistimiento y formulario</li><li>Licencia federativa y seguro</li>
<li>El keikogi de regalo</li><li>Protección de datos</li><li>Reclamaciones y contacto</li><li>Ley aplicable</li></ol>
<h2 class="h2">6. Duración y renovación automática</h2>
<p class="sub" style="max-width:40rem">La cuota se renueva sola al final de cada periodo, mes, trimestre o año, y se cobra
el día 5. Quince días antes de cada renovación te avisamos por correo de la fecha y el importe, y de cómo darte de
baja si no quieres continuar.</p>
"""
    fees = """
<p class="eyb">Cuotas</p><h1 class="h1" style="font-size:1.6rem">17 años o más</h1>
<div class="fee-mini">
<div class="fee-c"><span>Mensual</span><b>39 €</b><span>al mes</span><span class="fee-b">Inscribirme</span></div>
<div class="fee-c deal"><span>Trimestral</span><b>99 €</b><span>al trimestre · ahorras 18 €</span><span class="fee-b">Inscribirme</span></div>
<div class="fee-c deal"><span>Anual</span><b>360 €</b><span>al año · ahorras 108 €</span><span class="fee-b">Inscribirme</span></div></div>
<p class="sub" style="margin-top:1rem">La cuota se cobra el día 5, con tarjeta o domiciliación, a través de Stripe.
¿Ya tienes cuota? <a href="#">Área de miembros</a>.</p>"""
    foot = """<div class="foot"><div><b>Cuotas</b><span>Cuotas</span><span class="new">Inscripción</span><span class="new">Área de miembros</span></div>
<div><b>Legal</b><span>Aviso legal</span><span>Privacidad</span><span>Cookies</span><span class="new">Condiciones de la cuota</span><span class="new">Desistir del contrato</span></div>
<div><b>Contacto</b><span>info@aikidomusubi.com</span><span>717 171 177</span></div></div>"""

    qr = """<div class="qr-card"><div><p class="eyb" style="margin:0">Después de tus dos clases de prueba</p>
<h3>Inscríbete en línea</h3><p>Tres minutos. Tarjeta o domiciliación. Sin matrícula.</p>
<p><code>aikidomusubi.com/inscripcion</code></p></div>%s</div>""" % qr_svg()

    changes = [
        ('Cuotas <code>/cuotas/</code> ×4', 'Each card\'s button becomes "Inscribirme" and goes to <code>/inscripcion/?periodo=trimestral&amp;edad=17</code>, which starts at step 1 with that period waiting at step 2. Adds the billing line and the members-area link.'),
        ('Footer, every page', 'Inscripción and Área de miembros under Cuotas; Condiciones de la cuota and Desistir del contrato under Legal. The withdrawal link has to be on every page (spec 11.3).'),
        ('Privacidad ×4', 'New processing activity "online signup and fee collection": data, legal basis, retention; Stripe as processor and separate controller, with the US transfer; Cloudflare and the email provider as processors; "bank details" now held by Stripe, not the dojo.'),
        ('Cookies ×4', 'The signup adds no cookies; <code>sessionStorage</code> keeps the form while paying and is cleared after; Stripe\'s pages follow Stripe\'s policy.'),
        ('Accesibilidad ×4', 'It says the association offers no e-commerce. That stops being true. The new pages come into scope, and Stripe\'s pages are third-party content.'),
        ('Aviso legal ×4', 'A link to the membership terms.'),
        ('Preguntas frecuentes ×4', 'Three new questions: how and when the fee is charged, changing card or account, cancelling. "¿Cuánto cuesta empezar?" points at the signup.'),
        ('Recursos ×4', 'The <b>SEPA mandate form goes</b> at launch, because Stripe takes the mandate. The <b>enrolment form</b> loses anything about choosing the fee or giving bank details. That means editing the PDFs, which I have not seen yet.'),
        ('Contacto, Cómo es una clase, the location pages', 'Their "how to join" lines point at the signup instead of only at contact.'),
        ('llms.txt, mapa del sitio, sitemap.xml', 'The new pages, generated as usual. The thank-you and withdrawal-confirmation pages stay out.'),
        ('humans.txt', 'Stripe, Cloudflare Workers and the email provider, in the commit that adds them.'),
        ('New pages ×4 each', '<code>/inscripcion/</code> (+ <code>gracias/</code>), <code>/miembros/</code>, <code>/condiciones-de-la-cuota/</code>, <code>/desistimiento/</code> (+ <code>recibido/</code>), in ca, en and ja with their own slugs.'),
    ]
    chg = ('<table class="chg"><thead><tr><th>Page</th><th>What changes</th></tr></thead><tbody>%s</tbody></table>'
           % ''.join('<tr><th>%s</th><td>%s</td></tr>' % c for c in changes))

    body = """
<h1 class="pg">Members area, withdrawal, terms, and the rest of the site</h1>
<p class="top-lede"><b>There is no database and no password.</b> Stripe holds the subscription, the
payment method and the invoices, and its customer portal is the members area. Our
<code>/miembros/</code> page explains it and opens it; the member signs in with their email and a
one-time code that Stripe sends. We store nothing and maintain nothing.</p>

<h2 class="sec-t">/miembros/ · Área de miembros</h2>
%s
<div class="notes"><div class="note"><h2>One button</h2><p>"Ir a mi cuota" opens Stripe's no-code portal login link.
Every email we send links here, never to the portal directly, because a portal session link expires in
minutes.</p></div><div class="note"><h2>What is not self-service</h2><p>People, period and email changes go through
the dojo in v1. The spec says so, and it is right: the family price has to be recalculated, and the
portal's "switch plan" knows nothing about families.</p></div><div class="note"><h2>Indexing</h2><p>Public but
<code>noindex</code>: it is useful to members and to nobody arriving from a search.</p></div></div>

<h2 class="sec-t">Stripe's customer portal</h2>
<div class="pair one">%s</div>
<div class="notes"><div class="note"><h2>Configured, not built</h2><p>Payment methods, billing details and invoices on;
cancel at the end of the period, with a reason; switching plan and quantities off. Branding from our tokens.</p></div>
<div class="note"><h2>Cancelling here</h2><p>Sets the subscription to end at the period's close. Our webhook
then sends the member a confirmation and tells the admin. Until the end date the portal shows "Renovar",
so a mistaken cancel can be undone.</p></div><div class="note"><h2>Language</h2><p>Follows the
<code>preferred_locales</code> we set from the signup page. Catalan readers see Spanish.</p></div></div>

<h2 class="sec-t">/desistimiento/ · the withdrawal function</h2>
<div class="pair">%s%s</div>
<div class="notes"><div class="note"><h2>Why a form and not "email us"</h2><p>EU Directive 2023/2673 makes an online
withdrawal function mandatory for contracts concluded on a website, from 19 June 2026: a clearly labelled
link, a short form, and a "confirm withdrawal" button. The consumer then receives an acknowledgement with
the content, the date and the time.</p></div><div class="note"><h2>What happens behind it</h2><p>The Worker emails
the acknowledgement and the admin. The dojo cancels the subscription and refunds within 14 days. The refund is
the one task still worked out by hand; a small command can calculate it (tab 4).</p></div><div class="note">
<h2>After the 14 days</h2><p>The form points to the members area, because what remains is an ordinary
cancellation: no refund, effective at the end of the period.</p></div></div>

<h2 class="sec-t">/condiciones-de-la-cuota/ · the membership terms</h2>
<div class="pair one">%s</div>
<div class="notes"><div class="note"><h2>Versioned</h2><p>Each signup records <code>terms_version</code>; old versions
stay published at their own URLs, because a member is bound by the version they accepted.</p></div>
<div class="note"><h2>The keikogi is a section</h2><p>The rule decided in step 2 belongs in the terms, so that the
answer to "and if I cancel?" is written down.</p></div><div class="note"><h2>Advisor first</h2><p>Every legal
text here is a draft until the advisor has read it. That is the gate before launch.</p></div></div>

<h2 class="sec-t">What changes on pages that exist</h2>
<div class="pair">%s<div>%s<div style="height:1.4rem"></div>%s</div></div>
<div class="notes"><div class="note"><h2>/cuotas/</h2><p>The buttons stop going to Contact. A query string
preselects the period and the age; it never carries personal data.</p></div><div class="note"><h2>The QR</h2><p>For
the end of a trial class: a card that points at <code>/inscripcion/</code>, the short Spanish URL. The page has the
language switcher. Drawn here as an A6 landscape card; the real code is generated from the final URL.</p></div>
<div class="note"><h2>Shared by email</h2><p>Same URL. For somebody the dojo wants to treat specially, such as a free first
month, the spec's invite link does that.</p></div></div>
<div style="height:2rem"></div>
%s
""" % (pair_inline(mk(members), mk(members, True)), portal, mk(withdraw), mk(withdraw_ok, True), mk(terms),
       mk(fees), qr, foot, chg)
    page('inscripcion-paginas.html', 'Signup pages', 'inscripcion-paginas.html', body, EXTRA)


def pair_inline(a, b):
    return '<div class="pair">%s%s</div>' % (a, b)


# ---------------------------------------------------------------------------
# Emails to members
# ---------------------------------------------------------------------------
FOOT = """<div class="em-foot">Associació Cultural Musubi Aikido · CIF G-64799554 · Av. d'Alfons XIII, 351, 08918 Badalona<br>
Te escribimos porque tienes una cuota con nosotros. Para responder, contesta a este correo: llega a info@aikidomusubi.com.<br>
<a href="#">Área de miembros</a> · <a href="#">Condiciones de la cuota</a> · <a href="#">Privacidad</a> · <a href="#">Desistir del contrato</a></div>"""


def email(subject, kind, inner, when, to='ana.garcia@example.com'):
    return ("""<div class="em"><div class="em-meta">De: <b>Aikido Musubi</b> &lt;no-reply@aikidomusubi.com&gt; · Responder a: info@aikidomusubi.com<br>
Para: %s · %s<br>Asunto: <b>%s</b></div>
<div class="em-top"><b>AIKIDO MUSUBI</b><span>%s</span></div><div class="em-bar"></div>
<div class="em-b">%s</div>%s</div>""" % (to, when, subject, kind, inner, FOOT))


def row(em, notes):
    return '<div class="em-row">%s<div class="note">%s</div></div>' % (em, notes)


def build_emails():
    people = ''.join('<tr><td>%s</td><td>%s</td></tr>' % (a, eur(b)) for a, b in (
        ('Ana García López · 17 o más · cuota completa', FULL[Q]['a']),
        ('Marc García López · 17 o más · familia', fam(Q, 'a')),
        ('Lía García Ruiz · hasta 16 · familia', fam(Q, 'c')))) + \
        '<tr class="t"><td>Total cada trimestre</td><td>%s</td></tr>' % eur(H[Q])

    e1 = email('Inscripción hecha: 3 personas, trimestral', 'Confirmación', """
<h3>Ana, ya tenéis cuota</h3>
<p>Gracias por inscribiros. Esta es vuestra cuota, y lo que acordamos.</p>
<table class="em-t">%s</table>
<h4>Cuándo se cobra</h4>
<ul class="em-dates"><li><b>20 de enero, %s</b>: los 16 días hasta el 5 de febrero</li>
<li><b>5 de febrero, %s</b>: el primer trimestre completo</li>
<li>Después, <b>%s</b> cada 5 de mayo, agosto, noviembre y febrero, hasta que os deis de baja</li></ul>
<p>Pagáis con <b>domiciliación SEPA</b>, cuenta •••• 3000. Stripe os avisará antes de cada cargo, y os
avisaremos nosotros 15 días antes de cada renovación.</p>
<h4>Lo que queda</h4>
<p>Traed al dojo la <b>hoja de inscripción firmada</b>, una por persona, y la autorización de uso de imagen.
Están en <a href="#">Recursos</a>. Los <b>3 keikogi</b> os esperan en el dojo cuando se haya cobrado el
trimestre del 5 de febrero: os escribiremos.</p>
<span class="em-btn">Ir al área de miembros</span>
<h4>Las condiciones</h4>
<p>Las aceptasteis al inscribiros; van adjuntas, en la versión 2027-01. Lo esencial: os dais de baja cuando
queráis y se aplica al final del periodo pagado; no hay devolución de la parte no usada, salvo si desistís.</p>
<span class="em-att">condiciones-de-la-cuota-2027-01.pdf</span>
<div class="em-box"><b>Podéis desistir hasta el 3 de febrero de 2027</b>, sin dar explicaciones, en
<a href="#">aikidomusubi.com/desistimiento</a>, respondiendo a este correo o con el formulario que va abajo.
Como pedisteis empezar ya, pagaríais solo los días transcurridos hasta que nos lo digáis.</div>
<p style="font-size:.76rem"><b>Formulario de desistimiento.</b> A la atención de Associació Cultural Musubi Aikido,
Av. d'Alfons XIII, 351, 08918 Badalona, info@aikidomusubi.com: por la presente comunico que desisto de mi
contrato de cuota celebrado el 20 de enero de 2027. Nombre, dirección, firma (solo en papel) y fecha.</p>
""" % (people, eur(PRO[Q]), eur(H[Q]), eur(H[Q])), '20 ene 2027, 18:05')

    e2 = email('Vuestra cuota se renueva el 5 de mayo: 183 €', 'Aviso de renovación', """
<h3>El 5 de mayo se renueva vuestra cuota</h3>
<p class="em-big">%s</p><p>el 5 de mayo de 2027, por el trimestre del 5 de mayo al 4 de agosto, con
domiciliación SEPA en la cuenta •••• 3000.</p>
<p><b>Si queréis seguir, no tenéis que hacer nada.</b> La cuota continúa y se cobra ese día.</p>
<p><b>Si no queréis seguir</b>, daos de baja antes del 5 de mayo: en el área de miembros, respondiendo a este
correo, por teléfono o en el dojo. No hay penalización, y no se cobrará nada más.</p>
<span class="em-btn">Ir al área de miembros</span>
<table class="em-t">%s</table>
""" % (eur(H[Q]), people), '20 abr 2027, 09:00')

    e3 = email('Baja confirmada: vuestra cuota termina el 5 de agosto', 'Baja', """
<h3>Baja confirmada</h3>
<p>Hemos recibido vuestra baja el 10 de junio de 2027. <b>La cuota termina el 5 de agosto</b>, al final del
trimestre pagado, y no habrá más cobros. Hasta ese día podéis seguir entrenando con normalidad.</p>
<p>¿Ha sido sin querer? Hasta el 5 de agosto podéis deshacerla en el área de miembros, con "Renovar".</p>
<span class="em-btn">Ir al área de miembros</span>
<p>Si queréis contarnos por qué os vais, respondednos. Lo leemos.</p>
""", '10 jun 2027, 20:31')

    e4 = email('Vuestra cuota ha terminado', 'Fin de la cuota', """
<h3>Gracias por entrenar con nosotros</h3>
<p>Vuestra cuota terminó ayer, 5 de agosto de 2027. No habrá más cobros. Los recibos siguen en el área de
miembros, con el mismo correo, durante el tiempo que la ley obliga a guardarlos.</p>
<p>Si algún día queréis volver, la inscripción está en <a href="#">aikidomusubi.com/inscripcion</a> y la
puerta del dojo, abierta.</p>
<p style="font-size:.78rem;color:var(--Mute)">La licencia federativa y el seguro van aparte y no se ven afectados por esta baja.</p>
""", '6 ago 2027, 09:00')

    e5 = email('Hemos recibido tu desistimiento', 'Acuse de desistimiento', """
<h3>Desistimiento recibido</h3>
<span class="stamp" style="display:block">27 de enero de 2027, 21:14 (hora peninsular)</span>
<p><b>Lo que nos enviaste:</b></p>
<div class="em-box">Ana García López · ana.garcia@example.com<br>«Por la presente comunico que desisto de mi
contrato de cuota de entrenamiento con la Associació Cultural Musubi Aikido, celebrado el 20 de enero de 2027.»</div>
<p>Cancelamos vuestra cuota hoy: no habrá más cobros. Os devolveremos lo pagado, menos los 7 días
transcurridos, <b>antes del 10 de febrero</b>, por el mismo medio de pago. Os escribiremos con el importe.</p>
<p>¿Ha sido un error? Respondednos hoy y lo dejamos como estaba.</p>
""", '27 ene 2027, 21:14')

    e6 = email('No hemos podido cobrar la cuota del 5 de mayo', 'Problema con el cobro', """
<h3>El banco ha devuelto el cargo</h3>
<p>El cargo de <b>%s</b> del 5 de mayo, con domiciliación en la cuenta •••• 3000, ha sido devuelto por el
banco. Suele pasar cuando la cuenta ha cambiado o no tenía saldo ese día.</p>
<p><b>Lo volveremos a intentar el 9 de mayo.</b> Si la cuenta ha cambiado, actualízala antes en el área de
miembros, o paga con tarjeta.</p>
<span class="em-btn">Actualizar el medio de pago</span>
<p>Vuestra cuota sigue activa. Si hay algún problema, respondednos y lo hablamos.</p>
""" % eur(H[Q]), '7 may 2027, 10:12')

    e7 = email('Pol pasa a la cuota de 17 años o más', 'Cambio de cuota', """
<h3>Pol cumple 17</h3>
<p>Felicidades a Pol. Como dicen las condiciones, a partir del primer cobro después de su cumpleaños pasa a la
cuota de 17 años o más.</p>
<table class="em-t"><tr><td>Cuota de Pol, desde el 5 de marzo</td><td>14 € → 24 € al mes</td></tr>
<tr class="t"><td>Total de vuestra cuota</td><td>53 € → 63 € al mes</td></tr></table>
<p>No tenéis que hacer nada. Hemos borrado su fecha de nacimiento, que solo guardábamos para esto.</p>
""", '20 feb 2027, 09:00', 'jordi.serra@example.com')

    e8 = email('Cambios en vuestra cuota, desde el 5 de mayo', 'Cambio de cuota', """
<h3>Vuestra cuota cambia el 5 de mayo</h3>
<p>Como nos pedisteis, desde el 5 de mayo la cuota pasa a <b>anual</b>, con las mismas tres personas.</p>
<table class="em-t"><tr><td>Hasta el 4 de mayo</td><td>%s al trimestre</td></tr>
<tr class="t"><td>Desde el 5 de mayo</td><td>%s al año</td></tr></table>
<p>El primer cobro anual será el 5 de mayo y los siguientes, cada 5 de mayo. Como ya recibisteis el keikogi
con la cuota trimestral, este cambio no incluye otro.</p>
""" % (eur(H[Q]), eur(H['y'])), '22 abr 2027, 12:40')

    e9 = email('La cuota cambiará el 1 de enero de 2028', 'Aviso de cambio de precio', """
<h3>Cambio de precio desde el 1 de enero de 2028</h3>
<p>La asamblea de la asociación ha aprobado las cuotas de 2028. A vosotros os afecta así:</p>
<table class="em-t"><tr><td>Ahora</td><td>%s al trimestre</td></tr>
<tr class="t"><td>Desde el cobro del 5 de febrero de 2028</td><td>[nuevo importe] al trimestre</td></tr></table>
<p>Os lo decimos con más de un mes de antelación, como dicen las condiciones. <b>Si no estáis de acuerdo</b>,
podéis daros de baja antes de esa fecha, sin coste, en el área de miembros.</p>
""" % eur(H[Q]), '1 dic 2027, 09:00')

    e10 = email('Tu cuota pasa a pago en línea: tu enlace personal', 'Invitación', """
<h3>Hola, Marta: la cuota pasa a pago en línea</h3>
<p>Desde enero de 2027 las cuotas se cobran a través de Stripe, con tarjeta o domiciliación, en lugar de la
domiciliación del banco de siempre. Así cada cual puede cambiar su tarjeta, descargar recibos o darse de baja sin
tener que escribirnos.</p>
<p><b>Este enlace es solo tuyo y sirve una vez</b>, hasta el 31 de enero:</p>
<span class="em-btn">Pasar mi cuota a pago en línea</span>
<p><b>No pagarás dos veces.</b> El enlace no cobra nada hoy: el primer cobro por Stripe será el 5 de febrero,
y desde febrero ya no te pasaremos el recibo del banco.</p>
<p>¿Prefieres que lo hagamos juntos? Pásate por el dojo y lo hacemos en dos minutos.</p>
""", '8 ene 2027, 10:00', 'marta.vidal@example.com')

    e11 = email('Vuestros keikogi os esperan en el dojo', 'Keikogi', """
<h3>Ya podéis recoger los keikogi</h3>
<p>Se ha cobrado vuestro primer trimestre completo, así que los <b>3 keikogi</b> de regalo, uno para Ana,
otro para Marc y otro para Lía, os esperan en el dojo. Decidnos las tallas en la próxima clase, o respondiendo a
este correo.</p>
""", '8 feb 2027, 09:00')

    stripe_rows = [
        ('Receipt', 'Every payment, the first one included', 'Amount, date, a link to the invoice PDF. Our branding and the legal footer we set.'),
        ('SEPA pre-debit notice', 'Before every SEPA debit', 'Mandate reference, Stripe\'s creditor ID, amount and date. Required by the SEPA rules; Stripe sends it.'),
        ('Card payment failed', 'When a card renewal fails', 'With a link to update the card. Ours (above) covers SEPA; we must check in test mode that the two never both send.'),
        ('Card about to expire', 'A month before', 'With a link to update it.'),
        ('One-time login code', 'Each time somebody signs in to the portal', 'Six digits, from Stripe.'),
        ('3-D Secure confirmation', 'When the bank asks to confirm a renewal', 'With a link to confirm.'),
    ]
    stripe_tbl = ('<table class="stripe-list"><thead><tr><th>Stripe sends</th><th>When</th><th>What it carries</th></tr></thead><tbody>%s</tbody></table>'
                  % ''.join('<tr><th>%s</th><td>%s</td><td>%s</td></tr>' % r for r in stripe_rows))

    body = """
<h1 class="pg">Every email a member receives</h1>
<p class="top-lede">Eleven of ours, sent by the Worker through the email provider, in the payer's language, from
<code>no-reply@</code> with replies going to <code>info@</code>. Then six of Stripe's, which we brand but cannot
word. Same household and dates as the steps.</p>
<p class="warn"><b>One flaw found and fixed here:</b> Stripe's "upcoming renewal" event also fires 15 days before
the <b>first full charge</b>. For a signup on the 20th that means a "your fee renews" email the next day, for a
fee that has not started. The confirmation already states that charge, so the renewal notice is
<b>skipped for the first full charge</b> and starts with the one after. <span class="tag tag-q">confirm</span></p>

<h2 class="sec-t">After signing up</h2>
%s%s
<h2 class="sec-t">Every renewal</h2>
%s
<h2 class="sec-t">Leaving</h2>
%s%s%s
<h2 class="sec-t">Money problems</h2>
%s
<h2 class="sec-t">Changes the dojo makes</h2>
%s%s%s
<h2 class="sec-t">January 2027 only: existing members</h2>
%s
<h2 class="sec-t">Stripe's own emails</h2>
<p class="top-lede">Switched on in the Stripe dashboard. They carry our logo and colours and the invoice footer;
the wording is Stripe's.</p>
%s
""" % (
        row(e1, """<h2>Confirmation</h2><p><b>Trigger:</b> <code>checkout.session.completed</code>.</p>
<p><b>Why it exists:</b> consumer law wants the contract on a durable medium, and Stripe's receipt does not carry
our terms. So: people, prices, every date, the payment method, what is still to do, the terms as a PDF, the
withdrawal deadline as a date, and the model form.</p><p>Plural "vosotros" because the household is three;
for one person it reads in the singular. The templates hold both.</p>"""),
        row(e11, """<h2>Keikogi</h2><p><span class="tag tag-more">more</span><b>Trigger:</b> the first full quarterly or
annual invoice is paid, and the 14 days are over. The same moment tells the admin to have them ready.</p>
<p>It also turns the gift into a reason to come back to the dojo with a size, which is the point of it.</p>"""),
        row(e2, """<h2>Renewal notice</h2><p><b>Trigger:</b> <code>invoice.upcoming</code>, 15 days before every renewal,
monthly included (decided).</p><p><b>Why:</b> Ley 10/2025 (TRLGDCU art. 97.1 p): date, amount, that it will
continue and be charged, and how to stop it. The subject line carries the date and amount, so the notice
works without being opened.</p><p>Monthly members get twelve of these a year. That was the board's decision,
and it is worth knowing.</p>"""),
        row(e3, """<h2>Cancellation confirmed</h2><p><b>Trigger:</b> <code>customer.subscription.updated</code> with
<code>cancel_at_period_end</code>, whether the cancellation came from the portal or the dojo did it from an email or a call.</p>
<p>The end date, no more charges, training continues until then, and the way to undo it.</p>"""),
        row(e4, """<h2>Membership ended</h2><p><span class="tag tag-more">more</span><b>Trigger:</b>
<code>customer.subscription.deleted</code>. The spec only tells the admin. One line for the member closes it
properly, and says the licence is a separate matter.</p>"""),
        row(e5, """<h2>Withdrawal acknowledgement</h2><p><b>Trigger:</b> the withdrawal form. The directive requires the
content, date and time. The refund amount is calculated by the dojo, so this email promises a date for it, not
a figure.</p><p>7 days: 20 to 27 January.</p>"""),
        row(e6, """<h2>Payment problem</h2><p><b>Trigger:</b> <code>invoice.payment_failed</code> on a SEPA debit.
Stripe emails card failures itself; whether it does for SEPA has to be checked in test mode, and this email
exists only for the case it does not. Never both.</p><p>A returned SEPA debit costs the dojo 3.50 €: worth
the member knowing their account can be updated before the retry.</p>"""),
        row(e7, """<h2>Age change at 17</h2><p><b>Trigger:</b> the admin presses "apply" in the monthly digest
(tab 4). Sent with the change, never before it.</p><p>It says the date of birth has been deleted, which is
what the spec's data inventory promises.</p>"""),
        row(e8, """<h2>Plan or people changed</h2><p><b>Trigger:</b> the dojo applies a change. From the next billing
date, never mid-period.</p><p>The keikogi line answers the obvious question before it is asked: one per
person, first enrolment only.</p>"""),
        row(e9, """<h2>Price change</h2><p><b>Trigger:</b> the migration script's list, sent at least a month ahead
(decided: one month, in writing). Each member sees their own before and after, not a price table.</p>"""),
        row(e10, """<h2>Invitation</h2><p><b>Trigger:</b> <code>npm run invite</code>, one per existing member.</p>
<p>Its whole job is to remove the fear of paying twice, so it says when the first Stripe charge is and when
the bank stops: the same month, never both. The admin side of that is the third email in tab 4.</p>"""),
        stripe_tbl)
    page('inscripcion-correos.html', 'Member emails', 'inscripcion-correos.html', body, EXTRA)


if __name__ == '__main__':
    build_steps()
    build_pages()
    build_emails()
