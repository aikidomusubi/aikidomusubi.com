# Aikido Musubi — Claude Code Guide

## Project overview

Jekyll static site for **Aikido Musubi** (aikidomusubi.com), a non-profit martial arts cultural association in Badalona, Barcelona. Deployed via GitHub Pages.

## Stack

- **Jekyll** (github-pages gem) — static site generator
- **Bootstrap 5.3.3** — UI framework. `data-bs-*` attributes, `.btn-close`, `.g-0`, `.w-100`, `.fw-*`, `.ms-/.me-*`. **No jQuery.**
- **Gulp 5** — asset pipeline (LESS → CSS, JS concat/minify → `styles/all.min.css`, `scripts/all.min.js`)
- **Google Tag Manager** (GTM-KZ62VP5) — analytics
- **FullCalendar 4.3.1** (local copy in `plugins/`) — training schedule calendar. Intentionally **not** upgraded; the schedule layout is heavily customised and the upgrade is deferred.
- **GLightbox 3.2.0** — self-hosted (`scripts/`, `styles/`), lightbox for courses page

There are **no external CDN dependencies** and **no jQuery**. `scripts/default.js` is plain vanilla JS.

## Build & develop

```bash
RUBYOPT="-E utf-8:utf-8" bundle exec jekyll serve
```

`RUBYOPT` is required: the shell has an empty `LANG`, so without it the Sass
converter treats files as US-ASCII and the build dies on the first non-ASCII
character. The dev-start script sets it.

### URLs: relative for the site, absolute only for SEO

**Internal links and assets are root-relative** — `/images/foo.jpg`,
`/clases/`, `/styles/all.min.css`. Never use the `site.url` variable for these.
The site lives at the domain root (`baseurl` is empty), so root-relative paths
work unchanged on localhost and in production.

`site.url` is reserved for the places that genuinely need an absolute canonical
host, all of which live in `_includes/header.html` and `sitemap.xml`:

- `<link rel="canonical">`
- `og:url`, `og:image`, `twitter:image`
- `hreflang` alternates including `x-default`
- the `SportsClub` JSON-LD block
- every URL in the sitemap

This used to be `site.url` everywhere, which meant a locally served page pulled
its CSS, JS, images **and navigation** from the live site. Local changes were
invisible, and because the local HTML had Bootstrap 5 markup while the
production bundle it loaded was still Bootstrap 4, the dropdowns, hamburger and
right-aligned language switcher all looked broken locally while being correct.
If that combination ever reappears, look for a reintroduced absolute asset URL.

```bash
npx gulp styles scripts   # rebuild bundles after editing LESS/JS
npx gulp watch            # rebuild on change
npx gulp lint             # jshint scripts/default.js
npx gulp purge            # drop unused CSS — see the order below
```

Only four asset files ship: `all.min.css`, `all.min.js`, and the two GLightbox files. Everything Gulp consumes is in `_config.yml`'s `exclude:` list. Edit source, run Gulp, commit the compiled output.

### Unused CSS is purged, and the order matters

Bootstrap is ~235 KB of a 327 KB bundle and this site uses a fraction of it.
`gulp purge` takes `all.min.css` to ~157 KB — about 20 KB a page once brotli
has had it. **The committed `all.min.css` is the purged one**: GitHub Pages
does not run Gulp, so whatever is committed is what ships.

Full sequence when CSS changes:

```bash
npx gulp styles
RUBYOPT="-E utf-8:utf-8" bundle exec jekyll build
npx gulp purge
```

`purge` reads the **built `_site`**, not the templates, and that is not a
detail: kramdown generates `<blockquote>`, `<table>`, `<em>` and friends from
Markdown punctuation, so those tag names appear nowhere in the sources.
Purging against templates silently dropped the blockquote rules on the cookie
policy pages — caught only by diffing computed styles before and after. The
task refuses to run without a built `_site`.

Two other things keep it honest. The extractor only accepts class-shaped
tokens; the default one reads ordinary prose as class names, which is why an
earlier attempt at this saved 2–5% and was reverted. And the safelist covers
what no static analysis can see — classes that appear only once JS has run:
Bootstrap's `.show`/`.collapsing` states, everything FullCalendar builds,
GLightbox, and the cookie banner's `.is-open`.

If you use a Bootstrap class that was not previously on any page and forget to
re-purge, that class will be missing. This fails *visibly* — the dev server
serves the same committed bundle, so it looks broken immediately rather than
only in production.

