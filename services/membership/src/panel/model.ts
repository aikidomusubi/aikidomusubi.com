// What the panel shows, worked out from Stripe's subscriptions. Pure functions
// of the subscription and the date, so the tests can run them on fixtures and
// the pages never have to know Stripe's shapes.
import type Stripe from 'stripe';
import { CATALOG, date, venueName } from '../data.ts';
import { members as metaMembers, slots, type MetaMember } from '../meta.ts';
import { itemAmounts, priced, total } from '../household.ts';
import { Pricing, type PeriodId } from '../pricing.ts';
import { customerOf, method, periodEnd } from '../stripe.ts';
import { inWindow, withdrawalAt } from '../withdraw.ts';

export type Keikogi = 'none' | 'later' | 'ready' | 'delivered';

export interface Person extends MetaMember {
  first: string;
  amount: number;
  paper: 'due' | 'done' | 'none';     // none: moved over by invite, the dojo has it
  keikogi: Keikogi;
  ageFrom: number | null;             // the charge from which the 17+ fee applies, when it is due now
}

export type Status = 'ok' | 'failed' | 'ending' | 'ended';
export type EndReason = 'withdrawal' | 'baja' | 'impago';

export interface Family {
  id: string;
  customerId: string;
  name: string;                       // "Familia García", or the one person's name
  holder: string;
  email: string;
  phone: string;
  period: PeriodId;
  total: number;
  next: number;                       // next charge, ms
  method: string;                     // "Domiciliación SEPA" / "Tarjeta"
  status: Status;
  failedAmount: number | null;
  endsAt: number | null;
  created: number;
  invited: boolean;
  keikogiFrom: number | null;         // when the keikogi becomes due, while it is not yet
  withdrawalAt: number | null;        // a withdrawal request waiting to be settled
  withdrawalInWindow: boolean;        // within the 14 days; after them it is a cancellation
  ended: number | null;               // a former membership: when it ended, and why
  endReason: EndReason | null;
  refunded: number | null;            // what a settled withdrawal gave back
  before: { from: number; to: number }[];  // earlier memberships of the same customer
  people: Person[];
}

export type TaskKind = 'withdrawal' | 'paper' | 'keikogi' | 'sc' | 'age' | 'money';
export interface Task { kind: TaskKind; fam: Family; person: Person | null; since: number }

const LIVE: Stripe.Subscription.Status[] = ['active', 'trialing', 'past_due', 'unpaid', 'incomplete'];
export const isCurrent = (s: Stripe.Subscription) => Boolean(s.metadata?.signup_id) && LIVE.includes(s.status);
// A membership that was running and has ended. Not incomplete_expired: that is
// a first payment that never went through, which was never a membership.
export const isFormer = (s: Stripe.Subscription) => Boolean(s.metadata?.signup_id) && s.status === 'canceled';

export function familyName(people: MetaMember[], hello: string, customer: string): string {
  if (people.length < 2) return people[0]?.name || customer;
  // The names are "given family". `hello` is the holder's given name, which
  // is how the surname is found when the given name has two words.
  const holder = people.find((p) => hello && p.name.startsWith(hello + ' ')) ?? people[0];
  const rest = hello && holder.name.startsWith(hello + ' ') ? holder.name.slice(hello.length + 1) : holder.name.split(' ').slice(1).join(' ');
  const surname = rest.split(' ')[0];
  return surname ? `Familia ${surname}` : customer || holder.name;
}

