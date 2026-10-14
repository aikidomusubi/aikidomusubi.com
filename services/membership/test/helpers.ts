// A KV namespace in memory, and an Env with every secret set to something
// that is obviously a test value.
import type { Env } from '../src/env.ts';

export function memoryKV(): KVNamespace {
  const m = new Map<string, string>();
  return {
    get: async (k: string) => m.get(k) ?? null,
    put: async (k: string, v: string) => { m.set(k, v); },
    delete: async (k: string) => { m.delete(k); },
    list: async ({ prefix = '' }: { prefix?: string } = {}) => ({
      keys: [...m.keys()].filter((k) => k.startsWith(prefix)).map((name) => ({ name })),
      list_complete: true, cursor: ''
    })
  } as unknown as KVNamespace;
}

export function testEnv(over: Partial<Env> = {}): Env {
  return {
    KV: memoryKV(),
    ENVIRONMENT: 'dev',
    SITE_ORIGIN: 'https://aikidomusubi.com',
    API_ORIGIN: 'https://api.aikidomusubi.com',
    ADMIN_EMAIL: 'admin@aikidomusubi.com',
    FROM_EMAIL: 'no-reply@aikidomusubi.com',
    REPLY_TO: 'info@aikidomusubi.com',
    PUBLIC_PRORATION: 'create_prorations',
    RENEWAL_NOTICE_MONTHLY: 'true',
    AUTO_AGE_UPGRADE: 'false',
    MEMBER_FAILED_EMAIL_SEPA: 'true',
    MIGRATION_REMITTANCE_LIST: 'true',
    EMAIL_OVERRIDE: '',
    STRIPE_SECRET_KEY: '',
    STRIPE_WEBHOOK_SECRET: 'whsec_test_secret_for_unit_tests_only',
    INVITE_SIGNING_KEY: 'test-invite-signing-key-0123456789abcdef',
    ADMIN_ACTION_KEY: 'test-admin-action-key-0123456789abcdefgh',
    BREVO_API_KEY: '',
    ...over
  };
}

export function post(path: string, body: Record<string, string>, opts: { json?: boolean; origin?: string } = {}) {
  const json = opts.json ?? true;
  return new Request(`https://api.aikidomusubi.com${path}`, {
    method: 'POST',
    headers: {
      origin: opts.origin ?? 'https://aikidomusubi.com',
      'content-type': json ? 'application/json' : 'application/x-www-form-urlencoded',
      accept: json ? 'application/json' : 'text/html',
      'cf-connecting-ip': '203.0.113.' + Math.floor(Math.random() * 250)
    },
    body: json ? JSON.stringify(body) : new URLSearchParams(body).toString()
  });
}

// A complete, valid signup: the spec's fourth example, quarterly.
export const FAMILY = {
  lang: 'es', period: 'quarterly', holder: 'p1',
  p1_given: 'Ana', p1_family: 'García López', p1_cat: 'adult', p1_rate: 'general',
  p2_given: 'Marc', p2_family: 'García López', p2_cat: 'adult', p2_rate: 'general',
  p3_given: 'Lía', p3_family: 'García Ruiz', p3_cat: 'youth', p3_bm: '3', p3_by: '2014', p3_rate: 'general',
  email: 'ana.garcia@example.com', phone: '', adult: 'on', guardian: 'on', terms: 'on', early: 'on', website: ''
};
