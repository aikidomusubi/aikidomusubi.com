# Connecting Instagram and Facebook to the gallery

One-off setup. Once it is done, `tools/fetch-social.py` can collect everything
you have ever posted, and four commands keep it up to date whenever you feel
like running them.

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

## 5. Fetch review thumbnails

You cannot decide whether a photograph belongs in a gallery without seeing the
photograph. Eleven of the posts have the word "Post" as their entire caption.

```bash
source .env.local
.venv/bin/python tools/fetch-social.py --review-thumbs
```

Small 400px copies of every entry nobody has looked at yet, into `.cache/review/`.
That directory is **gitignored and never published** — these are throwaway
copies of posts that have not been decided on. `--limit 50` if you would rather
do it in batches.

This is separate from the 960px images an approved entry publishes, and it has
to be, because the ordering runs the other way: deciding comes before
downloading, and you cannot decide on a caption alone.

---

## 6. Review them, with the pictures

```bash
.venv/bin/python tools/review.py
```

Opens <http://localhost:8765> with **every entry loaded**, newest first. No
arguments to choose in advance: status, category, type and how many to show are
controls in the page.

```
Status     all · on the site · not on the site · never reviewed · reviewed
Category   all · no category · seminar · training · demo · travel · exams
Type       all · post · reel · album
Show       128 · 256 · 512 · 1024 · everything
```

**Click a picture** to put an entry on the site or take it off. **Click a
category chip** to add or remove it — more than one can be on, and 22 entries
legitimately carry two.

The header always says where you are and whether anything is pending:

```
769 entries · 462 on the site · 297 never reviewed        all saved   [Save]
```

When you change something it reads `3 unsaved`, the changed cards get an orange
border and say `unsaved`, and **Save** lights up. Press it and the file is
written, the page re-reads what is actually on disk, a green confirmation
appears and the header goes back to `all saved`. **The server keeps running** —
reviewing 769 entries is many sittings, not one. Closing the tab with unsaved
changes warns you first.

`Undo unsaved` throws away pending edits without touching the file. `Keep page`
and `Drop page` apply to the entries currently shown, which is why the filters
matter: they make "everything of this kind" a two-click operation.

A card carries its own state under the caption — `on the site` or `not shown`,
plus `new` if nobody has reviewed it and `unsaved` if you have just changed it.

---

## 6a. Dating media by when it was recorded

A clip of a 2015 seminar put up last month is honestly dated on Instagram and
wrong here: `_layouts/gallery.html` sorts on `date_iso` and groups the page by
its year, and Ura's archive does the same, so it lands under the wrong year in
both.

Tick the checkbox on each card you want, type a date in **Set date**, press
**Apply to selected**:

```
2015          the year, and nothing narrower is known   ->  2015-01-01
2015-06       the month                                 ->  2015-06-01
2015-06-20    the day                                   ->  2015-06-20
```

Anything else is refused rather than guessed. `select page` ticks everything
currently shown, so filtering first makes a whole category or a whole year a
two-click job.

**The posting date is not lost.** The first time an entry is redated its
original is kept in `posted:`, the card shows `posted 2026-07-05` under the
caption and the new date turns orange. **Restore posted date** puts it back for
whatever is selected, and the `posted:` line is removed once it has nothing
left to record.

The `thumb:` stem keeps the date it was minted with. It is an identifier rather
than a claim: the file exists under that name, `_data/imgw.yml` indexes it and
`sitemap.xml` names it, and renaming images to chase a metadata edit is the one
thing CLAUDE.md is most insistent about.

---

## 6b. Going back over the categories

Everything `--metadata-only` collects arrives tagged `training`, because that is
the default and nothing else can be known from a caption at collection time. So
the gallery's filter is lopsided: most published entries sit on `training`,
which is a filter with one dominant value and therefore not much of a filter.

Set **Status** to *on the site* and **Category** to *training*. That is the set
to work through. The reviewer opens on what the file already says — the
categories a card carries are lit, an entry already published has its green
border and an `on the site` label — so this is correcting rather than starting
from nothing, and `Keep page` cannot silently unpublish anything.

**No token and no fetching.** Published entries already have their pictures in
`images/` and the reviewer serves those directly. The only case needing the
network is an entry with a picture in neither place — a handful that were
reviewed, dropped, and so never had one downloaded:

```bash
source .env.local
.venv/bin/python tools/fetch-social.py --review-thumbs --all
```

`tools/retag.py` still guesses categories from captions in bulk. Use it if you
would rather start from a machine's guess and correct it; use the reviewer if
you would rather look. They write the same field.

---

## 7. Images for what survived

```bash
source .env.local
.venv/bin/python tools/fetch-social.py --thumbs
```

Every entry marked `show: true` with no image yet, at the size the site
publishes. Meta's URLs expire within days, so each one is re-requested by id at
the moment it is needed — which is why an entry keeps its `ref:`.

---

## 8. Categories

Everything arrives tagged `training`, which leaves the gallery filter with one
value and so nothing to filter. You set the category per item in the reviewer;
this is the bulk version for anything you did not:

```bash
.venv/bin/python tools/retag.py --dry-run
.venv/bin/python tools/retag.py
```

It reads the captions — a shihan's name means a seminar, 審査 a grading, a city
that is not Badalona means travel. **Always `--dry-run` first.**

---

## 9. Build and commit

```bash
npx gulp build && python3 tools/image-widths.py && npx gulp build && npx gulp qa
```

The middle step regenerates `_data/imgw.yml` so the new thumbnails get a real
`srcset` instead of a broken one. Then `git status`, stage what you meant to,
commit. **Never `git add -A`.**

---

## Doing it again, later

There is no scheduled job and that is deliberate: a nightly workflow needed
three GitHub secrets, a token that could expire without anybody noticing, and
an automation watching an account that posts a few times a month. Running four
commands when you feel like it is less machinery and the same result.

```bash
source .env.local
.venv/bin/python tools/fetch-social.py --metadata-only   # what is new
.venv/bin/python tools/fetch-social.py --review-thumbs   # pictures for it
.venv/bin/python tools/review.py                         # decide
.venv/bin/python tools/fetch-social.py --thumbs          # publish-size images
```

Then build and commit. After the backlog is cleared this is a handful of items
at a time and takes a couple of minutes.
