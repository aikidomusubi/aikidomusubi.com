# Connecting Instagram and Facebook to the gallery

One-off setup. Once it is done, `tools/fetch-social.py` can collect everything
you have ever posted, and the nightly workflow keeps it up to date.

Everything below happens in your own Meta account, on your own posts. **No App
Review is needed** — an app in Development mode can read the assets its own
admin owns, which is exactly what this does.

Set aside about 30 minutes.

---

## Before you start

- Your Instagram account is **Business** ✔ (you confirmed this).
- It should be **linked to the Aikido Musubi Facebook Page** — needed only for
  the Facebook album half. Instagram → Settings → Account type and tools →
  Sharing to other apps, or from the Page's Meta Business Suite.
- You are an **admin** of the Facebook Page.

---

## 1. Create the Meta app

1. Go to <https://developers.facebook.com/apps/>, log in, **Create app**.
2. App name: `Aikido Musubi website`. Contact email: yours.
3. Use case: choose **Other** → app type **Business**.
4. Create. Leave it in **Development** mode — do not submit anything for review.

You now have an app. Its only job is to hold a key that reads your own posts.

---

## 2. Get the token — as yourself, through the Page

> **If you tried "API setup with Instagram login" and hit *insufficient
> developer role*, this is why.** App roles belong to Facebook accounts. Logging
> in as `@aikidomusubi` presents an Instagram identity that holds no role on the
> app, so Meta refuses. Adding it as an Instagram Tester only counts once the
> invite is *accepted* from inside the Instagram app (Settings and privacy →
> Apps and websites → Tester invites).
>
> Do this instead. You authenticate as yourself — already the app Admin and the
> Page Admin — and the token you get reads the Page's albums **and** the
> Instagram account's posts. One token for both, and it does not expire.

1. Open the **Graph API Explorer**:
   <https://developers.facebook.com/tools/explorer/>
2. Top right, **Meta App**: choose `Aikido Musubi website`.
3. **User or Page**: leave it on *User token*.
4. **Permissions** — add these four:
   - `pages_show_list`
   - `pages_read_engagement`
   - `instagram_basic`
   - `business_management`
5. **Generate Access Token**. Log in **as yourself**, and when asked which
   Pages to allow, tick the Aikido Musubi Page. Approve.
