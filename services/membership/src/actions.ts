// The buttons in the admin emails (decided 14 October 2026, fix 6).
//
// The spec has the dojo mark keikogi handed over, sports-centre cards checked
// and the move to the 17-and-over price by editing Stripe metadata by hand.
// Instead, each of those is a button in the email that announces it. The
// button opens a confirmation page here; the change happens only when that
// page's own button is pressed (a POST), because mail scanners open every link
// in an email and a GET that changed something would be pressed by a robot.
//
// The link is signed (ADMIN_ACTION_KEY), expires, and works once. It carries a
// subscription id and a slot, nothing about the person.
import type Stripe from 'stripe';
import type { Env } from './env.ts';
import { flag } from './env.ts';
import { CATALOG, esc, money, periodUnit, venueName } from './data.ts';
import { randomId, sign, verify } from './crypto.ts';
import { page } from './http.ts';
import { members as metaMembers, encodeMember, slots, type MetaMember, type Meta } from './meta.ts';
import { asMembers, itemAmounts, priced, total } from './household.ts';
import { Pricing } from './pricing.ts';
import { periodEnd, priceIds, stripe, subscription } from './stripe.ts';
import { ctxFor } from './context.ts';
import * as member from './email/member.ts';
import { admin, B } from './email/admin.ts';

export type ActionKind = 'keikogi' | 'sc_ok' | 'sc_no' | 'age';
interface ActionPayload { a: ActionKind; s: string; n: number; x: number; id: string }

const LABEL: Record<ActionKind, string> = {
  keikogi: 'Keikogi entregado',
  sc_ok: 'Abono comprobado',
  sc_no: 'Abono no válido: pasar a la cuota general',
  age: 'Pasar a la cuota de 17 años o más'
};

export async function actionUrl(env: Env, a: ActionKind, sub: string, slot: number): Promise<string> {
  const token = await sign({ a, s: sub, n: slot, x: Date.now() + 45 * 86400000, id: randomId(9) }, env.ADMIN_ACTION_KEY);
  return `${env.API_ORIGIN}/admin/a?t=${encodeURIComponent(token)}`;
}

async function read(env: Env, token: string): Promise<ActionPayload | string> {
  const p = await verify<ActionPayload>(token, env.ADMIN_ACTION_KEY);
  if (!p || !p.a || !p.s || !p.id) return 'Este enlace no es válido.';
  if (p.x < Date.now()) return 'Este enlace ha caducado. Hazlo desde Stripe o espera al próximo aviso.';
  if (await env.KV.get(`act:${p.id}`)) return 'Este enlace ya se ha usado.';
  return p;
}

export async function actionPage(req: Request, env: Env): Promise<Response> {
  const u = new URL(req.url);
  const token = req.method === 'POST' ? new URLSearchParams(await req.text()).get('t') ?? '' : u.searchParams.get('t') ?? '';
  const p = await read(env, token);
  if (typeof p === 'string') return page('es', 'Aviso', `<h1>Aviso</h1><p>${esc(p)}</p>`, 400);

  const st = stripe(env);
  const sub = await subscription(st, p.s);
  const who = metaMembers(sub.metadata).find((m) => m.slot === p.n);
  if (!who) return page('es', 'Aviso', '<h1>Aviso</h1><p>Esa persona ya no está en la cuota.</p>', 404);

  if (req.method !== 'POST') {
    return page('es', LABEL[p.a], `<h1>${esc(LABEL[p.a])}</h1>
<p><b>${esc(who.name)}</b>${who.venue ? ` · ${esc(venueName(who.venue, 'es'))}` : ''}</p>
<p>${esc(explain(p.a))}</p>
<form method="post"><input type="hidden" name="t" value="${esc(token)}"><button type="submit">Confirmar</button></form>`);
  }

  await env.KV.put(`act:${p.id}`, '1', { expirationTtl: 50 * 86400 });
  const done = await apply(env, st, sub, who, p.a);
  return page('es', 'Hecho', `<h1>Hecho</h1><p class="ok">${esc(done)}</p>`);
}

function explain(a: ActionKind): string {
  switch (a) {
    case 'keikogi': return 'Marca el keikogi de esta persona como entregado.';
    case 'sc_ok': return 'Marca el abono municipal como comprobado. La cuota no cambia.';
    case 'sc_no': return 'Pasa a esta persona a la cuota general desde el próximo cobro, recalcula el descuento familiar y avisa a la familia por correo.';
    case 'age': return 'Pasa a esta persona a la cuota de 17 años o más desde el próximo cobro, recalcula el descuento familiar, borra su fecha de nacimiento y avisa a la familia por correo.';
  }
}

