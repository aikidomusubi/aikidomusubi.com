#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Paying in cash: the signup's steps 2 and 4, on the real page.

The built /inscripcion/ page with its own CSS, steps 1 and 3 folded away and
the signup script taken out, so the two steps that change can be read side by
side with a family already filled in (one adult and one under-17, monthly,
signing up on Monday 23 November 2026). A switch at the top flips the
example between "card or direct debit" and "cash", so both versions of step 4
can be compared.

Needs a build of the membership-signup branch in _site/ (npx gulp build).

    python3 docs/mockups/src/build_efectivo.py
    ./docs/mockups/render.sh        # then open localhost:4000/mockups/efectivo-inscripcion.html

The panel and the receipt are build_efectivo_panel.ts, which renders the
panel's real views.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
SRC = os.path.join(ROOT, '_site', 'inscripcion', 'index.html')
THANKS = os.path.join(ROOT, '_site', 'inscripcion', 'gracias', 'index.html')
OUT = os.path.join(HERE, '..')

for p in (SRC, THANKS):
    if not os.path.exists(p):
        sys.exit(f'needs {os.path.relpath(p, ROOT)}: run `npx gulp build` on the membership-signup branch first')

PAGE = open(SRC, encoding='utf-8').read()

BANNER_CSS = """
.mk-banner{position:relative;z-index:2000;background:#FFF200;color:#111314;font:14px/1.45 "Noto Sans",Arial,sans-serif;padding:.7rem 1.2rem}
.mk-banner b{font-family:Futura,"Trebuchet MS",Arial,sans-serif;letter-spacing:.04em;text-transform:uppercase;margin-right:.6rem}
.mk-banner a{color:#111314;margin-left:.8rem}
.mk-switch{display:inline-flex;gap:.4rem;margin-left:1rem}
.mk-switch button{font:inherit;border:1px solid #111314;background:#fff;padding:.15rem .6rem;cursor:pointer}
.mk-switch button[aria-pressed=true]{background:#111314;color:#FFF200}
.su-step[data-step="1"],.su-step[data-step="3"],.su-steps,.su-nav{display:none!important}
.su-step{display:block!important}
.su-new{outline:3px dashed #E8A33D;outline-offset:6px}
/* the new piece: the cash card's terms, under the two cards */
.su-cashbox{margin:.9rem 0 0;padding:.9rem 1rem;border-left:4px solid #1A7444;background:#F3F7F2;font-size:.9rem}
.su-cashbox ul{margin:.4rem 0 0;padding-left:1.1rem}
.su-cashbox li{margin:.2rem 0}
"""

METHOD = """
        <fieldset class="su-periods su-method su-new" aria-describedby="su-method-err">
          <legend class="su-legend">Forma de pago <span class="su-req">(obligatorio)</span></legend>
          <div class="su-cards">
            <label class="su-card" data-method="stripe">
              <input type="radio" name="method" value="stripe" data-mk="stripe">
              <span class="su-card-name">Tarjeta o domiciliación</span>
              <span class="su-card-static">Se cobra sola el día 5, a través de Stripe.</span>
            </label>
            <label class="su-card" data-method="cash">
              <input type="radio" name="method" value="cash" data-mk="cash" checked>
              <span class="su-card-name">En efectivo, en el dojo</span>
              <span class="su-card-static">Pagas en mano del día 1 al 5 de cada mes y te enviamos el recibo por correo.</span>
            </label>
          </div>
          <div class="su-cashbox" id="su-cashbox">
            <b>Cómo funciona el pago en efectivo</b>
            <ul>
              <li>La primera cuota se paga en el dojo en los 5 días siguientes a la inscripción.</li>
              <li>Después, del día 1 al 5 de cada periodo, a la persona de la junta que esté en el dojo.</li>
              <li>Cuando lo apunta, te llega el recibo a tu correo. Guárdalo: es tu justificante.</li>
              <li>Si se pasa el día 5, te enviamos un recordatorio. Para cambiar a tarjeta o domiciliación, pídelo en el dojo.</li>
            </ul>
          </div>
          <p class="su-err" id="su-method-err" hidden></p>
        </fieldset>"""

SUMMARY_ROWS = """<tr><td>Marta Serra Mas</td><td>17 o más</td><td>Cuota completa</td><td class="su-rv-unit">39,00 €</td></tr>
<tr><td>Pol Serra Mas</td><td>Hasta 16</td><td>Familia</td><td class="su-rv-unit">14,00 €</td></tr>"""

TL_CASH = """<li class="is-now"><b>Hoy no se cobra nada</b> · pagas en el dojo</li>
<li class="is-now"><b>Antes del sábado 28 de noviembre, 13,99 € en efectivo</b> · los días hasta el 1 de diciembre</li>
<li><b>7 de diciembre</b> · último día para desistir</li>
<li><b>Del 1 al 5 de diciembre, 53,00 € en efectivo</b> · primera cuota completa</li>
<li>Después, <b>53,00 €</b> del 1 al 5 de cada mes, en el dojo</li>"""

TL_CARD = """<li class="is-now"><b>Hoy, unos 21,05 €</b> · los días hasta el 5 de diciembre</li>
<li><b>7 de diciembre</b> · último día para desistir</li>
<li><b>5 de diciembre, 53,00 €</b> · primera cuota completa</li>
<li>Después, <b>53,00 €</b> cada día 5</li>"""

