// npm run stripe:setup -- --mode test|live [--webhook-url URL] [--confirm-live]
//
// Makes Stripe match _data/fees.yml and the spec, and can be run as often as
// you like: it creates what is missing and changes nothing that is already
// right (spec 7.1).
//
//   products        "Cuota general" and "Cuota con abono municipal"
//   prices          one per lookup key of the current catalogue version; a
//                   price is NEVER edited — a new fees.yml version makes new ones
//   payment methods a configuration with card and SEPA Direct Debit on and
//                   everything else off (Apple Pay and Google Pay ride on card)
//   customer portal configured as in spec 9.2, with its no-code login link,
//                   which is written into _data/membership.yml for the site
//   webhook         with --webhook-url: the endpoint and its events; its signing
//                   secret goes straight into `wrangler secret put` and is
//                   never printed
//
// Needs the FULL secret key of that mode in .dev.vars / .live.vars. Live mode
// refuses to run without --confirm-live.
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import Stripe from 'stripe';
import { CATALOG, M, SITE, t, url } from '../src/data.ts';
import { PMC_NAME } from '../src/stripe.ts';
import { args, die, euros, mode, pkg, repo, stripeFor, vars } from './_cli.ts';

const a = args();
const m = mode(a);
if (m === 'live' && !a['confirm-live']) die('live mode changes the real Stripe account: add --confirm-live once you mean it');
const v = vars(m);
const st = stripeFor(m, v.STRIPE_SECRET_KEY);
const APP = 'membership';
const say = (s: string) => console.log(s);

const EVENTS: Stripe.WebhookEndpointCreateParams.EnabledEvent[] = [
  'checkout.session.completed', 'checkout.session.async_payment_failed', 'invoice.paid',
  'invoice.payment_failed', 'invoice.upcoming', 'customer.subscription.updated', 'customer.subscription.deleted'
];

async function product(kind: 'general' | 'sc', name: string, description: string) {
  const found = await st.products.search({ query: `metadata['app']:'${APP}' AND metadata['kind']:'${kind}'` });
  if (found.data[0]) return found.data[0];
  say(`  + product ${name}`);
  return st.products.create({ name, description, metadata: { app: APP, kind } });
}

function wanted() {
  const out: { key: string; amount: number; product: 'general' | 'sc'; interval: 'month' | 'year'; count: number; nick: string }[] = [];
  const iv = (p: string) => (p === 'annual' ? { interval: 'year' as const, count: 1 } : { interval: 'month' as const, count: CATALOG.periods[p].months });
  const word = { adult: '17+', youth: '≤16' };
  for (const period of Object.keys(CATALOG.periods)) {
    for (const cat of ['adult', 'youth'] as const) {
      const full = CATALOG.prices[period][cat === 'adult' ? 'adults' : 'children'].fee;
      const months = CATALOG.periods[period].months;
      for (const kind of ['full', 'family'] as const) {
        const amount = kind === 'full' ? full : full - CATALOG.family * months;
        out.push({ key: `general_${cat}_${period}_${kind}_${CATALOG.version}`, amount, product: 'general', ...iv(period),
          nick: `${word[cat]} ${period}${kind === 'family' ? ', family' : ''} ${CATALOG.version}` });
      }
    }
  }
  for (const [venue, row] of Object.entries(CATALOG.sc)) {
    for (const cat of ['adult', 'youth'] as const) {
      const amount = row[cat];
      if (amount === undefined || amount === null) continue;
      out.push({ key: `sc_${venue.replace(/[^a-z0-9]+/gi, '_')}_${cat}_monthly_${CATALOG.version}`, amount: Number(amount), product: 'sc',
        interval: 'month', count: 1, nick: `${word[cat]} ${venue} members' rate ${CATALOG.version}` });
    }
  }
  return out;
}

async function prices(products: Record<'general' | 'sc', Stripe.Product>) {
  const want = wanted();
  const have: Record<string, Stripe.Price> = {};
  for (let i = 0; i < want.length; i += 10) {
    const r = await st.prices.list({ lookup_keys: want.slice(i, i + 10).map((w) => w.key), limit: 100 });
    for (const p of r.data) if (p.lookup_key) have[p.lookup_key] = p;
  }
  let made = 0;
  for (const w of want) {
    const p = have[w.key];
    if (p) {
      if (p.unit_amount !== Math.round(w.amount * 100)) {
        die(`${w.key} exists at ${euros((p.unit_amount ?? 0) / 100)} but fees.yml says ${euros(w.amount)}.
  Prices are never edited: bump catalog_version in _data/fees.yml and run this again.`);
      }
      continue;
    }
    await st.prices.create({
      product: products[w.product].id, currency: 'eur', unit_amount: Math.round(w.amount * 100),
      recurring: { interval: w.interval, interval_count: w.count }, lookup_key: w.key, nickname: w.nick,
      tax_behavior: 'unspecified', metadata: { app: APP, catalog_version: CATALOG.version }
    }, { idempotencyKey: `price-${w.key}` });
    say(`  + price ${w.key}  ${euros(w.amount)}`);
    made++;
  }
  say(`  prices: ${want.length} wanted, ${made} created, ${want.length - made} already there`);
}

