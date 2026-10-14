// Validation (spec 6.2) and the metadata it produces (6.6).
import { describe, expect, it } from 'vitest';
import { validate, unknownFields } from '../src/validate.ts';
import { metadata } from '../src/checkout.ts';
import { members } from '../src/meta.ts';
import { CATALOG } from '../src/data.ts';
import { Pricing } from '../src/pricing.ts';
import { FAMILY } from './helpers.ts';

const NOW = Date.parse('2027-01-20T18:04:00Z');
const codes = (body: Record<string, string>) => {
  const r = validate(body, NOW);
  return r.ok ? [] : r.errors.map((e) => `${e.field}:${e.code}`);
};

describe('a valid household', () => {
  it('passes', () => {
    const r = validate(FAMILY, NOW);
    expect(r.ok).toBe(true);
    if (r.ok) {
      expect(r.value.members.map((m) => m.cat)).toEqual(['adult', 'adult', 'youth']);
      expect(r.value.holder).toMatchObject({ slot: 1, given: 'Ana', family: 'García López' });
      expect(r.value.minors).toBe(true);
    }
  });
  it('accepts names in any script', () => {
    expect(codes({ ...FAMILY, p1_given: 'ジョアン・マネル', p1_family: 'モリナ' })).toEqual([]);
    expect(codes({ ...FAMILY, p1_given: "D'Artagnan", p1_family: 'Pérez-Molina' })).toEqual([]);
    expect(codes({ ...FAMILY, p1_given: 'J. M.', p1_family: 'Pérez' })).toEqual([]);
  });
  it('ignores empty person blocks from the no-JavaScript form', () => {
    expect(codes({ ...FAMILY, p4_given: '', p4_family: '', p4_cat: '' })).toEqual([]);
  });
});

describe('every rule', () => {
  it('names: required, letters only, 80 at most', () => {
    expect(codes({ ...FAMILY, p2_given: '' })).toContain('p2_given:given_required');
    expect(codes({ ...FAMILY, p2_family: '<script>' })).toContain('p2_family:name_invalid');
    expect(codes({ ...FAMILY, p2_given: 'a'.repeat(81) })).toContain('p2_given:name_invalid');
  });
  it('an up-to-16 born too early is told to choose 17 and over', () => {
    expect(codes({ ...FAMILY, p3_by: '2009', p3_bm: '6' })).toContain('p3_by:bym_too_old');
  });
  it('gives the benefit of the doubt in the birth month', () => {
    // January 2010 → 17 sometime in January 2027: accepted as up to 16.
    expect(codes({ ...FAMILY, p3_by: '2010', p3_bm: '1' })).toEqual([]);
  });
  it('an up-to-16 needs a month and a year', () => {
    expect(codes({ ...FAMILY, p3_by: '' })).toContain('p3_by:bym_required');
  });
  it('the guardian checkbox is required when a minor is listed, and only then', () => {
    expect(codes({ ...FAMILY, guardian: '' })).toContain('guardian:guardian_required');
    const adults = { ...FAMILY, p3_given: '', p3_family: '', p3_cat: '', p3_by: '', p3_bm: '', guardian: '' };
    expect(codes(adults)).toEqual([]);
  });
  it('adult, terms and early start are required', () => {
    expect(codes({ ...FAMILY, adult: '', terms: '', early: '' })).toEqual(['adult:adult_required', 'terms:terms_required', 'early:early_required']);
  });
  it('the account holder must be a listed person aged 17+, or someone else with a name', () => {
    expect(codes({ ...FAMILY, holder: 'p3' })).toContain('holder:holder_minor');
    expect(codes({ ...FAMILY, holder: 'p9' })).toContain('holder:holder_required');
    expect(codes({ ...FAMILY, holder: 'other', h_given: '', h_family: 'López' })).toContain('h_given:given_required');
    expect(codes({ ...FAMILY, holder: 'other', h_given: 'Rosa', h_family: 'López Martí' })).toEqual([]);
  });
  it('email and phone', () => {
    expect(codes({ ...FAMILY, email: '' })).toContain('email:email_required');
    expect(codes({ ...FAMILY, email: 'ana@' })).toContain('email:email_invalid');
    expect(codes({ ...FAMILY, phone: 'call me' })).toContain('phone:phone_invalid');
    expect(codes({ ...FAMILY, phone: '+34 600 000 000' })).toEqual([]);
  });
  it('the sports-centre rate: venue, age, monthly', () => {
    const sc = { ...FAMILY, period: 'monthly', p3_rate: 'sc', p3_venue: 'sant-adria' };
    expect(codes(sc)).toEqual([]);
    expect(codes({ ...sc, period: 'quarterly' })).toContain('period:sc_monthly_only');
    expect(codes({ ...sc, p3_venue: '' })).toContain('p3_venue:venue_required');
    expect(codes({ ...FAMILY, period: 'monthly', p1_rate: 'sc', p1_venue: 'sant-adria' })).toContain('p1_venue:sc_not_offered');
    // Espronceda's class is from 12: a 9-year-old is refused there.
    expect(codes({ ...sc, p3_venue: 'espronceda', p3_by: '2017' })).toContain('p3_venue:sc_min_age');
    expect(codes({ ...sc, p3_venue: 'espronceda', p3_by: '2013' })).toEqual([]);
  });
  it('a bad period', () => {
    expect(codes({ ...FAMILY, period: 'weekly' })).toContain('period:period_required');
  });
});

