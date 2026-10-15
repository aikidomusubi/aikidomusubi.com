// Signing in to the panel: an email address, a six-digit code sent to it, and
// a session cookie. No password to remember or to leak.
//
// Only the addresses in PANEL_USERS can get a code (decided 15 October 2026:
// admin@ and info@, the dojo's own mailboxes). Anybody else is told exactly
// what an allowed address is told, so the form says nothing about who is on
// the list.
//
// THE CODE is kept only as a hash, for ten minutes, and allows five tries;
// a new one is not sent while the last is less than a minute old, so the form
// cannot be used to flood the dojo's inbox.
//
// THE SESSION is a signed cookie naming a session id that must also exist in
// KV: signing out deletes it, and removing an address from PANEL_USERS ends
// every session it has, at the next page.
import type { Env } from '../env.ts';
import { randomId, sha256, sign, verify } from '../crypto.ts';
import { limited } from '../http.ts';
import { B, render } from '../email/layout.ts';
import { send } from '../email/send.ts';

export interface User { email: string; name: string }
export interface Session extends User { id: string; csrf: string }

const COOKIE = '__Host-cuotas';
const SESSION_DAYS = 30;
const CODE_MIN = 10;
const TRIES = 5;

export const normEmail = (s: string) => s.trim().toLowerCase().slice(0, 254);

export function users(env: Env): Map<string, string> {
  const out = new Map<string, string>();
  for (const part of (env.PANEL_USERS ?? '').split(',')) {
    const [email, name] = part.split(':');
    if (email?.includes('@')) out.set(normEmail(email), (name ?? '').trim());
  }
  return out;
}

// The session token is signed with the same key as the email buttons, so it
// carries `k: 'ses'`: an action token can never be presented as a session.
interface SessionToken { k: 'ses'; id: string; e: string; x: number }

export async function session(req: Request, env: Env): Promise<Session | null> {
  const raw = (req.headers.get('cookie') ?? '').split(/;\s*/).find((c) => c.startsWith(COOKIE + '='));
  if (!raw) return null;
  const p = await verify<SessionToken>(decodeURIComponent(raw.slice(COOKIE.length + 1)), env.ADMIN_ACTION_KEY);
  if (!p || p.k !== 'ses' || !p.id || p.x < Date.now()) return null;
  const allowed = users(env);
  if (!allowed.has(p.e)) return null;
  if ((await env.KV.get(`ses:${p.id}`)) !== p.e) return null;
  return { email: p.e, name: allowed.get(p.e) ?? '', id: p.id, csrf: await csrfFor(env, p.id) };
}

export const csrfFor = async (env: Env, id: string) => (await sha256(`csrf:${id}:${env.ADMIN_ACTION_KEY}`)).slice(0, 32);

// Every POST must come from a page of this panel: same origin, and carrying the
// session's own token. SameSite=Lax on the cookie is the third lock.
export function sameOrigin(req: Request): boolean {
  const origin = req.headers.get('origin');
  return origin === new URL(req.url).origin;
}

function cookie(value: string, maxAge: number) {
  return `${COOKIE}=${encodeURIComponent(value)}; Path=/; Secure; HttpOnly; SameSite=Lax; Max-Age=${maxAge}`;
}

export async function startSession(env: Env, email: string): Promise<string> {
  const id = randomId(18);
  await env.KV.put(`ses:${id}`, email, { expirationTtl: SESSION_DAYS * 86400 });
  const token = await sign({ k: 'ses', id, e: email, x: Date.now() + SESSION_DAYS * 86400000 } satisfies SessionToken, env.ADMIN_ACTION_KEY);
  return cookie(token, SESSION_DAYS * 86400);
}

export async function endSession(env: Env, s: Session | null): Promise<string> {
  if (s) await env.KV.delete(`ses:${s.id}`);
  return cookie('', 0);
}

// ---------------------------------------------------------------------------
interface CodeRecord { h: string; salt: string; tries: number; at: number }

function sixDigits(): string {
  // Rejection sampling, so every code is equally likely.
  const buf = new Uint32Array(1);
  for (;;) {
    crypto.getRandomValues(buf);
    if (buf[0] < 4_294_000_000) return String(buf[0] % 1_000_000).padStart(6, '0');
  }
}

const codeKey = async (email: string) => `pc:${await sha256(email)}`;

// Returns nothing either way: the page says the same thing to everyone.
export async function sendCode(req: Request, env: Env, emailIn: string): Promise<void> {
  const email = normEmail(emailIn);
  if (!users(env).has(email)) return;
  if (await limited(env, req, 'panel')) return;
  const key = await codeKey(email);
  const prev = await env.KV.get(key);
  if (prev && Date.now() - (JSON.parse(prev) as CodeRecord).at < 60_000) return;
  const code = sixDigits();
  const salt = randomId(9);
  await env.KV.put(key, JSON.stringify({ h: await sha256(`${salt}:${code}`), salt, tries: 0, at: Date.now() } satisfies CodeRecord),
    { expirationTtl: CODE_MIN * 60 });
  const { html, text } = render('es', 'Panel de cuotas', [
    B.h(`Tu código: ${code}`),
    B.p(`Escríbelo en el panel de cuotas para entrar. Caduca en ${CODE_MIN} minutos y sirve una sola vez.`),
    B.small('Si no has sido tú, no hagas nada: sin el código nadie puede entrar.')
  ], env.SITE_ORIGIN, true);
  await send(env, { to: email, subject: `${code} es tu código del panel de cuotas`, html, text, tag: 'panel_code' });
}

export async function checkCode(env: Env, emailIn: string, codeIn: string): Promise<boolean> {
  const email = normEmail(emailIn);
  const code = codeIn.replace(/\D/g, '');
  if (!users(env).has(email) || code.length !== 6) return false;
  const key = await codeKey(email);
  const raw = await env.KV.get(key);
  if (!raw) return false;
  const rec = JSON.parse(raw) as CodeRecord;
  if (rec.tries >= TRIES - 1) { await env.KV.delete(key); }
  if ((await sha256(`${rec.salt}:${code}`)) === rec.h) {
    await env.KV.delete(key);
    return true;
  }
  if (rec.tries < TRIES - 1) {
    const left = Math.max(60, Math.round((rec.at + CODE_MIN * 60000 - Date.now()) / 1000));
    await env.KV.put(key, JSON.stringify({ ...rec, tries: rec.tries + 1 }), { expirationTtl: left });
  }
  return false;
}
