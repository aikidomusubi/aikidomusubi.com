// The pricing engine (spec 14.1): the four worked examples from /cuotas/,
// every category × period × full/family, the sports-centre rules, and every
// household size.
import { describe, expect, it } from 'vitest';
import { CATALOG } from '../src/data.ts';
import { Pricing, type Member } from '../src/pricing.ts';

const A: Member = { cat: 'adult', rate: 'general' };
const Y: Member = { cat: 'youth', rate: 'general' };
const total = (period: string, members: Member[]) => Pricing.price({ period, members }, CATALOG).total;

describe('the four examples on /cuotas/', () => {
  it('two adults, monthly = 63 €', () => expect(total('monthly', [A, A])).toBe(63));
  it('one adult and one up to 16 = 53 €', () => expect(total('monthly', [A, Y])).toBe(53));
  it('two up to 16 = 43 €', () => expect(total('monthly', [Y, Y])).toBe(43));
  it('two adults and one up to 16 = 77 €', () => expect(total('monthly', [A, A, Y])).toBe(77));
});

describe('every category × period × full/family', () => {
  const table: [string, Member, number, number][] = [
    ['monthly', A, 39, 24], ['quarterly', A, 99, 54], ['annual', A, 360, 180],
    ['monthly', Y, 29, 14], ['quarterly', Y, 75, 30], ['annual', Y, 270, 90]
  ];
  for (const [period, m, full, fam] of table) {
    it(`${m.cat} ${period}: ${full} full, ${fam} family`, () => {
      const r = Pricing.price({ period, members: [m, m] }, CATALOG);
      expect(r.perMember.map((p) => [p.kind, p.amount])).toEqual([['full', full], ['family', fam]]);
    });
  }
});

describe('who pays the full fee', () => {
  it('is the first adult, wherever the adult is listed', () => {
    const r = Pricing.price({ period: 'monthly', members: [Y, A] }, CATALOG);
    expect(r.perMember.map((p) => p.kind)).toEqual(['family', 'full']);
    expect(r.total).toBe(53);
  });
  it('is the first up-to-16 when nobody is older', () => {
    expect(Pricing.price({ period: 'monthly', members: [Y, Y, Y] }, CATALOG).perMember.map((p) => p.kind))
      .toEqual(['full', 'family', 'family']);
  });
});

describe('line items', () => {
  it('group by Stripe price with a quantity', () => {
    const r = Pricing.price({ period: 'quarterly', members: [A, A, A, Y] }, CATALOG);
    expect(r.lineItems).toEqual([
      { lookupKey: 'general_adult_quarterly_full_2027', quantity: 1, unitAmount: 99 },
      { lookupKey: 'general_adult_quarterly_family_2027', quantity: 2, unitAmount: 54 },
      { lookupKey: 'general_youth_quarterly_family_2027', quantity: 1, unitAmount: 30 }
    ]);
    expect(r.total).toBe(99 + 54 + 54 + 30);
  });
});

describe('the sports-centre rate', () => {
  const ESP_A: Member = { cat: 'adult', rate: 'sc', venue: 'espronceda' };
  const ESP_Y: Member = { cat: 'youth', rate: 'sc', venue: 'espronceda' };
  const MAR_Y: Member = { cat: 'youth', rate: 'sc', venue: 'sant-adria' };
  const MAR_A: Member = { cat: 'adult', rate: 'sc', venue: 'sant-adria' };

  it('prices 19 and 9 at Espronceda, 9 at Marina-Besòs', () => {
    expect(total('monthly', [ESP_A])).toBe(19);
    expect(total('monthly', [ESP_Y])).toBe(9);
    expect(total('monthly', [MAR_Y])).toBe(9);
  });
  it('is monthly only', () => {
    expect(() => Pricing.price({ period: 'quarterly', members: [MAR_Y] }, CATALOG)).toThrow('sc_monthly_only');
  });
  it('is not offered to adults at Marina-Besòs', () => {
    expect(() => Pricing.price({ period: 'monthly', members: [MAR_A] }, CATALOG)).toThrow('sc_not_offered');
  });
  it('neither receives nor triggers the family discount', () => {
    // Lía on the Marina rate: Ana full, Marc family, Lía 9 → 72 (the mockup's case)
    expect(total('monthly', [A, A, MAR_Y])).toBe(39 + 24 + 9);
    // An adult on the CxEM rate and one child on the general: the child is the
    // household's first general member and pays the full 29.
    const r = Pricing.price({ period: 'monthly', members: [ESP_A, Y] }, CATALOG);
    expect(r.perMember.map((p) => [p.kind, p.amount])).toEqual([['sc', 19], ['full', 29]]);
  });
  it('has its own lookup keys', () => {
    expect(Pricing.price({ period: 'monthly', members: [MAR_Y] }, CATALOG).lineItems[0].lookupKey)
      .toBe('sc_sant_adria_youth_monthly_2027');
  });
});

