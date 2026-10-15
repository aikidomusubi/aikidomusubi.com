// The panel's pages, as approved in docs/mockups/panel-cuotas.html. Spanish
// only, plain words: it is read by a volunteer at the dojo, often on a phone.
//
// Every page works without JavaScript. Each button is a small form that posts
// and comes back to the same place with a message; the ones that change what
// a family pays go through a confirmation page first. /panel/app.js only adds
// filtering the member list as you type.
import type Stripe from 'stripe';
import { KNOT, esc, madrid, money, venueName } from '../data.ts';
import type { ActionKind, LogEntry } from '../actions.ts';
import { CSS } from './style.ts';
import { PERIOD, UNIT, ago, feeLabel, short, type Family, type Person, type Task, type TaskKind } from './model.ts';
import type { Session } from './auth.ts';

// ---------------------------------------------------------------------------
// Icons: simple strokes, drawn here so the panel loads nothing from elsewhere.
const PATHS: Record<string, string> = {
  paper: '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 16h5"/>',
  keikogi: '<path d="M8 3l4 3 4-3 4 4-3 3v11H7V10L4 7z"/><path d="M12 6v15"/>',
  sc: '<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18M7 15h4"/>',
  age: '<path d="M4 21h16v-7H4zM4 17h16M12 14V9M12 5v.01"/>',
  money: '<path d="M17 6a7 7 0 1 0 0 12M5 10h9M5 14h9"/>',
  check: '<path d="M5 12l4 4 10-10"/>',
  search: '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
  list: '<path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01"/>',
  people: '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M16 11a3 3 0 1 0 0-6M17 14c2.3.5 4 2.6 4 5"/>',
  help: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.5V14M12 17h.01"/>',
  ext: '<path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6"/>',
  door: '<path d="M5 21V4h10v17M15 12h.01M15 4l4 1v16"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/>',
  alert: '<path d="M12 3l9 16H3z"/><path d="M12 10v4M12 17h.01"/>',
  left: '<path d="M15 5l-7 7 7 7"/>',
  withdrawal: '<path d="M9 14L4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 0 12h-3"/>'
};
export const icon = (n: string) =>
  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${PATHS[n]}</svg>`;

const mark = () => `<span class="mark">${KNOT.replace('<svg ', '<svg aria-hidden="true" focusable="false" ')}</span>`;
const FAVICON = `data:image/svg+xml,${encodeURIComponent(KNOT)}`;

export const initials = (name: string) =>
  name.split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]!.toUpperCase()).join('');

const m = (n: number) => money(n, 'es');

// ---------------------------------------------------------------------------
export interface Shell {
  title: string;
  tab: 'p' | 'm' | 'h' | null;
  user: Session | null;
  test: boolean;
  counts?: { pending: number; members: number };
  body: string;
  script?: boolean;
}

export function shell(s: Shell): string {
  const tabs = s.user && s.tab !== undefined ? `<nav class="nav" aria-label="Secciones">
${navLink('/panel/', 'Pendiente', 'list', s.tab === 'p', s.counts?.pending)}
${navLink('/panel/miembros', 'Miembros', 'people', s.tab === 'm', s.counts?.members)}
${navLink('/panel/ayuda', 'Ayuda', 'help', s.tab === 'h')}
</nav>` : '';
  const who = s.user ? `<span class="who">${esc(s.user.name || s.user.email)}</span>
<form method="post" action="/panel/salir"><input type="hidden" name="csrf" value="${esc(s.user.csrf)}"><button class="out" type="submit">Salir</button></form>` : '';
  return `<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#111314">
<title>${esc(s.title)} · Cuotas</title><link rel="icon" href="${FAVICON}">
<style>${CSS}</style></head><body>
<a class="skip" href="#main">Saltar al contenido</a>
<header class="top">${mark()}<a class="name" href="/panel/">Cuotas</a>${s.test ? '<span class="mode" title="Datos de prueba de Stripe: nada es real">Pruebas</span>' : ''}<span class="sp"></span>${who}</header>
${tabs}
<main id="main" tabindex="-1">${s.body}</main>
${s.script ? '<script src="/panel/app.js" defer></script>' : ''}
</body></html>`;
}

function navLink(href: string, label: string, ic: string, on: boolean, n?: number) {
  const badge = n ? ` <span class="n">${n}<span class="sr"> ${label === 'Pendiente' ? 'cosas' : 'cuotas'}</span></span>` : '';
  return `<a href="${href}"${on ? ' aria-current="page"' : ''}>${icon(ic)}${label}${badge}</a>`;
}

// ---------------------------------------------------------------------------
// Buttons. Every one is a form: a link that changed something would be
// followed by a browser's prefetch or an email scanner.
export interface Ctx { csrf: string; back: 'p' | 'm' }

export function actBtn(c: Ctx, a: ActionKind, sub: string, slot: number | null, label: string, cls = '', ic = 'check', sr = '') {
  return `<form method="post" action="/panel/accion">
