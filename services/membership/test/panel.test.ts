// The panel: who can sign in and how, that every change needs a session and
// its token, and that the to-do list says what the demo families need.
import { describe, expect, it, beforeEach } from 'vitest';
import worker from '../src/index.ts';
import { testEnv } from './helpers.ts';
import { outbox } from '../src/email/send.ts';
import { sign } from '../src/crypto.ts';
import { demoSubscriptions } from '../src/panel/demo.ts';
import { family, tasks } from '../src/panel/model.ts';
import { greeting } from '../src/panel/views.ts';
import { keikogiGiven, leaveMath } from '../src/leave.ts';
import type { Env } from '../src/env.ts';

const API = 'https://api.aikidomusubi.com';
beforeEach(() => { outbox.length = 0; });

function form(path: string, body: Record<string, string>, cookie = '', origin = API) {
  return new Request(API + path, {
    method: 'POST',
    headers: { origin, cookie, 'content-type': 'application/x-www-form-urlencoded', 'cf-connecting-ip': '203.0.113.9' },
    body: new URLSearchParams(body).toString()
  });
}
const get = (path: string, cookie = '') => new Request(API + path, { headers: { cookie } });
const codeIn = () => /(\d{6}) es tu código/.exec(outbox.at(-1)?.subject ?? '')?.[1] ?? '';

async function signIn(env: Env, email = 'admin@aikidomusubi.com'): Promise<string> {
  await worker.fetch(form('/panel/entrar', { email }), env);
  const res = await worker.fetch(form('/panel/codigo', { email, code: codeIn() }), env);
  expect(res.status).toBe(303);
  return (res.headers.get('set-cookie') ?? '').split(';')[0];
}

describe('signing in', () => {
  it('sends nobody to the panel without a session', async () => {
    const res = await worker.fetch(get('/panel/'), testEnv());
    expect(res.status).toBe(303);
    expect(res.headers.get('location')).toBe('/panel/entrar');
  });
  it('answers an unknown address exactly like a known one, and sends it nothing', async () => {
    const env = testEnv();
    const a = await (await worker.fetch(form('/panel/entrar', { email: 'someone@example.com' }), env)).text();
    expect(outbox).toHaveLength(0);
    const b = await (await worker.fetch(form('/panel/entrar', { email: 'admin@aikidomusubi.com' }), env)).text();
    expect(outbox).toHaveLength(1);
    expect(a.replaceAll('someone@example.com', 'X')).toBe(b.replaceAll('admin@aikidomusubi.com', 'X'));
  });
  it('emails a six-digit code to the address itself, and not a second one within a minute', async () => {
    const env = testEnv();
    await worker.fetch(form('/panel/entrar', { email: ' Info@AikidoMusubi.com ' }), env);
    expect(outbox[0].to).toBe('info@aikidomusubi.com');
    expect(codeIn()).toMatch(/^\d{6}$/);
    await worker.fetch(form('/panel/entrar', { email: 'info@aikidomusubi.com' }), env);
    expect(outbox).toHaveLength(1);
  });
  it('lets the right code in once, and refuses a wrong one', async () => {
    const env = testEnv();
    await worker.fetch(form('/panel/entrar', { email: 'admin@aikidomusubi.com' }), env);
    const code = codeIn();
    const wrong = code === '000000' ? '111111' : '000000';
    expect((await worker.fetch(form('/panel/codigo', { email: 'admin@aikidomusubi.com', code: wrong }), env)).status).toBe(401);
    const ok = await worker.fetch(form('/panel/codigo', { email: 'admin@aikidomusubi.com', code }), env);
    expect(ok.status).toBe(303);
    expect(ok.headers.get('set-cookie')).toMatch(/^__Host-cuotas=.+; Path=\/; Secure; HttpOnly; SameSite=Lax/);
    expect((await worker.fetch(form('/panel/codigo', { email: 'admin@aikidomusubi.com', code }), env)).status).toBe(401);
  });
  it('gives up on a code after five wrong tries', async () => {
    const env = testEnv();
    await worker.fetch(form('/panel/entrar', { email: 'admin@aikidomusubi.com' }), env);
    const code = codeIn();
    const wrong = code === '000000' ? '111111' : '000000';
    for (let i = 0; i < 5; i++) await worker.fetch(form('/panel/codigo', { email: 'admin@aikidomusubi.com', code: wrong }), env);
    expect((await worker.fetch(form('/panel/codigo', { email: 'admin@aikidomusubi.com', code }), env)).status).toBe(401);
  });
  it('accepts the browser’s own form when it says Origin: null', async () => {
    // What a real browser sends under a no-referrer policy (the bug of 15 October).
    const req = new Request(API + '/panel/entrar', {
      method: 'POST', body: 'email=admin%40aikidomusubi.com',
      headers: { origin: 'null', 'sec-fetch-site': 'same-origin', 'content-type': 'application/x-www-form-urlencoded' }
    });
    expect((await worker.fetch(req, testEnv())).status).toBe(200);
    expect(outbox).toHaveLength(1);
  });
  it('refuses Origin: null from anywhere else', async () => {
    const req = new Request(API + '/panel/entrar', {
      method: 'POST', body: 'email=admin%40aikidomusubi.com',
      headers: { origin: 'null', 'sec-fetch-site': 'cross-site', 'content-type': 'application/x-www-form-urlencoded' }
    });
    const res = await worker.fetch(req, testEnv());
    expect(res.status).toBe(403);
    expect(await res.text()).toContain('No se ha podido hacer');
    expect(outbox).toHaveLength(0);
  });
  it('refuses a sign-in posted from another site', async () => {
    const res = await worker.fetch(form('/panel/entrar', { email: 'admin@aikidomusubi.com' }, '', 'https://evil.example'), testEnv());
    expect(res.status).toBe(403);
    expect(outbox).toHaveLength(0);
  });
});