describe('household size', () => {
  for (let n = 1; n <= 6; n++) {
    it(`${n} adult${n > 1 ? 's' : ''}, monthly = ${39 + 24 * (n - 1)} €`, () => {
      expect(total('monthly', Array(n).fill(A))).toBe(39 + 24 * (n - 1));
    });
  }
  it('refuses a seventh person and an empty household', () => {
    expect(() => total('monthly', Array(7).fill(A))).toThrow('too_many_members');
    expect(() => total('monthly', [])).toThrow('no_members');
  });
});

describe('compare: the step-2 cards', () => {
  it('gives the household total, base and saving per period', () => {
    const c = Pricing.compare([A, A, Y], CATALOG);
    expect(c.monthly).toMatchObject({ available: true, total: 77, saving: 0 });
    expect(c.quarterly).toMatchObject({ available: true, total: 183, base: 231, saving: 48 });
    expect(c.annual).toMatchObject({ available: true, total: 630, base: 924, saving: 294 });
  });
  it('marks quarterly and annual unavailable when someone is on a sports-centre rate', () => {
    const c = Pricing.compare([A, A, { cat: 'youth', rate: 'sc', venue: 'sant-adria' }], CATALOG);
    expect(c.monthly.total).toBe(72);
    expect(c.quarterly).toMatchObject({ available: false, reason: 'sc_monthly_only' });
  });
});

// ---------------------------------------------------------------------------
describe('the billing anchor: the next 5th at 08:00 UTC, at least an hour away', () => {
  const at = (iso: string) => new Date(Pricing.nextAnchor(Date.parse(iso))).toISOString();
  it('on the 4th', () => expect(at('2027-01-04T12:00:00Z')).toBe('2027-01-05T08:00:00.000Z'));
  it('on the 5th, before 07:00 UTC', () => expect(at('2027-01-05T06:30:00Z')).toBe('2027-01-05T08:00:00.000Z'));
  it('on the 5th, less than an hour before', () => expect(at('2027-01-05T07:30:00Z')).toBe('2027-02-05T08:00:00.000Z'));
  it('on the 5th, after 08:00', () => expect(at('2027-01-05T09:00:00Z')).toBe('2027-02-05T08:00:00.000Z'));
  it('on the 31st', () => expect(at('2027-01-31T22:00:00Z')).toBe('2027-02-05T08:00:00.000Z'));
  it('at the end of February, leap year and not', () => {
    expect(at('2027-02-28T10:00:00Z')).toBe('2027-03-05T08:00:00.000Z');
    expect(at('2028-02-29T10:00:00Z')).toBe('2028-03-05T08:00:00.000Z');
  });
  it('in December', () => expect(at('2027-12-20T10:00:00Z')).toBe('2028-01-05T08:00:00.000Z'));
  it('lands on the 5th in Madrid on both sides of daylight saving', () => {
    for (const iso of ['2027-03-20T10:00:00Z', '2027-10-20T10:00:00Z', '2027-03-28T00:30:00Z', '2027-10-31T00:30:00Z']) {
      const a = Pricing.nextAnchor(Date.parse(iso));
      expect(Pricing.madridDate(a).d).toBe(5);
    }
  });
});

describe('proration', () => {
  it('charges the share of a full period up to the anchor', () => {
    const now = Date.parse('2027-01-20T18:00:00Z');
    const anchor = Pricing.nextAnchor(now);
    const p = Pricing.prorated(77, now, anchor, 1);
    expect(p).toBeGreaterThan(38);
    expect(p).toBeLessThan(39.5);
    expect(Pricing.prorated(183, now, anchor, 3)).toBeCloseTo(183 * ((anchor - now) / (anchor - Pricing.addMonths(anchor, -3))), 2);
  });
  it('never exceeds the full amount', () => {
    const now = Date.parse('2027-01-05T09:00:00Z');
    expect(Pricing.prorated(39, now, Pricing.nextAnchor(now), 1)).toBeLessThanOrEqual(39);
  });
  it('lists the charge months after the first full one', () => {
    const anchor = Date.parse('2027-02-05T08:00:00Z');
    expect(Pricing.chargeMonths(anchor, 3)).toEqual([4, 7, 10, 1]); // May, Aug, Nov, Feb
    expect(Pricing.chargeMonths(anchor, 12)).toEqual([1]);
  });
});

describe('dates and ages', () => {
  it('counts the 14 days in Madrid, not in UTC', () => {
    // 00:30 on the 21st in Madrid is still the 20th in UTC.
    const d = Pricing.withdrawalDeadline(Date.parse('2027-01-20T23:30:00Z'));
    expect(new Date(d).toISOString().slice(0, 10)).toBe('2027-02-04');
    const e = Pricing.withdrawalDeadline(Date.parse('2027-01-20T18:04:00Z'));
    expect(new Date(e).toISOString().slice(0, 10)).toBe('2027-02-03');
  });
  it('takes the younger reading in the birth month', () => {
    const now = Date.parse('2026-10-14T10:00:00Z');
    expect(Pricing.minAge(2010, 3, now)).toBe(16);   // turned 16 in March
    expect(Pricing.minAge(2009, 10, now)).toBe(16);  // 17 this month, maybe not yet
    expect(Pricing.minAge(2009, 9, now)).toBe(17);
  });
});
