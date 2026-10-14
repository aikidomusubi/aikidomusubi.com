// Invite links, for the members moving over from the bank remittance in
// January 2027 and for anybody the dojo wants to treat specially (spec 8.4).
//
// The link carries a signed token: { i: id, p: proration, a: first charge, x:
// expiry }. It carries no email. The email the invite was issued for is in KV
// under `invite:<id>`, and checkout refuses the invite with any other address.
// The token never carries a price: it only chooses a proration mode and,
// optionally, the 5th of the first Stripe charge.
//
// `a` is what stops a migrating member paying twice: the dojo issues the
// invite for the 5th of the first month it leaves them out of the bank
// remittance, so Stripe's first charge and the bank's last one cannot overlap.
import type { Env } from './env.ts';
import { randomId, sign, verify } from './crypto.ts';

export interface InvitePayload { i: string; p: 'none' | 'create_prorations'; a?: number; x: number }
export interface InviteRecord { email: string; name?: string; lang?: string; created: number; used?: string }

export type InviteCheck =
  | { ok: true; id: string; proration: 'none' | 'create_prorations'; anchor: number | null }
  | { ok: false; code: 'invite_invalid' | 'invite_expired' | 'invite_used' | 'invite_email' };

export async function createInvite(env: Env, o: {
  email: string; name?: string; lang?: string; proration?: 'none' | 'create_prorations'; anchor?: number | null; days?: number;
}): Promise<{ token: string; id: string; expires: number }> {
  const id = randomId(9);
  const expires = Date.now() + (o.days ?? 30) * 86400000;
  const payload: InvitePayload = { i: id, p: o.proration ?? 'none', x: expires };
  if (o.anchor) payload.a = o.anchor;
  const record: InviteRecord = { email: o.email.trim().toLowerCase(), name: o.name, lang: o.lang, created: Date.now() };
  await env.KV.put(`invite:${id}`, JSON.stringify(record), { expirationTtl: (o.days ?? 30) * 86400 + 30 * 86400 });
  return { token: await sign(payload, env.INVITE_SIGNING_KEY), id, expires };
}

export async function checkInvite(env: Env, token: string, email: string, now: number): Promise<InviteCheck> {
  const p = await verify<InvitePayload>(token, env.INVITE_SIGNING_KEY);
  if (!p || !p.i || (p.p !== 'none' && p.p !== 'create_prorations')) return { ok: false, code: 'invite_invalid' };
  if (!p.x || p.x < now) return { ok: false, code: 'invite_expired' };
  const raw = await env.KV.get(`invite:${p.i}`);
  if (!raw) return { ok: false, code: 'invite_invalid' };
  const rec = JSON.parse(raw) as InviteRecord;
  if (rec.used) return { ok: false, code: 'invite_used' };
  if (rec.email !== email.trim().toLowerCase()) return { ok: false, code: 'invite_email' };
  const anchor = p.a && p.a > now + 3600_000 ? p.a : null;
  return { ok: true, id: p.i, proration: p.p, anchor };
}

// Spent on a completed checkout, not on the attempt: somebody who backs out of
// Stripe's page can use their link again.
export async function markUsed(env: Env, id: string, subscriptionId: string) {
  const raw = await env.KV.get(`invite:${id}`);
  if (!raw) return;
  const rec = JSON.parse(raw) as InviteRecord;
  rec.used = subscriptionId;
  await env.KV.put(`invite:${id}`, JSON.stringify(rec), { expirationTtl: 400 * 86400 });
}
