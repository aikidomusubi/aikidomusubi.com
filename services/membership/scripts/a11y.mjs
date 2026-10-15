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
// The dojo's panel (/panel/) is rendered by the Worker, not by Jekyll, so
// scripts/panel-pages.ts renders it first, with the demo families, and its
// pages are checked the same way at the same two widths.
//
// A11Y_SHOTS=<dir> also saves a screenshot of every panel page at each width.
//
//   node scripts/a11y.mjs [path/to/_site]       exit 1 on any violation
//
// Uses the Chrome already installed (puppeteer-core), and a tiny static
// server over _site, so it needs no network and no dev server.
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { extname, join, normalize } from 'node:path';
import { mkdtempSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { execFileSync } from 'node:child_process';
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
const PANEL = mkdtempSync(join(tmpdir(), 'panel-pages-'));
execFileSync('node', ['--experimental-strip-types', '--no-warnings', join(import.meta.dirname, 'panel-pages.ts'), PANEL],
  { cwd: join(import.meta.dirname, '..'), stdio: ['ignore', 'ignore', 'inherit'] });
const PANEL_PAGES = ['entrar', 'codigo', 'pendiente', 'pendiente-hecho', 'miembros', 'familia', 'confirmar-17', 'confirmar-baja', 'ayuda', 'vacio'];

const server = createServer(async (req, res) => {
  let p = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^(\.\.[/\\])+/, '');
  let file = join(p.startsWith('/panel/') ? PANEL : SITE, p);
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
    await Promise.all(document.getAnimations().map((a) => a.finished.catch(() => null)));
    // From the top: once scrolled, the site's sticky nav sits over whatever
    // passes under it, and axe reports those as crowded targets. That is a
    // property of a scroll position, not of the page.
    window.scrollTo({ top: 0, behavior: 'instant' });
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

async function state(page) {
  return page.evaluate(() => ({
    step: document.querySelector('.su-step:not([hidden])')?.getAttribute('data-step'),
    errors: [...document.querySelectorAll('#su-errors li')].map((l) => l.textContent)
  }));
}

async function signup(page, lang, path) {
  await page.goto(ORIGIN + path, { waitUntil: 'networkidle0' });
  await audit(page, `${path} step 1`);
  // Continue with nothing filled in: the error summary and inline errors.
  await page.click('.su-step[data-step="1"] .su-next');
  await audit(page, `${path} step 1 errors`);
  await page.type('#su-p1-given', lang === 'ja' ? '花子' : 'Ana');
  await page.type('#su-p1-family', lang === 'ja' ? '山田' : 'García');
  await page.click('#su-p1 input[name="p1_cat"][value="adult"]');
  await page.click('#su-add');
  await page.type('#su-p2-given', lang === 'ja' ? '花' : 'Lía');
  await page.type('#su-p2-family', lang === 'ja' ? '山田' : 'García');
  await page.click('#su-p2 input[name="p2_cat"][value="youth"]');
  await page.select('#su-p2-bm', '3');
  await page.select('#su-p2-by', '2014');
  await page.click('#su-p2 input[name="p2_rate"][value="sc"]');
  await page.select('#su-p2-venue', 'sant-adria');
  await audit(page, `${path} step 1 filled`);
  await page.click('.su-step[data-step="1"] .su-next');
  await audit(page, `${path} step 2`);
  await page.click('input[name="period"][value="monthly"]');
  await page.click('.su-step[data-step="2"] .su-next');
  await audit(page, `${path} step 3`);
  await page.click('input[name="holder"][value="p1"]');
  await page.type('#su-email', 'ana@example.com');
  await page.click('#su-adult');
  await page.click('#su-guardian');
  await page.click('.su-step[data-step="3"] .su-next');
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
  for (const name of PANEL_PAGES) {
    await page.goto(`${ORIGIN}/panel/${name}.html`, { waitUntil: 'networkidle0' });
    await audit(page, `/panel/${name} @${width}`);
    const wide = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    if (wide) { failures++; console.log(`  FAIL /panel/${name} @${width}: the page scrolls sideways`); }
    if (process.env.A11Y_SHOTS) {
      mkdirSync(process.env.A11Y_SHOTS, { recursive: true });
      await page.screenshot({ path: join(process.env.A11Y_SHOTS, `${name}-${width}.png`), fullPage: true });
    }
  }
  await page.close();
}

await browser.close();
server.close();
console.log(failures ? `\n  a11y: ${failures} violation(s)` : '  a11y: 0 violations on the membership pages (4 languages, 2 widths, every step) and the panel (10 pages)');
process.exit(failures ? 1 : 0);
