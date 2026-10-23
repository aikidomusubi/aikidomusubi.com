// Paying the fee in cash (decided 23 October 2026).
//
// A cash membership is an ordinary subscription with `metadata.method` set to
// "cash" and collection_method "send_invoice": Stripe makes the invoice on the
// 1st, as it would charge a card on the 5th, but waits to be told it was paid.
// The family pays at the dojo from the 1st to the 5th (the first time, within
// five days of signing up), the treasurer presses Cobrado in the panel, and
// that marks every open invoice of the membership paid outside Stripe and
// emails the family a receipt. So Stripe is still the one record: every cash
// payment is a paid invoice there, with its number and its PDF.
//
// Stripe has no field saying an invoice was paid in cash, so ours do: the
// invoice's metadata gets cash, cash_by and cash_at when it is marked.
//
// A refund to a cash family (a withdrawal, leaving early) is a credit note
// "outside Stripe": the record is kept in Stripe and the money is handed back
// at the dojo.
import type Stripe from 'stripe';
import type { Env } from './env.ts';
import { isoDay, madrid } from './data.ts';
import { Pricing } from './pricing.ts';
import { itemAmounts, priced, total } from './household.ts';
import { periodEnd } from './stripe.ts';
import { ctxFor } from './context.ts';
import * as member from './email/member.ts';

export const isCash = (sub: Pick<Stripe.Subscription, 'metadata'>) => sub.metadata?.method === 'cash';

// The period an invoice pays for: from its lines, as src/refund.ts reads it.
export function invoicePeriod(inv: Stripe.Invoice): { start: number; end: number } {
  const ps = (inv.lines?.data ?? []).map((l) => l.period).filter(Boolean);
  if (!ps.length) return { start: (inv.created ?? 0) * 1000, end: (inv.created ?? 0) * 1000 };
  return { start: Math.min(...ps.map((p) => p.start)) * 1000, end: Math.max(...ps.map((p) => p.end)) * 1000 };
}

// The last day to pay, as a Madrid date (YYYY-MM-DD). The first invoice:
// five days from signing up. Every other: the 5th of the month its period
// starts in. This is the dojo's rule, not Stripe's due date, which is set a
// day later on purpose (cashParams in src/checkout.ts).
export function payBy(inv: Pick<Stripe.Invoice, 'billing_reason' | 'created'> & { lines?: Stripe.Invoice['lines'] }): string {
  const created = (inv.created ?? 0) * 1000;
  if (inv.billing_reason === 'subscription_create') return isoDay(created + Pricing.CASH.firstDays * 86400000);
  const start = invoicePeriod(inv as Stripe.Invoice).start || created;
  const d = madrid(start);
  return `${d.y}-${String(d.m).padStart(2, '0')}-${String(Pricing.CASH.by).padStart(2, '0')}`;
}
export const isLate = (inv: Parameters<typeof payBy>[0], now = Date.now()) => isoDay(now) > payBy(inv);
export const payByMs = (inv: Parameters<typeof payBy>[0]) => Date.parse(payBy(inv) + 'T12:00:00Z');

export async function openInvoices(st: Stripe, subId: string): Promise<Stripe.Invoice[]> {
  const res = await st.invoices.list({ subscription: subId, status: 'open', limit: 24 });
  return res.data.filter((i) => i.amount_remaining > 0).sort((a, b) => (a.created ?? 0) - (b.created ?? 0));
}

// Cobrado: every open invoice of the membership, oldest first, marked paid
// outside Stripe, and one receipt for all of them.
export async function collect(env: Env, st: Stripe, sub: Stripe.Subscription, by: string, now = Date.now()) {
  const open = await openInvoices(st, sub.id);
  if (!open.length) throw new Error('nothing to collect on this membership');
  const paid: Stripe.Invoice[] = [];
  for (const inv of open) {
    await st.invoices.update(inv.id!, { metadata: { cash: 'true', cash_by: by, cash_at: new Date(now).toISOString() } });
    paid.push(await st.invoices.pay(inv.id!, { paid_out_of_band: true }, { idempotencyKey: `cash-${inv.id}` }));
  }
  await receipt(env, sub, paid, now);
  return { total: round(paid.reduce((s, i) => s + i.amount_paid, 0) / 100), invoices: paid };
}

// The receipt again, for the last cash payment (the panel's Reenviar).
export async function resend(env: Env, st: Stripe, sub: Stripe.Subscription) {
  const res = await st.invoices.list({ subscription: sub.id, status: 'paid', limit: 24 });
  const last = res.data.filter((i) => i.metadata?.cash === 'true').sort((a, b) => Date.parse(b.metadata!.cash_at ?? '') - Date.parse(a.metadata!.cash_at ?? ''));
  if (!last.length) throw new Error('no cash payment on this membership');
  const at = last[0].metadata!.cash_at;
  const same = last.filter((i) => i.metadata!.cash_at === at);
  await receipt(env, sub, same, Date.parse(at ?? '') || Date.now());
  return same;
}

async function receipt(env: Env, sub: Stripe.Subscription, invoices: Stripe.Invoice[], paidMs: number) {
  const ctx = ctxFor(env, sub);
  if (!ctx) return;
  const people = priced(sub.metadata, itemAmounts(sub));
  await member.cashReceipt(ctx, {
    paidMs,
    invoices: invoices.map((i) => ({ number: i.number ?? i.id ?? '', amount: i.amount_paid / 100, ...invoicePeriod(i), pdf: i.invoice_pdf ?? null })),
    people: invoices.length === 1 && invoices[0].billing_reason === 'subscription_cycle' ? people : null,
    period: sub.metadata.period as never,
    // Nothing more to pay if the membership is ending at this period's end.
    next: sub.cancel_at_period_end || sub.cancel_at ? null : { ms: periodEnd(sub), amount: total(people) }
  });
}

// A refund outside Stripe: a credit note recording the money handed back.
export async function creditCash(st: Stripe, invoice: string, amount: number, description: string, key: string) {
  const cents = Math.round(amount * 100);
  if (cents <= 0) return;
  await st.creditNotes.create({
    invoice,
    lines: [{ type: 'custom_line_item', description: description.slice(0, 200), quantity: 1, unit_amount: cents }],
    out_of_band_amount: cents
  }, { idempotencyKey: key });
}

// Ending a cash membership that still owes something: the unpaid invoices
// are voided, because nothing will be collected for a membership that is
// over. What the family owes for days used is settled at the dojo.
export async function voidOpen(st: Stripe, subId: string) {
  for (const inv of await openInvoices(st, subId)) await st.invoices.voidInvoice(inv.id!);
}

// Changing how a family pays, through the dojo. Each takes effect on the day
// that method's month begins, so the dates stay "1st to 5th" for cash and
// "the 5th" for card: the daily job does it (src/cron.ts), and Stripe credits
// whatever of the current period was already paid.
export async function switchToCash(st: Stripe, sub: Stripe.Subscription) {
  await st.subscriptions.update(sub.id, {
    collection_method: 'send_invoice', days_until_due: Pricing.CASH.firstDays + 1,
    billing_cycle_anchor: { type: 'now' }, proration_behavior: 'create_prorations' as const,
    metadata: { method: 'cash', method_next: '' }
  });
}

export async function switchToCard(st: Stripe, sub: Stripe.Subscription) {
  await st.subscriptions.update(sub.id, {
    collection_method: 'charge_automatically',
    billing_cycle_anchor: { type: 'now' }, proration_behavior: 'create_prorations' as const,
    metadata: { method: '', method_next: '' }
  });
}

const round = (n: number) => Math.round(n * 100) / 100;
