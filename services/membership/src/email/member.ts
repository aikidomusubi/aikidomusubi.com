// The eleven emails a member receives, in the order of
// docs/mockups/inscripcion-correos.html. Words from _data/membership_emails.yml;
// every value that came from a person is escaped before it reaches a template.
import type { Env } from '../env.ts';
import { CATALOG, E, M, date, esc, list, money, monthNames, periodName, periodUnit, t, time, url, venueName, type Lang } from '../data.ts';
import { peopleRows, total, type Priced } from '../household.ts';
import { Pricing, type PeriodId } from '../pricing.ts';
import { B, render, type Block } from './layout.ts';
import { send } from './send.ts';

export interface Ctx { env: Env; lang: Lang; to: string; toName: string; hello: string }
export interface Method { type: 'card' | 'sepa_debit' | string; last4?: string | null }

function methodText(m: Method | null, lang: Lang) {
  if (!m) return '';
  const c = E.common;
  const name = t(m.type === 'sepa_debit' ? c.sepa : c.card, lang);
  return m.last4 ? `${name} ${t(c.ending, lang, { last4: m.last4 })}` : name;
}

async function deliver(ctx: Ctx, tag: string, kind: string, subject: string, blocks: Block[]) {
  const { html, text } = render(ctx.lang, kind, blocks, ctx.env.SITE_ORIGIN);
  await send(ctx.env, { to: ctx.to, toName: ctx.toName, subject, html, text, tag });
}

