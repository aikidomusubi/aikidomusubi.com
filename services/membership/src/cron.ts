// The daily job, at 08:00 UTC. The day of the month decides what runs.
//
//   every day   keikogi whose 14 days have just ended; customers created by an
//               abandoned checkout more than a day ago (deleted, with nothing
//               attached to them: they hold a name and an email and no reason
//               to keep either)
//   the 1st     while members are moving over: who to leave out of this
//               month's bank remittance (decided 14 October 2026, fix 4)
//   the 20th    the digest: who turns 17 before their next charge, sports-
//               centre cards still unchecked after 30 days, paper forms still
//               missing after 14, payments overdue
//   every day   cash: a reminder to each family whose last day to pay has
//               gone (once per invoice); on the 1st, the families moving to
//               cash; on the 5th, those moving to card (src/cash.ts)
import type Stripe from 'stripe';
import type { Env } from './env.ts';
import { flag } from './env.ts';
import { date, esc, isoDay, madrid, money, venueName } from './data.ts';
import { log } from './http.ts';
import { members as metaMembers, slots, type MetaMember } from './meta.ts';
import { Pricing } from './pricing.ts';
import { customerOf, periodEnd, stripe } from './stripe.ts';
import { actionUrl, apply, autoAge, notifyKeikogiReady } from './actions.ts';
import { admin, todo, dashboard, B, type Todo } from './email/admin.ts';
import type { InviteRecord } from './invite.ts';
import { isCash, isLate, openInvoices, payByMs, switchToCard, switchToCash } from './cash.ts';
import { ctxFor } from './context.ts';
import * as member from './email/member.ts';

export async function daily(env: Env, now = Date.now()) {
  const st = stripe(env);
  const day = madrid(now).d;
  await keikogi(env, st, now);
  await orphans(st, now);
  await cash(env, st, now, day);
  if (day === 1 && flag(env.MIGRATION_REMITTANCE_LIST)) await remittance(env, st, now);
  if (day === 20) await digest(env, st, now);
}

async function allOurs(st: Stripe, status: Stripe.SubscriptionListParams.Status | 'all' = 'all') {
  const out: Stripe.Subscription[] = [];
  for await (const s of st.subscriptions.list({ status, limit: 100, expand: ['data.customer', 'data.latest_invoice'] })) {
    if (s.metadata?.signup_id) out.push(s);
  }
  return out;
}

async function keikogi(env: Env, st: Stripe, now: number) {
  const today = isoDay(now);
  const res = await st.subscriptions.search({ query: "metadata['keikogi']:'paid'", limit: 100 });
  for (const sub of res.data) {
    if (sub.status !== 'active') continue;
    if (today > sub.metadata.withdraw_by) {
      const full = await st.subscriptions.retrieve(sub.id, { expand: ['customer'] });
      await notifyKeikogiReady(env, st, full);
    }
  }
}

// ---------------------------------------------------------------------------
async function cash(env: Env, st: Stripe, now: number, day: number) {
  const res = await st.subscriptions.search({ query: "metadata['method']:'cash' OR metadata['method_next']:'cash' OR metadata['method_next']:'card'", limit: 100 });
  for (const sub of res.data) {
    if (!sub.metadata?.signup_id || !['active', 'past_due', 'unpaid'].includes(sub.status)) continue;
    try {
      if (day === 1 && sub.metadata.method_next === 'cash' && !isCash(sub)) {
        await switchToCash(st, sub);
        log({ job: 'cash', sub: sub.id, outcome: 'to_cash' });
        continue;
      }
      if (!isCash(sub)) continue;
      const open = await openInvoices(st, sub.id);
      // To card on the 5th, once nothing is owed in cash: otherwise Stripe
      // would credit days that were never paid. It waits a month.
      if (day === 5 && sub.metadata.method_next === 'card' && !open.length) {
        await switchToCard(st, sub);
        log({ job: 'cash', sub: sub.id, outcome: 'to_card' });
        continue;
      }
      const late = open.filter((i) => isLate(i, now));
      if (!late.length) continue;
      const newest = late[late.length - 1];
      const key = `late:${newest.id}`;
      if (await env.KV.get(key)) continue;
      const full = await st.subscriptions.retrieve(sub.id, { expand: ['customer'] });
      const ctx = ctxFor(env, full);
      if (ctx) await member.cashLate(ctx, { amount: late.reduce((s, i) => s + i.amount_remaining, 0) / 100, byMs: payByMs(late[0]) });
      await env.KV.put(key, '1', { expirationTtl: 120 * 86400 });
      log({ job: 'cash', sub: sub.id, outcome: 'late_reminder' });
    } catch (e) {
      log({ job: 'cash', sub: sub.id, outcome: 'error', error: (e as Error).message?.slice(0, 200) });
    }
  }
}

