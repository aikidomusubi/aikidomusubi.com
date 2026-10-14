// Server-side validation of a signup (spec 6.2).
//
// The form arrives as flat fields — the page posts the same names with or
// without JavaScript — and leaves as a typed signup or a list of errors, each
// tied to the id of the field it belongs to so the page can put it there.
// Error codes are keys of `errors` in _data/membership.yml: the server and the
// page say the same words.
import { CATALOG, isLang, type Lang, M } from './data.ts';
import { Pricing, isPricingError, type Cat, type Member, type PeriodId, type Rate } from './pricing.ts';

export interface Person {
  slot: number;
  given: string;
  family: string;
  cat: Cat;
  rate: Rate;
  venue: string | null;
  birth: { y: number; m: number } | null;
}

export interface Signup {
  lang: Lang;
  period: PeriodId;
  members: Person[];
  holder: { slot: number | null; given: string; family: string };
  email: string;
  phone: string;
  minors: boolean;
  invite: string | null;
  sid: string;
}

export interface FieldError { field: string; code: string }

const MAX = Number(M.max_people) || 6;
const PERSON_KEYS = ['given', 'family', 'cat', 'bm', 'by', 'rate', 'venue'];
const TOP_KEYS = ['lang', 'period', 'holder', 'h_given', 'h_family', 'email', 'phone',
  'adult', 'guardian', 'terms', 'early', 'website', 'invite', 'sid', 'step'];

export const KNOWN = new Set<string>([
  ...TOP_KEYS,
  ...Array.from({ length: MAX }, (_, i) => PERSON_KEYS.map((k) => `p${i + 1}_${k}`)).flat()
]);

