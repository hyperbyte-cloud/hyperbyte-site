#!/usr/bin/env python3
"""Pull hyperbyte.cloud into this static site and stamp SEO on every page."""

import hashlib
import html
import json
import os
import re
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from lxml import etree, html as lhtml

ROOT = Path(__file__).resolve().parent
ORIGIN = "https://hyperbyte.cloud"
MEDIA = ROOT / "assets" / "media"
UA = {"User-Agent": "Mozilla/5.0 (compatible; HyperbyteSiteBuilder/1.0)"}

EARLY = "https://form.typeform.com/to/BhFaBgc5?ref=hyperbyte.cloud"
DOCS = "https://docs.hyperbyte.cloud"
GITHUB = "https://github.com/hyperbyte-cloud/hyperbytedb"
EMAIL = "hello@hyperbyte.cloud"

NAV = [
    ("/", "Product"),
    ("/hyperbytedb/", "Database"),
    ("/cloud/", "Cloud"),
    ("/solutions/", "Solutions"),
    ("/oss/", "OSS"),
    ("/pricing/", "Pricing"),
    ("/tag/blog/", "Blog"),
]

CASE_STUDIES = [
    ("/unlocking-scalable-iot-insights-with-hyperbytedb/", "IoT fleets"),
    ("/observability-and-monitoring-with-hyperbytedb/", "Observability"),
    ("/powering-real-time-financial-analytics-with-hyperbytedb/", "Market data"),
    ("/optimizing-energy-systems-with-hyperbytedb/", "Energy systems"),
]

SHORT_PAGES = {
    "/hyperbytedb/": (
        "HyperbyteDB",
        f'''<p>An open-source time-series database that speaks InfluxDB v1. Same line protocol, same InfluxQL. Tag cardinality is capacity, not a ceiling.</p>
<p><a href="{GITHUB}" rel="noopener">Source on GitHub</a> · <a href="/cloud/">Managed cloud</a> · <a href="{DOCS}" rel="noopener">Docs</a></p>
<h2 id="change-one-url">Change one URL</h2>
<ul>
<li>Same <code>/write</code> and <code>/query</code> endpoints</li>
<li>Same InfluxQL, Telegraf, and Grafana</li>
<li>Continuous queries and master-master replication, in the open-source binary</li>
</ul>
<p>The <a href="{DOCS}" rel="noopener">docs</a> cover the endpoints. The <a href="/influxdb-v1-migration-checklist-clients-url-change/">checklist</a> covers each client.</p>
<h2 id="the-numbers">The numbers</h2>
<table>
<tr><td>Sustained ingest</td><td>1.5M points/sec, p95 under 250ms</td></tr>
<tr><td>Peak ingest</td><td>1.9M points/sec</td></tr>
<tr><td>Measured on</td><td>AMD EPYC 7413, 24c/48t, 251GB RAM, single node</td></tr>
</table>
<p>The engine alone does about 99M rows a second. <a href="/from-99-million-to-1-9-million-what-an-ingest-benchmark-doesnt-tell-you/">Where the other 98% goes</a>.</p>
<h2 id="sharding">Sharding</h2>
<p>HyperbyteDB runs as a single node today. Sharding lands this year, and the cluster will be measured the same way ingest was.</p>
<h2 id="self-hosted-or-managed">Self-hosted or managed</h2>
<table>
<tr><td></td><td><strong>Self-hosted</strong></td><td><strong>Cloud</strong></td></tr>
<tr><td>Licence</td><td>Open source</td><td>Early access</td></tr>
<tr><td>InfluxDB v1</td><td>Full</td><td>Full</td></tr>
<tr><td>Replication and backups</td><td>Yours to run</td><td>Managed</td></tr>
<tr><td>Price</td><td>Free</td><td><a href="/pricing/">Published at general availability</a></td></tr>
</table>
<h2 id="workloads">Workloads</h2>
<ul>
<li><a href="/unlocking-scalable-iot-insights-with-hyperbytedb/">IoT fleets</a></li>
<li><a href="/observability-and-monitoring-with-hyperbytedb/">Observability</a></li>
<li><a href="/powering-real-time-financial-analytics-with-hyperbytedb/">Market data</a></li>
<li><a href="/optimizing-energy-systems-with-hyperbytedb/">Energy systems</a></li>
</ul>''',
    ),
    "/cloud/": (
        "Hyperbyte Cloud",
        f'''<p>Point Telegraf at a URL. Cloud runs HyperbyteDB: tuning, replication, upgrades, backups, and capacity.</p>
<p><a href="{EARLY}" rel="noopener">Request early access</a>. A small number of design partners before general availability.</p>
<h2 id="capacity">Capacity</h2>
<table>
<tr><td>Sustained ingest</td><td>1.5M points/sec, p95 under 250ms</td></tr>
<tr><td>Peak ingest</td><td>1.9M points/sec</td></tr>
<tr><td>Measured on</td><td>AMD EPYC 7413, 24c/48t, 251GB RAM, single node</td></tr>
</table>
<p>The engine alone does about 99M rows a second. <a href="/from-99-million-to-1-9-million-what-an-ingest-benchmark-doesnt-tell-you/">Where the other 98% goes</a>.</p>
<h2 id="what-stays">What stays</h2>
<ul>
<li>Same <code>/write</code> and <code>/query</code> endpoints</li>
<li>Same InfluxQL, Telegraf, and Grafana</li>
<li>Continuous queries and replication included</li>
</ul>
<h2 id="self-hosted-or-managed">Self-hosted or managed</h2>
<table>
<tr><td></td><td><strong>Self-hosted</strong></td><td><strong>Cloud</strong></td></tr>
<tr><td>Licence</td><td>Open source</td><td>Early access</td></tr>
<tr><td>InfluxDB v1</td><td>Full</td><td>Full</td></tr>
<tr><td>Replication and backups</td><td>Yours to run</td><td>Managed</td></tr>
<tr><td>Support</td><td>Community</td><td><a href="/connect-with-us/">Direct</a></td></tr>
<tr><td>Price</td><td>Free</td><td><a href="/pricing/">Published at general availability</a></td></tr>
</table>
<h2 id="still-ahead">Still ahead</h2>
<p>Regions, a published uptime SLA, compliance certification, and bring-your-own-cloud. Early access is how design partners choose the order. <a href="/pricing/">Pricing</a> is published when it is real.</p>''',
    ),
    "/solutions/": (
        "Solutions",
        f'''<p>Same InfluxDB v1 endpoints, for telemetry that is spread out.</p>
<ul>
<li><a href="/unlocking-scalable-iot-insights-with-hyperbytedb/">IoT fleets</a>. Full-resolution sensor data, queried with the InfluxQL you already use.</li>
<li><a href="/observability-and-monitoring-with-hyperbytedb/">Observability</a>. High-cardinality metrics, with Telegraf and Grafana left as they are.</li>
<li><a href="/powering-real-time-financial-analytics-with-hyperbytedb/">Market data</a>. Tick-level ingest, millisecond queries.</li>
<li><a href="/optimizing-energy-systems-with-hyperbytedb/">Energy systems</a>. Grid and asset telemetry at full resolution.</li>
</ul>
<p><a href="/hyperbytedb/">HyperbyteDB</a> is free to self-host. <a href="/cloud/">Cloud</a> runs it. <a href="{DOCS}" rel="noopener">Docs</a>.</p>''',
    ),
}

