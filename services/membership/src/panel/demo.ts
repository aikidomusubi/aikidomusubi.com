// Invented families for the panel, shown only by a local `wrangler dev` with
// no Stripe key (ENVIRONMENT=dev) and by the tests. The same households as the
// approved mockup, priced by the real engine so every amount is a true one.
import type Stripe from 'stripe';
import { CATALOG } from '../data.ts';
import { encodeMember, type Meta, type MetaMember } from '../meta.ts';
import { Pricing, type Cat, type PeriodId } from '../pricing.ts';

interface P { name: string; cat: Cat; sc?: 'pending' | 'verified'; venue?: string; bym?: string }
interface F {
  id: string; holder: string; email: string; period: PeriodId; people: P[]; days: number;
  meta?: Meta; status?: Stripe.Subscription.Status; failed?: boolean; ending?: boolean; sepa?: boolean;
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
      people: [{ name: 'Jordi Mas Puig', cat: 'adult' }], meta: { hello: 'Jordi', invite_id: 'demo' } }
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
      id: f.id, object: 'subscription', status: f.failed ? 'past_due' : 'active', created,
      billing_cycle_anchor: Math.floor(next / 1000) - 86400 * 30,
      cancel_at: null, cancel_at_period_end: Boolean(f.ending), metadata: meta,
      customer: { id: `cus_${f.id.slice(4)}`, object: 'customer', name: f.holder, email: f.email, phone: '600 000 000' },
      default_payment_method: f.sepa ? { type: 'sepa_debit', sepa_debit: { last4: '1234' } } : { type: 'card', card: { last4: '4242' } },
      latest_invoice: f.failed ? { status: 'open', attempt_count: 2, amount_due: Math.round(res.total * 100) } : { status: 'paid', attempt_count: 1, amount_due: Math.round(res.total * 100) },
      items: { data: res.lineItems.map((l) => ({ price: { lookup_key: l.lookupKey, unit_amount: Math.round(l.unitAmount * 100) }, quantity: l.quantity, current_period_end: Math.floor(next / 1000) })) }
    } as unknown as Stripe.Subscription;
  });
}