<input type="hidden" name="csrf" value="${esc(c.csrf)}"><input type="hidden" name="a" value="${a}">
<input type="hidden" name="s" value="${esc(sub)}">${slot != null ? `<input type="hidden" name="n" value="${slot}">` : ''}
<input type="hidden" name="back" value="${c.back}">
<button class="btn ${cls}" type="submit">${ic ? icon(ic) : ''}${esc(label)}${sr ? `<span class="sr"> ${esc(sr)}</span>` : ''}</button></form>`;
}

export function askBtn(c: Ctx, a: ActionKind, sub: string, slot: number | null, label: string, cls = 'alt', ic = '', sr = '') {
  const q = new URLSearchParams({ a, s: sub, back: c.back });
  if (slot != null) q.set('n', String(slot));
  return `<a class="btn ${cls}" href="/panel/confirmar?${esc(q.toString())}">${ic ? icon(ic) : ''}${esc(label)}${sr ? `<span class="sr"> ${esc(sr)}</span>` : ''}</a>`;
}

const stripeLink = (href: string, label = 'Ver en Stripe', cls = 'alt') =>
  `<a class="btn ${cls}" href="${esc(href)}" target="_blank" rel="noopener noreferrer">${icon('ext')}${esc(label)}<span class="sr"> (se abre en otra pestaña)</span></a>`;

// ---------------------------------------------------------------------------
// The message after a button, with Deshacer for the everyday marks.
export interface Flash { a: string; fam?: Family; person?: Person | null; error?: boolean }

const UNDO: Partial<Record<ActionKind, ActionKind>> = { paper: 'paper_undo', keikogi: 'keikogi_undo', sc_ok: 'sc_undo' };

export function toast(f: Flash | null, c: Ctx): string {
  if (!f) return '';
  if (f.error) {
    return `<div class="toast err" role="alert">${icon('alert')}<span>No se ha podido hacer. Vuelve a probar en un momento; si sigue sin funcionar, avisa a quien mantiene la web.</span></div>`;
  }
  const p = f.person;
  const fam = f.fam;
  const who = p?.first ?? '';
  const text: Record<string, string> = {
    paper: `Hoja de ${who}: recibida.`,
    keikogi: `Keikogi de ${who}: entregado.`,
    sc_ok: `Abono de ${who}: comprobado.`,
    paper_undo: 'Deshecho: la hoja vuelve a estar por recoger.',
    keikogi_undo: 'Deshecho: el keikogi vuelve a estar por entregar.',
    sc_undo: 'Deshecho: el abono vuelve a estar por comprobar.',
    sc_no: `${who} pasa a la cuota general desde el próximo cobro. La familia ya tiene el correo.`,
    age: `${who} pasa a la cuota de 17 o más desde el próximo cobro. La familia ya tiene el correo.`,
    cancel: `Baja hecha${fam?.endsAt ? `: la cuota termina el ${short(fam.endsAt)}` : ''}. La familia recibe un correo de confirmación.`,
    resume: 'Baja anulada: la cuota sigue como antes.',
    withdraw: `Desistimiento resuelto${fam?.refunded != null ? `: devueltos ${m(fam.refunded)}` : ''}. La cuota ha terminado y la familia tiene el correo con el importe.`,
    withdraw_dismiss: 'Desistimiento quitado de la lista. La cuota sigue.',
    leave: `Baja hecha${fam?.refunded != null ? `: devueltos ${m(fam.refunded)}` : ''}. La cuota ha terminado y la familia tiene el correo con el importe.`
  };
  if (!(f.a in text)) return '';
  const undo = UNDO[f.a as ActionKind];
  const undoForm = undo && fam && p ? `<form method="post" action="/panel/accion">
<input type="hidden" name="csrf" value="${esc(c.csrf)}"><input type="hidden" name="a" value="${undo}">
<input type="hidden" name="s" value="${esc(fam.id)}"><input type="hidden" name="n" value="${p.slot}"><input type="hidden" name="back" value="${c.back}">
<button type="submit">Deshacer</button></form>` : '';
  return `<div class="toast" role="status">${icon('check')}<span>${esc(text[f.a])}</span>${undoForm}</div>`;
}

// ---------------------------------------------------------------------------
export function greeting(now: number, name: string): string {
  const [h, mi] = madrid(now).time.split(':').map(Number);
  const t = h * 60 + mi;
  const word = t >= 6 * 60 && t < 14 * 60 ? 'Buenos días' : t >= 14 * 60 && t < 21 * 60 ? 'Buenas tardes' : 'Buenas noches';
  return name ? `${word}, ${name}` : word;
}

interface GroupDef { title: string; sub: string }
export const GROUPS: Record<TaskKind, GroupDef> = {
  withdrawal: { title: 'Desistimientos', sub: 'Hay que resolverlos antes de 14 días desde la solicitud. El importe ya está calculado: un botón devuelve el dinero, termina la cuota y escribe a la familia.' },
  paper: { title: 'Hojas de inscripción por recoger', sub: 'En papel y firmadas, una por persona. Las de menores, con la firma de madre, padre o tutor.' },
  keikogi: { title: 'Keikogi para entregar', sub: 'Ya se ha cobrado el primer trimestre o año completo y han pasado los 14 días para desistir.' },
  sc: { title: 'Abonos municipales por comprobar', sub: 'Pide el carné del polideportivo en su primera clase allí.' },
  age: { title: 'Cumplen 17', sub: 'Pasan a la cuota de 17 años o más desde el próximo cobro. La familia recibe un correo.' },
  money: { title: 'Cobros que no han pasado', sub: 'Stripe lo reintenta solo y la familia ya tiene un correo. Si no se resuelve, habla con ella.' }
};
const ORDER: TaskKind[] = ['withdrawal', 'paper', 'keikogi', 'sc', 'age', 'money'];

const famLink = (f: Family, text: string) => `<a href="/panel/miembros?id=${esc(f.id)}">${esc(text)}</a>`;
const inFamily = (f: Family) => (f.people.length > 1 ? `${f.name} · ` : '');

function taskRow(t: Task, c: Ctx): string {
  const f = t.fam;
  const p = t.person;
  let who = p ? p.name : f.name;
  let what = '';
  let btns = '';
  switch (t.kind) {
    case 'paper':
      what = `${inFamily(f)}${p!.cat === 'youth' ? 'menor de edad · ' : ''}inscripción ${ago(f.created)}`;
      btns = actBtn(c, 'paper', f.id, p!.slot, 'Recibida', '', 'check', `la hoja de ${p!.name}`);
      break;
    case 'keikogi':
      what = `${inFamily(f)}${PERIOD[f.period]} · inscripción ${ago(f.created)}`;
      btns = actBtn(c, 'keikogi', f.id, p!.slot, 'Entregado', '', 'check', `el keikogi de ${p!.name}`);
      break;
    case 'sc':
      what = `${venueName(p!.venue, 'es')} · ${m(p!.amount)} al mes · inscripción ${ago(f.created)}`;
      btns = actBtn(c, 'sc_ok', f.id, p!.slot, 'Comprobado', '', 'check', `el abono de ${p!.name}`)
        + askBtn(c, 'sc_no', f.id, p!.slot, 'No es válido…', 'warn', '', `el abono de ${p!.name}`);
      break;
    case 'age':
      what = `${inFamily(f)}nueva cuota desde el cobro del ${short(p!.ageFrom!)}`;
      btns = askBtn(c, 'age', f.id, p!.slot, 'Aplicar y avisar…', 'alt', '', `la cuota de 17 o más a ${p!.name}`);
      break;
    case 'withdrawal':
      who = f.name;
      if (f.withdrawalInWindow) {
        what = `Recibido el ${short(f.withdrawalAt!)} · resolver antes del ${short(f.withdrawalAt! + 14 * 86400000)}`;
        btns = askBtn(c, 'withdraw', f.id, null, 'Resolver…', '', '', `el desistimiento de ${f.name}`);
      } else {
        what = `Recibido el ${short(f.withdrawalAt!)}, pasados los 14 días: es una baja, no un desistimiento`;
        btns = askBtn(c, 'cancel', f.id, null, 'Dar de baja…', 'alt', '', f.name)
          + askBtn(c, 'withdraw_dismiss', f.id, null, 'Quitar de la lista…', 'alt', '', `el desistimiento de ${f.name}`);
      }
      break;
    case 'money':
      who = f.name;
      what = `${f.failedAmount != null ? m(f.failedAmount) : ''}${f.method ? ` · ${f.method}` : ''}`;
      btns = stripeLink(stripeUrl(f.id));
      break;
  }
  return `<li class="task"><span class="av" aria-hidden="true">${esc(initials(p ? p.name : f.name))}</span>