export async function apply(env: Env, st: Stripe, sub: Stripe.Subscription, who: MetaMember, a: ActionKind): Promise<string> {
  const meta: Meta = { ...sub.metadata };
  if (a === 'keikogi') {
    const left = slots(meta.keikogi_due).filter((s) => s !== `m${who.slot}`);
    await st.subscriptions.update(sub.id, { metadata: { keikogi_due: left.join(','), keikogi: left.length ? meta.keikogi : 'delivered' } });
    return `Keikogi de ${who.name}: entregado.${left.length ? ` Quedan ${left.length}.` : ' No queda ninguno.'}`;
  }
  if (a === 'sc_ok') {
    await st.subscriptions.update(sub.id, { metadata: encodeMember({ ...who, sc: 'verified' }) });
    return `Abono de ${who.name}: comprobado.`;
  }
  // The two that change the price: recompute the household with the shared
  // engine, swap the items from the next charge, and tell the family.
  const people = metaMembers(meta).map((m) => (m.slot !== who.slot ? m
    : a === 'age' ? { ...m, cat: 'adult' as const, bym: null }
    : { ...m, rate: 'general' as const, venue: null, sc: null }));
  const { before, after } = await rehouse(env, st, sub, people);
  const ctx = ctxFor(env, sub);
  if (ctx) {
    if (a === 'age') {
      const b = before.find((x) => x.slot === who.slot)!;
      const n = after.find((x) => x.slot === who.slot)!;
      await member.ageChange(ctx, {
        person: who.name.split(' ')[0], fromMs: periodEnd(sub), before: b.amount, after: n.amount,
        totalBefore: total(before), totalAfter: total(after), period: meta.period as never
      });
    } else {
      await member.planChange(ctx, {
        fromMs: periodEnd(sub), before: { people: before, period: meta.period as never },
        after: { people: after, period: meta.period as never }, keikogiNote: false
      });
    }
  }
  const unit = periodUnit(meta.period, 'es');
  return `${who.name}: ${a === 'age' ? 'cuota de 17 o más' : 'cuota general'} desde el próximo cobro. Total ${money(total(before), 'es')} → ${money(total(after), 'es')} ${unit}. La familia ya tiene el correo.`;
}

// Re-price a household on the same billing period and replace the
// subscription's items from the next charge on, with no proration: the period
// already paid stays as it was. Used by the admin buttons, the plan CLI and
// the automatic age change.
export async function rehouse(_env: Env, st: Stripe, sub: Stripe.Subscription, people: MetaMember[]) {
  const meta = sub.metadata;
  const before = priced(meta, itemAmounts(sub));
  const res = Pricing.price({ period: meta.period, members: asMembers(people) }, CATALOG);
  const ids = await priceIds(st, res.lineItems.map((l) => l.lookupKey));
  const newMeta: Meta = { catalog_version: CATALOG.version };
  people.forEach((p, i) => Object.assign(newMeta, encodeMember({ ...p, kind: res.perMember[i].kind })));
  await st.subscriptions.update(sub.id, {
    items: [
      ...sub.items.data.map((it) => ({ id: it.id, deleted: true as const })),
      ...res.lineItems.map((l) => ({ price: ids[l.lookupKey], quantity: l.quantity }))
    ],
    proration_behavior: 'none',
    metadata: newMeta
  });
  const after = people.map((p, i) => ({ ...p, kind: res.perMember[i].kind, amount: res.perMember[i].amount }));
  return { before, after };
}

// Spec 8.3's optional mode: AUTO_AGE_UPGRADE=true makes the monthly job do
// what the "age" button does, unattended.
export const autoAge = (env: Env) => flag(env.AUTO_AGE_UPGRADE);

export async function notifyKeikogiReady(env: Env, st: Stripe, sub: Stripe.Subscription) {
  const people = metaMembers(sub.metadata);
  const due = slots(sub.metadata.keikogi_due);
  const who = people.filter((p) => due.includes(`m${p.slot}`));
  if (!who.length) return;
  const ctx = ctxFor(env, sub);
  if (ctx) await member.keikogiReady(ctx, who.map((p) => p.name.split(' ')[0]));
  const items = await Promise.all(who.map(async (p) => ({
    title: `Keikogi para ${p.name}`,
    action: { label: 'Entregado', href: await actionUrl(env, 'keikogi', sub.id, p.slot) }
  })));
  const { todo, dashboard } = await import('./email/admin.ts');
  await admin(env, `Keikogi listos para entregar: ${who.map((p) => p.name.split(' ')[0]).join(', ')}`, 'Keikogi', [
    B.h('Keikogi listos para entregar'),
    B.p('Se ha cobrado el primer periodo completo y han pasado los 14 días para desistir. La familia ya tiene un correo que le pide las tallas.'),
    todo(items),
    B.button('Abrir en Stripe', dashboard(env, `subscriptions/${sub.id}`))
  ], 'keikogi');
  await st.subscriptions.update(sub.id, { metadata: { keikogi: 'ready' } });
}
