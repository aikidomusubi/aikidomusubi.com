// The routes, end to end inside the Worker, without Stripe: origin checks,
// unknown fields, the honeypot, validation messages in the right language,
// invite tokens, webhook signatures and repeats, and the emails' rendering.
import { describe, expect, it, beforeEach } from 'vitest';
import Stripe from 'stripe';
import worker from '../src/index.ts';
import { FAMILY, post, testEnv } from './helpers.ts';
import { checkInvite, createInvite, markUsed } from '../src/invite.ts';
import { sign, verify } from '../src/crypto.ts';
import { outbox } from '../src/email/send.ts';
import * as member from '../src/email/member.ts';
import { CATALOG } from '../src/data.ts';

beforeEach(() => { outbox.length = 0; });

describe('POST /checkout', () => {
  it('prices a valid signup and, without Stripe, ends at the thank-you page', async () => {
    const res = await worker.fetch(post('/checkout', FAMILY), testEnv());
    expect(res.status).toBe(200);
    const body = await res.json() as { url: string; dev: { total: number } };
    expect(body.url).toBe('https://aikidomusubi.com/inscripcion/gracias/');
    expect(body.dev.total).toBe(183);
  });
  it('refuses another origin', async () => {
    const res = await worker.fetch(post('/checkout', FAMILY, { origin: 'https://evil.example' }), testEnv({ ENVIRONMENT: 'test' }));
    expect(res.status).toBe(403);
  });
  it('refuses unknown fields, such as an amount', async () => {
    const res = await worker.fetch(post('/checkout', { ...FAMILY, amount: '1' }), testEnv());
    expect(res.status).toBe(400);
  });
  it('gives nothing away to a bot that fills the honeypot', async () => {
    const res = await worker.fetch(post('/checkout', { ...FAMILY, website: 'http://spam' }), testEnv());
    expect(res.status).toBe(422);
  });
  it('returns field errors in the page’s language', async () => {
    const res = await worker.fetch(post('/checkout', { ...FAMILY, lang: 'ca', terms: '' }), testEnv());
    expect(res.status).toBe(422);
    const body = await res.json() as { errors: { field: string; message: string }[] };
    expect(body.errors[0]).toMatchObject({ field: 'terms', message: 'Accepta les condicions de la quota.' });
  });
  it('without JavaScript, answers with a page listing the errors', async () => {
    const res = await worker.fetch(post('/checkout', { ...FAMILY, email: 'x' }, { json: false }), testEnv());
    expect(res.status).toBe(422);
    const html = await res.text();
    expect(html).toContain('Ese correo no parece válido');
    expect(res.headers.get('content-security-policy')).toContain("default-src 'none'");
  });
  it('refuses an oversized body', async () => {
    const res = await worker.fetch(post('/checkout', { ...FAMILY, p1_given: 'x'.repeat(11000) }), testEnv());
    expect(res.status).toBe(400);
  });
});

describe('invites', () => {
  it('work once, for their email, before they expire', async () => {
    const env = testEnv();
    const now = Date.now();
    const { token, id } = await createInvite(env, { email: 'Marta.Vidal@example.com' });
    expect(await checkInvite(env, token, 'marta.vidal@example.com', now)).toMatchObject({ ok: true, proration: 'none' });
    expect(await checkInvite(env, token, 'other@example.com', now)).toEqual({ ok: false, code: 'invite_email' });
    expect(await checkInvite(env, token, 'marta.vidal@example.com', now + 31 * 86400000)).toEqual({ ok: false, code: 'invite_expired' });
    await markUsed(env, id, 'sub_123');
    expect(await checkInvite(env, token, 'marta.vidal@example.com', now)).toEqual({ ok: false, code: 'invite_used' });
  });
  it('reject a tampered token', async () => {
    const env = testEnv();
    const { token } = await createInvite(env, { email: 'a@example.com' });
    const [body, sig] = token.split('.');
    const forged = body.slice(0, -2) + (body.endsWith('A') ? 'B' : 'A') + body.slice(-1) + '.' + sig;
    expect(await checkInvite(env, forged, 'a@example.com', Date.now())).toEqual({ ok: false, code: 'invite_invalid' });
    expect(await checkInvite(env, 'nonsense', 'a@example.com', Date.now())).toEqual({ ok: false, code: 'invite_invalid' });
  });
  it('carry no email in the token', async () => {
    const env = testEnv();
    const { token } = await createInvite(env, { email: 'secret.person@example.com' });
    expect(atob(token.split('.')[0].replace(/-/g, '+').replace(/_/g, '/'))).not.toContain('secret');
  });
  it('can fix the 5th of the first charge', async () => {
    const env = testEnv();
    const anchor = Date.parse('2027-02-05T08:00:00Z');
    const { token } = await createInvite(env, { email: 'a@example.com', anchor, days: 400 });
    const r = await checkInvite(env, token, 'a@example.com', Date.parse('2027-01-10T10:00:00Z'));
    expect(r).toMatchObject({ ok: true, anchor });
  });
});