async function paymentMethods() {
  let cfg: Stripe.PaymentMethodConfiguration | undefined;
  for await (const c of st.paymentMethodConfigurations.list({ limit: 100 })) if (c.name === PMC_NAME) cfg = c;
  const on = { display_preference: { preference: 'on' as const } };
  if (!cfg) {
    cfg = await st.paymentMethodConfigurations.create({ name: PMC_NAME, card: on, sepa_debit: on, apple_pay: on, google_pay: on });
    say(`  + payment method configuration "${PMC_NAME}"`);
  }
  // Everything else off. The configuration object lists every method it
  // knows, each with its effective value; anything on that is not ours goes.
  const keep = new Set(['card', 'sepa_debit', 'apple_pay', 'google_pay']);
  const off: Record<string, { display_preference: { preference: 'off' } }> = {};
  for (const [k, val] of Object.entries(cfg as unknown as Record<string, unknown>)) {
    const dp = (val as { display_preference?: { value?: string } } | null)?.display_preference;
    if (dp && dp.value === 'on' && !keep.has(k)) off[k] = { display_preference: { preference: 'off' } };
  }
  if (Object.keys(off).length) {
    await st.paymentMethodConfigurations.update(cfg.id, off as Stripe.PaymentMethodConfigurationUpdateParams);
    say(`  payment methods switched off: ${Object.keys(off).join(', ')}`);
  }
  say('  payment methods: card and SEPA Direct Debit (Apple Pay and Google Pay ride on card)');
}

async function portal() {
  const params: Stripe.BillingPortal.ConfigurationCreateParams = {
    name: 'Cuotas',
    business_profile: {
      headline: `${SITE.org} · Cuota / Quota`.slice(0, 60),
      privacy_policy_url: url('privacy', 'es'),
      terms_of_service_url: url('terms', 'es')
    },
    default_return_url: url('members', 'es'),
    login_page: { enabled: true },
    features: {
      payment_method_update: { enabled: true },
      customer_update: { enabled: true, allowed_updates: ['name', 'address', 'phone'] },
      invoice_history: { enabled: true },
      subscription_cancel: {
        enabled: true, mode: 'at_period_end', proration_behavior: 'none',
        cancellation_reason: { enabled: true, options: ['too_expensive', 'unused', 'switched_service', 'other'] }
      },
      subscription_update: { enabled: false }
    },
    metadata: { app: APP }
  };
  let cfg: Stripe.BillingPortal.Configuration | undefined;
  for await (const c of st.billingPortal.configurations.list({ limit: 100 })) if (c.metadata?.app === APP) cfg = c;
  if (cfg) {
    const { metadata: _m, ...rest } = params;
    void _m;
    cfg = await st.billingPortal.configurations.update(cfg.id, rest as Stripe.BillingPortal.ConfigurationUpdateParams);
  } else {
    cfg = await st.billingPortal.configurations.create(params);
    say('  + customer portal configuration');
  }
  const link = cfg.login_page.url;
  if (!link) die('the portal has no login link: is the portal activated in the Dashboard (Settings > Billing > Customer portal)?');
  // Not a secret: it is the link on /miembros/. Written where the site reads it.
  const file = join(repo, '_data', 'membership.yml');
  const yml = readFileSync(file, 'utf8');
  const next = yml.replace(new RegExp(`(portal_url:[\\s\\S]*?\\n\\s+${m}: )"[^"]*"`), `$1"${link}"`);
  if (next !== yml) { writeFileSync(file, next); say(`  portal login link written to _data/membership.yml (portal_url.${m})`); }
  say(`  portal: ${link}`);
  if (!cfg.is_default) say('  NOTE: this portal configuration is not the account default; the login link above uses it anyway.');
}

async function webhook(endpoint: string) {
  let found: Stripe.WebhookEndpoint | undefined;
  for await (const w of st.webhookEndpoints.list({ limit: 100 })) if (w.url === endpoint) found = w;
  if (found) {
    await st.webhookEndpoints.update(found.id, { enabled_events: EVENTS });
    say(`  webhook ${endpoint}: events updated; its signing secret is unchanged`);
    return;
  }
  const created = await st.webhookEndpoints.create({
    url: endpoint, enabled_events: EVENTS, api_version: Stripe.API_VERSION as Stripe.WebhookEndpointCreateParams.ApiVersion,
    description: 'Cuotas: api.aikidomusubi.com'
  });
  say(`  + webhook ${endpoint} (API ${Stripe.API_VERSION})`);
  // Straight into Cloudflare, never onto the screen.
  const r = spawnSync('npx', ['wrangler', 'secret', 'put', 'STRIPE_WEBHOOK_SECRET', '--env', m === 'live' ? 'live' : ''],
    { cwd: pkg, input: created.secret, stdio: ['pipe', 'inherit', 'inherit'] });
  if (r.status !== 0) {
    say('  could not store the signing secret with wrangler. Roll it in the Dashboard (Developers > Webhooks) and run:');
    say(`    npx wrangler secret put STRIPE_WEBHOOK_SECRET${m === 'live' ? ' --env live' : ''}`);
  } else {
    say('  webhook signing secret stored in Cloudflare');
  }
}

say(`\nStripe setup · ${m} mode · catalogue ${CATALOG.version} · terms ${M.terms_version}\n`);
const general = await product('general', 'Cuota general', t({ es: 'Todas las clases, en todos los espacios.' }, 'es'));
const sc = await product('sc', 'Cuota con abono municipal', t({ es: 'Las clases del polideportivo cuyo abono se tiene, mes a mes.' }, 'es'));
await prices({ general, sc });
await paymentMethods();
await portal();
if (typeof a['webhook-url'] === 'string') await webhook(a['webhook-url']);
say('\nDone. What this cannot do is in docs/membership/SETUP.md: branding, public details, emails, retries, the restricted key.\n');