POST_URLS = [
    "/why-influxdb-enterprise-pricing-hits-a-wall/",
    "/telegraf-grafana-alerts-stack-database-that-doesnt-buckle/",
    "/stop-watching-metrics-explode-high-cardinality-without-rewrite/",
    "/scaling-chdb-inserts-from-5-million-to-99-million-rows-second/",
    "/influxdb-v1-migration-checklist-clients-url-change/",
    "/influxdb-v1-kubernetes-operator-swap-keep-urls/",
    "/influxdb-v1-compatibility-drop-in/",
    "/from-99-million-to-1-9-million-what-an-ingest-benchmark-doesnt-tell-you/",
    "/exporting-historical-time-series-influxdb-v1-to-hyperbytedb/",
    "/every-sensor-every-tick-influxql-analytics-iot-data-scale/",
    "/before-you-trust-our-numbers-run-this/",
]

PAGE_URLS = [
    "/optimizing-energy-systems-with-hyperbytedb/",
    "/powering-real-time-financial-analytics-with-hyperbytedb/",
    "/observability-and-monitoring-with-hyperbytedb/",
    "/unlocking-scalable-iot-insights-with-hyperbytedb/",
    "/about-us/",
    "/hyperbytedb/",
    "/pricing/",
    "/cloud/",
    "/solutions/",
    "/connect-with-us/",
    "/oss/",
    "/privacy/",
    "/terms/",
    "/dpa/",
]

image_cache = {}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as resp:
        return resp.read()


def decode_cf(hexstr):
    key = int(hexstr[:2], 16)
    return "".join(chr(int(hexstr[i : i + 2], 16) ^ key) for i in range(2, len(hexstr), 2))


def esc(text):
    return html.escape(text or "", quote=True)


def fix_text(text):
    if not text:
        return text
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def abs_url(path):
    if not path.startswith("/"):
        path = "/" + path
    return ORIGIN + path


def canonical_path(href):
    if not href:
        return None
    href = href.strip()
    if href.startswith(("mailto:", "tel:", "#")):
        return href
    if href.startswith("//"):
        href = "https:" + href
    fragment = ""
    if "#" in href:
        href, fragment = href.split("#", 1)
        fragment = "#" + fragment
    href = href.split("?")[0]
    host = ""
    path = href
    if href.startswith("http"):
        parsed = urlparse(href)
        host = parsed.netloc.lower().removeprefix("www.")
        if host not in ("hyperbyte.cloud",):
            return None
        path = parsed.path or "/"
    if not path.startswith("/"):
        return None
    if path == "/home" or path == "/home/":
        path = "/"
    if path != "/" and not path.endswith("/"):
        path += "/"
    return path + fragment


def localize_image(url):
    if not url or url.startswith("data:"):
        return url
    full = url
    if full.startswith("//"):
        full = "https:" + full
    elif full.startswith("/"):
        full = ORIGIN + full
    if "hyperbyte.cloud" not in full and "ghost.org" not in full:
        return url
    if "publication-cover" in full:
        return "/assets/logo.png"
    if full in image_cache:
        return image_cache[full]
    ext = os.path.splitext(urlparse(full).path)[1].lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
        ext = ".jpg"
    name = hashlib.sha1(full.encode()).hexdigest()[:16] + ext
    dest = MEDIA / name
    if not dest.exists():
        try:
            dest.write_bytes(fetch(full))
        except Exception as exc:
            print("image failed", full, exc)
            image_cache[full] = url
            return url
    local = "/assets/media/" + name
    image_cache[full] = local
    return local


def rewrite_srcset(value):
    parts = []
    for chunk in value.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        bits = chunk.split()
        bits[0] = localize_image(bits[0])
        parts.append(" ".join(bits))
    return ", ".join(parts)


def clean_fragment(section):
    raw = "".join(etree.tostring(child, encoding="unicode", method="html") for child in section)
    if not raw.strip():
        raw = "<p></p>"
    frag = lhtml.fragment_fromstring(raw, create_parent="div")
    for bad in frag.xpath(".//script|.//style|.//iframe"):
        bad.getparent().remove(bad)
    for node in frag.xpath(".//*[@data-cfemail]"):
        email = decode_cf(node.get("data-cfemail"))
        parent = node.getparent()
        if parent is not None and parent.tag == "a":
            parent.set("href", "mailto:" + email)
            parent.text = email
            for child in list(parent):
                parent.remove(child)
        else:
            node.text = email
    for anchor in frag.xpath(".//a[@href]"):
        href = anchor.get("href")
        if href and "email-protection" in href:
            continue
        local = canonical_path(href)
        if local:
            anchor.set("href", local)
            if anchor.get("rel"):
                anchor.attrib.pop("rel", None)
        elif href and href.startswith("http"):
            anchor.set("rel", "noopener")
    for img in frag.xpath(".//img"):
        src = img.get("src")
        if src:
            img.set("src", localize_image(src))
        if img.get("srcset"):
            img.set("srcset", rewrite_srcset(img.get("srcset")))
        if not (img.get("alt") or "").strip():
            img.set("alt", "")
    for node in frag.xpath(".//*[@srcset]"):
        if node.tag == "img":
            continue
        node.set("srcset", rewrite_srcset(node.get("srcset")))
    for heading in frag.xpath(".//h1"):
        heading.tag = "h2"
    for heading in frag.xpath(".//h2|.//h3"):
        if not heading.get("id"):
            text = " ".join(heading.itertext()).strip().lower()
            slug = re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:80]
            if slug:
                heading.set("id", slug)
    for node in frag.xpath(".//text()"):
        parent = node.getparent()
        if parent is None:
            continue
        fixed = fix_text(node)
        if node.is_text:
            parent.text = fixed
        else:
            parent.tail = fixed
    for anchor in frag.xpath(".//a[not(@href)]"):
        label = " ".join(anchor.itertext()).strip().lower()
        if label == "earlier post":
            anchor.set("href", "/scaling-chdb-inserts-from-5-million-to-99-million-rows-second/")
    return frag


