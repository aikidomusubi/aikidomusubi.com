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
"""

import argparse
import http.server
import io
import json
import os
import re
import socketserver
import threading
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
        "tags": [t.strip() for t in (tags.group(1) if tags else "").split(",") if t.strip()],
        "show": "show: true" in block,
        "seen": "seen: true" in block,
    }


def tag_ids(text):
    i, j = text.index("\ntags:"), text.index("\nui:")
    return re.findall(r"^  - id: (\w+)", text[i:j], re.M)


def load():
    text = io.open(DATA, encoding="utf-8").read()
    _, _, blocks = split_entries(text)
    items = []
    for n, b in enumerate(blocks):
        d = parse(b)
        d["i"] = n
        d["has_thumb"] = bool(d["ref"]) and os.path.exists(os.path.join(CACHE, d["ref"] + ".jpg"))
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
        tags = dec.get("tags") or []
        if tags:
            b = re.sub(r"\n    tags: \[[^\]]*\]", "\n    tags: [%s]" % ", ".join(tags), b, count=1)
        if b != blocks[n]:
            changed += 1
        blocks[n] = b

    io.open(DATA, "w", encoding="utf-8").write(head + lead + "".join(blocks))
    return changed


# ---------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------
PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gallery review</title>
<style>
 :root{--ink:#111314;--mute:#4f5d63;--line:rgba(17,19,20,.13);--keep:#1a7444;--paper:#faf9f7}
 *{box-sizing:border-box}
 body{margin:0;background:var(--paper);color:var(--ink);
      font:14px/1.5 "Noto Sans",system-ui,sans-serif}
 header{position:sticky;top:0;z-index:5;background:var(--ink);color:#fff;
        padding:.7rem 1.1rem;display:flex;gap:1.1rem;align-items:center;flex-wrap:wrap}
 header b{font-size:1rem;letter-spacing:.02em}
 header .sp{flex:1}
 button{font:inherit;cursor:pointer;border-radius:.25rem;border:1px solid transparent;padding:.42rem .85rem}
 .save{background:#FFF200;color:#111314;font-weight:700}
 .save[disabled]{opacity:.35;cursor:default}
 .ghost{background:transparent;color:#fff;border-color:rgba(255,255,255,.45)}
 .count{color:#c9cdcf;font-variant-numeric:tabular-nums}
 main{padding:1.1rem;display:grid;gap:1rem;
      grid-template-columns:repeat(auto-fill,minmax(210px,1fr))}
 .card{border:1px solid var(--line);border-radius:.4rem;background:#fff;overflow:hidden;
       display:flex;flex-direction:column}
 .card.keep{border-color:var(--keep);box-shadow:0 0 0 2px var(--keep) inset}
 .shot{display:block;width:100%;aspect-ratio:1;object-fit:cover;background:#e9e9e7;
       border:0;padding:0;cursor:pointer}
 .none{display:flex;align-items:center;justify-content:center;color:var(--mute);
       font-size:.72rem;text-align:center;padding:.5rem}
 .meta{padding:.6rem .7rem;display:flex;flex-direction:column;gap:.3rem;flex:1}
 .nm{font-size:.8rem;line-height:1.35;max-height:3.5em;overflow:hidden}
 .sub{font-size:.68rem;color:var(--mute);letter-spacing:.04em;text-transform:uppercase;
      display:flex;gap:.4rem;align-items:center;justify-content:space-between}
 .sub a{color:var(--mute)}
 select{font:inherit;font-size:.75rem;width:100%;padding:.25rem;border:1px solid var(--line);
        border-radius:.2rem;background:#fff;margin-top:auto}
 .done{padding:3rem 1.1rem;color:var(--mute)}
 kbd{background:#fff;border:1px solid var(--line);border-bottom-width:2px;border-radius:.2rem;
     padding:0 .3rem;font:inherit;font-size:.8em}
</style></head><body>
<header>
  <b>Gallery review</b>
  <span class="count" id="c"></span>
  <span class="sp"></span>
  <button class="ghost" id="all">Keep all shown</button>
  <button class="ghost" id="none">Drop all shown</button>
  <button class="save" id="save" disabled>Save</button>
</header>
<main id="g"></main>
<script>
const TAGS = __TAGS__, ITEMS = __ITEMS__;
const state = new Map();          // i -> {keep, tags}
const g = document.getElementById('g');

function draw(){
  g.innerHTML = '';
  if(!ITEMS.length){
    g.innerHTML = '<p class="done">Nothing left to review. '
                + 'Run <kbd>fetch-social.py --metadata-only</kbd> to pull new posts.</p>';
    return;
  }
  for(const it of ITEMS){
    const s = state.get(it.i) || {keep:false, tags:it.tags.slice()};
    const card = document.createElement('div');
    card.className = 'card' + (s.keep ? ' keep' : '');
    const shot = it.has_thumb
      ? `<img class="shot" loading="lazy" src="/t/${it.ref}.jpg" alt="">`
      : `<div class="shot none">no image<br>offered by Meta</div>`;
    card.innerHTML = shot
      + `<div class="meta">
           <div class="sub"><span>${it.type} · ${it.date}</span>
             <a href="${it.url}" target="_blank" rel="noopener">open</a></div>
           <div class="nm">${it.name ? it.name.replace(/</g,'&lt;') : '<i>no caption</i>'}</div>
           <select>${TAGS.map(t =>
              `<option value="${t}"${s.tags[0]===t?' selected':''}>${t}</option>`).join('')}</select>
         </div>`;
    card.querySelector('.shot').addEventListener('click', () => {
      const cur = state.get(it.i) || {keep:false, tags:it.tags.slice()};
      cur.keep = !cur.keep; state.set(it.i, cur); draw(); tally();
    });
    card.querySelector('select').addEventListener('change', e => {
      const cur = state.get(it.i) || {keep:false, tags:it.tags.slice()};
      cur.tags = [e.target.value]; state.set(it.i, cur); tally();
    });
    g.appendChild(card);
  }
}
function tally(){
  const k = [...state.values()].filter(v => v.keep).length;
  document.getElementById('c').textContent =
    `${ITEMS.length} shown · ${k} kept · ${state.size} decided`;
  document.getElementById('save').disabled = state.size === 0;
}
document.getElementById('all').onclick = () => {
  ITEMS.forEach(it => state.set(it.i, {keep:true, tags:(state.get(it.i)||{}).tags || it.tags.slice()}));
  draw(); tally();
};
document.getElementById('none').onclick = () => {
  ITEMS.forEach(it => state.set(it.i, {keep:false, tags:(state.get(it.i)||{}).tags || it.tags.slice()}));
  draw(); tally();
};
document.getElementById('save').onclick = async () => {
  const body = {};
  for(const [i, v] of state) body[i] = v;
  const r = await fetch('/save', {method:'POST', body: JSON.stringify(body)});
  const t = await r.text();
  if(r.ok){ document.body.innerHTML =
      '<p class="done">' + t + '<br><br>Close this tab and stop the server with Ctrl-C.</p>'; }
  else { alert(t); }
};
draw(); tally();
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

    def do_GET(self):
        if self.path.startswith("/t/"):
            # Only ever a cached review thumbnail, addressed by its media id.
            name = os.path.basename(self.path[3:])
            if not re.fullmatch(r"[0-9A-Za-z_-]+\.jpg", name):
                return self._send(400, b"no", "text/plain")
            f = os.path.join(CACHE, name)
            if not os.path.exists(f):
                return self._send(404, b"no", "text/plain")
            return self._send(200, io.open(f, "rb").read(), "image/jpeg")
        page = (PAGE.replace("__TAGS__", json.dumps(self.tags))
                    .replace("__ITEMS__", json.dumps(self.items)))
        self._send(200, page)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            decisions = json.loads(self.rfile.read(n) or b"{}")
            changed = apply(decisions)
        except Exception as exc:
            return self._send(500, str(exc), "text/plain; charset=utf-8")
        kept = sum(1 for v in decisions.values() if v.get("keep"))
        msg = "Saved %d decisions, %d kept." % (changed, kept)
        print("\n  " + msg)
        self._send(200, msg, "text/plain; charset=utf-8")
        threading.Thread(target=self.server.shutdown, daemon=True).start()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=60, help="how many to show at once")
    ap.add_argument("--type", choices=["reel", "post", "album"])
    ap.add_argument("--from", dest="since", help="only items on or after YYYY-MM-DD")
    ap.add_argument("--all", action="store_true", help="include already-reviewed items")
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
    pool = [i for i in items if (a.all or not i["seen"])]
    if a.type:
        pool = [i for i in pool if i["type"] == a.type]
    if a.since:
        pool = [i for i in pool if i["date"] >= a.since]
    pool.sort(key=lambda i: i["date"], reverse=True)
    total = len(pool)
    pool = pool[:a.size]

    missing = sum(1 for i in pool if not i["has_thumb"])
    print("%d to review, showing %d." % (total, len(pool)))
    if missing:
        print("%d of them have no thumbnail yet. To fetch:" % missing)
        print("    source .env.local && .venv/bin/python tools/fetch-social.py --review-thumbs")
    if not pool:
        print("Nothing to do.")
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
            print("\nStopped. Nothing saved unless you pressed Save.")


if __name__ == "__main__":
    main()
