#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Look at the gallery backlog and decide, with the pictures in front of you.

    .venv/bin/python tools/review.py

Opens http://localhost:8765 in your browser. Click a card to keep it, click
again to drop it, pick a category from its menu, press Save. Decisions go
straight into _data/gallery.yml.

WHY THIS REPLACED THE TERMINAL VERSION. tools/triage.py printed a numbered list
of captions and asked for "3,4,7-9". That is fine for a reel called "How was
Michelle Feilen Sensei's class last Saturday" and useless for the eleven posts
whose entire caption is the word "Post". You cannot decide whether a photograph
belongs in a gallery without seeing the photograph, and 297 of them were
waiting on exactly that. triage.py is deleted; it is in the history if the
terminal version is ever wanted back.

NO NETWORK AND NO TOKEN. It reads _data/gallery.yml and .cache/review/, both
already on disk. Fetching is a separate job:

    .venv/bin/python tools/fetch-social.py --review-thumbs

NO DEPENDENCIES. http.server and json from the standard library, one HTML
string. It never needs to be installed, upgraded or trusted with anything, and
it binds to 127.0.0.1 so nothing outside this machine can reach it.

THE FILE IS EDITED AS TEXT, not loaded and re-dumped. _data/gallery.yml is
mostly comments explaining itself and a YAML dumper would throw every one of
them away. Each decision is a targeted replacement inside one entry's block.

WHAT A DECISION MEANS
    keep     show: true,  seen: true   — it will appear on /galeria/
    drop     show: false, seen: true   — reviewed and passed over
    neither  show: false               — not yet looked at; comes back next time

Nothing is ever deleted. A decision is one word in a text file.

EVERY ENTRY IS LOADED AND THE FILTERS ARE IN THE PAGE. There is nothing to
choose on the command line and no restart to change your mind:

    Status     all / on the site / not on the site / never reviewed / reviewed
    Category   all / no category / seminar / training / demo / travel / exams
    Type       all / post / reel / album
    Show       128 / 256 / 512 / 1024 / everything

A card opens showing WHAT THE FILE SAYS — its categories lit, its border green
if it is live, an "on the site" label — so a re-review is a correction rather
than a blank slate, and "Keep page" cannot silently unpublish the lot.

SAVING DOES NOT END THE SESSION, which is the other reason this was confusing.
The first version shut the server down on the first save, so there was no way
to tell from the page whether anything had been written. Now the header says
"all saved" or "N unsaved" at all times, changed cards carry an orange border,
Save writes and then re-reads the file so the page shows what is on disk, and
closing the tab with pending edits warns first.

CATEGORIES ARE MULTI-SELECT, and that is not decoration: 22 entries are
`travel, seminar` and both are true of them. The first version of this used a
<select>, which would have quietly thrown the second one away on every entry it
touched.

DATES CAN BE THE DAY THE MEDIA WAS RECORDED rather than the day it was posted.
A clip of a 2015 seminar put up last month is honestly dated on Instagram and
wrong here, because the gallery sorts on `date_iso` and groups by its year.
Tick the cards, type 2015 / 2015-06 / 2015-06-20, Apply. A bare year means the
year and nothing narrower is known, so it becomes 2015-01-01; anything that is
not one of those three shapes is refused rather than guessed.