def meta_content(doc, prop=None, name=None):
    if prop:
        found = doc.xpath(f'//meta[@property="{prop}"]/@content')
    else:
        found = doc.xpath(f'//meta[@name="{name}"]/@content')
    return found[0].strip() if found else ""


def text_of(doc, xpath):
    nodes = doc.xpath(xpath)
    if not nodes:
        return ""
    return " ".join(nodes[0].itertext()).strip()


def load_document(path, kind):
    url = ORIGIN + path
    print("fetch", path)
    doc = lhtml.fromstring(fetch(url))
    title = meta_content(doc, prop="og:title") or text_of(doc, "//title")
    title = fix_text(re.sub(r"\s+", " ", html.unescape(title)).strip())
    title = re.sub(r"\s+(?:\||—|-)\s+Hyperbyte(?:DB| Cloud)?$", "", title).strip()
    description = fix_text(html.unescape(meta_content(doc, name="description")))
    description = re.sub(r"\s+", " ", description).strip()
    published = meta_content(doc, prop="article:published_time")[:10]
    modified = meta_content(doc, prop="article:modified_time")[:10] or published
    sections = doc.xpath('//article//section[contains(@class,"gh-content")]')
    if not sections:
        sections = doc.xpath('//section[contains(@class,"gh-content")]')
    content = clean_fragment(sections[0]) if sections else lhtml.fragment_fromstring("<p></p>", create_parent="div")
    if not description:
        paragraph = content.xpath(".//p")
        if paragraph:
            description = " ".join(paragraph[0].itertext())
            description = re.sub(r"\s+", " ", description).strip()[:155]
    tags = []
    articles = doc.xpath('//article[contains(@class,"post")]')
    if articles:
        seen = set()
        for token in articles[0].get("class", "").split():
            if not token.startswith("tag-") or token.startswith("tag-hash"):
                continue
            slug = token[4:]
            if slug in {"blog", "featured"} or slug in seen:
                continue
            seen.add(slug)
            tags.append((f"/tag/{slug}/", slug.replace("-", " ")))
    words = len(re.findall(r"\w+", " ".join(content.itertext())))
    minutes = max(1, round(words / 220))
    read = re.search(r"(\d+)\s*min read", " ".join(doc.xpath("//text()")))
    if read:
        minutes = int(read.group(1))
    image = meta_content(doc, prop="og:image")
    image_local = localize_image(image) if image and "publication-cover" not in image else ""
    headings = []
    for heading in content.xpath(".//h2"):
        hid = heading.get("id")
        label = " ".join(heading.itertext()).strip()
        if hid and label:
            headings.append((hid, label))
    loaded = {
        "path": path,
        "kind": kind,
        "title": title,
        "description": description[:300],
        "published": published,
        "modified": modified,
        "tags": tags,
        "minutes": minutes,
        "image": image_local,
        "content": content,
        "headings": headings,
    }
    return apply_short_page(loaded)


def apply_short_page(doc):
    short = SHORT_PAGES.get(doc["path"])
    if not short:
        return doc
    label, markup = short
    content = lhtml.fragment_fromstring(markup, create_parent="div")
    headings = []
    for heading in content.xpath(".//h2"):
        hid = heading.get("id")
        text = " ".join(heading.itertext()).strip()
        if hid and text:
            headings.append((hid, text))
    doc["display"] = label
    doc["content"] = content
    doc["headings"] = headings
    doc["image"] = ""
    return doc


def inner(frag):
    return "".join(etree.tostring(child, encoding="unicode", method="html") for child in frag)


def json_ld(data):
    raw = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return f'<script type="application/ld+json">{raw}</script>'


def org_node():
    return {
        "@type": "Organization",
        "@id": ORIGIN + "/#org",
        "name": "Hyperbyte Cloud",
        "url": ORIGIN + "/",
        "email": EMAIL,
        "logo": {
            "@type": "ImageObject",
            "url": ORIGIN + "/assets/logo.png",
        },
        "sameAs": [GITHUB],
    }


def crumbs(items):
    parts = ['<nav class="crumbs" aria-label="Breadcrumb"><ol>']
    ld_items = []
    for i, (href, label) in enumerate(items, start=1):
        sep = '<span aria-hidden="true">/</span>' if i < len(items) else ""
        if i < len(items):
            parts.append(f'<li><a href="{esc(href)}">{esc(label)}</a>{sep}</li>')
        else:
            parts.append(f'<li><span aria-current="page">{esc(label)}</span></li>')
        ld_items.append({
            "@type": "ListItem",
            "position": i,
            "name": label,
            "item": abs_url(href),
        })
    parts.append("</ol></nav>")
    return "".join(parts), {
        "@type": "BreadcrumbList",
        "itemListElement": ld_items,
    }


def nav_html(current):
    links = []
    for href, label in NAV:
        current_attr = ' aria-current="page"' if href == current else ""
        links.append(f'<a href="{href}"{current_attr}>{label}</a>')
    links.append(f'<a href="{DOCS}" rel="noopener">Docs</a>')
    links.append(f'<a class="btn btn-primary" href="{EARLY}" rel="noopener">Request early access</a>')
    return f'''
    <a class="skip" href="#main">Skip to content</a>
    <header class="site-header">
      <div class="wrap">
        <a class="brand" href="/">
          <img src="/assets/logo.png" width="28" height="28" alt="">
          Hyperbyte
        </a>
        <button class="menu-btn" type="button" data-menu aria-expanded="false" aria-controls="site-nav">Menu</button>
        <nav class="nav" id="site-nav" data-nav aria-label="Primary">{"".join(links)}</nav>
      </div>
    </header>'''