// Letters in any script (Japanese included), combining marks, spaces,
// apostrophes, hyphens, the full stop of an initial, and the katakana middle
// dot that joins a compound given name (ジョアン・マネル).
const NAME = /^[\p{L}\p{M}](?:[\p{L}\p{M}\s'’.\-・·]*[\p{L}\p{M}.])?$/u;
const EMAIL = /^[^\s@<>()",;]+@[^\s@<>()",;]+\.[^\s@<>()",;]{2,}$/;
const PHONE = /^\+?[0-9][0-9 ().-]{5,22}$/;
const on = (v: string | undefined) => v === 'on' || v === 'true' || v === '1';
const clean = (v: string | undefined) => (v ?? '').normalize('NFC').replace(/\s+/g, ' ').trim();

export function unknownFields(body: Record<string, string>): string[] {
  return Object.keys(body).filter((k) => !KNOWN.has(k));
}

export function validate(body: Record<string, string>, nowMs: number):
  { ok: true; value: Signup } | { ok: false; errors: FieldError[]; lang: Lang } {
  const errors: FieldError[] = [];
  const err = (field: string, code: string) => errors.push({ field, code });
  const lang: Lang = isLang(body.lang) ? body.lang : 'es';

  // Who trains. Person 1 always exists; the others exist once anything of
  // theirs has been filled in, which is how the no-JS form's closed blocks
  // for persons 2 to 6 come through: empty, and ignored.
  const members: Person[] = [];
  for (let n = 1; n <= MAX; n++) {
    const f = (k: string) => clean(body[`p${n}_${k}`]);
    const present = n === 1 || ['given', 'family', 'cat'].some((k) => f(k) !== '');
    if (!present) continue;
    const id = (k: string) => `p${n}_${k}`;

    const given = f('given');
    const family = f('family');
    if (!given) err(id('given'), 'given_required');
    else if (given.length > 80 || !NAME.test(given)) err(id('given'), 'name_invalid');
    if (!family) err(id('family'), 'family_required');
    else if (family.length > 80 || !NAME.test(family)) err(id('family'), 'name_invalid');

    const cat = f('cat') as Cat;
    if (cat !== 'adult' && cat !== 'youth') err(id('cat'), 'cat_required');

    let birth: Person['birth'] = null;
    if (cat === 'youth') {
      const y = Number(f('by'));
      const m = Number(f('bm'));
      const thisYear = new Date(nowMs).getUTCFullYear();
      if (!Number.isInteger(y) || !Number.isInteger(m) || m < 1 || m > 12 || y < thisYear - 30 || y > thisYear) {
        err(id('by'), 'bym_required');
      } else if (Date.UTC(y, m - 1, 1) > nowMs) {
        err(id('by'), 'bym_future');
      } else if (Pricing.minAge(y, m, nowMs) > 16) {
        err(id('by'), 'bym_too_old');
      } else {
        birth = { y, m };
      }
    }

    const rate = (f('rate') || 'general') as Rate;
    let venue: string | null = null;
    if (rate !== 'general' && rate !== 'sc') err(id('rate'), 'rate_required');
    if (rate === 'sc') {
      venue = f('venue') || null;
      const row = venue ? CATALOG.sc[venue] : undefined;
      if (!row) err(id('venue'), 'venue_required');
      else if ((cat === 'adult' || cat === 'youth') && (row[cat] === undefined || row[cat] === null)) {
        err(id('venue'), 'sc_not_offered');
      } else if (cat === 'youth' && birth && row.minAge) {
        // In the birth month itself the birthday may or may not have passed;
        // refuse only when even the older reading is too young.
        const age = Pricing.minAge(birth.y, birth.m, nowMs);
        const older = new Date(nowMs).getUTCMonth() + 1 === birth.m ? age + 1 : age;
        if (older < row.minAge) err(id('venue'), 'sc_min_age');
      }
    }
    members.push({ slot: n, given, family, cat, rate, venue, birth });
  }
  if (Object.keys(body).some((k) => /^p(\d+)_/.test(k) && Number(k.slice(1).split('_')[0]) > MAX)) {
    err('p1_given', 'too_many');
  }

  // How they pay.
  const period = body.period as PeriodId;
  if (!CATALOG.periods[period]) err('period', 'period_required');

  // Who pays. A listed person aged 17 or over, or somebody else.
  const holderRaw = clean(body.holder);
  const holder = { slot: null as number | null, given: '', family: '' };
  if (holderRaw === 'other') {
    holder.given = clean(body.h_given);
    holder.family = clean(body.h_family);
    if (!holder.given) err('h_given', 'given_required');
    else if (holder.given.length > 80 || !NAME.test(holder.given)) err('h_given', 'name_invalid');
    if (!holder.family) err('h_family', 'family_required');
    else if (holder.family.length > 80 || !NAME.test(holder.family)) err('h_family', 'name_invalid');
  } else {
    const slot = Number(holderRaw.replace(/^p/, ''));
    const p = members.find((x) => x.slot === slot);
    if (!p) err('holder', 'holder_required');
    else if (p.cat !== 'adult') err('holder', 'holder_minor');
    else { holder.slot = slot; holder.given = p.given; holder.family = p.family; }
  }

  const email = clean(body.email).toLowerCase();
  if (!email) err('email', 'email_required');
  else if (email.length > 254 || !EMAIL.test(email)) err('email', 'email_invalid');
  const phone = clean(body.phone);
  if (phone && !PHONE.test(phone)) err('phone', 'phone_invalid');

  const minors = members.some((m) => m.cat === 'youth');
  if (!on(body.adult)) err('adult', 'adult_required');
  if (minors && !on(body.guardian)) err('guardian', 'guardian_required');
  if (!on(body.terms)) err('terms', 'terms_required');
  if (!on(body.early)) err('early', 'early_required');

  // The household as a whole: what the pricing engine refuses, said in the
  // place the person can fix it.
  if (!errors.length) {
    try {
      Pricing.price({ period, members: members.map(toMember) }, CATALOG);
    } catch (e) {
      if (!isPricingError(e)) throw e;
      if (e.code === 'sc_monthly_only') err('period', 'sc_monthly_only');
      else if (e.code === 'too_many_members') err('p1_given', 'too_many');
      else err('period', 'period_required');
    }
  }

  if (errors.length) return { ok: false, errors, lang };

  const sid = /^[A-Za-z0-9_-]{16,40}$/.test(body.sid ?? '') ? body.sid : '';
  const invite = clean(body.invite) || null;
  return {
    ok: true,
    value: { lang, period, members, holder, email, phone, minors, invite, sid }
  };
}

export const toMember = (p: Person): Member => ({ cat: p.cat, rate: p.rate, venue: p.venue });
