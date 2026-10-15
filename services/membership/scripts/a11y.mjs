// axe-core over the membership pages, in the state a person actually sees.
//
// tools/qa.py reads the built HTML, so it cannot see what scripts build — the
// steps, the live totals, the review table, the error summary. That is the
// exact gap CLAUDE.md records for the calendar's buttons. This drives the
// signup in headless Chrome through all four steps, with an error shown on
// the way, in all four languages, at desktop and phone widths, and runs axe
// (WCAG 2.0, 2.1 and 2.2, A and AA) at every stop. Zero violations allowed
// (spec 5.5).
//
// The dojo's panel (/panel/) is the Worker's, not Jekyll's, so
// scripts/panel-serve.ts runs the Worker locally with the demo families, and
// the panel is USED here in Chrome, not just loaded: sign in with the emailed
// code, press Recibida, Deshacer, open a family, a confirmation, sign out.
// Each stop is audited, at the same two widths. A button that does nothing in
// a real browser fails here even when every unit test passes.
//
// A11Y_SHOTS=<dir> also saves a screenshot of every panel stop at each width.
//
//   node scripts/a11y.mjs [path/to/_site]       exit 1 on any violation
//
// Uses the Chrome already installed (puppeteer-core), and a tiny static
// server over _site, so it needs no network and no dev server.
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { extname, join, normalize } from 'node:path';
import { mkdirSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline';
import { createRequire } from 'node:module';
import puppeteer from 'puppeteer-core';

const require = createRequire(import.meta.url);
const AXE = await readFile(require.resolve('axe-core/axe.min.js'), 'utf8');
const SITE = process.argv[2] ?? join(import.meta.dirname, '..', '..', '..', '_site');
const CHROME = [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'
].find(existsSync);
if (!CHROME) { console.log('a11y: no Chrome found — skipped'); process.exit(0); }
if (!existsSync(SITE)) { console.log(`a11y: ${SITE} does not exist — build first`); process.exit(1); }

const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.png': 'image/png', '.json': 'application/json' };
const panelProc = spawn('node', ['--experimental-strip-types', '--no-warnings', join(import.meta.dirname, 'panel-serve.ts')],
  { cwd: join(import.meta.dirname, '..'), stdio: ['ignore', 'pipe', 'inherit'] });
const PANEL = await new Promise((resolve, reject) => {
  const rl = createInterface({ input: panelProc.stdout });
  rl.once('line', (l) => resolve(`http://localhost:${JSON.parse(l).port}`));
  panelProc.once('exit', (c) => reject(new Error(`panel-serve exited ${c}`)));
});
panelProc.stdout.resume();

const server = createServer(async (req, res) => {
  let p = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^(\.\.[/\\])+/, '');
  let file = join(SITE, p);
  try { if ((await stat(file)).isDirectory()) file = join(file, 'index.html'); } catch { /* 404 below */ }
  try {
    res.writeHead(200, { 'content-type': TYPES[extname(file)] ?? 'application/octet-stream' });
    res.end(await readFile(file));
  } catch { res.writeHead(404); res.end('not found'); }
});
await new Promise((r) => server.listen(0, r));
const ORIGIN = `http://localhost:${server.address().port}`;

const PAGES = {
  es: { signup: '/inscripcion/', others: ['/inscripcion/gracias/', '/miembros/', '/desistimiento/', '/desistimiento/recibido/', '/condiciones-de-la-cuota/', '/cuotas/'] },
  ca: { signup: '/ca/inscripcio/', others: ['/ca/inscripcio/gracies/', '/ca/membres/', '/ca/desistiment/', '/ca/condicions-de-la-quota/'] },
  en: { signup: '/en/sign-up/', others: ['/en/sign-up/thank-you/', '/en/members/', '/en/withdrawal/', '/en/membership-terms/'] },
  ja: { signup: '/ja/sign-up/', others: ['/ja/sign-up/thank-you/', '/ja/members/', '/ja/withdrawal/', '/ja/membership-terms/'] }
};

const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ['--no-first-run'] });
let failures = 0;
const seen = new Set();

