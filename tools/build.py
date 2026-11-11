#!/usr/bin/env python3
"""Regenerate sitemap.xml and rss.xml from the HTML pages, then check the site.

The HTML files in this repo are the source of truth. Edit them directly, then
run:

    python3 tools/build.py            # rebuild feeds, fail on any problem
    python3 tools/build.py --draft    # same, but allow [TO CONFIRM] markers

Checks: every local href/src/srcset resolves to a file, no page loads from
fonts.googleapis.com or another third party, every indexable page has a title,
description and canonical, and no page contains a [TO CONFIRM] marker.

Standard library only.
"""

import email.utils
import html
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "https://hyperbyte.cloud"
FEED_TITLE = "Hyperbyte Cloud"
FEED_DESC = "Notes on HyperbyteDB, InfluxDB v1 compatibility, and time-series engineering."
# Pages that must never be listed, whatever their robots tag says.
SKIP = {"/404.html"}
# Hosts a page may load scripts, styles or fonts from. Links (<a href>) are not limited.
ASSET_HOSTS = ()


def meta(page, attr, key):
    m = re.search(rf'<meta {attr}="{re.escape(key)}" content="([^"]*)"', page)
    return html.unescape(m.group(1)) if m else ""


def route_for(path):
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def git_date(path):
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path)],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        out = ""
    if out:
        return out
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).strftime("%Y-%m-%d")


def load_pages():
    pages = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
            continue
        text = path.read_text(encoding="utf-8")
        title = re.search(r"<title>(.*?)</title>", text, re.S)
        pages.append({
            "path": path,
            "route": route_for(path),
            "text": text,
            "title": html.unescape(title.group(1).strip()) if title else "",
            "description": meta(text, "name", "description"),
            "robots": meta(text, "name", "robots"),
            "canonical": (re.search(r'<link rel="canonical" href="([^"]*)"', text) or [None, ""])[1],
            "type": meta(text, "property", "og:type"),
            "published": meta(text, "property", "article:published_time")[:10],
            "modified": meta(text, "property", "article:modified_time")[:10],
        })
    return pages


def indexable(page):
    return (
        page["route"] not in SKIP
        and "noindex" not in page["robots"]
        and page["canonical"] == ORIGIN + page["route"]
    )


def write_sitemap(pages):
    rows = []
    for page in pages:
        if not indexable(page):
            continue
        lastmod = page["modified"] or page["published"] or git_date(page["path"])
        rows.append(f"<url><loc>{ORIGIN}{page['route']}</loc><lastmod>{lastmod}</lastmod></url>")
    body = "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        *rows,
        "</urlset>",
    ])
    (ROOT / "sitemap.xml").write_text(body + "\n", encoding="utf-8")
    return len(rows)


def rfc822(day):
    dt = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return email.utils.format_datetime(dt)


def esc(text):
    return html.escape(text, quote=True)


def write_rss(pages):
    posts = [p for p in pages if p["type"] == "article" and p["published"] and indexable(p)]
    posts.sort(key=lambda p: p["published"], reverse=True)
    items = []
    for post in posts:
        url = ORIGIN + post["route"]
        title = re.sub(r"\s+(?:\||—)\s+Hyperbyte(?:DB| Cloud)?$", "", post["title"])
        items.append(
            "    <item>\n"
            f"      <title>{esc(title)}</title>\n"
            f"      <link>{url}</link>\n"
            f'      <guid isPermaLink="true">{url}</guid>\n'
            f"      <pubDate>{rfc822(post['published'])}</pubDate>\n"
            f"      <description>{esc(post['description'])}</description>\n"
            "    </item>"
        )
    newest = rfc822(max(p["modified"] or p["published"] for p in posts)) if posts else ""
    xml = "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        f"    <title>{FEED_TITLE}</title>",
        f"    <link>{ORIGIN}/tag/blog/</link>",
        f"    <description>{FEED_DESC}</description>",
        "    <language>en-gb</language>",
        f"    <lastBuildDate>{newest}</lastBuildDate>",
        f'    <atom:link href="{ORIGIN}/rss.xml" rel="self" type="application/rss+xml"/>',
        *items,
        "  </channel>",
        "</rss>",
    ])
    (ROOT / "rss.xml").write_text(xml + "\n", encoding="utf-8")
    return len(items)


def local_target(url):
    url = unquote(url.split("#", 1)[0].split("?", 1)[0])
    if url.startswith(ORIGIN):
        url = url[len(ORIGIN):] or "/"
    if not url.startswith("/") or url.startswith("//"):
        return None
    target = ROOT / url.lstrip("/")
    if url.endswith("/"):
        target = target / "index.html"
    return target


def check(pages, draft):
    problems = []
    for page in pages:
        text, where = page["text"], page["route"]
        refs = re.findall(r'\s(?:href|src)="([^"]+)"', text)
        for srcset in re.findall(r'\ssrcset="([^"]+)"', text):
            refs += [part.strip().split()[0] for part in srcset.split(",") if part.strip()]
        for ref in refs:
            ref = html.unescape(ref)
            target = local_target(ref)
            if target is not None and not target.exists():
                problems.append(f"{where}: missing {ref}")
        for tag in re.findall(r"<(?:script|link)\b[^>]*>", text):
            if 'rel="canonical"' in tag or 'rel="alternate"' in tag or 'rel="prev"' in tag or 'rel="next"' in tag:
                continue
            m = re.search(r'(?:src|href)="(https?:)?//([^/"]+)', tag)
            if m and m.group(2) not in ASSET_HOSTS and m.group(2) != "hyperbyte.cloud":
                problems.append(f"{where}: loads from third party {m.group(2)}")
        if indexable(page):
            for field in ("title", "description"):
                if not page[field]:
                    problems.append(f"{where}: no {field}")
        elif page["route"] not in SKIP and "noindex" not in page["robots"]:
            problems.append(f"{where}: canonical {page['canonical'] or '(none)'} is not its own URL and page is not noindex")
        if not draft and "[TO CONFIRM" in text:
            problems.append(f"{where}: {text.count('[TO CONFIRM')} [TO CONFIRM] marker(s)")
    return problems


def main():
    draft = "--draft" in sys.argv[1:]
    pages = load_pages()
    urls = write_sitemap(pages)
    posts = write_rss(pages)
    problems = check(pages, draft)
    print(f"{len(pages)} pages, {urls} in sitemap, {posts} in rss.xml")
    for line in problems:
        print("  " + line)
    if problems:
        print(f"{len(problems)} problem(s)")
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