The posting date survives in `posted:`, which is appended after `show:` and
`seen:` ON PURPOSE — fetch-social.py's fetch_thumbs matches entry blocks with a
positional regex ending at `show: true`, and a field inserted higher up would
stop it finding anything.
"""

import argparse
import http.server
import io
import json
import os
import re
import socketserver
import urllib.parse
import webbrowser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "_data", "gallery.yml")
CACHE = os.path.join(ROOT, ".cache", "review")
PORT = 8765


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------
def split_entries(text):
    """(head, [entry blocks]) — entries start at the `entries:` key."""
    i = text.index("\nentries:")
    head, body = text[:i + len("\nentries:")], text[i + len("\nentries:"):]
    parts = re.split(r"(?=^  - type: )", body, flags=re.M)
    return head, parts[0], parts[1:]


def parse(block):
    def g(k, default=""):
        m = re.search(r'%s: "([^"]*)"' % k, block)
        return m.group(1) if m else default
    tags = re.search(r"tags: \[([^\]]*)\]", block)
    return {
        "type": (re.search(r"type: (\w+)", block) or [None, ""])[1],
        "date": g("date_iso"),
        "name": g("name"),
        "url": g("url"),
        "ref": g("ref"),
        "thumb": g("thumb"),
        "posted": g("posted"),
        "tags": [t.strip() for t in (tags.group(1) if tags else "").split(",") if t.strip()],
        "show": "show: true" in block,
        "seen": "seen: true" in block,
    }


def tag_ids(text):
    i, j = text.index("\ntags:"), text.index("\nui:")
    return re.findall(r"^  - id: (\w+)", text[i:j], re.M)


IMAGES = os.path.join(ROOT, "images")


def thumb_for(d):
    """Where this entry's picture is, if it has one anywhere.

    An entry that was approved carries a `thumb:` stem and a real published
    image in images/. One that has not been decided on has, at most, a 400px
    copy in .cache/review/ keyed by media id. Re-reviewing walks over both
    kinds at once, so it asks for whichever exists — published first, because
    it is the better picture and it is already on disk.
    """
    if d["thumb"]:
        f = os.path.join(IMAGES, d["thumb"] + ".jpg")
        if os.path.exists(f):
            return "/p/" + d["thumb"] + ".jpg"
    if d["ref"]:
        f = os.path.join(CACHE, d["ref"] + ".jpg")
        if os.path.exists(f):
            return "/t/" + d["ref"] + ".jpg"
    return ""


def load():
    text = io.open(DATA, encoding="utf-8").read()
    _, _, blocks = split_entries(text)
    items = []
    for n, b in enumerate(blocks):
        d = parse(b)
        d["i"] = n
        d["src"] = thumb_for(d)
        d["has_thumb"] = bool(d["src"])
        items.append(d)
    return text, items, tag_ids(text)


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------
def apply(decisions):
    """decisions: {index: {"keep": bool, "tags": [...]}} → rewrite gallery.yml.

    Indexes address the entry list as it was read. The file is re-read here and
    the blocks are re-split, so a hand edit made while the reviewer was open
    would shift them — hence the count check, which refuses rather than writing
    a decision onto the wrong post.
    """
    text = io.open(DATA, encoding="utf-8").read()
    head, lead, blocks = split_entries(text)
    if decisions and max(int(k) for k in decisions) >= len(blocks):
        raise IndexError("gallery.yml changed while the reviewer was open")

    changed = 0
    for k, dec in decisions.items():
        n = int(k)
        b = blocks[n]
        keep = bool(dec.get("keep"))

        b = re.sub(r"\n    show: (?:true|false)", "\n    show: %s" % str(keep).lower(), b, count=1)
        if "seen: true" not in b:
            # `seen` goes last, after show, and the block ends with a newline.
            b = b.rstrip("\n") + "\n    seen: true\n"
        # Written even when empty: deselecting every category is a decision
        # ("this one is not any of them"), and silently keeping the old value
        # would make the chips lie about what is stored.
        tags = dec.get("tags")
        if tags is not None:
            b = re.sub(r"\n    tags: \[[^\]]*\]", "\n    tags: [%s]" % ", ".join(tags), b, count=1)

        # THE DATE, when the media was recorded rather than when it was posted.
        #
        # A reel of a 2015 seminar put up last month is honestly dated on
        # Instagram and wrong here: _layouts/gallery.html sorts on `date_iso`
        # and groups the page by `date_iso | slice: 0, 4`, and Ura's archive
        # does the same, so the clip lands under the wrong year in both.
        #
        # The posting date is not deleted. The first time an entry is redated
        # its original goes into `posted:`, which is appended AFTER `show:` and
        # `seen:` on purpose: fetch-social.py's fetch_thumbs matches entry
        # blocks with a positional regex that ends at `show: true`, and a field
        # inserted higher up would stop it finding anything.
        #
        # The `thumb:` stem keeps the date it was minted with. It is an
        # identifier, not a claim — the file exists under that name, imgw.yml
        # indexes it and the sitemap names it, and renaming images to chase a
        # metadata edit is the one thing CLAUDE.md is most insistent about.
        date = dec.get("date")
        if date:
            was = re.search(r'date_iso: "([^"]+)"', b)
            if was and was.group(1) != date:
                if "\n    posted:" not in b:
                    b = b.rstrip("\n") + '\n    posted: "%s"\n' % was.group(1)
                b = re.sub(r'date_iso: "[^"]+"', 'date_iso: "%s"' % date, b, count=1)
            # Put a date back to the day it was posted and the record of the
            # posting date has nothing left to record. Leaving it behind would
            # litter the file with `posted:` lines equal to their own
            # `date_iso:`, and make "has this been redated?" unanswerable.
            orig = re.search(r'posted: "([^"]+)"', b)
            if orig and orig.group(1) == date:
                b = re.sub(r'\n    posted: "[^"]+"', "", b, count=1)

        if b != blocks[n]:
            changed += 1
        blocks[n] = b

    io.open(DATA, "w", encoding="utf-8").write(head + lead + "".join(blocks))
    return changed


# ---------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------
PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gallery review</title>
<style>
 :root{--ink:#111314;--mute:#4f5d63;--line:rgba(17,19,20,.13);--keep:#1a7444;
       --paper:#faf9f7;--warn:#ae5224;--yellow:#FFF200}
 *{box-sizing:border-box}
 body{margin:0;background:var(--paper);color:var(--ink);
      font:14px/1.5 "Noto Sans",system-ui,sans-serif}
 header{position:sticky;top:0;z-index:6;background:var(--ink);color:#fff}
 .bar{display:flex;gap:.8rem;align-items:center;flex-wrap:wrap;padding:.6rem 1rem}
 .bar.two{border-top:1px solid rgba(255,255,255,.14);font-size:.8rem}
 header b{font-size:1rem;letter-spacing:.02em}
 .sp{flex:1}
 .fig{color:#c9cdcf;font-variant-numeric:tabular-nums}
 .fig em{color:#fff;font-style:normal;font-weight:700}
 label.f{display:flex;gap:.35rem;align-items:center;color:#c9cdcf;font-size:.76rem}
 select{font:inherit;font-size:.78rem;padding:.25rem .4rem;border-radius:.2rem;
        border:1px solid rgba(255,255,255,.3);background:#1e2325;color:#fff}
 button{font:inherit;cursor:pointer;border-radius:.25rem;border:1px solid transparent;
        padding:.38rem .8rem}
 .save{background:var(--yellow);color:#111314;font-weight:700}
 .save[disabled]{opacity:.3;cursor:default}
 .ghost{background:transparent;color:#fff;border-color:rgba(255,255,255,.4);font-size:.78rem;
        padding:.3rem .6rem}
 .ghost[disabled]{opacity:.3;cursor:default}
 .toast{position:fixed;left:50%;transform:translateX(-50%);bottom:1.4rem;z-index:20;
        background:var(--keep);color:#fff;padding:.7rem 1.2rem;border-radius:.3rem;
        box-shadow:0 6px 24px rgba(0,0,0,.25);font-weight:700}
 main{padding:1rem;display:grid;gap:.9rem;
      grid-template-columns:repeat(auto-fill,minmax(200px,1fr))}
 .card{border:1px solid var(--line);border-radius:.4rem;background:#fff;overflow:hidden;
       display:flex;flex-direction:column}
 .card.keep{border-color:var(--keep);box-shadow:0 0 0 2px var(--keep) inset}
 .card.dirty{border-color:var(--warn);box-shadow:0 0 0 2px var(--warn) inset}
 .shot{display:block;width:100%;aspect-ratio:1;object-fit:cover;background:#e9e9e7;
       border:0;padding:0;cursor:pointer}
 .none{display:flex;flex-direction:column;gap:.35rem;align-items:center;
       justify-content:center;color:var(--mute);font-size:.72rem;text-align:center;
       padding:.5rem;cursor:pointer}
 .none small{font-size:.6rem;line-height:1.4;opacity:.75;font-family:ui-monospace,monospace}
 .meta{padding:.55rem .65rem;display:flex;flex-direction:column;gap:.28rem;flex:1}
 .nm{font-size:.78rem;line-height:1.35;max-height:3.4em;overflow:hidden}
 .sub{font-size:.66rem;color:var(--mute);letter-spacing:.04em;text-transform:uppercase;
      display:flex;gap:.4rem;justify-content:space-between}
 .sub a{color:var(--mute)}
 .st{font-size:.62rem;letter-spacing:.07em;text-transform:uppercase;font-weight:700}
 .pick{position:absolute;top:.4rem;left:.4rem;z-index:2;width:1.1rem;height:1.1rem;
       accent-color:var(--warn);cursor:pointer}
 .wrap{position:relative}
 .card.sel{outline:3px solid var(--warn);outline-offset:-3px}
 .redated{color:var(--warn);font-weight:700}
 input[type=text].dt{font:inherit;font-size:.78rem;width:7.5rem;padding:.25rem .4rem;
      border-radius:.2rem;border:1px solid rgba(255,255,255,.3);background:#1e2325;color:#fff}
 input[type=text].dt::placeholder{color:#8b9296}
 .st.on{color:var(--keep)} .st.off{color:var(--mute)}
 .tags{display:flex;flex-wrap:wrap;gap:.22rem;margin-top:auto;padding-top:.4rem}
 .tag{font:inherit;font-size:.64rem;letter-spacing:.04em;text-transform:uppercase;
      padding:.18rem .4rem;border:1px solid var(--line);border-radius:.2rem;
      background:#fff;color:var(--mute)}
 .tag[aria-pressed="true"]{background:var(--ink);border-color:var(--ink);color:#fff}
 .pager{display:flex;gap:.6rem;align-items:center;justify-content:center;
        padding:1.4rem 1rem 3rem;color:var(--mute);font-size:.8rem}
 .pager button{border-color:var(--line);background:#fff;color:var(--ink)}
 .pager button[disabled]{opacity:.35;cursor:default}
 .empty{padding:3rem 1rem;color:var(--mute)}
</style></head><body>
<header>
  <div class="bar">
    <b>Gallery review</b>
    <span class="fig" id="totals"></span>
    <span class="sp"></span>
    <span class="fig" id="dirty"></span>
    <button class="ghost" id="revert" disabled>Undo unsaved</button>
    <button class="save" id="save" disabled>Save</button>
  </div>
  <div class="bar two">
    <label class="f">Status
      <select id="fStatus">
        <option value="all">all</option>
        <option value="pub">on the site</option>
        <option value="notpub">not on the site</option>
        <option value="unseen">never reviewed</option>
        <option value="seen">reviewed</option>
        <option value="nopic">no picture</option>
      </select></label>
    <label class="f">Category <select id="fTag"></select></label>
    <label class="f">Type
      <select id="fType">
        <option value="all">all</option><option>post</option>
        <option>reel</option><option>album</option>
      </select></label>
    <label class="f">Show
      <select id="fSize">
        <option>128</option><option selected>256</option>
        <option>512</option><option>1024</option><option value="0">everything</option>
      </select></label>
    <span class="sp"></span>
    <span class="fig" id="range"></span>
    <button class="ghost" id="keepPage">Keep page</button>
    <button class="ghost" id="dropPage">Drop page</button>
  </div>
  <div class="bar two">
    <label class="f"><input type="checkbox" id="selAll"> select page</label>
    <span class="fig" id="selCount">0 selected</span>
    <span class="sp"></span>
    <label class="f">Set date
      <input type="text" class="dt" id="dtVal" placeholder="2015 or 2015-06-20"></label>
    <button class="ghost" id="dtApply" disabled>Apply to selected</button>
    <button class="ghost" id="dtUndo" disabled>Restore posted date</button>
    <button class="ghost" id="selNone" disabled>Clear selection</button>
  </div>
</header>
<main id="g"></main>
<div class="pager" id="pager"></div>
<script>
const TAGS = __TAGS__;
let ITEMS = __ITEMS__;
const state = new Map();              // i -> {keep, tags}   only while unsaved
let page = 0;

const $ = id => document.getElementById(id);
const g = $('g');

$('fTag').innerHTML = '<option value="all">all</option>'
  + '<option value="none">no category</option>'
  + TAGS.map(t => `<option value="${t}">${t}</option>`).join('');

// What an entry looks like right now: the unsaved edit if there is one,
// otherwise what the file says. Nothing is ever seeded into `state` just by
// being drawn, so `state.size` is exactly the number of unsaved edits.
const now = it => state.get(it.i) || {keep: it.show, tags: it.tags, date: it.date};
const dirty = it => {
  const s = state.get(it.i);
  return !!s && (s.keep !== it.show || s.tags.join() !== it.tags.join() || s.date !== it.date);
};
function edit(it){
  if(!state.has(it.i))
    state.set(it.i, {keep: it.show, tags: it.tags.slice(), date: it.date});
  return state.get(it.i);
}

// Selection is separate from keep/drop on purpose: picking entries out in
// order to redate them has nothing to do with whether they are published.
const picked = new Set();

// "2015" means the year and nothing narrower is known, so it becomes
// 2015-01-01 and the gallery groups it under 2015. "2015-06" is the month.
// Anything else must be a full ISO date or it is refused rather than guessed.
function normDate(v){
  v = (v || '').trim();
  if(/^\d{4}$/.test(v)) return v + '-01-01';
  if(/^\d{4}-\d{2}$/.test(v)) return v + '-01';
  if(/^\d{4}-\d{2}-\d{2}$/.test(v)) return v;
  return null;
}

function filtered(){
  const st = $('fStatus').value, tg = $('fTag').value, ty = $('fType').value;
  return ITEMS.filter(it => {
    const s = now(it);
    if(st === 'pub'    && !s.keep) return false;
    if(st === 'notpub' &&  s.keep) return false;
    if(st === 'unseen' &&  it.seen) return false;
    if(st === 'seen'   && !it.seen) return false;
    if(st === 'nopic'  &&  it.src) return false;
    if(tg === 'none'   && s.tags.length) return false;
    if(tg !== 'all' && tg !== 'none' && !s.tags.includes(tg)) return false;
    if(ty !== 'all' && it.type !== ty) return false;
    return true;
  });
}
const pageSize = () => { const v = +$('fSize').value; return v === 0 ? 1e9 : v; };

function draw(){
  const list = filtered(), size = pageSize();
  const pages = Math.max(1, Math.ceil(list.length / size));
  if(page >= pages) page = pages - 1;
  const slice = list.slice(page * size, page * size + size);

  g.innerHTML = '';
  if(!slice.length){
    g.innerHTML = '<p class="empty">Nothing matches those filters.</p>';
  }
  for(const it of slice){
    const s = now(it);
    const card = document.createElement('div');
    card.className = 'card' + (s.keep ? ' keep' : '') + (dirty(it) ? ' dirty' : '')
                   + (picked.has(it.i) ? ' sel' : '');
    const shot = it.src
      ? `<img class="shot" loading="lazy" src="${it.src}" alt="">`
      : `<div class="shot none">no picture yet<br><small>fetch-social.py<br>--review-thumbs --all</small></div>`;
    const moved = s.date !== (it.posted || it.date);
    card.innerHTML = `<div class="wrap"><input type="checkbox" class="pick"${
        picked.has(it.i) ? ' checked' : ''} title="select for redating">` + shot + `</div>`
      + `<div class="meta">
        <div class="sub"><span>${it.type} · <span class="${moved ? 'redated' : ''}">${s.date}</span></span>
          <a href="${it.url}" target="_blank" rel="noopener">open</a></div>
        <div class="nm">${it.name ? it.name.replace(/</g,'&lt;') : '<i>no caption</i>'}</div>
        <div class="st ${s.keep?'on':'off'}">${s.keep ? 'on the site' : 'not shown'}${
          dirty(it) ? ' · unsaved' : ''}${!it.seen ? ' · new' : ''}${
          moved ? ' · posted ' + (it.posted || it.date) : ''}</div>
        <div class="tags">${TAGS.map(t =>
           `<button class="tag" type="button" data-t="${t}" aria-pressed="${s.tags.includes(t)}">${t}</button>`
         ).join('')}</div></div>`;
    card.querySelector('.shot').addEventListener('click', () => {
      const c = edit(it); c.keep = !c.keep; sync();
    });
    card.querySelector('.pick').addEventListener('change', e => {
      if(e.target.checked) picked.add(it.i); else picked.delete(it.i);
      sync();
    });
    card.querySelectorAll('.tag').forEach(btn => btn.addEventListener('click', () => {
      const c = edit(it), t = btn.dataset.t, n = c.tags.indexOf(t);
      if(n === -1) c.tags.push(t); else c.tags.splice(n, 1);
      sync();
    }));
    g.appendChild(card);
  }

  $('range').textContent = list.length
    ? `${page*size+1}\u2013${Math.min((page+1)*size, list.length)} of ${list.length}`
    : '0 of 0';
  $('pager').innerHTML = pages > 1
    ? `<button id="prev" ${page===0?'disabled':''}>\u2190 previous</button>
       <span>page ${page+1} of ${pages}</span>
       <button id="next" ${page>=pages-1?'disabled':''}>next \u2192</button>` : '';
  if(pages > 1){
    $('prev').onclick = () => { page--; draw(); scrollTo(0,0); };
    $('next').onclick = () => { page++; draw(); scrollTo(0,0); };
  }
}

function sync(){
  // A card edited back to what the file already says is not an edit. Every
  // field that can be edited has to be compared here or the pruning throws the
  // edit away: the date was missing from this test, so a date-only change was
  // written into `state` and deleted again by the next sync(), which made the
  // Apply button look like it had done nothing at all.
  for(const [i, s] of [...state]){
    const it = ITEMS.find(x => x.i === +i);
    if(it && s.keep === it.show && s.tags.join() === it.tags.join()
          && s.date === it.date) state.delete(+i);
  }
  const pub = ITEMS.filter(it => now(it).keep).length;
  const unseen = ITEMS.filter(it => !it.seen).length;
  $('totals').innerHTML =
    `<em>${ITEMS.length}</em> entries \u00b7 <em>${pub}</em> on the site \u00b7 `
    + `<em>${unseen}</em> never reviewed`;
  $('dirty').innerHTML = state.size
    ? `<em>${state.size}</em> unsaved` : 'all saved';
  $('save').disabled = state.size === 0;
  $('revert').disabled = state.size === 0;
  $('selCount').innerHTML = picked.size ? `<em>${picked.size}</em> selected` : '0 selected';
  $('selNone').disabled = !picked.size;
  $('dtUndo').disabled = !picked.size;
  $('dtApply').disabled = !picked.size || !normDate($('dtVal').value);
  draw();
}

['fStatus','fTag','fType','fSize'].forEach(id =>
  $(id).addEventListener('change', () => { page = 0; sync(); }));

$('keepPage').onclick = () => {
  const size = pageSize();
  filtered().slice(page*size, page*size+size).forEach(it => { edit(it).keep = true; });
  sync();
};
$('dropPage').onclick = () => {
  const size = pageSize();
  filtered().slice(page*size, page*size+size).forEach(it => { edit(it).keep = false; });
  sync();
};
$('revert').onclick = () => { state.clear(); sync(); };

// ---- selection and redating ------------------------------------------------
$('selAll').onchange = e => {
  const size = pageSize();
  filtered().slice(page*size, page*size+size)
    .forEach(it => e.target.checked ? picked.add(it.i) : picked.delete(it.i));
  sync();
};
$('selNone').onclick = () => { picked.clear(); sync(); };

$('dtVal').addEventListener('input', () => {
  $('dtApply').disabled = !picked.size || !normDate($('dtVal').value);
});

$('dtApply').onclick = () => {
  const d = normDate($('dtVal').value);
  if(!d){ toast('Type a year, a year-month, or a full date: 2015 / 2015-06 / 2015-06-20', true); return; }
  let n = 0;
  for(const i of picked){
    const it = ITEMS.find(x => x.i === i);
    if(!it) continue;
    edit(it).date = d;
    n++;
  }
  sync();
  toast(`${n} entr${n===1?'y':'ies'} dated ${d} — not saved yet`);
};

// The posting date is kept in `posted:` the first time an entry is redated, so
// putting one back is possible rather than a matter of remembering.
$('dtUndo').onclick = () => {
  let n = 0;
  for(const i of picked){
    const it = ITEMS.find(x => x.i === i);
    if(!it || !it.posted) continue;
    edit(it).date = it.posted;
    n++;
  }
  sync();
  toast(n ? `${n} restored to the date they were posted` : 'None of those were redated', !n);
};

function toast(msg, bad){
  const t = document.createElement('div');
  t.className = 'toast'; t.textContent = msg;
  if(bad) t.style.background = '#ae5224';
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3200);
}

$('save').onclick = async () => {
  const body = {};
  for(const [i, v] of state) body[i] = {keep: v.keep, tags: v.tags, date: v.date};
  $('save').disabled = true;
  try{
    const r = await fetch('/save', {method:'POST', body: JSON.stringify(body)});
    const msg = await r.text();
    if(!r.ok){ toast(msg, true); $('save').disabled = false; return; }
    // Re-read from disk so the page shows what is actually in the file.
    const fresh = await (await fetch('/state')).json();
    ITEMS = fresh.items;
    state.clear();
    sync();
    toast(msg);
  }catch(e){ toast(String(e), true); $('save').disabled = false; }
};

addEventListener('beforeunload', e => {
  if(state.size){ e.preventDefault(); e.returnValue = ''; }
});

sync();
</script></body></html>
"""