<div class="tx"><b>${famLink(f, who)}</b><span>${esc(what)}</span></div><div class="btns">${btns}</div></li>`;
}

let STRIPE_BASE = 'https://dashboard.stripe.com/test/';
export function setStripeBase(live: boolean) { STRIPE_BASE = `https://dashboard.stripe.com/${live ? '' : 'test/'}`; }
const stripeUrl = (id: string) => `${STRIPE_BASE}subscriptions/${id}`;

export function pendingPage(user: Session, fams: Family[], list: Task[], now: number, flash: Flash | null): string {
  const c: Ctx = { csrf: user.csrf, back: 'p' };
  const people = fams.reduce((s, f) => s + f.people.length, 0);
  const { y, m: mo } = madrid(now);
  const thisMonth = fams.filter((f) => { const d = madrid(f.created); return d.y === y && d.m === mo; }).length;
  const ending = fams.filter((f) => f.endsAt).length;
  const n = list.length;
  const groups = ORDER.map((k) => {
    const items = list.filter((t) => t.kind === k);
    if (!items.length) return '';
    const g = GROUPS[k];
    return `<section class="group" aria-labelledby="g-${k}"><div class="gh"><span class="ic ${k}">${icon(k)}</span>
<div><h2 id="g-${k}">${esc(g.title)}</h2><p>${esc(g.sub)}</p></div><span class="cnt" aria-label="${items.length} por hacer">${items.length}</span></div>
<ul class="tasks">${items.map((t) => taskRow(t, c)).join('')}</ul></section>`;
  }).join('');
  const body = n ? `<div class="cols">${groups}</div>` : `<div class="empty"><div class="okc">${icon('check')}</div><h2>Todo al día</h2>
<p>No hay nada pendiente. Cuando alguien se inscriba, o haya un keikogi listo o un cumpleaños, aparecerá aquí.</p></div>
<p class="help">${icon('info')}<span>Cada mañana se revisan los keikogi listos para entregar. El día 20 llega además un resumen por correo con lo que siga pendiente.</span></p>`;
  return `${toast(flash, c)}<h1 class="hello">${esc(greeting(now, user.name))}</h1>
<p class="sub">${n ? `Hay <b>${n} ${n === 1 ? 'cosa' : 'cosas'}</b> por hacer.` : 'Nada por hacer ahora mismo.'}</p>
<ul class="stats" aria-label="Resumen">
<li class="stat"><a href="/panel/miembros"><b>${fams.length}</b><span>cuotas activas</span></a></li>
<li class="stat"><a href="/panel/miembros"><b>${people}</b><span>personas entrenando</span></a></li>
<li class="stat"><b>${thisMonth}</b><span>${thisMonth === 1 ? 'inscripción' : 'inscripciones'} este mes</span></li>
<li class="stat"><a href="/panel/miembros?f=bajas"><b>${ending}</b><span>${ending === 1 ? 'baja en curso' : 'bajas en curso'}</span></a></li></ul>
${body}`;
}

// ---------------------------------------------------------------------------
export type Filter = 'todos' | 'pendiente' | 'cobros' | 'bajas' | 'abono' | 'antiguos';
export const FILTERS: [Filter, string, (f: Family, t: Task[]) => boolean][] = [
  ['todos', 'Todos', () => true],
  ['pendiente', 'Con algo pendiente', (f, t) => t.some((x) => x.fam.id === f.id)],
  ['cobros', 'Cobros pendientes', (f) => f.status === 'failed'],
  ['bajas', 'Bajas en curso', (f) => Boolean(f.endsAt)],
  ['abono', 'Con abono municipal', (f) => f.people.some((p) => p.rate === 'sc')],
  // Read from the former memberships, not the current ones: see membersPage.
  ['antiguos', 'Antiguos miembros', () => true]
];

export const fold = (s: string) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const searchText = (f: Family) => fold([f.name, f.holder, f.email, ...f.people.map((p) => p.name)].join(' '));

const REASON: Record<string, string> = { withdrawal: 'desistimiento', baja: 'baja', impago: 'impago' };