async function orphans(st: Stripe, now: number) {
  const cutoff = Math.floor(now / 1000) - 86400;
  const res = await st.customers.search({ query: `metadata['source']:'signup' AND created<${cutoff}`, limit: 100 });
  let n = 0;
  for (const c of res.data) {
    const subs = await st.subscriptions.list({ customer: c.id, status: 'all', limit: 1 });
    const invs = await st.invoices.list({ customer: c.id, limit: 1 });
    if (!subs.data.length && !invs.data.length) { await st.customers.del(c.id); n++; }
  }
  if (n) log({ job: 'orphans', deleted: n });
}

// ---------------------------------------------------------------------------
async function remittance(env: Env, st: Stripe, now: number) {
  const { y, m } = madrid(now);
  const monthEnd = Date.UTC(y, m, 1);              // first day of next month
  const moved: string[] = [];
  const later: string[] = [];
  for (const s of await allOurs(st)) {
    if (!s.metadata.invite_id || !['active', 'trialing', 'past_due', 'incomplete'].includes(s.status)) continue;
    const first = s.billing_cycle_anchor * 1000;
    const name = esc(customerOf(s)?.name ?? s.id);
    if (first < monthEnd) moved.push(`${name} · primer cobro por Stripe el ${date(first, 'es')}`);
    else later.push(`${name} · desde ${date(first, 'es')}`);
  }
  let unused = 0;
  let cursor: string | undefined;
  do {
    const page = await env.KV.list({ prefix: 'invite:', cursor });
    for (const k of page.keys) {
      const rec = JSON.parse((await env.KV.get(k.name)) ?? '{}') as InviteRecord;
      if (!rec.used) unused++;
    }
    cursor = page.list_complete ? undefined : page.cursor;
  } while (cursor);
  if (!moved.length && !later.length && !unused) return;

  const month = date(Date.UTC(y, m - 1, 15), 'es').replace(/^\d+ de /, '');
  await admin(env, `Remesa del banco de ${month}: no incluyas a estas ${moved.length} cuotas`, 'Remesa', [
    B.h(`Antes de la remesa de ${month}`),
    B.p(`Estas cuotas ya pagan por Stripe este mes. <b>No las incluyas en la remesa del banco</b>, o pagarán dos veces.`),
    ...(moved.length ? [B.box(moved.join('<br>'))] : [B.p('Ninguna todavía.')]),
    ...(later.length ? [B.p('Empiezan más adelante, así que este mes <b>siguen</b> en la remesa:'), B.box(later.join('<br>'))] : []),
    B.p(`Invitaciones sin usar: <b>${unused}</b>. Esas personas siguen pagando por el banco.`),
    B.small('Cuando ya no quede nadie por pasar, pon MIGRATION_REMITTANCE_LIST a "false" en wrangler.toml y este aviso deja de llegar.')
  ], 'remittance');
}

