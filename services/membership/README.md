# services/membership

The Cloudflare Worker behind online signup and fee collection, at
`api.aikidomusubi.com`. Spec: "Aikido Musubi — Online Membership Signup & Stripe
Billing Spec", 14 October 2026. Setup: `docs/membership/SETUP.md`. Day to day:
`docs/membership/RUNBOOK.md`.

The site is static, so this holds the four things that need a server: pricing a
signup and handing it to Stripe Checkout (`/checkout`), hearing back from Stripe
(`/stripe/webhook`), the withdrawal function (`/withdrawal`), the admin emails'
buttons (`/admin/a`), and a daily job. It stores no personal data of its own:
Stripe is the record, and the household lives in the subscription's metadata.

## One source for everything

| What | Where | Read by |
|---|---|---|
| prices | `_data/fees.yml` | `/cuotas/`, the signup page, this Worker, `stripe:setup` |
| the pricing rules | `scripts/pricing.js` | the signup page and this Worker, the same file |
| words, URLs, terms version | `_data/membership.yml` | the signup page and this Worker |
| email copy | `_data/membership_emails.yml` | this Worker |
| organisation names | `_config.yml` `title`, `_data/footer.yml` `org` | everything, as `{org}` and `{title}` |

`npm run catalog` (run before every test, dev session and deploy) turns those into
`src/generated/`, which is not committed.

## Commands

```bash
npm test                # 89 tests: pricing, validation, routes, emails, the panel
npm run typecheck
npm run dev             # a local Worker on :8787; without a Stripe key it ends at the thank-you page
npm run deploy          # the TEST Worker; live is `npx wrangler deploy --env live`
node scripts/a11y.mjs   # axe over the built membership pages and the panel (also part of `npx gulp qa`)
```

The tools, each documented at its top: `stripe:setup`, `invite`, `plan`, `refund`,
`migrate-prices`, `retention`. They read secrets from `.dev.vars` (test) or
`.live.vars` (live), both gitignored; `.dev.vars.example` lists the names.

## Layout

```
src/index.ts        routes and the cron entry
src/checkout.ts     /checkout: validate, price, create the Checkout Session
src/validate.ts     the rules of spec 6.2, field by field
src/webhook.ts      Stripe's events: emails, keikogi, renewal notices
src/actions.ts      every change a person makes (email buttons and panel alike), its
                    history in KV; re-pricing a household
src/panel/          /panel/, the dojo's back office: sign-in by emailed code (auth),
                    families and the to-do list from Stripe (model), the pages
                    (views, style), and invented families for local work (demo)
src/cron.ts         the daily job: keikogi, orphans, the 1st and the 20th
src/withdrawal.ts   /withdrawal
src/refund.ts       what a withdrawal gives back
src/invite.ts       invite tokens (signed, single use, no email inside)
src/meta.ts         the subscription metadata format
src/email/          layout, member emails, admin emails, the Brevo adapter
scripts/            the command-line tools and the catalogue generator
test/               vitest
```

## Where this departs from the spec, and why

- **The rate is per person**, not per household, because the spec's own pricing rule
  is per person (3.2). Metadata is therefore `m1` + `m1_name` per person rather than
  the flat `m1_cat`, `m1_price`…: six people with flat keys would pass Stripe's 50-key limit.
- **The payer is picked from the people listed**, so the page never asks a name twice.
  A Customer is created before Checkout with that name; abandoned ones are deleted
  by the daily job after a day.
- **Keikogi after the first full period and the 14 days**, not on enrolment.
- **One active membership per email**: a second signup is refused with "write to us".
- **No renewal notice before the first full charge**: the confirmation states it.
- **Invites carry the first charge's month**, so the bank remittance and Stripe never
  overlap; a remittance list arrives on the 1st while members move over.
- **Buttons in admin emails** instead of hand-edited metadata, and **a panel at
  `/panel/`** (15 October 2026) for the volunteer who runs the memberships: the to-do
  list, the members, one family's status and history. Sign-in is a code emailed to the
  addresses in `PANEL_USERS` only. It also records the **paper enrolment form** per
  person (`paper_due`), which the spec left to memory.
- **Payment methods** come from a payment-method configuration (card and SEPA), because
  this API version no longer takes `payment_method_types` on Checkout.
- **sports-centre lookup keys** use the venue ids of `fees.yml` (`sc_sant_adria_...`), not
  the spec's `marina_besos`, so the price list stays the single source.
