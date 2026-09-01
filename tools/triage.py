#!/usr/bin/env python3
"""Work through the collected gallery entries a batch at a time.

`fetch-social.py --metadata-only` drops the whole back catalogue into
_data/gallery.yml as text: no images, nothing published. This walks that list in
batches, shows you what each item is, and writes your decision back.

    .venv/bin/python tools/triage.py                 # next 50, newest first
    .venv/bin/python tools/triage.py --size 25
    .venv/bin/python tools/triage.py --type reel     # only reels
    .venv/bin/python tools/triage.py --from 2024-01-01
    .venv/bin/python tools/triage.py --stats         # where you are

At the prompt: numbers, ranges, `all`, `none`, `q` to stop.

    > 1,4,7-9,22

Kept entries get `show: true`; the rest keep `show: false`. Either way they get
`seen: true`, so the next batch moves on rather than showing you the same
rejections again — and re-running the fetch will not resurrect them.

Nothing is deleted. A decision is one word in a text file and can be changed at
any time.
"""

import argparse
import io
import re
import sys

DATA = "_data/gallery.yml"
TAGS = ["seminar", "training", "demo", "travel", "exams"]


def load():
    text = io.open(DATA, encoding="utf-8").read()
    head, sep, body = text.partition("\nentries:")
    if not sep:
        sys.exit("No `entries:` block in %s" % DATA)
    blocks = re.split(r"(?m)^(?=  - type: )", body)
    lead, items = blocks[0], blocks[1:]
    return head + sep, lead, items


def field(block, name):
    # The first line of a block is `  - type: reel`, so the key can be preceded
    # by the list dash as well as by indentation.
    m = re.search(r'^\s*(?:-\s*)?%s:\s*"?([^"\n]*)"?\s*$' % name, block, re.M)
    return m.group(1).strip() if m else ""


def set_field(block, name, value):
    if re.search(r"^\s*%s:" % name, block, re.M):
        return re.sub(r"^(\s*%s:).*$" % name, r"\1 %s" % value, block, count=1, flags=re.M)
    return block.rstrip("\n") + "\n    %s: %s\n" % (name, value)


def parse_choice(raw, n):
    raw = raw.strip().lower()
    if raw in ("q", "quit", "exit"):
        return None
    if raw in ("", "none", "n"):
        return set()
    if raw in ("all", "a"):
        return set(range(1, n + 1))
    keep = set()
    for part in re.split(r"[,\s]+", raw):
        if not part:
            continue
        if "-" in part:
            a, _, b = part.partition("-")
            try:
                keep.update(range(int(a), int(b) + 1))
            except ValueError:
                print("  ? ignoring %r" % part)
        else:
            try:
                keep.add(int(part))
            except ValueError:
                print("  ? ignoring %r" % part)
    return {i for i in keep if 1 <= i <= n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=50)
    ap.add_argument("--type", choices=["reel", "post", "album"])
    ap.add_argument("--from", dest="since", help="only items on or after YYYY-MM-DD")
    ap.add_argument("--tags", default="training", help="tags applied to kept items")
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()

    prefix, lead, items = load()

    total = len(items)
    kept = sum(1 for b in items if field(b, "show") == "true")
    seen = sum(1 for b in items if field(b, "seen") == "true")

    if args.stats or not total:
        print("entries   %d" % total)
        print("reviewed  %d  (%d%%)" % (seen, 100 * seen // total if total else 0))
        print("keeping   %d" % kept)
        print("remaining %d" % (total - seen))
        if not total:
            print("\nNothing collected yet. Run:\n"
                  "  .venv/bin/python tools/fetch-social.py --metadata-only")
        return

    # Newest first — recent clips are the ones worth showing, and it means the
    # work that matters most is done before the enthusiasm runs out.
    order = sorted(range(total), key=lambda i: field(items[i], "date_iso"), reverse=True)
    pending = [i for i in order if field(items[i], "seen") != "true"]
    if args.type:
        pending = [i for i in pending if field(items[i], "type") == args.type]
    if args.since:
        pending = [i for i in pending if field(items[i], "date_iso") >= args.since]

    if not pending:
        print("Nothing left to review with those filters.")
        print("%d of %d reviewed, %d kept." % (seen, total, kept))
        return

    batch = pending[: args.size]
    print("\n%d to review%s — showing %d  (%d of %d done, %d kept so far)\n"
          % (len(pending),
             (" (%s)" % args.type) if args.type else "",
             len(batch), seen, total, kept))

    for n, idx in enumerate(batch, 1):
        b = items[idx]
        print("%3d  %-5s  %s  %s" % (n, field(b, "type"), field(b, "date_iso"),
                                     field(b, "name")[:64]))

    print("\nKeep which?  numbers / ranges / all / none / q")
    try:
        choice = parse_choice(input("> "), len(batch))
    except (EOFError, KeyboardInterrupt):
        print("\nnothing written.")
        return
    if choice is None:
        print("nothing written.")
        return

    tags = ", ".join(t.strip() for t in args.tags.split(",") if t.strip())
    for n, idx in enumerate(batch, 1):
        items[idx] = set_field(items[idx], "seen", "true")
        if n in choice:
            items[idx] = set_field(items[idx], "show", "true")
            items[idx] = set_field(items[idx], "tags", "[%s]" % tags)

    io.open(DATA, "w", encoding="utf-8").write(prefix + lead + "".join(items))

    left = len(pending) - len(batch)
    print("\nkept %d, passed on %d.  %d still to review." % (len(choice), len(batch) - len(choice), left))
    if choice:
        print("\nWhen you have finished, fetch their images:\n"
              "  .venv/bin/python tools/fetch-social.py --thumbs")
    if left:
        print("\nNext batch:  .venv/bin/python tools/triage.py")


if __name__ == "__main__":
    main()
