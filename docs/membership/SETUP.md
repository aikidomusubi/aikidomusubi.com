# Online signup: setting it up

Everything in the repository is built and tested. What is left needs your
accounts: Stripe, Cloudflare and Brevo. This is the order to do it in, **test
mode only**. Live mode is the same steps again in December, and is at the end.

Allow about two hours, most of it waiting for Stripe to verify SEPA and for DNS.

**Two rules for the whole of this:**

- **A key or a token is a password.** It goes into `services/membership/.dev.vars`
  (test) or `.live.vars` (live), and into Cloudflare through `wrangler secret put`.
  It never goes into a chat, an email, a ticket or a screenshot, and never into git
  (both files are ignored; check with `git status` before every commit).
- **Nothing in live mode until December**, and not before the advisor has read the
  terms (see "Before launch").

Every command below runs from `services/membership/` unless it says otherwise.

```bash
cd services/membership
npm install
npm test
```

`npm test` should end with `74 passed`.

---

## 1. Stripe, test mode (about 20 minutes, plus SEPA verification)

Use the account you already have for seminars. Make sure the **Test mode** switch
at the top of the Dashboard is on.

**Business details** (Settings → Business → Public details)

- Public business name: `Aikido Musubi`
- Support email `info@aikidomusubi.com`, phone `+34 717 171 177`
- Terms of service URL: `https://aikidomusubi.com/condiciones-de-la-cuota/`
  (Checkout's terms checkbox needs this: without it every session fails)
- Privacy policy URL: `https://aikidomusubi.com/politica-privacidad/`

**Branding** (Settings → Branding): the logo, an icon, brand colour `#111314`
(black) and accent `#FFF200` (yellow). Checkout, the emails and the portal use these.

**Payment methods** (Settings → Payment methods): turn on **SEPA Direct Debit**. Stripe
asks for extra verification of the account before it can be used live; start it
now, it takes days. Do not switch anything else on or off here: the setup script
makes its own configuration, with card and SEPA only, and uses that.

**Customer emails** (Settings → Billing → search "Customer emails"), switch on:

- Successful payments (receipts)
- Failed card payments
- Expiring cards
- SEPA Direct Debit pre-debit notifications (Settings → Payment methods → SEPA)

**Subscriptions** (Settings → Billing → Subscriptions and emails):

- **Upcoming renewal events: 15 days.** This is what sends our legal renewal notice.
- **Smart Retries: on.** If all retries fail: **leave the subscription past due**
  (do not cancel it). The dojo follows up in person.

**Invoices** (Settings → Billing → Invoices): footer with
`Associació Cultural Musubi Aikido · CIF G-64799554 · Av. d'Alfons XIII, 351, 08918 Badalona`
and the VAT exemption sentence the tax advisor gives you. Until then, leave the
exemption line out rather than guess it.

**Customer portal** (Settings → Billing → Customer portal): press **Activate**.
Change nothing else. The setup script configures it.

**Team** (Settings → Team): two-step authentication on for everyone.

**Keys** (Developers → API keys, test mode):

1. The **secret key** (`sk_test_...`): reveal it and paste it into `.dev.vars` as
   `STRIPE_SECRET_KEY` (step 3 creates that file). Only the scripts use it.
2. **Create restricted key**, named `Worker (test)`, with exactly these permissions,
   everything else None:

   | Resource | Permission |
   |---|---|
   | Checkout Sessions | Write |
   | Customers | Write |
   | Subscriptions | Write |
   | Invoices | Read |
   | Prices | Read |
   | Products | Read |
   | PaymentMethods | Read |
   | Payment Method Configurations | Read |
   | Refunds | Write |

   Refunds is for the panel's **Resolver el desistimiento**, which gives the money back
   without anybody opening Stripe. A key made before 15 October 2026 lacks it: edit the
   key (Developers → API keys → the key → ⋯ → Edit) and set Refunds to Write. The
   key's value does not change, so nothing has to be put in Cloudflare again.

   Copy it (`rk_test_...`). It goes to Cloudflare in step 3, and nowhere else.

---

## 2. Brevo, the email provider (about 20 minutes, plus DNS)

1. Create an account at brevo.com (free plan: 300 emails a day, which is plenty).
2. **Senders, domains and dedicated IPs → Domains → Add a domain**: `aikidomusubi.com`.
   Brevo shows two to four DNS records (a `brevo-code` TXT, DKIM, DMARC). Add them
   **exactly as shown** in Cloudflare → aikidomusubi.com → DNS. Wait until Brevo says
   *Authenticated*.
3. **Senders → Add a sender**: name `Aikido Musubi`, email `no-reply@aikidomusubi.com`.
4. **SMTP & API → API keys → Generate**: name it `Worker`. Paste it into `.dev.vars`
   as `BREVO_API_KEY`.
5. Sign Brevo's data processing agreement (Account → Legal / GDPR). The privacy
   policy names Brevo as a processor.

**`admin@aikidomusubi.com` has to receive mail.** Every admin email and withdrawal
request goes there. If it does not exist yet, the quickest is Cloudflare →
aikidomusubi.com → Email → Email Routing → forward `admin@` to your own inbox.

---

## 3. Cloudflare, the Worker (about 20 minutes)

```bash
npx wrangler login
```

A browser window opens; approve it. Then:

**The KV store** (event ids, invites, the admin buttons' one-use tokens):

```bash
npx wrangler kv namespace create KV
```

It prints an `id`. Put it in `wrangler.toml`, replacing `REPLACE_WITH_TEST_KV_ID`.

**The secrets file.** Copy the example and fill it in:

```bash
cp .dev.vars.example .dev.vars
```

- `STRIPE_SECRET_KEY`: the `sk_test_...` from step 1
- `BREVO_API_KEY`: from step 2
- `INVITE_SIGNING_KEY` and `ADMIN_ACTION_KEY`: make each with the command below,
  one run per key
- `STRIPE_WEBHOOK_SECRET`: leave empty; step 4 fills Cloudflare's copy for you
- `EMAIL_OVERRIDE`: your own address, so that every test email comes to you

```bash
openssl rand -base64 48
```

**Deploy the test Worker:**

```bash
npm run deploy
```

It prints the Worker's address, `https://membership-test.<something>.workers.dev`.
Put that in `wrangler.toml` as `API_ORIGIN` (replacing the `REPLACE` one), then give
the Worker its secrets. Each command asks you to paste a value:

```bash
npx wrangler secret put STRIPE_SECRET_KEY
```

Paste the **restricted** key `rk_test_...` from step 1 here, not the full one.

```bash
npx wrangler secret put INVITE_SIGNING_KEY
npx wrangler secret put ADMIN_ACTION_KEY
npx wrangler secret put BREVO_API_KEY
npx wrangler secret put EMAIL_OVERRIDE
```

The last four take the same values as in `.dev.vars`. Then deploy again so the
new `API_ORIGIN` takes effect:

```bash
npm run deploy
```

Check it answers: open `https://membership-test.<something>.workers.dev/health`.
It should say `{"ok":true,"env":"test"}`.

---

## 4. The setup script (5 minutes)

```bash
npm run stripe:setup -- --mode test --webhook-url https://membership-test.<something>.workers.dev/stripe/webhook
```

It creates, and on later runs only checks:

- the two products and all 15 prices from `_data/fees.yml`
- the payment-method configuration (card and SEPA, nothing else)
- the customer portal, and writes its login link into `_data/membership.yml`
  (`portal_url.test`)
- the webhook, and puts its signing secret straight into Cloudflare. It is never
  printed.

Running it twice is safe. If a price in `fees.yml` ever differs from the one in
Stripe, it stops and tells you to bump `catalog_version`: prices are never edited.

---

## 5. A test run (30 to 45 minutes)

Point your local site at the test Worker. In the repository root, edit
`_config.dev.yml`:

```yaml
membership_endpoint: "https://membership-test.<something>.workers.dev"
```

Then restart the dev server:

```bash
bin/dev stop
```

```bash
bin/dev start
```

Open `http://localhost:4000/inscripcion/`. Stripe's test cards and IBANs are listed
at docs.stripe.com/testing. The ones you need:

| | Card or IBAN |
|---|---|
| Card that works | `4242 4242 4242 4242`, any future date, any CVC |
| Card that asks for 3-D Secure | `4000 0027 6000 3184` |
| SEPA that works | `DE89370400440532013000` |
| SEPA that fails | `DE62370400440532013001` |

**What to check** (spec 14.2):

1. A family of three, quarterly, by card. Stripe's page shows about the amount our
   step 4 showed, the yellow sentence, and the terms checkbox. You land on the thank-you page.
2. Your inbox (`EMAIL_OVERRIDE`) has our confirmation and the admin notice. In
   Stripe → Subscriptions, the subscription's next invoice is on the next 5th, and its
   metadata lists the three people.
3. The same with SEPA that works, then SEPA that fails: the failure reaches the admin
   inbox and the member's.
4. A monthly signup with someone on the Marina-Besòs rate: step 2 offers monthly
   only; the admin email has the two "abono" buttons. Press "Comprobado": a
   confirmation page, then "Hecho".
5. Sign up again with the same email: step 4 says there is already a membership.
6. `/miembros/` now shows "Ir a mi cuota". Sign in with the code; change the card;
   download a receipt; cancel. The cancellation email arrives, and so does the admin's.
7. `/desistimiento/`: send one for a test family signed up today. You and the admin both
   get an email, with date and time. In the panel it is first under **Pendiente**:
   **Resolver…** shows the refund, worked out at the moment you sent the form; confirm
   it. In Stripe the payment shows a partial refund and the subscription is cancelled;
   the family gets one email with the amount, not the ordinary "your membership has
   ended". The family is then under **Miembros → Antiguos miembros**.
8. **Time travel**, for renewals: Stripe → Billing → Test clocks → create one, copy
   its id (`clock_...`), then:

   ```bash
   npx wrangler secret put TEST_CLOCK
   ```

   Create the clock **in the same sandbox as the key** ("Cuotas pruebas"): a clock id
   from anywhere else makes every signup stop at step 4 with "No hemos podido
   continuar", and the Worker's log says `test_clock_problem`. A clock holds at most
   **three customers**, and only a **new** email lands on it: an email that has signed
   up before reuses its old customer, which is not on the clock. Use
   `you+clock1@…`, `you+clock2@…` and so on.

   New signups are then on that clock. Sign up quarterly, then advance the clock
   past the 5th (first full charge: the keikogi emails), then to 15 days before the
   next renewal (the renewal notice), then past it. Remove it afterwards with
   `npx wrangler secret delete TEST_CLOCK`.
9. With JavaScript switched off in the browser: the form still signs up.
10. Keyboard only, then VoiceOver: the four steps, an error, Stripe's page and the portal.
11. **The panel**: open `https://membership-test.aikidomusubi.workers.dev/panel/` and sign
    in as `admin@aikidomusubi.com`. In test mode the code goes to `EMAIL_OVERRIDE`, your
    own inbox, like every other test email. It greets you as Alberto. Your test families
    are under Miembros; signups from before the panel existed ask for no paper form.
    Press **Recibida** on a form, then **Deshacer**; open a family and look at its
    history; try **Dar de baja…** then **Anular la baja…** on a test family. Then the
    same on a phone. The panel needs no new Stripe permission and no new secret: only a
    deploy, so the Worker has `PANEL_USERS`.
12. **Leaving and coming back**: **Dar de baja…** on a test family: the family's page says
    so in a blue band at the top, every person carries "Baja el …", and the count under
    **Pendiente** links to them. Then cancel one immediately in Stripe and sign up again
    with the same email: the new membership says "Ya fue miembro de … a …", and anyone
    whose keikogi was handed over the first time is not promised a second.

Write down anything odd. Bring it back here and I will fix it.

---

## 6. Live mode (December, after the advisor)

The same steps, with these differences:

- Stripe: switch Test mode off and repeat step 1. The restricted key is `Worker (live)`.
- `cp .dev.vars.example .live.vars` and fill it with the **live** values. Leave
  `EMAIL_OVERRIDE` empty.
- `npx wrangler kv namespace create KV --env live` → its id into `[env.live]` in `wrangler.toml`.
- Every `wrangler secret put` gets `--env live`.
- Deploy with `npx wrangler deploy --env live`. The `custom_domain` route creates
  `api.aikidomusubi.com` in Cloudflare's DNS by itself.
- `npm run stripe:setup -- --mode live --confirm-live --webhook-url https://api.aikidomusubi.com/stripe/webhook`
- One real signup of your own at the lowest price, then cancel it and refund it.

---

## Before launch

- [ ] The legal advisor has read: the membership terms (4 languages), the privacy and
      cookie changes, the accessibility statement, the confirmation and renewal emails.
      Then remove `review_pending: true` from the four terms pages.
- [ ] The tax advisor has given the VAT exemption sentence for the invoice footer, and
      answered the Verifactu question (spec 16, point 10).
- [ ] The records of processing list "online signup and fee collection" (spec 10.3).
- [ ] The paper enrolment form no longer asks for the fee or bank details; the SEPA
      mandate PDFs are deleted from `/files/`.
- [ ] By **1 December**: the written notice to every member about the 2027 prices and
      the move to Stripe.
- [ ] January: invites (`npm run invite -- --mode live --csv members.csv --first 2027-02 --send`),
      then the remittance list arrives on the 1st of each month.
- [ ] Merge the `membership-signup` branch, build, QA, push.
- [ ] Re-check that the "Fees from 1 January 2027" line has gone from /cuotas/: the
      first build after 1 January drops it.