describe('signed tokens', () => {
  it('round-trip and reject the wrong key', async () => {
    const t = await sign({ a: 1 }, 'k'.repeat(32));
    expect(await verify(t, 'k'.repeat(32))).toEqual({ a: 1 });
    expect(await verify(t, 'j'.repeat(32))).toBeNull();
  });
});

describe('POST /stripe/webhook', () => {
  const env = testEnv({ ENVIRONMENT: 'test', STRIPE_SECRET_KEY: 'sk_test_unit' });
  const event = JSON.stringify({ id: 'evt_unit_1', object: 'event', type: 'customer.created', data: { object: {} } });
  const hook = async (payload: string, header: string) => worker.fetch(new Request('https://api.aikidomusubi.com/stripe/webhook', {
    method: 'POST', headers: { 'stripe-signature': header, 'content-type': 'application/json' }, body: payload
  }), env);

  it('refuses a bad signature with 400', async () => {
    expect((await hook(event, 't=1,v1=deadbeef')).status).toBe(400);
  });
  it('handles an event once and acknowledges a repeat without doing it again', async () => {
    const s = new Stripe('sk_test_unit');
    const header = await s.webhooks.generateTestHeaderStringAsync({
      payload: event, secret: env.STRIPE_WEBHOOK_SECRET, cryptoProvider: Stripe.createSubtleCryptoProvider()
    });
    const first = await hook(event, header);
    expect(first.status).toBe(200);
    expect(await first.text()).toBe('ok');
    const again = await hook(event, header);
    expect(await again.text()).toBe('ok (repeat)');
  });
});

describe('emails', () => {
  const env = testEnv();
  it('the confirmation carries every date, the terms and the withdrawal form, and escapes names', async () => {
    await member.confirmation({ env, lang: 'es', to: 'ana@example.com', toName: 'Ana', hello: 'Ana' }, {
      people: [
        { slot: 1, name: '<b>Ana</b> García', cat: 'adult', rate: 'general', kind: 'full', venue: null, sc: null, bym: null, amount: 99 },
        { slot: 2, name: 'Marc García', cat: 'adult', rate: 'general', kind: 'family', venue: null, sc: null, bym: null, amount: 54 },
        { slot: 3, name: 'Lía García', cat: 'youth', rate: 'general', kind: 'family', venue: null, sc: null, bym: '2014-03', amount: 30 }
      ],
      period: 'quarterly', signupMs: Date.parse('2027-01-20T17:04:00Z'), anchorMs: Date.parse('2027-02-05T08:00:00Z'),
      todayAmount: 30.99, method: { type: 'sepa_debit', last4: '3000' }, processing: true, under14: true, keikogi: 3,
      scVenues: [], withdrawBy: Date.parse('2027-02-03T12:00:00Z'), termsVersion: '2027-01'
    });
    const m = outbox[0];
    expect(m.subject).toBe('Inscripción hecha: 3 personas, trimestral');
    expect(m.html).toContain('&lt;b&gt;Ana&lt;/b&gt;');
    expect(m.html).not.toContain('<b>Ana</b>');
    for (const s of ['30,99', '5 de febrero de 2027', '183', 'mayo, agosto, noviembre y febrero', '3 de febrero de 2027',
      'Formulario de desistimiento', 'Associació Aikido Musubi', 'domiciliación SEPA acabada en 3000', '3 keikogi']) {
      expect(m.html).toContain(s);
    }
    expect(m.text).toContain('Formulario de desistimiento');
    expect(m.text).not.toMatch(/<(p|table|td|a) /);
  });
  it('renders in all four languages', async () => {
    for (const lang of ['es', 'ca', 'en', 'ja'] as const) {
      await member.renewal({ env, lang, to: 'x@example.com', toName: 'X', hello: 'X' }, {
        chargeMs: Date.parse('2027-05-05T08:00:00Z'), fromMs: Date.parse('2027-05-05T08:00:00Z'), toMs: Date.parse('2027-08-04T08:00:00Z'),
        method: { type: 'card', last4: '4242' }, period: 'quarterly',
        people: [{ slot: 1, name: 'X Y', cat: 'adult', rate: 'general', kind: 'full', venue: null, sc: null, bym: null, amount: CATALOG.prices.quarterly.adults.fee }]
      });
    }
    expect(outbox.map((m) => m.subject)).toEqual([
      'Tu cuota se renueva el 5 de mayo: 99\u00a0€',
      'La teva quota es renova el 5 de maig: 99\u00a0€',
      'Your membership renews on 5 May: 99\u00a0€',
      '5月5日に会費が更新されます：99ユーロ'
    ]);
    expect(outbox[1].text).toContain("4 d'agost de 2027");
  });
});
