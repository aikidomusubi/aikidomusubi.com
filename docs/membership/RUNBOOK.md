# Online signup: day to day

What the dojo does by hand, and how. Most of it starts from an email in
`admin@aikidomusubi.com`. Commands run from `services/membership/`; add
`--mode live` for the real thing (and `--mode test` when practising).

## The panel: start here

**`https://api.aikidomusubi.com/panel/`** (in test mode,
`https://membership-test.aikidomusubi.workers.dev/panel/`). Everything below that
has a button in an email also has one there, and the panel is the easier way.

- **Signing in:** type `admin@` or `info@aikidomusubi.com` and a six-digit code arrives
  at that address. No password. Nobody else can get a code; who can is `PANEL_USERS` in
  `wrangler.toml` (after the colon, the name the panel greets them by).
- **Pendiente** is the to-do list: paper forms to collect, keikogi to hand over,
  sports-centre cards to check, people turning 17, payments that failed.
- **Miembros**: search by name or email, filter, open a family: each person's status,
  the plan, a short history (with who pressed what), and the actions.
- Everyday buttons work at once and offer **Deshacer** right after. The ones that change
  what a family pays, or end a membership, ask first and show the amounts.
- **Ayuda** answers the usual questions in the volunteer's own words.

Money (payments, refunds, the card or account) stays in Stripe: every family has a
**Pagos y recibos en Stripe** button. Adding or removing a person or changing the period
is still `npm run plan` (below), because the whole family is re-priced.

## Every new signup

The notice says who, which plan, the first charge, and what is left:

- **The paper enrolment form**, one per person, with the guardian's signature for a
  minor and the image release. Press **Recibida** for each, in the email or the panel.
  The digest on the 20th lists any still missing after two weeks. An invited member
  (moving over from the bank) has one on file already and is not asked.
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
- **Paper forms** still missing two weeks after signing up.
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

**Leaving a quarterly or annual plan early, with a refund** (terms, section 8): in the
panel, open the family → **Baja ahora, devolviendo los meses no empezados**. It keeps the
current monthly fee of the household for each month of the period already started and
refunds the rest (annual, 17 and over, leaving in the fourth month: 360 − 4 × 39 = 204 €),
ends the membership at once and emails the family the amount. No reason is needed, and
no health or other evidence should be asked for. A monthly plan has nothing to refund.

**Cancel by email or in person:** in the panel, open the family →
**Dar de baja al final del periodo**. (Or Dashboard → Subscriptions → Cancel → **At the
end of the period**.) The family gets the confirmation email by itself either way, and
**Anular la baja** in the panel undoes it before the date.

## A withdrawal (within 14 days)

The email says whether the address has a membership. If it has, the request is first
under **Pendiente → Desistimientos** in the panel. Press **Resolver…**: it shows each
payment, what is kept and what goes back, and one button does the rest, within 14 days
of the request:

- refunds each payment by the same means it was paid,
- ends the membership at once (no more charges),
- emails the family the amount, which the acknowledgement promised.

**The amount does not change with the day you do it.** The law has the member pay for
the days until they told us, so it is worked out at the moment of the request, which
the form stamped on the membership. Settling it a week later gives the same figure.

**After the 14 days** it is a cancellation, not a withdrawal: the panel says so and
offers **Dar de baja…** (end of the paid period, no refund) or **Quitar de la lista…**.

**A first SEPA payment still being confirmed** cannot be refunded yet; the panel says
so and the request waits. Come back in a few days.

Without the panel, the same figure from the command line, then refund and cancel
**Immediately** in the Dashboard:

```bash
npm run refund -- --mode live --sub sub_123 --at 2027-01-27T21:14
```

## Former members, and coming back

**Miembros → Antiguos miembros** lists every membership that has ended, newest first,
with how it ended (baja, desistimiento, impago). Nothing can be pressed there.

Coming back is just signing up again **with the same email**. Stripe keeps one customer,
so the history is together, and the new membership says "Ya fue miembro de … a …".
Under the terms (section 14) the keikogi is one per person: whoever had theirs handed
over the first time is not promised another. A paper form is asked again, as for any
signup. A different email is a new person as far as Stripe knows.

## Editing the metadata by hand

When a button has expired. Dashboard → Subscriptions → the subscription → Metadata:

| Key | Meaning |
|---|---|
| `m1`, `m2`… | `cat=adult;rate=general;kind=full`; for the members' rate `rate=sc;venue=espronceda;sc=pending` |
| `m1_name` … | the person's name |
| `keikogi` | `due` → `paid` → `ready` → `delivered` |
| `keikogi_due` | who has not had theirs yet: `m1,m3` |
| `paper_due` | whose paper form is still to collect: `m2,m3`. Absent for an invited member |
| `period`, `catalog_version`, `terms_version` | the plan, the price list, the terms accepted |

Change `sc=pending` to `sc=verified` to mark a card checked; remove `mN` from
`keikogi_due` when one is handed over, or from `paper_due` when a form arrives. The
panel does all three; this is for when it cannot be reached.

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
