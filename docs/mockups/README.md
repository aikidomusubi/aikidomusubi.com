# Mockups

Every design that was reviewed and approved before it was built, kept here so
it survives.

**Why here.** They used to be generated straight into `_site/mockups/`, and
`npx gulp build` begins with `rm -rf _site`. The whole set was lost that way and
had to be recovered out of a conversation transcript. `docs/` is in `exclude:`
in `_config.yml`, so this directory is in git, is never deployed, and no build
can touch it.

## Looking at them

They reference `/styles/all.min.css`, so they need the site's own stylesheets to
render. One command renders them into `_site/mockups/` and they are then at
`http://localhost:4000/mockups/…`:

```
./docs/mockups/render.sh
```

Run it again after any `npx gulp build`, which wipes `_site`.

## What is here

| File | What it is |
|---|---|
| `ura.html` | **Ura**, the aside. The approved reference for `/ura/`. |
| `home.html` | The home page as approved. |
| `glosario-a.html` / `-b.html` | The glossary, two interfaces. **A was chosen.** |
| `about-dojo/aikido/asociacion/faq.html` | The expanded About pages. |
| `404.html` | The 404 with the ma-ai minigame. **Chosen.** |
| `404-a.html` / `404-b.html` / `404-b2.html` | The three earlier proposals. |
| `accesibilidad.html` | The accessibility statement. |
| `mapa-a.html` / `mapa-b.html` | Site map, two versions. **A was chosen.** |
| `variants.html` | Title, Ura wording, door layouts, panel openings. |
| `final.html` | Separator, section title, shidoin wording, chain subtitle. |
| `names.html` | The six candidate names for the aside. **Ura was chosen.** |
| `switch.html` | Three ways to open the aside. |
| `loc-barcelona-a/-b.html` | The location page, two approaches: a reference entry with the facts first, and a landing page that opens with the room. Barcelona is the template for `/badalona/` and `/sant-adria-de-besos/`. **Undecided.** |
| `bar-glosario-a/-b.html`, `bar-recursos-a/-b.html` | The sticky search-and-filter bar on a phone, two proposals, each shown on both pages. **A was chosen** and is built: one line, chips in a drawer. B kept the chips visible by scrolling them, which hides options behind an edge. |

## Editing them

The HTML in this directory is **generated**. The sources are in `src/`:

- `_dat.py` — real figures pulled from `_data/` and `_events/`
- `_aside.py` — Ura's content and both layouts
- `_home2.py` — the home page
- `_gloss.py` — the 123 glossary terms
- `build3.py`, `build_gloss.py`, `build_about.py`, `build_extra.py` — the builders
- `build_loc.py` — the location-page proposals. Every fact on both pages comes out
  of `_data/venues.yml`, `_data/schedule.yml` and `_data/fees.yml`; nothing is
  invented, because a location page that invents anything is the exact thing
  Google penalises.
- `_bar.py` / `build_bar.py` — the sticky-bar proposals. `build_bar.py` reads
  `_data/resources.yml` directly rather than keeping a second copy of it, so the
  chip counts and the label lengths in the mockup are the ones that really have
  to wrap. The measurements quoted in it were taken off the built pages at
  375x667, not estimated.

Edit the source, run `render.sh`, review, then implement in the site proper.
