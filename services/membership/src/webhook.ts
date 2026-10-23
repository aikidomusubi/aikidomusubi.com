// POST /stripe/webhook — Stripe tells us what happened (spec 8.1).
//
// Stripe is the record; this only reacts: emails to the member and the dojo,
// and a few metadata flags. Every event is handled at most once: its id is
// kept in KV for 30 days (no personal data) and a repeat is acknowledged and
// ignored.
import type Stripe from 'stripe';
import type { Env } from './env.ts';
import { flag } from './env.ts';
import { CATALOG, esc, isoDay, money, periodName, venueName, date } from './data.ts';
import { log } from './http.ts';
import { members as metaMembers, slots } from './meta.ts';
import { itemAmounts, priced, total, personLabel } from './household.ts';
import { Pricing, type PeriodId } from './pricing.ts';
import { cryptoProvider, customerOf, method, periodEnd, stripe, subId, subscription } from './stripe.ts';
import { markUsed } from './invite.ts';
import { ctxFor } from './context.ts';
import { actionUrl, notifyKeikogiReady } from './actions.ts';
import * as member from './email/member.ts';
import { isCash, payByMs } from './cash.ts';
import { cardGiven } from './cardlink.ts';
import { admin, todo, dashboard, B, type Todo } from './email/admin.ts';

export async function webhook(req: Request, env: Env): Promise<Response> {
  const sig = req.headers.get('stripe-signature');
  const raw = await req.text();
  if (!sig) return new Response('missing signature', { status: 400 });
  let event: Stripe.Event;
  const st = stripe(env);
  try {
    event = await st.webhooks.constructEventAsync(raw, sig, env.STRIPE_WEBHOOK_SECRET, undefined, cryptoProvider);
  } catch {
    log({ route: 'webhook', outcome: 'bad_signature' });
    return new Response('bad signature', { status: 400 });
  }

  const seenKey = `evt:${event.id}`;
  if (await env.KV.get(seenKey)) return new Response('ok (repeat)', { status: 200 });

  try {
    await handle(env, st, event);
    await env.KV.put(seenKey, '1', { expirationTtl: 30 * 86400 });
    log({ route: 'webhook', event: event.type, id: event.id, outcome: 'handled' });
    return new Response('ok', { status: 200 });
  } catch (e) {
    // Not marked as seen: Stripe retries, and the next attempt runs again.
    log({ route: 'webhook', event: event.type, id: event.id, outcome: 'error', error: (e as Error).message?.slice(0, 200) });
    return new Response('error', { status: 500 });
  }
}

export async function handle(env: Env, st: Stripe, event: Stripe.Event) {
  switch (event.type) {
    case 'checkout.session.completed':
      return completed(env, st, event.data.object as Stripe.Checkout.Session);
    case 'checkout.session.async_payment_failed':
      return asyncFailed(env, st, event.data.object as Stripe.Checkout.Session);
    case 'invoice.paid':
      return paid(env, st, event.data.object as Stripe.Invoice);
    case 'invoice.payment_failed':
      return failed(env, st, event.data.object as Stripe.Invoice);
    case 'invoice.upcoming':
      return upcoming(env, st, event.data.object as Stripe.Invoice);
    case 'customer.subscription.updated':
      return updated(env, event.data.object as Stripe.Subscription,
        (event.data as { previous_attributes?: Partial<Stripe.Subscription> }).previous_attributes ?? {});
    case 'customer.subscription.deleted':
      return deleted(env, st, event.data.object as Stripe.Subscription);
    default:
      return;
  }
}

const invoiceSub = (inv: Stripe.Invoice) => subId(inv.parent?.subscription_details?.subscription as string | Stripe.Subscription | null);
const ours = (sub: Stripe.Subscription) => Boolean(sub.metadata?.signup_id);

// ---------------------------------------------------------------------------
async function completed(env: Env, st: Stripe, session: Stripe.Checkout.Session) {
  // A cash family giving a card or account to move off cash (src/cardlink.ts).
  if (session.mode === 'setup') return cardGiven(env, st, session);
  if (session.mode !== 'subscription') return;          // seminar payments and the like
  const id = subId(session.subscription as string | Stripe.Subscription | null);
  if (!id) return;
  await welcome(env, st, id, session.payment_status === 'unpaid');
}

