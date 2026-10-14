// Who an email about a subscription goes to, and in what language.
import type Stripe from 'stripe';
import type { Env } from './env.ts';
import { isLang, type Lang } from './data.ts';
import { customerOf } from './stripe.ts';
import type { Ctx } from './email/member.ts';

export function ctxFor(env: Env, sub: Stripe.Subscription, customer?: Stripe.Customer | null): Ctx | null {
  const c = customer ?? customerOf(sub);
  if (!c || !c.email) return null;
  const meta = sub.metadata ?? {};
  const lang: Lang = isLang(meta.lang) ? meta.lang : 'es';
  const name = c.name ?? '';
  return { env, lang, to: c.email, toName: name, hello: meta.hello || name.split(' ')[0] || name };
}
