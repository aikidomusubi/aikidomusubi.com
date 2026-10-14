// api.aikidomusubi.com — online signup and fee collection for the dojo.
//
// The site is static on GitHub Pages and cannot run code, so this Worker holds
// the four things that need a server: pricing a signup and handing it to
// Stripe Checkout, hearing back from Stripe, the withdrawal form, and a daily
// job. It stores no personal data of its own; Stripe is the record.
//
// Spec: "Aikido Musubi — Online Membership Signup & Stripe Billing Spec",
// 14 October 2026. Setup: docs/membership/SETUP.md. Day-to-day: RUNBOOK.md.
import type { Env } from './env.ts';
import { checkout } from './checkout.ts';
import { webhook } from './webhook.ts';
import { withdrawal } from './withdrawal.ts';
import { actionPage } from './actions.ts';
import { daily } from './cron.ts';
import { cors, json, log } from './http.ts';

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const { pathname } = new URL(req.url);
    try {
      if (req.method === 'OPTIONS') {
        // The page posts JSON with fetch; this is the preflight for it.
        return new Response(null, {
          status: 204,
          headers: { ...cors(env, req), 'access-control-allow-methods': 'POST', 'access-control-allow-headers': 'content-type, accept', 'access-control-max-age': '600' }
        });
      }
      if (pathname === '/checkout' && req.method === 'POST') return await checkout(req, env);
      if (pathname === '/stripe/webhook' && req.method === 'POST') return await webhook(req, env);
      if (pathname === '/withdrawal' && req.method === 'POST') return await withdrawal(req, env);
      if (pathname === '/admin/a' && (req.method === 'GET' || req.method === 'POST')) return await actionPage(req, env);
      if (pathname === '/health') return json(env, req, { ok: true, env: env.ENVIRONMENT });
      return new Response('not found', { status: 404, headers: { 'x-content-type-options': 'nosniff' } });
    } catch (e) {
      log({ route: pathname, outcome: 'unhandled', error: (e as Error).message?.slice(0, 200) });
      return new Response('error', { status: 500 });
    }
  },

  async scheduled(_ctrl: ScheduledController, env: Env, ctx: ExecutionContext) {
    ctx.waitUntil(daily(env).catch((e) => log({ job: 'daily', outcome: 'error', error: (e as Error).message?.slice(0, 200) })));
  }
} satisfies ExportedHandler<Env>;
