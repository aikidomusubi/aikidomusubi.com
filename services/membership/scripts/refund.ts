// npm run refund -- --mode test|live --sub sub_123 [--at 2027-01-27T21:14]
//
// What a withdrawal gives back (spec 11.3): every paid invoice split at the
// moment of the notice, the used part kept, the rest refunded. --at is the
// date and time the withdrawal was received, from the acknowledgement email;
// without it, now. Prints the figure; the refund itself is one click per
// payment in the Dashboard, so a person looks at it before money moves.
import { refundFor } from '../src/refund.ts';
import { args, die, euros, mode, stripeFor, vars } from './_cli.ts';

const a = args();
const m = mode(a);
const st = stripeFor(m, vars(m).STRIPE_SECRET_KEY);
if (typeof a.sub !== 'string') die('--sub sub_123');
const at = typeof a.at === 'string' ? Date.parse(a.at) : Date.now();
if (Number.isNaN(at)) die('--at must be a date and time, e.g. 2027-01-27T21:14');

const r = await refundFor(st, a.sub, at);
const d = (ms: number) => new Date(ms).toISOString().slice(0, 10);
console.log(`\n  withdrawal at ${new Date(at).toISOString()}\n`);
for (const l of r.lines) {
  console.log(`  ${l.invoice}  ${d(l.start)} → ${d(l.end)}  paid ${euros(l.paid)}  keep ${euros(l.keep)}  refund ${euros(l.refund)}`);
}
console.log(`\n  REFUND ${euros(r.total)}, by the same payment method, within 14 days of the notice.`);
console.log(`  Then cancel the subscription immediately: Dashboard > Subscriptions > ${a.sub} > Cancel > Immediately.\n`);
