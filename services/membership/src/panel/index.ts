// /panel/ — the dojo's back office (approved in docs/mockups/panel-cuotas.html,
// 15 October 2026). For the volunteer who looks after the memberships: what is
// to do, who our members are, and one family in detail. It replaces editing
// Stripe metadata by hand; money itself stays in Stripe, one button away.
//
//   GET  /panel/              Pendiente: the to-do list
//   GET  /panel/miembros      the members, search, filters; ?id= opens one
//   GET  /panel/ayuda         questions and answers
//   GET  /panel/confirmar     the confirmation for a change that costs money
//   POST /panel/accion        do it, then back to where it was pressed
//   GET/POST /panel/entrar    the email form; POST /panel/codigo the code
//   POST /panel/salir         sign out
//
// Nothing is stored here but sessions, login codes and a short history of who
// pressed what. The members are read from Stripe on every page.
import type Stripe from 'stripe';
import type { Env } from '../env.ts';
import { isLive } from '../env.ts';
import { log, readBody } from '../http.ts';
import { members as metaMembers } from '../meta.ts';
import { ACTIONS, ASKS_FIRST, WHOLE, apply, history, preview, type ActionKind } from '../actions.ts';
import { total } from '../household.ts';
import { stripe, subscription } from '../stripe.ts';
import { checkCode, endSession, sameOrigin, sendCode, session, startSession, users, type Session } from './auth.ts';
import { family, isCurrent, isFormer, linkReturning, tasks, type Family } from './model.ts';
import { refundFor } from '../refund.ts';
import { pendingPayment, withdrawalAt } from '../withdraw.ts';
import { demoLeave, demoRefund } from './demo.ts';
import { leaveQuote } from '../leave.ts';
import { invoicePeriod, openInvoices } from '../cash.ts';
import { APP_JS, FILTERS, confirmPage, helpPage, loginPage, membersPage, messagePage, pendingPage, setStripeBase, shell, type Filter, type Flash } from './views.ts';
import { demoSubscriptions } from './demo.ts';

const HEADERS = {
  'x-content-type-options': 'nosniff',
  // same-origin, not no-referrer: see sameOrigin() in auth.ts.
  'referrer-policy': 'same-origin',
  'strict-transport-security': 'max-age=31536000; includeSubDomains',
  'cache-control': 'no-store',
  'x-robots-tag': 'noindex, nofollow',
  'x-frame-options': 'DENY',
  'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'; script-src 'self'; img-src 'self' data:; form-action 'self'; frame-ancestors 'none'; base-uri 'none'"
};

const html = (body: string, status = 200, extra: Record<string, string> = {}) =>
  new Response(body, { status, headers: { 'content-type': 'text/html; charset=utf-8', ...HEADERS, ...extra } });
// What a refused POST shows: never a bare "Forbidden" to a volunteer.
const refused = (test: boolean) => html(shell({ title: 'Aviso', tab: null, user: null, test,
  body: messagePage('No se ha podido hacer', 'La página había caducado, o el envío no venía del panel. Vuelve a empezar desde el panel.') }), 403);
const go = (to: string, extra: Record<string, string> = {}) =>
  new Response(null, { status: 303, headers: { location: to, ...HEADERS, ...extra } });

// Without a Stripe key on a local `wrangler dev`, the panel shows invented
// families, so it can be looked at and checked without an account.
const demo = (env: Env) => env.ENVIRONMENT === 'dev' && !env.STRIPE_SECRET_KEY;

async function load(env: Env): Promise<Stripe.Subscription[]> {
  if (demo(env)) return demoSubscriptions(Date.now());
  const st = stripe(env);
  const out: Stripe.Subscription[] = [];
  for await (const s of st.subscriptions.list({ status: 'all', limit: 100, expand: ['data.customer', 'data.default_payment_method', 'data.latest_invoice'] })) {
    if (isCurrent(s) || isFormer(s)) out.push(s);
  }
  return out;
}

async function one(env: Env, id: string): Promise<Stripe.Subscription | null> {
  if (!/^sub_[A-Za-z0-9]{6,64}$/.test(id)) return null;
  if (demo(env)) return demoSubscriptions(Date.now()).find((s) => s.id === id) ?? null;
  try {
    const s = await subscription(stripe(env), id);
    return s.metadata?.signup_id ? s : null;
  } catch { return null; }
}

function flashFrom(u: URL, fams: Family[]): Flash | null {
  if (u.searchParams.get('error')) return { a: 'error', error: true };
  const a = u.searchParams.get('hecho');
  if (!a) return null;
  const fam = fams.find((f) => f.id === (u.searchParams.get('s') ?? u.searchParams.get('id')));
  const n = Number(u.searchParams.get('n'));
  return { a, fam, person: fam?.people.find((p) => p.slot === n) ?? null };
}

