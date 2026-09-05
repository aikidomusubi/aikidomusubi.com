#!/usr/bin/env python3
"""
QA — the standing checks that run before any change is called done.

    npx gulp qa          (or: python3 tools/qa.py)

WHY THIS IS A SCRIPT AND NOT A CHECKLIST IN A DOCUMENT

Everything in here was, at some point, found by hand and then forgotten about
until it broke again: source files leaking into _site, a heading level skipped
on sixteen pages, an anchor offset measured against an element that no longer
existed, a link duplicated on every seminar. A written checklist drifts exactly
the way the `exclude:` list in _config.yml drifted. A script does not.

WHAT IT DOES NOT COVER

Anything needing a rendering engine: colour contrast, computed-style diffs
before/after a refactor, layout geometry, focus behaviour. Those need a real
browser and are listed under "Browser checks" in CLAUDE.md. This file is the
part that can be automated cheaply, and it is the part that should never be
skipped.

EXIT CODE

Non-zero if any FAIL is reported, so it can gate a build. WARN and INFO never
fail the run — they are trends worth watching, not errors.

NOTHING IS EXCLUDED. There used to be a WIP carve-out here: the four Resources
pages of an unfinished feature knowingly failed two checks, so every check
skipped any path containing "resources" or "recursos". That feature was
replaced by the data-driven /recursos/ page during the rebuild, and the
carve-out outlived it — the live Resources pages, in four languages, were still
being skipped by every check in this file. A blanket path match is a bad way to
exempt anything: it exempts whatever later takes the same name.
"""

import os
import re
import sys
import glob
import datetime
import gzip
import html
import subprocess
import tempfile
from collections import Counter, defaultdict

SITE = '_site'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr'}

FAILS, WARNS, INFOS = [], [], []


def fail(check, detail=''):
    FAILS.append((check, detail))


def warn(check, detail=''):
    WARNS.append((check, detail))


def info(check, detail=''):
    INFOS.append((check, detail))


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def strip_noise(s):
    """Remove comments and raw-text elements before parsing structure."""
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    return re.sub(r'<(script|style|svg)\b.*?</\1>', '', s, flags=re.S | re.I)


def load_pages():
    out = []
    for p in sorted(glob.glob(SITE + '/**/index.html', recursive=True)):
        s = read(p)
        if 'http-equiv="refresh"' in s:      # jekyll-redirect-from stubs
            continue
        out.append((p, s))
    return out


# ---------------------------------------------------------------------------
# 1. Structure — the markup has to be well formed before anything else means
#    anything. A stray </div> silently reshapes a page and every other check
#    downstream then measures the wrong thing.
# ---------------------------------------------------------------------------
def check_structure(pages):
    bad = 0
    for p, raw in pages:
        s = strip_noise(raw)
        stack = []
        for m in re.finditer(r'<(/?)([a-zA-Z][\w-]*)([^>]*)>', s):
            closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
            if tag in VOID or attrs.rstrip().endswith('/'):
                continue
            if closing:
                if stack and stack[-1] == tag:
                    stack.pop()
                elif tag in stack:
                    bad += 1
                    fail('tag balance', f'{p}: <{tag}> closed early')
                    while stack and stack.pop() != tag:
                        pass
                else:
                    bad += 1
                    fail('tag balance', f'{p}: stray </{tag}>')
            else:
                stack.append(tag)
        if stack:
            bad += 1
            fail('tag balance', f'{p}: unclosed {",".join(stack[:3])}')
    print(f'  {"tag balance":<34} {len(pages)} pages, {bad} problems')


def check_ids(pages):
    n = 0
    for p, raw in pages:
        ids = re.findall(r'\sid="([^"]+)"', raw)
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            n += 1
            fail('duplicate ids', f'{p}: {", ".join(sorted(dupes)[:3])}')
    print(f'  {"duplicate ids":<34} {n} pages affected')