Requires `@fullhuman/postcss-purgecss`, which is in `devDependencies`. Note
that `package.json` and `package-lock.json` are listed in `.gitignore` but were
committed before that entry existed, so Git still tracks them — dependency
changes do get recorded, despite what the ignore file suggests.

Jekyll does **not** prune `_site`; after changing `exclude:`, `rm -rf _site` before rebuilding or deleted files linger and look like leaks.

`.claude/dev-start.sh` opens Jekyll and Gulp in a Hyper split pane and runs automatically on the first message of a session (`UserPromptSubmit` hook in `.claude/settings.local.json`). It is idempotent.

## Multilingual structure

Four languages: **es** (default, root `/`), **ca** (`/ca/`), **en** (`/en/`), **ja** (`/ja/`).

- Each page has a `lang:` and `i18n-ref:` front-matter key
- Language-specific URL slugs: e.g., `/clases/` (es), `/classes/` (en/ca), `/classes/` (ja)
- Hreflang alternates generated in `_includes/header.html`
- Language switcher in navbar via `_includes/language-switcher.html`
- Translations data in `_data/translations.yml` (only two keys currently — most translations are inline Liquid `{% if page.lang == '...' %}` blocks)
- All four language versions of a page must be kept in sync when adding/editing content

## Collections

| Collection | Output | Notes |
|---|---|---|
| `_events/` | no | Rendered inside `courses.md` via layout |
| `_resources/` | no | Rendered inside `resources.md` via `_layouts/resource.html` |
| `_photos/` | yes | Each album is a page; displayed via modal on photos listing |
| `_videos/` | no | Rendered inside `videos.md` |

## Key files

| File | Purpose |
|---|---|
| `_config.yml` | Site-wide settings, collections, excludes |
| `_layouts/default.html` | Base layout (header + main + footer) |
| `_layouts/resource.html` | Resources page layout — renders cards from `_resources/` collection |
| `_includes/header.html` | `<head>`, full-page header SVG (homepage only), Google Tag Manager |
| `_includes/navigation.html` | Bootstrap 5 navbar with all nav links |
| `_includes/stickyBar.html` | In-page anchor nav (per-page, keyed by `i18n-ref`) |
| `_includes/footer.html` | Fixed footer with social links and copyright |
| `_includes/language-switcher.html` | Language switcher dropdown |
| `_data/translations.yml` | Shared translation strings (extend when adding new shared UI text) |
| `sitemap.xml` | **Liquid template that generates the whole sitemap** — never hand-edit the output |
| `training-schedule-{lang}.json` | Weekly training schedule data consumed by FullCalendar |
| `gulpfile.js` | Gulp tasks for CSS/JS compilation |
| `_includes/fonts-ja.css` | **Generated** `@font-face` set for the Japanese faces, inlined on `/ja/` pages — see below |
| `tools/subset-ja-fonts.py` | **Regenerates** the Japanese faces and that include — re-run after editing Japanese copy |

## Fonts — self-hosted, no third party

Nothing is fetched from `fonts.googleapis.com` or `fonts.gstatic.com`. The
files live in `/fonts/` and are served from this origin, which removes two DNS
lookups and TLS handshakes from the critical path and stops every visitor's IP
reaching Google before they have consented to anything.

**Latin (every page).** Eight static Noto Sans faces — 400/700 × roman/italic
× latin/latin-ext — declared in `styles/base.less` and compiled into
`all.min.css`. Static instances, not the variable font the CSS API now
returns: the site uses exactly two weights, and the static latin faces are
~13 KB each against ~35 KB variable.

`latin-ext` is a separate declaration and is genuinely needed — the romanised
Japanese in the copy (dōjō, jūdō, Ōsensei) uses U+014D, U+016B and U+014C,
which are outside the latin range. Splitting it keeps pages that use no macron
at ~26 KB of font.

`_includes/preload.html` preloads only the two roman latin faces. Do not add
the italic or latin-ext faces: preloading a face the page never paints costs a
download for nothing. The `crossorigin` attribute is required even though the
fonts are same-origin — without it the preload and the CSS request use
different modes and the file is fetched twice.

**Japanese (`/ja/` pages only).** `Noto Sans JP` and `M PLUS 1p` are applied
exclusively inside `html[lang="ja"]` blocks in `default.less`, so they are
declared on Japanese pages and nowhere else. This matters: the old single
Google stylesheet described all three families, so every Spanish page parsed
~90 KB (gzipped) of rules for fonts it could never use.

