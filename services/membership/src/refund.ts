// What a withdrawal costs and what it gives back (spec 11.3).
//
// A member who withdraws within the 14 days, having asked to start at once,
// pays for the days up to their notice and gets the rest back. Every paid
// invoice of the subscription is split at that moment: the part of its period
// already used is kept, the rest is refunded. Day-based, because a membership
// is access to the classes rather than a count of them. The advisor confirms
// the wording; the arithmetic is this.
import type Stripe from 'stripe';

export interface RefundLine { invoice: string; paid: number; start: number; end: number; keep: number; refund: number }

export async function refundFor(st: Stripe, subId: string, atMs: number): Promise<{ lines: RefundLine[]; total: number }> {
  const invoices = await st.invoices.list({ subscription: subId, status: 'paid', limit: 20 });
  const lines: RefundLine[] = [];
  for (const inv of invoices.data) {
    const paid = inv.amount_paid / 100;
    if (paid <= 0) continue;
    const ps = inv.lines.data.map((l) => l.period).filter(Boolean);
    const start = Math.min(...ps.map((p) => p.start)) * 1000;
    const end = Math.max(...ps.map((p) => p.end)) * 1000;
    const span = Math.max(end - start, 1);
    const used = Math.min(Math.max(atMs - start, 0), span);
    const keep = Math.round(paid * (used / span) * 100) / 100;
    lines.push({ invoice: inv.id!, paid, start, end, keep, refund: Math.round((paid - keep) * 100) / 100 });
  }
  return { lines, total: Math.round(lines.reduce((s, l) => s + l.refund, 0) * 100) / 100 };
}
