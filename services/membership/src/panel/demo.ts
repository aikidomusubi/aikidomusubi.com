// Invented families for the panel, shown only by a local `wrangler dev` with
// no Stripe key (ENVIRONMENT=dev) and by the tests. The same households as the
// approved mockup, priced by the real engine so every amount is a true one.
import type Stripe from 'stripe';
import { CATALOG } from '../data.ts';
import { encodeMember, type Meta, type MetaMember } from '../meta.ts';
import { Pricing, type Cat, type PeriodId } from '../pricing.ts';
import { leaveMath, monthlyFee, type Leave } from '../leave.ts';

interface P { name: string; cat: Cat; sc?: 'pending' | 'verified'; venue?: string; bym?: string }
interface F {
  id: string; holder: string; email: string; period: PeriodId; people: P[]; days: number;
  meta?: Meta; status?: Stripe.Subscription.Status; failed?: boolean; ending?: boolean; sepa?: boolean;
  cus?: string; endedDaysAgo?: number; endedBy?: 'cancellation_requested' | 'payment_failed';
}

export function demoSubscriptions(now: number): Stripe.Subscription[] {
  const d = Pricing.madridDate(now);
  // Pol turned seventeen last month, so the new fee is due at the next charge.
  const bornY = d.m === 1 ? d.y - 18 : d.y - 17;
  const bornM = d.m === 1 ? 12 : d.m - 1;
  const pol = `${bornY}-${String(bornM).padStart(2, '0')}`;
  const fams: F[] = [
    { id: 'sub_demoGarcia01', holder: 'Ana García López', email: 'ana.garcia@example.com', period: 'quarterly', days: 20, sepa: true,
      people: [{ name: 'Ana García López', cat: 'adult' }, { name: 'Marc García López', cat: 'adult' }, { name: 'Lía García Ruiz', cat: 'youth', bym: '2014-03' }],
      meta: { hello: 'Ana', paper_due: 'm2,m3', keikogi: 'ready', keikogi_due: 'm1' } },
    { id: 'sub_demoPuig0001', holder: 'Joan Puig Ferrer', email: 'joan.puig@example.com', period: 'monthly', days: 13,
      people: [{ name: 'Joan Puig Ferrer', cat: 'adult', sc: 'pending', venue: 'espronceda' }], meta: { hello: 'Joan', paper_due: 'm1' } },
    { id: 'sub_demoRoca0001', holder: 'Pere Roca Serra', email: 'pere.roca@example.com', period: 'monthly', days: 70, failed: true, sepa: true,
      people: [{ name: 'Pere Roca Serra', cat: 'adult' }, { name: 'Laia Roca Vidal', cat: 'adult' }, { name: 'Bru Roca Vidal', cat: 'youth', bym: '2016-05' }],
      meta: { hello: 'Pere', paper_due: '' } },
    { id: 'sub_demoSoler001', holder: 'Nil Soler Vidal', email: 'nil.soler@example.com', period: 'annual', days: 40,
      people: [{ name: 'Nil Soler Vidal', cat: 'adult' }], meta: { hello: 'Nil', paper_due: '', keikogi: 'ready', keikogi_due: 'm1' } },
    { id: 'sub_demoVidal001', holder: 'Carla Vidal Puig', email: 'carla.vidal@example.com', period: 'monthly', days: 200, ending: true,
      people: [{ name: 'Carla Vidal Puig', cat: 'adult' }], meta: { hello: 'Carla', paper_due: '' } },
    { id: 'sub_demoSerra001', holder: 'Marta Serra Mas', email: 'marta.serra@example.com', period: 'monthly', days: 300,
      people: [{ name: 'Marta Serra Mas', cat: 'adult' }, { name: 'Pol Serra Mas', cat: 'youth', bym: pol }], meta: { hello: 'Marta', paper_due: '' } },
    { id: 'sub_demoMas00001', holder: 'Jordi Mas Puig', email: 'jordi.mas@example.com', period: 'monthly', days: 6,
      people: [{ name: 'Jordi Mas Puig', cat: 'adult' }], meta: { hello: 'Jordi', invite_id: 'demo' } },
    // Asked to withdraw yesterday, within the 14 days.
    { id: 'sub_demoFont0001', holder: 'Laura Font Riera', email: 'laura.font@example.com', period: 'quarterly', days: 5,
      people: [{ name: 'Laura Font Riera', cat: 'adult' }],
      meta: { hello: 'Laura', paper_due: 'm1', keikogi: 'due', keikogi_due: 'm1',
        withdraw_by: new Date(now + 9 * 86400000).toISOString().slice(0, 10), withdrawal_at: new Date(now - 86400000).toISOString() } },
    // Former members: one who left, one who withdrew, and Joan, who was a member before.
    { id: 'sub_demoCosta001', holder: 'Pau Costa Gil', email: 'pau.costa@example.com', period: 'monthly', days: 260, endedDaysAgo: 45,
      people: [{ name: 'Pau Costa Gil', cat: 'adult' }, { name: 'Ona Costa Gil', cat: 'youth', bym: '2015-02' }], meta: { hello: 'Pau', paper_due: '' } },
    { id: 'sub_demoRibas001', holder: 'Marc Ribas Soler', email: 'marc.ribas@example.com', period: 'quarterly', days: 70, endedDaysAgo: 62,
      people: [{ name: 'Marc Ribas Soler', cat: 'adult' }], meta: { hello: 'Marc', withdrawal_at: new Date(now - 63 * 86400000).toISOString(), withdrawal_done: '2026-08-15', withdrawal_refund: '81.40' } },
    { id: 'sub_demoPuigOld1', holder: 'Joan Puig Ferrer', email: 'joan.puig@example.com', period: 'monthly', days: 500, endedDaysAgo: 200, cus: 'cus_demoPuig0001',
      people: [{ name: 'Joan Puig Ferrer', cat: 'adult' }], meta: { hello: 'Joan', keikogi: 'delivered' } }
  ];
  const next = Pricing.nextAnchor(now);
  return fams.map((f) => {
    const members = f.people.map((p) => ({ cat: p.cat, rate: p.sc ? 'sc' as const : 'general' as const, venue: p.venue ?? null }));
    const res = Pricing.price({ period: f.period, members }, CATALOG);
    const meta: Meta = { catalog_version: CATALOG.version, period: f.period, lang: 'es', signup_id: `demo-${f.id}`, withdraw_by: '2026-01-01', ...f.meta };
    f.people.forEach((p, i) => Object.assign(meta, encodeMember({
      slot: i + 1, name: p.name, cat: p.cat, rate: members[i].rate, kind: res.perMember[i].kind,
      venue: p.venue ?? null, sc: p.sc ?? null, bym: p.bym ?? null
    } satisfies MetaMember)));
    const created = Math.floor((now - f.days * 86400000) / 1000);
    return {
      id: f.id, object: 'subscription', status: f.endedDaysAgo ? 'canceled' : f.failed ? 'past_due' : 'active', created,
      ended_at: f.endedDaysAgo ? Math.floor((now - f.endedDaysAgo * 86400000) / 1000) : null,
      cancellation_details: { reason: f.endedDaysAgo ? f.endedBy ?? 'cancellation_requested' : null },
      billing_cycle_anchor: Math.floor(next / 1000) - 86400 * 30,
      cancel_at: null, cancel_at_period_end: Boolean(f.ending), metadata: meta,
      customer: { id: f.cus ?? `cus_${f.id.slice(4)}`, object: 'customer', name: f.holder, email: f.email, phone: '600 000 000' },
      default_payment_method: f.sepa ? { type: 'sepa_debit', sepa_debit: { last4: '1234' } } : { type: 'card', card: { last4: '4242' } },
      latest_invoice: f.failed ? { status: 'open', attempt_count: 2, amount_due: Math.round(res.total * 100) } : { status: 'paid', attempt_count: 1, amount_due: Math.round(res.total * 100) },
      items: { data: res.lineItems.map((l) => ({ price: { lookup_key: l.lookupKey, unit_amount: Math.round(l.unitAmount * 100) }, quantity: l.quantity, current_period_end: Math.floor(next / 1000) })) }
    } as unknown as Stripe.Subscription;
  });
}

