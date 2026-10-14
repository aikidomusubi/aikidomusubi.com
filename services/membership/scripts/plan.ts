// npm run plan -- --people adult,adult,youth [--period quarterly]
//     Prints what a household costs on every period. No Stripe needed.
//
// npm run plan -- --mode test|live --sub sub_123 [--people SPEC] [--period P] [--apply] [--notify]
//     Changes a membership from its next charge (spec 8.6): different people,
//     a different period, or both. Without --apply it only shows the change.
//
// SPEC, for an existing membership, names everybody who will be in it:
//     "Ana García López:adult,Marc García López:adult,Lía García Ruiz:youth:2014-03"
//     "Joan Puig:adult:sc:espronceda"
// Without names (adult,youth) it only prices.
//
// A different PERIOD is applied with a subscription schedule at the end of the
// period already paid, so the billing date stays on the 5th. Changing the
// period in the Dashboard instead resets the billing date to the day of the
// change: that is why this exists.
import Stripe from 'stripe';
import { CATALOG, money, periodName } from '../src/data.ts';
import { Pricing, type Cat, type Member, type PeriodId, type Rate } from '../src/pricing.ts';
import { members as metaMembers, encodeMember, type Meta, type MetaMember } from '../src/meta.ts';
import { itemAmounts, priced, total } from '../src/household.ts';
import { rehouse } from '../src/actions.ts';
import { periodEnd, priceIds, subscription } from '../src/stripe.ts';
import { ctxFor } from '../src/context.ts';
import * as member from '../src/email/member.ts';
import { args, die, env, mode, stripeFor, vars } from './_cli.ts';

const a = args();

interface Spec { name: string; cat: Cat; rate: Rate; venue: string | null; bym: string | null }
function parse(spec: string): Spec[] {
  return spec.split(',').map((raw) => {
    const parts = raw.trim().split(':');
    let name = '';
    if (!['adult', 'youth'].includes(parts[0])) name = parts.shift()!;
    const cat = parts.shift() as Cat;
    if (cat !== 'adult' && cat !== 'youth') die(`"${raw}": the age group must be adult or youth`);
    let rate: Rate = 'general';
    let venue: string | null = null;
    if (parts[0] === 'sc') { rate = 'sc'; parts.shift(); venue = parts.shift() ?? null; }
    const bym = parts[0] && /^\d{4}-\d{2}$/.test(parts[0]) ? parts[0] : null;
    return { name, cat, rate, venue, bym };
  });
}

const asMember = (s: Spec): Member => ({ cat: s.cat, rate: s.rate, venue: s.venue });

// --- pricing only ---------------------------------------------------------
if (!a.sub) {
  if (typeof a.people !== 'string') die('--people adult,adult,youth');
  const people = parse(a.people).map(asMember);
  const c = Pricing.compare(people, CATALOG);
  for (const [p, r] of Object.entries(c)) {
    if (!r.available) { console.log(`  ${p.padEnd(10)} not available (${r.reason})`); continue; }
    console.log(`  ${p.padEnd(10)} ${money(r.total!, 'es').padStart(9)}   saving ${money(r.saving ?? 0, 'es')}`);
    for (const l of r.result!.lineItems) console.log(`      ${l.quantity} × ${l.lookupKey}  ${money(l.unitAmount, 'es')}`);
  }
  process.exit(0);
}

// --- an existing membership ---------------------------------------------
const m = mode(a);
const v = vars(m);
const st = stripeFor(m, v.STRIPE_SECRET_KEY);
const e = env(m, v);
const sub = await subscription(st, String(a.sub));
if (!sub.metadata?.signup_id) die('that subscription was not created by the online signup');
const meta = sub.metadata as Meta;
const nowPeriod = meta.period as PeriodId;
const newPeriod = (typeof a.period === 'string' ? a.period : nowPeriod) as PeriodId;
if (!CATALOG.periods[newPeriod]) die(`unknown period ${newPeriod}`);