The three faces are **subset to the glyphs the site actually uses**, by
`tools/subset-ja-fonts.py`. Served whole, these are CJK fonts — ~6 MB across
~250 `unicode-range` chunks, with ~300 KB of `@font-face` CSS just to describe
the chunking. Subsetting takes that to three files totalling ~430 KB and under
a kilobyte of CSS, which is then **inlined** into the `<head>` by
`_includes/header.html`: at that size a separate stylesheet is pure overhead,
costing a render-blocking round trip to deliver three rules. A Japanese page
went from 1,976 KiB to 1,161 KiB total transfer.

**Re-run the subsetter after adding or editing Japanese copy:**

```bash
RUBYOPT="-E utf-8:utf-8" bundle exec jekyll build
python3 tools/subset-ja-fonts.py
```

It needs `fonttools` and `brotli`, which are deliberately not project
dependencies — install them into a throwaway venv, as the script's error
message explains. It reads the built `/ja/` pages plus
`training-schedule-ja.json` (the calendar injects that at runtime, so scanning
HTML alone would miss it), and always includes all kana, CJK punctuation and
ASCII as a safety margin so ordinary copy edits do not need a re-subset. New
**kanji** do: one outside the subset falls back to the reader's system
Japanese font — a visible mismatch, not tofu. The script prints any in-use
character it could not cover, so watch that line. `✕` in the collaboration
course titles is expected there; Noto Sans JP has never had that glyph.

`tools/` is excluded from the build — the unsubset source faces live in
`tools/ja-font-sources/` as inputs only.

## Sitemap — generated, but it has one manual obligation

`sitemap.xml` is a Liquid template. Adding, renaming or removing a page updates
the sitemap on the next build with no manual step, and uncommitted WIP pages
cannot leak into production because they do not exist when GitHub Pages builds.

**Review the generated sitemap after every content change.** Build, then check
`_site/sitemap.xml`.

What is automatic:

- one `<url>` per page carrying an `i18n-ref`
- hreflang alternates for all four languages plus `x-default` → Spanish
- images: collection-backed pages (courses, photos) read the exact filename the
  page renders from front-matter, keeping localised titles and honouring
  cross-language fallbacks; other pages match `/images/` by `i18n-ref` prefix
  and keep only files the page actually references
- `lastmod` on collection-backed index pages, which advance to the newest item
  date — publishing a course bumps the four courses pages by itself

**The one thing that is not automatic:** every page carries
`last_modified: YYYY-MM-DD` in its front-matter, and that is the `lastmod`
baseline. **When you meaningfully change a page's content, bump
`last_modified` on all four language versions.** Do not bump it for
whitespace or a typo — Google discounts `lastmod` it decides is unreliable.

Other rules:

- opt a page out with `sitemap: false` (set on the four 404 pages)
- `changefreq` and `priority` are deliberately omitted; Google ignores both
- every image entry must resolve to a file that exists — the generator only
  emits files it can see, so a broken entry means a broken reference on the page

## Resource front-matter schema

```yaml
---
layout: resource        # always "resource"
categories: Examination Guidelines   # or: Weapons Training | Application Forms | Information
title_ca: "..."
title_en: "..."
title_es: "..."
title_ja: "..."
desc_ca: "..."
desc_en: "..."
desc_es: "..."
desc_ja: "..."
file_type: pdf          # audio | code | excel | image | lines | pdf | powerpoint | video | word | zipper
file_ca: filename.pdf
file_en: filename.pdf
file_es: filename.pdf
file_ja: filename.pdf
date: 2026-01-01
---
```

Files go in `/files/` directory.

## In-progress (do NOT commit)

Two independent features are in flight and not ready to publish.

**Feature A — Photos category filter**
- `_includes/stickyBar.html` — the photos filter nav block
- `photos.md` + `ca/`, `en/`, `ja/` — the `{% include stickyBar.html %}` line
- 27 × `_photos/*.md` — the `category:` front-matter field
- `_layouts/photo.html` — the `{{ photo.photos.category }}` class and the
  `album-size-badge` span

**Feature B — Resources section**
- `_layouts/resource.html`, `_resources/`, `resources.md` + `ca/`, `en/`, `ja/`
- `graphics/file-*.svg`
- `_config.yml` — the `resources:` collection block

Always check `git status` before committing. Never `git add -A`.

**Watch for shared files.** `_config.yml`, `_layouts/photo.html` and the four
`photos.md` files each hold WIP *and* shippable changes. A plain
`git add <file>` stages the WIP too — this has already caused one bad commit
that had to be reverted. Use `git add -p` and take only the hunks you want. If
the WIP and the real change land in the *same* hunk, temporarily strip the WIP,
stage, then put it back.