class Handler(http.server.BaseHTTPRequestHandler):
    items = []
    tags = []

    def log_message(self, *a):
        pass                                  # the terminal is for the summary

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        raw = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _serve_image(self, base, raw):
        """One .jpg out of one directory, and provably not out of any other.

        THE GUARD IS NOT A CHARACTER WHITELIST ANY MORE, and that was a real
        bug rather than a theoretical one: image stems are slugified from
        captions and captions are not ASCII. `gallery-2026-04-27-saturday-
        evening-土曜夜.jpg` exists on disk and the site serves it, and this
        route answered 400 to it because 土 is not in [0-9A-Za-z._-]. Every
        Japanese-titled post in the gallery was invisible in the reviewer.

        So the test is where the file actually resolves to, which is what the
        question really was. realpath collapses `..`, symlinks and any spelling
        of the separator, and commonpath then says whether the result is still
        inside the directory we meant. Nothing outside it is reachable however
        the path is written, and every filename that legitimately exists works.
        """
        name = os.path.basename(urllib.parse.unquote(raw))
        if not name.endswith(".jpg"):
            return self._send(400, b"no", "text/plain")
        f = os.path.realpath(os.path.join(base, name))
        if os.path.commonpath([f, os.path.realpath(base)]) != os.path.realpath(base):
            return self._send(400, b"no", "text/plain")
        if not os.path.isfile(f):
            return self._send(404, b"no", "text/plain")
        return self._send(200, io.open(f, "rb").read(), "image/jpeg")

    def do_GET(self):
        if self.path.startswith("/p/"):
            return self._serve_image(IMAGES, self.path[3:])
        if self.path.startswith("/t/"):
            return self._serve_image(CACHE, self.path[3:])
        if self.path == "/state":
            _, items, tags = load()
            return self._send(200, json.dumps({"items": items, "tags": tags}),
                              "application/json; charset=utf-8")
        page = (PAGE.replace("__TAGS__", json.dumps(self.tags))
                    .replace("__ITEMS__", json.dumps(self.items)))
        self._send(200, page)

    def do_POST(self):
        """Save, and KEEP THE SERVER UP.

        It used to shut down on the first save, which is why it was not obvious
        whether anything had been written: the page was replaced by a sentence
        and the session was over. Now the file is written, the page re-reads
        /state so it shows what is actually on disk, and the header goes back to
        "all saved". Reviewing 769 entries is many sittings, not one.
        """
        n = int(self.headers.get("Content-Length", 0))
        try:
            decisions = json.loads(self.rfile.read(n) or b"{}")
            changed = apply(decisions)
        except Exception as exc:
            return self._send(500, "NOT saved: %s" % exc, "text/plain; charset=utf-8")
        msg = "Saved. %d entr%s written to _data/gallery.yml." % (
            changed, "y" if changed == 1 else "ies")
        print("  " + msg)
        self._send(200, msg, "text/plain; charset=utf-8")