const current = metaMembers(meta);
let people: MetaMember[] = current;
if (typeof a.people === 'string') {
  const spec = parse(a.people);
  if (spec.some((s) => !s.name)) die('to change an existing membership, give every person a name: "Ana García:adult,..."');
  people = spec.map((s, i) => ({ slot: i + 1, name: s.name, cat: s.cat, rate: s.rate, kind: 'full', venue: s.venue,
    sc: s.rate === 'sc' ? (current.find((c) => c.name === s.name && c.sc)?.sc ?? 'pending') : null,
    bym: s.cat === 'youth' ? (s.bym ?? current.find((c) => c.name === s.name)?.bym ?? null) : null }));
}
const res = Pricing.price({ period: newPeriod, members: people.map((p) => ({ cat: p.cat, rate: p.rate, venue: p.venue })) }, CATALOG);
const before = priced(meta, itemAmounts(sub));
const after = people.map((p, i) => ({ ...p, kind: res.perMember[i].kind, amount: res.perMember[i].amount }));
const from = periodEnd(sub);

console.log(`\n  ${sub.id} · from ${new Date(from).toISOString().slice(0, 10)}`);
console.log(`  now   ${periodName(nowPeriod, 'es')}: ${before.map((p) => `${p.name} ${money(p.amount, 'es')}`).join(', ')} = ${money(total(before), 'es')}`);
console.log(`  then  ${periodName(newPeriod, 'es')}: ${after.map((p) => `${p.name} ${money(p.amount, 'es')}`).join(', ')} = ${money(total(after), 'es')}`);
const added = people.filter((p) => !current.some((c) => c.name === p.name));
if (added.length && newPeriod !== 'monthly') console.log(`  NOTE: ${added.map((p) => p.name).join(', ')} new on a ${newPeriod} plan: hand over the keikogi by hand.`);
if (!a.apply) { console.log('\n  (nothing changed: add --apply)\n'); process.exit(0); }

if (newPeriod === nowPeriod) {
  await rehouse(e, st, sub, people);
  // Slots beyond the new household are cleared.
  const clear: Meta = {};
  for (let n = people.length + 1; n <= 6; n++) if (meta[`m${n}`]) { clear[`m${n}`] = ''; clear[`m${n}_name`] = ''; }
  if (Object.keys(clear).length) await st.subscriptions.update(sub.id, { metadata: clear });
} else {
  if (people.some((p) => p.rate === 'sc') && newPeriod !== 'monthly') die('the sports-centre rate is monthly only');
  const ids = await priceIds(st, res.lineItems.map((l) => l.lookupKey));
  const newMeta: Meta = { period: newPeriod, catalog_version: CATALOG.version };
  for (let n = 1; n <= 6; n++) { newMeta[`m${n}`] = ''; newMeta[`m${n}_name`] = ''; }
  after.forEach((p) => Object.assign(newMeta, encodeMember(p)));
  const sched = await st.subscriptionSchedules.create({ from_subscription: sub.id });
  const phase0 = sched.phases[0];
  await st.subscriptionSchedules.update(sched.id, {
    end_behavior: 'release',
    phases: [
      { items: phase0.items.map((it) => ({ price: typeof it.price === 'string' ? it.price : it.price.id, quantity: it.quantity })),
        start_date: phase0.start_date, end_date: Math.floor(from / 1000) },
      { items: res.lineItems.map((l) => ({ price: ids[l.lookupKey], quantity: l.quantity })),
        proration_behavior: 'none', metadata: { ...meta, ...newMeta } as Stripe.MetadataParam }
    ]
  });
}
console.log('  applied.');
if (a.notify) {
  const ctx = ctxFor(e, await subscription(st, sub.id));
  if (ctx) {
    await member.planChange(ctx, { fromMs: from, before: { people: before, period: nowPeriod }, after: { people: after, period: newPeriod },
      keikogiNote: newPeriod !== 'monthly' && nowPeriod === 'monthly' });
    console.log(`  the payer has been emailed.`);
  }
}