export function family(sub: Stripe.Subscription): Family {
  const meta = sub.metadata;
  const cust = customerOf(sub);
  const amounts = priced(meta, itemAmounts(sub));
  const next = periodEnd(sub);
  const paperDue = slots(meta.paper_due);
  const kDue = slots(meta.keikogi_due);
  const k = meta.keikogi ?? '';
  const hasPaper = 'paper_due' in meta;
  const people: Person[] = metaMembers(meta).map((m, i) => {
    let ageFrom: number | null = null;
    if (m.bym && m.cat === 'youth') {
      const [y, mo] = m.bym.split('-').map(Number);
      // Only the month of birth is known, so the new fee starts with the first
      // charge in a month AFTER the birthday month: never early (as cron.ts).
      const from = Pricing.addMonths(Pricing.turns17(y, mo), 1);
      if (from <= next) ageFrom = next;
    }
    const keikogi: Keikogi = !k ? 'none'
      : k === 'due' || k === 'paid' ? (kDue.includes(`m${m.slot}`) ? 'later' : 'none')
      : kDue.includes(`m${m.slot}`) ? 'ready' : 'delivered';
    return {
      ...m, first: m.name.split(' ')[0], amount: amounts[i]?.amount ?? NaN,
      paper: !hasPaper || meta.invite_id ? 'none' : paperDue.includes(`m${m.slot}`) ? 'due' : 'done',
      keikogi, ageFrom
    };
  });
  const inv = sub.latest_invoice && typeof sub.latest_invoice !== 'string' ? sub.latest_invoice : null;
  const failed = ['past_due', 'unpaid', 'incomplete'].includes(sub.status)
    || Boolean(inv && inv.status === 'open' && (inv.attempt_count ?? 0) > 0);
  const endsAt = sub.cancel_at ? sub.cancel_at * 1000 : sub.cancel_at_period_end ? next : null;
  const pm = method(sub);
  // The keikogi becomes due with the first full charge (the anchor) once the
  // 14 days to withdraw are over too.
  const withdrawEnd = meta.withdraw_by ? Date.parse(meta.withdraw_by + 'T12:00:00Z') + 86400000 : 0;
  const wd = sub.status === 'canceled' || meta.withdrawal_done ? null : withdrawalAt(sub);
  const ended = sub.status === 'canceled' ? (sub.ended_at ?? sub.canceled_at ?? sub.created) * 1000 : null;
  const endReason: EndReason | null = !ended ? null
    : meta.withdrawal_done ? 'withdrawal'
    : sub.cancellation_details?.reason === 'payment_failed' ? 'impago' : 'baja';
  return {
    id: sub.id,
    customerId: cust?.id ?? (typeof sub.customer === 'string' ? sub.customer : ''),
    name: familyName(metaMembers(meta), meta.hello ?? '', cust?.name ?? ''),
    holder: cust?.name ?? '',
    email: cust?.email ?? '',
    phone: cust?.phone ?? '',
    period: (meta.period as PeriodId) || 'monthly',
    total: total(amounts),
    next,
    method: pm?.type === 'sepa_debit' ? 'Domiciliación SEPA' : pm?.type === 'card' ? 'Tarjeta' : '',
    status: ended ? 'ended' : failed ? 'failed' : endsAt ? 'ending' : 'ok',
    failedAmount: failed && inv ? inv.amount_due / 100 : null,
    endsAt,
    created: sub.created * 1000,
    invited: Boolean(meta.invite_id),
    keikogiFrom: !ended && (k === 'due' || k === 'paid') ? Math.max(sub.billing_cycle_anchor * 1000, withdrawEnd) : null,
    withdrawalAt: wd,
    withdrawalInWindow: wd != null && inWindow(sub, wd),
    ended,
    endReason,
    refunded: meta.withdrawal_refund ? Number(meta.withdrawal_refund) : null,
    before: [],
    people
  };
}

// Who has been a member before: each current membership learns the earlier
// ones of the same Stripe customer (a returning member signs up with the same
// email, and checkout.ts reuses the customer).
export function linkReturning(current: Family[], former: Family[]) {
  for (const f of current) {
    f.before = former.filter((x) => x.customerId && x.customerId === f.customerId)
      .map((x) => ({ from: x.created, to: x.ended! })).sort((a, b) => a.from - b.from);
  }
}

// The to-do list, in the order the page shows it.
export function tasks(fams: Family[]): Task[] {
  const out: Task[] = [];
  for (const f of fams) {
    if (f.withdrawalAt) out.push({ kind: 'withdrawal', fam: f, person: null, since: f.withdrawalAt });
    // A family that is withdrawing needs no forms collected or keikogi handed over.
    const leaving = f.withdrawalAt != null && f.withdrawalInWindow;
    for (const p of leaving ? [] : f.people) {
      if (p.paper === 'due') out.push({ kind: 'paper', fam: f, person: p, since: f.created });
      if (p.keikogi === 'ready') out.push({ kind: 'keikogi', fam: f, person: p, since: f.created });
      if (p.sc === 'pending') out.push({ kind: 'sc', fam: f, person: p, since: f.created });
      if (p.ageFrom) out.push({ kind: 'age', fam: f, person: p, since: p.ageFrom });
    }
    if (f.status === 'failed') out.push({ kind: 'money', fam: f, person: null, since: f.created });
  }
  // Oldest first within a kind: what has waited longest is the most urgent.
  return out.sort((a, b) => a.since - b.since);
}

// Short descriptions used in more than one place.
export const PERIOD: Record<string, string> = { monthly: 'Mensual', quarterly: 'Trimestral', annual: 'Anual' };
export const UNIT: Record<string, string> = { monthly: 'al mes', quarterly: 'al trimestre', annual: 'al año' };
export const periodWord: Record<string, string> = { monthly: 'mes', quarterly: 'trimestre', annual: 'año' };

export function feeLabel(p: Person): string {
  const age = p.cat === 'adult' ? '17 o más' : 'Hasta 16';
  const kind = p.kind === 'full' ? 'completa' : p.kind === 'family' ? 'familia' : `abono ${venueName(p.venue, 'es')}`;
  return `${age} · ${kind}`;
}

export function ago(ms: number, now = Date.now()): string {
  const days = Math.floor((now - ms) / 86400000);
  if (days <= 0) return 'hoy';
  if (days === 1) return 'ayer';
  if (days < 14) return `hace ${days} días`;
  if (days < 60) return `hace ${Math.round(days / 7)} semanas`;
  return `hace ${Math.round(days / 30)} meses`;
}

export const short = (ms: number) => date(ms, 'es', false);

export function months(period: string) { return CATALOG.periods[period]?.months ?? 1; }
