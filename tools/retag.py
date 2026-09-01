#!/usr/bin/env python3
"""Propose tags for gallery entries from what their captions say.

Everything triaged with the default lands on `training`, which leaves the
filter with a single value and so nothing to filter — the exact problem the old
photos page had, where all 27 albums were `events`.

The captions carry the answer: a shihan's name means a seminar, 審査 means a
grading, an embukai means a demonstration, a city that is not Badalona means
travel. This reads those signals and writes the tags.

    .venv/bin/python tools/retag.py --dry-run     # show what it would change
    .venv/bin/python tools/retag.py               # write it

Only entries that are `show: true` AND still carry the untouched default
`[training]` are considered, so anything you tagged by hand is left alone.
An entry can end up with two tags; a seminar in Milan is travel as well.
"""

import argparse
import collections
import io
import re

DATA = "_data/gallery.yml"

# Ordered: the first rule that matches contributes its tag, and several can.
RULES = [
    ("exams", [
        "審査", "exam", "examen", "exàmen", "graduation", "kyu-", "shinsa",
    ]),
    ("demo", [
        "embukai", "演武", "exhibi", "demostra", "japan weekend", "manga",
        "saló", "salon del manga", "salón del manga", "festa", "fira",
        "open class", "clase abierta", "classe oberta",
    ]),
    ("travel", [
        "corsico", "milan", "milán", "milano", "tokyo", "東京", "brussels",
        "bruselas", "andorra", "valencia", "madrid", "lyon", "paris", "parís",
        "hombu", "pedraforca", "terrassa", "castelldefels", "iwama", "japan ",
        "japón", "kyoto", "京都", "osaka",
    ]),
    ("seminar", [
        "shihan", "seminar", "seminario", "seminari", "curso", "curs ",
        "stage", "講習", "masterclass", "sensei",
    ]),
]


def field(block, name):
    m = re.search(r'^\s*(?:-\s*)?%s:\s*"?([^"\n]*)"?\s*$' % name, block, re.M)
    return m.group(1).strip() if m else ""


def suggest(name):
    low = name.lower()
    tags = [tag for tag, words in RULES if any(w in low for w in words)]
    # `sensei` alone is weak — half the dojo's posts name a teacher without the
    # post being a seminar. It only counts when nothing more specific matched.
    if tags == ["seminar"] and "sensei" in low and not any(
            w in low for w in ("shihan", "seminar", "講習", "stage", "masterclass")):
        tags = ["training"]
    return tags or ["training"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    text = io.open(DATA, encoding="utf-8").read()
    prefix, sep, body = text.partition("\nentries:")
    blocks = re.split(r"(?m)^(?=  - type: )", body)
    lead, items = blocks[0], blocks[1:]

    counts = collections.Counter()
    changed = 0
    for i, b in enumerate(items):
        if field(b, "show") != "true":
            continue
        if field(b, "tags") != "[training]":
            continue                      # hand-tagged: leave it
        tags = suggest(field(b, "name"))
        counts["+".join(tags)] += 1
        if tags != ["training"]:
            changed += 1
            if not args.dry_run:
                items[i] = re.sub(r"^(\s*tags:).*$", r"\1 [%s]" % ", ".join(tags),
                                  b, count=1, flags=re.M)

    for combo, n in counts.most_common():
        print("  %-24s %3d" % (combo, n))
    print("\n%s %d of %d entries" % ("Would change" if args.dry_run else "Changed",
                                     changed, sum(counts.values())))
    if not args.dry_run:
        io.open(DATA, "w", encoding="utf-8").write(prefix + sep + lead + "".join(items))


if __name__ == "__main__":
    main()