function famChips(f: Family): string {
  if (f.status === 'ended') return `<ul class="chips">${statusChip(f, 'li')}</ul>`;
  const out: string[] = [statusChip(f, 'li')];
  if (f.withdrawalAt) out.unshift('<li class="chip bad">Desistimiento por resolver</li>');
  if (f.before.length) out.push('<li class="chip info">Vuelve</li>');
  const count = (pred: (p: Person) => boolean) => f.people.filter(pred).length;
  const paper = count((p) => p.paper === 'due');
  const kei = count((p) => p.keikogi === 'ready');
  const sc = count((p) => p.sc === 'pending');
  const age = count((p) => Boolean(p.ageFrom));
  if (paper) out.push(`<li class="chip todo">${paper} ${paper === 1 ? 'hoja' : 'hojas'} por recoger</li>`);
  if (kei) out.push(`<li class="chip todo">${kei} keikogi por entregar</li>`);
  if (sc) out.push(`<li class="chip todo">Abono por comprobar</li>`);
  if (age) out.push(`<li class="chip todo">Cumple 17</li>`);
  return `<ul class="chips">${out.join('')}</ul>`;
}

function statusChip(f: Family, tag = 'span') {
  if (f.status === 'ended') return `<${tag} class="chip wait">Terminó el ${esc(short(f.ended!))} · ${REASON[f.endReason ?? 'baja']}</${tag}>`;
  if (f.status === 'failed') return `<${tag} class="chip bad">Cobro pendiente</${tag}>`;
  if (f.endsAt) return `<${tag} class="chip info">Baja el ${esc(short(f.endsAt))}</${tag}>`;
  return `<${tag} class="chip ok">Al día</${tag}>`;
}

function famMeta(f: Family) {
  const ppl = `${f.people.length} ${f.people.length === 1 ? 'persona' : 'personas'}`;
  if (f.ended) return `${PERIOD[f.period]} · ${ppl} · de ${short(f.created)} a ${short(f.ended)}`;
  const when = f.endsAt ? `termina el ${short(f.endsAt)}` : `próximo cobro ${short(f.next)}`;
  return `${PERIOD[f.period]} · ${m(f.total)} · ${ppl} · ${when}`;
}

export interface Detail { fam: Family; log: LogEntry[]; invoices: Stripe.Invoice[]; names: Map<string, string> }

export function membersPage(user: Session, fams: Family[], former: Family[], list: Task[], q: string, filter: Filter, detail: Detail | null, flash: Flash | null): string {
  const c: Ctx = { csrf: user.csrf, back: 'm' };
  const test = FILTERS.find(([k]) => k === filter)?.[2] ?? (() => true);
  const qf = fold(q.trim());
  const pool = filter === 'antiguos' ? former : fams;
  const shown = pool.filter((f) => test(f, list) && (!qf || searchText(f).includes(qf)))
    .sort((a, b) => filter === 'antiguos' ? b.ended! - a.ended! : a.name.localeCompare(b.name, 'es'));
  const chips = FILTERS.map(([k, label, fn]) => {
    const n = k === 'antiguos' ? former.length : fams.filter((f) => fn(f, list)).length;
    const qs = new URLSearchParams({ ...(k !== 'todos' ? { f: k } : {}), ...(q ? { q } : {}) }).toString();
    return `<li><a href="/panel/miembros${qs ? '?' + esc(qs) : ''}"${k === filter ? ' aria-current="true"' : ''}>${esc(label)} · ${n}</a></li>`;
  }).join('');
  const cards = shown.map((f) => {
    const sel = detail?.fam.id === f.id;
    const qs = new URLSearchParams({ id: f.id, ...(filter !== 'todos' ? { f: filter } : {}), ...(q ? { q } : {}) }).toString();
    return `<li class="fam" data-search="${esc(searchText(f))}"${sel ? ' aria-current="true"' : ''}><a class="open" href="/panel/miembros?${esc(qs)}">
<h3>${esc(f.name)}</h3><div class="meta">${esc(famMeta(f))}</div>
<div class="ppl">${esc(f.people.map((p) => p.first).join(', '))}</div>${famChips(f)}</a></li>`;
  }).join('');
  const listHtml = `<div class="list"><h1 class="page">Miembros</h1>
<form class="search" method="get" action="/panel/miembros" role="search">
<label>${icon('search')}<span class="sr">Buscar</span><input id="q" type="search" name="q" value="${esc(q)}" placeholder="Busca por nombre, apellido o correo" autocomplete="off"></label>
${filter !== 'todos' ? `<input type="hidden" name="f" value="${filter}">` : ''}<button class="btn alt" type="submit">Buscar</button></form>
<ul class="filters" aria-label="Filtros">${chips}</ul>
<p class="sr" id="shown" aria-live="polite">${shown.length} ${shown.length === 1 ? 'cuota' : 'cuotas'}</p>
<ul class="fams">${cards}</ul>
<p class="none"${shown.length ? ' hidden' : ''}>${filter === 'antiguos' && !qf ? 'Todavía no ha terminado ninguna cuota.' : 'Ninguna cuota coincide.'}${q || filter !== 'todos' ? ' <a href="/panel/miembros">Ver todas</a>' : ''}</p></div>`;
  return `${toast(flash, c)}<div class="split${detail ? ' detail' : ' solo'}">${listHtml}${detail ? detailPanel(detail, c, filter, q) : ''}</div>`;
}