// The confirmation to the family and the notice to the dojo. After Checkout
// for a card or direct debit; straight from /checkout for cash, which has no
// Checkout and so no checkout.session.completed.
export async function welcome(env: Env, st: Stripe, id: string, processing: boolean) {
  const sub = await st.subscriptions.retrieve(id, { expand: ['default_payment_method', 'customer', 'latest_invoice'] });
  if (!ours(sub)) return;
  const meta = sub.metadata;
  const cash = isCash(sub);
  if (meta.invite_id) await markUsed(env, meta.invite_id, sub.id);

  const people = priced(meta, itemAmounts(sub));
  const period = meta.period as PeriodId;
  const anchor = sub.billing_cycle_anchor * 1000;
  const signupMs = sub.created * 1000;
  const inv = sub.latest_invoice && typeof sub.latest_invoice !== 'string' ? sub.latest_invoice : null;
  const todayAmount = inv ? inv.amount_due / 100 : null;
  const now = Date.now();
  const under14 = metaMembers(meta).some((m) => {
    if (!m.bym) return false;
    const [y, mo] = m.bym.split('-').map(Number);
    return Pricing.minAge(y, mo, now) < 14;
  });
  const keikogi = slots(meta.keikogi_due).length;
  const scVenues = [...new Set(metaMembers(meta).filter((m) => m.rate === 'sc' && m.venue).map((m) => m.venue!))];

  const ctx = ctxFor(env, sub);
  if (ctx) {
    await member.confirmation(ctx, {
      people, period, signupMs, anchorMs: anchor, todayAmount, method: method(sub), processing,
      under14, keikogi, scVenues, withdrawBy: Date.parse(meta.withdraw_by + 'T12:00:00Z'), termsVersion: meta.terms_version,
      ...(cash && inv ? { cashFirstBy: payByMs(inv) } : {})
    });
  }

  // The dojo's notice: who, what, when, and what is still to do by hand.
  const items: Todo[] = [];
  const paper = slots(meta.paper_due);
  for (const m of metaMembers(meta).filter((x) => paper.includes(`m${x.slot}`))) {
    items.push({ title: `Recoger la hoja de inscripción de ${m.name}`,
      sub: m.cat === 'youth' ? 'Firmada por madre, padre o tutor, con la autorización de imagen.' : 'Firmada, con la autorización de uso de imagen.',
      action: { label: 'Recibida', href: await actionUrl(env, 'paper', sub.id, m.slot) } });
  }
  for (const m of metaMembers(meta).filter((x) => x.sc === 'pending')) {
    items.push({ title: `Comprobar el abono de ${m.name}`, sub: venueName(m.venue, 'es'),
      action: { label: 'Comprobado', href: await actionUrl(env, 'sc_ok', sub.id, m.slot) } });
    items.push({ title: `Si el abono de ${m.name} no es válido`, sub: 'Pasa a la cuota general desde el próximo cobro y se avisa a la familia.',
      action: { label: 'No válido', href: await actionUrl(env, 'sc_no', sub.id, m.slot) } });
  }
  if (keikogi) {
    items.push({ title: `${keikogi} keikogi`, sub: `Cuando se cobre la primera cuota completa (${date(anchor, 'es')}) y pasen los 14 días. Ese día llega otro aviso con los botones.` });
  }
  if (meta.invite_id) {
    items.push({ title: `Remesa del banco: no incluyas a ${customerOf(sub)?.name ?? 'esta familia'} desde ${date(anchor, 'es').replace(/^\d+ de /, '')}`,
      sub: `Su primer cobro por Stripe es el ${date(anchor, 'es')}. Si pasas la remesa de ese mes, pagaría dos veces.` });
  }
  const rows: [string, string][] = people.map((p) => [personLabel(p, 'es', CATALOG.family * (CATALOG.periods[period]?.months ?? 1)), money(p.amount, 'es')]);
  rows.push([`Total ${periodName(period, 'es')}`, money(total(people), 'es')]);
  await admin(env,
    `Nueva inscripción${cash ? ' en efectivo' : ''} · ${people.length} ${people.length === 1 ? 'persona' : 'personas'} · ${periodName(period, 'es')} · primer cobro ${date(anchor, 'es', false)}`,
    'Inscripción', [
      B.h('Nueva inscripción'),
      B.p(cash
        ? `${date(signupMs, 'es')}. <b>En efectivo.</b>${meta.invite_id ? ' Con invitación.' : ''} Primer pago en el dojo: ${todayAmount != null ? money(todayAmount, 'es') : '—'}${inv ? `, antes del ${date(payByMs(inv), 'es')}` : ''}. Cuando lo traigan, márcalo como cobrado en el panel.`
        : `${date(signupMs, 'es')}. ${esc(method(sub)?.type === 'sepa_debit' ? 'Domiciliación SEPA' : 'Tarjeta')}${processing ? ', pendiente de confirmar' : ''}.${meta.invite_id ? ' Con invitación.' : ''} Hoy: ${todayAmount != null ? money(todayAmount, 'es') : '—'}.`),
      B.table(rows, true),
      B.h4('Pendiente'),
      ...(items.length ? [todo(items)] : [B.p('Nada por hacer a mano.')]),
      B.button('Abrir en el panel', `${env.API_ORIGIN}/panel/miembros?id=${sub.id}`),
      B.small(`O <a href="${dashboard(env, `subscriptions/${sub.id}`)}">en Stripe</a>, para los pagos.`)
    ], 'signup');
}

