// Paying in cash: the panel and the receipt, drawn by the panel's own views.
//
// The real shell, CSS, task rows and family detail from
// services/membership/src/panel/views.ts, fed the panel's demo families (the
// ones `wrangler dev` shows), with the cash pieces added where they would go.
// What is new is outlined in dashed amber, as on the signup mockup.
//
//   cd services/membership && npm run catalog && cd ../..
//   node --experimental-strip-types --no-warnings docs/mockups/src/build_efectivo_panel.ts
//   ./docs/mockups/render.sh   # then localhost:4000/mockups/efectivo-panel.html
//
// Four pages: Pendiente on 3 December with the cash group and the message
// after pressing Cobrado; the confirmation; a family paying cash; the receipt.
import { writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { demoSubscriptions } from '../../../services/membership/src/panel/demo.ts';
import { family, isCurrent, isFormer, linkReturning, tasks } from '../../../services/membership/src/panel/model.ts';
import { membersPage, pendingPage, shell } from '../../../services/membership/src/panel/views.ts';
import { B, render } from '../../../services/membership/src/email/layout.ts';

const OUT = join(dirname(fileURLToPath(import.meta.url)), '..');
const now = Date.UTC(2026, 11, 3, 10, 0); // Thursday 3 December 2026, 11:00 in Madrid
const user = { email: 'admin@aikidomusubi.com', name: 'Alberto', csrf: 'x', exp: 0 } as never;

const subs = demoSubscriptions(now);
const fams = subs.filter(isCurrent).map(family);
const former = subs.filter(isFormer).map(family);
linkReturning(fams, former);
const list = tasks(fams);

const CASH = '<rect x="3" y="6" width="18" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M6.5 9.5v.01M17.5 14.5v.01"/>';
const ic = (p: string) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${p}</svg>`;
const CHECK = '<path d="M5 12l4 4 10-10"/>';

const NEW_CSS = `.mk-new{outline:3px dashed #E8A33D;outline-offset:4px}
.mk-banner{background:#FFF200;color:#111314;font:14px/1.45 "Noto Sans",Arial,sans-serif;padding:.7rem 1.2rem}
.mk-banner b{text-transform:uppercase;letter-spacing:.04em;margin-right:.6rem}
.mk-banner a{color:#111314;margin-left:.8rem}
.ic.cash{background:#E6F0E8;color:#1A7444}
.tx span.late,.late{display:inline-block;width:auto;font-size:.72rem;font-weight:700;color:#A62C37;background:#FBEAEC;padding:.05rem .45rem;border-radius:99px;margin-right:.3rem}`;

const PAGES = [['efectivo-panel.html', 'Pendiente'], ['efectivo-panel-confirmar.html', 'Confirmar'],
  ['efectivo-panel-familia.html', 'Una familia'], ['efectivo-recibo.html', 'El recibo']] as const;

function page(file: string, title: string, note: string, html: string) {
  const nav = PAGES.filter(([f]) => f !== file).map(([f, t]) => `<a href="${f}">${t}</a>`).join('')
    + '<a href="efectivo-inscripcion.html">Inscripción</a>';
  html = html.replace('</head>', `<style>${NEW_CSS}</style></head>`)
    .replace(/<body([^>]*)>/, `<body$1><div class="mk-banner" role="note"><b>Pago en efectivo · ${title}</b>${note}${nav}</div>`);
  writeFileSync(join(OUT, file), html);
}

// ---------------------------------------------------------------------------
// 1. Pendiente, the morning of 3 December.
const row = (av: string, who: string, what: string, btn: string) => `<li class="task"><span class="av" aria-hidden="true">${av}</span>
<div class="tx"><b><a href="efectivo-panel-familia.html">${who}</a></b><span>${what}</span></div><div class="btns">${btn}</div></li>`;
const cobrado = (who: string) => `<a class="btn" href="efectivo-panel-confirmar.html">${ic(CASH)}Cobrado…<span class="sr"> ${who}</span></a>`;
const cashGroup = `<section class="group mk-new" aria-labelledby="g-cash"><div class="gh"><span class="ic cash">${ic(CASH)}</span>
<div><h2 id="g-cash">Cuotas en efectivo por cobrar</h2><p>Se pagan en el dojo del día 1 al 5. Cuando te paguen, pulsa Cobrado: queda apuntado y la familia recibe el recibo por correo.</p></div><span class="cnt" aria-label="4 por hacer">4</span></div>
<ul class="tasks">
${row('JF', 'Familia Ferrer', '<span class="late">Con retraso</span>Mensual · 39,00 € · tocaba del 1 al 5 de noviembre · recordatorio enviado el 6', cobrado('Familia Ferrer'))}
${row('LP', 'Laia Puig Soler', 'Primera cuota · 21,40 € · antes del 6 de diciembre · inscripción hace 2 días', cobrado('Laia Puig Soler'))}
${row('NV', 'Núria Vila Bosch', 'Trimestral · 99,00 € · del 1 al 5 de diciembre', cobrado('Núria Vila Bosch'))}
${row('MS', 'Familia Serra', 'Mensual · 53,00 € · del 1 al 5 de diciembre', cobrado('Familia Serra'))}
</ul></section>`;
const toastCash = `<div class="toast mk-new" role="status">${ic(CHECK)}<span>Cobro en efectivo apuntado: 53,00 € de la Familia Serra. Marta tiene el recibo en su correo.</span></div>`;
let pend = pendingPage(user, fams, list, now, null);
pend = pend.replace('<div class="cols">', `<div class="cols">${cashGroup}`);
pend = pend.replace(/<h1 class="hello">/, `${toastCash}<h1 class="hello">`);
pend = pend.replace(/Hay <b>(\d+) cosas<\/b>/, (_, n) => `Hay <b>${Number(n) + 4} cosas</b>`);
page('efectivo-panel.html', 'Pendiente', 'El 3 de diciembre: el grupo nuevo, y el mensaje que sale después de pulsar Cobrado. Los retrasos van primero.',
  shell({ title: 'Pendiente', tab: 'p', user, test: true, counts: { pending: list.length + 4, members: fams.length }, body: pend }));

// ---------------------------------------------------------------------------
// 2. The confirmation, before anything is written down.
const sheet = `<div class="sheet mk-new" role="group" aria-labelledby="ask-h"><h1 id="ask-h">¿Has cobrado 53,00 € en efectivo de la Familia Serra?</h1>
<p>Cuota mensual de <b>diciembre</b>, del 1 al 31. Al confirmar queda apuntada como pagada y Marta recibe el recibo en <b>marta.serra@example.com</b>.</p>
<div class="sum"><div><span>Marta Serra Mas · 17 o más · completa</span><b>39,00 €</b></div>
<div><span>Pol Serra Mas · hasta 16 · familia</span><b>14,00 €</b></div>
<div class="tot"><span>Total en efectivo</span><b>53,00 €</b></div></div>
<p class="note">Cuenta el dinero con la persona delante antes de confirmar. Un cobro apuntado no se borra desde aquí: si te equivocas, avisa a quien mantiene la web.</p>
<a class="btn big" href="efectivo-panel.html">Sí, cobrado: enviar el recibo</a>
<a class="btn alt big" href="efectivo-panel.html">No, volver</a></div>`;
page('efectivo-panel-confirmar.html', 'Confirmar', 'Lo que se ve al pulsar Cobrado. El importe sale de Stripe: no se escribe a mano.',
  shell({ title: 'Confirmar', tab: null, user, test: true, body: sheet }));

// ---------------------------------------------------------------------------
// 3. A family that pays cash: the Serras, as in the signup example.
const serra = fams.find((f) => f.id === 'sub_demoSerra001')!;
let fam = membersPage(user, fams, former, list, '', 'todos', { fam: serra, log: [], invoices: [], names: new Map() }, null);
fam = fam.replace(/<dt>Próximo cobro<\/dt><dd>[^<]*<\/dd>/, '<dt>Próxima cuota</dt><dd>del 1 al 5 de enero</dd>')
  .replace(/(<dt>Periodo<\/dt><dd>[^<]*<\/dd>)/, '$1<dt class="mk-new">Pago</dt><dd class="mk-new">En efectivo, en el dojo</dd>')
  .replace(/<dt>Pago<\/dt><dd>(Tarjeta|Domiciliación SEPA)<\/dd>/, '')
  .replace('<ul class="tl">', `<ul class="tl mk-new"><li class="g"><time datetime="2026-12-03">3 dic 2026</time>Cobrado en efectivo · 53,00 € · recibo 2026-0412 <small> · Alberto</small></li>
<li class="g"><time datetime="2026-11-04">4 nov 2026</time>Cobrado en efectivo · 53,00 € · recibo 2026-0377 <small> · Alberto</small></li>`)
  .replace('<div class="actions">', `<div class="actions"><a class="btn alt mk-new" href="efectivo-recibo.html">${ic(CASH)}Reenviar el último recibo</a>
<a class="btn alt mk-new" href="#">${ic('<path d="M4 7h13l-3-3M20 17H7l3 3"/>')}Pasar a tarjeta o domiciliación…</a>`)
  .replace(/<p>Añadir o quitar personas/, '<p class="mk-new">Pasar a tarjeta o domiciliación envía a la familia un enlace para dar los datos en Stripe; desde la cuota siguiente se cobra sola el día 5. </p><p>Añadir o quitar personas');
page('efectivo-panel-familia.html', 'Una familia', 'Paga en efectivo: se dice en la ficha, cada cobro sale en la historia con su recibo, y se puede reenviar o cambiar la forma de pago.',
  shell({ title: 'Familia Serra', tab: 'm', user, test: true, counts: { pending: list.length + 4, members: fams.length }, body: fam }));

// ---------------------------------------------------------------------------
// 4. The receipt the family receives.
const mail = render('es', 'Recibo', [
  B.p('Hola, Marta:'),
  B.h('Recibo de tu cuota'),
  B.p('Hemos recibido el pago de tu cuota en efectivo. Este correo es tu recibo: guárdalo.'),
  B.table([
    ['Recibo n.º', '2026-0412'],
    ['Fecha de pago', '3 de diciembre de 2026'],
    ['Forma de pago', 'Efectivo, en el dojo'],
    ['Periodo', 'Diciembre de 2026 (mensual)'],
    ['Marta Serra Mas · 17 o más · completa', '39,00 €'],
    ['Pol Serra Mas · hasta 16 · familia', '14,00 €'],
    ['Total pagado', '53,00 €']
  ], true),
  B.small('Cuota de socio de la Associació Aikido Musubi, CIF G-64799554, Av. d\'Alfons XIII, 351, 08918 Badalona.'),
  B.p('La próxima cuota, 53,00 €, se paga en el dojo del 1 al 5 de enero.'),
  B.button('Área de miembros', 'https://aikidomusubi.com/miembros/')
], 'https://aikidomusubi.com');
page('efectivo-recibo.html', 'El recibo', 'El correo que llega al pulsar Cobrado. El número es el de la factura en Stripe, así hay un solo registro.',
  `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Recibo</title></head><body style="margin:0;background:#EEE">${mail.html}</body></html>`);

console.log('wrote docs/mockups/efectivo-panel*.html, efectivo-recibo.html');
