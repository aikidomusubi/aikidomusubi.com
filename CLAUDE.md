# Aikido Musubi — Claude Code Guide

## Project overview

Jekyll static site for **Aikido Musubi** (aikidomusubi.com), a non-profit martial arts cultural association in Badalona, Barcelona. Deployed via GitHub Pages.

## Stack

- **Jekyll** (github-pages gem) — static site generator
- **Bootstrap 5.3.3 — CSS only, and only some of it.** `bootstrap.bundle.min.js`
  is gone: it was loaded on every page for exactly two behaviours, the navbar
  dropdown and its collapse, both of which now live in `scripts/nav.js`. What
  remains of the framework in the bundle is layout and a few components the
  pages still mark up — `.container`, `.row`/`.col-*`, `.btn*`, `.card*`,
  `.list-group*`, `.nav-link`. Nothing uses `data-bs-*` any more.
- **Gulp 5** — asset pipeline (LESS → CSS, JS concat/minify → `styles/all.min.css`, `scripts/all.min.js`)
- **Google Tag Manager** (GTM-KZ62VP5) — analytics
- **No calendar library.** FullCalendar was removed; the weekly timetable is a CSS grid rendered at build time from `_data/schedule.yml`, and `/calendario/` is built the same way from `_data/calendar.yml`.
- **GLightbox 3.2.0** — self-hosted (`scripts/`, `styles/`), lightbox for courses page

There are **no external CDN dependencies** and **no jQuery**. Every authored
script is plain vanilla JS.

### Nav and footer are data-driven and framework-free

`_includes/navigation.html` and `_includes/footer.html` are loops over
`_data/nav.yml` and `_data/footer.yml`. Both used to write every label and URL
out four times, once per language, so adding one menu entry meant eight edits
and getting all eight right.

The footer's first two columns are **the nav's own groups**, read by id, so a
section renamed in `nav.yml` is renamed in the footer too and the two cannot
disagree.

Anything that has to line up with the page content uses the **`.page-measure()`**
mixin in `styles/nav.less`. The content column is two things — `.container` at
1140px with no padding of its own, plus `> main`'s 2/4/6rem inset — and matching
only the 1140 lines a bar up with an edge nothing is drawn on.

## QA — this is the definition of done, not an extra

**Nothing is finished until `npx gulp build && npx gulp qa` is green.** Do not
wait to be asked; do not report a change as done without it. The two commands
are separate on purpose — `qa` reads the built site, so it has to run after the
build, and keeping it out of the pipeline means it reports *everything* it finds
instead of stopping at the first failure.

```bash
npx gulp build      # lint, compile, jekyll, purge, check-css, check-assets
npx gulp qa         # the standing checks below
```

`tools/qa.py` is the list. It is a script and not a section of this document on
purpose: a written checklist drifts, exactly the way `exclude:` in `_config.yml`
drifted until eleven source files were shipping to production. Add a check to
the script, not to a list somewhere.

### What it checks, in order

1. **Tag balance** — a stray `</div>` reshapes a page silently and makes every
   later check measure the wrong thing, so this runs first.
2. **Duplicate ids** — breaks `aria-*`, `<label for>` and fragment links.
3. **Heading order** — exactly one `h1`, no skipped levels. This is what caught
   sixteen About pages shipping with no `h1` at all.
4. **Internal links and fragments** — every `href` resolves, every `#anchor`
   exists on the page it points at.
5. **Image references** — every `src` and every `srcset` candidate resolves.
   Check 4 reads only `href`, which is how 374 broken variant URLs shipped.
6. **Exam syllabus** — the cumulative kyū sheet still matches the five grades
   it is generated from. Warns rather than fails when PyYAML is absent.
7. **Sitemap** — every image it names exists on disk, and no `lastmod` is
   dated in the future. The second half is there because the Seminars pages
   produced one without anybody typing it: the sitemap advances a
   collection-backed index to its newest item, and a seminar's date is when
   it *will* happen, so booking a masterclass five months out dated the page
   2027-01-30. `sitemap.xml` clamps to the build day; this is the guard.
8. **Accessibility (markup half)** — `alt`, accessible names on links and
   buttons, `aria-*` pointing at real ids, one `<main>`, `lang`, the skip link,
   positive `tabindex`.
9. **SEO tags** — `title`, description, canonical, hreflang; duplicates counted
   **within a language only**, because the same title in `ca` and `en` is a
   legitimate hreflang pair, not duplicate content.
10. **Build hygiene** — no `.less` or unminified `.js` in `_site`.
11. **Dead CSS** (informational) — classes with no matching markup anywhere.
12. **Page weight** (informational) — gzipped total and render-blocking bytes.
13. **`last_modified`** (asks, does not assert) — it can see the source changed;
    it cannot see whether the *rendered* page did. Most large diffs here are
    refactors that move content into a layout and render identically. Bump only
    where the reader would notice.

FAIL fails the run. WARN and INFO never do — they are trends, not errors.

### Two traps in the toolchain itself

**`jekyll serve` and `npx gulp build` fight over `_site`.** The dev server
watches and rebuilds, and it sets `site.url` to `http://localhost:4000`. Run it
while building and it overwrites the build, so `qa` audits a dev build with
localhost URLs in the sitemap. `qa.py` now fails loudly when it sees that, but
the habit is: stop the server, `rm -rf _site && npx gulp build`.

**clean-css in this pipeline is from 2018 and silently drops values it does not
know.** `overflow: clip` disappears — inside `@supports` too. It was wanted to
stop full-bleed sections overflowing, and the workaround is
`.full-bleed()` in `base.less`, which subtracts a scrollbar width measured by
`scripts/default.js` and published as `--sbw`. If a modern CSS value ever
"doesn't apply", check the compiled bundle before blaming specificity.

### Approved mockups live in `docs/mockups/`, in git

Every design that was reviewed and approved before it was built is kept there,
rendered HTML and the generators that produce it. `docs` is in `exclude:`, so
it is versioned and never deployed.

They used to be generated straight into `_site/mockups/`, and `npx gulp build`
begins with `rm -rf _site`. **The whole set was lost that way** and had to be
recovered out of a conversation transcript. Never keep the only copy of
anything under `_site/`.

To look at them, render into `_site` and open `localhost:4000/mockups/`:

```bash
./docs/mockups/render.sh
```

### Browser checks — the half a script cannot do

These need a rendering engine and are run by hand when the change touches
layout, colour or focus. They are how the palette regressions and the container
bugs were actually found:

- **Colour contrast**, computed per element against its real composited
  background. The recurring trap is `opacity`/`fadeout()` on text over a tint —
  it has caused six regressions in this codebase, most recently `.tt-axis-break`
  at 2.26:1. Never eyeball it; measure it.
- **Computed-style diffing** before and after any refactor that touches
  selectors or specificity. Snapshot every element's computed properties and
  geometry, change, re-snapshot, diff. Flattening the whole prose prefix was
  proved safe this way: 4,436 elements, 27 properties each, zero differences.
- **Responsive choreography** — walk 1440 / 992 / 768 / 375 and check the column
  count steps down cleanly, nothing overflows horizontally, and no page has more
  than two left edges.
- **Focus and keyboard** — tab order, the skip link, submenus reachable with
  JavaScript blocked.
- **Lighthouse, or any axe run, on a phone viewport.** `qa.py` reads the built
  HTML, so a control that does not exist until a script has run is invisible to
  it — and the calendar's day-entry trigger is exactly that. `calendar.js` wraps
  each entry's spans in a `<button>`, the narrow layout then hides those spans
  with `display: none`, and the result was ten buttons a month with no
  accessible name at all: a plain 4.1.2 failure on the page a phone is most
  likely to be reading, sitting under a green QA run for as long as it existed.
  The button takes its name from the text it wraps now. Anything the scripts
  build has to be checked in a browser.

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

