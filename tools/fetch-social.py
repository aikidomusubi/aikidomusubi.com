#!/usr/bin/env python3
"""Collect Instagram posts/reels and Facebook albums into the gallery.

Used twice: once by hand to load the back catalogue, then nightly by
.github/workflows/gallery.yml. Both runs do the same thing.

WHAT IT DOES

  * asks Meta what has been posted
  * downloads each item's thumbnail into images/ as .jpg and .webp
  * appends an entry to _data/gallery.yml with `show: false`

Nothing it adds reaches the site until that flag is flipped to true. That is
deliberate: the page is a showcase, not a mirror of the feed, and an unattended
job that could publish on its own would make it one.

WHY THUMBNAILS ARE DOWNLOADED RATHER THAN HOTLINKED

Meta's CDN URLs are signed and expire within days, so a hotlinked gallery would
quietly turn into broken images. Copying the file also means a visitor loads
nothing from Meta and so is not tracked by it.

USAGE

    export FB_TOKEN=...          # Page access token (does not expire)
    export FB_PAGE_ID=...        # numeric page id
    export IG_USER_ID=...        # the Instagram Business account behind the Page

    .venv/bin/python tools/fetch-social.py --discover   # find the three values

Or, if you went the Instagram-login route instead:

    export IG_TOKEN=...          # Instagram user token, expires in ~60 days

    .venv/bin/python tools/fetch-social.py --csv        # list it, write nothing
    .venv/bin/python tools/fetch-social.py --dry-run    # show what would change
    .venv/bin/python tools/fetch-social.py              # download and append
    .venv/bin/python tools/fetch-social.py --limit 20   # only the 20 newest

Setup, once:  python3 -m venv .venv && .venv/bin/pip install requests pillow
"""

import argparse
import io
import os
import re
import sys
import datetime as dt

try:
    import requests
    from PIL import Image
except ImportError:
    # Homebrew's Python refuses system-wide installs (PEP 668), so the advice
    # has to be the venv rather than `pip install`.
    sys.exit(
        "Missing dependencies.\n\n"
        "Use the project virtualenv:\n"
        "    .venv/bin/python tools/fetch-social.py ...\n\n"
        "If .venv does not exist yet, create it once:\n"
        "    python3 -m venv .venv && .venv/bin/pip install requests pillow\n")

GRAPH_IG = "https://graph.instagram.com/v21.0"
GRAPH_FB = "https://graph.facebook.com/v21.0"
DATA = "_data/gallery.yml"
IMAGES = "images"

# Wide enough for the largest tile at 2x without being wasteful — the grid never
# shows one bigger than about 480 CSS px.
THUMB_W = 960


# ---------------------------------------------------------------------------
# Meta
# ---------------------------------------------------------------------------
def paged(url, params, limit=None):
    """Walk a Graph API cursor to the end, or to `limit` items."""
    out = []
    while url:
        r = requests.get(url, params=params, timeout=30)
        if r.status_code != 200:
            sys.exit("Graph API %s: %s" % (r.status_code, r.text[:400]))
        body = r.json()
        out.extend(body.get("data", []))
        if limit and len(out) >= limit:
            return out[:limit]
        url = body.get("paging", {}).get("next")
        params = None          # `next` already carries every parameter
    return out


def instagram(token, limit=None, ig_user_id=None):
    """Instagram media, by whichever route is available.

    TWO ROUTES, SAME DATA:

      graph.facebook.com/{ig-user-id}/media   with a Page token   (preferred)
      graph.instagram.com/me/media            with an IG token

    The first is preferred because of who has to log in. App roles belong to
    Facebook accounts, so signing in as the Instagram account hits "insufficient
    developer role" unless that account is invited as a tester and accepts the
    invite from inside the Instagram app. Going through the Page means the app
    admin authenticates as themselves, which they already are — nothing to
    grant, nothing to accept, and the resulting Page token does not expire.
    """
    if ig_user_id:
        base = GRAPH_FB + "/%s/media" % ig_user_id
    else:
        base = GRAPH_IG + "/me/media"

    items = paged(base, {
        "fields": "id,caption,media_type,media_product_type,permalink,"
                  "media_url,thumbnail_url,timestamp",
        "limit": 100,
        "access_token": token,
    }, limit)
    out = []
    for m in items:
        # A reel is media_type VIDEO with media_product_type REELS. Plain videos
        # in the feed are VIDEO/FEED and are shown as posts.
        kind = "reel" if m.get("media_product_type") == "REELS" else "post"
        # For video the still is thumbnail_url; for an image the media itself is.
        thumb = m.get("thumbnail_url") or m.get("media_url")
        if not thumb:
            continue
        out.append({
            "type": kind,
            "date": m["timestamp"][:10],
            "url": m["permalink"],
            "thumb_src": thumb,
            "caption": (m.get("caption") or "").strip(),
            "id": m["id"],
        })
    return out