def footer_html():
    return f'''
    <footer class="site-footer">
      <div class="wrap">
        <span class="footer-brand"><img src="/assets/hyperbyte-cloud-mark.jpg" width="1024" height="388" alt="Hyperbyte Cloud" loading="lazy"> © 2026</span>
        <nav aria-label="Footer">
          <a href="/about-us/">About</a>
          · <a href="/connect-with-us/">Contact</a>
          · <a href="/pricing/">Pricing</a>
          · <a href="/oss/">Open source</a>
          · <a href="/privacy/">Privacy</a>
          · <a href="/terms/">Terms</a>
          · <a href="/dpa/">DPA</a>
          · <a href="{DOCS}" rel="noopener">Docs</a>
          · <a href="{GITHUB}" rel="noopener">GitHub</a>
          · <a href="mailto:{EMAIL}">{EMAIL}</a>
        </nav>
      </div>
    </footer>
    <script src="/assets/site.js"></script>'''


def cta_html(extra=""):
    return f'''
    <div class="cta-band">
      <div class="wrap">
        <p class="kicker">Next step</p>
        <h2>Run it yourself, or let us run it.</h2>
        <p class="lede">HyperbyteDB is free to self-host. Cloud early access is a short form, and a person reads it.</p>
        <div class="actions">
          <a class="btn btn-primary" href="{EARLY}" rel="noopener">Request early access</a>
          <a class="btn btn-ghost" href="{GITHUB}" rel="noopener">Self-host on GitHub</a>
          <a class="btn btn-ghost" href="/connect-with-us/">Talk to an engineer</a>
          <a class="btn btn-ghost" href="{DOCS}" rel="noopener">Read the docs</a>
        </div>
        {extra}
      </div>
    </div>'''


def head(page):
    path = page["path"]
    url = abs_url(path)
    title = page["title"]
    if "Hyperbyte" not in title and len(title) < 48:
        full_title = f"{title} — Hyperbyte Cloud"
    else:
        full_title = title
    desc = page["description"]
    image = page.get("image") or "/assets/logo.png"
    image_url = ORIGIN + image if image.startswith("/") else image
    robots = page.get("robots", "index, follow")
    og_type = page.get("og_type", "website")
    card = "summary_large_image" if page.get("image") else "summary"
    fonts = '''
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'''
    extra = page.get("head_extra", "")
    ld = json_ld(page["jsonld"]) if page.get("jsonld") else ""
    published = f'\n    <meta property="article:published_time" content="{esc(page["published"])}">' if page.get("published") else ""
    modified = f'\n    <meta property="article:modified_time" content="{esc(page["modified"])}">' if page.get("modified") else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#000000">
    <meta property="og:locale" content="en_GB">
    <title>{esc(full_title)}</title>
    <meta name="description" content="{esc(desc)}">
    <link rel="canonical" href="{esc(url)}">
    <meta name="robots" content="{esc(robots)}">
    <meta property="og:site_name" content="Hyperbyte Cloud">
    <meta property="og:type" content="{esc(og_type)}">
    <meta property="og:title" content="{esc(full_title)}">
    <meta property="og:description" content="{esc(desc)}">
    <meta property="og:url" content="{esc(url)}">
    <meta property="og:image" content="{esc(image_url)}">
    <meta name="twitter:card" content="{card}">
    <meta name="twitter:title" content="{esc(full_title)}">
    <meta name="twitter:description" content="{esc(desc)}">
    <meta name="twitter:image" content="{esc(image_url)}">{published}{modified}
    <link rel="icon" href="/assets/logo.png" type="image/png">
    <link rel="alternate" type="application/rss+xml" title="Hyperbyte Cloud" href="{ORIGIN}/rss.xml">
    {fonts}
    <link rel="stylesheet" href="/assets/site.css">
    {ld}
    {extra}