async function asyncFailed(env: Env, st: Stripe, session: Stripe.Checkout.Session) {
  const id = subId(session.subscription as string | Stripe.Subscription | null);
  if (!id) return;
  const sub = await subscription(st, id);
  if (!ours(sub)) return;
  const people = priced(sub.metadata, itemAmounts(sub));
  const ctx = ctxFor(env, sub);
  if (ctx) await member.paymentFailed(ctx, { amount: (session.amount_total ?? 0) / 100, dueMs: sub.created * 1000, method: method(sub) });
  await admin(env, `Primer cargo SEPA devuelto: ${customerOf(sub)?.name ?? sub.id}`, 'Cobro', [
    B.h('El primer cargo por domiciliación no ha pasado'),
    B.p(`${esc(people.map((p) => p.name).join(', '))}. La familia ya tiene un correo con los pasos. Mira en Stripe si hay que hablar con ella.`),
    B.button('Abrir en Stripe', dashboard(env, `subscriptions/${sub.id}`))
  ], 'async_failed');
}

// ---------------------------------------------------------------------------
// invoice.paid: the first FULL period is the one billed on the anchor, with
// billing_reason "subscription_cycle". That date opens the keikogi (once the
// 14 days are also over) and switches renewal notices on.
async function paid(env: Env, st: Stripe, inv: Stripe.Invoice) {
  if (inv.billing_reason !== 'subscription_cycle') return;
  const id = invoiceSub(inv);
  if (!id) return;
  const sub = await subscription(st, id);
  if (!ours(sub) || sub.metadata.first_full) return;
  await st.subscriptions.update(sub.id, { metadata: { first_full: isoDay(Date.now()) } });
  if (sub.metadata.keikogi === 'due') {
    if (isoDay(Date.now()) > sub.metadata.withdraw_by) await notifyKeikogiReady(env, st, sub);
    else await st.subscriptions.update(sub.id, { metadata: { keikogi: 'paid' } });
  }
}

async function failed(env: Env, st: Stripe, inv: Stripe.Invoice) {
  const id = invoiceSub(inv);
  if (!id) return;
  const sub = await subscription(st, id);
  if (!ours(sub)) return;
  const m = method(sub);
  // Stripe emails card failures itself. For SEPA it may not, and our email is
  // sent only then, so a member never receives two (spec 8.1, decided).
  if (m?.type === 'sepa_debit' && flag(env.MEMBER_FAILED_EMAIL_SEPA)) {
    const ctx = ctxFor(env, sub);
    if (ctx) await member.paymentFailed(ctx, { amount: inv.amount_due / 100, dueMs: (inv.created ?? 0) * 1000, method: m });
  }
  await admin(env, `Cobro fallido: ${customerOf(sub)?.name ?? sub.id} · ${money(inv.amount_due / 100, 'es')}`, 'Cobro', [
    B.h('Un cobro no ha pasado'),
    B.p(`${esc(customerOf(sub)?.name ?? '')}: ${money(inv.amount_due / 100, 'es')}, intento ${inv.attempt_count ?? 1}. Stripe lo reintenta; si el último falla, la cuota queda pendiente de pago y no se cancela sola.`),
    B.button('Abrir en Stripe', dashboard(env, `invoices/${inv.id}`))
  ], 'payment_failed');
}