**One command does everything, in the only order that works:**

```bash
npx gulp build
```

It lints, compiles the scripts and both tiers of stylesheet, builds the site,
purges the CSS against what was built, and then **verifies** the result. It is
what you run before committing.

```bash
npx gulp watch            # development loop — fast, and deliberately not correct
npx gulp lint             # jshint, all eight authored scripts
npx gulp jekyll           # just the Jekyll build, with RUBYOPT set for you
```

Only four asset files ship: `all.min.css`, `all.min.js`, and the two GLightbox files. Everything Gulp consumes is in `_config.yml`'s `exclude:` list. Edit source, run Gulp, commit the compiled output.

### Unused CSS is purged, and `build` is what guarantees it

Bootstrap dominates the core bundle and this site uses a fraction of it.
Purging takes `all.min.css` from ~300 KB to ~110 KB. **The committed
`all.min.css` is the purged one**: GitHub Pages does not run Gulp, so whatever
is committed is what ships.

`gulp watch` rebuilds `all.min.css` **unpurged** on every LESS edit. That is
deliberate — during development you want a class to work the moment you write
it, not after the next purge. It also means the working tree spends most of its
life holding the wrong bundle, and that bundle has reached a commit before.

`gulp build` is the answer: it ends with `check-css`, which re-purges in memory
and fails the build if the file on disk is more than 2% larger than it should
be. There is no size threshold to keep up to date and no way for the check to
drift from the task it checks.

```
styles/all.min.css is not purged — 186 KB of unused CSS is still in it.
Run `npx gulp build`.
```

`purge` reads the **built `_site`**, not the templates, and that is not a
detail: kramdown generates `<blockquote>`, `<table>`, `<em>` and friends from
Markdown punctuation, so those tag names appear nowhere in the sources.
Purging against templates silently dropped the blockquote rules on the cookie
policy pages — caught only by diffing computed styles before and after. Both
`purge` and `check-css` refuse to run without a built `_site`.

Two other things keep it honest. The extractor only accepts class-shaped
tokens; the default one reads ordinary prose as class names, which is why an
earlier attempt at this saved 2–5% and was reverted. And the safelist covers
what no static analysis can see — classes that appear only once JS has run:
GLightbox, the cookie banner's `.is-open`, and the timetable, calendar, gallery
and fee grids the page scripts build.

**Keep the safelist honest.** It once also protected `navbar`, `dropdown`,
`collapse`, `modal`, `offcanvas`, `carousel`, `tooltip`, `popover`, `toast`,
`sticky-top`, `table-bordered` and `fixed-bottom`, because Bootstrap's script
applied those at runtime. That script is gone, and all twelve were found on
**zero** built pages — the safelist was preserving whole component families the
site no longer had. Removing them took `all.min.css` from **110 KB to 68 KB**.
A safelist entry is a promise that something creates that class at runtime; when
a script goes, check what it was keeping alive.

### Linting

`.jshintrc` holds the settings, each non-default one commented with the pattern
in this codebase it exists for. Lint covers **all eight authored scripts**, not
just `default.js` as it used to — the page scripts had never been linted.

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

## Images: one generated map, and no hand-written `srcset`

`srcset` used to be spelled out in each template — `-480 480w, -800 800w,
.webp 960w` — the same three widths for every image alike. It was wrong twice.
`tools/image-widths.py` only makes variants for sources above `MIN_SOURCE`, so
**374 of the 666 referenced variants were 404s**, and `960w` was a constant, so
a 720px original was advertised at 960 and the browser picked it for slots it
could not fill.

`tools/image-widths.py` writes **`_data/imgw.yml`**: one ready-made srcset per
image, naming only files that exist at widths that are true. Templates do

```liquid
{%- assign ss = site.data.imgw[image] -%}
<source type="image/webp"
        srcset="{% if ss %}{{ ss }}{% else %}/images/{{ image }}.webp{% endif %}"
        {% if ss %}sizes="…"{% endif %}>
```

so an image with no variants gets no srcset rather than a broken one. Seven
templates read it: `home.html` (×2), `event.html`, `gallery.html`,
`classes.html`, `about.html` (×2), `elsewhere.html`, `video.html`.

**Re-run it after adding or changing images, then build again** so the map
reaches the pages:

```bash
npx gulp build && python3 tools/image-widths.py && npx gulp build
```

The same run writes **`_data/imgdim.yml`**, `[width, height]` per image. Most
templates can hardcode the `<img>` dimensions because every image they show is
one shape: the Seminars page's posters are all 640x905, the discipline photos
are all 948x632. The **Elsewhere** page cannot. Its posters are other
organisations' work and arrive 1:1, 4:5, 2:3 and four other ratios besides, so
a hardcoded `width`/`height` there is a wrong aspect-ratio box and a layout
shift on every card. That page reads the map instead.

    {%- assign dim = site.data.imgdim[img] -%}

Its CSS follows from the same fact. The Seminars page can `object-fit: cover` a
poster into a 640:905 column because filling it crops nothing that can be seen;
on Elsewhere that would take 29% off the top and bottom of the square one. So
`styles/seminars.less` ends with a `body.elsewhere-Kp8vR2Qs` block that mounts
the poster instead of cropping it.

`qa.py`'s **image references** check reads every `src` and every `srcset`
candidate and fails on any that does not resolve — `check_links` only ever read
`href`, which is why this was invisible for so long.

**Measure `sizes`, never read it off the grid template.** The gallery declared
`24rem` because that was the `minmax()` floor; the tile is actually drawn at
305px. A `sizes` that over-declares makes the browser fetch a size up on every
viewport. Put the real numbers in, taken from `getBoundingClientRect()` at 1440
and at 375.

## `?v=` is derived from the file, not typed

There were twenty-two hand-written `?v=N` tokens across `header.html`,
`footer.html` and `preload.html`, each needing a bump whenever its file
changed. They drifted, as the excludes and the safelist did before them:
`ura.min.js` changed with `?v=5` left in place, so returning visitors kept
running the old script — it cost an hour of debugging a fix that was already
correct. `ura.min.css` was `?v=3` on its stylesheet link and `?v=5` on its own
preload, and `all.min.css` was `?v=8` and `?v=5`: two cache entries for one
file, which turns a preload into a second download instead of a head start.

`gulp stamp` hashes every built bundle and writes `_data/assets.yml`; the
templates read `{{ site.data.assets["ura.min.js"] }}`. The token changes when
and only when the file does. It runs before `jekyll` and so hashes
`all.min.css` unpurged — deliberate: the token has to *change with* the
content, not equal it, and the unpurged bundle is a pure function of the
sources. **Never write a `?v=` by hand again.**

## Rōmaji: one convention, everywhere

The glossary said `jūji-nage` and `shihō nage` — hyphen in one, space in the
other — and `suwariwaza` run together beside `hanmi handachi` spaced. Three
spellings of the same idea.

**There is no single standard to defer to here, and it is worth being straight
about that.** Modified Hepburn settles the letters — it is what Japanese
passports, road signs and the Library of Congress use — but it does not govern
how a compound technique name is broken up; the LC's own cataloguing rules
would have us write `shihonage`, which no dojo does. What exists in budō
publishing is a practice, not a standard: hyphenate the elements of a compound.

So the letters follow modified Hepburn, and the hyphens follow **the dojo's own
Birankai bokken and jō guides**, which were already set that way —
`KIRI-OTOSHI`, `KAESHI-UCHI-OTOSHI`, `KI-MUSUBI-NO-TACHI`. Using the source
documents as the authority beats inventing a house style.

