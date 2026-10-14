// What the Worker is given. The [vars] are in wrangler.toml and are not
// secret; the rest are set with `wrangler secret put` and live only in
// Cloudflare (locally, in .dev.vars, which git ignores).
export interface Env {
  KV: KVNamespace;
  // Per-IP limits, from Cloudflare's rate-limit binding (wrangler.toml). Not
  // KV: KV allows a thousand writes a day on the free plan, and a limiter that
  // writes on every request is a way to use them up.
  RL_FORMS?: RateLimit;

  ENVIRONMENT: 'dev' | 'test' | 'live' | string;
  SITE_ORIGIN: string;
  API_ORIGIN: string;
  ADMIN_EMAIL: string;
  FROM_EMAIL: string;
  REPLY_TO: string;
  PUBLIC_PRORATION: string;
  RENEWAL_NOTICE_MONTHLY: string;
  AUTO_AGE_UPGRADE: string;
  MEMBER_FAILED_EMAIL_SEPA: string;
  MIGRATION_REMITTANCE_LIST: string;
  EMAIL_OVERRIDE: string;
  // Test mode only: attach new customers to this Stripe test clock, so that
  // renewals, the 15-day notice and failed retries can be run in minutes.
  TEST_CLOCK?: string;

  // secrets
  STRIPE_SECRET_KEY: string;       // a RESTRICTED key: see docs/membership/SETUP.md
  STRIPE_WEBHOOK_SECRET: string;
  INVITE_SIGNING_KEY: string;
  ADMIN_ACTION_KEY: string;
  BREVO_API_KEY: string;
}

export const flag = (v: string | undefined) => v === 'true' || v === '1';
export const isLive = (env: Env) => env.ENVIRONMENT === 'live';
export const stripeMode = (env: Env): 'test' | 'live' => (isLive(env) ? 'live' : 'test');
