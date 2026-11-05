#!/usr/bin/env python3
"""Pre-publish checks for the HR Digest page (index.html).

Run from the repo root before every push:

    python3 tools/check.py            # dates, expiry, limits, sources, rules
    python3 tools/check.py --links    # also fetch every link (needs network)

Any FAIL means the page breaks a rule in CLAUDE.md: fix it and re-run, and do
not publish until it passes. WARN lines need a look but don't block.
Standard library only.
"""
import argparse
import datetime as dt
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

RETIRED_CHECKLIST_IDS = {"holiday-audit", "family-leave"}
PAGE_WORD_LIMIT = 2500
RAG_LIMITS = {"What it is:": 20, "Why it matters:": 25, "Do now:": 35, "Then later:": 15}
MAX = {"rag": 8, "news": 5, "cases": 8, "checklist": 10, "tags": 6}
WORD = re.compile(r"\S*[0-9A-Za-z£$%]\S*")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


# ---------------------------------------------------------------- tiny DOM
class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs), parent, []

    @property
    def classes(self):
        return set((self.attrs.get("class") or "").split())

    def text(self, skip=lambda n: False):
        out = []
        for c in self.children:
            if isinstance(c, str):
                out.append(c)
            elif not skip(c):
                out.append(c.text(skip))
        return re.sub(r"\s+", " ", "".join(out)).strip()

    def all(self, pred):
        for c in self.children:
            if isinstance(c, Node):
                if pred(c):
                    yield c
                yield from c.all(pred)

    def first(self, pred):
        return next(self.all(pred), None)

    def kids(self, tag):
        return [c for c in self.children if isinstance(c, Node) and c.tag == tag]


class Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.cur = node.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def has_class(name):
    return lambda n: name in n.classes


def words(s):
    return len(WORD.findall(s))


def is_src(n):
    return n.tag == "a" and "src" in n.classes


# ---------------------------------------------------------------- checks
class Report:
    def __init__(self):
        self.fails, self.warns = [], []

    def fail(self, msg):
        self.fails.append(msg)

    def warn(self, msg):
        self.warns.append(msg)


def parse_date(value, where, rep):
    if not value or not DATE.match(value):
        rep.fail(f"{where}: missing or malformed date {value!r} (want YYYY-MM-DD)")
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        rep.fail(f"{where}: invalid date {value!r}")
        return None


def check_off(li, where, today, rep):
    off = parse_date(li.attrs.get("data-off"), f"{where} data-off", rep)
    if off and off <= today:
        rep.fail(f"{where}: data-off {off} has passed — delete it (assumed done)")


def today_london():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("Europe/London")).date()
    except Exception:
        return dt.datetime.now(dt.timezone.utc).date()


