// What every command-line tool here shares: arguments, the secrets file for a
// Stripe mode, an Env shaped like the Worker's, and KV through wrangler.
//
// SECRETS LIVE IN TWO FILES, NEVER IN THE REPOSITORY:
//
//   .dev.vars    test mode — also what `wrangler dev` reads
//   .live.vars   live mode
//
// Both are gitignored. Each holds the same names the Worker's secrets have
// (STRIPE_SECRET_KEY, INVITE_SIGNING_KEY, ADMIN_ACTION_KEY, BREVO_API_KEY,
// STRIPE_WEBHOOK_SECRET), as KEY="value" lines. The setup and migration
// scripts need the FULL secret key; the Worker gets a restricted one.
import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import Stripe from 'stripe';
import type { Env } from '../src/env.ts';

export const here = dirname(fileURLToPath(import.meta.url));
export const pkg = join(here, '..');
export const repo = join(here, '..', '..', '..');

export function args(): Record<string, string | true> {
  const out: Record<string, string | true> = {};
  const a = process.argv.slice(2);
  for (let i = 0; i < a.length; i++) {
    if (!a[i].startsWith('--')) continue;
    const k = a[i].slice(2);
    const v = a[i + 1];
    if (v === undefined || v.startsWith('--')) out[k] = true;
    else { out[k] = v; i++; }
  }
  return out;
}

export function mode(a: Record<string, string | true>): 'test' | 'live' {
  const m = a.mode ?? 'test';
  if (m !== 'test' && m !== 'live') die('--mode must be test or live');
  return m as 'test' | 'live';
}

export function vars(m: 'test' | 'live'): Record<string, string> {
  const file = join(pkg, m === 'live' ? '.live.vars' : '.dev.vars');
  if (!existsSync(file)) die(`${file} does not exist — see docs/membership/SETUP.md`);
  const out: Record<string, string> = {};
  for (const line of readFileSync(file, 'utf8').split('\n')) {
    const m2 = line.match(/^\s*([A-Z0-9_]+)\s*=\s*"?(.*?)"?\s*$/);
    if (m2) out[m2[1]] = m2[2];
  }
  return out;
}

// A Stripe client whose key must match the mode asked for: running a live key
// by accident, or a test key against live, stops here.
export function stripeFor(m: 'test' | 'live', key: string | undefined): Stripe {
  if (!key) die('STRIPE_SECRET_KEY missing from the vars file');
  const live = /^(sk|rk)_live_/.test(key!);
  if (live !== (m === 'live')) die(`the key in the vars file is a ${live ? 'LIVE' : 'test'} key but --mode is ${m}`);
  return new Stripe(key!, { maxNetworkRetries: 2 });
}

// KV through wrangler, against the deployed namespace of that mode.
export function kv(m: 'test' | 'live'): KVNamespace {
  const base = ['wrangler', 'kv', 'key'];
  const tail = ['--binding', 'KV', '--remote', ...(m === 'live' ? ['--env', 'live'] : [])];
  const run = (a: string[]) => execFileSync('npx', [...base, ...a, ...tail], { cwd: pkg, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
  return {
    get: async (k: string) => { try { return run(['get', k]).trim() || null; } catch { return null; } },
    put: async (k: string, v: string, o?: { expirationTtl?: number }) => {
      run(['put', k, v, ...(o?.expirationTtl ? ['--ttl', String(o.expirationTtl)] : [])]);
    },
    delete: async (k: string) => { run(['delete', k]); },
    list: async () => { throw new Error('not available from the command line'); }
  } as unknown as KVNamespace;
}

export function env(m: 'test' | 'live', v: Record<string, string>, withKv = false): Env {
  return {
    KV: withKv ? kv(m) : (undefined as unknown as KVNamespace),
    ENVIRONMENT: m,
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
    EMAIL_OVERRIDE: v.EMAIL_OVERRIDE ?? '',
    STRIPE_SECRET_KEY: v.STRIPE_SECRET_KEY ?? '',
    STRIPE_WEBHOOK_SECRET: v.STRIPE_WEBHOOK_SECRET ?? '',
    INVITE_SIGNING_KEY: v.INVITE_SIGNING_KEY ?? '',
    ADMIN_ACTION_KEY: v.ADMIN_ACTION_KEY ?? '',
    BREVO_API_KEY: v.BREVO_API_KEY ?? ''
  };
}

export function die(msg: string): never {
  console.error(`\n  ${msg}\n`);
  process.exit(1);
}

export const euros = (n: number) => `${n.toFixed(2).replace(/\.00$/, '')} €`;