function personRow(f: Family, p: Person, c: Ctx): string {
  const chips: string[] = [];
  const btns: string[] = [];
  if (f.status === 'ended') {
    return `<li class="person"><span class="av" aria-hidden="true">${esc(initials(p.name))}</span><b>${esc(p.name)}</b>
<span class="fee">${esc(feeLabel(p))}</span></li>`;
  }
  if (f.endsAt) chips.push(`<li class="chip info">Baja el ${esc(short(f.endsAt))}</li>`);
  if (p.paper === 'due') {
    chips.push('<li class="chip todo">Hoja por recoger</li>');
    btns.push(actBtn(c, 'paper', f.id, p.slot, 'Hoja recibida', 'alt', 'paper', `de ${p.name}`));
  } else if (p.paper === 'done') chips.push('<li class="chip ok">Hoja recibida</li>');
  if (p.keikogi === 'ready') {
    chips.push('<li class="chip todo">Keikogi por entregar</li>');
    btns.push(actBtn(c, 'keikogi', f.id, p.slot, 'Keikogi entregado', 'alt', 'keikogi', `a ${p.name}`));
  } else if (p.keikogi === 'later') chips.push(`<li class="chip wait">Keikogi ${f.keikogiFrom ? `desde el ${esc(short(f.keikogiFrom))}` : 'más adelante'}</li>`);
  else if (p.keikogi === 'delivered') chips.push('<li class="chip ok">Keikogi entregado</li>');
  if (p.sc === 'pending') {
    chips.push(`<li class="chip todo">Abono por comprobar</li>`);
    btns.push(actBtn(c, 'sc_ok', f.id, p.slot, 'Abono comprobado', 'alt', 'sc', `de ${p.name}`));
    btns.push(askBtn(c, 'sc_no', f.id, p.slot, 'No es válido…', 'warn', '', `el abono de ${p.name}`));
  } else if (p.sc === 'verified') chips.push('<li class="chip ok">Abono comprobado</li>');
  if (p.ageFrom) {
    chips.push(`<li class="chip todo">Cumple 17: nueva cuota</li>`);
    btns.push(askBtn(c, 'age', f.id, p.slot, 'Aplicar cuota de 17 o más…', 'alt', 'age', `a ${p.name}`));
  }
  return `<li class="person"><span class="av" aria-hidden="true">${esc(initials(p.name))}</span><b>${esc(p.name)}</b>
<span class="fee">${esc(feeLabel(p))}${Number.isFinite(p.amount) ? ` · ${esc(m(p.amount))} ${UNIT[f.period]}` : ''}</span>
${chips.length ? `<ul class="chips">${chips.join('')}</ul>` : ''}${btns.length ? `<div class="do">${btns.join('')}</div>` : ''}</li>`;
}

const ACT_TEXT: Record<ActionKind, (who: string) => string> = {
  paper: (w) => `Hoja de ${w} recibida`,
  paper_undo: (w) => `Hoja de ${w}: deshecho, otra vez por recoger`,
  keikogi: (w) => `Keikogi de ${w} entregado`,
  keikogi_undo: (w) => `Keikogi de ${w}: deshecho, otra vez por entregar`,
  sc_ok: (w) => `Abono de ${w} comprobado`,
  sc_undo: (w) => `Abono de ${w}: deshecho, otra vez por comprobar`,
  sc_no: (w) => `Abono de ${w} no válido: pasa a la cuota general`,
  age: (w) => `${w} pasa a la cuota de 17 o más`,
  cancel: () => 'Baja pedida',
  resume: () => 'Baja anulada',
  withdraw: () => 'Desistimiento resuelto: dinero devuelto y cuota terminada',
  withdraw_dismiss: () => 'Desistimiento quitado de la lista',
  leave: () => 'Baja con devolución de los meses no empezados'
};

interface Event { t: number; html: string; cls: string }

export function historyOf(d: Detail): Event[] {
  const f = d.fam;
  const ev: Event[] = [{ t: f.created, cls: 'g', html: `<b>Inscripción en línea</b>${f.invited ? ' · con invitación' : ''}` }];
  for (const inv of d.invoices) {
    const amt = inv.amount_due / 100;
    if (!amt) continue;
    const paidAt = inv.status_transitions?.paid_at;
    if (inv.status === 'paid' && paidAt) {
      ev.push({ t: paidAt * 1000, cls: 'g', html: `${inv.billing_reason === 'subscription_create' ? 'Primer cobro, hasta el primer día 5' : 'Cobrado'} · ${esc(m(amt))}` });
    } else if (inv.status === 'open' && (inv.attempt_count ?? 0) > 0) {
      ev.push({ t: (inv.created ?? 0) * 1000, cls: 'r', html: `<b>Cobro no pasado</b> · ${esc(m(amt))} · ${inv.attempt_count} ${inv.attempt_count === 1 ? 'intento' : 'intentos'}` });
    }
  }
  for (const e of d.log) {
    const p = e.n ? f.people.find((x) => x.slot === e.n) : null;
    const by = e.by === 'email' ? 'desde el correo' : e.by === 'automático' ? 'automático' : (d.names.get(e.by) || e.by.split('@')[0] + '@');
    const text = ACT_TEXT[e.a]?.(p?.first ?? 'una persona') ?? e.a;
    ev.push({ t: e.t, cls: e.a.endsWith('_undo') ? '' : 'g', html: `${esc(text)} <span class="sr">·</span><small> · ${esc(by)}</small>` });
  }
  return ev.sort((a, b) => b.t - a.t).slice(0, 14);
}

function detailPanel(d: Detail, c: Ctx, filter: Filter, q: string): string {
  const f = d.fam;
  const backQs = new URLSearchParams({ ...(filter !== 'todos' ? { f: filter } : {}), ...(q ? { q } : {}) }).toString();
  const contact = [f.holder && `Titular: ${esc(f.holder)}`, f.email && `<a href="mailto:${esc(f.email)}">${esc(f.email)}</a>`,
    f.phone && `<a class="tel" href="tel:${esc(f.phone.replace(/\s/g, ''))}">${esc(f.phone)}</a>`].filter(Boolean).join(' · ');
  const hist = historyOf(d).map((e) => `<li class="${e.cls}"><time datetime="${new Date(e.t).toISOString().slice(0, 10)}">${esc(short(e.t))}</time>${e.html}</li>`).join('');
  const rows: [string, string][] = f.ended ? [
    ['Periodo', `${PERIOD[f.period]} · ${m(f.total)}`],
    ['Desde', short(f.created)], ['Hasta', short(f.ended)],
    ...(f.refunded != null ? [['Devuelto', m(f.refunded)] as [string, string]] : [])
  ] : [
    ['Periodo', `${PERIOD[f.period]} · ${m(f.total)}`],
    [f.endsAt ? 'Termina' : 'Próximo cobro', short(f.endsAt ?? f.next)],
    ...(f.method ? [['Pago', f.method] as [string, string]] : []),
  ];
  const leave = f.ended ? ''
    : f.withdrawalAt && f.withdrawalInWindow ? askBtn(c, 'withdraw', f.id, null, 'Resolver el desistimiento…', 'warn', 'withdrawal')
    : (f.endsAt ? askBtn(c, 'resume', f.id, null, 'Anular la baja…', 'alt', 'door')
      : askBtn(c, 'cancel', f.id, null, `Dar de baja al final del ${periodWordOf(f)}…`, 'warn', 'door'))
      + (f.canLeaveEarly ? askBtn(c, 'leave', f.id, null, 'Baja ahora, devolviendo los meses no empezados…', 'warn', 'money') : '');
  return `<section class="panel" aria-labelledby="fam-h">
<div class="ph"><a class="back" href="/panel/miembros${backQs ? '?' + esc(backQs) : ''}">${icon('left')}Volver a la lista</a>
<h2 id="fam-h">${esc(f.name)}</h2><p>${contact}</p></div>
${banner(f)}<div class="pb"><h3>${f.ended ? 'Quién entrenaba' : 'Quién entrena'}</h3><ul class="people">${f.people.map((p) => personRow(f, p, c)).join('')}</ul>
<h3>Cuota</h3><dl class="kv">${rows.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('')}<dt>Estado</dt><dd>${statusChip(f)}</dd></dl>
<h3>Historia, lo último arriba</h3><ul class="tl">${hist}</ul></div>
<div class="actions">${leave}${stripeLink(stripeUrl(f.id), 'Pagos y recibos en Stripe')}
${f.ended ? '<p>Si vuelve, se inscribe en la web con el mismo correo, y su historia sigue en Stripe.</p>' : '<p>Añadir o quitar personas, o cambiar de periodo, recalcula la cuota de toda la familia: de momento lo hace quien mantiene la web. Pásale el nombre de la familia y lo que piden.</p>'}</div>
</section>`;
}