def run(html, today, repo, rep):
    b = Builder()
    b.feed(html)
    root = b.root

    # ---- dates
    wrap = root.first(lambda n: "data-compiled" in n.attrs)
    compiled = parse_date(wrap.attrs.get("data-compiled") if wrap else None, "data-compiled", rep)
    if compiled and compiled != today:
        rep.fail(f"data-compiled is {compiled}, today (Europe/London) is {today}")
    long_date = f"{today:%A} {today.day} {today:%B} {today.year}"
    block = root.first(has_class("dateblock"))
    if not block or (block.first(lambda n: n.tag == "strong") or Node("x", [], None)).text() != long_date:
        rep.fail(f"masthead date should read '{long_date}'")
    if not block or f"Brief compiled {today.day} {today:%b} {today.year}" not in block.text():
        rep.fail(f"masthead should say 'Brief compiled {today.day} {today:%b} {today.year}'")
    footer = root.first(lambda n: n.tag == "footer")
    if not footer or f"Compiled {today.day} {today:%B} {today.year}" not in footer.text():
        rep.fail(f"footer should say 'Compiled {today.day} {today:%B} {today.year}'")

    item_links = {}

    # ---- priority list
    rag = root.first(has_class("rag"))
    rag_items = rag.kids("li") if rag else []
    if not rag_items:
        rep.fail("priority list (.rag) is missing or empty")
    if len(rag_items) > MAX["rag"]:
        rep.fail(f"priority list has {len(rag_items)} entries (max {MAX['rag']}); move the rest to the overflow line")
    band = {"is-red": 0, "is-amber": 1, "is-green": 2}
    last_band = -1
    for li in rag_items:
        name = (li.first(lambda n: n.tag == "h3") or Node("x", [], None)).text() or "?"
        where = f"priority '{name[:50]}'"
        level = [band[c] for c in li.classes if c in band]
        if len(level) != 1:
            rep.fail(f"{where}: needs exactly one of is-red / is-amber / is-green")
        elif level[0] < last_band:
            rep.fail(f"{where}: out of order (Red → Amber → Green)")
        else:
            last_band = level[0]
        if not li.attrs.get("data-id"):
            rep.fail(f"{where}: missing data-id")
        check_off(li, where, today, rep)
        link = li.first(is_src)
        if not link or not link.attrs.get("href"):
            rep.fail(f"{where}: no Source ↗ link (class=\"src\") to the page that confirms it")
        else:
            item_links.setdefault(link.attrs["href"], where)
        seen = set()
        for p in li.all(lambda n: n.tag == "p"):
            label = p.first(lambda n: n.tag == "b")
            lab = label.text() if label else ""
            if lab in RAG_LIMITS:
                seen.add(lab)
                n = words(p.text(skip=lambda c: c is label or is_src(c)))
                if n > RAG_LIMITS[lab]:
                    rep.fail(f"{where}: '{lab}' is {n} words (max {RAG_LIMITS[lab]})")
                if lab == "Do now:" and re.search(r"seek (legal )?advice|review your position", p.text(), re.I):
                    rep.warn(f"{where}: 'Do now' leans on 'seek advice'/'review your position' — give a concrete step")
        for lab in RAG_LIMITS:
            if lab not in seen:
                rep.fail(f"{where}: missing '{lab}' line")

    # ---- news
    news = root.first(has_class("news"))
    news_items = news.kids("li") if news else []
    if len(news_items) > MAX["news"]:
        rep.fail(f"news has {len(news_items)} items (max {MAX['news']})")
    for li in news_items:
        h3 = li.first(lambda n: n.tag == "h3")
        title = h3.text() if h3 else "?"
        where = f"news '{title[:50]}'"
        if re.search(r"no (major )?(new )?developments", title, re.I):
            rep.fail(f"{where}: quiet-week filler item — say it in the card's sub line instead, keep real items")
        check_off(li, where, today, rep)
        p = li.first(lambda n: n.tag == "p")
        if p:
            body = p.text(skip=is_src)
            if words(body) > 30:
                rep.fail(f"{where}: sentence is {words(body)} words (max 30)")
            if re.search(r"[.!?]\s+[A-Z]", body):
                rep.warn(f"{where}: looks like more than one sentence")
            link = p.first(is_src)
        else:
            link = None
            rep.fail(f"{where}: missing sentence")
        if not link or not link.attrs.get("href"):
            rep.fail(f"{where}: no Source ↗ link to the page that confirms it")
        else:
            item_links.setdefault(link.attrs["href"], where)
        act = li.first(has_class("act"))
        if not act or not act.text().startswith("Do:"):
            rep.fail(f"{where}: missing bold 'Do:' line")
        elif words(act.text()[3:]) > 20:
            rep.fail(f"{where}: 'Do:' line is {words(act.text()[3:])} words (max 20)")

    # ---- timeline stops
    stops = root.first(lambda n: n.attrs.get("id") == "stops")
    for li in (stops.kids("li") if stops else []):
        when = li.first(has_class("when"))
        label = when.text() if when else "?"
        where = f"timeline stop '{label}'"
        bad = li.classes - {"is-live", "is-soon"}
        if bad:
            rep.fail(f"{where}: unexpected class {sorted(bad)}")
        tags = li.first(has_class("tags"))
        tag_items = tags.kids("li") if tags else []
        if len(tag_items) > MAX["tags"]:
            rep.fail(f"{where}: {len(tag_items)} tags (max {MAX['tags']})")
        for t in tag_items:
            if words(t.text()) > 7:
                rep.fail(f"{where}: tag '{t.text()}' is over 7 words")
        try:
            day = dt.datetime.strptime(label, "%d %b %Y").date()
        except ValueError:
            day = None
        if day and "is-live" in li.classes and day > today:
            rep.fail(f"{where}: marked in force but the date is still ahead")
        if day and "is-live" not in li.classes and day <= today:
            rep.fail(f"{where}: date has passed — flip it to is-live / 'In force'")

    # ---- deadlines and countdowns
    for n in root.all(lambda n: "data-due" in n.attrs):
        due = parse_date(n.attrs.get("data-due"), "data-due", rep)
        inside_dl = any("dl" in (a.classes if isinstance(a, Node) else set()) for a in ancestors(n))
        if due and due < today and inside_dl:
            rep.fail(f"deadline {due} has passed — drop it from Dates to diary")
        elif due and due < today:
            rep.warn(f"countdown {due} has passed — update the chip or stop")
    for n in root.all(lambda n: "data-stale-after" in n.attrs):
        until = parse_date(n.attrs.get("data-stale-after"), "data-stale-after", rep)
        if until and until <= today:
            rep.fail(f"content marked data-stale-after={until} is now out of date — refresh it and move the date on")

    # ---- case law
    cases = root.first(has_class("cases"))
    case_items = cases.kids("li") if cases else []
    if len(case_items) > MAX["cases"]:
        rep.fail(f"case law has {len(case_items)} entries (max {MAX['cases']})")
    for li in case_items:
        name = li.first(has_class("cn"))
        where = f"case '{(name.text() if name else '?')[:50]}'"
        check_off(li, where, today, rep)
        if not name or name.tag != "a" or not name.attrs.get("href"):
            rep.fail(f"{where}: case name must link to the judgment (or the page reporting it)")
        else:
            item_links.setdefault(name.attrs["href"], where)
        paras = li.kids("p")
        take = next((p for p in paras if "means" not in p.classes), None)
        means = next((p for p in paras if "means" in p.classes), None)
        if not take:
            rep.fail(f"{where}: missing takeaway line")
        elif words(take.text()) > 25:
            rep.fail(f"{where}: takeaway is {words(take.text())} words (max 25)")
        if not means or not means.text().startswith("What it could change:"):
            rep.fail(f"{where}: missing 'What it could change:' line")
        elif words(means.text()) > 30 + 4:
            rep.fail(f"{where}: 'What it could change' is {words(means.text()) - 4} words (max 30)")

    # ---- checklist
    checklist = root.first(lambda n: n.attrs.get("id") == "checklist")
    check_items = checklist.kids("li") if checklist else []
    if len(check_items) > MAX["checklist"]:
        rep.fail(f"checklist has {len(check_items)} items (max {MAX['checklist']})")
    seen_ids = set()
    for li in check_items:
        box = li.first(lambda n: n.tag == "input")
        cid = box.attrs.get("data-id") if box else None
        where = f"checklist '{cid}'"
        if not cid:
            rep.fail("checklist item without a checkbox data-id")
        elif cid in RETIRED_CHECKLIST_IDS:
            rep.fail(f"{where}: reuses a retired id")
        elif cid in seen_ids:
            rep.fail(f"{where}: duplicate id")
        seen_ids.add(cid)
        check_off(li, where, today, rep)
        why = li.first(has_class("why"))
        if why and words(why.text()) > 10:
            rep.fail(f"{where}: reason line is {words(why.text())} words (max 10)")

    # ---- sources
    details = root.first(has_class("sources"))
    footer_links = [a.attrs.get("href", "") for a in details.all(lambda n: n.tag == "a")] if details else []
    if not footer_links:
        rep.fail("footer sources list is missing or empty")
    for href, where in item_links.items():
        if href not in footer_links:
            rep.fail(f"{where}: its source isn't in the footer list ({href})")
    dupes = {h for h in footer_links if footer_links.count(h) > 1}
    for h in sorted(dupes):
        rep.warn(f"footer lists the same source twice: {h}")
    for a in root.all(lambda n: n.tag == "a" and "href" in n.attrs):
        if a.attrs["href"].startswith("http:"):
            rep.fail(f"insecure link: {a.attrs['href']}")

    # ---- page-wide rules
    no_sources = re.sub(r'(?s)<details class="sources">.*?</details>|<p class="disclaimer">.*?</p>', " ", html)
    no_code = re.sub(r"(?is)<(style|script)[^>]*>.*?</\1>", " ", no_sources)
    total = words(re.sub(r"(?s)<[^>]+>", " ", no_code))
    if total >= PAGE_WORD_LIMIT:
        rep.fail(f"page is {total} words excluding sources (limit {PAGE_WORD_LIMIT})")
    if re.search(r"<script[^>]+src=|<link[^>]+stylesheet|@import|url\(\s*['\"]?https?:|<(img|iframe)[^>]+src=['\"]?https?:", html, re.I):
        rep.fail("page loads an external resource — keep everything inline")
    if re.search(r"noindex", html, re.I):
        rep.fail("page contains 'noindex' — it must stay search-indexable")
    notice = root.first(has_class("notice"))
    if not notice or "AI" not in notice.text() or "Northern Ireland" not in notice.text():
        rep.fail("masthead notice (compiled by AI, check the source, Great Britain only) is missing — put it back")
    if block and "Great Britain" not in block.text():
        rep.fail("masthead date block should say 'Great Britain' — Northern Ireland law differs")
    disclaimer = root.first(has_class("disclaimer"))
    if not disclaimer or "not legal advice" not in disclaimer.text():
        rep.fail("footer disclaimer is missing — put it back")
    credit = root.first(has_class("credit"))
    if not credit or "made by" not in credit.text() or not credit.first(lambda n: n.tag == "a" and n.attrs.get("href", "").rstrip("/") == "https://hrlar.co.uk"):
        rep.fail("masthead credit '— made by Lara Pegg' linking to https://hrlar.co.uk is missing")
    cname = repo / "CNAME"
    if not cname.exists() or cname.read_text().strip() != "digest.hrlar.co.uk":
        rep.fail("CNAME file is missing or doesn't say digest.hrlar.co.uk — the live site depends on it")
    config = repo / "_config.yml"
    if not config.exists() or "CLAUDE.md" not in config.read_text():
        rep.warn("_config.yml is missing or no longer excludes CLAUDE.md — the rules file will be public on the site")

    return [a.attrs["href"] for a in root.all(lambda n: n.tag == "a" and n.attrs.get("href", "").startswith("http"))], total