async function audit(page, label) {
  // The cookie banner is not this page's business, and it is audited elsewhere.
  // The site fades every page in; measuring contrast mid-fade reports colours
  // nobody sees, so wait for every animation to finish.
  await page.evaluate(async () => {
    document.getElementById('cookieBanner')?.remove();
    // From the top: once scrolled, the site's sticky nav sits over whatever
    // passes under it, and axe reports those as crowded targets. That is a
    // property of a scroll position, not of the page.
    window.scrollTo({ top: 0, behavior: 'instant' });
    // Scrolling back is itself a change, so the wait comes after it. A step
    // change scrolls the page and shrinks the nav; returning to the top
    // un-shrinks it, a 0.28s transition nav.js starts from a rAF. About 100ms
    // in, the utility strip is half open and clips the language links, and axe
    // reported them as undersized targets (1 run in 3, 2026-10-15) — at rest
    // and fully shrunk they pass. So: two frames for nav.js to apply its state,
    // then wait out every running animation and transition, and look again in
    // case one finishing started another.
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    for (let run; (run = document.getAnimations().filter((a) => a.playState === 'running')).length;) {
      await Promise.all(run.map((a) => a.finished.catch(() => null)));
    }
  });
  if (!(await page.evaluate(() => typeof window.axe !== 'undefined'))) await page.evaluate(AXE);
  const r = await page.evaluate(async () => {
    const out = await window.axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] } });
    return out.violations.map((v) => ({ id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.slice(0, 3).map((n) => n.target.join(' ')) }));
  });
  for (const v of r) {
    const key = `${label.split(' ')[0]}|${v.id}|${v.nodes[0]}`;
    if (seen.has(key)) continue;
    seen.add(key);
    failures++;
    console.log(`  FAIL ${label}: ${v.id} (${v.impact}) — ${v.help}\n       ${v.nodes.join('\n       ')}`);
  }
}

// One stop in the panel: audited, checked for sideways scroll, photographed.
async function stop(page, name, width) {
  await audit(page, `/panel/${name} @${width}`);
  if (await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)) {
    failures++; console.log(`  FAIL /panel/${name} @${width}: the page scrolls sideways`);
  }
  if (process.env.A11Y_SHOTS) {
    mkdirSync(process.env.A11Y_SHOTS, { recursive: true });
    await page.screenshot({ path: join(process.env.A11Y_SHOTS, `${name}-${width}.png`), fullPage: true });
  }
}

async function expectText(page, sel, text, what) {
  const got = await page.$eval(sel, (el) => el.textContent).catch(() => '');
  if (!got.includes(text)) throw new Error(`${what}: expected "${text}" in ${sel}, got "${got.trim().slice(0, 80)}"`);
}

const submit = (page, sel) => Promise.all([page.waitForNavigation({ waitUntil: 'networkidle0' }), page.click(sel)]);

async function panel(page, width) {
  const client = await page.createCDPSession();
  await client.send('Network.clearBrowserCookies');
  await page.goto(`${PANEL}/panel/`, { waitUntil: 'networkidle0' });
  await expectText(page, 'h1', 'Entrar en el panel', 'not signed in goes to the sign-in page');
  await stop(page, 'entrar', width);
  await page.type('#email', 'admin@aikidomusubi.com');
  await submit(page, 'form button[type=submit]');
  await expectText(page, 'h1', 'Escribe el código', 'the email form');
  await stop(page, 'codigo', width);
  const code = await (await fetch(`${PANEL}/__code`)).text();
  if (!/^\d{6}$/.test(code)) throw new Error('no code was emailed');
  await page.type('#code', code);
  await submit(page, 'form button[type=submit]');
  await expectText(page, 'h1', 'Alberto', 'the code form');
  await stop(page, 'pendiente', width);
  await submit(page, '.task form button[type=submit]');
  await expectText(page, '.toast', 'recibida', 'pressing Recibida');
  await stop(page, 'pendiente-hecho', width);
  await submit(page, '.toast form button');
  await expectText(page, '.toast', 'Deshecho', 'pressing Deshacer');
  await page.goto(`${PANEL}/panel/miembros`, { waitUntil: 'networkidle0' });
  await stop(page, 'miembros', width);
  await submit(page, '.fam a.open');
  await expectText(page, '#fam-h', '', 'opening a family');
  await stop(page, 'familia', width);
  await page.goto(`${PANEL}/panel/confirmar?a=age&s=sub_demoSerra001&n=2&back=p`, { waitUntil: 'networkidle0' });
  await expectText(page, 'h1', '17 o más', 'the confirmation');
  await stop(page, 'confirmar', width);
  await submit(page, '.sheet form button[type=submit]');
  await expectText(page, '.toast', 'Pol pasa', 'confirming');
  await page.goto(`${PANEL}/panel/confirmar?a=withdraw&s=sub_demoFont0001&back=p`, { waitUntil: 'networkidle0' });
  await expectText(page, 'h1', 'desistimiento', 'the withdrawal confirmation');
  await stop(page, 'desistimiento', width);
  await page.goto(`${PANEL}/panel/miembros?f=antiguos`, { waitUntil: 'networkidle0' });
  await stop(page, 'antiguos', width);
  await submit(page, '.fam a.open');
  await expectText(page, '.banner', 'terminó', 'a former membership');
  await stop(page, 'antiguo', width);
  await page.goto(`${PANEL}/panel/ayuda`, { waitUntil: 'networkidle0' });
  await stop(page, 'ayuda', width);
  await page.goto(`${PANEL}/__empty`, { waitUntil: 'networkidle0' });
  await stop(page, 'vacio', width);
  await page.goto(`${PANEL}/panel/`, { waitUntil: 'networkidle0' });
  await submit(page, '.top .out');
  await expectText(page, 'h1', 'Entrar en el panel', 'signing out');
}