export async function panel(req: Request, env: Env): Promise<Response> {
  const u = new URL(req.url);
  const path = u.pathname.replace(/\/+$/, '') || '/panel';
  setStripeBase(isLive(env));
  const test = !isLive(env);

  if (path === '/panel/app.js') {
    return new Response(APP_JS, { headers: { 'content-type': 'text/javascript; charset=utf-8', ...HEADERS } });
  }

  // ---- signing in ---------------------------------------------------------
  if (path === '/panel/entrar') {
    if (req.method === 'POST') {
      if (!sameOrigin(req)) return refused(test);
      const body = await readBody(req);
      const email = (body?.email ?? '').trim();
      if (!email.includes('@')) return html(shell({ title: 'Entrar', tab: null, user: null, test, body: loginPage('email', { email, error: 'Escribe un correo completo.' }) }), 422);
      try { await sendCode(req, env, email); } catch (e) { log({ route: 'panel/entrar', outcome: 'send_error', error: (e as Error).message?.slice(0, 200) }); }
      return html(shell({ title: 'Código', tab: null, user: null, test, body: loginPage('code', { email }) }));
    }
    if (await session(req, env)) return go('/panel/');
    return html(shell({ title: 'Entrar', tab: null, user: null, test, body: loginPage('email') }));
  }
  if (path === '/panel/codigo' && req.method === 'POST') {
    if (!sameOrigin(req)) return refused(test);
    const body = await readBody(req);
    const email = body?.email ?? '';
    if (await checkCode(env, email, body?.code ?? '')) {
      log({ route: 'panel/codigo', outcome: 'signed_in' });
      return go('/panel/', { 'set-cookie': await startSession(env, email.trim().toLowerCase()) });
    }
    log({ route: 'panel/codigo', outcome: 'refused' });
    return html(shell({ title: 'Código', tab: null, user: null, test,
      body: loginPage('code', { email, error: 'Ese código no es correcto o ha caducado. Revísalo, o vuelve a empezar para recibir otro.' }) }), 401);
  }

  const user = await session(req, env);
  if (path === '/panel/salir' && req.method === 'POST') {
    if (!sameOrigin(req)) return refused(test);
    return go('/panel/entrar', { 'set-cookie': await endSession(env, user) });
  }
  if (!user) return go('/panel/entrar');

  // ---- doing something ----------------------------------------------------
  if (path === '/panel/accion' && req.method === 'POST') return act(req, env, user);

  // ---- pages --------------------------------------------------------------
  let subs: Stripe.Subscription[];
  try {
    subs = await load(env);
  } catch (e) {
    log({ route: path, outcome: 'stripe_error', error: (e as Error).message?.slice(0, 200) });
    return html(shell({ title: 'Aviso', tab: null, user, test,
      body: messagePage('Stripe no contesta', 'No se han podido leer las cuotas. Vuelve a cargar la página en un momento.') }), 502);
  }
  const fams = subs.filter(isCurrent).map((s) => family(s));
  const former = subs.filter(isFormer).map((s) => family(s));
  linkReturning(fams, former);
  const all = [...fams, ...former];
  const list = tasks(fams);
  const counts = { pending: list.length, members: fams.length };
  const page = (title: string, tab: 'p' | 'm' | 'h' | null, body: string, script = false) =>
    html(shell({ title, tab, user, test, counts, body, script }));

  if (path === '/panel') return page('Pendiente', 'p', pendingPage(user, fams, list, Date.now(), flashFrom(u, all)));
  if (path === '/panel/ayuda') return page('Ayuda', 'h', helpPage());
  if (path === '/panel/miembros') {
    const f = (u.searchParams.get('f') ?? 'todos') as Filter;
    const filter: Filter = FILTERS.some(([k]) => k === f) ? f : 'todos';
    const q = (u.searchParams.get('q') ?? '').slice(0, 100);
    const id = u.searchParams.get('id');
    let detail = null;
    const fam = id ? all.find((x) => x.id === id) : null;
    if (fam) {
      const invoices = demo(env) ? [] : (await stripe(env).invoices.list({ subscription: fam.id, limit: 24 }).catch(() => ({ data: [] }))).data;
      detail = { fam, log: await history(env, fam.id), invoices, names: users(env) };
    }
    // A former membership opened from a link lists among the former ones.
    const shownFilter: Filter = fam?.ended && filter === 'todos' ? 'antiguos' : filter;
    return page(fam ? fam.name : 'Miembros', 'm', membersPage(user, fams, former, list, q, shownFilter, detail, flashFrom(u, all)), true);
  }
  if (path === '/panel/confirmar') {
    const a = u.searchParams.get('a') as ActionKind;
    const back = u.searchParams.get('back') === 'm' ? 'm' : 'p';
    const fam = fams.find((x) => x.id === u.searchParams.get('s'));
    if (!ASKS_FIRST.includes(a) || !fam) return page('Aviso', null, messagePage('No encontrado', 'Esa cuota ya no está, o el enlace no es correcto.'));
    const person = fam.people.find((p) => p.slot === Number(u.searchParams.get('n'))) ?? null;
    if ((a === 'age' || a === 'sc_no') && !person) return page('Aviso', null, messagePage('No encontrado', 'Esa persona ya no está en la cuota.'));
    let amounts = {};
    if (a === 'withdraw' || a === 'withdraw_dismiss') {
      const sub = subs.find((s) => s.id === fam.id)!;
      const at = withdrawalAt(sub);
      if (at == null || sub.metadata.withdrawal_done) return page('Aviso', null, messagePage('Nada que resolver', 'Esta cuota no tiene ningún desistimiento pendiente.'));
      if (a === 'withdraw') {
        const r = demo(env) ? demoRefund(sub, at) : await refundFor(stripe(env), sub.id, at);
        amounts = { refund: { ...r, pending: pendingPayment(sub) } };
      }
    }
    if (a === 'cash_paid') {
      const sub = subs.find((s) => s.id === fam.id)!;
      // What Cobrado will mark: every open invoice of the membership. The
      // demo has only the one its family carries.
      const open = demo(env)
        ? (fam.cashDue ? [sub.latest_invoice as Stripe.Invoice] : [])
        : await openInvoices(stripe(env), sub.id);
      const lines = open.map((i) => ({ number: i.number ?? null, amount: i.amount_remaining / 100, ...invoicePeriod(i), first: i.billing_reason === 'subscription_create' }));
      amounts = { cash: { lines, total: Math.round(lines.reduce((s, l) => s + l.amount, 0) * 100) / 100 } };
    }
    if (a === 'leave') {
      const sub = subs.find((s) => s.id === fam.id)!;
      amounts = { leave: demo(env) ? demoLeave(sub, Date.now()) : await leaveQuote(stripe(env), sub) };
    }
    if (person && (a === 'age' || a === 'sc_no')) {
      const sub = subs.find((s) => s.id === fam.id)!;
      const who = metaMembers(sub.metadata).find((x) => x.slot === person.slot)!;
      const { before, after } = preview(sub, who, a);
      amounts = { before: before.find((x) => x.slot === who.slot)!.amount, after: after.find((x) => x.slot === who.slot)!.amount,
        totalBefore: total(before), totalAfter: total(after) };
    }
    return page('Confirmar', null, confirmPage({ csrf: user.csrf, back }, { a, fam, person, ...amounts }));
  }
  return page('No encontrado', null, messagePage('No encontrado', 'Esta página del panel no existe.'));
}