def discover(token):
    """Print the Pages this token can see and the Instagram account behind each.

    Run this first on the Facebook route: it turns a token into the two ids the
    rest of the script needs, without hunting through the Graph API Explorer.
    """
    r = requests.get(GRAPH_FB + "/me/accounts", params={
        "fields": "id,name,access_token,instagram_business_account{id,username}",
        "access_token": token,
    }, timeout=30)
    if r.status_code != 200:
        sys.exit("Graph API %s: %s" % (r.status_code, r.text[:400]))
    pages = r.json().get("data", [])
    if not pages:
        sys.exit("This token can see no Pages. Check pages_show_list was granted.")
    for p in pages:
        ig = p.get("instagram_business_account") or {}
        print("\nPage:        %s" % p.get("name"))
        print("  FB_PAGE_ID  %s" % p.get("id"))
        print("  FB_TOKEN    %s" % p.get("access_token", "")[:24] + "…  (full value below)")
        if ig:
            print("  IG_USER_ID  %s   (@%s)" % (ig.get("id"), ig.get("username")))
        else:
            print("  IG_USER_ID  -- no Instagram account linked to this Page --")
        print("\n  Full Page token:\n  %s" % p.get("access_token", ""))


# Albums Facebook makes by itself. They are not collections of anything — the
# profile picture history, every photo ever attached to a post — and they came
# back as four tiles of noise.
FB_AUTO_ALBUMS = {
    "photos", "mobile uploads", "profile pictures", "cover photos",
    "timeline photos", "untitled album", "instagram photos",
}


def album_date(name, created):
    """When the album is about, which is not always when it was uploaded.

    Several albums were uploaded in 2011, when the Page was first set up, but
    hold photographs from 2008 and 2009. Facebook does not let you edit an
    album's created_time, so the upload date is simply the wrong fact to sort by.

    The titles carry the right one — "Ricard Coll Sensei @ Andorra (2008)" — and
    reading it is a rule rather than an exception: it applies to every album, and
    for the ones uploaded in the year they happened it changes nothing.

    Where the two disagree, only the year is known, so the date becomes 1
    January of that year. An invented month would sort no better and would claim
    to know something we do not.
    """
    m = re.search(r"\((\d{4})\)\s*$", name or "")
    if not m:
        return created
    year = m.group(1)
    return created if created.startswith(year) else "%s-01-01" % year


def facebook_albums(token, page_id, limit=None):
    items = paged(GRAPH_FB + "/%s/albums" % page_id, {
        "fields": "id,name,created_time,count,link,privacy,cover_photo{source}",
        "limit": 100,
        "access_token": token,
    }, limit)
    out = []
    for a in items:
        if (a.get("name") or "").strip().lower() in FB_AUTO_ALBUMS:
            continue
        cover = (a.get("cover_photo") or {}).get("source")
        if not cover:
            continue
        out.append({
            "privacy": ((a.get("privacy") or {}).get("value") or "").upper(),
            "type": "album",
            "date": album_date(a.get("name"), a["created_time"][:10]),
            "url": a.get("link") or "",
            "thumb_src": cover,
            "caption": a.get("name") or "",
            "count": a.get("count"),
            "id": a["id"],
        })
    return out


def token_days_left(token):
    """Days until the Instagram long-lived token expires, or None."""
    try:
        r = requests.get(GRAPH_IG + "/refresh_access_token",
                         params={"grant_type": "ig_refresh_token",
                                 "access_token": token}, timeout=30)
        if r.status_code == 200:
            return int(r.json().get("expires_in", 0)) // 86400, r.json().get("access_token")
    except Exception:
        pass
    return None, None


# ---------------------------------------------------------------------------
# Thumbnails
# ---------------------------------------------------------------------------
def stem_for(date, caption, media_id):
    """A filename that is unique even when two posts share a caption.

    Three posts can go out the same day with the same words — the dojo posts a
    carousel as separate items — and naming from date plus caption gave all
    three the same file. save_thumb() skips a file that already exists, so the
    second and third silently pointed at the first one's picture. The media id
    is what makes them different, so a piece of it belongs in the name.
    """
    return "gallery-%s-%s-%s" % (date, slugify(caption, "post"), media_id[-6:])


def slugify(text, fallback):
    s = re.sub(r"[^\w\s-]", "", (text or "").lower(), flags=re.UNICODE)
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return (s[:40].rstrip("-") or fallback)


