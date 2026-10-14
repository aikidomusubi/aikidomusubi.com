// Signed tokens, for invite links and for the action buttons in admin emails.
//
// A token is base64url(JSON) + "." + base64url(HMAC-SHA256). It carries ids and
// dates, never personal data: an invite's email lives in KV under the token's
// id, so the link in somebody's inbox says nothing about who it is for.
const enc = new TextEncoder();

function b64url(bytes: ArrayBuffer | Uint8Array): string {
  const a = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  let s = '';
  for (const b of a) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function unb64url(s: string): Uint8Array {
  const pad = s.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((s.length + 3) % 4);
  const bin = atob(pad);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

async function key(secret: string) {
  if (!secret || secret.length < 32) throw new Error('signing key missing or shorter than 32 characters');
  return crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign', 'verify']);
}

export async function sign(payload: object, secret: string): Promise<string> {
  const body = b64url(enc.encode(JSON.stringify(payload)));
  const sig = await crypto.subtle.sign('HMAC', await key(secret), enc.encode(body));
  return `${body}.${b64url(sig)}`;
}

// Returns the payload, or null for anything malformed, tampered or unsigned.
// Expiry is the caller's business: an expired token deserves a different
// message from a forged one.
export async function verify<T = Record<string, unknown>>(token: string, secret: string): Promise<T | null> {
  if (typeof token !== 'string' || token.length > 2048) return null;
  const [body, sig] = token.split('.');
  if (!body || !sig) return null;
  try {
    const ok = await crypto.subtle.verify('HMAC', await key(secret), unb64url(sig), enc.encode(body));
    if (!ok) return null;
    return JSON.parse(new TextDecoder().decode(unb64url(body))) as T;
  } catch {
    return null;
  }
}

export function randomId(bytes = 12): string {
  return b64url(crypto.getRandomValues(new Uint8Array(bytes)));
}

export async function sha256(s: string): Promise<string> {
  return b64url(await crypto.subtle.digest('SHA-256', enc.encode(s)));
}
