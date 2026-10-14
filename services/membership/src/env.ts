// What the Worker is given. The [vars] are in wrangler.toml and are not
// secret; the rest are set with `wrangler secret put` and live only in
// Cloudflare (locally, in .dev.vars, which git ignores).
export interface Env {
  KV: KVNamespace;

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
