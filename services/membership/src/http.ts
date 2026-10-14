// Responses, and the rules every request goes through (spec 12.2).
import type { Env } from './env.ts';
import { M, SITE, esc, t, url, type Lang } from './data.ts';
import type { FieldError } from './validate.ts';

const SECURITY = {
  'x-content-type-options': 'nosniff',
  'referrer-policy': 'no-referrer',
  'strict-transport-security': 'max-age=31536000; includeSubDomains',
  'cache-control': 'no-store'
};

export function cors(env: Env, req: Request): Record<string, string> {
  const origin = req.headers.get('origin');
  return origin === env.SITE_ORIGIN
    ? { 'access-control-allow-origin': origin, vary: 'origin' }
    : {};
}

export function json(env: Env, req: Request, body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', ...SECURITY, ...cors(env, req),
      'content-security-policy': "default-src 'none'" }
  });
}

export function redirect(to: string): Response {
  return new Response(null, { status: 303, headers: { location: to, ...SECURITY } });
}

// A small page in the site's own colours, for the paths that work without
// JavaScript: validation errors, and the admin's confirmation screens.
export function page(lang: Lang | 'es', title: string, body: string, status = 200): Response {
  const html = `<!doctype html><html lang="${lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>${esc(title)} · ${esc(SITE.title)}</title>
<style>
body{margin:0;background:#fff;color:#111314;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
header{background:#111314;color:#fff;padding:14px 20px;font:700 16px/1 Futura,"Trebuchet MS",Arial,sans-serif;letter-spacing:.04em;text-transform:uppercase;border-bottom:4px solid #FFF200}
main{max-width:40rem;margin:0 auto;padding:28px 20px 48px}
h1{font:700 26px/1.2 Futura,"Trebuchet MS",Arial,sans-serif;margin:0 0 16px}
ul{padding-left:1.2rem}li{margin:0 0 6px}
.err{border:2px solid #82241f;padding:12px 16px;margin:0 0 20px}.err li{color:#82241f;font-weight:700}
a{color:#111314}button{font:700 15px/1 Futura,"Trebuchet MS",Arial,sans-serif;letter-spacing:.06em;text-transform:uppercase;background:#111314;color:#fff;border:0;padding:14px 20px;cursor:pointer;min-height:44px}
button:focus-visible,a:focus-visible{outline:3px solid #064F6E;outline-offset:2px}
table{border-collapse:collapse;width:100%;margin:0 0 16px}td{border-bottom:1px solid #ddd;padding:6px 4px}
.ok{border-left:4px solid #1a7444;padding:8px 14px;background:#f4f8f5}
</style></head><body><header>${esc(SITE.title)}</header><main>${body}</main></body></html>`;
  return new Response(html, {
    status,
    headers: {
      'content-type': 'text/html; charset=utf-8', ...SECURITY,
      'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
    }
  });
}

// Validation errors when JavaScript is off. The browser's back button returns
// to the form with what was typed still in it (spec 6.1).
export function errorPage(lang: Lang, errors: FieldError[], origin: string): Response {
  const items = errors.map((e) => {
    const msg = t(M.errors[e.code] ?? M.errors.generic, lang, { url: esc(url('contact', lang, true, origin)) });
    return `<li>${msg}</li>`;
  }).join('');
  return page(lang, t(M.errors.error_page_title, lang), `<h1>${esc(t(M.errors.error_page_title, lang))}</h1>
<div class="err" role="alert"><ul>${items}</ul></div>
<p>${esc(t(M.errors.error_page_back, lang))}</p>`, 422);
}

// A request from anywhere but the site is refused (spec 12.2). Stripe's own
// webhook calls are not subject to this: they are checked by signature.
export function fromSite(env: Env, req: Request): boolean {
  const origin = req.headers.get('origin');
  if (origin) return origin === env.SITE_ORIGIN || (env.ENVIRONMENT === 'dev' && /^http:\/\/localhost:\d+$/.test(origin));
  const ref = req.headers.get('referer') ?? '';
  return ref.startsWith(env.SITE_ORIGIN + '/') || (env.ENVIRONMENT === 'dev' && /^http:\/\/localhost:\d+\//.test(ref));
}

// Best effort, per IP and per minute. KV is eventually consistent, so this is a
// brake rather than a wall; together with the honeypot and Stripe's own fraud
// checks it is what the spec asks for without a third-party CAPTCHA.
export async function limited(env: Env, req: Request, route: string, perMinute = 10): Promise<boolean> {
  const ip = req.headers.get('cf-connecting-ip') ?? 'unknown';
  const minute = Math.floor(Date.now() / 60000);
  const key = `rl:${route}:${ip}:${minute}`;
  const n = Number((await env.KV.get(key)) ?? '0') + 1;
  await env.KV.put(key, String(n), { expirationTtl: 120 });
  return n > perMinute;
}

export async function readBody(req: Request): Promise<Record<string, string> | null> {
  const len = Number(req.headers.get('content-length') ?? '0');
  if (len > 10_240) return null;
  const raw = await req.text();
  if (raw.length > 10_240) return null;
  const type = req.headers.get('content-type') ?? '';
  try {
    if (type.includes('application/json')) {
      const o = JSON.parse(raw);
      if (!o || typeof o !== 'object' || Array.isArray(o)) return null;
      const out: Record<string, string> = {};
      for (const [k, v] of Object.entries(o)) {
        if (typeof v !== 'string' && typeof v !== 'number' && typeof v !== 'boolean') return null;
        out[k] = String(v);
      }
      return out;
    }
    if (type.includes('application/x-www-form-urlencoded')) {
      return Object.fromEntries(new URLSearchParams(raw));
    }
  } catch {
    return null;
  }
  return null;
}

export const wantsJson = (req: Request) => (req.headers.get('accept') ?? '').includes('application/json');

export function log(o: Record<string, unknown>) {
  // Structured, and never with a name, an email, a phone or a request body
  // (spec 12.4): ids and outcomes only.
  console.log(JSON.stringify(o));
}