// invoice.upcoming, 15 days before a renewal (Ley 10/2025). Skipped for the
// first full charge, which the confirmation email already announced (decided
// 14 October 2026, fix 3), and for monthly plans if the flag says so.
async function upcoming(env: Env, st: Stripe, inv: Stripe.Invoice) {
  const id = invoiceSub(inv);
  if (!id) return;
  const sub = await subscription(st, id);
  if (!ours(sub) || sub.status === 'canceled') return;
  if (!sub.metadata.first_full) return;
  if (sub.cancel_at_period_end || sub.cancel_at) return;
  const period = sub.metadata.period as PeriodId;
  if (period === 'monthly' && !flag(env.RENEWAL_NOTICE_MONTHLY)) return;
  const ctx = ctxFor(env, sub);
  if (!ctx) return;
  const charge = periodEnd(sub);
  const months = CATALOG.periods[period]?.months ?? 1;
  await member.renewal(ctx, {
    chargeMs: charge, fromMs: charge, toMs: Pricing.addMonths(charge, months) - 86400000,
    method: isCash(sub) ? { type: 'cash' } : method(sub), people: priced(sub.metadata, itemAmounts(sub)), period
  });
}

// ---------------------------------------------------------------------------
async function updated(env: Env, sub: Stripe.Subscription, prev: Partial<Stripe.Subscription>) {
  if (!ours(sub)) return;
  const pending = (s: Partial<Stripe.Subscription>) => Boolean(s.cancel_at_period_end || s.cancel_at);
  const was = ('cancel_at_period_end' in prev || 'cancel_at' in prev) ? pending(prev) : pending(sub);
  const now = pending(sub);
  if (was === now) return;
  const end = sub.cancel_at ? sub.cancel_at * 1000 : periodEnd(sub);
  const st = stripe(env);
  const full = await subscription(st, sub.id);
  const name = customerOf(full)?.name ?? sub.id;
  if (now) {
    const ctx = ctxFor(env, full);
    if (ctx) await member.cancelled(ctx, end);
    await admin(env, `Baja: ${name} · termina el ${date(end, 'es', false)}`, 'Baja', [
      B.h('Baja'),
      B.p(`${esc(name)} se ha dado de baja. La cuota termina el ${date(end, 'es')}, al final del periodo pagado. La familia ya tiene la confirmación.`),
      B.button('Abrir en Stripe', dashboard(env, `subscriptions/${sub.id}`))
    ], 'cancelled');
  } else {
    await admin(env, `Baja deshecha: ${name}`, 'Baja', [
      B.h('Baja deshecha'), B.p(`${esc(name)} ha renovado: la cuota sigue.`),
      B.button('Abrir en Stripe', dashboard(env, `subscriptions/${sub.id}`))
    ], 'reactivated');
  }
}

async function deleted(env: Env, st: Stripe, sub: Stripe.Subscription) {
  if (!ours(sub)) return;
  const full = await st.subscriptions.retrieve(sub.id, { expand: ['customer'] });
  const name = customerOf(full)?.name ?? sub.id;
  const end = (sub.ended_at ?? Math.floor(Date.now() / 1000)) * 1000;
  // A settled withdrawal has already told the family, with the amount.
  const withdrawn = Boolean(sub.metadata.withdrawal_done);
  const leftEarly = Boolean(sub.metadata.early_leave);
  const ctx = ctxFor(env, full);
  if (ctx && !withdrawn && !leftEarly) await member.ended(ctx, end);
  await admin(env, `Cuota terminada${withdrawn ? ' por desistimiento' : ''}: ${name}`, 'Fin', [
    B.h(withdrawn ? 'Desistimiento resuelto' : 'Cuota terminada'),
    ...(withdrawn ? [B.p(`Devueltos ${money(Number(sub.metadata.withdrawal_refund ?? 0), 'es')}. La familia ya tiene el correo con el importe.`)] : []),
    ...(leftEarly ? [B.p(`Baja con devolución de los meses no empezados: ${money(Number(sub.metadata.early_leave_refund ?? 0), 'es')}. La familia ya tiene el correo con el importe.`)] : []),
    B.p(`La cuota de ${esc(name)} ha terminado el ${date(end, 'es')}. ${sub.status === 'canceled' && sub.cancellation_details?.reason === 'payment_failed' ? 'Ha terminado por impago.' : ''}`),
    B.button('Abrir en Stripe', dashboard(env, `subscriptions/${sub.id}`))
  ], 'ended');
}
