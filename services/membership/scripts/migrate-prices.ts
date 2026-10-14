// npm run migrate-prices -- --mode test|live --to 2028 [--apply] [--notify]
//
// Spec 8.5: move every active membership to a new price list at its first
// renewal on or after the list's `effective_from`.
//
//   1. Edit _data/fees.yml: the new prices, `catalog_version` and
//      `effective_from`.
//   2. npm run stripe:setup -- --mode ...   (creates the new Prices)
//   3. npm run migrate-prices -- --mode ... --to <version>          (the list)
//   4. ... --apply --notify, at least ONE MONTH before the first switch: each
//      payer gets their own before and after (template "price_change").
//
// The switch is a subscription schedule, so the billing date stays the 5th.
import Stripe from 'stripe';
import { CATALOG, money } from '../src/data.ts';
import { Pricing, type PeriodId } from '../src/pricing.ts';
import { members as metaMembers, encodeMember, type Meta } from '../src/meta.ts';
import { itemAmounts, priced, total } from '../src/household.ts';
import { periodEnd, priceIds } from '../src/stripe.ts';
import { ctxFor } from '../src/context.ts';
import * as member from '../src/email/member.ts';
import { args, die, env, mode, stripeFor, vars } from './_cli.ts';

const a = args();
const m = mode(a);
const v = vars(m);
const st = stripeFor(m, v.STRIPE_SECRET_KEY);
const e = env(m, v);
if (typeof a.to !== 'string' || a.to !== CATALOG.version) die(`--to must be the catalog_version now in fees.yml (${CATALOG.version})`);
const effective = CATALOG.effectiveFrom ? Date.parse(CATALOG.effectiveFrom + 'T00:00:00Z') : Date.now();
let warned = false;

for await (const sub of st.subscriptions.list({ status: 'active', limit: 100, expand: ['data.customer'] })) {
  const meta = sub.metadata as Meta;
  if (!meta.signup_id || meta.catalog_version === CATALOG.version) continue;
  const period = meta.period as PeriodId;
  const months = CATALOG.periods[period].months;
  let at = periodEnd(sub);
  while (at < effective) at = Pricing.addMonths(at, months);
  const people = metaMembers(meta);
  const res = Pricing.price({ period, members: people.map((p) => ({ cat: p.cat, rate: p.rate, venue: p.venue })) }, CATALOG);
  const before = total(priced(meta, itemAmounts(sub)));
  const name = (sub.customer as Stripe.Customer)?.name ?? sub.id;
  console.log(`  ${name.padEnd(30)} ${money(before, 'es').padStart(9)} → ${money(res.total, 'es').padStart(9)}  from ${new Date(at).toISOString().slice(0, 10)}`);
  if (!warned && at - Date.now() < 31 * 86400000) { console.log('  WARNING: less than a month before the switch: the notice is late.'); warned = true; }
  if (!a.apply) continue;

  const ids = await priceIds(st, res.lineItems.map((l) => l.lookupKey));
  const newMeta: Meta = { catalog_version: CATALOG.version };
  people.forEach((p, i) => Object.assign(newMeta, encodeMember({ ...p, kind: res.perMember[i].kind })));
  const sched = await st.subscriptionSchedules.create({ from_subscription: sub.id });
  const p0 = sched.phases[0];
  await st.subscriptionSchedules.update(sched.id, {
    end_behavior: 'release',
    phases: [
      { items: p0.items.map((it) => ({ price: typeof it.price === 'string' ? it.price : it.price.id, quantity: it.quantity })),
        start_date: p0.start_date, end_date: Math.floor(at / 1000) },
      { items: res.lineItems.map((l) => ({ price: ids[l.lookupKey], quantity: l.quantity })),
        proration_behavior: 'none', metadata: { ...meta, ...newMeta } as Stripe.MetadataParam }
    ]
  });
  if (a.notify) {
    const ctx = ctxFor(e, sub);
    if (ctx) await member.priceChange(ctx, { fromMs: at, now: before, then: res.total, period });
  }
}
if (!a.apply) console.log('\n  (dry run: add --apply, and --notify to email each payer)\n');
