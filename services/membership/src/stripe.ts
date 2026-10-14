// The Stripe client, and the few reads every handler needs.
import Stripe from 'stripe';
import type { Env } from './env.ts';

export function stripe(env: Env): Stripe {
  if (!env.STRIPE_SECRET_KEY) throw new Error('STRIPE_SECRET_KEY is not set');
  // Refuse to run a live key anywhere but the live Worker, and a test key in
  // it: the two modes must never cross.
  const live = env.STRIPE_SECRET_KEY.startsWith('sk_live_') || env.STRIPE_SECRET_KEY.startsWith('rk_live_');
  if (live !== (env.ENVIRONMENT === 'live')) throw new Error('Stripe key mode does not match ENVIRONMENT');
  return new Stripe(env.STRIPE_SECRET_KEY, {
    httpClient: Stripe.createFetchHttpClient(),
    maxNetworkRetries: 2
  });
}

export const cryptoProvider = Stripe.createSubtleCryptoProvider();

export async function subscription(s: Stripe, id: string) {
  return s.subscriptions.retrieve(id, { expand: ['default_payment_method', 'customer'] });
}

export function subId(x: string | { id: string } | null | undefined): string | null {
  if (!x) return null;
  return typeof x === 'string' ? x : x.id;
}

// The end of the period a subscription is in. Since the 2025 API versions this
// lives on each item rather than on the subscription; the items share one
// interval, so the first is enough.
export function periodEnd(sub: Stripe.Subscription): number {
  const it = sub.items.data[0] as Stripe.SubscriptionItem & { current_period_end?: number };
  return (it?.current_period_end ?? 0) * 1000;
}
export function periodStart(sub: Stripe.Subscription): number {
  const it = sub.items.data[0] as Stripe.SubscriptionItem & { current_period_start?: number };
  return (it?.current_period_start ?? 0) * 1000;
}

export function method(sub: Stripe.Subscription): { type: string; last4: string | null } | null {
  const pm = sub.default_payment_method;
  if (!pm || typeof pm === 'string') return null;
  if (pm.type === 'card') return { type: 'card', last4: pm.card?.last4 ?? null };
  if (pm.type === 'sepa_debit') return { type: 'sepa_debit', last4: pm.sepa_debit?.last4 ?? null };
  return { type: pm.type, last4: null };
}

export function customerOf(sub: Stripe.Subscription): Stripe.Customer | null {
  return sub.customer && typeof sub.customer !== 'string' && !('deleted' in sub.customer && sub.customer.deleted)
    ? (sub.customer as Stripe.Customer) : null;
}

export async function priceIds(s: Stripe, keys: string[]): Promise<Record<string, string>> {
  const out: Record<string, string> = {};
  const uniq = [...new Set(keys)];
  for (let i = 0; i < uniq.length; i += 10) {
    const res = await s.prices.list({ lookup_keys: uniq.slice(i, i + 10), active: true, limit: 100 });
    for (const p of res.data) if (p.lookup_key) out[p.lookup_key] = p.id;
  }
  const missing = uniq.filter((k) => !out[k]);
  if (missing.length) throw new Error(`no Stripe Price for ${missing.join(', ')} — run npm run stripe:setup`);
  return out;
}

// Which payment methods Checkout offers. Recent API versions no longer take a
// list per session: they take a "payment method configuration", made once by
// `npm run stripe:setup` with card and SEPA Direct Debit on and everything
// else off (Apple Pay and Google Pay ride on card). Found here by its name and
// remembered for a day.
export const PMC_NAME = 'Cuotas: tarjeta y SEPA';

export async function paymentConfig(st: Stripe, kv: KVNamespace, mode: string): Promise<string> {
  const cacheKey = `pmc:${mode}`;
  const cached = await kv.get(cacheKey);
  if (cached) return cached;
  for await (const c of st.paymentMethodConfigurations.list({ limit: 100 })) {
    if (c.name === PMC_NAME && c.active) {
      await kv.put(cacheKey, c.id, { expirationTtl: 86400 });
      return c.id;
    }
  }
  throw new Error(`no payment method configuration named "${PMC_NAME}" — run npm run stripe:setup`);
}