describe('sessions', () => {
  it('greets admin@ by name and info@ without one', async () => {
    const env = testEnv();
    const a = await (await worker.fetch(get('/panel/', await signIn(env)), env)).text();
    expect(a).toMatch(/Buen(os días|as tardes|as noches), Alberto<\/h1>/);
    const b = await (await worker.fetch(get('/panel/', await signIn(env, 'info@aikidomusubi.com')), env)).text();
    expect(b).toMatch(/<h1 class="hello">Buen(os días|as tardes|as noches)<\/h1>/);
  });
  it('end when signing out, and when the address leaves PANEL_USERS', async () => {
    const env = testEnv();
    const cookie = await signIn(env);
    expect((await worker.fetch(get('/panel/ayuda', cookie), env)).status).toBe(200);
    const page = await (await worker.fetch(get('/panel/ayuda', cookie), env)).text();
    const csrf = /name="csrf" value="([^"]+)"/.exec(page)![1];
    await worker.fetch(form('/panel/salir', { csrf }, cookie), env);
    expect((await worker.fetch(get('/panel/ayuda', cookie), env)).status).toBe(303);
    const again = await signIn(env);
    expect((await worker.fetch(get('/panel/ayuda', again), { ...env, PANEL_USERS: 'info@aikidomusubi.com' })).status).toBe(303);
  });
  it('cannot be made from an email button’s token', async () => {
    const env = testEnv();
    const t = await sign({ a: 'keikogi', s: 'sub_x', n: 1, x: Date.now() + 1e6, id: 'abc' }, env.ADMIN_ACTION_KEY);
    expect((await worker.fetch(get('/panel/', `__Host-cuotas=${encodeURIComponent(t)}`), env)).status).toBe(303);
  });
});