# ---------------------------------------------------------------------------
# 2. Headings — exactly one h1, no skipped levels. Both Lighthouse and every
#    screen reader's heading list depend on it, and it is the check that caught
#    sixteen About pages shipping with no h1 at all.
# ---------------------------------------------------------------------------
def check_headings(pages):
    n = 0
    for p, raw in pages:
        hs = [int(m.group(1)) for m in re.finditer(r'<h([1-6])\b', strip_noise(raw))]
        if not hs:
            n += 1; fail('heading order', f'{p}: no headings')
        elif hs[0] != 1:
            n += 1; fail('heading order', f'{p}: starts at h{hs[0]}')
        elif hs.count(1) > 1:
            n += 1; fail('heading order', f'{p}: {hs.count(1)} h1s')
        else:
            for a, b in zip(hs, hs[1:]):
                if b > a + 1:
                    n += 1; fail('heading order', f'{p}: h{a} -> h{b}')
                    break
    print(f'  {"heading order":<34} {n} pages affected')


# ---------------------------------------------------------------------------
# 3. Links — every internal href must resolve, and every #fragment must exist
#    on the page it points at.
# ---------------------------------------------------------------------------
def resolves(u):
    u = u.split('#')[0].split('?')[0]
    if not u.startswith('/'):
        return True
    if u == '/':
        return True
    q = os.path.join(SITE, u.strip('/'))
    return os.path.isfile(os.path.join(q, 'index.html')) or os.path.isfile(q)


def check_links(pages):
    total = broken = anchors = 0
    for p, raw in pages:
        for m in re.finditer(r'href="(/[^"]*)"', raw):
            u = html.unescape(m.group(1))
            total += 1
            if not resolves(u):
                broken += 1
                fail('broken link', f'{p} -> {u}')
            elif '#' in u:
                base, frag = u.split('#', 1)
                target = os.path.join(SITE, base.strip('/'), 'index.html')
                if os.path.isfile(target) and f'id="{frag}"' not in read(target):
                    anchors += 1
                    fail('broken anchor', f'{p} -> {u}')
    print(f'  {"internal links":<34} {total} checked, {broken} broken, {anchors} dead anchors')


def check_image_refs(pages):
    """Every src and srcset URL must resolve.

    `check_links` only reads `href`, so a missing image is invisible to it.
    Three templates used to spell their srcset out by hand and name a `-800`
    for every image alike; sources narrower than 900px never get one, so 374
    of the 666 referenced variants were 404s — silent in the page, loud in the
    console, and a Best Practices failure on Galeria and Seminarios. The
    srcsets are generated from `_data/imgw.yml` now, and this is what keeps
    them honest when someone adds an image and forgets to regenerate it.
    """
    seen, broken = set(), 0
    for p, raw in pages:
        urls = set(re.findall(r'<(?:img|source)[^>]*?\ssrc="(/[^"]+)"', raw))
        for m in re.finditer(r'srcset="([^"]+)"', raw):
            for cand in m.group(1).split(','):
                cand = cand.strip().split()
                if cand and cand[0].startswith('/'):
                    urls.add(cand[0])
        for u in urls:
            seen.add(u)
            if not os.path.isfile(os.path.join(SITE, html.unescape(u).lstrip('/'))):
                broken += 1
                fail('missing image', f'{p} -> {u}')
    print(f'  {"image references":<34} {len(seen)} unique, {broken} missing')