6. Make it long-lived. Open the **Access Token Debugger**
   (<https://developers.facebook.com/tools/debug/accesstoken/>), paste the
   token, **Debug**, then **Extend Access Token** at the bottom. Copy the
   extended token.

### 3. Turn that into the three values you need

On your Mac, in the site folder. **One-off setup** — macOS's Homebrew Python
refuses system-wide installs (that is the `externally-managed-environment`
error), so the script gets its own virtualenv:

```bash
python3 -m venv .venv && .venv/bin/pip install requests pillow
```

That is already done on your machine; `.venv/` is gitignored, so it never
reaches the repository. From then on, always call the script through it:

Put the token in a file rather than typing it into each terminal. Copy the
example and fill it in:

```bash
cp .env.local.example .env.local
```

Open `.env.local`, paste the extended token into `FB_TOKEN`, then:

```bash
source .env.local
.venv/bin/python tools/fetch-social.py --discover
```

`.env.local` is gitignored, so it stays on your machine. **A token is a
password** — keep it out of chat, email and screenshots. If one does get out,
revoke it at Facebook → Settings & Privacy → Settings → Apps and Websites →
remove the app, then generate a new one.

It prints, for each Page you administer:

```
Page:        Aikido Musubi
  FB_PAGE_ID  1234567890
  FB_TOKEN    EAAG...  (full value below)
  IG_USER_ID  17841400000000000   (@aikidomusubi)
```

Those three are what everything else uses. **The Page token printed there is
the one to keep** — a Page token derived from a long-lived user token does not
expire, so there is no 60-day renewal on this route.

```bash
export FB_TOKEN="the-page-token-from-discover"
export FB_PAGE_ID="1234567890"
export IG_USER_ID="17841400000000000"
```

If `IG_USER_ID` comes back as *no Instagram account linked*, the Page and the
Instagram account are not connected yet. Fix that in Meta Business Suite →
Settings → Linked accounts, then run `--discover` again.

---

## 4. Load the back catalogue

Fill the other two values into `.env.local` from what `--discover` printed,
then in any terminal:

```bash
source .env.local
```

```bash
.venv/bin/python tools/fetch-social.py --csv > /tmp/instagram.csv
```

`--csv` writes nothing and touches nothing. It prints every post you have ever
made — type, date, URL and first line of the caption. **This is the "collect all
my Instagram URLs" list.** Open it and see that it looks right.

### The catalogue is large — do it in two passes

Your account holds **773 items** (198 reels, 521 posts, 54 Facebook albums,
going back to 2011). Downloading a thumbnail for every one of them would add
roughly 100 MB to the repository, most of it for posts that will never appear
on the site.

So: collect the *text* first, decide, then fetch images only for what you kept.

**Pass one — metadata only, no downloads:**

```bash
source .env.local
.venv/bin/python tools/fetch-social.py --metadata-only
```

Fast, and adds no images at all. Every item lands in `_data/gallery.yml` as a
few lines with `show: false` and an empty `thumb`.

**Pass two — images for the approved ones** *(after step 5 below):*

```bash
.venv/bin/python tools/fetch-social.py --thumbs
```

This finds every entry you marked `show: true` that has no image yet, asks Meta
for a fresh URL for each, and downloads it. The listing URLs from pass one
expire within days, which is why each entry keeps its `ref:` — the media id —
so the image can be fetched whenever you get round to approving it.

If you would rather not load all 773 at once, `--limit 40` takes only the
newest.

---

## 5. Approve what you want, 50 at a time

773 entries is too many to face in a text editor. `tools/triage.py` walks them
in batches, newest first:

```bash
.venv/bin/python tools/triage.py
```

```
773 to review — showing 50  (0 of 773 done, 0 kept so far)

  1  reel   2026-07-12  💐 PART 2
  2  reel   2026-07-11  🎤 ¥€$
  3  reel   2026-07-05  A warrior of the gentlest kind. Welcome, mama! ✨
  4  reel   2026-06-27  How was Michelle Feilen Sensei's class last Saturday…
  …

Keep which?  numbers / ranges / all / none / q
> 3,4,7-9
```

It writes `show: true` on the ones you named, `seen: true` on all of them, and
stops. Run it again for the next 50. Nothing is deleted — a decision is one word
in a text file, changeable at any time — and rejected items are remembered, so
they will not come back in a later batch or when the nightly job runs.

Useful arguments:

| | |
|---|---|
| `--size 25` | smaller batches |
| `--type reel` | only reels — 198 of them, and the best of your recent work |
| `--from 2024-01-01` | skip the deep archive for now |
| `--tags demo` | tag this batch's keepers (default `training`) |
| `--stats` | how far through you are |
| `q` at the prompt | stop without writing anything |

Since `--tags` applies to a whole batch, the quickest way through is to make
each batch one kind of thing: `--type reel --from 2025-01-01 --tags training`
for recent mat clips, then a pass with `--tags demo` for the fairs, and so on.
Anything you get wrong is one word in `_data/gallery.yml`.

**Then fetch the images for exactly what you kept:**

```bash
.venv/bin/python tools/fetch-social.py --thumbs
```

An entry that is `show: true` but has no image yet is skipped by the page rather
than rendering broken, so there is no wrong order to work in.

Finally, tidy the `name:` on the ones you kept. Captions make mediocre titles —
`💐 PART 2` says nothing on a tile. Only the kept ones matter, so this is a short
list, and the tags are already set.

Build and look:

```bash
RUBYOPT="-E utf-8:utf-8" bundle exec jekyll serve
```

---

## 6. Turn on the nightly job

1. On GitHub: **Settings → Secrets and variables → Actions → New repository
   secret**. Add:

   | Name | Value |
   |---|---|
   | `FB_TOKEN` | the Page token from `--discover` |
   | `FB_PAGE_ID` | the Page id |
   | `IG_USER_ID` | the Instagram account id |

2. **Actions** tab → **Gallery** → **Run workflow** to try it once by hand.
3. It runs by itself at 03:17 UTC every night from then on.

Each run commits anything new with `show: false`. Your job becomes: once a week,
open `_data/gallery.yml`, flip the good ones, push.

---

## About expiry

On this route, nothing expires. A Page access token derived from a long-lived
user token stays valid until you change your Facebook password, remove the app,
or revoke the permissions.

If you ever do have to redo it, that is steps 2 and 3 again — about five
minutes — followed by updating the `FB_TOKEN` secret.

The workflow still watches for trouble and opens an issue titled *"Gallery: the
Instagram token needs renewing"* if a run fails, so a broken connection surfaces
within a day rather than months later.

---

## If something goes wrong

- **"Insufficient developer role"** — you are on the Instagram-login route.
  Use the Page route in step 2 instead; it does not involve app roles at all.
- **`Graph API 190`** — the token was revoked or the password changed.
  Regenerate it from step 2.
- **`Graph API 200`** — a permission is missing. Re-generate the token with all
  four permissions from step 2.4 ticked.
- **`Graph API 100`** — a field name Meta has changed. Tell me the message and
  I will adjust the script.
- **No Instagram items** — `IG_USER_ID` is unset or wrong. Run `--discover`
  again and check the account is Business and linked to the Page.
- **No albums** — check `FB_PAGE_ID` is the numeric id from `me/accounts`, not
  the page's vanity name.

The script never deletes anything and never publishes anything. The worst a bad
run can do is add entries you then delete.