describe('changes', () => {
  it('need the session’s own token and this origin', async () => {
    const env = testEnv();
    const cookie = await signIn(env);
    const body = { a: 'paper', s: 'sub_demoGarcia01', n: '2', back: 'p' };
    expect((await worker.fetch(form('/panel/accion', body, cookie), env)).status).toBe(403);
    expect((await worker.fetch(form('/panel/accion', { ...body, csrf: 'nope' }, cookie), env)).status).toBe(403);
    const page = await (await worker.fetch(get('/panel/', cookie), env)).text();
    const csrf = /name="csrf" value="([^"]+)"/.exec(page)![1];
    expect((await worker.fetch(form('/panel/accion', { ...body, csrf }, cookie, 'https://evil.example'), env)).status).toBe(403);
    const ok = await worker.fetch(form('/panel/accion', { ...body, csrf }, cookie), env);
    expect(ok.status).toBe(303);
    expect(ok.headers.get('location')).toContain('hecho=paper');
  });
  it('that cost money ask first, with the amounts', async () => {
    const env = testEnv();
    const cookie = await signIn(env);
    const html = await (await worker.fetch(get('/panel/confirmar?a=age&s=sub_demoSerra001&n=2&back=p', cookie), env)).text();
    expect(html).toContain('¿Pasar a Pol a la cuota de 17 o más?');
    expect(html).toMatch(/14\s€ → 24\s€ al mes/);
    expect(html).toMatch(/53\s€ → 63\s€ al mes/);
  });
});

describe('leaving and coming back', () => {
  it('puts a withdrawal first, with the refund worked out at the moment it was asked', async () => {
    const env = testEnv();
    const cookie = await signIn(env);
    const home = await (await worker.fetch(get('/panel/', cookie), env)).text();
    expect(home.indexOf('g-withdrawal')).toBeGreaterThan(-1);
    expect(home.indexOf('g-withdrawal')).toBeLessThan(home.indexOf('g-paper'));
    const ask = await (await worker.fetch(get('/panel/confirmar?a=withdraw&s=sub_demoFont0001&back=p', cookie), env)).text();
    expect(ask).toContain('¿Resolver el desistimiento de Laura Font Riera?');
    expect(ask).toMatch(/Sí, devolver \d+(,\d+)?\s€ y terminar/);
  });
  it('does not ask a withdrawing member for forms or keikogi', () => {
    const fams = demoSubscriptions(Date.now()).map((s) => family(s));
    const laura = tasks(fams).filter((t) => t.fam.id === 'sub_demoFont0001').map((t) => t.kind);
    expect(laura).toEqual(['withdrawal']);
  });
  it('lists former members apart, with why they left, and nothing to press', async () => {
    const env = testEnv();
    const cookie = await signIn(env);
    const list = await (await worker.fetch(get('/panel/miembros?f=antiguos', cookie), env)).text();
    expect(list).toContain('Familia Costa');
    expect(list).toContain('· desistimiento');
    expect(list).not.toContain('Familia García');
    const one = await (await worker.fetch(get('/panel/miembros?id=sub_demoRibas001', cookie), env)).text();
    expect(one).toContain('por desistimiento: se devolvieron 81,40');
    expect(one).not.toContain('Dar de baja');
  });
  it('says when somebody has been a member before', async () => {
    const env = testEnv();
    const cookie = await signIn(env);
    const joan = await (await worker.fetch(get('/panel/miembros?id=sub_demoPuig0001', cookie), env)).text();
    expect(joan).toContain('Ya fue miembro de');
  });
  it('makes a membership that is ending plain at the top', async () => {
    const env = testEnv();
    const cookie = await signIn(env);
    const carla = await (await worker.fetch(get('/panel/miembros?id=sub_demoVidal001', cookie), env)).text();
    expect(carla).toMatch(/class="banner info">.*Baja: la cuota termina el/s);
  });
});

