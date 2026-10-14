// A household as the emails and the admin tools see it: the people in a
// subscription's metadata, priced from the subscription's own items.
//
// Amounts come from Stripe's items, not from fees.yml, because a member is
// charged what their subscription says, which after a price change is not
// necessarily today's price list.
import type Stripe from 'stripe';
import { CATALOG, M, esc, money, t, venueName, type Lang } from './data.ts';
import { members as metaMembers, type Meta, type MetaMember } from './meta.ts';
import { Pricing, type Member, type PeriodId } from './pricing.ts';

export function keyFor(m: Pick<MetaMember, 'cat' | 'rate' | 'venue' | 'kind'>, period: string, version: string) {
  return Pricing.lookupKey({ ...CATALOG, version }, { cat: m.cat, rate: m.rate, venue: m.venue }, period, m.kind);
}

// lookup_key → euros, from the subscription's items.
export function itemAmounts(sub: Stripe.Subscription): Record<string, number> {
  const out: Record<string, number> = {};
  for (const it of sub.items.data) {
    const k = it.price.lookup_key;
    if (k && it.price.unit_amount != null) out[k] = it.price.unit_amount / 100;
  }
  return out;
}

export interface Priced extends MetaMember { amount: number }

export function priced(meta: Meta, amounts: Record<string, number>): Priced[] {
  const ver = meta.catalog_version || CATALOG.version;
  return metaMembers(meta).map((m) => ({ ...m, amount: amounts[keyFor(m, meta.period, ver)] ?? NaN }));
}

export function total(people: Priced[]) {
  return people.reduce((s, p) => s + (Number.isFinite(p.amount) ? p.amount : 0), 0);
}

// "Ana García López · 17 o más · cuota completa" — names escaped here, so the
// rows can go straight into an email table.
export function personLabel(p: Pick<Priced, 'name' | 'cat' | 'kind' | 'venue'>, lang: Lang, familyOff?: number) {
  const age = t(p.cat === 'adult' ? M.ui.adult_short : M.ui.youth_short, lang);
  const kind = p.kind === 'full' ? t(M.ui.kind_full, lang)
    : p.kind === 'sc' ? t(M.ui.kind_sc, lang, { venue: venueName(p.venue, lang) })
    : t(M.ui.kind_family, lang, { amount: money(familyOff ?? CATALOG.family, lang) });
  return `${esc(p.name)} · ${esc(age)} · ${esc(kind)}`;
}

export function peopleRows(people: Priced[], period: PeriodId, lang: Lang, totalLabel: string): [string, string][] {
  const months = CATALOG.periods[period]?.months ?? 1;
  const rows: [string, string][] = people.map((p) => [personLabel(p, lang, CATALOG.family * months), money(p.amount, lang)]);
  rows.push([esc(totalLabel), money(total(people), lang)]);
  return rows;
}

export const asMembers = (people: MetaMember[]): Member[] => people.map((p) => ({ cat: p.cat, rate: p.rate, venue: p.venue }));