</head>'''


def page_shell(page, body):
    return head(page) + f"<body>{nav_html(page.get('nav', page['path']))}{body}{footer_html()}</body></html>\n"


def write(rel, text):
    dest = ROOT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text)
    print("wrote", rel)


def related_posts(doc, posts):
    mine = {path for path, _ in doc["tags"]}
    ranked = []
    for other in posts:
        if other["path"] == doc["path"]:
            continue
        shared = len(mine & {path for path, _ in other["tags"]})
        ranked.append((shared, other["published"], other))
    ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
    return [row[2] for row in ranked[:3]]


def related_html(items):
    if not items:
        return ""
    links = []
    for item in items:
        links.append(
            f'<a href="{esc(item["path"])}"><strong>{esc(item["title"])}</strong><br><span>{esc(item["description"][:140])}</span></a>'
        )
    return f'<section class="wrap" aria-labelledby="related-heading"><h2 id="related-heading">Keep reading</h2><div class="related">{"".join(links)}</div></section>'


def toc_html(headings):
    if len(headings) < 3:
        return ""
    items = "".join(f'<li><a href="#{esc(hid)}">{esc(label)}</a></li>' for hid, label in headings)
    return f'<nav class="toc" aria-label="On this page"><p>On this page</p><ol>{items}</ol></nav>'


def tag_links(tags, indexable):
    parts = []
    for path, label in tags:
        if path in indexable:
            parts.append(f'<a href="{esc(path)}">{esc(label)}</a>')
        else:
            parts.append(esc(label))
    return " · ".join(parts)


def render_article(doc, posts, indexable_tags):
    heading = doc.get("display") or doc["title"]
    crumb_html, crumb_ld = crumbs([
        ("/", "Home"),
        ("/tag/blog/", "Blog") if doc["kind"] == "post" else ("/solutions/", "Solutions") if doc["path"] in {p for p, _ in CASE_STUDIES} else ("/", "Home"),
        (doc["path"], heading),
    ])
    if doc["kind"] != "post" and doc["path"] not in {p for p, _ in CASE_STUDIES}:
        crumb_html, crumb_ld = crumbs([("/", "Home"), (doc["path"], heading)])
    figure = ""
    if doc["image"]:
        figure = f'<figure class="hero-img"><img src="{esc(doc["image"])}" alt="{esc(doc["title"])}"></figure>'
    meta = ""
    if doc["kind"] == "post":
        meta = (
            f'<p class="post-meta"><time datetime="{esc(doc["published"])}">{esc(doc["published"])}</time>'
            f'<span>{doc["minutes"]} min read</span>'
            f'<a href="/author/austin/">Austin</a>'
            f'<span>{tag_links(doc["tags"], indexable_tags)}</span></p>'
        )
    graph = [org_node(), crumb_ld]
    if doc["kind"] == "post":
        graph.append({
            "@type": "BlogPosting",
            "headline": doc["title"],
            "description": doc["description"],
            "datePublished": doc["published"],
            "dateModified": doc["modified"] or doc["published"],
            "author": {"@type": "Person", "name": "Austin", "url": ORIGIN + "/author/austin/"},
            "publisher": {"@id": ORIGIN + "/#org"},
            "mainEntityOfPage": abs_url(doc["path"]),
            "image": ORIGIN + doc["image"] if doc["image"] else ORIGIN + "/assets/logo.png",
            "keywords": ", ".join(label for _, label in doc["tags"]),
        })
    pager = ""
    if doc["kind"] == "post":
        ordered = [item for item in posts]
        index = next(i for i, item in enumerate(ordered) if item["path"] == doc["path"])
        newer = ordered[index - 1] if index > 0 else None
        older = ordered[index + 1] if index + 1 < len(ordered) else None
        links = []
        head_bits = []
        if newer:
            links.append(f'<a rel="prev" href="{esc(newer["path"])}"><small>Newer</small>{esc(newer["title"])}</a>')
            head_bits.append(f'<link rel="prev" href="{abs_url(newer["path"])}">')
        if older:
            links.append(f'<a rel="next" href="{esc(older["path"])}"><small>Older</small>{esc(older["title"])}</a>')
            head_bits.append(f'<link rel="next" href="{abs_url(older["path"])}">')
        pager = f'<nav class="pager" aria-label="More posts">{"".join(links)}</nav>'
        doc["head_extra"] = "\n".join(head_bits)
        graph[-1]["wordCount"] = len(re.findall(r"\w+", " ".join(doc["content"].itertext())))
        graph[-1]["inLanguage"] = "en-GB"
    siblings = ""
    if doc["path"] in {p for p, _ in CASE_STUDIES}:
        links = "".join(
            f'<a href="{esc(path)}">{esc(label)}</a>'
            for path, label in CASE_STUDIES if path != doc["path"]
        )
        siblings = f'<p class="post-meta">Other workloads: {links} · <a href="/solutions/">All solutions</a></p>'
    body = f'''
    <main id="main">
      <article class="wrap page-head">
        {crumb_html}
        <h1>{esc(heading)}</h1>
        {meta}
        {figure}
        {toc_html(doc["headings"])}
        <div class="prose">{inner(doc["content"])}</div>
        {siblings}
        {pager}
      </article>
      {"" if doc["path"] in SHORT_PAGES else related_html(related_posts(doc, posts if doc["kind"] == "post" else posts))}
      {cta_html()}
    </main>'''
    page = {
        **doc,
        "og_type": "article" if doc["kind"] == "post" else "website",
        "jsonld": {"@context": "https://schema.org", "@graph": graph},
        "nav": "/tag/blog/" if doc["kind"] == "post" else doc["path"] if doc["path"] in {href for href, _ in NAV} else "",
    }
    write(doc["path"].strip("/") + "/index.html", page_shell(page, body))


def render_listing(path, title, description, intro, items, json_type, robots="index, follow"):
    cards = []
    for item in items:
        cards.append(
            f'''<a class="post" href="{esc(item["path"])}">
              <header><time datetime="{esc(item["published"])}">{esc(item["published"])}</time><span>{item["minutes"]} min read</span></header>
              <h2>{esc(item["title"])}</h2>
              <p>{esc(item["description"][:220])}</p>
            </a>'''
        )
    crumb_html, crumb_ld = crumbs([("/", "Home"), (path, title)])
    graph = [
        org_node(),
        crumb_ld,
        {
            "@type": json_type,
            "name": title,
            "description": description,
            "url": abs_url(path),
            "blogPost": [{"@type": "BlogPosting", "headline": item["title"], "url": abs_url(item["path"])} for item in items],
        },
    ]
    body = f'''
    <main id="main">
      <div class="wrap page-head">
        {crumb_html}
        <p class="kicker">Hyperbyte Cloud</p>
        <h1>{esc(title)}</h1>
        <p>{esc(intro)}</p>
      </div>
      <div class="wrap posts">{"".join(cards)}</div>
      {cta_html()}
    </main>'''
    page = {
        "path": path,
        "title": title,
        "description": description,
        "robots": robots,
        "jsonld": {"@context": "https://schema.org", "@graph": graph},
        "nav": path if path in {href for href, _ in NAV} else "/tag/blog/",
    }
    write(path.strip("/") + "/index.html", page_shell(page, body))


def home_page(posts):
    featured = posts[:4]
    notes = "".join(
        f'<a href="{esc(p["path"])}">{esc(p["title"])}</a>' for p in featured
    )
    cases = "".join(f'<a href="{esc(path)}">{esc(label)}</a>' for path, label in CASE_STUDIES)
    graph = [
        org_node(),
        {
            "@type": "WebSite",
            "@id": ORIGIN + "/#website",
            "url": ORIGIN + "/",
            "name": "Hyperbyte Cloud",
            "publisher": {"@id": ORIGIN + "/#org"},
        },
        {
            "@type": "SoftwareApplication",
            "name": "HyperbyteDB",
            "applicationCategory": "DeveloperApplication",
            "operatingSystem": "Linux",
            "description": "InfluxDB v1-compatible time-series database built for high cardinality. Open source, self-hosted or managed.",
            "url": ORIGIN + "/hyperbytedb/",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        },
        {
            "@type": "HowTo",
            "name": "Move an InfluxDB v1 stack to HyperbyteDB",
            "description": "Run HyperbyteDB, point existing clients at it, and keep the tags you actually need.",
            "step": [
                {"@type": "HowToStep", "position": 1, "name": "Run the binary", "text": "Pull ghcr.io/hyperbyte-cloud/hyperbytedb and listen on port 8086, or hand the node to Hyperbyte Cloud.", "url": ORIGIN + "/#how"},
                {"@type": "HowToStep", "position": 2, "name": "Point the clients", "text": "Keep Telegraf, Grafana, and InfluxQL. Change the URL.", "url": ORIGIN + "/influxdb-v1-migration-checklist-clients-url-change/"},
                {"@type": "HowToStep", "position": 3, "name": "Tag what you need", "text": "Cardinality becomes a capacity question instead of a ceiling.", "url": ORIGIN + "/stop-watching-metrics-explode-high-cardinality-without-rewrite/"},
            ],
        },
        {
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": "Is HyperbyteDB a drop-in for InfluxDB v1?", "acceptedAnswer": {"@type": "Answer", "text": "It speaks line protocol and InfluxQL on the same /write and /query endpoints."}},
                {"@type": "Question", "name": "Is self-hosting free?", "acceptedAnswer": {"@type": "Answer", "text": "Yes. No feature gates. Replication, retention, and continuous queries are in the open-source binary."}},
                {"@type": "Question", "name": "What ingest number should a capacity plan use?", "acceptedAnswer": {"@type": "Answer", "text": "1.5 million points a second sustained, p95 under 250ms, on an AMD EPYC 7413 with 251GB RAM. Peak was about 1.9 million."}},
                {"@type": "Question", "name": "Does sharding exist today?", "acceptedAnswer": {"@type": "Answer", "text": "HyperbyteDB runs as a single node today. Sharding lands this year."}},
                {"@type": "Question", "name": "What is still ahead for Cloud?", "acceptedAnswer": {"@type": "Answer", "text": "Regions, a published uptime SLA, formal compliance certification, and bring-your-own-cloud."}},
            ],
        },
    ]
    body = f'''
    <main id="main">
      <section class="hero">
        <div class="wrap">
          <p class="kicker">Open source · InfluxDB v1 compatible</p>
          <h1>A sharded, infinite-cardinality database built for <em>time-series data.</em></h1>
          <p class="lede">Cardinality is where time-series databases stop. Add a container ID, a device serial, a player session, and InfluxDB v1 goes from milliseconds to seconds. HyperbyteDB shards across nodes so cardinality is a capacity question, and speaks InfluxDB v1 line protocol and InfluxQL, so switching costs one URL.</p>
          <div class="actions">
            <a class="btn btn-primary" href="{GITHUB}" rel="noopener">Self-host on GitHub</a>
            <a class="btn btn-ghost" href="/cloud/">See managed cloud</a>
            <a class="btn btn-ghost" href="{DOCS}" rel="noopener">Read the docs</a>
          </div>
        </div>
      </section>
      <div class="wrap">
        <dl class="metrics" id="numbers">
          <div class="metric"><dt>Sustained ingest</dt><dd>1.5M<span> pts/s</span></dd><p>p95 under 250ms. The figure that survives a capacity plan. <a href="/from-99-million-to-1-9-million-what-an-ingest-benchmark-doesnt-tell-you/">Where the other 98% goes</a>.</p></div>
          <div class="metric"><dt>Peak ingest</dt><dd>1.9M<span> pts/s</span></dd><p>Same machine, ramp test, durable writes. <a href="/before-you-trust-our-numbers-run-this/">Run the benchmark yourself</a>.</p></div>
          <div class="metric"><dt>Measured on</dt><dd>EPYC 7413</dd><p>24c/48t, 251GB RAM, single node. Engine ceiling about 99M rows/s with nothing in front of it.</p></div>
        </dl>
      </div>
      <section id="problem">
        <div class="wrap split">
          <div>
            <p class="kicker">The problem</p>
            <h2>The problem is tags, not volume.</h2>
            <div class="prose">
              <p>Time-series databases rarely fall over because of how many points you write. They fall over because of how many distinct series those points create. A database comfortable at a hundred thousand series starts taking seconds to answer queries that took milliseconds.</p>
              <p>InfluxDB v1 was built for lower-cardinality workloads, and it is very good at them. Nothing about a real fleet stays low-cardinality. The exits are dropping the tags you needed, downsampling data you will want next quarter, or a tier where replication stops being optional.</p>
              <p><a href="/stop-watching-metrics-explode-high-cardinality-without-rewrite/">High cardinality without the rewrite</a> · <a href="/hyperbytedb/">The database, in detail</a></p>
            </div>
          </div>
          <aside class="panel">
            <h3>Where the other 98% goes</h3>
            <p>The storage engine on its own inserts about 99 million rows a second. Put a network, a parser, a series index, and a durable write-ahead log in front of it and you get 1.5 million. Both numbers are true. Only one of them belongs in a capacity plan.</p>
            <p class="more"><a href="/from-99-million-to-1-9-million-what-an-ingest-benchmark-doesnt-tell-you/">Read the benchmark notes</a></p>
          </aside>
        </div>
      </section>
      <section id="database">
        <div class="wrap split">
          <div>
            <p class="kicker">HyperbyteDB</p>
            <h2>Change one URL.</h2>
            <div class="prose">
              <p>Monitoring, IoT, observability, and analytics stacks already speak InfluxDB v1 line protocol and InfluxQL. HyperbyteDB is a full drop-in: same <span class="mono">/write</span> and <span class="mono">/query</span>, same clients, written in Rust with columnar MergeTree storage and a RocksDB write-ahead log.</p>
              <p><a href="/influxdb-v1-compatibility-drop-in/">What the compatibility actually covers</a> · <a href="/influxdb-v1-migration-checklist-clients-url-change/">Client-by-client migration checklist</a></p>
            </div>
            <ul class="checklist">
              <li><span class="mark" aria-hidden="true">+</span><span>Same endpoints, same InfluxQL: aggregates, derivatives, moving averages, <span class="mono">GROUP BY time()</span>, subqueries, regex measurements.</span></li>
              <li><span class="mark" aria-hidden="true">+</span><span>Same agents. <a href="/telegraf-grafana-alerts-stack-database-that-doesnt-buckle/">Point Telegraf and Grafana at HyperbyteDB</a> and keep the dashboards.</span></li>
              <li><span class="mark" aria-hidden="true">+</span><span>Continuous queries and master-master replication ship in the open-source binary. <a href="/why-influxdb-enterprise-pricing-hits-a-wall/">Why that matters on price</a>.</span></li>
              <li><span class="mark" aria-hidden="true">+</span><span>Writes land in the write-ahead log before acknowledgement, then flush to columnar storage.</span></li>
            </ul>
          </div>
          <div>
            <pre><span class="dim"># self-host</span>