async function state(page) {
  return page.evaluate(() => ({
    step: document.querySelector('.su-step:not([hidden])')?.getAttribute('data-step'),
    errors: [...document.querySelectorAll('#su-errors li')].map((l) => l.textContent)
  }));
}

// A real mouse click, aimed where a person would aim: at a control in the
// middle of the screen. page.click and Locator.click both treat a control as
// "in view" once any of it intersects the viewport and then fire at its centre
// — and at 375px the bottom 52px of the viewport is the pinned legal strip.
// A chip or a "next" button resting at the foot of the screen took the click
// on .ft-strip instead: on 2026-10-15, one run in six lost a chip on
// /ja/sign-up/, the walk carried on, and the failure surfaced two steps later
// as "Node is either not clickable" on a step-2 radio still hidden. (Focus is
// not the problem: membership.less's scroll-padding keeps a focused field
// clear of the strip; this is only about where a synthetic pointer lands.)
//
// So centre it first; the Locator then waits for it to be enabled and hold
// the same box for two frames. A radio or checkbox must then BE checked, and
// `next` must reach the next step — a lost click is named where it happens,
// not two steps later.
async function click(page, sel) {
  await page.$eval(sel, (el) => el.scrollIntoView({ block: 'center', behavior: 'instant' }));
  await page.locator(sel).click();
  const checked = await page.$eval(sel, (el) => (el.type === 'radio' || el.type === 'checkbox') ? el.checked : null);
  if (checked === false) throw new Error(`clicked ${sel} and it is not checked`);
}

async function next(page, n) {
  await click(page, `.su-step[data-step="${n}"] .su-next`);
  const s = await state(page);
  if (s.step !== String(n + 1)) throw new Error(`step ${n} did not advance: ${s.errors.join(' / ')}`);
}

async function signup(page, lang, path) {
  await page.goto(ORIGIN + path, { waitUntil: 'networkidle0' });
  await audit(page, `${path} step 1`);
  // Continue with nothing filled in: the error summary and inline errors.
  await click(page, '.su-step[data-step="1"] .su-next');
  await audit(page, `${path} step 1 errors`);
  await page.type('#su-p1-given', lang === 'ja' ? '花子' : 'Ana');
  await page.type('#su-p1-family', lang === 'ja' ? '山田' : 'García');
  await click(page, '#su-p1 input[name="p1_cat"][value="adult"]');
  await click(page, '#su-add');
  await page.type('#su-p2-given', lang === 'ja' ? '花' : 'Lía');
  await page.type('#su-p2-family', lang === 'ja' ? '山田' : 'García');
  await click(page, '#su-p2 input[name="p2_cat"][value="youth"]');
  await page.select('#su-p2-bm', '3');
  await page.select('#su-p2-by', '2014');
  await click(page, '#su-p2 input[name="p2_rate"][value="sc"]');
  await page.select('#su-p2-venue', 'sant-adria');
  await audit(page, `${path} step 1 filled`);
  await next(page, 1);
  await audit(page, `${path} step 2`);
  await click(page, 'input[name="period"][value="monthly"]');
  await next(page, 2);
  await audit(page, `${path} step 3`);
  await click(page, 'input[name="holder"][value="p1"]');
  await page.type('#su-email', 'ana@example.com');
  await click(page, '#su-adult');
  await click(page, '#su-guardian');
  await next(page, 3);
  await audit(page, `${path} step 4`);
}

for (const width of [1280, 375]) {
  const page = await browser.newPage();
  await page.setViewport({ width, height: 900 });
  for (const [lang, p] of Object.entries(PAGES)) {
    try {
      await signup(page, lang, p.signup);
    } catch (e) {
      failures++;
      console.log(`  FAIL ${p.signup} @${width}: could not walk the steps (${e.message})`, JSON.stringify(await state(page)));
    }
    for (const o of p.others) {
      await page.goto(ORIGIN + o, { waitUntil: 'networkidle0' });
      await audit(page, `${o} @${width}`);
    }
  }
  try {
    await panel(page, width);
  } catch (e) {
    failures++;
    console.log(`  FAIL /panel/ @${width}: could not use the panel (${e.message}) at ${page.url()}`);
  }
  await page.close();
}

await browser.close();
server.close();
panelProc.kill();
console.log(failures ? `\n  a11y: ${failures} violation(s)` : '  a11y: 0 violations on the membership pages (4 languages, 2 widths, every step) and the panel (signed in, used and signed out in Chrome)');
process.exit(failures ? 1 : 0);