// The one thing to know about a family before anything else, said at the top.
function banner(f: Family): string {
  const span = (b: { from: number; to: number }) => `de ${short(b.from)} a ${short(b.to)}`;
  const items: [string, string][] = [];
  if (f.ended) {
    items.push(['done', f.endReason === 'withdrawal'
      ? `Esta cuota terminó el ${short(f.ended)} por desistimiento${f.refunded != null ? `: se devolvieron ${m(f.refunded)}` : ''}.`
      : f.endReason === 'impago' ? `Esta cuota terminó el ${short(f.ended)} por impago.`
      : `Esta cuota terminó el ${short(f.ended)}: se dieron de baja${f.refunded != null ? `, y se devolvieron ${m(f.refunded)} de los meses no empezados` : ''}.`]);
  } else if (f.withdrawalAt) {
    items.push(['bad', f.withdrawalInWindow
      ? `Desistimiento recibido el ${short(f.withdrawalAt)}. Resuélvelo antes del ${short(f.withdrawalAt + 14 * 86400000)}: devolver el dinero y terminar la cuota es un solo botón, abajo.`
      : `Pidieron desistir el ${short(f.withdrawalAt)}, pasados los 14 días: es una baja. Dales de baja al final del periodo, abajo, o quítalo de Pendiente.`]);
  } else if (f.endsAt) {
    items.push(['info', `Baja: la cuota termina el ${short(f.endsAt)}. Hasta entonces pueden seguir entrenando, y después no se cobra nada más.`]);
  }
  if (f.status === 'failed') items.push(['bad', `Cobro pendiente${f.failedAmount != null ? ` de ${m(f.failedAmount)}` : ''}. Stripe lo reintenta; si no pasa, habla con la familia.`]);
  if (f.before.length) items.push(['info', `Ya fue miembro ${f.before.map(span).join(' y ')}. No recibe otro keikogi: es uno por persona.`]);
  return items.map(([k, t]) => `<p class="banner ${k}">${icon(k === 'bad' ? 'alert' : 'info')}<span>${esc(t)}</span></p>`).join('');
}

const periodWordOf = (f: Family) => ({ monthly: 'mes', quarterly: 'trimestre', annual: 'año' }[f.period] ?? 'periodo');

// ---------------------------------------------------------------------------
export interface RefundView { lines: { start: number; end: number; paid: number; keep: number; refund: number }[]; total: number; pending: boolean }
export interface LeaveView { applies: boolean; paid: number; start: number; end: number; months: number; started: number; monthly: number; keep: number; refund: number }
export interface Confirm { a: ActionKind; fam: Family; person: Person | null; before?: number; after?: number; totalBefore?: number; totalAfter?: number; refund?: RefundView; leave?: LeaveView }