describe('tampering', () => {
  it('reports unknown fields, such as an amount', () => {
    expect(unknownFields({ ...FAMILY, amount: '1' })).toEqual(['amount']);
    expect(unknownFields({ ...FAMILY, p7_given: 'X' })).toEqual(['p7_given']);
    expect(unknownFields(FAMILY)).toEqual([]);
  });
});

describe('metadata', () => {
  it('fits Stripe’s limits with six people and reads back', () => {
    const six: Record<string, string> = { ...FAMILY, period: 'monthly' };
    for (let n = 4; n <= 6; n++) Object.assign(six, { [`p${n}_given`]: 'Nombre', [`p${n}_family`]: 'Apellido Apellido', [`p${n}_cat`]: 'adult', [`p${n}_rate`]: 'general' });
    const r = validate(six, NOW);
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    const priced = Pricing.price({ period: 'monthly', members: r.value.members.map((m) => ({ cat: m.cat, rate: m.rate, venue: m.venue })) }, CATALOG);
    const meta = metadata(r.value, priced.perMember, 'sid_0123456789abcdef', NOW, null);
    expect(Object.keys(meta).length).toBeLessThanOrEqual(50);
    for (const [k, v] of Object.entries(meta)) {
      expect(k.length).toBeLessThanOrEqual(40);
      expect(v.length).toBeLessThanOrEqual(500);
    }
    const back = members(meta);
    expect(back).toHaveLength(6);
    expect(back[2]).toMatchObject({ name: 'Lía García Ruiz', cat: 'youth', kind: 'family', bym: '2014-03' });
    expect(meta.withdraw_by).toBe('2027-02-03');
    expect(meta.keikogi).toBe('');
  });
  it('lists everyone for the keikogi on a quarterly plan', () => {
    const r = validate(FAMILY, NOW);
    if (!r.ok) throw new Error('invalid');
    const priced = Pricing.price({ period: 'quarterly', members: r.value.members.map((m) => ({ cat: m.cat, rate: m.rate, venue: m.venue })) }, CATALOG);
    const meta = metadata(r.value, priced.perMember, 'sid_0123456789abcdef', NOW, null);
    expect(meta.keikogi).toBe('due');
    expect(meta.keikogi_due).toBe('m1,m2,m3');
    expect(meta.holder).toBe('m1');
    expect(meta.guardian_at).toBeTruthy();
  });
  it('gives no keikogi to an invited member, who is not enrolling for the first time', () => {
    const r = validate(FAMILY, NOW);
    if (!r.ok) throw new Error('invalid');
    const priced = Pricing.price({ period: 'quarterly', members: r.value.members.map((m) => ({ cat: m.cat, rate: m.rate, venue: m.venue })) }, CATALOG);
    const meta = metadata(r.value, priced.perMember, 'sid_0123456789abcdef', NOW, 'inv_123');
    expect(meta.keikogi).toBe('');
    expect(meta.keikogi_due).toBe('');
    expect(meta.invite_id).toBe('inv_123');
  });
  it('renumbers people when the form had a gap', () => {
    const gap = { ...FAMILY, p2_given: '', p2_family: '', p2_cat: '', p2_rate: '', holder: 'p3',
      p3_cat: 'adult', p3_by: '', p3_bm: '', guardian: '' };
    const r = validate(gap, NOW);
    if (!r.ok) throw new Error(JSON.stringify(r.errors));
    const priced = Pricing.price({ period: 'quarterly', members: r.value.members.map((m) => ({ cat: m.cat, rate: m.rate, venue: m.venue })) }, CATALOG);
    const meta = metadata(r.value, priced.perMember, 'sid_0123456789abcdef', NOW, null);
    expect(members(meta).map((m) => m.slot)).toEqual([1, 2]);
    expect(meta.holder).toBe('m2');
  });
});
