// Settling a withdrawal (spec 11.3), from the panel, so nobody has to do it in
// the Stripe Dashboard: refund every paid invoice for the part of its period
// after the notice, end the membership at once, and tell the family the amount.
//
// THE AMOUNT IS FIXED AT THE NOTICE, NOT AT THE SETTLING. The law has the
// member pay for the days up to the moment they told us, so refundFor() is
// always run at `withdrawal_at`, stamped on the subscription by /withdrawal
// when the request arrived. Settling it a week later gives the same figure.
//
// Order matters: the metadata is written first, because cancelling fires
// customer.subscription.deleted, and the webhook reads `withdrawal_done` to
// send this email instead of the ordinary "your membership has ended".
import type Stripe from 'stripe';
import type { Env } from './env.ts';
import { isoDay } from './data.ts';
import { refundFor, type RefundLine } from './refund.ts';
import { ctxFor } from './context.ts';
import * as member from './email/member.ts';

export const withdrawalAt = (sub: Stripe.Subscription) => {
  const at = Date.parse(sub.metadata?.withdrawal_at ?? '');
  return Number.isFinite(at) ? at : null;
};

// Within the 14 days, a withdrawal; after them, it is a cancellation.
export const inWindow = (sub: Stripe.Subscription, at: number) =>
  !sub.metadata.withdraw_by || isoDay(at) <= sub.metadata.withdraw_by;

// A payment still being confirmed (a first SEPA debit takes days) cannot be
// refunded yet, and would be collected after the cancellation: wait for it.
export function pendingPayment(sub: Stripe.Subscription): boolean {
  const inv = sub.latest_invoice && typeof sub.latest_invoice !== 'string' ? sub.latest_invoice : null;
  return Boolean(inv && inv.status === 'open' && inv.amount_due > 0);
}

async function paymentOf(st: Stripe, invoice: string): Promise<{ payment_intent: string } | { charge: string }> {
  const pays = await st.invoicePayments.list({ invoice, status: 'paid', limit: 5 });
  for (const ip of pays.data) {
    const p = ip.payment;
    const pi = typeof p.payment_intent === 'string' ? p.payment_intent : p.payment_intent?.id;
    if (pi) return { payment_intent: pi };
    const ch = typeof p.charge === 'string' ? p.charge : p.charge?.id;
    if (ch) return { charge: ch };
  }
  throw new Error(`no paid payment found for ${invoice}`);
}

export async function settle(env: Env, st: Stripe, sub: Stripe.Subscription): Promise<{ total: number; lines: RefundLine[] }> {
  const at = withdrawalAt(sub);
  if (at == null) throw new Error('no withdrawal on this membership');
  if (pendingPayment(sub)) throw new Error('a payment is still being confirmed');
  const r = await refundFor(st, sub.id, at);
  for (const l of r.lines) {
    if (l.refund <= 0) continue;
    await st.refunds.create({
      ...(await paymentOf(st, l.invoice)),
      amount: Math.round(l.refund * 100),
      reason: 'requested_by_customer',
      metadata: { withdrawal: sub.id, invoice: l.invoice }
    }, { idempotencyKey: `wd-${sub.id}-${l.invoice}` });
  }
  await st.subscriptions.update(sub.id, { metadata: { withdrawal_done: isoDay(Date.now()), withdrawal_refund: r.total.toFixed(2) } });
  await st.subscriptions.cancel(sub.id, { prorate: false, invoice_now: false, cancellation_details: { comment: 'Desistimiento' } });
  const ctx = ctxFor(env, sub);
  if (ctx) await member.withdrawalDone(ctx, { amount: r.total, atMs: at });
  return r;
}
