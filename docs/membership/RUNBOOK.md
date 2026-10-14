# Online signup: day to day

What the dojo does by hand, and how. Most of it starts from an email in
`admin@aikidomusubi.com`. Commands run from `services/membership/`; add
`--mode live` for the real thing (and `--mode test` when practising).

## Every new signup

The notice says who, which plan, the first charge, and what is left:

- **The paper enrolment form**, one per person, with the guardian's signature for a
  minor and the image release. Nothing to record online.
- **Sports-centre card** (CxEM Espronceda or Marina-Besòs rate): check it at the first
  class, then press **Comprobado** in the email. If it is not valid, press **No válido**:
  that person moves to the general fee from the next charge, the family discount is
  recalculated and the family is told.
- **Keikogi** (quarterly and annual): nothing yet. A second email arrives once the first
  full period is paid and the 14 days are over, with an **Entregado** button per person.
- **An invited member**: the notice says from which month to leave them out of the bank
  remittance.

The buttons open a page that asks you to confirm; nothing changes until you do.
Each button works once and lasts 45 days. After that, do it in the Dashboard (below).

## The 1st of the month (while members are moving over)

**Remittance list**: who already pays through Stripe this month. Leave them out of the
bank remittance. When nobody is left on the bank, set `MIGRATION_REMITTANCE_LIST =
"false"` in `wrangler.toml` and deploy.

## The 20th of the month

**The digest**, sent only when there is something in it:

- **Turning 17**: press **Aplicar y avisar**. The person moves to the 17-and-over fee
  from the next charge, after the month of their birthday, never before.
- **Unchecked sports-centre cards** older than 30 days.
- **Overdue payments**: the subscription stays active and past due; talk to the family.

## Changes people ask for

**Add or remove someone, or change the period:**

```bash
npm run plan -- --mode live --sub sub_123 --people "Ana García López:adult,Marc García López:adult,Lía García Ruiz:youth:2014-03" --period annual
```

That shows the before and after. Add `--apply --notify` to do it and email the family.
A change of period is applied at the end of the period already paid, so the billing
date stays on the 5th. **Do not change the period in the Dashboard**: it moves the
billing date to the day of the change.

What a household costs, with no Stripe at all:

```bash
npm run plan -- --people adult,adult,youth
```

**Change the email on a membership:** Dashboard → Customers → the customer → Edit.
The portal cannot.

**Cancel by email, phone or in person:** Dashboard → Subscriptions → the subscription →
Cancel → **At the end of the period**. The family gets the confirmation email by itself.

## A withdrawal (within 14 days)

The email says whether the address has a membership and suggests a refund. Then:

```bash
npm run refund -- --mode live --sub sub_123 --at 2027-01-27T21:14
```

Use the date and time from the acknowledgement. Then, within 14 days of the request:

1. Dashboard → Payments → each payment listed → Refund the amount printed.
2. Dashboard → Subscriptions → Cancel → **Immediately**.

Write to the family with the amount (the acknowledgement promised it).

## Editing the metadata by hand

When a button has expired. Dashboard → Subscriptions → the subscription → Metadata:

| Key | Meaning |
|---|---|
| `m1`, `m2`… | `cat=adult;rate=general;kind=full`; for the members' rate `rate=sc;venue=espronceda;sc=pending` |
| `m1_name` … | the person's name |
| `keikogi` | `due` → `paid` → `ready` → `delivered` |
| `keikogi_due` | who has not had theirs yet: `m1,m3` |
| `period`, `catalog_version`, `terms_version` | the plan, the price list, the terms accepted |

Change `sc=pending` to `sc=verified` to mark a card checked; remove `mN` from
`keikogi_due` when one is handed over.

## Invites

```bash
npm run invite -- --mode live --email marta@example.com --name "Marta Vidal" --first 2027-02 --send
```

`--first` is the month of the first Stripe charge, on the 5th: the first month the person
is **not** in the bank remittance. `--csv members.csv` does a list (columns `email,name,lang,first`).
Keep that CSV out of the repository and delete it after.

## A price change

1. `_data/fees.yml`: the new prices, a new `catalog_version`, the `effective_from` date.
2. `npm run stripe:setup -- --mode live --confirm-live`: creates the new prices.
3. `npm run migrate-prices -- --mode live --to <version>`: the list, nothing changes.
4. At least a month before the date: `... --apply --notify`. Each payer gets their own
   before and after.

## Once a year

- `npm run retention -- --mode live`: customers whose membership ended more than four years
  ago (until the advisor says otherwise). Delete them in the Dashboard.
- Rotate the keys (below). In the Stripe Dashboard, confirm the PCI questionnaire (SAQ A).

## Rotating a secret

Do it once a year, and at once if anybody with access leaves.

| Secret | Where to make a new one | Then |
|---|---|---|
| Stripe restricted key | Developers → API keys → roll | `npx wrangler secret put STRIPE_SECRET_KEY` |
| Stripe secret key (scripts) | Developers → API keys → roll | update `.dev.vars` / `.live.vars` |
| Webhook signing secret | Developers → Webhooks → the endpoint → Roll secret | `npx wrangler secret put STRIPE_WEBHOOK_SECRET` |
| Brevo key | SMTP & API → API keys | `npx wrangler secret put BREVO_API_KEY`, and the vars file |
| `INVITE_SIGNING_KEY` | `openssl rand -base64 48` | secret **and** vars file. Outstanding invites stop working |
| `ADMIN_ACTION_KEY` | `openssl rand -base64 48` | secret. Buttons in old emails stop working |

Add `--env live` for live.

## When something goes wrong

- **What the Worker is doing:** `npx wrangler tail` (`--env live`) shows each request:
  route, outcome and ids, never names or emails.
- **A webhook that failed:** Dashboard → Developers → Webhooks → the endpoint → the event →
  **Resend**. Every handler is safe to run twice.
- **An email that did not arrive:** Brevo → Transactional → Logs.
- **Signups fail with "no Stripe Price":** `npm run stripe:setup` was not run for this
  catalogue version.
- **A suspected breach:** roll every key above (Stripe first); check Stripe → Developers →
  Logs and `wrangler tail` for what was done; work out who is affected. If there is a risk to
  people, notify the AEPD within 72 hours (sedeagpd.gob.es) and tell those affected.