docker pull ghcr.io/hyperbyte-cloud/hyperbytedb:latest

docker run -d \\
  --name hyperbytedb \\
  -p 8086:8086 \\
  ghcr.io/hyperbyte-cloud/hyperbytedb:latest

<span class="dim"># the migration</span>
<span class="dim">#   http://influxdb:8086</span>
    http://hyperbytedb:8086</pre>
          </div>
        </div>
      </section>
      <section id="platform">
        <div class="wrap">
          <p class="kicker">Two ways to run it</p>
          <h2>The database, or the platform that runs it.</h2>
          <p class="prose">Self-hosting HyperbyteDB is free, with no feature gates. <a href="/cloud/">Hyperbyte Cloud</a> is the same core, operated for you. <a href="/pricing/">Pricing</a> for Cloud is published when it is real, not quoted per deal.</p>
          <div class="products">
            <article class="product">
              <p class="tag">Open source</p>
              <h3><a href="/hyperbytedb/">HyperbyteDB</a></h3>
              <p>InfluxDB v1 line protocol and HTTP API, TimeseriesQL, per-measurement MergeTree storage, Raft schema consensus, and active-active clustering where every node accepts writes.</p>
              <ul>
                <li><a href="/oss/">Open source at Hyperbyte</a></li>
                <li><a href="/influxdb-v1-kubernetes-operator-swap-keep-urls/">Swap the Kubernetes operator, keep the URLs</a></li>
                <li><a href="{GITHUB}" rel="noopener">Source and releases on GitHub</a></li>
              </ul>
            </article>
            <article class="product">
              <p class="tag">Managed</p>
              <h3><a href="/cloud/">Hyperbyte Cloud</a></h3>
              <p>Point Telegraf at a URL. The platform handles tuning, replication, upgrades, backups, and capacity. Early access is open to a small number of design partners.</p>
              <ul>
                <li><a href="/pricing/">Self-hosted is free. Cloud price is still being published.</a></li>
                <li><a href="/connect-with-us/">Talk to an engineer</a></li>
                <li>Hostnames on <span class="mono">db.hyperbyte.cloud</span></li>
              </ul>
            </article>
          </div>
          <div class="table-scroll">
            <table>
              <caption>Self-hosted or managed. <a href="/pricing/">Full pricing notes</a>.</caption>
              <thead><tr><th scope="col"> </th><th scope="col">Self-hosted</th><th scope="col">Cloud</th></tr></thead>
              <tbody>
                <tr><th scope="row">Licence</th><td><a href="/oss/">Open source, on GitHub</a></td><td><a href="/cloud/">Early access</a></td></tr>
                <tr><th scope="row">InfluxDB v1 compatibility</th><td>Full</td><td>Full</td></tr>
                <tr><th scope="row">Replication and HA</th><td>Yours to run</td><td>Managed</td></tr>
                <tr><th scope="row">Upgrades, backups, restore tests</th><td>Yours to run</td><td>Managed</td></tr>
                <tr><th scope="row">Support</th><td>Community</td><td><a href="/connect-with-us/">Direct</a></td></tr>
                <tr><th scope="row">Price</th><td>Free</td><td>Announced at general availability</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
      <section id="solutions">
        <div class="wrap">
          <p class="kicker">Workloads</p>
          <h2>Built for telemetry that is spread out.</h2>
          <p class="prose"><a href="/solutions/">Solutions</a> for device fleets, distributed systems, and high tag cardinality. Same InfluxDB v1 endpoints, so the stack you already run keeps working.</p>
          <p class="post-meta">{cases}</p>
        </div>
      </section>
      <section id="how">
        <div class="wrap">
          <p class="kicker">How it works</p>
          <h2>Three moves. No rewrite.</h2>
          <ol class="steps">
            <li><span>01</span><h3>Run the binary</h3><p>Pull <a href="{GITHUB}" rel="noopener">ghcr.io/hyperbyte-cloud/hyperbytedb</a> and listen on port 8086. Or <a href="/cloud/">hand the node to Cloud</a>.</p></li>
            <li><span>02</span><h3>Point the clients</h3><p>Telegraf, Grafana, and InfluxQL stay. Change the URL. The <a href="/influxdb-v1-migration-checklist-clients-url-change/">checklist</a> says which clients are only that.</p></li>
            <li><span>03</span><h3>Tag what you need</h3><p>Cardinality becomes capacity, not a ceiling. <a href="/stop-watching-metrics-explode-high-cardinality-without-rewrite/">Read why the series index stops being the wall</a>.</p></li>
          </ol>
        </div>
      </section>
      <section id="shift">
        <div class="wrap">
          <p class="kicker">The shift</p>
          <h2>Same wire. Different ceiling.</h2>
          <div class="split compare">
            <article>
              <p class="kicker">Before</p>
              <h3>InfluxDB v1 under tag pressure</h3>
              <ul>
                <li>Queries slip from milliseconds to seconds as series multiply</li>
                <li>The exits are fewer tags, downsampling, or an enterprise tier</li>
                <li>Replication and continuous queries sit behind a licence</li>
              </ul>
            </article>
            <article class="after">
              <p class="kicker">After</p>
              <h3>HyperbyteDB on the same stack</h3>
              <ul>
                <li>1.5M points/sec sustained, p95 under 250ms, on one EPYC node</li>
                <li>Line protocol, InfluxQL, Telegraf, and Grafana stay</li>
                <li>Master-master replication ships in the open-source binary</li>
              </ul>
            </article>
          </div>
        </div>
      </section>
      <section id="faq">
        <div class="wrap">
          <p class="kicker">Questions</p>
          <h2>Asked before the cutover.</h2>
          <div class="faq">
            <details>
              <summary>Is HyperbyteDB a drop-in for InfluxDB v1?</summary>
              <p>It speaks line protocol and InfluxQL on the same <span class="mono">/write</span> and <span class="mono">/query</span> endpoints. Coverage, and the differences, are written up in <a href="/influxdb-v1-compatibility-drop-in/">what works and what does not</a>.</p>
            </details>
            <details>
              <summary>Is self-hosting free?</summary>
              <p>Yes. No feature gates. Replication, retention, and continuous queries are in the binary. <a href="/pricing/">Cloud pricing</a> is published when it is real, not quoted per deal.</p>
            </details>
            <details>
              <summary>What ingest number should a capacity plan use?</summary>
              <p>1.5 million points a second sustained, p95 under 250ms, on an AMD EPYC 7413 with 251GB RAM. Peak on that box was about 1.9 million. The engine alone does about 99 million rows a second with nothing in front of it. <a href="/from-99-million-to-1-9-million-what-an-ingest-benchmark-doesnt-tell-you/">Both numbers, and why only one belongs in a plan</a>.</p>
            </details>
            <details>
              <summary>Does sharding exist today?</summary>
              <p>HyperbyteDB runs as a single node today. Sharding, which turns cardinality into a capacity decision, lands this year. The same kind of measurement published for ingest will be published for the cluster.</p>
            </details>
            <details>
              <summary>What is still ahead for Cloud?</summary>
              <p>Regions, a published uptime SLA, formal compliance certification, and bring-your-own-cloud. Early access exists so design partners get a say in which lands first. <a href="/connect-with-us/">Write to an engineer</a>.</p>
            </details>
          </div>
        </div>
      </section>
      <section id="notes">
        <div class="wrap">
          <p class="kicker">From the notes</p>
          <h2>The measurements, and the migration.</h2>
          <div class="related">{notes}</div>
          <p class="more"><a href="/tag/blog/">All 11 posts</a></p>
        </div>
      </section>
      {cta_html()}
    </main>'''
    page = {
        "path": "/",
        "title": "HyperbyteDB — InfluxDB v1-compatible time-series database",
        "description": "Drop-in replacement for InfluxDB v1: same wire protocol, same InfluxQL, a Rust core built for high cardinality. Change one URL. Managed or self-hosted.",
        "jsonld": {"@context": "https://schema.org", "@graph": graph},
        "nav": "/",
    }
    write("index.html", page_shell(page, body))


def redirect(rel, target):
    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<link rel="canonical" href="{ORIGIN}{target}">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0;url={target}">
<title>Redirect</title>
</head>
<body><p><a href="{target}">Continue</a></p></body>
</html>
'''
    write(rel, page)