export function confirmPage(c: Ctx, x: Confirm): string {
  const f = x.fam;
  const p = x.person;
  const unit = UNIT[f.period];
  const sum = x.before != null ? `<div class="sum"><div><span>${esc(p!.first)}</span><b>${esc(m(x.before))} → ${esc(m(x.after!))} ${unit}</b></div>
${f.people.length > 1 ? `<div><span>Total de la familia</span><b>${esc(m(x.totalBefore!))} → ${esc(m(x.totalAfter!))} ${unit}</b></div>` : ''}</div>` : '';
  let title = '', text = '', yes = '', cls = '';
  let extra = '';
  switch (x.a) {
    case 'withdraw': {
      const r = x.refund!;
      title = `¿Resolver el desistimiento de ${f.name}?`;
      if (r.pending) {
        const backHref = c.back === 'm' ? `/panel/miembros?id=${esc(f.id)}` : '/panel/';
        return `<div class="sheet" role="group" aria-labelledby="ask-h"><h1 id="ask-h">Todavía no se puede</h1>
<p>Hay un cobro de esta familia que el banco aún está confirmando (una domiciliación tarda unos días). Hasta que se confirme no se puede devolver, y si terminaras la cuota ahora se cobraría igualmente. Vuelve en unos días: seguirá aquí, y el importe no cambia.</p>
<a class="btn alt big" href="${backHref}">Volver</a></div>`;
      }
      text = `Pidieron desistir el <b>${esc(short(f.withdrawalAt!))}</b>. Pagan los días hasta esa fecha y se les devuelve el resto, ya calculado; aunque lo resuelvas otro día, el importe es el mismo. La cuota termina ahora, no habrá más cobros, y la familia recibe un correo con el importe.`;
      extra = `<div class="sum">${r.lines.map((l) => `<div><span>Cobro del ${esc(short(l.start))}: ${esc(m(l.paid))}, se quedan ${esc(m(l.keep))}</span><b>${esc(m(l.refund))}</b></div>`).join('')}
<div class="tot"><span>Se devuelve</span><b>${esc(m(r.total))}</b></div></div>
<p class="note">Se devuelve por el mismo medio de pago. Con domiciliación bancaria tarda unos días en verse en su cuenta.</p>`;
      yes = r.total > 0 ? `Sí, devolver ${m(r.total)} y terminar` : 'Sí, terminar la cuota'; cls = 'warn';
      break;
    }
    case 'leave': {
      const q = x.leave!;
      const backHref = c.back === 'm' ? `/panel/miembros?id=${esc(f.id)}` : '/panel/';
      if (!q.applies) {
        return `<div class="sheet" role="group" aria-labelledby="ask-h"><h1 id="ask-h">No hay nada que devolver ahora</h1>
<p>No hay un cobro de este ${periodWordOf(f)} ya confirmado que se pueda devolver: o el periodo en curso aún no se ha cobrado, o el cobro se está confirmando. Si quieren irse, dales de baja al final del periodo.</p>
<a class="btn alt big" href="${backHref}">Volver</a></div>`;
      }
      title = `¿Dar de baja a ${f.name} ahora y devolver los meses no empezados?`;
      text = `Hazlo solo si la familia lo ha pedido. Se calcula como si hubieran pagado mes a mes: de lo pagado por este ${periodWordOf(f)} se queda la cuota mensual de cada mes ya empezado. La cuota termina ahora, no habrá más cobros, y la familia recibe un correo con el importe.`;
      extra = `<div class="sum"><div><span>Pagado por el ${periodWordOf(f)}, del ${esc(short(q.start))} al ${esc(short(q.end - 86400000))}</span><b>${esc(m(q.paid))}</b></div>
<div><span>${q.started} ${q.started === 1 ? 'mes empezado' : 'meses empezados'} × ${esc(m(q.monthly))} al mes</span><b>− ${esc(m(q.keep))}</b></div>
<div class="tot"><span>Se devuelve</span><b>${esc(m(q.refund))}</b></div></div>
<p class="note">Se devuelve por el mismo medio de pago. El keikogi de regalo no se descuenta.</p>`;
      yes = q.refund > 0 ? `Sí, dar de baja y devolver ${m(q.refund)}` : 'Sí, dar de baja ahora'; cls = 'warn';
      break;
    }
    case 'withdraw_dismiss':
      title = '¿Quitar el desistimiento de Pendiente?';
      text = 'Hazlo solo si la familia ha dicho que fue un error, o si ya lo habéis resuelto de otra forma. La cuota sigue como estaba y no se devuelve nada.';
      yes = 'Sí, quitarlo';
      break;
    case 'age':
      title = `¿Pasar a ${p!.first} a la cuota de 17 o más?`;
      text = `Desde el próximo cobro, el <b>${esc(short(f.next))}</b>. La familia recibe un correo que se lo explica, y se borra la fecha de nacimiento, que ya no hace falta.`;
      yes = 'Sí, aplicar y avisar';
      break;
    case 'sc_no':
      title = `¿El abono de ${p!.first} no es válido?`;
      text = `${esc(p!.first)} pasa a la cuota general, que vale en todos los espacios, desde el próximo cobro, el <b>${esc(short(f.next))}</b>. La familia recibe un correo con la cuota nueva.`;
      yes = 'Sí, pasar a la cuota general'; cls = 'warn';
      break;
    case 'cancel':
      title = `¿Dar de baja a ${f.name}?`;
      text = `Hazlo solo si la familia lo ha pedido. La cuota termina el <b>${esc(short(f.next))}</b>, al final del ${periodWordOf(f)} ya pagado: hasta entonces pueden seguir entrenando, y no se cobra nada más. La familia recibe un correo de confirmación.`;
      yes = 'Sí, dar de baja'; cls = 'warn';
      break;
    case 'resume':
      title = `¿Anular la baja de ${f.name}?`;
      text = `La cuota sigue, y el <b>${esc(short(f.next))}</b> se cobran ${esc(m(f.total))} como siempre.`;
      yes = 'Sí, la cuota sigue';
      break;
    default:
      return '';
  }
  const backHref = c.back === 'm' ? `/panel/miembros?id=${esc(f.id)}` : '/panel/';
  return `<div class="sheet" role="group" aria-labelledby="ask-h"><h1 id="ask-h">${esc(title)}</h1><p>${text}</p>${sum}${extra}
${actBtn(c, x.a, f.id, p ? p.slot : null, yes, `big ${cls}`, '')}
<a class="btn alt big" href="${backHref}">No, volver</a></div>`;
}

// ---------------------------------------------------------------------------
export function loginPage(step: 'email' | 'code', opts: { email?: string; error?: string } = {}): string {
  if (step === 'email') {
    return `<div class="login"><div class="card"><h1>Entrar en el panel de cuotas</h1>
<p>Escribe tu correo. Te enviamos un código de 6 cifras; no hay contraseña.</p>
${opts.error ? `<p class="err" role="alert">${esc(opts.error)}</p>` : ''}
<form method="post" action="/panel/entrar"><label for="email">Correo</label>
<input id="email" name="email" type="email" autocomplete="email" required value="${esc(opts.email ?? '')}">
<button class="btn big" type="submit">Enviar código</button></form></div>
<p class="note">Solo pueden entrar los correos de la asociación que están autorizados.</p></div>`;
  }
  return `<div class="login"><div class="card"><h1>Escribe el código</h1>
<p>Si <b>${esc(opts.email ?? '')}</b> está autorizado, acaba de recibir un correo con un código de 6 cifras. Caduca en 10 minutos.</p>
${opts.error ? `<p class="err" role="alert">${esc(opts.error)}</p>` : ''}
<form method="post" action="/panel/codigo"><input type="hidden" name="email" value="${esc(opts.email ?? '')}">
<label for="code">Código</label><input id="code" class="code" name="code" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9 ]{6,7}" maxlength="7" required autofocus>
<button class="btn big" type="submit">Entrar</button></form>
<a class="again" href="/panel/entrar">No me ha llegado: volver a empezar</a></div>
<p class="note">Mira también en la carpeta de spam. Puedes pedir un código nuevo pasado un minuto.</p></div>`;
}