def check_exam_cumulative():
    """The cumulative kyū sheet must still be the union of the five grades.

    `_data/exams-sheets.yml` is generated from `_data/exams.yml`. Edit a
    grade and forget to regenerate, and the "whole syllabus" sheet quietly
    disagrees with the sheet next to it — the kind of drift that is invisible
    until somebody prints both. Regenerated here in memory and compared.
    """
    tool = os.path.join('tools', 'exam-sheets.py')
    out = os.path.join('_data', 'exams-sheets.yml')
    if not os.path.exists(tool) or not os.path.exists(out):
        return
    r = subprocess.run([sys.executable, tool, '--check'],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print(f'  {"exam syllabus":<34} cumulative sheet matches the five grades')
    elif 'PyYAML' in (r.stdout + r.stderr):
        # The tool needs a library that is deliberately not a project
        # dependency; say so rather than failing a build over it.
        warn('exam syllabus not verified', 'tools/exam-sheets.py needs PyYAML')
    else:
        fail('exam syllabus', (r.stdout + r.stderr).strip().split(chr(10))[-1])


# ---------------------------------------------------------------------------
# 4. Sitemap — generated, but every image it names must exist or the entry is
#    a broken reference on the page too.
# ---------------------------------------------------------------------------
def check_build_warnings():
    """Jekyll warns and carries on; that is how three pages went missing.

    A `: ` inside an unquoted front-matter value makes YAML read the line as a
    mapping. Jekyll prints "YAML Exception", skips the file, exits 0, and the
    page simply does not exist. Nothing downstream notices except a broken link
    somewhere else — if anything happens to link to it.

    This re-runs the build and reads the warnings, which is cheap next to
    finding out in production.
    """
    env = dict(os.environ, RUBYOPT='-E utf-8:utf-8')
    try:
        r = subprocess.run(['bundle', 'exec', 'jekyll', 'build', '--verbose'],
                           capture_output=True, text=True, env=env, timeout=180)
    except Exception as e:
        warn('build warnings', 'could not re-run jekyll: %s' % e)
        print('  %-34s skipped' % 'jekyll warnings')
        return
    out = (r.stdout or '') + (r.stderr or '')
    bad = [l.strip() for l in out.splitlines()
           if 'YAML Exception' in l or 'Build Warning' in l or 'Conversion error' in l]
    for b in bad[:6]:
        fail('jekyll warning', b[:160])
    print('  %-34s %d warnings' % ('jekyll warnings', len(bad)))


def check_orphan_layouts():
    """Every layout should be reachable. A page that failed to build leaves its
    layout with nothing pointing at it, which is the same symptom from the
    other side and costs nothing to check."""
    used = set()
    for f in glob.glob('_layouts/*.html'):
        used.add(os.path.splitext(os.path.basename(f))[0])
    seen = set()
    for f in (glob.glob('*.md') + glob.glob('*/*.md') + glob.glob('_*/*.md')):
        m = re.search(r'^layout:\s*(\S+)', read(f), re.M)
        if m:
            seen.add(m.group(1).strip('"\''))
    orphans = sorted(used - seen - {'default'})
    if orphans:
        warn('unused layout', ', '.join(orphans))
    print('  %-34s %d unused' % ('layouts', len(orphans)))


def check_less_selectors():
    """LESS silently deletes part of a selector, and it took hours to find.

    `a:hover b { ... }` compiles to `.scope b { ... }` — the compound before the
    descendant is dropped. The hover colour for every link in Ura's link block
    was therefore applied to *every* `b` in it, painting the whole list yellow,
    and nothing anywhere reported a problem. In lessc 4.4.2 it happens for two
    descendants, `b` and `s`; which two is a property of the compiler, not of
    this codebase, so the check asks the compiler rather than hard-coding them.

    A fixture names every HTML element after a pseudo-class. Any element whose
    prefix does not survive is then searched for in the real stylesheets.
    """
    probe = os.path.join(tempfile.gettempdir(), 'qa-less-probe.less')
    els = ('a abbr b bdi bdo br button cite code data del dfn em i img input kbd '
           'label mark output picture q rp rt ruby s samp select small span '
           'strong sub sup svg template textarea time u var wbr video div p h1 '
           'h2 h3 h4 h5 h6 ul ol li dl dt dd table thead tbody tr th td figure '
           'figcaption blockquote pre hr nav main header footer section article '
           'aside form fieldset legend').split()
    with open(probe, 'w') as fh:
        fh.write('.probe {\n')
        for e in els:
            fh.write('  a:hover %s { color: red; }\n' % e)
        fh.write('}\n')
    try:
        r = subprocess.run(['npx', 'lessc', probe], capture_output=True,
                           text=True, timeout=120)
    except Exception as e:
        warn('less selectors', 'could not run lessc: %s' % e)
        print('  %-34s skipped' % 'less selector loss')
        return
    lost = [e for e in els if re.search(r'(?m)^\.probe %s \{' % e, r.stdout)]

    hits = []
    if lost:
        pat = re.compile(r':[a-z-]+(?:\([^)]*\))?\s+(%s)(?=[\s,{])' % '|'.join(lost))
        for f in sorted(glob.glob('styles/*.less')):
            for n, line in enumerate(read(f).splitlines(), 1):
                if pat.search(line):
                    hits.append('%s:%d  %s' % (f, n, line.strip()[:70]))
    for h in hits:
        fail('less drops the compound — use a child combinator (`> %s`)' % lost[0], h)
    print('  %-34s %d swallowed by lessc (%s), %d in sources'
          % ('less selector loss', len(lost), ' '.join(lost) or '-', len(hits)))


def check_sitemap():
    f = os.path.join(SITE, 'sitemap.xml')
    if not os.path.isfile(f):
        fail('sitemap', 'not generated')
        return
    s = read(f)

    # A dev build. `jekyll serve` rewrites site.url to http://localhost:4000 and
    # it watches, so a running dev server silently overwrites whatever
    # `npx gulp build` just produced — and then every check below is auditing
    # the wrong site. This is a fail and not a warning because the sitemap that
    # ships would carry localhost URLs.
    if 'localhost' in s:
        fail('sitemap', 'built by `jekyll serve` — site.url is localhost. '
                        'Stop the dev server, then `rm -rf _site && npx gulp build`.')
        print('  %-34s DEV BUILD — stop `jekyll serve` and rebuild' % 'sitemap')
        return

    urls = re.findall(r'<loc>(.*?)</loc>', s)
    imgs = re.findall(r'<image:loc>(.*?)</image:loc>', s)
    missing = [u for u in set(imgs)
               if not os.path.isfile(SITE + u.replace('https://aikidomusubi.com', ''))]
    for u in missing[:5]:
        fail('sitemap image missing', u)

    # A lastmod cannot be in the future — a page has not changed on a day that
    # has not arrived, and Google discounts a lastmod it decides is unreliable.
    # This is here because the Seminars pages produced one without anybody
    # typing it: the sitemap advances a collection-backed index to its newest
    # item, and a seminar's date is when it WILL happen. Booking a masterclass
    # five months out dated the page 2027-01-30.
    today = datetime.date.today().isoformat()
    ahead = sorted(set(d for d in re.findall(r'<lastmod>(.*?)</lastmod>', s) if d > today))
    for d in ahead[:5]:
        fail('sitemap lastmod in the future', d)
    print(f'  {"sitemap":<34} {len(urls)} urls, {len(imgs)} images, '
          f'{len(missing)} missing, {len(ahead)} dated ahead')


# ---------------------------------------------------------------------------
# 5. Accessibility — the machine-checkable half. Contrast and focus behaviour
#    are browser checks and live in CLAUDE.md, not here.
# ---------------------------------------------------------------------------
def check_a11y(pages):
    found = Counter()
    for p, raw in pages:
        body = raw[raw.find('<body'):]

        for m in re.finditer(r'<img[^>]*>', body):
            if 'alt=' not in m.group(0):
                found['img without alt'] += 1
                fail('a11y: img without alt', f'{p}: {m.group(0)[:60]}')

        for m in re.finditer(r'<a\b([^>]*)>(.*?)</a>', body, re.S):
            attrs, inner = m.group(1), m.group(2)
            if re.sub(r'<[^>]+>', '', inner).strip():
                continue
            if any(a in attrs for a in ('aria-label', 'aria-labelledby', 'title=')):
                continue
            if '<img' in inner and 'alt=""' not in inner:
                continue
            found['link with no name'] += 1
            fail('a11y: link with no accessible name', f'{p}: {m.group(0)[:60]}')

        for m in re.finditer(r'<button\b([^>]*)>(.*?)</button>', body, re.S):
            attrs, inner = m.group(1), m.group(2)
            if re.sub(r'<[^>]+>', '', inner).strip():
                continue
            if any(a in attrs for a in ('aria-label', 'aria-labelledby')):
                continue
            found['button with no name'] += 1
            fail('a11y: button with no accessible name', f'{p}: {m.group(0)[:60]}')

        ids = set(re.findall(r'\sid="([^"]+)"', raw))
        for m in re.finditer(r'aria-(?:labelledby|describedby|controls)="([^"]+)"', raw):
            for ref in m.group(1).split():
                if ref not in ids:
                    found['dangling aria reference'] += 1
                    fail('a11y: aria-* points at a missing id', f'{p}: {ref}')

        if raw.count('<main') != 1:
            found['main landmark'] += 1
            fail('a11y: not exactly one <main>', p)
        if not re.search(r'<html[^>]+lang="', raw):
            found['html lang'] += 1
            fail('a11y: <html> without lang', p)
        if 'skip-link' not in body or 'id="main"' not in body:
            found['skip link'] += 1
            fail('a11y: no skip link (WCAG 2.4.1)', p)
        for m in re.finditer(r'tabindex="([1-9]\d*)"', body):
            found['positive tabindex'] += 1
            fail('a11y: positive tabindex', f'{p}: {m.group(0)}')

    total = sum(found.values())
    detail = ', '.join(f'{k}: {v}' for k, v in found.most_common(3)) or 'clean'
    print(f'  {"accessibility (markup)":<34} {total} problems  ({detail})')


# ---------------------------------------------------------------------------
# 6. SEO and semantics — the per-page tags that have to be present and unique.
# ---------------------------------------------------------------------------
def page_lang(raw):
    m = re.search(r'<html[^>]+lang="([a-z-]+)"', raw)
    return m.group(1) if m else '?'


def check_seo(pages):
    """Duplicates are only counted WITHIN a language.

    "Aikido Musubi - Classes" is the title of both the Catalan and the English
    Classes page, because the word is spelled the same in both. That is not a
    duplicate-content problem: the pages carry distinct canonicals and are tied
    together by hreflang, which is exactly how a search engine is told they are
    language variants of one another. Flagging it would be a warning that is
    always wrong, and a warning that is always wrong teaches you to skip the
    warnings that are not.
    """
    titles, descs = defaultdict(Counter), defaultdict(Counter)
    missing = 0
    for p, raw in pages:
        lang = page_lang(raw)
        t = re.search(r'<title>([^<]*)</title>', raw)
        d = re.search(r'<meta name="description" content="([^"]*)"', raw)
        if not t or len(t.group(1).strip()) < 5:
            missing += 1; fail('seo: missing or short <title>', p)
        else:
            titles[lang][t.group(1).strip()] += 1
        if not d or len(d.group(1).strip()) < 20:
            missing += 1; fail('seo: missing or short meta description', p)
        else:
            descs[lang][d.group(1).strip()] += 1
        if 'rel="canonical"' not in raw:
            missing += 1; fail('seo: missing canonical', p)
        if 'hreflang=' not in raw:
            missing += 1; fail('seo: missing hreflang alternates', p)

    dup_t = [(l, t) for l, c in titles.items() for t, n in c.items() if n > 1]
    dup_d = [(l, d) for l, c in descs.items() for d, n in c.items() if n > 1]
    for l, t in dup_t[:3]:
        warn(f'seo: duplicate <title> within one language', f'[{l}] {t[:60]}')
    for l, d in dup_d[:3]:
        warn(f'seo: duplicate meta description within one language', f'[{l}] {d[:60]}')
    print(f'  {"seo tags":<34} {missing} missing, '
          f'{len(dup_t)} duplicate titles, {len(dup_d)} duplicate descriptions '
          f'(compared within each language)')


# ---------------------------------------------------------------------------
# 7. Build hygiene — no Gulp input may reach _site. This is enforced by
#    `check-assets` in gulpfile.js too; repeated here so `python3 tools/qa.py`
#    is a complete picture on its own.
# ---------------------------------------------------------------------------
def check_build_output():
    leaked = []
    for d in (SITE + '/styles', SITE + '/scripts'):
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.endswith('.less') or (f.endswith('.js') and not f.endswith('.min.js')):
                leaked.append(f'{d}/{f}')
    for f in leaked:
        fail('source file deployed to _site', f)
    print(f'  {"build output":<34} {len(leaked)} source files leaked')


# ---------------------------------------------------------------------------
# 7b. Generated redirects that lead nowhere worth going.
#
#     `redirect_from:` makes jekyll-redirect-from write a REAL, crawlable HTML
#     page at each old path. That is right for a page that was renamed and has
#     inbound links — /cursos/ -> /seminarios/ is twelve of those and they earn
#     their keep.
#
#     The four 404 pages carried thirty-six more, added in July 2020: every
#     asset directory, once per language — /images/, /ca/scripts/, /ja/fonts/
#     and so on. Half of those paths have never existed in any language. Each
#     one answered 200 with a meta-refresh to a noindex page, so Googlebot
#     fetched thirty-six URLs, followed thirty-six redirects and was told at the
#     end of each not to index what it found. Deleting them lets those paths do
#     the honest thing and return a real 404.
#
#     The rule this checks is the general one: a redirect whose destination is
#     noindex is a URL that exists only to be crawled.
# ---------------------------------------------------------------------------
def check_redirects():
    targets, bad = {}, []
    for f in glob.glob(SITE + '/**/*.html', recursive=True):
        raw = open(f, encoding='utf-8', errors='ignore').read()
        if 'Redirecting&hellip;' not in raw:
            continue
        m = re.search(r'<link rel="canonical" href="([^"]+)"', raw)
        if m:
            targets[f] = m.group(1)

    for src, dest in targets.items():
        path = re.sub(r'^https?://[^/]+', '', dest)
        local = SITE + path
        if local.endswith('/'):
            local += 'index.html'
        if not os.path.exists(local):
            bad.append((src, dest, 'destino inexistente'))
            continue
        raw = open(local, encoding='utf-8', errors='ignore').read()
        if re.search(r'<meta name="robots" content="[^"]*noindex', raw):
            bad.append((src, dest, 'destino noindex'))

    for src, dest, why in bad:
        fail('redirect to a page that cannot be indexed',
             f'{src[len(SITE):]} -> {dest}  ({why})')
    print(f'  {"generated redirects":<34} {len(targets)} pages, {len(bad)} pointing at a noindex or missing target')


# ---------------------------------------------------------------------------
# 8. Dead code — CSS and JS that no built page can ever use. Purging hides most
#    of it, so it accumulates in the sources unnoticed.
# ---------------------------------------------------------------------------
def check_dead_code(pages):
    built = ' '.join(raw for _, raw in pages)
    dead = []
    for f in glob.glob('styles/*.less'):
        for cls in set(re.findall(r'\.([a-z][\w-]{3,})\s*[{,:]', read(f))):
            if cls.startswith(('nv-', 'ft-', 'tt-', 'cal-', 'gx-', 'fee-', 'vn-',
                               'vs-', 'ct-', 'cl-', 'ab-', 'pv-', 'skip-')):
                continue                     # built by script, or state classes
            if f'class="{cls}' in built or f' {cls}"' in built or f' {cls} ' in built:
                continue
            dead.append((os.path.basename(f), cls))
    shown = Counter(f for f, _ in dead)
    for f, n in shown.most_common(5):
        info('css classes with no matching markup', f'{f}: {n}')
    print(f'  {"dead css (informational)":<34} {len(dead)} classes with no markup')


# ---------------------------------------------------------------------------
# 9. Weight — what a visitor actually downloads. Render-blocking is what moves
#    the Lighthouse number, so it is reported separately.
# ---------------------------------------------------------------------------
def gz(path):
    p = os.path.join(SITE, path.split('?')[0].lstrip('/'))
    if not os.path.isfile(p):
        return 0
    with open(p, 'rb') as f:
        return len(gzip.compress(f.read(), 9))


def check_weight(pages):
    worst = []
    for p, raw in pages:
        css = re.findall(r'<link[^>]+rel="stylesheet"[^>]+href="(/[^"]+)"', raw) + \
              re.findall(r'<link[^>]+href="(/[^"]+)"[^>]+rel="stylesheet"', raw)
        js = [j for j in re.findall(r'<script[^>]+src="(/[^"]+)"', raw)]
        blocking = sum(gz(c) for c in css)
        total = len(gzip.compress(raw.encode(), 9)) + blocking + sum(gz(j) for j in js)
        worst.append((total, blocking, p))
    worst.sort(reverse=True)
    for t, b, p in worst[:3]:
        info('heaviest pages (gzip)',
             f'{p.replace(SITE + "/", "") or "home"}: {t // 1024} KB total, {b // 1024} KB render-blocking')
    if worst:
        avg = sum(t for t, _, _ in worst) // len(worst)
        maxb = max(b for _, b, _ in worst)
        print(f'  {"page weight (gzip)":<34} avg {avg // 1024} KB, worst render-block {maxb // 1024} KB')
        if maxb > 30 * 1024:
            warn('render-blocking CSS over 30 KB gzipped', f'{maxb // 1024} KB')


# ---------------------------------------------------------------------------
# 10. last_modified — the one part of the sitemap that is not automatic.
#
#     THIS ONE ASKS, IT DOES NOT ASSERT. It can see that a page's source changed;
#     it cannot see whether the RENDERED page changed. Most of the big diffs in
#     this repo are the opposite: content moved out of a .md and into a data file
#     and a layout, hundreds of lines removed, and the page a visitor sees is
#     byte-identical. Those must NOT be bumped — a lastmod Google decides is
#     unreliable is one it stops trusting altogether.
#
#     So: treat every line below as a question. Bump only where the rendered
#     content actually changed.
# ---------------------------------------------------------------------------
def check_lastmod():
    try:
        out = subprocess.run(['git', 'diff', '--numstat'],
                             capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return
    today = subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()
    stale = []
    for line in out.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) != 3:
            continue
        added, deleted, f = parts
        if not f.endswith('.md') or f.startswith('_') or f == 'CLAUDE.md':
            continue
        if not os.path.isfile(f):
            continue
        try:
            added = int(added)
        except ValueError:
            continue
        if added < 3:                       # front-matter-only edits do not count
            continue
        m = re.search(r'^last_modified:\s*([\d-]+)\s*$', read(f), re.M)
        if m and m.group(1) < today:
            stale.append(f'{f} ({m.group(1)})')
    for f in stale[:6]:
        warn('source edited — did the RENDERED page change? if so, bump last_modified', f)
    print(f'  {"last_modified freshness":<34} {len(stale)} pages with edits and a stale date')


# ---------------------------------------------------------------------------
def main():
    if not os.path.isdir(SITE):
        print('no _site — run `npx gulp build` first')
        return 1

    pages = load_pages()
    print(f'\nQA — {len(pages)} built pages\n')

    check_structure(pages)
    check_ids(pages)
    check_headings(pages)
    check_links(pages)
    check_image_refs(pages)
    check_exam_cumulative()
    check_build_warnings()
    check_orphan_layouts()
    check_less_selectors()
    check_sitemap()
    check_a11y(pages)
    check_seo(pages)
    check_build_output()
    check_redirects()
    check_dead_code(pages)
    check_weight(pages)
    check_lastmod()

    print()
    for label, bucket in (('FAIL', FAILS), ('WARN', WARNS), ('INFO', INFOS)):
        if not bucket:
            continue
        grouped = defaultdict(list)
        for check, detail in bucket:
            grouped[check].append(detail)
        print(f'{label} ({len(bucket)})')
        for check, details in grouped.items():
            print(f'  {check}  x{len(details)}')
            for d in details[:3]:
                if d:
                    print(f'      {d}')
            if len(details) > 3:
                print(f'      … and {len(details) - 3} more')
        print()

    if FAILS:
        print(f'FAILED — {len(FAILS)} problem(s)\n')
        return 1
    print('All checks passed.'
          + (f' {len(WARNS)} warning(s) worth a look.' if WARNS else '') + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