async function act(req: Request, env: Env, user: Session): Promise<Response> {
  const test = !isLive(env);
  const body = await readBody(req);
  if (!sameOrigin(req) || !body || body.csrf !== user.csrf) return refused(test);
  const a = body.a as ActionKind;
  const back = body.back === 'm' ? 'm' : 'p';
  const id = body.s ?? '';
  const where = (extra: Record<string, string>) => {
    const q = new URLSearchParams(back === 'm' ? { id, ...extra } : { ...extra, s: id });
    return go(back === 'm' ? `/panel/miembros?${q}` : `/panel/?${q}`);
  };
  if (!ACTIONS.includes(a)) return where({ error: '1' });
  if (demo(env)) return where({ hecho: a, n: body.n ?? '' });
  const sub = await one(env, id);
  if (!sub) return where({ error: '1' });
  const who = body.n ? metaMembers(sub.metadata).find((x) => x.slot === Number(body.n)) ?? null : null;
  if (!WHOLE.includes(a) && !who) return where({ error: '1' });
  try {
    await apply(env, stripe(env), sub, who, a, user.email);
    log({ route: 'panel/accion', action: a, sub: sub.id, outcome: 'done' });
    return where({ hecho: a, n: who ? String(who.slot) : '' });
  } catch (e) {
    log({ route: 'panel/accion', action: a, sub: sub.id, outcome: 'error', error: (e as Error).message?.slice(0, 200) });
    return where({ error: '1' });
  }
}