def rss(posts):
    items = []
    for post in posts:
        items.append(f'''<item>
      <title>{esc(post["title"])}</title>
      <link>{abs_url(post["path"])}</link>
      <guid>{abs_url(post["path"])}</guid>
      <pubDate>{esc(post["published"])}</pubDate>
      <description>{esc(post["description"])}</description>
    </item>''')
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Hyperbyte Cloud</title>
    <link>{ORIGIN}/tag/blog/</link>
    <description>Notes on HyperbyteDB, InfluxDB v1 compatibility, and time-series engineering.</description>
    {"".join(items)}
  </channel>
</rss>
'''
    write("rss.xml", xml)


def sitemap(urls):
    body = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, lastmod in urls:
        last = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        body.append(f"<url><loc>{abs_url(path)}</loc>{last}</url>")
    body.append("</urlset>")
    write("sitemap.xml", "\n".join(body) + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n")


def main():
    MEDIA.mkdir(parents=True, exist_ok=True)
    posts = [load_document(path, "post") for path in POST_URLS]
    posts.sort(key=lambda doc: doc["published"], reverse=True)
    pages = [load_document(path, "page") for path in PAGE_URLS]
    tag_map = {}
    for post in posts:
        for path, label in post["tags"]:
            tag_map.setdefault(path, {"label": label, "posts": []})["posts"].append(post)
    indexable = {path for path, info in tag_map.items() if len(info["posts"]) >= 2}
    home_page(posts)
    for doc in posts + pages:
        render_article(doc, posts, indexable)
    render_listing(
        "/tag/blog/",
        "Blog",
        "Notes on HyperbyteDB ingest, InfluxDB v1 compatibility, cardinality, and moving a Telegraf and Grafana stack without a rewrite.",
        "Eleven posts on the measurements, the migration, and what ships in the open-source binary.",
        posts,
        "Blog",
    )
    render_listing(
        "/author/austin/",
        "Austin",
        "Articles by Austin at Hyperbyte Cloud, on HyperbyteDB ingest, InfluxDB v1 compatibility, and time-series engineering.",
        "Engineering notes from Hyperbyte Cloud.",
        posts,
        "ProfilePage",
    )
    for path, info in sorted(tag_map.items()):
        if path == "/tag/blog/":
            continue
        label = info["label"]
        robots = "index, follow" if path in indexable else "noindex, follow"
        render_listing(
            path,
            label[:1].upper() + label[1:],
            f"{label.capitalize()} notes from Hyperbyte Cloud: HyperbyteDB, InfluxDB v1, and time-series engineering.",
            f"{len(info['posts'])} post{'s' if len(info['posts']) != 1 else ''} tagged {label}.",
            info["posts"],
            "CollectionPage",
            robots=robots,
        )
    redirect("home/index.html", "/")
    redirect("blog/index.html", "/tag/blog/")
    redirect("blog.html", "/tag/blog/")
    urls = { "/": "" }
    for doc in posts + pages:
        urls[doc["path"]] = doc["modified"] or doc["published"]
    urls["/tag/blog/"] = posts[0]["published"]
    urls["/author/austin/"] = posts[0]["published"]
    for path in sorted(indexable):
        if path == "/tag/blog/":
            continue
        dates = [p["published"] for p in tag_map[path]["posts"]]
        urls[path] = max(dates)
    sitemap(urls.items())
    rss(posts)
    print("pages", len(posts) + len(pages) + 1, "tags", len(tag_map), "images", len(image_cache))


if __name__ == "__main__":
    main()
