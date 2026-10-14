/* global module */
/* Membership pricing — ONE engine for the signup page and for the server.
 *
 * The signup page loads this file to show a live total; the Cloudflare Worker
 * in services/membership imports the very same file to work out what Stripe
 * actually charges. The browser's figure is a courtesy and the server never
 * trusts it, but the two cannot disagree, because there is only one of them.
 *
 * It reads _data/fees.yml in the shape that file already has: the page gets it
 * from Liquid, the Worker from services/membership/scripts/gen-catalog.mjs.
 * There is no second price list anywhere. Change a price in fees.yml and both
 * sides move on the next build.
 *
 * THE RULES, from the spec of 14 October 2026 and /cuotas/:
 *
 *   household       one payer, one subscription, one billing period for all
 *   family          the first person pays the full fee; every other person on
 *                   the general rate pays `family.amount` less per month
 *                   (45 € a quarter, 180 € a year). The full fee goes to the
 *                   first person aged 17 or over, or to the first person up to
 *                   16 when nobody is older, so invoices are deterministic.
 *   sports centre   per person, for holders of that centre's membership: the
 *                   price in `members.rows`, that space only, monthly only. It
 *                   neither receives nor triggers the family discount: the rest
 *                   of the household is priced as if that person were not there.
 *
 * Amounts are whole euros, as in fees.yml. Stripe wants cents; the Worker and
 * the setup script multiply.
 *
 * Plain ES2015 in a UMD wrapper, because the site's scripts are not modules and
 * the Worker's bundler reads CommonJS. No dependencies.
 */