def save_thumb(url, stem):
    jpg = os.path.join(IMAGES, stem + ".jpg")
    webp = os.path.join(IMAGES, stem + ".webp")
    if os.path.exists(jpg) and os.path.exists(webp):
        return True
    r = requests.get(url, timeout=60)
    if r.status_code != 200:
        print("  ! thumbnail %s for %s" % (r.status_code, stem))
        return False
    im = Image.open(io.BytesIO(r.content))
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    if im.width > THUMB_W:
        im = im.resize((THUMB_W, round(im.height * THUMB_W / im.width)), Image.LANCZOS)
    im.save(jpg, "JPEG", quality=82, optimize=True, progressive=True)
    im.save(webp, "WEBP", quality=80, method=6)
    return True


# ---------------------------------------------------------------------------
# The data file
#
# Appended to as text rather than rewritten by a YAML dumper: the file is mostly
# comments explaining itself, and a dumper would throw all of them away.
# ---------------------------------------------------------------------------
def existing_urls(text):
    return set(re.findall(r'^\s*url:\s*"([^"]+)"', text, re.M))


def entry_block(item, stem, tags):
    lines = [
        '  - type: %s' % item["type"],
        '    date_iso: "%s"' % item["date"],
        '    name: "%s"' % (first_line(item["caption"]) or item["type"].title()),
        '    url: "%s"' % item["url"],
        '    thumb: "%s"' % stem,
        # The media id, kept so --thumbs can ask Meta for a fresh image URL.
        # The ones returned by the listing are signed and expire within days,
        # so they cannot be stored and used later.
        '    ref: "%s"' % item["id"],
        '    tags: [%s]' % ", ".join(tags),
    ]
    if item.get("count"):
        lines.append('    count: %d' % item["count"])
    # The flag that keeps an unattended job from publishing anything.
    lines.append('    show: false')
    return "\n".join(lines) + "\n"


def first_line(caption):
    line = (caption or "").strip().split("\n")[0].strip()
    line = re.sub(r"\s*#\w+", "", line).strip()          # drop trailing hashtags
    return line[:70].replace('"', "'")


def append(items, tags, dry, metadata_only=False):
    text = io.open(DATA, encoding="utf-8").read()
    seen = existing_urls(text)
    fresh = [i for i in items if i["url"] and i["url"] not in seen]
    if not fresh:
        print("Nothing new.")
        return 0

    if text.rstrip().endswith("entries: []"):
        text = text.rstrip()[: -len("[]")].rstrip() + "\n"

    blocks = []
    for it in sorted(fresh, key=lambda x: x["date"]):
        stem = stem_for(it["date"], it["caption"], it["id"])
        print("  + %-5s %s  %s" % (it["type"], it["date"], first_line(it["caption"])[:48]))
        if dry:
            continue
        if metadata_only:
            # No image yet. 773 thumbnails is ~100 MB, and most of them are for
            # posts that will never be shown; --thumbs fetches only the ones
            # actually approved.
            blocks.append(entry_block(it, "", tags))
            continue
        if not save_thumb(it["thumb_src"], stem):
            continue
        blocks.append(entry_block(it, stem, tags))

    if dry:
        return len(fresh)
    io.open(DATA, "w", encoding="utf-8").write(text + "".join(blocks))
    return len(blocks)