// What a withdrawal would give back, for the demo families: one payment, from
// the signup to the next 5th, split at the moment of the request.
export function demoRefund(sub: Stripe.Subscription, at: number) {
  const start = sub.created * 1000;
  const end = (sub.items.data[0] as unknown as { current_period_end: number }).current_period_end * 1000;
  const inv = sub.latest_invoice as unknown as { amount_due: number };
  const paid = inv.amount_due / 100;
  const keep = Math.round(paid * Math.min(Math.max((at - start) / (end - start), 0), 1) * 100) / 100;
  const refund = Math.round((paid - keep) * 100) / 100;
  return { lines: [{ invoice: 'in_demo', paid, start, end, keep, refund }], total: refund };
}

// Leaving early, for the demo families: the current period started a whole
// period before the next 5th, and its invoice is the latest one.
export function demoLeave(sub: Stripe.Subscription, now: number): Leave {
  const months = CATALOG.periods[sub.metadata.period]?.months ?? 1;
  const end = (sub.items.data[0] as unknown as { current_period_end: number }).current_period_end * 1000;
  const start = Pricing.addMonths(end, -months);
  const paid = (sub.latest_invoice as unknown as { amount_due: number }).amount_due / 100;
  const monthly = monthlyFee(sub);
  return { applies: months > 1, invoice: 'in_demo', paid, start, end, months, monthly, ...leaveMath({ paid, start, months, monthly, now }) };
}
