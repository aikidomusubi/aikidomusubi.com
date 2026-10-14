// npm run retention -- --mode test|live [--years 4]
//
// Spec 10.3: once a year, the customers whose memberships ended longer ago
// than the retention period, so the dojo can delete them in Stripe. Invoices
// the law requires keeping stay with Stripe whatever happens to the customer.
// The period is 4 years until the advisor says otherwise (the current privacy
// policy's figure for tax). Lists only: deleting is a person's decision.
import { args, mode, stripeFor, vars } from './_cli.ts';

const a = args();
const m = mode(a);
const st = stripeFor(m, vars(m).STRIPE_SECRET_KEY);
const years = Number(typeof a.years === 'string' ? a.years : 4);
const cutoff = Date.now() / 1000 - years * 365.25 * 86400;

let n = 0;
for await (const c of st.customers.list({ limit: 100 })) {
  if (c.metadata?.source !== 'signup') continue;
  const subs = await st.subscriptions.list({ customer: c.id, status: 'all', limit: 100 });
  if (!subs.data.length) continue;
  if (subs.data.some((s) => s.status !== 'canceled' || (s.ended_at ?? 0) > cutoff)) continue;
  const last = Math.max(...subs.data.map((s) => s.ended_at ?? 0));
  console.log(`  ${c.id}  ${c.name ?? ''}  ended ${new Date(last * 1000).toISOString().slice(0, 10)}`);
  n++;
}
console.log(`\n  ${n} customer(s) past ${years} years. Delete them in the Dashboard: Customers > the customer > Delete.\n`);
