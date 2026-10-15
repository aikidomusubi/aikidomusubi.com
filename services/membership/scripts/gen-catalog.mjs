// Turns the site's own data files into the JSON the Worker bundles.
//
// ONE SOURCE. _data/fees.yml is the price list /cuotas/ renders and the one the
// signup page prices from; _data/membership.yml holds the URLs, the terms
// version and every message the page and the server share; the emails' words
// are in _data/membership_emails.yml. The Worker reads all three through this
// file and nothing else, so a price or a sentence is never typed twice.
//
// Runs before every test, dev session and deploy (see package.json). The
// output is gitignored: it is derived, and a stale committed copy is exactly
// the drift this exists to prevent.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse } from 'yaml';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..', '..');
const read = (f) => parse(readFileSync(join(root, '_data', f), 'utf8'));

const fees = read('fees.yml');
const membership = read('membership.yml');
const emails = read('membership_emails.yml');
const schedule = read('schedule.yml');
const venues = read('venues.yml');
const footer = read('footer.yml');
const config = parse(readFileSync(join(root, '_config.yml'), 'utf8'));

// The organisation's names, from the three places a rename touches (CLAUDE.md):
// `title` in _config.yml and `org` in _data/footer.yml. Strings in the
// membership files say {org} and {title}; nothing types either name.
const site = {
  title: config.title,
  org: footer.ui.org,
  org_ja: footer.ui.org_ja,
  cif: footer.ui.cif,
  address: String(footer.ui.address).replace(/<br\s*\/?>/g, ', ')
};

// The sports-centre rows name a timetable location (`espronceda`); the name a
// person reads is the venue's, resolved the way _layouts/fees.html does it.
const venueNames = {};
for (const r of fees.members.rows) {
  const loc = schedule.locations.find((l) => l.id === r.venue);
  const v = loc && venues.venues.find((x) => x.id === loc.slug);
  if (!v) throw new Error(`fees.yml members row ${r.venue}: no venue found`);
  venueNames[r.venue] = v.name;
}

// fees.yml carries a great deal of page copy the server never needs. Only the
// parts that price something travel.
const out = {
  fees: {
    catalog_version: fees.catalog_version,
    year: fees.year,
    effective_from: fees.effective_from,
    periods: fees.periods.map((p) => ({ id: p.id, months: p.months, name: p.name, unit: p.unit })),
    categories: fees.categories.map((c) => ({ id: c.id, name: c.name })),
    prices: fees.prices,
    family: { amount: fees.family.amount },
    members: { rows: fees.members.rows }
  },
  site,
  venues: venueNames,
  membership,
  emails,
  // The panel's mark is the site's own favicon, not a redrawing of it.
  knot: readFileSync(join(root, 'icons', 'musubi2-knot.svg'), 'utf8').trim()
};

mkdirSync(join(here, '..', 'src', 'generated'), { recursive: true });
writeFileSync(join(here, '..', 'src', 'generated', 'data.json'), JSON.stringify(out, null, 1));

// The pricing engine is scripts/pricing.js, the file the signup page loads. It
// is a plain script with a CommonJS export, which the Worker's bundler and the
// test runner each treat a little differently; this wraps the same source as an
// ES module so both import one thing the same way.
const pricing = readFileSync(join(root, 'scripts', 'pricing.js'), 'utf8');
writeFileSync(join(here, '..', 'src', 'generated', 'pricing.mjs'),
  '// GENERATED from scripts/pricing.js by scripts/gen-catalog.mjs. Do not edit.\n' +
  'const module = { exports: {} };\n' + pricing + '\nexport default module.exports;\n');
console.log('catalog: fees', out.fees.catalog_version, '· membership terms', membership.terms_version);
