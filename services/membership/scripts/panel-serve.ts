// The Worker on a local port, with the demo families and no Stripe, for
// scripts/a11y.mjs to drive the panel in a real browser: sign in with the
// emailed code, press a button, undo it, open a family, sign out.
//
// A real browser, because the bug it exists for was in the browser's own
// headers: under a no-referrer policy Chrome posts `Origin: null`, the
// panel's same-origin check refused its own sign-in form, and every unit test
// passed because the tests wrote the header themselves (15 October 2026).
//
//   node --experimental-strip-types scripts/panel-serve.ts
//   -> prints {"port": N}; GET /__code answers the last code "emailed"
import { createServer } from 'node:http';
import worker from '../src/index.ts';
import { outbox } from '../src/email/send.ts';
import { pendingPage, shell } from '../src/panel/views.ts';
import type { Env } from '../src/env.ts';

const kv = new Map<string, string>();
const env = {
  KV: {
    get: async (k: string) => kv.get(k) ?? null,
    put: async (k: string, v: string) => { kv.set(k, v); },
    delete: async (k: string) => { kv.delete(k); },
    list: async () => ({ keys: [], list_complete: true, cursor: '' })
  } as unknown as KVNamespace,
  ENVIRONMENT: 'dev', SITE_ORIGIN: 'http://localhost:4000', API_ORIGIN: 'http://localhost',
  ADMIN_EMAIL: 'admin@aikidomusubi.com', FROM_EMAIL: 'no-reply@aikidomusubi.com', REPLY_TO: 'info@aikidomusubi.com',
  PUBLIC_PRORATION: 'create_prorations', RENEWAL_NOTICE_MONTHLY: 'true', AUTO_AGE_UPGRADE: 'false',
  MEMBER_FAILED_EMAIL_SEPA: 'true', MIGRATION_REMITTANCE_LIST: 'true',
  PANEL_USERS: 'admin@aikidomusubi.com:Alberto,info@aikidomusubi.com',
  STRIPE_SECRET_KEY: '', STRIPE_WEBHOOK_SECRET: '', BREVO_API_KEY: '',
  INVITE_SIGNING_KEY: 'panel-serve-invite-key-not-a-secret-0000', ADMIN_ACTION_KEY: 'panel-serve-action-key-not-a-secret-0000'
} satisfies Env;

const server = createServer(async (req, res) => {
  const url = `http://${req.headers.host}${req.url}`;
  if (req.url === '/__code') {
    res.end(/(\d{6})/.exec(outbox.at(-1)?.subject ?? '')?.[1] ?? '');
    return;
  }
  if (req.url === '/__empty') {
    // "Todo al día", which the demo families never reach.
    const info = { email: 'info@aikidomusubi.com', name: '', id: 'demo', csrf: 'demo' };
    res.setHeader('content-type', 'text/html; charset=utf-8');
    res.end(shell({ title: 'Pendiente', tab: 'p', user: info, test: false, counts: { pending: 0, members: 41 }, body: pendingPage(info, [], [], Date.now(), null) }));
    return;
  }
  const chunks: Buffer[] = [];
  for await (const c of req) chunks.push(c as Buffer);
  const headers = new Headers();
  for (const [k, v] of Object.entries(req.headers)) if (typeof v === 'string') headers.set(k, v);
  const r = await worker.fetch(new Request(url, {
    method: req.method, headers, body: req.method === 'GET' || req.method === 'HEAD' ? undefined : Buffer.concat(chunks)
  }), env);
  const out: Record<string, string | string[]> = {};
  r.headers.forEach((v, k) => { out[k] = v; });
  const cookies = r.headers.getSetCookie();
  if (cookies.length) out['set-cookie'] = cookies;
  res.writeHead(r.status, out);
  res.end(Buffer.from(await r.arrayBuffer()));
});
server.listen(0, () => {
  const a = server.address();
  console.log(JSON.stringify({ port: typeof a === 'object' && a ? a.port : 0 }));
});