## Naming conventions

### The `i18n-ref` — universal page identifier

Every page has `i18n-ref: {page-slug}-{8-char-id}` in front-matter (e.g. `events-hFZ2XXIp`). The slug is always the **English canonical name**. The 8-char suffix is Base64url-style for collision resistance. This ID propagates into every associated asset name.

### Page images — `/images/`

```
{i18n-ref}-{NN}.jpg/.webp                   standard (NN = zero-padded 2-digit seq)
{i18n-ref}-{NN}_.jpg/.webp                  alternate crop of same photo
{i18n-ref}-{NN}-{lang}.jpg/.webp            language-specific variant (map, flyer, text overlay)
{i18n-ref}-{NN}-{width}.jpg/.webp           responsive size variant (hero only: 1200/1920/2560/2880)
{i18n-ref}-{name}.jpg/.webp                 named non-sequential images (e.g. 404-24EeTTuv-godzilla)
```

Every image exists in **both `.jpg` and `.webp`**, same base name. Global shared assets (placeholder, logos) have **no page prefix**.

### Collection files — `_events/`, `_videos/`, `_photos/`, `_resources/`

```
# Courses & Videos: event date + descriptive slug
{YYYY}-{MM}-{DD}-{instructor-name}-{rank}.md
{YYYY}-{MM}-{DD}-aikido-musubi-x-{event}-{city}-{year}.md

# Photos: year prefix + slug + year repeated (album must be self-describing)
{YYYY}-{slug}-{YYYY}.md                      year precision only
{YYYY}-{MM}-{DD}-{slug}-{YYYY}.md            full date precision

# Resources: revision date + category-slug + descriptor
{YYYY}-{MM}-{DD}-{category-slug}-{descriptor}.md
```

Rank notation: `shihan-6th-dan` (title before numeric), `4th-dan` (numeric only). Multiple instructors: joined with `-and-`.

### Photo album files — `/photos/{album-slug}/`

Album slug = `photos.album` front-matter value = collection filename (without `.md`).
```
{album-slug}-{n}.jpg/.webp     n is unpadded integer, 0 = cover
```
Unpadded (not zero-padded) because albums can exceed 60 images.

### Course/resource images and PDFs — `/images/` and `/files/`

```
{i18n-ref}-{collection-item-slug}-{lang}.jpg/.webp/.pdf
```
Where `{collection-item-slug}` is identical to the collection filename (without `.md`).
Multi-language flyers concatenate langs: `-ca-es-en`.

Fees and schedule files use a descriptive segment instead:
```
fees-UjbuGtGz-fees-{year}-{detail|summary}-{lang}.pdf
training-schedule-IFMn5oCc-training-schedule-{year}-{lang}.pdf
resources-uStNjtHz-{category-slug}-{descriptor}-{lang}.pdf
```

### Graphics — `/graphics/`

```
file-{type}.svg          file type icons (audio/code/excel/image/lines/pdf/powerpoint/video/word/zipper)
file-{type}-solid.svg    solid variant
file.svg                 generic fallback
logo-{NN}.svg            numbered logo variants
logo-{NN}-{variant}.svg  logo with named variant (alt, children)
```

Third-party assets keep their original filenames (e.g. `Logotip_UB.svg`).

### HTML element IDs

```
{i18n-ref}-{descriptor}    e.g. index-8oGCaMDs-nav, events-hFZ2XXIp-nav
```

Ensures no cross-page collisions when pages share layouts.

## Important conventions

- **Bootstrap 5** — use `data-bs-*` attributes. Bootstrap 4 names (`data-toggle`, `.close`, `.no-gutters`, `.btn-block`, `.font-weight-*`, `.mr-/.ml-*`, `.media`) are gone.
- **Image format**: always provide both WebP and JPEG via `<picture>`. Put `loading="lazy"` on the `<img>` (native lazy-loading; the old `lazyload` class and lazysizes are gone). `<source>` elements need no class.
- **Inline i18n**: most text uses `{% if page.lang == 'xx' %}...{% endif %}` blocks — follow this pattern
- **IDs**: use the `i18n-ref` slug as part of element IDs to avoid collisions (e.g., `index-8oGCaMDs-nav`)
- **Anchors**: section anchors use `<hr id="section-name" class="anchor">` pattern
- **Phone**: stored in `_config.yml` as `phone`, used with `| to_integer` filter for tel: / wa.me links
