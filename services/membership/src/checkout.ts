// POST /checkout — a validated signup in, a Stripe Checkout Session out (spec 6).
//
// Stateless: nothing is stored here. The Customer and the Subscription Stripe
// creates are the record, and the household travels in the subscription's
// metadata (src/meta.ts).
import type Stripe from 'stripe';
import type { Env } from './env.ts';
import { CATALOG, M, date, esc, money, periodName, periodUnit, t, url, type Lang } from './data.ts';
import { randomId, sha256 } from './crypto.ts';
import { encodeMember, type Meta } from './meta.ts';
import { Pricing } from './pricing.ts';
import { checkInvite } from './invite.ts';
import { errorPage, fromSite, json, limited, log, readBody, redirect, wantsJson } from './http.ts';
import { stripe, priceIds, paymentConfig } from './stripe.ts';
import { toMember, unknownFields, validate, type FieldError, type Signup } from './validate.ts';

const LIVE_STATUSES = new Set(['active', 'trialing', 'past_due', 'unpaid', 'incomplete']);

function fail(env: Env, req: Request, lang: Lang, errors: FieldError[], status = 422) {
  if (wantsJson(req)) {
    return json(env, req, {
      errors: errors.map((e) => ({
        field: e.field, code: e.code,
        message: t(M.errors[e.code] ?? M.errors.generic, lang, { url: esc(url('contact', lang, true, env.SITE_ORIGIN)) })
      }))
    }, status);
  }
  return errorPage(lang, errors, env.SITE_ORIGIN);
}

export async function checkout(req: Request, env: Env, now = Date.now()): Promise<Response> {
  if (!fromSite(env, req)) return json(env, req, { error: 'origin' }, 403);
  if (await limited(env, req, 'checkout')) return fail(env, req, 'es', [{ field: 'form', code: 'rate_limited' }], 429);

  const body = await readBody(req);
  if (!body) return fail(env, req, 'es', [{ field: 'form', code: 'generic' }], 400);
  const unknown = unknownFields(body);
  if (unknown.length) {
    log({ route: 'checkout', outcome: 'unknown_fields', count: unknown.length });
    return fail(env, req, 'es', [{ field: 'form', code: 'generic' }], 400);
  }
  // The honeypot: a field no person sees. Filled in means a bot; it gets the
  // same answer a person with a server problem would, and nothing is created.
  if ((body.website ?? '') !== '') {
    log({ route: 'checkout', outcome: 'honeypot' });
    return fail(env, req, 'es', [{ field: 'form', code: 'generic' }], 422);
  }

  const v = validate(body, now);
  if (!v.ok) return fail(env, req, v.lang, v.errors);
  const s = v.value;

  // Invites: a proration mode and, maybe, the 5th of the first charge.
  let proration: 'none' | 'create_prorations' = env.PUBLIC_PRORATION === 'none' ? 'none' : 'create_prorations';
  let anchor = Pricing.nextAnchor(now);
  let inviteId: string | null = null;
  if (s.invite) {
    const inv = await checkInvite(env, s.invite, s.email, now);
    if (!inv.ok) return fail(env, req, s.lang, [{ field: 'email', code: inv.code }]);
    proration = inv.proration;
    if (inv.anchor) anchor = inv.anchor;
    inviteId = inv.id;
  }

  const sid = s.sid || randomId(12);
  const lang = s.lang;
  const result = Pricing.price({ period: s.period, members: s.members.map(toMember) }, CATALOG);

  // Local development without Stripe: the flow ends at the thank-you page.
  if (env.ENVIRONMENT === 'dev' && !env.STRIPE_SECRET_KEY) {
    const to = url('thanks', lang, true, env.SITE_ORIGIN);
    return wantsJson(req) ? json(env, req, { url: to, dev: { lineItems: result.lineItems, total: result.total } }) : redirect(to);
  }

  try {
    const st = stripe(env);

    // One active membership per email: a second signup would be a second
    // subscription at full price and the family discount would be lost.
    const customers = await st.customers.list({ email: s.email, limit: 10 });
    let reuse: Stripe.Customer | null = null;
    for (const c of customers.data) {
      const subs = await st.subscriptions.list({ customer: c.id, status: 'all', limit: 20 });
      if (subs.data.some((x) => LIVE_STATUSES.has(x.status))) {
        log({ route: 'checkout', sid, outcome: 'existing_subscription' });
        return fail(env, req, lang, [{ field: 'email', code: 'existing' }]);
      }
      reuse ??= c;
    }

    const holderName = `${s.holder.given} ${s.holder.family}`;
    const stripeLocale = t(M.stripe_locale, lang) as 'es' | 'en' | 'ja';
    const customerParams = {
      name: holderName,
      email: s.email,
      ...(s.phone ? { phone: s.phone } : {}),
      preferred_locales: [stripeLocale],
      metadata: { source: 'signup', signup_id: sid, lang }
    };
    // A test clock lets the whole year of a membership be run in minutes
    // (docs/membership/SETUP.md, step 5). Never in live mode.
    const clock = env.ENVIRONMENT === 'test' && env.TEST_CLOCK ? { test_clock: env.TEST_CLOCK } : {};
    const customer = reuse
      ? await st.customers.update(reuse.id, customerParams)
      : await st.customers.create({ ...customerParams, ...clock }, { idempotencyKey: `cust-${sid}-${await sha256(s.email)}` });

    const ids = await priceIds(st, result.lineItems.map((l) => l.lookupKey));
    const meta = metadata(s, result.perMember, sid, now, inviteId);
    const total = result.total;
    const unit = periodUnit(s.period, stripeLocale);
    const withdrawBy = Pricing.withdrawalDeadline(now);
    const vars = {
      first: date(anchor, stripeLocale), amount: money(total, stripeLocale), unit,
      withdraw: date(withdrawBy, stripeLocale), url: url('terms', lang, true, env.SITE_ORIGIN)
    };

    const params: Stripe.Checkout.SessionCreateParams = {
      mode: 'subscription',
      customer: customer.id,
      client_reference_id: sid,
      line_items: result.lineItems.map((l) => ({ price: ids[l.lookupKey], quantity: l.quantity })),
      payment_method_configuration: await paymentConfig(st, env.KV, env.ENVIRONMENT),
      billing_address_collection: 'auto',
      customer_update: { address: 'auto' },
      locale: stripeLocale,
      consent_collection: { terms_of_service: 'required' },
      custom_text: {
        submit: { message: t(proration === 'none' ? M.stripe.submit_none : M.stripe.submit, stripeLocale, vars).slice(0, 1200) },
        terms_of_service_acceptance: { message: t(M.stripe.terms, stripeLocale, vars).slice(0, 1200) }
      },
      subscription_data: {
        billing_cycle_anchor: Math.floor(anchor / 1000),
        proration_behavior: proration,
        description: t(M.stripe.description, stripeLocale, { period: periodName(s.period, stripeLocale), people: peopleWord(s.members.length, stripeLocale) }).slice(0, 500),
        metadata: meta
      },
      allow_promotion_codes: false,
      success_url: url('thanks', lang, true, env.SITE_ORIGIN),
      cancel_url: url('signup', lang, true, env.SITE_ORIGIN) + '#volver',
      expires_at: Math.floor(now / 1000) + 30 * 60 + 60
    };

    // The same submission twice (a double click, a retry after a slow network)
    // gets the same session back; a changed one gets a new session.
    const key = `co-${sid}-${(await sha256(JSON.stringify({ ...params, expires_at: 0 }))).slice(0, 16)}`;
    const session = await st.checkout.sessions.create(params, { idempotencyKey: key });
    log({ route: 'checkout', sid, outcome: 'session', session: session.id });
    return wantsJson(req) ? json(env, req, { url: session.url }) : redirect(session.url!);
  } catch (e) {
    log({ route: 'checkout', sid, outcome: 'error', error: (e as Error).message?.slice(0, 200) });
    return fail(env, req, lang, [{ field: 'form', code: 'generic' }], 502);
  }
}