// ---------------------------------------------------------------------------
async function digest(env: Env, st: Stripe, now: number) {
  const items: Todo[] = [];
  const done: string[] = [];
  const pastDue: Todo[] = [];
  for (const s of await allOurs(st)) {
    if (isCash(s)) {
      const inv = s.latest_invoice && typeof s.latest_invoice !== 'string' ? s.latest_invoice : null;
      if (inv && inv.status === 'open' && isLate(inv, now)) {
        pastDue.push({ title: `${customerOf(s)?.name ?? s.id}: cuota en efectivo sin pagar, ${money(inv.amount_remaining / 100, 'es')}`,
          sub: `Tocaba hasta el ${date(payByMs(inv), 'es')}. Ya tiene el recordatorio; habla con la familia en su próxima clase.`,
          action: { label: 'Abrir en el panel', href: `${env.API_ORIGIN}/panel/miembros?id=${s.id}` } });
      }
    } else if (s.status === 'past_due' || s.status === 'unpaid') {
      pastDue.push({ title: `${customerOf(s)?.name ?? s.id}: cobro pendiente`, sub: 'Stripe ya lo ha reintentado. La cuota sigue activa, pendiente de pago.',
        action: { label: 'Abrir', href: dashboard(env, `subscriptions/${s.id}`) } });
    }
    if (s.status !== 'active' && s.status !== 'past_due') continue;
    const next = periodEnd(s);
    for (const m of metaMembers(s.metadata)) {
      if (m.bym) {
        const [y, mo] = m.bym.split('-').map(Number);
        // Only the month of birth is known, so the change is applied from the
        // first charge in a month AFTER the birthday month: never early.
        if (Pricing.addMonths(Pricing.turns17(y, mo), 1) <= next) {
          const key = `age:${s.id}:${m.slot}`;
          if (await env.KV.get(key)) continue;
          if (autoAge(env)) {
            done.push(await apply(env, st, s, m, 'age', 'automático'));
            await env.KV.put(key, '1', { expirationTtl: 400 * 86400 });
          } else {
            items.push(await ageItem(env, s, m, next));
            await env.KV.put(key, '1', { expirationTtl: 45 * 86400 });
          }
        }
      }
      if (slots(s.metadata.paper_due).includes(`m${m.slot}`) && now - s.created * 1000 > 14 * 86400000) {
        items.push({ title: `${m.name}: falta la hoja de inscripción en papel`, sub: `Inscripción del ${date(s.created * 1000, 'es')}.`,
          action: { label: 'Recibida', href: await actionUrl(env, 'paper', s.id, m.slot) } });
      }
      if (m.sc === 'pending' && now - s.created * 1000 > 30 * 86400000) {
        items.push({ title: `${m.name}: abono de ${venueName(m.venue, 'es')} sin comprobar`, sub: `Desde el ${date(s.created * 1000, 'es')}.`,
          action: { label: 'Comprobado', href: await actionUrl(env, 'sc_ok', s.id, m.slot) } });
      }
    }
  }
  if (!items.length && !pastDue.length && !done.length) return;
  await admin(env, `Cuotas: ${items.length + pastDue.length + done.length} cosas antes del próximo cobro`, 'Resumen del día 20', [
    B.h('Antes del cobro del día 5'),
    B.p(`Todo esto está también en el panel de cuotas: <a href="${env.API_ORIGIN}/panel/">${env.API_ORIGIN.replace(/^https?:\/\//, '')}/panel</a>.`),
    ...(items.length ? [B.h4('Para decidir'), todo(items)] : []),
    ...(done.length ? [B.h4('Hecho automáticamente'), B.box(done.map(esc).join('<br>'))] : []),
    ...(pastDue.length ? [B.h4('Cobros pendientes'), todo(pastDue)] : [])
  ], 'digest');
}

async function ageItem(env: Env, s: Stripe.Subscription, m: MetaMember, next: number): Promise<Todo> {
  return {
    title: `${m.name} cumple 17 antes del cobro del ${date(next, 'es')}`,
    sub: `${customerOf(s)?.name ?? ''}. Pulsa para pasarle a la cuota de 17 o más desde ese cobro: se recalcula la familia y se le avisa.`,
    action: { label: 'Aplicar y avisar', href: await actionUrl(env, 'age', s.id, m.slot) }
  };
}

export { money };
