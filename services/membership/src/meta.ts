// Subscription metadata: the only place the household is written down.
//
// Stripe allows 50 keys of up to 40 characters, values up to 500. The spec's
// flat keys (m1_name, m1_cat, m1_price, m1_birth_ym, ...) times six people plus
// the rest come to more than 50 once the rate is per person, so each person is
// two keys instead:
//
//   m1_name   "Ana García López"
//   m1        "cat=adult;rate=general;kind=full"
//             "cat=youth;rate=sc;venue=sant-adria;kind=sc;sc=pending;bym=2014-03"
//
// Both are readable in the Stripe Dashboard, which is where the dojo looks.
// The household-level keys:
//
//   catalog_version period lang signup_id holder terms_version terms_at
//   early_start_at adult_at guardian_at invite_id withdraw_by
//   keikogi        ""|due|paid|ready|delivered — see src/keikogi.ts
//   keikogi_due    "m1,m2,m3": who has not had theirs yet
//   keikogi_for    who this membership gives one to at all (fixed at signup)
//   first_full     the day the first full period was paid (YYYY-MM-DD)
//
// Nothing here is payment data, an ID number, health data or free text the
// person typed other than names (spec 6.6).
import type { Cat, Kind, PeriodId, Rate } from './pricing.ts';

export type Meta = Record<string, string>;

export interface MetaMember {
  slot: number;
  name: string;
  cat: Cat;
  rate: Rate;
  kind: Kind;
  venue: string | null;
  sc: 'pending' | 'verified' | 'rejected' | null;
  bym: string | null;            // YYYY-MM
}

export function encodeMember(m: MetaMember): Meta {
  const parts = [`cat=${m.cat}`, `rate=${m.rate}`];
  if (m.venue) parts.push(`venue=${m.venue}`);
  parts.push(`kind=${m.kind}`);
  if (m.sc) parts.push(`sc=${m.sc}`);
  if (m.bym) parts.push(`bym=${m.bym}`);
  return { [`m${m.slot}_name`]: m.name.slice(0, 500), [`m${m.slot}`]: parts.join(';') };
}

export function members(meta: Meta): MetaMember[] {
  const out: MetaMember[] = [];
  for (let n = 1; n <= 6; n++) {
    const raw = meta[`m${n}`];
    if (!raw) continue;
    const kv: Record<string, string> = {};
    raw.split(';').forEach((p) => { const [k, v] = p.split('='); if (k) kv[k] = v ?? ''; });
    out.push({
      slot: n,
      name: meta[`m${n}_name`] ?? '',
      cat: (kv.cat as Cat) ?? 'adult',
      rate: (kv.rate as Rate) ?? 'general',
      kind: (kv.kind as Kind) ?? 'full',
      venue: kv.venue || null,
      sc: (kv.sc as MetaMember['sc']) || null,
      bym: kv.bym || null
    });
  }
  return out;
}

// The keys to send to Stripe to rewrite one person. Removing a key is done by
// sending it empty.
export function memberUpdate(m: MetaMember): Meta {
  return encodeMember(m);
}

export const slots = (s: string | undefined) =>
  (s ?? '').split(',').map((x) => x.trim()).filter(Boolean);

export const period = (meta: Meta) => (meta.period as PeriodId) || 'monthly';

export const firstName = (full: string) => full.split(' ')[0] ?? full;