export function messagePage(title: string, text: string, link = '/panel/'): string {
  return `<div class="sheet"><h1>${esc(title)}</h1><p>${esc(text)}</p><a class="btn alt big" href="${link}">Volver al panel</a></div>`;
}

// ---------------------------------------------------------------------------
const FAQ: [string, string][] = [
  ['¿Qué significa cada grupo de «Pendiente»?',
    `<p><b>Hojas de inscripción:</b> cada persona que se inscribe en línea tiene que entregar además la hoja en papel, firmada. Cuando la tengas, pulsa <b>Recibida</b>.</p>
<p><b>Keikogi:</b> quien se inscribe por trimestre o por año tiene keikogi, una vez cobrado el primer periodo completo y pasados los 14 días para desistir. La familia ya ha recibido un correo que le pide las tallas. Cuando se lo des, pulsa <b>Entregado</b>.</p>
<p><b>Abonos municipales:</b> quien paga la cuota con abono del polideportivo tiene que enseñar el carné. Si es válido, <b>Comprobado</b>; si no, <b>No es válido</b>, y pasa a la cuota general.</p>
<p><b>Cumplen 17:</b> aparece antes del cobro en que cambia la cuota. <b>Aplicar y avisar</b> la cambia y avisa a la familia.</p>
<p><b>Cobros que no han pasado:</b> solo para que lo sepas. Stripe lo vuelve a intentar.</p>`],
  ['Me he equivocado al pulsar un botón',
    `<p>Justo después aparece un aviso arriba con <b>Deshacer</b>. Si ya no está, no pasa nada grave: avisa a quien mantiene la web y lo corrige.</p>
<p>Los botones que cambian lo que paga una familia (abono no válido, 17 o más, baja) siempre piden confirmación antes, con los importes.</p>`],
  ['Una familia quiere darse de baja',
    `<p>Pueden hacerlo ellos mismos desde <b>Mi cuota</b>; el enlace está en todos sus correos. Si te lo piden a ti, abre la familia en <b>Miembros</b> y pulsa <b>Dar de baja al final del periodo</b>. Siguen entrenando hasta esa fecha y no se cobra nada más.</p>
<p>Si tienen cuota <b>trimestral o anual</b> y piden que les devolvamos los meses que no han empezado, pulsa en cambio <b>Baja ahora, devolviendo los meses no empezados</b>. El panel lo calcula como si hubieran pagado mes a mes, te enseña el importe antes de confirmar, devuelve el dinero y les escribe. No hace falta que den explicaciones.</p>
<p>Si quieren <b>desistir</b> dentro de los 14 días y recuperar el dinero, es otra cosa: que usen el formulario de desistimiento de la web.</p>`],
  ['Ha llegado un desistimiento',
    `<p>Aparece el primero en <b>Pendiente</b>. Pulsa <b>Resolver…</b>: verás lo que se devuelve, ya calculado. Al confirmar se devuelve el dinero por el mismo medio de pago, la cuota termina y la familia recibe un correo con el importe. No hace falta entrar en Stripe.</p>
<p>El importe se calcula a la hora en que lo pidieron, así que no cambia aunque lo resuelvas otro día. Eso sí, hay que hacerlo antes de 14 días desde la solicitud.</p>
<p>Si llega pasados los 14 días, ya no es un desistimiento sino una baja: el panel te lo dice y te ofrece darles de baja al final del periodo.</p>`],
  ['Alguien que se dio de baja quiere volver',
    `<p>Que se inscriba otra vez en la web, con el mismo correo. Su historia sigue junta, y en su ficha verás «Ya fue miembro». No recibe otro keikogi si ya tuvo uno. Las cuotas que terminaron están en <b>Miembros → Antiguos miembros</b>.</p>`],
  ['Alguien dice que ha pagado dos veces, o pide una devolución',
    `<p>Los pagos y las devoluciones se miran en Stripe: abre la familia y pulsa <b>Pagos y recibos en Stripe</b>. Si no lo ves claro, no toques nada y pregunta.</p>`],
  ['Quieren añadir o quitar a alguien, o cambiar a trimestral o anual',
    `<p>Hay que recalcular la cuota de toda la familia, y de momento lo hace quien mantiene la web. Pásale el nombre de la familia y lo que piden.</p>`],
  ['Un cobro no ha pasado',
    `<p>Stripe lo reintenta varias veces durante unos días, y la familia recibe un correo. Si al final no pasa, la cuota no se cancela sola: queda pendiente de pago. Si ves a la familia en el dojo, coméntaselo.</p>`],
  ['¿Qué correos me llegan?',
    `<p>Uno por cada inscripción, otro cuando hay keikogi listos, uno por cada cobro fallido o baja, y un resumen el día 20 de cada mes con lo que siga pendiente. Todo lo que dicen está también aquí.</p>`],
  ['¿Quién puede entrar en el panel?',
    `<p>Solo los correos autorizados de la asociación, con un código que llega por correo. Si usas un ordenador compartido, pulsa <b>Salir</b> al terminar.</p>`]
];

export function helpPage(): string {
  return `<h1 class="page">Ayuda</h1><div class="faq">${FAQ.map(([q, a]) => `<details><summary>${esc(q)}</summary><div>${a}</div></details>`).join('')}</div>`;
}

export const APP_JS = `(function(){
var q=document.getElementById('q');if(!q)return;
var cards=[].slice.call(document.querySelectorAll('.fam[data-search]'));
var out=document.getElementById('shown');var none=document.querySelector('.none');
function fold(s){return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();}
q.addEventListener('input',function(){var v=fold(q.value.trim());var n=0;
cards.forEach(function(c){var ok=!v||c.getAttribute('data-search').indexOf(v)>-1;c.hidden=!ok;if(ok)n++;});
if(out)out.textContent=n+(n===1?' cuota':' cuotas');if(none)none.hidden=n>0;});
})();`;
