// Renders the panel's pages, with the demo families, into a folder of static
// HTML, so scripts/a11y.mjs can run axe over them in a real browser like the
// signup pages. Goes through the Worker itself: signs in with an emailed code,
// keeps the cookie, and asks for each page, so what is checked is what ships.
//
//   node --experimental-strip-types scripts/panel-pages.ts <out-dir>
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import worker from '../src/index.ts';
import { outbox } from '../src/email/send.ts';
import { pendingPage, shell, APP_JS } from '../src/panel/views.ts';
import type { Env } from '../src/env.ts';

const out = process.argv[2];
if (!out) { console.error('usage: panel-pages.ts <out-dir>'); process.exit(2); }
mkdirSync(join(out, 'panel'), { recursive: true });

const kv = new Map<string, string>();
const env = {
  KV: {
    get: async (k: string) => kv.get(k) ?? null,
    put: async (k: string, v: string) => { kv.set(k, v); },
    delete: async (k: string) => { kv.delete(k); },
    list: async () => ({ keys: [], list_complete: true, cursor: '' })
  } as unknown as KVNamespace,
  ENVIRONMENT: 'dev', SITE_ORIGIN: 'http://localhost:4000', API_ORIGIN: 'https://api.aikidomusubi.com',
  ADMIN_EMAIL: 'admin@aikidomusubi.com', FROM_EMAIL: 'no-reply@aikidomusubi.com', REPLY_TO: 'info@aikidomusubi.com',
  PUBLIC_PRORATION: 'create_prorations', RENEWAL_NOTICE_MONTHLY: 'true', AUTO_AGE_UPGRADE: 'false',
  MEMBER_FAILED_EMAIL_SEPA: 'true', MIGRATION_REMITTANCE_LIST: 'true',
  PANEL_USERS: 'admin@aikidomusubi.com:Alberto,info@aikidomusubi.com',
  STRIPE_SECRET_KEY: '', STRIPE_WEBHOOK_SECRET: '', BREVO_API_KEY: '',
  INVITE_SIGNING_KEY: 'panel-pages-invite-key-not-a-secret-000', ADMIN_ACTION_KEY: 'panel-pages-action-key-not-a-secret-000'
} satisfies Env;

const API = env.API_ORIGIN;
const post = (p: string, b: Record<string, string>, cookie = '') => new Request(API + p, {
  method: 'POST', headers: { origin: API, cookie, 'content-type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams(b).toString()
});
const save = async (name: string, res: Response | string) =>
  writeFileSync(join(out, 'panel', `${name}.html`), typeof res === 'string' ? res : await res.text());

await save('entrar', await worker.fetch(new Request(API + '/panel/entrar'), env));
await save('codigo', await worker.fetch(post('/panel/entrar', { email: 'admin@aikidomusubi.com' }), env));
const code = /(\d{6})/.exec(outbox.at(-1)?.subject ?? '')?.[1] ?? '';
const signedIn = await worker.fetch(post('/panel/codigo', { email: 'admin@aikidomusubi.com', code }), env);
const cookie = (signedIn.headers.get('set-cookie') ?? '').split(';')[0];
if (!cookie) { console.error('panel-pages: could not sign in'); process.exit(1); }
const get = (p: string) => worker.fetch(new Request(API + p, { headers: { cookie } }), env);

await save('pendiente', await get('/panel/'));
await save('pendiente-hecho', await get('/panel/?hecho=keikogi&s=sub_demoGarcia01&n=1'));
await save('miembros', await get('/panel/miembros'));
await save('familia', await get('/panel/miembros?id=sub_demoGarcia01&hecho=paper&n=2'));
await save('confirmar-17', await get('/panel/confirmar?a=age&s=sub_demoSerra001&n=2&back=p'));
await save('confirmar-baja', await get('/panel/confirmar?a=cancel&s=sub_demoSoler001&back=m'));
await save('ayuda', await get('/panel/ayuda'));
const info = { email: 'info@aikidomusubi.com', name: '', id: 'demo', csrf: 'demo' };
await save('vacio', shell({ title: 'Pendiente', tab: 'p', user: info, test: false, counts: { pending: 0, members: 41 },
  body: pendingPage(info, [], [], Date.now(), null) }));
writeFileSync(join(out, 'panel', 'app.js'), APP_JS);
console.log('panel-pages: 10 pages');