describe('leaving a quarterly or annual plan early', () => {
  it('keeps the monthly fee for every month started, and refunds the rest', () => {
    const start = Date.UTC(2027, 0, 5, 8);
    // Annual, 17 and over, cancelled in the fourth month: 360 − 4 × 39 = 204.
    expect(leaveMath({ paid: 360, start, months: 12, monthly: 39, now: Date.UTC(2027, 3, 20) })).toEqual({ started: 4, keep: 156, refund: 204 });
    // Quarterly, on the first day: one month started.
    expect(leaveMath({ paid: 99, start, months: 3, monthly: 39, now: start })).toEqual({ started: 1, keep: 39, refund: 60 });
    // With the keikogi already handed over: an adult's costs 50 €.
    expect(leaveMath({ paid: 360, start, months: 12, monthly: 39, now: Date.UTC(2027, 3, 20), keikogi: 50 })).toEqual({ started: 4, keep: 206, refund: 154 });
    // Never more kept than was paid.
    expect(leaveMath({ paid: 99, start, months: 3, monthly: 39, now: Date.UTC(2027, 2, 20) })).toEqual({ started: 3, keep: 99, refund: 0 });
  });
  it('counts only the keikogi this membership handed over', () => {
    const meta = { keikogi: 'ready', keikogi_due: 'm1', keikogi_for: 'm1,m2', m1: 'cat=adult;rate=general;kind=full', m1_name: 'A B',
      m2: 'cat=youth;rate=general;kind=family', m2_name: 'C B', m3: 'cat=adult;rate=general;kind=family', m3_name: 'D B' };
    // m3 had one in an earlier membership, so this one was never for them.
    expect(keikogiGiven(meta)).toEqual({ count: 1, cost: 30 });
    expect(keikogiGiven({ ...meta, keikogi: 'paid' })).toEqual({ count: 0, cost: 0 });
  });
  it('is offered, and worked out, only for quarterly and annual families', async () => {
    const env = testEnv();
    const cookie = await signIn(env);
    const garcia = await (await worker.fetch(get('/panel/miembros?id=sub_demoGarcia01', cookie), env)).text();
    expect(garcia).toContain('devolviendo los meses no empezados');
    const carla = await (await worker.fetch(get('/panel/miembros?id=sub_demoVidal001', cookie), env)).text();
    expect(carla).not.toContain('devolviendo los meses no empezados');
    const ask = await (await worker.fetch(get('/panel/confirmar?a=leave&s=sub_demoGarcia01&back=m', cookie), env)).text();
    expect(ask).toMatch(/meses? empezados? × 77\s€ al mes/);
    // Marc's and Lía's keikogi are handed over: 50 € + 30 €.
    expect(ask).toMatch(/2 keikogi ya entregados<\/span><b>− 80\s€/);
  });
});

describe('the to-do list', () => {
  const now = Date.now();
  const fams = demoSubscriptions(now).map((s) => family(s));
  const list = tasks(fams);
  const count = (k: string) => list.filter((t) => t.kind === k).length;
  it('finds what each demo family needs', () => {
    expect(count('paper')).toBe(3);
    expect(count('keikogi')).toBe(2);
    expect(count('sc')).toBe(1);
    expect(count('age')).toBe(1);
    expect(count('money')).toBe(1);
  });
  it('asks no paper form of a member who moved over by invite', () => {
    const jordi = fams.find((f) => f.id === 'sub_demoMas00001')!;
    expect(jordi.people[0].paper).toBe('none');
  });
  it('names a household by its surname', () => {
    expect(fams[0].name).toBe('Familia García');
    expect(fams[1].name).toBe('Joan Puig Ferrer');
  });
  it('says good morning, afternoon or evening in Madrid', () => {
    expect(greeting(Date.UTC(2027, 0, 15, 8), 'Alberto')).toBe('Buenos días, Alberto');
    expect(greeting(Date.UTC(2027, 0, 15, 16), '')).toBe('Buenas tardes');
    expect(greeting(Date.UTC(2027, 0, 15, 22), '')).toBe('Buenas noches');
  });
});