**1. Modified Hepburn, with macrons.** Long vowels take a macron: `ō`, `ū`
(and `ā`, `ē`, `ī` where they occur). Never `ou`, `oh`, `uu` or a bare `o`:
`shihō-nage`, `kokyū-hō`, `ikkyō`, `jō`, `tantō`, `jōdan`, `chūdan`, `sanshō`.

**2. Hyphenate the elements of a compound.** A term built from two or more
Japanese words takes a hyphen between each — never a space, never run together:
`kote-gaeshi`, `kesa-uchi`, `maki-otoshi`, `suwari-waza`, `ushiro-tenkan`,
`hiji-kime-osae`, `kaeshi-uchi-otoshi`.

**3. A single word takes no hyphen.** `bokken`, `jō`, `tsuki`, `kesa`,
`randori`, `hanmi`, `ukemi`, `zanshin`, `suburi`, `hakama`, `tanden`.

**4. Particles are hyphenated in.** `ichi-no-tachi`, `ki-musubi-no-tachi`,
`tai-no-atari`.

**5. Rendaku is written as it is said.** The sound change is real, so it is
spelled: `kote-gaeshi` not `kote-kaeshi`, `shihō-giri`, `choku-zuki`,
`jūji-nage`, `kaeshi-zuki`.

**6. A separate qualifier takes a space.** The hyphen binds *within* a term;
a space separates one term from the next: `katate-dori gyaku-hanmi`,
`kaiten-nage uchi`, `ikkyō jōdan`, `kesa-uchi #1, #2`.

**7. Case.** The glossary sets headwords lowercase, because they are words. The
grading sheets capitalise the first element, because they are list entries:
`Kaeshi-uchi-otoshi`. Both are the same string under rule 2.

Where a name genuinely disagrees with this — a proper noun, a kata title the
federation writes its own way — the document wins and the exception is worth a
comment. Everything else follows the rules above.

### External links rot, and nothing here notices

`qa.py` checks every **internal** link on every build. It does not touch
external ones, on purpose: a build that fails because somebody else's server is
briefly down is a build that gets ignored.

That leaves them unwatched, and the reading list makes that a real liability —
it is mostly other people's URLs. Aikikai's own media page already has dead
entries on it. **Check them by hand every few months**, and after any change to
`_data/resources.yml` or `_data/links.yml`:

```bash
grep -rhoE 'https?://[^"<) ]+' _data/*.yml | sort -u | \
  while read u; do
    code=$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 12 "$u")
    [ "$code" = 200 ] || echo "$code  $u"
  done
```

Amazon and some shops answer `403` to a bare `curl` — that is a bot check, not
a dead link, so open those in a browser before removing anything. What matters
is `404` and `410`.

## The search-and-filter bar is one line on a phone

`/glosario/` and `/recursos/` carry the same control: a search box, a set of
category chips and a count, sticky under the nav. Measured at 375x667 with the
nav shrunk, it was **389px of a 667px viewport on the glossary** (twelve chips
over five rows) and **274px on Resources** (seven over four). With the 49px nav
above it, two thirds of a small phone was furniture before a single entry was
read. It is **60px** now, on both.

Below `@bp-md` the sticky line is the search, the count and a filter button, and
the chips live in a drawer that opens under it, pushes the list rather than
covering it, and closes when a chip is picked. The button then carries that
chip's label and `data-active` paints it like a chosen chip, so the state reads
without opening anything.

**From `@bp-md` nothing changed, and that is done with `display: contents`.**
The tree is `.gl-bar-in > .gl-bar-line(search, count, filter) + .gl-drawer(chips)`.
At desktop `.gl-bar-line` becomes `display: contents`, which dissolves it and
hands its three children back to `.gl-bar-in` as flex items, so `order` puts
them in the order the page has always had — search, chips, count. One tree, two
layouts, no second copy of the markup.

Three details that are load-bearing:

- **`.gl-bar-line` and `.rs-bar-line`, never `.gl-row`/`.rs-row`.** `.rs-row` is
  already *a resource* — one row of the list — so the bar's own line matched
  `.rs-wrap .rs-row`, was collected by the script as a searchable term, and had
  `hidden` set on it the moment a filter matched nothing inside it. The bar
  measured 18px and the search field measured zero. **The list owns the
  unprefixed names; prefix anything belonging to the bar with `-bar-`.**
- **`flex: 1` on the search stays inside the mobile media query.** At desktop
  the parent is a column, where `flex: 1` grows on the *vertical* axis and
  stretches the search row to fill the bar.
- **The count's unit goes off-screen on mobile, not to `display: none`.** It is
  a live region, and a hidden node is not announced: the screen reader keeps
  "12 entradas" while the eye sees "12".

The button's accessible name is a `.sr-only` phrase plus the label, so it reads
"Filtrar por categoría: Todas" and then "Filtrar por categoría: En el dojo".
That is why the visible label starts at "Todas" rather than at the word
"Filtrar" — the button always says which filter is on, and "all of them" is a
filter like any other.

**Change one of the two pages and change the other with it.** They are one
component with two sets of labels.

## "Próximamente" reads forwards; everything else reads backwards

Both `/seminarios/` and `/fuera-del-dojo/` render newest first, which is the
right reading order for a record. "Upcoming" is not a record, it is a queue, and
the useful end of a queue is the front — rendered in page order it put the
seminar fifteen months out above the one this Saturday.

`scripts/seminars.js` (which drives both pages) computes both orders once from
the DOM and reorders with `insertBefore` against `.seminar-empty`, so that
paragraph stays last where the markup puts it. "All" and "Past" are untouched.
Each card carries `data-date` for this and nothing else.

## The calendar's vocabulary, and the things easy to get wrong

`_data/calendar.yml` is the only place a dated fact is written. Everything that
has a page of its own — every seminar, masterclass and collaboration — comes
from `_events/` instead and is never copied here.

**A `change` has two shapes, and `affects` is what tells them apart.** Without
`affects` the change is day-wide: the whole timetable is on a different footing,
which is what the August entries are, and Ura's day strip replaces the day with
it. With `affects` it substitutes the one class it names — a guest teacher, a
weapons session in place of the usual open class — and the rest of that day runs
as printed. The data file documented both from the start; Ura only implemented
the first, so the monthly weapons Wednesday deleted judo, the two Barcelona
classes and Marina-Besòs from the evening along with the class it replaced.

**The match is category + start + `location`.** Not decoration: on a Wednesday,
aikido at 20:00 is one class at the dojo and a different one at CxEM Espronceda,
and matching on the first two alone swaps both.

**`routine: true` keeps an entry out of Ura's "what is coming".** That section
answers *what is news*, and something on a fixed rhythm is not news however many
times it is written down: the Saturday grading class is nineteen entries and the
weapons Wednesday is four, and between them they filled the section with two
sentences repeated. Both stay on the calendar and in Ura's day strip, which is
where a date is looked up. It sits beside `holiday: true`, which does the same
job for the thirteen statutory closures and for the same reason.

An earlier attempt folded repeats by title instead, which looked equivalent and
was not: it silently cost the monthly weapons class three of its four dates.
Suppress the repetition at the source; do not dedupe the output.

**Ura's "what is coming" sorts on date AND time.** The row is
`date|time|type|title|detail|url|key`, string-sorted. Without the time field the
rest of the row decided, which meant the *type*: 12 December read dinner,
karate, exams, open mat, masterclass — five things in alphabetical order of a
word the reader never sees. An entry with no time sorts first, which is where an
all-day entry belongs.

**A cancellation has no title, and whatever renders one has to build it.** What
is cancelled is the class named in `affects`, so the title is the category plus
the hour: "Sin clase: Aikido 19:30". The label comes from the calendar's own
`types`, in `_includes/calendar.html` and `_includes/ura.html` alike, so the two
cannot drift.