const hello = (ctx: Ctx) => B.p(esc(t(E.common.hello, ctx.lang, { name: ctx.hello })));
const membersBtn = (ctx: Ctx) => B.button(t(E.common.btn_members, ctx.lang), url('members', ctx.lang, true, ctx.env.SITE_ORIGIN));
const link = (ctx: Ctx, kind: string) => {
  const u = url(kind, ctx.lang, true, ctx.env.SITE_ORIGIN);
  return { url: esc(u), url_text: esc(u.replace(/^https?:\/\//, '').replace(/\/$/, '')) };
};

// ---------------------------------------------------------------------------
export async function confirmation(ctx: Ctx, o: {
  people: Priced[]; period: PeriodId; signupMs: number; anchorMs: number; todayAmount: number | null;
  method: Method | null; processing: boolean; under14: boolean; keikogi: number; scVenues: string[];
  withdrawBy: number; termsVersion: string;
}) {
  const L = ctx.lang;
  const c = E.confirmation;
  const n = o.people.length;
  const amount = money(total(o.people), L);
  const months = CATALOG.periods[o.period].months;
  const blocks: Block[] = [
    hello(ctx),
    B.h(t(c.heading, L)),
    B.p(esc(t(c.intro, L))),
    B.table(peopleRows(o.people, o.period, L, t(E.common.total_per, L, { unit: periodUnit(o.period, L) })), true),
    B.h4(t(c.when_h, L)),
    B.dates([
      o.todayAmount && o.todayAmount > 0
        ? t(c.today, L, { date: date(o.signupMs, L, false), amount: money(o.todayAmount, L), first: date(o.anchorMs, L, false) })
        : t(c.today_none, L),
      t(c.first, L, { date: date(o.anchorMs, L), amount }),
      months === 1
        ? t(c.then, L, { amount })
        : t(c.then_q, L, { amount, months: monthNames(Pricing.chargeMonths(o.anchorMs, months), L) })
    ]),
    B.p(esc(t(c.method, L, { method: methodText(o.method, L) }))),
    ...(o.processing ? [B.p(esc(t(c.processing, L)))] : []),
    B.h4(t(c.todo_h, L)),
    B.p(t(c.todo, L, { resources: esc(url('resources', L, true, ctx.env.SITE_ORIGIN)) })),
    ...(o.under14 ? [B.p(esc(t(c.todo_minor, L)))] : []),
    ...(o.keikogi ? [B.p(t(c.keikogi, L, { n: o.keikogi, date: date(o.anchorMs, L) }))] : []),
    ...o.scVenues.map((v) => B.p(esc(t(c.sc_note, L, { venue: venueName(v, L) })))),
    membersBtn(ctx),
    B.h4(t(c.terms_h, L)),
    B.p(t(c.terms, L, { version: esc(o.termsVersion), ...link(ctx, 'terms') })),
    B.box(t(c.withdraw_box, L, { date: date(o.withdrawBy, L), ...link(ctx, 'withdrawal') })),
    B.small(t(c.model_form, L, { date: date(o.signupMs, L) }))
  ];
  const people = n === 1 ? t(c.people_1, L) : t(c.people_n, L, { n });
  await deliver(ctx, 'confirmation', t(c.kind, L), t(c.subject, L, { people, period: periodName(o.period, L) }), blocks);
}

export async function keikogiReady(ctx: Ctx, names: string[]) {
  const L = ctx.lang;
  const k = E.keikogi;
  await deliver(ctx, 'keikogi', t(k.kind, L), t(k.subject, L), [
    hello(ctx), B.h(t(k.heading, L)), B.p(t(k.body, L, { names: esc(list(names, L)) }))
  ]);
}

export async function renewal(ctx: Ctx, o: {
  chargeMs: number; fromMs: number; toMs: number; method: Method | null; people: Priced[]; period: PeriodId;
}) {
  const L = ctx.lang;
  const r = E.renewal;
  const amount = money(total(o.people), L);
  const d = date(o.chargeMs, L);
  await deliver(ctx, 'renewal', t(r.kind, L), t(r.subject, L, { date: date(o.chargeMs, L, false), amount }), [
    hello(ctx),
    B.h(t(r.heading, L, { date: date(o.chargeMs, L, false) })),
    B.big(amount),
    B.p(esc(t(r.charge, L, { date: d, from: date(o.fromMs, L, false), to: date(o.toMs, L), method: methodText(o.method, L) }))),
    B.p(t(r.stay, L)),
    B.p(t(r.leave, L, { date: d })),
    membersBtn(ctx),
    B.table(peopleRows(o.people, o.period, L, t(E.common.total_per, L, { unit: periodUnit(o.period, L) })), true)
  ]);
}

export async function cancelled(ctx: Ctx, endMs: number) {
  const L = ctx.lang;
  const c = E.cancelled;
  const d = date(endMs, L);
  await deliver(ctx, 'cancelled', t(c.kind, L), t(c.subject, L, { date: date(endMs, L, false) }), [
    hello(ctx), B.h(t(c.heading, L)), B.p(t(c.body, L, { date: d })), B.p(esc(t(c.undo, L, { date: d }))),
    membersBtn(ctx), B.p(esc(t(c.why, L)))
  ]);
}

export async function ended(ctx: Ctx, endMs: number) {
  const L = ctx.lang;
  const e = E.ended;
  await deliver(ctx, 'ended', t(e.kind, L), t(e.subject, L), [
    hello(ctx), B.h(t(e.heading, L)), B.p(esc(t(e.body, L, { date: date(endMs, L) }))),
    B.p(t(e.back, L, link(ctx, 'signup'))), B.small(esc(t(e.licence, L)))
  ]);
}

export async function withdrawalAck(ctx: Ctx, o: { atMs: number; name: string; email: string; statement: string; refundBy: number }) {
  const L = ctx.lang;
  const w = E.withdrawal;
  await deliver(ctx, 'withdrawal', t(w.kind, L), t(w.subject, L), [
    hello(ctx),
    B.h(t(w.heading, L)),
    B.box(esc(t(w.at, L, { date: date(o.atMs, L), time: time(o.atMs) }))),
    B.p(esc(t(w.sent, L))),
    B.box(`${esc(o.name)} · ${esc(o.email)}<br>«${esc(o.statement)}»`),
    B.p(t(w.next, L, { date: date(o.refundBy, L) })),
    B.p(esc(t(w.mistake, L)))
  ]);
}

// The withdrawal settled from the panel: the amount the acknowledgement
// promised to write with.
export async function withdrawalDone(ctx: Ctx, o: { amount: number; atMs: number }) {
  const L = ctx.lang;
  const w = E.withdrawal_done;
  const vars = { amount: money(o.amount, L), date: date(o.atMs, L) };
  await deliver(ctx, 'withdrawal_done', t(w.kind, L), t(o.amount > 0 ? w.subject : w.subject_none, L, vars), [
    hello(ctx), B.h(t(w.heading, L)), B.p(t(o.amount > 0 ? w.body : w.body_none, L, vars)),
    B.p(t(E.ended.back, L, link(ctx, 'signup'))), B.small(esc(t(E.ended.licence, L)))
  ]);
}

export async function paymentFailed(ctx: Ctx, o: { amount: number; dueMs: number; method: Method | null }) {
  const L = ctx.lang;
  const f = E.payment_failed;
  await deliver(ctx, 'payment_failed', t(f.kind, L), t(f.subject, L, { date: date(o.dueMs, L, false) }), [
    hello(ctx), B.h(t(f.heading, L)),
    B.p(t(f.body, L, { amount: money(o.amount, L), date: date(o.dueMs, L), method: esc(methodText(o.method, L)) })),
    B.p(t(f.retry, L)),
    B.button(t(f.btn, L), url('members', L, true, ctx.env.SITE_ORIGIN)),
    B.p(esc(t(f.still, L)))
  ]);
}

export async function ageChange(ctx: Ctx, o: {
  person: string; fromMs: number; before: number; after: number; totalBefore: number; totalAfter: number; period: PeriodId;
}) {
  const L = ctx.lang;
  const a = E.age_change;
  const unit = periodUnit(o.period, L);
  await deliver(ctx, 'age_change', t(a.kind, L), t(a.subject, L, { person: o.person }), [
    hello(ctx), B.h(t(a.heading, L, { person: o.person })),
    B.p(esc(t(a.body, L, { person: o.person }))),
    B.table([
      [esc(t(a.row_person, L, { person: o.person, date: date(o.fromMs, L, false) })), `${money(o.before, L)} → ${money(o.after, L)} ${esc(unit)}`],
      [esc(t(a.row_total, L)), `${money(o.totalBefore, L)} → ${money(o.totalAfter, L)} ${esc(unit)}`]
    ], true),
    B.p(esc(t(a.deleted, L)))
  ]);
}

export async function planChange(ctx: Ctx, o: {
  fromMs: number; before: { people: Priced[]; period: PeriodId }; after: { people: Priced[]; period: PeriodId }; keikogiNote: boolean;
}) {
  const L = ctx.lang;
  const p = E.plan_change;
  const d = date(o.fromMs, L, false);
  await deliver(ctx, 'plan_change', t(p.kind, L), t(p.subject, L, { date: d }), [
    hello(ctx), B.h(t(p.heading, L, { date: d })), B.p(esc(t(p.body, L, { date: d }))),
    B.h4(t(p.before, L)),
    B.table(peopleRows(o.before.people, o.before.period, L, t(E.common.total_per, L, { unit: periodUnit(o.before.period, L) })), true),
    B.h4(t(p.after, L, { date: d })),
    B.table(peopleRows(o.after.people, o.after.period, L, t(E.common.total_per, L, { unit: periodUnit(o.after.period, L) })), true),
    ...(o.keikogiNote ? [B.small(esc(t(p.keikogi_note, L)))] : [])
  ]);
}

export async function priceChange(ctx: Ctx, o: { fromMs: number; now: number; then: number; period: PeriodId }) {
  const L = ctx.lang;
  const p = E.price_change;
  const unit = periodUnit(o.period, L);
  await deliver(ctx, 'price_change', t(p.kind, L), t(p.subject, L, { date: date(o.fromMs, L) }), [
    hello(ctx), B.h(t(p.heading, L, { date: date(o.fromMs, L) })), B.p(esc(t(p.body, L))),
    B.table([
      [esc(t(p.now, L)), `${money(o.now, L)} ${esc(unit)}`],
      [esc(t(p.from, L, { date: date(o.fromMs, L) })), `${money(o.then, L)} ${esc(unit)}`]
    ], true),
    B.p(t(p.leave, L)), membersBtn(ctx)
  ]);
}

export async function invite(ctx: Ctx, o: { link: string; expiresMs: number }) {
  const L = ctx.lang;
  const i = E.invite;
  await deliver(ctx, 'invite', t(i.kind, L), t(i.subject, L), [
    hello(ctx), B.h(t(i.heading, L)), B.p(esc(t(i.body, L))),
    B.p(t(i.link, L, { date: date(o.expiresMs, L) })),
    B.button(t(i.btn, L), o.link),
    B.p(t(i.twice, L)), B.p(esc(t(i.together, L)))
  ]);
}

export { M };
