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

## Editing them

The HTML in this directory is **generated**. The sources are in `src/`:

- `_dat.py` — real figures pulled from `_data/` and `_events/`
- `_aside.py` — Ura's content and both layouts
- `_home2.py` — the home page
- `_gloss.py` — the 123 glossary terms
- `build3.py`, `build_gloss.py`, `build_about.py`, `build_extra.py` — the builders

Edit the source, run `render.sh`, review, then implement in the site proper.