def main():
    ap = argparse.ArgumentParser()
    # Status, category, type and page size are controls IN the page. The only
    # thing left here is a hard cutoff, for the rare case of not wanting the
    # first fifteen years loaded at all.
    ap.add_argument("--from", dest="since", help="only items on or after YYYY-MM-DD")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--no-open", action="store_true")
    ap.add_argument("--stats", action="store_true", help="where you are; writes nothing")
    a = ap.parse_args()

    _, items, tags = load()

    if a.stats:
        seen = sum(1 for i in items if i["seen"])
        kept = sum(1 for i in items if i["show"])
        cached = sum(1 for i in items if not i["seen"] and i["has_thumb"])
        print("entries    %d" % len(items))
        print("reviewed   %d  (%d%%)" % (seen, 100 * seen // len(items) if items else 0))
        print("keeping    %d" % kept)
        print("remaining  %d" % (len(items) - seen))
        print("           %d of those have a review thumbnail" % cached)
        return
    # EVERY ENTRY GOES TO THE PAGE. The command line used to do the filtering,
    # which meant choosing the question before you could see the answers and
    # restarting the server to change your mind. Status, category, type and how
    # many to show are controls in the page now; 769 entries of metadata is
    # about 200 KB of JSON and the pictures load lazily.
    pool = sorted(items, key=lambda i: i["date"], reverse=True)
    if a.since:
        pool = [i for i in pool if i["date"] >= a.since]

    missing = sum(1 for i in pool if not i["has_thumb"])
    print("%d entries \u00b7 %d on the site \u00b7 %d never reviewed"
          % (len(pool), sum(1 for i in pool if i["show"]),
             sum(1 for i in pool if not i["seen"])))
    if missing:
        print("\n%d have no picture on disk. To fetch them:" % missing)
        print("    source .env.local && "
              ".venv/bin/python tools/fetch-social.py --review-thumbs --all")
    if not pool:
        print("Nothing collected yet.")
        return

    Handler.items, Handler.tags = pool, tags
    socketserver.TCPServer.allow_reuse_address = True
    # 127.0.0.1, never 0.0.0.0: this serves your unpublished decisions.
    with socketserver.TCPServer(("127.0.0.1", a.port), Handler) as srv:
        url = "http://localhost:%d" % a.port
        print("\n  %s   (Ctrl-C to stop)\n" % url)
        if not a.no_open:
            webbrowser.open(url)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