function peopleWord(n: number, lang: 'es' | 'en' | 'ja') {
  if (lang === 'ja') return `${n}名`;
  if (lang === 'en') return n === 1 ? '1 person' : `${n} people`;
  return n === 1 ? '1 persona' : `${n} personas`;
}

export function metadata(s: Signup, priced: { slot: number; kind: 'full' | 'family' | 'sc' }[], sid: string, now: number, inviteId: string | null): Meta {
  const iso = new Date(now).toISOString();
  const quarterlyOrAnnual = s.period !== 'monthly';
  const meta: Meta = {
    catalog_version: CATALOG.version,
    period: s.period,
    lang: s.lang,
    signup_id: sid,
    holder: s.holder.slot ? `m${s.holder.slot}` : 'other',
    hello: s.holder.given.slice(0, 100),
    terms_version: String(M.terms_version),
    terms_at: iso,
    early_start_at: iso,
    adult_at: iso,
    withdraw_by: new Date(Pricing.withdrawalDeadline(now)).toISOString().slice(0, 10),
    keikogi: quarterlyOrAnnual ? 'due' : '',
    keikogi_due: ''
  };
  if (s.minors) meta.guardian_at = iso;
  if (inviteId) meta.invite_id = inviteId;
  const slots: string[] = [];
  // Members are renumbered 1..n in the order given: the form's slot numbers
  // can have gaps (person 2 removed, person 3 kept), the metadata does not.
  s.members.forEach((p, i) => {
    const n = i + 1;
    const kind = priced[i].kind;
    Object.assign(meta, encodeMember({
      slot: n, name: `${p.given} ${p.family}`, cat: p.cat, rate: p.rate, kind, venue: p.venue,
      sc: p.rate === 'sc' ? 'pending' : null,
      bym: p.birth ? `${p.birth.y}-${String(p.birth.m).padStart(2, '0')}` : null
    }));
    if (quarterlyOrAnnual) slots.push(`m${n}`);
    if (s.holder.slot === p.slot) meta.holder = `m${n}`;
  });
  meta.keikogi_due = slots.join(',');
  return meta;
}