def ancestors(n):
    while n.parent is not None:
        n = n.parent
        yield n


def probe(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (HR Digest link check)"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return url, r.status, None
    except urllib.error.HTTPError as e:
        return url, e.code, None
    except Exception as e:
        return url, None, type(e).__name__


def check_links(urls, rep):
    from concurrent.futures import ThreadPoolExecutor

    urls = sorted(set(urls))
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(probe, urls))
    if urls and all(code is None for _, code, _ in results):
        rep.warn("no link could be reached — the network looks blocked; open any new link with WebFetch instead")
        return
    for url, code, err in results:
        if code is None:
            rep.warn(f"couldn't reach {url} ({err}) — confirm it with WebFetch")
        elif code in (401, 403, 429):
            rep.warn(f"{url} answered {code} (bot-blocked?) — confirm it opens with WebFetch")
        elif code >= 400:
            rep.fail(f"dead link ({code}): {url}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", nargs="?", default="index.html")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for testing")
    ap.add_argument("--links", action="store_true", help="also fetch every link")
    args = ap.parse_args()
    path = Path(args.page)
    today = dt.date.fromisoformat(args.today) if args.today else today_london()
    rep = Report()
    urls, total = run(path.read_text(encoding="utf-8"), today, path.resolve().parent, rep)
    if args.links:
        check_links(urls, rep)
    for w in rep.warns:
        print("WARN ", w)
    for f in rep.fails:
        print("FAIL ", f)
    print(f"{len(rep.fails)} fail, {len(rep.warns)} warn · {total} words · checked as of {today}")
    sys.exit(1 if rep.fails else 0)


if __name__ == "__main__":
    main()
