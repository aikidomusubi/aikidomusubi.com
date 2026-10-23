// Leaving a quarterly or annual plan early, with the months not yet started
// refunded (the terms, section 8; decided 15 October 2026).
//
// Worked out as if the period had been paid month by month: from what was paid
// for the current period, the current monthly fee of the household (family
// discount included) is kept for every month already started, and the rest is
// refunded. A monthly plan has nothing to refund, and is not offered this.
//
// Like a withdrawal it is one press in the panel: refund, cancel at once, and
// one email to the family with the amount (src/withdraw.ts has the same shape).
import type Stripe from 'stripe';
import type { Env } from './env.ts';
import { CATALOG, isoDay, keikogiCost } from './data.ts';
import { members as metaMembers, slots } from './meta.ts';
import { asMembers } from './household.ts';
import { Pricing } from './pricing.ts';
import { periodEnd, periodStart } from './stripe.ts';
import { paymentOf, pendingPayment } from './withdraw.ts';
import { ctxFor } from './context.ts';
import * as member from './email/member.ts';
import { creditCash, isCash, voidOpen } from './cash.ts';

export interface Leave {
  applies: boolean;          // a quarterly or annual period, paid, that has not ended
  invoice: string | null;    // the invoice that paid the current period
  paid: number;
  start: number;
  end: number;
  months: number;            // in the period: 3 or 12
  started: number;           // months of it already begun, counting the current one
  monthly: number;           // the household's monthly fee now
  keikogi: number;           // what the keikogi already handed over cost
  keikogiCount: number;
  keep: number;
  refund: number;
}

const r2 = (n: number) => Math.round(n * 100) / 100;

// The arithmetic alone, so it can be tested without Stripe. `keikogi` is what
// the keikogi already handed over cost the dojo: bought for the member and
// not returnable, so it is kept as well (terms, section 8).
export function leaveMath(o: { paid: number; start: number; months: number; monthly: number; now: number; keikogi?: number }) {
  let started = 0;
  while (started < o.months && Pricing.addMonths(o.start, started) <= o.now) started++;
  const keep = r2(Math.min(o.paid, started * o.monthly + (o.keikogi ?? 0)));
  return { started, keep, refund: r2(Math.max(0, o.paid - keep)) };
}

// The keikogi this membership has handed over: those it was for, less those
// still due. A membership from before keikogi_for existed counts everybody
// who is no longer due once the keikogi were ready.
export function keikogiGiven(meta: Stripe.Metadata): { count: number; cost: number } {
  const state = meta.keikogi ?? '';
  if (state !== 'ready' && state !== 'delivered') return { count: 0, cost: 0 };
  const due = slots(meta.keikogi_due);
  const forWhom = 'keikogi_for' in meta ? slots(meta.keikogi_for) : metaMembers(meta).map((m) => `m${m.slot}`);
  const given = metaMembers(meta).filter((m) => forWhom.includes(`m${m.slot}`) && !due.includes(`m${m.slot}`));
  return { count: given.length, cost: given.reduce((s, m) => s + keikogiCost(m.cat), 0) };
}

export const monthlyFee = (sub: Stripe.Subscription) =>
  Pricing.price({ period: 'monthly', members: asMembers(metaMembers(sub.metadata)) }, CATALOG).total;

export async function leaveQuote(st: Stripe, sub: Stripe.Subscription, now = Date.now()): Promise<Leave> {
  const months = CATALOG.periods[sub.metadata.period]?.months ?? 1;
  const start = periodStart(sub);
  const end = periodEnd(sub);
  const monthly = monthlyFee(sub);
  const k = keikogiGiven(sub.metadata);
  const none: Leave = { applies: false, invoice: null, paid: 0, start, end, months, started: 0, monthly, keikogi: k.cost, keikogiCount: k.count, keep: 0, refund: 0 };
  if (months === 1 || sub.status === 'canceled' || pendingPayment(sub) || now >= end) return none;
  // The invoice whose lines cover the current period.
  const invoices = await st.invoices.list({ subscription: sub.id, status: 'paid', limit: 10 });
  const inv = invoices.data.find((i) => i.lines.data.some((l) => l.period && Math.abs(l.period.start * 1000 - start) < 86400000));
  if (!inv) return none;
  const paid = inv.amount_paid / 100;
  return { applies: true, invoice: inv.id!, paid, start, end, months, monthly, keikogi: k.cost, keikogiCount: k.count,
    ...leaveMath({ paid, start, months, monthly, now, keikogi: k.cost }) };
}

export async function settleLeave(env: Env, st: Stripe, sub: Stripe.Subscription): Promise<Leave> {
  const q = await leaveQuote(st, sub);
  if (!q.applies) throw new Error('nothing to refund early on this membership');
  const cash = isCash(sub);
  if (q.refund > 0 && cash) {
    await creditCash(st, q.invoice!, q.refund, 'Baja: meses no empezados, se devuelven en efectivo en el dojo', `leave-${sub.id}-${q.invoice}`);
  } else if (q.refund > 0) {
    await st.refunds.create({
      ...(await paymentOf(st, q.invoice!)),
      amount: Math.round(q.refund * 100),
      reason: 'requested_by_customer',
      metadata: { early_leave: sub.id, invoice: q.invoice! }
    }, { idempotencyKey: `leave-${sub.id}-${q.invoice}` });
  }
  // Written before the cancellation, so the webhook sends this email rather
  // than the ordinary "your membership has ended" (as for a withdrawal).
  await st.subscriptions.update(sub.id, { metadata: { early_leave: isoDay(Date.now()), early_leave_refund: q.refund.toFixed(2) } });
  if (cash) await voidOpen(st, sub.id);
  await st.subscriptions.cancel(sub.id, { prorate: false, invoice_now: false, cancellation_details: { comment: 'Baja con devolución de meses no empezados' } });
  const ctx = ctxFor(env, sub);
  if (ctx) await member.earlyLeaveDone(ctx, { amount: q.refund, paid: q.paid, started: q.started, monthly: q.monthly, keikogi: q.keikogi, cash });
  return q;
}