**`announce_cancellations` in `_data/ura.yml` says which of them Ura's "what is
coming" speaks for, and it lists aikido only.** Judo, iaijutsu and karate are
taught here too, and when one of them is off — most Saturdays the dojo is given
over to a masterclass or to gradings, karate is — that belongs on the calendar
and it is on the calendar. It is not news on the aikido dojo's own aside. It is
a list and not a flag so that adding a fifth art cannot silently start
announcing it. The day strip is untouched by this: a cancelled class disappears
from its day there whatever its category, because that grid answers "is there a
class on Saturday" and the honest answer is no.

**Saturday karate is cancelled by hand on the Saturdays something else has the
mat.** The overlap is derivable in principle — a Saturday `_events/` entry
against the Saturday class in `schedule.yml` — but "the mat is busy" and "the
class is off" are not the same statement, and only the dojo knows which it is. A
rule that guessed would cancel karate for a 07:30 morning class it never
touches.

**`association` is the life of the association rather than the life of the
tatami** — the general assembly, the deadline for standing for the board, the
group photograph, the two dinners a year. It exists because the only other type
that fits the shape of an added event is `extra`, which renders as "Clase
extra", and calling the winter dinner an extra class would simply be false.

**Two sorts had to be fixed to put five things on one day in order.** Liquid's
`sort` is not stable, so `C.entries | sort: 'date'` left 12 December drawing its
21:00 dinner above its 11:00 open mat. The month grid sorts each day's entries
by `start`; the agenda list carries `data-start` and `scripts/calendar.js` sorts
on date *and* clock. An entry with no time sorts first, which is where an
all-day entry belongs.

