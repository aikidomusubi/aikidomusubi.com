#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Accumulate the kyū grade sheets from the additions in _data/exams.yml.

The syllabus is cumulative: 4th kyū is everything in 5th plus more. `exams.yml`
stores only what each grade ADDS, so that property is structural rather than
something five hand-written lists have to agree about. They did not agree: the
1st kyū PDF had lost Udekime-nage and Maki-otoshi from yokomen, the whole jō
programme and Kata-dori nikyō, and nothing could have caught that except
reading all five side by side.

This writes `_data/exams-sheets.yml` — one complete sheet per grade, every
technique stamped with `from`, the grade it first appears at. The page renders
five sheets; the sixth, "the whole programme", is the 1st kyū sheet with the
colours turned on, because with a cumulative syllabus those are the same list.
That is also why it is not emitted twice: it would be ten kilobytes of
duplicate markup on a page that already carries the other five.

    python3 tools/exam-sheets.py            # write the sheets
    python3 tools/exam-sheets.py --check    # exit 1 if they are stale

`tools/qa.py` runs the check. Needs PyYAML, which is deliberately not a project
dependency — install it into a throwaway venv, as the font subsetter does.
"""
import os
import sys

try:
    import yaml
except ImportError:                                          # pragma: no cover
    sys.exit('needs PyYAML —\n'
             '  python3 -m venv /tmp/exam && /tmp/exam/bin/pip install pyyaml\n'
             '  /tmp/exam/bin/python tools/exam-sheets.py')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_data', 'exams.yml')
OUT = os.path.join(ROOT, '_data', 'exams-sheets.yml')
GRADE_N = {'kyu5': 5, 'kyu4': 4, 'kyu3': 3, 'kyu2': 2, 'kyu1': 1}


def wkey(w):
    """Identity of a technique: its name, plus a note when the note changes it.

    `Ikkyō` and `Ikkyō from the inside` are different things to ask for.
    """
    if isinstance(w, dict):
        return (w.get('n', ''), (w.get('note') or {}).get('en', ''))
    return (w, '')


def accumulate(data):
    """Walk 5th → 1st, carrying everything forward, and snapshot at each grade."""
    order = []            # section ids, in the order they first appear
    sections = {}         # sid -> {'bn':…, 'rows':[…], 'rowix':{key:row}, 'tail':[…]}
    seen_w = set()
    seen_tail = set()
    sheets = {}

    for grade in data['grades']:
        n = GRADE_N[grade['id']]

        for block in grade.get('adds') or []:
            sid = block['section']
            if sid not in sections:
                sections[sid] = {'bn': None, 'rows': [], 'rowix': {}, 'tail': []}
                order.append(sid)
            sec = sections[sid]

            if block.get('bn'):
                sec['bn'] = block['bn']

            for t in block.get('tail') or []:
                tk = (sid, t.get('n', ''), (t.get('note') or {}).get('en', ''))
                if tk not in seen_tail:
                    seen_tail.add(tk)
                    sec['tail'].append(t)

            # `upd` restates something already asked for: the suburi count
            # grows 4 → 6 → 8, and the jō numbering goes #1 → #1, #2. In a
            # grade sheet only the current value belongs; in the cumulative
            # view the progression is the point, so the value being replaced is
            # kept beside it, marked, and the page reveals it there.
            for row in block.get('upd') or []:
                rk = (row['a'], (row.get('an') or {}).get('en', ''))
                entry = sec['rowix'].get(rk)
                if entry is None:
                    sys.exit('upd for a row that does not exist yet: %s / %s'
                             % (sid, row['a']))
                for w in row.get('w') or []:
                    name = w['n'] if isinstance(w, dict) else w
                    hit = None
                    for cand in entry['w']:
                        if cand['n'] == name and not cand.get('was'):
                            hit = cand
                    if hit is None:
                        sys.exit('upd for a technique that does not exist yet: %s / %s'
                                 % (sid, name))
                    superseded = dict(hit)
                    superseded['was'] = True
                    hit['note'] = w.get('note') if isinstance(w, dict) else None
                    if hit['note'] is None:
                        hit.pop('note', None)
                    hit['from'] = n
                    entry['w'].insert(entry['w'].index(hit), superseded)

            for row in block.get('rows') or []:
                rk = (row['a'], (row.get('an') or {}).get('en', ''))
                if rk not in sec['rowix']:
                    entry = {'a': row['a'], 'w': []}
                    if row.get('an'):
                        entry['an'] = row['an']
                    sec['rowix'][rk] = entry
                    sec['rows'].append(entry)
                entry = sec['rowix'][rk]

                for w in row.get('w') or []:
                    k = (sid,) + rk + wkey(w)
                    if k in seen_w:
                        continue
                    seen_w.add(k)
                    item = {'n': w['n'] if isinstance(w, dict) else w, 'from': n}
                    if isinstance(w, dict) and w.get('note'):
                        item['note'] = w['note']
                    entry['w'].append(item)

        # Snapshot. Deep-copied through yaml so later grades cannot mutate it.
        snap = []
        for sid in order:
            sec = sections[sid]
            b = {'section': sid}
            if sec['bn']:
                b['bn'] = sec['bn']
            b['rows'] = [{kk: vv for kk, vv in r.items()} for r in sec['rows']]
            for r in b['rows']:
                # `was` entries are history. They belong to the cumulative view,
                # which is rendered from the last snapshot, and nowhere else.
                keep = r['w'] if grade['id'] == 'kyu1' else [w for w in r['w'] if not w.get('was')]
                r['w'] = [dict(w) for w in keep]
            if sec['tail']:
                b['tail'] = list(sec['tail'])
            if b['rows'] or b.get('tail') or b.get('bn'):
                snap.append(b)
        sheets[grade['id']] = snap

    return sheets


def dump(sheets):
    head = ('# Generated by tools/exam-sheets.py — do not edit.\n'
            '# One complete sheet per kyū grade, accumulated from the additions in\n'
            '# _data/exams.yml. `from` is the grade a technique first appears at.\n')
    return head + yaml.safe_dump({'sheets': sheets}, allow_unicode=True,
                                 sort_keys=False, default_flow_style=False, width=100)


def main():
    data = yaml.safe_load(open(SRC, encoding='utf-8'))
    sheets = accumulate(data)
    want = dump(sheets)
    have = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else None

    if '--check' in sys.argv:
        if want != have:
            sys.exit('_data/exams-sheets.yml is stale — run `python3 tools/exam-sheets.py`')
        print('  exams-sheets.yml is current')
        return

    open(OUT, 'w', encoding='utf-8').write(want)

    print('  sheets written%s' % ('' if want == have else '  (changed)'))
    for gid in ('kyu5', 'kyu4', 'kyu3', 'kyu2', 'kyu1'):
        blocks = sheets[gid]
        total = sum(len(r['w']) for b in blocks for r in b['rows'])
        atk = sum(len(b['rows']) for b in blocks if b['section'] in ('suwari', 'hanmi', 'tachi'))
        tai = sum(len(r['w']) for b in blocks if b['section'] in ('suwari', 'hanmi', 'tachi')
                  for r in b['rows'])
        print('    %-5s %3d entries  (%d taijutsu across %d attacks)' % (gid, total, tai, atk))

    # Cumulative by construction, but say so out loud: every grade must contain
    # every technique of the grade below it.
    ids = ['kyu5', 'kyu4', 'kyu3', 'kyu2', 'kyu1']
    def flat(bl):
        # By name only: a note that was restated (suburi 4 → 6 → 8) is not a
        # technique going missing.
        return {(b['section'], r['a'], w['n'])
                for b in bl for r in b['rows'] for w in r['w'] if not w.get('was')}
    for lo, hi in zip(ids, ids[1:]):
        missing = flat(sheets[lo]) - flat(sheets[hi])
        if missing:
            sys.exit('NOT cumulative: %s is missing %d of %s: %s'
                     % (hi, len(missing), lo, sorted(missing)[:4]))
    print('    cumulative: every grade contains the one below it')


if __name__ == '__main__':
    main()