SWITCH_JS = """
<script>
(function(){
  var tl = document.getElementById('su-tl'), pay = document.querySelector('.su-pay'),
      note = document.querySelector('.su-paynote'), box = document.getElementById('su-cashbox'),
      line = document.getElementById('su-method-line'), bs = document.querySelectorAll('.mk-switch button');
  var V = {
    cash: { tl: %s, pay: 'Confirmar la inscripción',
            note: 'No se cobra nada en línea. Te llega un correo con lo que pagas, cuándo y dónde.',
            line: 'En efectivo, en el dojo' },
    stripe: { tl: %s, pay: 'Ir al pago seguro',
            note: 'En Stripe eliges tarjeta o domiciliación y confirmas. Hasta entonces no se cobra nada.',
            line: 'Tarjeta o domiciliación' }
  };
  function show(k){
    tl.innerHTML = V[k].tl; pay.textContent = V[k].pay; note.textContent = V[k].note; line.textContent = V[k].line;
    box.hidden = k !== 'cash';
    document.querySelector('input[data-mk=' + k + ']').checked = true;
    bs.forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.k === k); });
  }
  bs.forEach(function(b){ b.addEventListener('click', function(){ show(b.dataset.k); }); });
  document.querySelectorAll('input[name=method]').forEach(function(r){ r.addEventListener('change', function(){ show(r.value); }); });
  show('cash');
})();
</script>
"""


def build_signup():
    html = PAGE
    # No signup script: the page is a still, with the example filled in.
    html = re.sub(r'<script[^>]*src="/scripts/membership[^"]*"[^>]*></script>', '', html)
    # The method choice goes after the period, still inside step 2.
    m = re.search(r'(<fieldset class="su-periods".*?</fieldset>)', html, re.S)
    if not m:
        sys.exit('step 2 period fieldset not found')
    html = html.replace(m.group(1), m.group(1) + METHOD, 1)
    # Choose the monthly card, as the example family has.
    html = html.replace('name="period" value="monthly"', 'name="period" value="monthly" checked', 1)
    # Step 4: the summary, filled in.
    html = html.replace('<div class="su-review-sum" id="su-summary" hidden>', '<div class="su-review-sum su-new" id="su-summary">', 1)
    html = html.replace('<tbody></tbody>', f'<tbody>{SUMMARY_ROWS}</tbody>', 1)
    html = html.replace('<td class="su-rv-total"></td>', '<td class="su-rv-total">53,00 €</td>', 1)
    html = html.replace('<span id="su-holder-line"></span>',
                        '<span id="su-holder-line">Titular: Marta Serra Mas, marta.serra@example.com</span> · <span>Pago: <b id="su-method-line"></b></span>', 1)
    banner = ('<div class="mk-banner" role="note"><b>Pago en efectivo · inscripción</b>'
              'Pasos 2 y 4 con una familia de ejemplo (mensual, inscripción el 23 de noviembre). '
              'Lo nuevo va recuadrado.<span class="mk-switch" role="group" aria-label="Ejemplo">'
              '<button type="button" data-k="cash">Efectivo</button><button type="button" data-k="stripe">Tarjeta</button></span>'
              '<a href="efectivo-gracias.html">Página de gracias →</a><a href="efectivo-panel.html">Panel →</a><a href="efectivo-recibo.html">Recibo →</a></div>')
    html = html.replace('</head>', f'<style>{BANNER_CSS}</style></head>', 1)
    html = re.sub(r'(<body[^>]*>)', r'\1' + banner, html, count=1)
    js = SWITCH_JS % (repr(TL_CASH.replace('\n', '')), repr(TL_CARD.replace('\n', '')))
    html = html.replace('</body>', js + '</body>', 1)
    with open(os.path.join(OUT, 'efectivo-inscripcion.html'), 'w', encoding='utf-8') as f:
        f.write(html)


THANKS_STEPS = """<li><b>Paga la primera cuota en el dojo antes del sábado 28 de noviembre:</b> 13,99 € en efectivo, por los días hasta el 1 de diciembre. A partir de ahí, 53,00 € del día 1 al 5 de cada mes.</li>
<li><b>Mira tu correo.</b> Te llega nuestra confirmación, con las condiciones y las fechas. Cada vez que pagues, te llegará el recibo. Si no lo ves en unos minutos, revisa el correo no deseado.</li>"""


def build_thanks():
    html = open(THANKS, encoding='utf-8').read()
    # The thanks page's first step is about Stripe's receipt and its fourth
    # about direct debit: for cash both are replaced by the two above.
    lis = re.findall(r'<li>.*?</li>', html, re.S)
    stripe_mail = next((x for x in lis if 'Stripe' in x), None)
    debit = next((x for x in lis if 'domiciliación' in x), None)
    if stripe_mail:
        html = html.replace(stripe_mail, f'<li class="su-new" style="list-style:none;padding:0;margin:0"><ol style="padding-left:0;list-style:none">{THANKS_STEPS}</ol></li>', 1)
    if debit:
        html = html.replace(debit, '', 1)
    html = html.replace('Gracias. Ya tienes cuota y puedes entrenar desde hoy',
                        'Gracias. Ya tienes cuota y puedes entrenar desde hoy; la primera la pagas en el dojo', 1)
    banner = ('<div class="mk-banner" role="note"><b>Pago en efectivo · gracias</b>'
              'La página tras inscribirse en efectivo: sin la página de Stripe, y con lo que hay que pagar, cuánto y hasta cuándo.'
              '<a href="efectivo-inscripcion.html">← Inscripción</a><a href="efectivo-panel.html">Panel →</a></div>')
    html = html.replace('</head>', f'<style>{BANNER_CSS}</style></head>', 1)
    html = re.sub(r'(<body[^>]*>)', r'\1' + banner, html, count=1)
    with open(os.path.join(OUT, 'efectivo-gracias.html'), 'w', encoding='utf-8') as f:
        f.write(html)


build_signup()
build_thanks()
print('wrote docs/mockups/efectivo-inscripcion.html, efectivo-gracias.html')