**A seminar with no poster yet is a real state.** `_layouts/event.html` renders
`.seminar-poster-soon` when `image_*` is empty: the card keeps the shape it will
have, so nothing reflows the day the artwork lands. The three alternatives were
all worse — a link to a missing JPEG, the flat yellow `placeholder.jpg` (which
tells a screen reader the instructor's name is a picture), or leaving the event
off the calendar until the poster exists, which is the one thing a calendar must
not do. `sitemap.xml` and the JSON-LD both test `img != ''` rather than `img`,
because an empty string is truthy in Liquid.

## The grading programme is content, not a PDF

`_data/exams.yml` holds the five kyū sheets, transcribed from the dojo's own
PDFs. **The PDFs are not published.** There is one copy, the page renders it,
and the browser's own print-to-PDF cannot go stale the way a second file on a
shelf can — the reasoning `_data/resources.yml` already gives for `kind: page`.

It is read in a panel over `/recursos/`, deep-linked as `?r=kyu3`. The links in
the list are real URLs, so without JavaScript that address loads the page with
the sheet open; the script turns the click into a slide. Ura links to the same
addresses, so a sheet opens on arrival instead of leaving somebody on the list.

### Each grade stores only what it ADDS

The programme is cumulative — 4th kyū is everything in 5th plus more — so
`exams.yml` records the additions and `tools/exam-sheets.py` accumulates them
into `_data/exams-sheets.yml`, one complete sheet per grade with every
technique stamped `from:`, the grade it first appears at.

This is not tidiness. Stored as five complete lists, the grades disagreed: the
1st kyū PDF had lost Udekime-nage and Maki-otoshi from yokomen, the whole jō
programme and Kata-dori nikyō. Nothing could catch that except reading all five
side by side. Storing additions makes it impossible to express, and the tool
asserts it besides.

**The sixth sheet is not rendered.** "The whole programme" IS the 1st kyū sheet
with the colours turned on, because with a cumulative programme they are the
same list. Rendering it twice was ten kilobytes of duplicate markup.

```bash
python3 tools/exam-sheets.py          # after editing _data/exams.yml
python3 tools/exam-sheets.py --check  # what qa.py runs
```

Needs PyYAML, deliberately not a project dependency: without it the QA check
**warns instead of failing**, so a missing library cannot redden a build.

### Notation, decided once

Macrons on long vowels (`Shihō-nage`, `Kokyū-hō`, `Ikkyō`, `Jō`), matching
`_data/glossary.yml`, which has spelled rōmaji that way from the start.
Compound terms hyphenated. Qualifiers follow the name, space-separated, **no
parentheses** — `Katate-dori gyaku-hanmi`, `Ikkyō jōdan`, `Kaiten-nage uchi`.
Anything that is not part of a name is a `note` and renders in italic. The
glossary carries every term the sheets use.

### The print sheet is measured, not guessed

Each sheet lands on one side of one A4. Verified by applying the compiled
`@media print` rules as `media="all"`, forcing the panel to A4's content box
(726 × 1047 px at 96 dpi) and reading the height back — the largest is 0.89 of
a page at 7.6pt in three columns.

Three things that cost an hour between them:

- **`break-inside: avoid` on a block taller than a column** pins the whole
  sheet to that block's height. Tachi-waza is ten attacks deep; four columns
  changed nothing until the rule came off. Print uses `break-inside: auto` with
  `break-after: avoid` on `h3` and `dt`, and `break-before: column` on
  tachi-waza so the areas fall in columns rather than flowing continuously.
- **The panel is inside `.page`** — Ura's is outside, because `footer.html`
  emits it after the close and this one is emitted by the layout before it. The
  print rules hide `main`, the nav and the footer, and must NOT hide `.page`.
  Hiding it hid the thing being printed, and measured as a zero-height sheet.
- **`html` is painted `@Black`** for the overscroll at the end of a dark
  footer. Both on screen (the page shortens when its scroll is locked, and the
  black canvas showed through the scrim as a black half-window) and on paper
  (a black field wherever the sheet did not reach). `html.ex-on` paints white,
  and print paints white over everything.

## Multilingual structure

Four languages: **es** (default, root `/`), **ca** (`/ca/`), **en** (`/en/`), **ja** (`/ja/`).

- Each page has a `lang:` and `i18n-ref:` front-matter key
- Language-specific URL slugs: e.g., `/clases/` (es), `/classes/` (en/ca), `/classes/` (ja)
- Hreflang alternates generated in `_includes/header.html`
- Language switcher lives in the nav's utility strip, built inline in
  `_includes/navigation.html` from the `i18n-ref` index, so it lands on the
  translation of the page you are on rather than the other language's home page.
  The old `_includes/language-switcher.html` was deleted once nothing referenced
  it.
- Translations data in `_data/translations.yml` (only two keys currently — most translations are inline Liquid `{% if page.lang == '...' %}` blocks)
- All four language versions of a page must be kept in sync when adding/editing content

## Collections

| Collection | Output | Notes |
|---|---|---|
| `_events/` | no | Seminars and masterclasses. Rendered inside `seminars.md`; the calendar reads it too |
| `_elsewhere/` | no | Things done away from the dojo. Rendered inside `fuera-del-dojo.md` |
| `_videos/` | no | Rendered inside `prensa-y-tv.md` |

`_photos/` and `_courses/` are gone. The photo albums were replaced by
`_data/gallery.yml` (albums, posts and reels in one list, filtered client-side)
and `courses` was renamed `events`. `photos.md`, `videos.md`, `courses.md` and
`_layouts/photo.html` no longer exist; the pages are `galeria.md`,
`prensa-y-tv.md` and `seminars.md`.

## Key files

| File | Purpose |
|---|---|
| `_config.yml` | Site-wide settings, collections, excludes |
| `_layouts/default.html` | Base layout (header + main + footer) |
| `_layouts/resource.html` | Resources page layout — renders cards from `_resources/` collection |
| `_includes/header.html` | `<head>`, the homepage hero, the homepage `<h1>`, Google Tag Manager |
| `_includes/navigation.html` | The menu — a loop over `_data/nav.yml`, no framework |
| `_includes/stickyBar.html` | In-page anchor nav (per-page, keyed by `i18n-ref`) |
| `_includes/footer.html` | The footer and the pinned legal strip — a loop over `_data/footer.yml`; also closes `.page` and loads the scripts |
| `_includes/calendar-entry.html` | One calendar entry **and its detail panel** |
| `_data/translations.yml` | Shared translation strings (extend when adding new shared UI text) |
| `sitemap.xml` | **Liquid template that generates the whole sitemap** — never hand-edit the output |
| `_data/schedule.yml` | **The** weekly timetable — categories, levels, venues and every class. The timetable page, the calendar and the classes page all read it |
| `_data/nav.yml` | **The** menu: groups, labels and per-language URLs. The footer's first two columns read it too |
| `_data/footer.yml` | The footer: the invitation band, the column headings, the legal links, and the association's name and CIF (copied from `aviso-legal.md`) |
| `_data/imgw.yml` | **Generated** — one `srcset` per image; see the images section |
| `_data/imgdim.yml` | **Generated** by the same tool — `[width, height]` per image, for `<img>` on pages whose images are not all one shape |
| `_data/assets.yml` | **Generated** by `gulp stamp` — the `?v=` cache tokens |
| `_data/exams.yml` | The five kyū syllabus sheets — see the syllabus section |
| `_data/exams-cumulative.yml` | **Generated** by `tools/exam-cumulative.py` |
| `_data/calendar.yml` | Dated entries — gradings, closures, changes, and the association's own dates. Seminars come from `_events/` instead |
| `_data/classes.yml` | The Classes page: the four disciplines and their programmes |
| `_data/about.yml` | The four About topics, plus the instructors-in-training band that closes the Association page |
| `_data/gallery.yml` | Every album, post and reel, plus the filter chips |
| `_data/venues.yml` | The three dojos: addresses, entrances, plan overlays |
| `styles/nav.less` | The nav, and the `.page-measure()` mixin everything aligns to |
| `styles/footer.less` | The footer and the pinned strip |
| `scripts/nav.js` | Dropdowns, the mobile panel, the shrink on scroll |
| `gulpfile.js` | Gulp tasks for CSS/JS compilation |
| `_includes/fonts-ja.css` | **Generated** `@font-face` set for the Japanese faces, inlined on `/ja/` pages — see below |
| `tools/subset-ja-fonts.py` | **Regenerates** the Japanese faces and that include — re-run after editing Japanese copy |

## Layout: one scale, one column, one measure

Three tokens in `styles/base.less` decide every horizontal dimension on the
site. Change them there, never in a component.

```less
@bp-sm/@bp-md/@bp-lg/@bp-xl   576 / 768 / 992 / 1200
@page-max                     1140px, the outer column
@gut-sm/@gut-md/@gut-lg       2rem / 4rem / 6rem, the gutter
@measure                      43.25rem (692px), the reading measure
```

**The column is elastic.** `.container` is `width: 100%; max-width: @page-max`
with the gutter as its padding — it fills the viewport until it reaches 1140px
and then stops. Bootstrap's stepped `.container` (540/720/960/1140) is
overridden: those tiers made the layout jump sideways at every breakpoint and
sit in a 960px box with 120px of dead margin either side for the whole
992–1200 range.

**There are two verticals on a page and no more.** Headings, rules and
components use the full column; long-form blocks — `p`, `ul`, `ol`, `dl`,
`blockquote`, `pre`, `table`, `figure` — are held to `@measure` and centred
inside it.

This replaced **a second, hidden inset layer**. `> p` and `> ul` used to carry
`padding: 0 2/3/4/8rem !important` once per breakpoint, `> table` and the
cookie card carried the same as margins through a `.prose-inset()` mixin, and
every other element carried none — so the `<blockquote>` on the cookie policy
ran 256px wider than the paragraph above it, and the legal pages looked inset
while the component pages did not. Twenty rules became one. `@measure` is
43.25rem precisely because that is what the old 8rem paddings produced at
desktop: the prose did not move, everything else came into line with it.

`> p:first-of-type` is the lede — centred, and allowed the full column rather
than the measure.

**Anything that must line up with the content** uses `.page-measure()` from
`styles/nav.less`, which reads the same tokens. The nav and the footer both do.

### The prose prefix is `.page main`, and it is deliberately that short

Everything under `<main>` used to be written as one five-level LESS nest —
`html { body { .page { .container { > main {` — so every rule compiled with a
`html body .page .container > main` prefix at specificity **(0,2,3)**. Fifty-four
rules carried it, and anything wanting to override one needed `!important`.

The five levels are five sibling blocks now and the prefix is `.page main`
(0,1,1). Verified behaviour-neutral: 4,436 elements across nine pages, 27
computed properties each plus geometry, **zero differences**.

**It did not remove the need for `!important`, and that was measured, not
assumed.** `.page main a` is (0,1,2); a component rule like `.ab-nav > a` is
(0,1,1), so the prose rule still wins. Stripping the flags from `about.less`
put the underline back on every sibling link and repainted three of them black.
Reverted.

The next step, if it is ever wanted, is dropping the prose rules from
`.page main X` to `main X` (0,0,2) so single-class component rules beat them
naturally. That is a real behaviour change — Bootstrap's `.btn` and
`.card-title` would start winning too — so it needs its own verification pass,
not a find-and-replace.

**Anchor targets clear the nav via `@anchor-clear`**, not JavaScript.
`scroll-margin-top` is set on `.anchor` and `:target` from the nav's resting
height, so the browser's own fragment scroll lands correctly on the first
navigation. It used to be a hardcoded `50px + 1.75rem` — the height of the
Bootstrap navbar that no longer exists — plus a load-time correction in
`default.js` measured against `.navbar.sticky-top`, an element the site has not
had for some time, so the offset evaluated to zero. Arriving from the calendar
put the event card under the nav; reloading appeared to fix it only because the
restored scroll position had already shrunk the nav.

## The footer is two objects, and `--footer-height` measures only one

`.ft` sits at the end of the page like an ordinary footer: the invitation band,
the association's details, three columns of internal links. `.ft-strip` is a
30px band **pinned to the viewport**, because Art. 10 LSSI-CE wants the legal
links reachable from anywhere, and it carries the copyright, the CIF and those
links and nothing else.

`--footer-height` is **the strip's height, not the footer's**. It is 30px, and
52px below 576px where the strip wraps to two rows — redefined in
`footer.less`, which must stay in step with `@ft-strip-h` beside it. Two things
consume it: the room reserved for the strip, and the cookie banner's offset so
it sits above rather than over it.

That reservation lives on **`.ft`, not `.page`**. `.page` is the white surface,
and a rubber-band overscroll at the end of a document lifts fixed elements in
both Safari and Chrome — with the padding on `.page` that exposed a white band
between the black footer and the black strip. `html` is painted `@Black` for
the same reason: it is the canvas that shows when the document is overscrolled.

## `exclude:` uses globs, and `check-assets` proves it

`exclude:` in `_config.yml` keeps Gulp's inputs out of `_site`. It used to name
every source file one by one and it drifted every time a file was added — at the
last count **eleven files, 65 KB of `.less` and unminified `.js`, were being
deployed to production**. It uses globs now (`styles/*.less`), and
`npx gulp build` ends with `check-assets`, which fails if any `.less` or
non-`.min.js` reaches `_site`:

```
source files reached _site — add a matching glob to `exclude:` in _config.yml:
    _site/styles/nav.less
```

Same principle as `check-css`: the guard is derived from the thing it guards, so
it cannot drift out of step with it.

## Every page starts with a skip link

WCAG 2.4.1, Level A. The nav is about twenty links; without it a keyboard or
switch user tabs through all of them on every page. It is the first thing in
`<body>`, off-screen at `left: -9999px` until `:focus` brings it back — **not**
`display: none`, because a hidden element cannot be focused.

`<main>` carries `id="main"` **and `tabindex="-1"`** in all eleven layouts. The
tabindex is what makes the jump move focus rather than only the viewport;
without it the browser scrolls and the next Tab carries on from the nav.

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

**The four `latin-ext` faces are subset too**, by
`tools/subset-latin-fonts.py`. Served whole they are Google's originals and
carry all of Latin Extended-A and B, the IPA extensions and a run of currency
signs — 62 to 66 KB each against 13 KB for the corresponding `latin` face,
while the site uses **four characters** out of the lot: ō ū Ō ī. A page paid the
whole face the moment it painted one of them in that style, so the home page
carried 106 KB of font and /ura/ 88 KB against 26 KB everywhere else.

    256 KB across the four faces  ->  28 KB
    home    106 KB of font -> 49 KB    Lighthouse mobile 81 -> 90
    /ura/    88 KB         -> 34 KB    Lighthouse mobile 78 -> 90

The margin is the whole of Latin Extended-A (U+0100-017F), not just the four in
use, so a Polish surname or a Czech place name in the copy tomorrow is already
covered and no re-subset is needed for ordinary editing. The script prints any
in-use character it could not cover. **The `latin` faces are deliberately left
alone** — they are 13 KB, every page loads them, and there is nothing to remove.

**Re-run it after adding copy in a language with unusual diacritics:**

```bash
npx gulp build && python3 tools/subset-latin-fonts.py
```

Same dependencies as the Japanese subsetter, same throwaway venv, same reason
they are not project dependencies. The unsubset originals are the input and live
in `tools/latin-font-sources/`.

**FONT FILES CARRY NO `?v=` AND CANNOT BE CACHE-BUSTED.** `gulp stamp` hashes
the bundles; the `url()`s in the compiled CSS and the preloads in
`_includes/preload.html` name the fonts by plain path. With Cloudflare's browser
cache TTL at a year, a returning visitor keeps whatever face they already have
until it expires. That is harmless for a subset — the old file is a superset and
renders identically, so nobody breaks and nobody gains until their cache turns
over — but it would NOT be harmless for a face whose glyphs changed. If that
ever happens, rename the file rather than trusting a purge.

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
message explains. It reads the built `/ja/` pages plus every `_data/*.yml`
(the timetable, calendar, venue and fee pages render Japanese from data, and a
label sitting in a hidden panel would be missed by an HTML-only scan), and
always includes all kana, CJK punctuation and
ASCII as a safety margin so ordinary copy edits do not need a re-subset. New
**kanji** do: one outside the subset falls back to the reader's system
Japanese font — a visible mismatch, not tofu. The script prints any in-use
character it could not cover, so watch that line. `✕` in the collaboration
course titles is expected there; Noto Sans JP has never had that glyph.

`tools/` is excluded from the build — the unsubset source faces live in
`tools/ja-font-sources/` as inputs only.

## Sitemap — generated, but it has one manual obligation

`sitemap.xml` is a Liquid template. Adding, renaming or removing a page updates
the sitemap on the next build with no manual step, and an uncommitted page
cannot leak into production because it does not exist when GitHub Pages builds.

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

- opt a page out with `sitemap: false` (set on the four 404 pages). It also
  emits `<meta name="robots" content="noindex, follow">` — a page not worth
  listing is not worth indexing, and the four 404s were four near-copies in
  the index. One flag, both meanings, so they cannot drift apart.
- `changefreq` and `priority` are deliberately omitted; Google ignores both
- every image entry must resolve to a file that exists — the generator only
  emits files it can see, so a broken entry means a broken reference on the page

## The three location pages

`/badalona/`, `/barcelona/`, `/sant-adria-de-besos/`, in four languages, from
`_layouts/location.html` and `_data/locations.yml`. The town is a proper noun so
the slug is the same in every language.

**Three, and only where the association actually teaches.** A town with a real
room, a real timetable and a real teacher gets a page; a town we would like to
rank in does not. A page that only rearranges the same words under a different
place name is a doorway page and Google acts on those. Four guards keep these
on the right side of it:

- every fact is specific to that town's rooms — address, hours, teacher, the
  way in, the floor plan
- nothing is copied from `/clases/` or `/cuotas/`; the long version is a link,
  which is also the internal linking these pages need to be crawled at all
- the last question is per town and answers "how is this different from the
  others", which a doorway page cannot answer honestly
- what is not offered is said plainly

**Almost nothing on them is written.** The rooms come from `_data/venues.yml`,
the classes from `_data/schedule.yml`, the fee from `_data/fees.yml`, and the
three figures are counted at build time — instructors from `_data/about.yml`,
seminars from `_events/`, rooms from `venues.yml`. Move a class an hour and the
pages move with it. `_data/locations.yml` holds only what cannot be derived: the
lede, the questions, the labels and the per-town paragraph about who teaches.

**`person:` in `_data/schedule.yml` is the join to the dan grades.** The
timetable holds `P. Martín` and the association page holds `Pablo Martín` with
his grade; `person` is the key between them, so the grade is written once and
the day somebody grades there is one file to edit.

**They are linked from four places each** — the home page's venue cards (via
`page:` in `_data/home.yml`, an i18n-ref resolved per language), `/acceso/`, and
each other. A page reachable only from the sitemap is crawled rarely, ranks
badly and looks like exactly the thing it is not.