(function (root, factory) {
  'use strict';
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.MusubiPricing = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // fees.yml calls the two age groups `adults` and `children`, because
  // tools/qa.py reads those ids. Stripe's lookup keys and the subscription
  // metadata use the spec's words.
  var CAT = { adult: 'adults', youth: 'children' };
  var MAX_PEOPLE = 6;
  var DAY = 86400000;

  function PricingError(code, detail) {
    this.name = 'PricingError';
    this.code = code;
    this.detail = detail || null;
    this.message = code;
  }
  PricingError.prototype = Object.create(Error.prototype);

  // -------------------------------------------------------------------------
  // The catalogue: fees.yml, reduced to what pricing needs.
  // -------------------------------------------------------------------------
  function catalog(fees) {
    if (!fees || !fees.prices || !fees.periods || !fees.family) {
      throw new PricingError('bad_catalog');
    }
    var periods = {};
    fees.periods.forEach(function (p) { periods[p.id] = { months: p.months }; });
    var sc = {};
    ((fees.members && fees.members.rows) || []).forEach(function (r) {
      sc[r.venue] = { adult: r.adults, youth: r.children, minAge: r.min_age || 0 };
    });
    return {
      version: String(fees.catalog_version || fees.year),
      effectiveFrom: fees.effective_from || null,
      periods: periods,
      prices: fees.prices,
      family: Number(fees.family.amount),
      sc: sc
    };
  }

  function fullPrice(cat, period, who) {
    var row = cat.prices[period] && cat.prices[period][CAT[who]];
    if (!row) throw new PricingError('unknown_price', period + '/' + who);
    return Number(row.fee);
  }

  function keyPart(s) { return String(s).replace(/[^a-z0-9]+/gi, '_').toLowerCase(); }

  function lookupKey(cat, member, period, kind) {
    if (kind === 'sc') {
      return 'sc_' + keyPart(member.venue) + '_' + member.cat + '_monthly_' + cat.version;
    }
    return 'general_' + member.cat + '_' + period + '_' + kind + '_' + cat.version;
  }

  // -------------------------------------------------------------------------
  // price({ period, members: [{ cat, rate, venue }] }, catalog)
  //
  //   cat    'adult' (17 or over) | 'youth' (up to 16)
  //   rate   'general' | 'sc' (sports-centre membership; needs `venue`)
  //
  // Returns one entry per person, in the order given, and the Stripe line
  // items grouped by Price, because a subscription cannot hold the same Price
  // twice: two family-rate adults are one line with quantity 2.
  // -------------------------------------------------------------------------
  function price(sel, cat) {
    var period = sel && sel.period;
    var members = (sel && sel.members) || [];
    if (!cat.periods[period]) throw new PricingError('bad_period', period);
    if (!members.length) throw new PricingError('no_members');
    if (members.length > MAX_PEOPLE) throw new PricingError('too_many_members');

    var months = cat.periods[period].months;
    var hasSc = members.some(function (m) { return m.rate === 'sc'; });
    if (hasSc && period !== 'monthly') throw new PricingError('sc_monthly_only');

    // Who pays the full fee: the first general-rate person aged 17 or over,
    // otherwise the first general-rate person up to 16.
    var full = -1;
    members.forEach(function (m, i) {
      if (m.rate !== 'sc' && m.cat === 'adult' && full < 0) full = i;
    });
    if (full < 0) {
      members.forEach(function (m, i) {
        if (m.rate !== 'sc' && full < 0) full = i;
      });
    }

    var perMember = members.map(function (m, i) {
      if (!CAT[m.cat]) throw new PricingError('bad_category', m.cat);
      var kind, amount;
      if (m.rate === 'sc') {
        var row = cat.sc[m.venue];
        amount = row && row[m.cat];
        if (amount === undefined || amount === null) {
          throw new PricingError('sc_not_offered', m.venue + '/' + m.cat);
        }
        amount = Number(amount);
        kind = 'sc';
      } else if (m.rate === 'general' || !m.rate) {
        var base = fullPrice(cat, period, m.cat);
        kind = i === full ? 'full' : 'family';
        amount = kind === 'full' ? base : base - cat.family * months;
        if (amount <= 0) throw new PricingError('bad_family_amount');
      } else {
        throw new PricingError('bad_rate', m.rate);
      }
      return {
        slot: i + 1,
        cat: m.cat,
        rate: m.rate === 'sc' ? 'sc' : 'general',
        venue: m.rate === 'sc' ? m.venue : null,
        kind: kind,
        amount: amount,
        lookupKey: lookupKey(cat, m, period, kind)
      };
    });

    var lines = [];
    var byKey = {};
    perMember.forEach(function (p) {
      if (!byKey[p.lookupKey]) {
        byKey[p.lookupKey] = { lookupKey: p.lookupKey, quantity: 0, unitAmount: p.amount };
        lines.push(byKey[p.lookupKey]);
      }
      byKey[p.lookupKey].quantity += 1;
    });

    var total = perMember.reduce(function (s, p) { return s + p.amount; }, 0);
    return { period: period, months: months, perMember: perMember, lineItems: lines, total: total };
  }

  // The same household on every period, for the cards on step 2. A period that
  // cannot hold this household (the sports-centre rate is monthly only) comes
  // back as { available: false, reason } rather than as an error.
  function compare(members, cat) {
    var monthly = null;
    var out = {};
    Object.keys(cat.periods).forEach(function (p) {
      try {
        var r = price({ period: p, members: members }, cat);
        out[p] = { available: true, total: r.total, months: r.months, result: r };
        if (p === 'monthly') monthly = r.total;
      } catch (e) {
        if (!(e instanceof PricingError)) throw e;
        out[p] = { available: false, reason: e.code };
      }
    });
    Object.keys(out).forEach(function (p) {
      var o = out[p];
      if (o.available && monthly !== null) {
        o.base = monthly * o.months;
        o.saving = o.base - o.total;
      }
    });
    return out;
  }

  // -------------------------------------------------------------------------
  // Billing on the 5th
  //
  // The next 5th of a month at 08:00 UTC that is at least an hour away. 08:00
  // UTC is 09:00 or 10:00 in Madrid, so the charge lands on the 5th locally in
  // both halves of the year. Stripe wants the anchor inside the first billing
  // period, which a next-5th always is.
  // -------------------------------------------------------------------------
  function nextAnchor(nowMs) {
    var d = new Date(nowMs);
    var y = d.getUTCFullYear();
    var m = d.getUTCMonth();
    var a = Date.UTC(y, m, 5, 8, 0, 0);
    if (a < nowMs + 3600000) a = Date.UTC(y, m + 1, 5, 8, 0, 0);
    return a;
  }

  function addMonths(ms, n) {
    var d = new Date(ms);
    return Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + n, d.getUTCDate(),
                    d.getUTCHours(), d.getUTCMinutes(), d.getUTCSeconds());
  }

  // What today's charge comes to with proration: the share of one full period
  // between now and the anchor. Stripe computes the real figure to the second
  // and its page shows it; this one is for display, which is why the page
  // rounds it and says "about".
  function prorated(total, nowMs, anchorMs, months) {
    var start = addMonths(anchorMs, -months);
    var share = (anchorMs - nowMs) / (anchorMs - start);
    if (share < 0) share = 0;
    if (share > 1) share = 1;
    return Math.round(total * share * 100) / 100;
  }

  // The 5ths a plan is charged on after the first full one, for the sentence
  // "then every 5 May, August, November and February".
  function chargeMonths(anchorMs, months) {
    var out = [];
    var n = Math.round(12 / months);
    for (var i = 0; i < Math.min(n, 4); i++) {
      out.push(new Date(addMonths(anchorMs, months * (i + 1))).getUTCMonth());
    }
    return out;
  }

  // -------------------------------------------------------------------------
  // Age from a month and a year of birth
  //
  // With month precision the birthday itself is unknown, so in the birth month
  // the younger reading is taken: "up to 16" is accepted for somebody who may
  // or may not have turned 17 this month. The spec asks for "16 or younger
  // today"; this is that, with the benefit of the doubt where the data cannot
  // settle it.
  // -------------------------------------------------------------------------
  function minAge(birthYear, birthMonth, nowMs) {
    var d = new Date(nowMs);
    var y = d.getUTCFullYear();
    var m = d.getUTCMonth() + 1;
    var age = y - birthYear;
    if (m <= birthMonth) age -= 1;
    return age;
  }

  // The month somebody turns 17, as a UTC timestamp at its first day.
  function turns17(birthYear, birthMonth) {
    return Date.UTC(birthYear + 17, birthMonth - 1, 1);
  }

  // The calendar date in Madrid, which is the date the law counts in: a signup
  // at 00:30 on the 21st local time is the 20th in UTC.
  function madridDate(ms) {
    var parts = {};
    new Intl.DateTimeFormat('en-GB', {
      timeZone: 'Europe/Madrid', year: 'numeric', month: '2-digit', day: '2-digit'
    }).formatToParts(new Date(ms)).forEach(function (p) { parts[p.type] = p.value; });
    return { y: Number(parts.year), m: Number(parts.month), d: Number(parts.day) };
  }

  // Withdrawal: the last day, 14 calendar days after the day of signing up,
  // as a UTC midnight that only its date part should be read from.
  function withdrawalDeadline(signupMs) {
    var d = madridDate(signupMs);
    return Date.UTC(d.y, d.m - 1, d.d + 14);
  }

  return {
    PricingError: PricingError,
    MAX_PEOPLE: MAX_PEOPLE,
    DAY: DAY,
    catalog: catalog,
    price: price,
    compare: compare,
    lookupKey: lookupKey,
    nextAnchor: nextAnchor,
    addMonths: addMonths,
    prorated: prorated,
    chargeMonths: chargeMonths,
    minAge: minAge,
    turns17: turns17,
    madridDate: madridDate,
    withdrawalDeadline: withdrawalDeadline
  };
}));