def fetch_thumbs(token, ig_user_id=None):
    """Download images for approved entries that do not have one yet.

    Phase two of the split flow: `--metadata-only` writes every post as a line
    of text, you flip `show: true` on the ones worth keeping, and this fetches
    images for exactly those. Meta's listing URLs expire within days, so each
    one is re-requested by id at the moment it is needed.
    """
    text = io.open(DATA, encoding="utf-8").read()
    # entries that are shown, carry a ref, and have no image yet
    pending = re.findall(
        r'  - type: (\w+)\n    date_iso: "([^"]+)"\n    name: "([^"]*)"\n'
        r'    url: "([^"]*)"\n    thumb: ""\n    ref: "([^"]+)"[^\n]*\n'
        r'    tags: \[[^\]]*\]\n(?:    count: \d+\n)?    show: true',
        text)
    if not pending:
        print("No approved entries are waiting for an image.")
        return 0

    done = 0
    for kind, date, name, url, ref in pending:
        fields = "cover_photo{source}" if kind == "album" else "thumbnail_url,media_url"
        host = GRAPH_FB if (kind == "album" or ig_user_id) else GRAPH_IG
        r = requests.get("%s/%s" % (host, ref),
                         params={"fields": fields, "access_token": token}, timeout=30)
        if r.status_code != 200:
            print("  ! %s %s: %s" % (date, ref, r.text[:120]))
            continue
        body = r.json()
        src = ((body.get("cover_photo") or {}).get("source")
               or body.get("thumbnail_url") or body.get("media_url"))
        if not src:
            print("  ! %s %s: no image in the response" % (date, ref))
            continue
        stem = stem_for(date, name, ref)
        if save_thumb(src, stem):
            text = text.replace('    url: "%s"\n    thumb: ""' % url,
                                '    url: "%s"\n    thumb: "%s"' % (url, stem), 1)
            print("  * %s  %s" % (date, name[:52]))
            done += 1
    io.open(DATA, "w", encoding="utf-8").write(text)
    return done


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", action="store_true", help="list everything, write nothing")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--tags", default="training",
                    help="tags for new entries (default: training)")
    ap.add_argument("--skip-facebook", action="store_true")
    ap.add_argument("--discover", action="store_true",
                    help="print the Page and Instagram ids this token can see")
    ap.add_argument("--metadata-only", action="store_true",
                    help="append entries without downloading any image")
    ap.add_argument("--thumbs", action="store_true",
                    help="download images for approved entries that lack one")
    ap.add_argument("--audit-albums", action="store_true",
                    help="check every approved album link is reachable by a visitor")
    args = ap.parse_args()

    ig_token = os.environ.get("IG_TOKEN")
    fb_token = os.environ.get("FB_TOKEN")
    fb_page = os.environ.get("FB_PAGE_ID")
    ig_user = os.environ.get("IG_USER_ID")

    if args.discover:
        if not fb_token:
            sys.exit("Set FB_TOKEN first.")
        discover(fb_token)
        return

    if args.audit_albums:
        # What is knowable, and nothing more.
        #
        # Facebook does not return `privacy` for Page albums at all — Page
        # content is public by nature, so the field does not exist there — and
        # an earlier version of this check read "field missing" as "not public"
        # and reported all 49 as private. It also cannot be tested by fetching
        # the link: Facebook answers 400 to anything that is not a real browser
        # session, whatever the album's privacy.
        #
        # So this lists the albums and their links, and the one reliable test is
        # named at the end for a human to run.
        if not fb_token:
            sys.exit("Set FB_TOKEN first.")
        text = io.open(DATA, encoding="utf-8").read()
        rows = re.findall(
            r'  - type: album\n(?:    .*\n)*?    name: "([^"]*)"\n'
            r'    url: "([^"]*)"\n(?:    .*\n)*?    ref: "([^"]+)"', text)
        for name, url, ref in rows:
            print("  %-46s %s" % (name[:46], url))
        print("\n%d albums." % len(rows))
        print("Facebook does not expose album privacy through the API, and it "
              "blocks scripted\nrequests, so neither can be checked from here. "
              "Open two or three of those links\nin a private window: if they "
              "open, they are public.")
        return

    if args.thumbs:
        token = fb_token or ig_token
        if not token:
            sys.exit("Set FB_TOKEN (or IG_TOKEN) first.")
        n = fetch_thumbs(token, ig_user)
        print("Fetched %d image%s" % (n, "" if n == 1 else "s"))
        return

    items = []
    # Preferred: the Page token reaching Instagram through the linked account.
    if fb_token and ig_user:
        items += instagram(fb_token, args.limit, ig_user_id=ig_user)
        print("Instagram (via Page): %d items" % len(items))
    elif ig_token:
        items += instagram(ig_token, args.limit)
        print("Instagram (direct): %d items" % len(items))
    else:
        print("Neither FB_TOKEN+IG_USER_ID nor IG_TOKEN set — skipping Instagram")

    if fb_token and fb_page and not args.skip_facebook:
        fb = facebook_albums(fb_token, fb_page, args.limit)
        items += fb
        print("Facebook: %d albums" % len(fb))

    if args.csv:
        print("\ntype,date,url,caption")
        for i in sorted(items, key=lambda x: x["date"], reverse=True):
            print('%s,%s,%s,"%s"' % (i["type"], i["date"], i["url"],
                                     first_line(i["caption"]).replace('"', "'")))
        return

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    n = append(items, tags, args.dry_run, args.metadata_only)
    print("%s %d entr%s" % ("Would add" if args.dry_run else "Added", n,
                            "y" if n == 1 else "ies"))

    # Only the graph.instagram.com token has a 60-day clock on it. A Page token
    # derived from a long-lived user token does not expire, so on that route
    # there is nothing to warn about.
    if ig_token and not (fb_token and ig_user):
        days, _ = token_days_left(ig_token)
        if days is not None:
            print("::notice::Instagram token expires in %d days" % days)
            if days < 10:
                print("::error::Instagram token expires in %d days — refresh it" % days)
                sys.exit(78)


if __name__ == "__main__":
    main()
