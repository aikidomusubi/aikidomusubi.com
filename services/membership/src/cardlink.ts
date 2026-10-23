// Moving a cash family to card or direct debit, through the dojo (decided 23
// October 2026).
//
// The panel's "Pasar a tarjeta o domiciliación" emails the family a link to
// /pago/tarjeta. It is signed, carries only the subscription id, and works
// for 14 days; each press makes a fresh Stripe Checkout in setup mode, so the
// family types the card or account on Stripe's page and we never see it.
// Nothing is charged there. When Stripe says it is done
// (checkout.session.completed, mode "setup"), the method is saved on the
// customer and the subscription and `method_next` is set to "card"; on the
// next 5th the daily job turns the subscription to charging automatically
// (src/cash.ts, switchToCard), with Stripe crediting what cash already paid.
import type Stripe from 'stripe';
import type { Env } from './env.ts';
import { date, esc, isLang, t, url, type Lang } from './data.ts';
import { randomId, sign, verify } from './crypto.ts';
import { log, page, redirect } from './http.ts';
import { customerOf, paymentConfig, stripe, subscription } from './stripe.ts';
import { ctxFor } from './context.ts';
import { isCash } from './cash.ts';
import * as member from './email/member.ts';
import { admin, B, dashboard } from './email/admin.ts';
import { M } from './data.ts';

const DAYS = 14;
interface Payload { s: string; x: number; id: string }

export async function sendCardLink(env: Env, sub: Stripe.Subscription, now = Date.now()) {
  const x = now + DAYS * 86400000;
  const token = await sign({ s: sub.id, x, id: randomId(9) } satisfies Payload, env.ADMIN_ACTION_KEY);
  const ctx = ctxFor(env, sub);
  if (!ctx) throw new Error('this membership has no email to send the link to');
  await member.cardLink(ctx, { link: `${env.API_ORIGIN}/pago/tarjeta?t=${encodeURIComponent(token)}`, expiresMs: x });
}

// GET /pago/tarjeta?t=…
export async function cardPage(req: Request, env: Env): Promise<Response> {
  const u = new URL(req.url);
  const p = await verify<Payload>(u.searchParams.get('t') ?? '', env.ADMIN_ACTION_KEY);
  const fail = (lang: Lang, key: string) => page(lang, t(M.card_link.title, lang), `<h1>${esc(t(M.card_link.title, lang))}</h1><p>${esc(t(M.card_link[key], lang))}</p>`, 400);
  if (!p?.s) return fail('es', 'invalid');
  const st = stripe(env);
  let sub: Stripe.Subscription;
  try { sub = await subscription(st, p.s); } catch { return fail('es', 'invalid'); }
  const lang: Lang = isLang(sub.metadata?.lang) ? sub.metadata.lang : 'es';
  if (p.x < Date.now()) return fail(lang, 'expired');
  if (!isCash(sub) || sub.metadata.method_next === 'card' || sub.status === 'canceled') return fail(lang, 'done');
  const cust = customerOf(sub);
  if (!cust) return fail(lang, 'invalid');
  const members = url('members', lang, true, env.SITE_ORIGIN);
  const session = await st.checkout.sessions.create({
    mode: 'setup',
    customer: cust.id,
    currency: 'eur',
    // The same card-and-SEPA configuration the signup's Checkout uses.
    payment_method_configuration: await paymentConfig(st, env.KV, env.ENVIRONMENT),
    locale: t(M.stripe_locale, lang) as 'es' | 'en' | 'ja',
    metadata: { purpose: 'cash_to_card', sub: sub.id },
    setup_intent_data: { metadata: { purpose: 'cash_to_card', sub: sub.id } },
    success_url: `${members}#tarjeta`,
    cancel_url: members
  });
  log({ route: 'pago/tarjeta', sub: sub.id, outcome: 'session' });
  return redirect(session.url!);
}

// checkout.session.completed with mode "setup", from the webhook.
export async function cardGiven(env: Env, st: Stripe, session: Stripe.Checkout.Session) {
  if (session.metadata?.purpose !== 'cash_to_card' || !session.metadata.sub) return;
  const si = typeof session.setup_intent === 'string'
    ? await st.setupIntents.retrieve(session.setup_intent) : session.setup_intent;
  const raw = si?.payment_method ?? null;
  const pm = typeof raw === 'string' ? raw : raw?.id;
  if (!pm) return;
  const sub = await subscription(st, session.metadata.sub);
  const cust = customerOf(sub);
  if (cust) await st.customers.update(cust.id, { invoice_settings: { default_payment_method: pm } });
  await st.subscriptions.update(sub.id, { default_payment_method: pm, metadata: { method_next: 'card' } });
  const fifth = nextFifth(Date.now());
  log({ route: 'webhook', event: 'cash_to_card', sub: sub.id });
  await admin(env, `${cust?.name ?? sub.id} pasa a tarjeta o domiciliación desde el ${date(fifth, 'es', false)}`, 'Forma de pago', [
    B.h('Pasa a tarjeta o domiciliación'),
    B.p(`${esc(cust?.name ?? '')} ha dado los datos en Stripe. Desde el ${date(fifth, 'es')} la cuota se cobra sola ese día, y ese primer cobro descuenta lo ya pagado en efectivo por los días que quedan. Si aún debe algo en efectivo, el cambio espera a que lo marques como cobrado.`),
    B.button('Abrir en Stripe', dashboard(env, `subscriptions/${sub.id}`))
  ], 'cash_to_card');
}

const nextFifth = (now: number) => { const d = new Date(now); const a = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), 5, 8); return a > now ? a : Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 5, 8); };