**`styles/locations.less` reproduces four components rather than importing
them.** `.lo-facts`, `.lo-steps` and the section rhythm are `home.less`'s
`.hm-facts`, `.hm-steps` and `.hm-sec` copied value for value, because those
live in a per-page bundle this page does not load and pulling in two more
stylesheets to borrow four components costs more than the components weigh.
**So keep them in step.** `.ab-faq` is the exception and is deliberately the
same class name as the About pages': one accordion on this site, not two.

The one genuinely new component is `.lo-tt`, a small timetable. `/horarios/`
has the full weekly grid and there was nothing smaller. It **sorts on the day
first and the clock second**, in `week_start`'s rotation — Monday first in es
and ca, Sunday first in en and ja — so it reads as a week rather than as a list
of hours, and it **drops the "where" column on a town with one room**, which was
thirteen identical cells on the dojo's page.

**`&` in a LESS parent selector is the whole compiled selector, not a class.**
The hero's controls were written `.lo-hero-in & { }` inside `.page main
a.lo-btn`, which compiles to `.lo-hero-in .page main a.lo-btn` — a `.page`
inside the hero, which cannot exist. Not one of those rules ever matched, so
what shipped was the black-on-white pair over a dark photograph: the secondary
button drew @Black text in a 13%-black ring on the scrim and the note beside it
drew `--lo-mute` on the same ground, both illegible, and the primary was black
where the design is yellow. **When the rule is "this element inside that
ancestor", write the ancestor on the left.** They are `.page main .lo-hero-in
a.lo-btn` now and measure 15.9:1, 17.8:1 and 14.2:1.

**"Lo esencial" answers "when could I come", not "what is on at 20:30".** It
lists one line per discipline — the days, in `S.categories` order, which is
aikido, iaijutsu, judo, karate. It used to print one line per class, so the
dojo's fact list was the fourteen-row timetable again, above the actual
timetable and without the columns that make it readable.

**Instructor grades: the aikido team's are in `_data/about.yml`, everyone
else's are in `_data/schedule.yml`.** The aikido instructors are the
association's own teaching team and `about.yml` is where that team is written
down; `person:` on the instructor is the join. The iaijutsu, judo and karate
instructors are guests and do not belong on that list, so they carry `grade:`
beside their name in `schedule.yml` instead, and the location layout falls back
to it when there is no `person`. An instructor with neither prints no grade
line, which is a state and not an omission — P. Llorens's is not recorded.

**Badalona's "quién enseña" row is the roster; the other two towns' is derived.**
`aikido_roster: true` in `_data/locations.yml` switches it. The derived list is
right for Barcelona — it names the two people who take its two classes — but on
the dojo it mixed four arts into a line the reader takes as "who will be
teaching me", and left out the aikido instructors who teach at the other spaces
and are the same team. With the flag the row is `_data/about.yml`'s instructor
list in full, in the order that file keeps them, which is by grade. Still not
typed here, still cannot disagree with the About page. Everywhere else the
derived list is **filtered to aikido**.

The hero is the only photograph-first opening on the site, and that is on
purpose: a location page is landed on cold from a search result by somebody
deciding whether a place is for them. Everywhere else opens with
`page-head.html` and should stay that way. All three carry **the home page's
hero art**, named once as `hero_image` in `_data/locations.yml`, until each town
has a photograph of its own room — three different photographs of somewhere else
would be three different promises. It exists only at the four hero widths and
has no base variant, so `_data/imgw.yml` has no entry and the layout writes its
own srcset.

**The site-map page is built from `_data/nav.yml`, so anything not in the menu
has to be added to it by hand.** The home page was the first such case — the
wordmark is its link — and the three location pages are the second: they are
reached from the home page's venue cards, from `/acceso/` and from each other.
`_layouts/sitemap.html` renders them from `_data/locations.yml`, resolved per
language through `i18n-ref`, under the footer's own venue-column heading. Note
that this is the **site-map page**, `/mapa-del-sitio/`, and not `sitemap.xml`,
which is generated from every page carrying an `i18n-ref` and had them from the
first build.

### The access page's venue links are deep links, and they need a script

`/acceso/` is a picker: four radios and a `:has()` rule that shows the one panel
whose radio is checked. Every other panel is `display: none`, **and a fragment
cannot scroll to a box that is not drawn**. The footer's "Dónde entrenamos"
column points straight at those four ids, so three of its four links landed on
the page with the first venue showing and no scroll — nothing appeared to
happen. `initVenueLinks()` in `scripts/press.js` (already loaded there, for the
map facades and the entrance dialog) checks the right radio and then scrolls.

Three cases, and the third is the one that is easy to miss:

- **arriving from another page.** The browser tries its own scroll, finds a
  hidden element and gives up. The script is `defer`, so it runs with the DOM
  parsed and scrolls itself.
- **`hashchange`**, for the back button or a pasted address.
- **clicking one of those links while already on `/acceso/`.** Nothing
  navigates, so there is no load; and if the hash already names that panel there
  is no `hashchange` either. That is why the click is intercepted rather than
  left to the browser — it was the case where only the currently-open venue's
  link appeared to work, because only that one was already in view.

The offset is **not computed**: `.vn-panel` carries `scroll-margin-top:
@anchor-clear` like every other anchor on the site, and `scrollIntoView` honours
it. It is called with **`behavior: 'instant'`**, not the document's own
`scroll-behavior: smooth` — a fragment should arrive, the panel did not exist a
frame ago, and a smooth scroll is an animation that simply does not finish when
something interrupts it.

### Facility names are in `_data/venues.yml` and nowhere else

**`name` is the short form and is fixed; `facility` is the descriptive name and
is translated.** "CxEM Espronceda" reads the same in all four languages;
`facility` is "Complejo Deportivo Municipal Espronceda" / "Complex Esportiu
Municipal Espronceda" / "Espronceda Municipal Sports Complex" /
「エスプロンセダ市立スポーツ複合施設」. What is fixed is *Espronceda*; "complex
esportiu municipal" is three common nouns describing it, and the same goes for
*poliesportiu* at Marina-Besòs (センター, not 複合施設) and for *university* at the
UB (universidad / universitat / university / 大学).

**Three places used to keep their own copy of those names, and all three
drifted.** `_includes/map.html` had a `case` over `map_section` with the four
facilities in four languages — sixteen strings — and it still said "Mapa de
Complejo Deportivo Municipal Espronceda" a few hundred pixels below the
corrected name on the same page. `_data/links.yml` had a `name` plus a
`name_ja` per venue, which printed the *Catalan* name to all four languages and
disagreed with `venues.yml` in kana besides: マリナ・バゾス in one, マリナ・ベソス in
the other; エスプロンセダ…複合施設 in one, …施設 on the location pages. Neither
spelling is wrong on its own. Having both is.

Both read `facility[L]` now — `map.html` across `map_section`, `links.yml`
across a `venue:` id — so /acceso/, the map buttons, /ura/'s links, the home
page and the three location pages print one string per language.

**Japanese proper nouns are a live source of this.** Sant Adrià de Besòs was
サント・アドリアー・ダ・バゾス in two files and サント・アドリア・ダ・バゾス in
fifteen. When a place name is added, grep the kana across `_data/`, `_includes/`
and the four `*.md` sets before assuming it is new. The same applies to Arashi
Group, which is **嵐グループ** everywhere — the Latin name in Japanese copy is a
bug, except inside `_data/gallery.yml`, where the captions are the Instagram
posts verbatim and are a record rather than our own writing.

### Every video has a page of its own; /prensa-y-tv/ is the showcase

Search Console reported four videos as "Video isn't on a watch page", and that
was structural rather than a mistake. All six live on `/prensa-y-tv/`, and
**Google treats at most one video as a given URL's main content** — five of the
six could never be indexed as video however the markup was written.

So `_layouts/videopage.html` renders one video per page at
`/prensa-y-tv/<slug>/` (and the three translations), and the `VideoObject`
moved there. The index page is unchanged in what it shows: it is still the
showcase, its cards still carry the click-to-load facade, and each title is now
a link. What changed on it is its structured data — six `VideoObject`s became
an `ItemList` of links, because six of them was the page claiming to be six
watch pages at once.

**The stub carries `video:` and a language, nothing else.** The titles,
descriptions, date, YouTube id and thumbnail stay in `_videos/`, and the layout
reads them. Adding a video is one file in `_videos/` plus four stubs — the same
shape as the three location pages. `tools/` has no generator for them; they
were written once by a throwaway script and are ordinary files now.

Two things that bit while building them, both worth knowing:

- **Titles carry colons** — "Televisió de Badalona: la inauguración del dojo" —
  and an unquoted colon-space in YAML front matter starts a mapping. Quote them.
- **The source descriptions carry markup**, `<i>Via 15</i>`, and a `description`
  goes into `content="…"` of a meta tag. Truncating one mid-tag put a stray
  `</i>` inside an attribute on nine pages, which is what `qa.py`'s tag-balance
  check is for. Strip HTML from anything destined for an attribute.

### llms.txt is generated, and it is the only Agentic Browsing item that applies

PageSpeed's Agentic Browsing category lists four checks as "not applicable".
Three are **WebMCP**, which describes tools a page exposes for an agent to
operate — and this site has no forms to operate: contact is a `mailto:` and a
WhatsApp link. Annotating tools that do not exist would be an invention, so
they stay not applicable on purpose.

The fourth, `llms.txt`, does apply and now exists. It is a **Liquid template**
like `sitemap.xml`, not a written file: the rooms come from `_data/venues.yml`,
the fee from `_data/fees.yml`, the pages from `_data/nav.yml` and their own
descriptions. Rename a page and it follows on the next build. English only —
a model asking "where can I train aikido in Barcelona" needs one legible
answer, not the same answer four times.

## Where this site is going: Aikikai Barcelona

A new association, **Aikikai Barcelona**, has been registered and the site
transitions to it once it is operational. **Aikido Musubi becomes the name of
the Badalona dojo** — the main venue and the headquarters — and stops being the
name of the organisation. The association runs four locations across the
province of Barcelona and expects more.

Until then everything ships under the Aikido Musubi name. **Barcelona is the
primary location word from now on**; Badalona, Sant Adrià de Besòs and any town
with a linked dojo stay present and secondary. `areaServed` on the SportsClub
block already names all three, read from `_data/venues.yml`, so adding a fifth
venue adds a fifth town without touching a template.

**Do not introduce anything that hardcodes "Aikido Musubi" as the organisation.**
It is already once in `_config.yml` as `title`, once in `_data/footer.yml` as
`org`, and in the `SportsClub` block in `header.html`; those are the three that
will need editing at the rename, and the number should not grow. The site
description and the home-page title live in `_data/translations.yml` as
`tagline`, `about` and `home_title` — they used to be written out five times
between them in `header.html` and had already drifted apart, one saying
"en Badalona" while another said "en Badalona, Barcelona".

**Per-location pages go in subdirectories, never on subdomains.** A subdomain
starts its authority at zero and has to earn it again; `/barcelona/` inherits
what the domain already has. And a location page has to carry its own
timetable, teacher, address and transport — a page that only rearranges the
same words for a different town name is a doorway page, which Google penalises.

## Render-blocking CSS is deliberate, and inlining it was measured and rejected

Lighthouse reports the two stylesheets as render-blocking and offers ~580 ms
back for inlining them. **It was tried, measured, and it was worse:**

    external   home 95   ura 94   glosario 95
    inlined    home 94   ura 79   glosario 91

The cost moves rather than disappearing. Parsing 11 KB of CSS inside the
document happens on the main thread while it is also parsing the document, and
Ura's total blocking time went from 0 ms to 653 ms. TBT is 30% of the
performance score and the round trip is worth less than that. The full note is
in `_includes/header.html`. **Do not "fix" this audit.**

What is worth doing, and is done: `fetchpriority="high"` on the hero preloads,
because the hero is a CSS background on `.fixedHead` and nothing in the markup
tells the browser it is the LCP element; and `sizes` values measured in a
browser rather than read off the grid.

**The largest single number PageSpeed reports is not ours to fix.** "Use
efficient cache lifetimes — 313 KiB" is a `Cache-TTL` of **10 minutes** on
every asset, which is GitHub Pages' own `max-age=600` reaching the browser
untouched. Cloudflare's Browser Cache TTL only overrides it when it is not set
to "Respect Existing Headers". That is a dashboard setting, not a commit.

## What Search Console found, and what robots.txt was doing

**`robots.txt` was blocking `/scripts/` and `/styles/`.** Googlebot fetched the
HTML, could not fetch the CSS or the JS, and indexed an unstyled document with
none of the content the page scripts build. Search Console reported 53 pages
"Crawled - currently not indexed" while that was true. It also blocked
`/graphics/` and `/icons/`, which twelve pages and all ninety-six pages
respectively need in order to render, and `/plugins/`, which has never existed.
Nothing is disallowed now. Do not add a `Disallow` back without writing down
what it is protecting.

**Structured data is checked in Search Console, not by `qa.py`.** `qa.py`
validates that the JSON parses; it cannot know that schema.org wants a field.
The Events report had 44 items with `Missing field "location"` — a critical
error, because an Event with no place is not eligible for a rich result, so the
whole block was decoration for as long as it shipped. Also missing: `endDate` on
35, `performer` and `offers` on all 44.

Three things came out of fixing it:

- **The address lives once, in `postal:` in `_data/venues.yml`**, and
  `_includes/place-jsonld.html` renders it. It had been written three times —
  a `PostalAddress` hardcoded in `header.html`, a flat string on `/acceso/`, and
  nothing at all on the events.
- **A false location is worse than a missing one.** Everything the dojo hosts
  defaults to the dojo; `venue:` names another id and `place_*` a plain string.
  The four `collaboration` entries happen in trade-fair halls this repo does not
  know the address of, so they keep the warning rather than claiming the dojo.
  Same for `offers`: it is emitted only where `price:` is written down, and the
  masterclasses carry `price: 0` because their own copy says "entrada libre" in
  four languages.
- **The UTC offset is computed with `%:z`, never typed.** It was `+02:00`
  everywhere, which is correct in summer and an hour wrong from late October to
  late March; a January masterclass was published as starting at 11:00 UTC.
  `timezone: Europe/Madrid` in `_config.yml` is what `%:z` resolves against.

**Public holidays are not Events.** The calendar was publishing every
`holiday: true` closure as a schema.org Event with `EventCancelled`, the dojo as
organiser and a location — thirty-eight of them across two years, saying the
association had cancelled Christmas. They are skipped.

**A redirect to a `noindex` page is a URL that exists only to be crawled.** The
four `404.md` files carried thirty-six `redirect_from:` entries added in July
2020 — every asset directory, once per language: `/images/`, `/ca/scripts/`,
`/ja/fonts/` and so on, half of them paths that have never existed in any
language. `jekyll-redirect-from` writes a **real, crawlable HTML page** at each,
so those thirty-six answered `200` with a meta-refresh to a page whose own
`<meta robots>` says `noindex`. Googlebot fetched thirty-six URLs, followed
thirty-six redirects, and was told at the end of each one not to index what it
found. They are gone, and those paths return an honest 404 now — which is what
GitHub Pages does for any path with no file behind it, and what `404.html` at
the root is for.

`qa.py`'s **generated redirects** check is the guard: it reads every emitted
redirect page and fails if the destination is missing or `noindex`. Twelve
remain and all twelve earn their keep — `/cursos/`, `/fotos/`, `/videos/` and
their translations are renamed pages with inbound links.

**The renamed pages redirect; the renamed PDFs do not.** `jekyll-redirect-from`
covers `/cursos/`, `/fotos/`, `/videos/` and their translations, which is where
the traffic is. The `_courses/` to `_events/` rename also renamed sixty PDFs,
and `/files/courses-hFZ2XXIp-*.pdf` now 404s — twenty-one of them with
impressions. Jekyll cannot redirect a static file, and GitHub Pages has no
server config, so that one belongs in Cloudflare as a redirect rule.

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

## Nothing is in progress, and nothing is excluded from the audit

There were two unfinished features here. Both are resolved, and the note is
kept because of how the second one nearly outlived its own cleanup.

**Feature A**, the photos category filter, went when `_photos/` did:
`_data/gallery.yml` and the gallery's own chips replaced it.

**Feature B**, the Resources section, was a `_resources/` collection rendered
by `_layouts/resource.html`, with its own `_config.yml` block and a set of
`graphics/file-*.svg` icons. It was replaced during the rebuild by the
data-driven `/recursos/` page: `_data/resources.yml` plus
`_layouts/resources.html` (plural). Collection, layout, config block and icons
are all gone.

**What nearly outlived it was the exemption, not the feature.** `tools/qa.py`
carried `WIP = ('resources', 'recursos')` and every check skipped any path
containing either word. The WIP pages it was written for had ceased to exist,
but the live Resources pages match the same strings, so all four of them were
still being skipped by every check in the file — and one had been shipping
`<meta name="description" content="...">`, the literal placeholder, invisibly.

The lesson is about the shape of the exemption rather than about remembering to
remove it: **a blanket path match exempts whatever later takes the same name.**
If something genuinely has to be exempt, exempt it by an explicit list of URLs
that has to be edited to grow, so that adding a page cannot silently inherit
the exemption.

Always check `git status` before committing. Never `git add -A`.

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
logo-{NN}.svg            numbered logo variants
logo-{NN}-{variant}.svg  logo with named variant (alt, children)
logo-ajuntament-{town}   a town's own arms, for a venue in its building
```

The `file-{type}.svg` icon set is gone with the `_resources/` collection that
used it. `/recursos/` says what a thing is with a coloured word rather than a
glyph — see `.rs-k-*` in `styles/resources.less`.

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
