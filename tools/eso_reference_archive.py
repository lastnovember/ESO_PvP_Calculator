#!/usr/bin/env python3
"""
ESO reference archive: official ZOS content + UESP game data.

One script, three sources, one menu. Companion to eso_patch_archive.py
(which handles the patch note change log and is unchanged).

  zos     Developer Deep Dives, official guides, New Player Guide, and
          combat/PvP/class/CP news posts. Needs a real browser because
          the site is age gated.

  uesp    The mechanics reference, pulled through the MediaWiki API
          rather than by scraping: sets (all 10 category pages), skills,
          champion points, traits, mundus, buffs, armor, weapons,
          classes, status effects, consumables, PvP rules. Returns clean
          wikitext plus rendered HTML, so no browser and no bot wall.

  esolog  UESP's game-client data browser, including the skill
          coefficient table. That table is the damage formula input ZOS
          has never published. It blocks plain HTTP, so it rides along
          in the same browser session as the zos source.

Output, per the brief: structured data first, PDFs rendered from it.

  data/     every wiki table as CSV, plus reference.sqlite and JSON
  pdf/      one readable PDF per page
  raw/      untouched source, so re-parsing never re-downloads

Usage
-----
  python eso_reference_archive.py             (menu)
  python eso_reference_archive.py all
  python eso_reference_archive.py harvest --source uesp
  python eso_reference_archive.py data
  python eso_reference_archive.py render

Setup
-----
  pip install playwright beautifulsoup4 pypdf lxml
  playwright install chromium

UESP text is CC BY-SA. This is a personal reference copy. Attribute UESP
if you republish any of it.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html as _html
import json
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# ----------------------------------------------------------------------
# configuration
# ----------------------------------------------------------------------

UA = ("ESOReferenceArchive/1.0 (personal research archive; "
      "contact via github.com/uesp/uesp-esolog issues)")

WIKI_API = "https://en.uesp.net/w/api.php"
WIKI_DELAY = 1.2          # seconds between API calls, deliberately polite

ZOS_BASE = "https://www.elderscrollsonline.com"
ZOS_SEEDS = ["/en-us/news", "/en-us/guides"]
ZOS_DELAY = 2.5
MAX_INDEX_PAGES = 40

ESOLOG_PAGES = {
    "skill_coefficients": "https://esolog.uesp.net/viewSkillCoef.php",
}

NAV_TIMEOUT = 60_000

# UESP seed pages, weighted to PvP per the brief: combat systems and
# character mechanics, not dungeon or trial encounter scripting.
UESP_SEEDS = [
    # core combat and stats. Combat covers blocking, dodging, breaking free
    # and crowd control immunity, which have no pages of their own.
    "Online:Combat", "Online:Attributes", "Online:Health",
    "Online:Magicka", "Online:Stamina", "Online:Buffs", "Online:Leveling",
    "Online:Off Balance", "Online:Penetration", "Online:Resistance",
    "Online:Critical Damage", "Online:Block", "Online:Dodge",
    "Online:Roll Dodge", "Online:Sneak", "Online:Sprint", "Online:Stun",
    "Online:Immobilize", "Online:Snare", "Online:Status Effects",
    "Online:Ultimate", "Online:Synergy",
    # damage types carry the status effect each one applies
    "Online:Physical Damage", "Online:Magic Damage", "Online:Flame Damage",
    "Online:Frost Damage", "Online:Shock Damage", "Online:Poison Damage",
    "Online:Disease Damage", "Online:Bleed Damage", "Online:Oblivion Damage",
    # character build
    "Online:Champion", "Online:Skills", "Online:Classes", "Online:Races",
    "Online:Mundus Stones", "Online:Traits", "Online:Armor", "Online:Weapons",
    "Online:Werewolf", "Online:Vampire",
    # gear
    "Online:Sets",
    # consumables and enchants
    "Online:Enchanting", "Online:Provisioning", "Online:Potions",
    "Online:Poisons", "Online:Alchemy", "Online:Food", "Online:Drink",
    # pvp. Battle Spirit has no page of its own, it lives in Campaigns
    # along with battle leveling.
    "Online:Alliance War", "Online:Campaigns", "Online:Cyrodiil",
    "Online:Imperial City", "Online:Battlegrounds", "Online:Siege Weapons",
]

# Whole families are enumerated from their category rather than guessed at.
# Every set and every ability, morph and passive has its own page.
UESP_FAMILIES = {
    "sets": "Category:Online-Sets",
    "skills": "Category:Online-Skills",
}

# Hub pages whose outgoing Online: links are worth following one level.
UESP_EXPAND = {
    "Online:Sets": re.compile(r"Sets$", re.I),
    "Online:Skills": re.compile(r"Skills|Skill Line", re.I),
    "Online:Champion": re.compile(r"Champion", re.I),
    "Online:Classes": re.compile(r"^Online:(Dragonknight|Nightblade|Sorcerer|"
                                 r"Templar|Warden|Necromancer|Arcanist)", re.I),
}

# Anything matched here is dropped during expansion: PvE encounter content.
UESP_REJECT = re.compile(
    r"Quest|Places|NPC|Creatures|Achievement|Houses|Furnishing|Books|Lore|"
    r"Antiquities|Fishing|Motif|Style|Dungeons:|Trial:|Arena:", re.I)

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR / "ESO Reference Archive"


def log(msg: str) -> None:
    print(f"[{dt.datetime.now():%H:%M:%S}] {msg}", flush=True)


def die(msg: str) -> None:
    print(f"\nERROR: {msg}\n", file=sys.stderr)
    sys.exit(1)


def safe_name(s: str, limit: int = 80) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")
    return s[:limit] or "untitled"


class Paths:
    def __init__(self, out: Path):
        out = Path(out).expanduser().resolve()
        self.out = out
        self.raw = out / "raw"
        self.raw_uesp = out / "raw" / "uesp"
        self.raw_uesp_bulk = out / "raw" / "uesp_bulk"
        self.raw_zos = out / "raw" / "zos"
        self.raw_esolog = out / "raw" / "esolog"
        self.data = out / "data"
        self.tables = out / "data" / "tables"
        self.clean = out / "clean_html"
        self.pdf = out / "pdf"
        self.profile = out / "_browser_profile"
        self.sqlite = out / "data" / "reference.sqlite"
        self.manifest = out / "manifest.csv"
        self.merged = out / "ESO_Reference_Complete.pdf"

    def mkdirs(self) -> None:
        for p in (self.raw_uesp, self.raw_uesp_bulk, self.raw_zos, self.raw_esolog, self.data,
                  self.tables, self.clean, self.pdf, self.profile):
            p.mkdir(parents=True, exist_ok=True)


def _soup(html: str):
    from bs4 import BeautifulSoup  # type: ignore
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html.parser")


# ======================================================================
# source: UESP, via the MediaWiki API
# ======================================================================

def api(params: dict) -> dict:
    params = {**params, "format": "json", "formatversion": "2",
              "maxlag": "5"}
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.loads(r.read().decode("utf-8", "replace"))
            if "error" in data and data["error"].get("code") == "maxlag":
                time.sleep(5 * (attempt + 1))
                continue
            return data
        except Exception as exc:
            if attempt == 3:
                raise
            log(f"  api retry {attempt + 1} ({exc})")
            time.sleep(3 * (attempt + 1))
    return {}


def uesp_expand(seeds: list[str]) -> list[str]:
    """Seeds plus one level of links from the designated hub pages."""
    titles = list(dict.fromkeys(seeds))
    for hub, keep in UESP_EXPAND.items():
        if hub not in titles:
            continue
        time.sleep(WIKI_DELAY)
        data = api({"action": "parse", "page": hub, "prop": "links"})
        links = (data.get("parse") or {}).get("links") or []
        added = 0
        for l in links:
            t = l.get("title", "")
            if l.get("ns") != 144 or l.get("exists") is not True:
                continue
            if not t.startswith("Online:") or UESP_REJECT.search(t):
                continue
            if not keep.search(t):
                continue
            if t not in titles:
                titles.append(t)
                added += 1
        log(f"  {hub}: +{added} linked pages")
    return titles


def category_members(cat: str, cap: int | None = None) -> list[str]:
    """Every Online-namespace page in a category, following continuations."""
    out: list[str] = []
    cont: dict = {}
    while True:
        time.sleep(WIKI_DELAY)
        data = api({"action": "query", "list": "categorymembers",
                    "cmtitle": cat, "cmnamespace": "144", "cmlimit": "500",
                    **cont})
        for m in (data.get("query") or {}).get("categorymembers", []):
            out.append(m["title"])
        if cap and len(out) >= cap:
            return out[:cap]
        cont = data.get("continue") or {}
        if not cont:
            return out


def bulk_wikitext(titles: list[str]) -> dict[str, str]:
    """Wikitext for up to 50 pages in one request.

    This is the whole reason a full pull takes minutes instead of an hour.
    """
    got: dict[str, str] = {}
    data = api({"action": "query", "prop": "revisions", "rvprop": "content",
                "rvslots": "main", "titles": "|".join(titles), "redirects": "1"})
    for p in (data.get("query") or {}).get("pages", []):
        if p.get("missing"):
            continue
        try:
            got[p["title"]] = p["revisions"][0]["slots"]["main"]["content"]
        except (KeyError, IndexError):
            continue
    return got


def harvest_family(paths: Paths, name: str, category: str,
                   refresh: bool, cap: int | None) -> None:
    dest = paths.raw_uesp_bulk / f"{name}.json"
    if dest.exists() and not refresh:
        log(f"{name}: already saved, skipping")
        return
    log(f"Enumerating {category}...")
    titles = category_members(category, cap)
    log(f"  {len(titles)} pages")
    store: dict[str, str] = {}
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        time.sleep(WIKI_DELAY)
        try:
            store.update(bulk_wikitext(chunk))
        except Exception as exc:
            log(f"  batch {i // 50 + 1} failed: {exc}")
        log(f"  {len(store)}/{len(titles)}")
    dest.write_text(json.dumps(store, indent=1), encoding="utf-8")
    log(f"{name}: saved {len(store)} pages")


# --- wikitext template parsing ---------------------------------------
#
# UESP renders sets and abilities from templates, so the template
# parameters ARE the structured data. Parsing them beats scraping the
# rendered tables, and needs no per-page schema.

def parse_templates(wikitext: str) -> list[dict]:
    out = []
    i = 0
    while True:
        start = wikitext.find("{{", i)
        if start == -1:
            return out
        depth, j = 0, start
        while j < len(wikitext):
            if wikitext.startswith("{{", j):
                depth += 1
                j += 2
            elif wikitext.startswith("}}", j):
                depth -= 1
                j += 2
                if depth == 0:
                    break
            else:
                j += 1
        if depth != 0:
            return out
        body = wikitext[start + 2:j - 2]
        parts, buf, d2 = [], [], 0
        for ch in body:
            if ch in "{[":
                d2 += 1
            elif ch in "}]":
                d2 -= 1
            if ch == "|" and d2 <= 0:
                parts.append("".join(buf))
                buf = []
            else:
                buf.append(ch)
        parts.append("".join(buf))
        if parts:
            name = parts[0].strip()
            params = {}
            for n, raw in enumerate(parts[1:], 1):
                if "=" in raw:
                    k, _, v = raw.partition("=")
                    params[k.strip()] = v.strip()
                else:
                    params[str(n)] = raw.strip()
            if name and len(name) < 80:
                out.append({"template": name, "params": params})
        i = j


# UESP writes stat values through helper templates, for example
#   {{ESO Health Link|28-1206 Maximum}}   -> "28-1206 Maximum Health"
#   {{ESO Resistance Link|Physical|||y}}  -> "Physical Resistance"
# Expanding those first keeps the numbers attached to what they measure.
#   {{ESO Spell Damage Link}}             -> "Spell Damage"
# The parameters are optional and often positional and empty, as in
# {{ESO Weapon Damage Link|||y}}, so take the first non-empty one.
ESO_LINK = re.compile(r"\{\{ESO ([A-Za-z /'-]+?) Link((?:\|[^{}]*)?)\}\}")


def _eso_link(m: "re.Match") -> str:
    """Parameters are positional: first is a prefix, second a suffix.

    {{ESO Health Link|Max}}       -> "Max Health"
    {{ESO Health Link||Recovery}} -> "Health Recovery"
    """
    name = m.group(1).strip()
    parts = [p.strip() for p in (m.group(2) or "").split("|")[1:]]
    parts = [p for p in parts if p != "y"]
    prefix = parts[0] if parts else ""
    suffix = parts[1] if len(parts) > 1 else ""
    return " ".join(p for p in (prefix, name, suffix) if p)


# Any other template, innermost first. Its content is usually the value
# being displayed, so keep it rather than deleting it: {{Nowrap|[1587 /
# 1604 / 1621 / 1639]}} is a skill's per-rank scaling, not decoration.
GENERIC_TPL = re.compile(r"\{\{([^{}]*)\}\}")
DROP_TPL = re.compile(r"^(sic|ref|anchor|icon|clear|huh|verify|cite|"
                      r"disambig|notoc)\b", re.I)


def _generic_tpl(m: "re.Match") -> str:
    inner = m.group(1)
    parts = [p.strip() for p in inner.split("|")]
    name = parts[0]
    # Leave ESO stat links for the next pass, which names them properly.
    if re.match(r"^ESO .+ Link$", name, re.I):
        return m.group(0)
    if DROP_TPL.match(name):
        return ""
    values = [p for p in parts[1:] if p and "=" not in p]
    return values[-1] if values else ""

WIKI_CLEAN = [
    (re.compile(r"<ref[^>]*>.*?</ref>", re.S), ""),
    (re.compile(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]"), r"\1"),
    (re.compile(r"'''?"), ""),
    (re.compile(r"<[^>]+>"), " "),
    (re.compile(r"\s+"), " "),
]


def wiki_plain(s: str) -> str:
    # Resolve templates innermost first. Stat links are named on each
    # pass, then whatever wraps them collapses to its value, so a nested
    # {{ESO Health Link|{{Nowrap|[1587 / 1604]}}}} survives intact.
    for _ in range(6):
        new = GENERIC_TPL.sub(_generic_tpl, ESO_LINK.sub(_eso_link, s))
        if new == s:
            break
        s = new
    s = re.sub(r"\{\{|\}\}", " ", s)
    s = _html.unescape(s)
    s = s.replace("\u2013", "-").replace("\u2014", "-").replace("\u00a0", " ")
    for rx, rep in WIKI_CLEAN:
        s = rx.sub(rep, s)
    return re.sub(r"\s+([,.;:])", r"\1", s).strip()


# Set bonuses are not template parameters. They are wikitext lines inside
# an <onlyinclude> block, one per piece count.
SET_BONUS = re.compile(
    r"'''\s*(\d+)\s*items?\s*'''\s*:?\s*(.+?)(?=\n?'''\s*\d+\s*items?\s*'''"
    r"|</onlyinclude>|\n\s*===|\Z)", re.S | re.I)


def parse_set_bonuses(wikitext: str) -> dict[str, str]:
    """{'2': 'Adds 1206 Maximum Health', ...} for one set page."""
    block = wikitext
    m = re.search(r"<onlyinclude>(.*?)</onlyinclude>", wikitext, re.S)
    if m:
        block = m.group(1)
    out = {}
    for count, text in SET_BONUS.findall(block):
        text = re.sub(r"<br\s*/?>", " ", text)
        cleaned = wiki_plain(text)
        if cleaned:
            out[count] = cleaned[:1500]
    return out


def harvest_uesp(paths: Paths, refresh: bool, limit: int | None) -> None:
    paths.mkdirs()
    log("Expanding UESP page list...")
    titles = uesp_expand(UESP_SEEDS)
    log(f"{len(titles)} candidate pages")

    # Drop titles that do not exist, 50 at a time.
    existing: list[str] = []
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        time.sleep(WIKI_DELAY)
        data = api({"action": "query", "titles": "|".join(chunk),
                    "redirects": "1"})
        q = data.get("query") or {}
        for p in q.get("pages", []):
            if not p.get("missing"):
                existing.append(p["title"])
        # A redirect resolves to a different title, which is still a hit.
        for r in q.get("redirects", []) + q.get("normalized", []):
            if r.get("to") in existing and r.get("from") not in existing:
                existing.append(r["from"])
    missing = [t for t in titles if t not in existing]
    if missing:
        log(f"  not on the wiki, skipped: {', '.join(missing[:8])}"
            f"{'...' if len(missing) > 8 else ''}")
    log(f"{len(existing)} pages to fetch")

    (paths.raw / "uesp_pages.json").write_text(
        json.dumps(sorted(existing), indent=2), encoding="utf-8")

    targets = existing[:limit] if limit else existing
    for i, title in enumerate(sorted(targets), 1):
        dest = paths.raw_uesp / f"{safe_name(title)}.json"
        if dest.exists() and not refresh:
            continue
        time.sleep(WIKI_DELAY)
        log(f"[{i}/{len(targets)}] {title}")
        try:
            data = api({"action": "parse", "page": title,
                        "prop": "text|wikitext|displaytitle"})
            parse = data.get("parse")
            if not parse:
                log("      no content returned")
                continue
            dest.write_text(json.dumps({
                "title": title,
                "displaytitle": parse.get("displaytitle", title),
                "html": parse.get("text", ""),
                "wikitext": parse.get("wikitext", ""),
                "url": "https://en.uesp.net/wiki/" + title.replace(" ", "_"),
                "fetched": dt.date.today().isoformat(),
            }, indent=2), encoding="utf-8")
        except Exception as exc:
            log(f"      failed: {exc}")

    for name, cat in UESP_FAMILIES.items():
        try:
            harvest_family(paths, name, cat, refresh,
                           cap=(limit * 10) if limit else None)
        except Exception as exc:
            log(f"{name}: failed ({exc})")
    log("UESP harvest complete.")


# ======================================================================
# source: ZOS official site, and esolog, via a real browser
# ======================================================================

BLOCK_WORDS = ("just a moment", "checking your browser", "verify you are human",
               "performing security verification")


def _blocked(url: str, title: str, body: str) -> str | None:
    hay = f"{url} {title} {body[:600]}".lower()
    if "agegate" in hay or "date of birth" in hay or "age verification" in hay:
        return "age gate"
    if any(m in hay for m in BLOCK_WORDS):
        return "bot check"
    return None


def _get(page, url: str) -> str:
    """Load a page, pausing for a human if the site interrupts.

    The age gate is never answered by the script. Stating your date of
    birth is yours to do, so it waits for you instead.
    """
    page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
    deadline = time.time() + 300
    warned = ""
    while time.time() < deadline:
        try:
            title, here = page.title(), page.url
            body = page.evaluate("document.body ? document.body.innerText : ''")
        except Exception:
            time.sleep(1.5)
            continue
        kind = _blocked(here, title, body)
        if not kind:
            return page.content()
        if kind != warned:
            log("The site wants your date of birth. Type it in the browser "
                "window, it only asks once. Waiting..." if kind == "age gate"
                else "Bot check shown. Click it in the browser window. Waiting...")
            warned = kind
        time.sleep(2.0)
    raise RuntimeError(f"still blocked at {url}")


ANCHOR_JS = """
[...document.querySelectorAll('a[href]')].map(a => ({
  href: a.href,
  text: (a.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 250)
})).filter(x => x.href.startsWith('http'))
"""

NEWS_POST = re.compile(r"/news/post/(\d+)", re.I)
ZOS_ALWAYS = re.compile(r"/newplayerguide/|/guides/", re.I)
RX_DEEP_DIVE = re.compile(r"deep dive", re.I)
RX_COMBAT = re.compile(
    r"\bcombat\b|\bpvp\b|player vs|cyrodiil|imperial city|battleground"
    r"|champion point|\bclass\b|subclass|skill|ability|abilities|balance"
    r"|itemization|item set|\bsets?\b|scribing|armor|weapon|werewolf|vampire"
    r"|update \d+|patch", re.I)


def zos_key(url: str) -> str | None:
    m = NEWS_POST.search(url)
    if m:
        return f"news-{m.group(1)}"
    if ZOS_ALWAYS.search(url):
        slug = re.sub(r"[?#].*$", "", re.sub(r"^https?://[^/]+", "", url)).strip("/")
        return "page-" + safe_name(slug.replace("/", "-"), 70)
    return None


def zos_tier(url: str, text: str) -> str | None:
    if RX_DEEP_DIVE.search(text):
        return "deep-dive"
    if "/newplayerguide/" in url.lower():
        return "new-player-guide"
    if "/guides/" in url.lower():
        return "guide"
    if NEWS_POST.search(url) and RX_COMBAT.search(text):
        return "combat-news"
    return None


def _browser(pw, paths: Paths):
    for channel in ("chrome", "msedge", None):
        try:
            return pw.chromium.launch_persistent_context(
                user_data_dir=str(paths.profile), headless=False,
                channel=channel, viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"])
        except Exception:
            continue
    return None


def harvest_browser(paths: Paths, refresh: bool, include_all: bool,
                    limit: int | None, do_zos: bool = True,
                    do_esolog: bool = True) -> None:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        die("playwright is not installed.\n"
            "  pip install playwright beautifulsoup4 pypdf lxml\n"
            "  playwright install chromium")

    paths.mkdirs()
    with sync_playwright() as pw:
        ctx = _browser(pw, paths)
        if ctx is None:
            die("could not launch a browser. Run: playwright install chromium")
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_default_timeout(NAV_TIMEOUT)

        if do_esolog:
            for name, url in ESOLOG_PAGES.items():
                dest = paths.raw_esolog / f"{name}.html"
                if dest.exists() and not refresh:
                    continue
                log(f"esolog: {name}")
                try:
                    dest.write_text(_get(page, url), encoding="utf-8")
                except Exception as exc:
                    log(f"      failed: {exc}")
                time.sleep(ZOS_DELAY)

        if do_zos:
            found: dict[str, dict] = {}

            def read_index(url: str, tag: str) -> int:
                html = _get(page, url)
                (paths.raw_zos / f"index_{safe_name(tag)}.html").write_text(
                    html, encoding="utf-8")
                new = 0
                for a in (page.evaluate(ANCHOR_JS) or []):
                    key = zos_key(a["href"])
                    if not key or key in found:
                        continue
                    tier = "everything" if include_all else zos_tier(a["href"], a["text"])
                    if not tier:
                        continue
                    found[key] = {"key": key, "url": a["href"].split("#")[0],
                                  "title": a["text"], "tier": tier}
                    new += 1
                return new

            for seed in ZOS_SEEDS:
                log(f"Reading {seed}")
                read_index(f"{ZOS_BASE}{seed}", seed.strip("/").replace("/", "-"))
                empty = 0
                for n in range(2, MAX_INDEX_PAGES + 1):
                    time.sleep(ZOS_DELAY)
                    try:
                        new = read_index(f"{ZOS_BASE}{seed}?page={n}",
                                         f"{seed.strip('/').replace('/', '-')}-p{n}")
                    except Exception as exc:
                        log(f"  page {n} failed ({exc}), stopping this seed")
                        break
                    log(f"  page {n}: {new} new")
                    empty = empty + 1 if new == 0 else 0
                    if empty >= 2:
                        break

            counts: dict[str, int] = {}
            for v in found.values():
                counts[v["tier"]] = counts.get(v["tier"], 0) + 1
            log(f"{len(found)} ZOS pages selected: "
                + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
            (paths.raw / "zos_pages.json").write_text(
                json.dumps(sorted(found.values(), key=lambda d: d["key"]), indent=2),
                encoding="utf-8")

            targets = sorted(found.values(), key=lambda d: d["key"])
            if limit:
                targets = targets[:limit]
            for i, rec in enumerate(targets, 1):
                dest = paths.raw_zos / f"{rec['key']}.html"
                if dest.exists() and not refresh:
                    continue
                time.sleep(ZOS_DELAY)
                log(f"[{i}/{len(targets)}] {rec['title'][:70] or rec['url']}")
                try:
                    dest.write_text(_get(page, rec["url"]), encoding="utf-8")
                    (paths.raw_zos / f"{rec['key']}.json").write_text(
                        json.dumps(rec, indent=2), encoding="utf-8")
                except Exception as exc:
                    log(f"      failed: {exc}")

        ctx.close()
    log("Browser harvest complete.")


# ======================================================================
# structured data extraction
# ======================================================================

def _clean_cell(el) -> str:
    txt = el.get_text(" ", strip=True)
    return re.sub(r"\[\d+\]", "", txt).strip()


NAVBOX_CLASS = re.compile(r"navbox|navigation|vertical-nav|nowraplinks|toc|"
                          r"metadata|ambox|infobox-nav", re.I)


def _is_navbox(tbl) -> bool:
    """The link box at the foot of a wiki page is not data.

    Every sets page carries the same one, which otherwise shows up as a
    dozen identical 310-row tables.
    """
    for el in [tbl] + list(tbl.parents)[:3]:
        cls = " ".join(el.get("class", []) or []) if hasattr(el, "get") else ""
        if cls and NAVBOX_CLASS.search(cls):
            return True
    head = [c.get_text(" ", strip=True).lower()
            for c in tbl.find_all(["th", "td"], limit=3)]
    return head[:3] == ["v", "t", "e"]


def tables_from_html(html: str) -> list[list[list[str]]]:
    soup = _soup(html)
    out = []
    for tbl in soup.find_all("table"):
        if _is_navbox(tbl):
            continue
        rows = []
        for tr in tbl.find_all("tr"):
            cells = tr.find_all(["th", "td"])
            if not cells:
                continue
            rows.append([_clean_cell(c) for c in cells])
        if len(rows) >= 2 and max(len(r) for r in rows) >= 2:
            out.append(rows)
    return out


def build_data(paths: Paths) -> None:
    paths.mkdirs()
    con = sqlite3.connect(paths.sqlite)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS pages")
    cur.execute("DROP TABLE IF EXISTS cells")
    cur.execute("""CREATE TABLE pages (source TEXT, title TEXT, url TEXT,
                   words INTEGER, text TEXT)""")
    cur.execute("""CREATE TABLE cells (source TEXT, page TEXT, table_no INTEGER,
                   row_no INTEGER, col_no INTEGER, header TEXT, value TEXT)""")

    for old in paths.tables.glob("*.csv"):
        old.unlink()

    n_pages = n_tables = 0
    index = []

    for f in sorted(paths.raw_uesp.glob("*.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        title, html = rec["title"], rec.get("html", "")
        text = _soup(html).get_text(" ", strip=True) if html else ""
        cur.execute("INSERT INTO pages VALUES (?,?,?,?,?)",
                    ("uesp", title, rec.get("url", ""), len(text.split()), text))
        n_pages += 1
        for ti, rows in enumerate(tables_from_html(html)):
            header = rows[0]
            name = f"uesp_{safe_name(title, 60)}_t{ti:02d}"
            with (paths.tables / f"{name}.csv").open("w", newline="",
                                                     encoding="utf-8") as fh:
                csv.writer(fh).writerows(rows)
            for ri, row in enumerate(rows[1:], 1):
                for ci, val in enumerate(row):
                    cur.execute("INSERT INTO cells VALUES (?,?,?,?,?,?,?)",
                                ("uesp", title, ti, ri, ci,
                                 header[ci] if ci < len(header) else "", val))
            index.append({"source": "uesp", "page": title, "table": ti,
                          "rows": len(rows) - 1, "cols": len(header),
                          "csv": name + ".csv", "header": header})
            n_tables += 1

    for f in sorted(paths.raw_esolog.glob("*.html")):
        html = f.read_text(encoding="utf-8", errors="replace")
        for ti, rows in enumerate(tables_from_html(html)):
            header = rows[0]
            name = f"esolog_{safe_name(f.stem, 60)}_t{ti:02d}"
            with (paths.tables / f"{name}.csv").open("w", newline="",
                                                     encoding="utf-8") as fh:
                csv.writer(fh).writerows(rows)
            index.append({"source": "esolog", "page": f.stem, "table": ti,
                          "rows": len(rows) - 1, "cols": len(header),
                          "csv": name + ".csv", "header": header})
            n_tables += 1

    # --- families: sets and skills, from template parameters ----------
    cur.execute("DROP TABLE IF EXISTS entities")
    cur.execute("""CREATE TABLE entities (family TEXT, page TEXT,
                   template TEXT, param TEXT, value TEXT)""")
    n_entities = 0

    for f in sorted(paths.raw_uesp_bulk.glob("*.json")):
        family = f.stem
        pages = json.loads(f.read_text(encoding="utf-8"))
        rows_by_page: dict[str, dict] = {}
        tpl_count: dict[str, int] = {}

        for title, wikitext in pages.items():
            # Sets keep their real content outside templates.
            for count, text in parse_set_bonuses(wikitext).items():
                cur.execute("INSERT INTO entities VALUES (?,?,?,?,?)",
                            (family, title, "SetBonus", f"{count} items", text))
                n_entities += 1
                rows_by_page.setdefault(title, {})[f"bonus_{count}"] = text
            for tpl in parse_templates(wikitext):
                name = tpl["template"]
                tpl_count[name] = tpl_count.get(name, 0) + 1
                for k, v in tpl["params"].items():
                    val = wiki_plain(v)[:2000]
                    if not val:
                        continue
                    cur.execute("INSERT INTO entities VALUES (?,?,?,?,?)",
                                (family, title, name, k, val))
                    n_entities += 1
                    rows_by_page.setdefault(title, {}).setdefault(
                        f"{name}.{k}", val)

        if not tpl_count:
            continue
        # Navigation and formatting helpers are not the page's data.
        boring = re.compile(r"^(Trail|Nowrap|ESO|Anchor|Ref|Cite|NewLeft|"
                            r"Huh|Verify|Clear|Icon|Main|See ?also|Item ?Link|"
                            r"Link|Small|Big|Center|Color)$", re.I)
        ranked = sorted(tpl_count.items(), key=lambda kv: -kv[1])
        summary = [n for n, _ in ranked if "summary" in n.lower()]
        real = [n for n, _ in ranked if not boring.match(n)]
        main_tpl = summary[0] if summary else (real[0] if real else ranked[0][0])

        # Columns that a meaningful share of pages actually use.
        col_freq: dict[str, int] = {}
        for row in rows_by_page.values():
            for k in row:
                col_freq[k] = col_freq.get(k, 0) + 1
        cutoff = max(1, len(rows_by_page) // 20)
        cols = [c for c, n in sorted(col_freq.items(), key=lambda kv: -kv[1])
                if n >= cutoff][:60]
        lead = sorted((c for c in col_freq if c.startswith("bonus_")),
                      key=lambda c: int(c.split("_")[1]))
        cols = lead + [c for c in cols if c not in lead]

        out = paths.data / f"{family}.csv"
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["page"] + cols)
            for title in sorted(rows_by_page):
                row = rows_by_page[title]
                w.writerow([title] + [row.get(c, "") for c in cols])
        log(f"  {family}: {len(rows_by_page)} pages, {len(cols)} columns "
            f"(main template: {main_tpl}) -> {out.name}")

    con.commit()
    con.close()
    (paths.data / "tables_index.json").write_text(
        json.dumps(index, indent=2), encoding="utf-8")
    if n_entities:
        log(f"  {n_entities} template values in the entities table")
    log(f"Data built: {n_pages} pages, {n_tables} tables -> {paths.tables}")
    log(f"  queryable database: {paths.sqlite}")


# ======================================================================
# rendering
# ======================================================================

PAGE_CSS = """
@page { size: A4; margin: 16mm 14mm; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10pt;
       line-height: 1.4; color: #1a1a1a; }
h1.archive-title { font-family: Helvetica, Arial, sans-serif; font-size: 16pt;
       margin: 0 0 4px 0; }
.archive-meta { font-family: Helvetica, Arial, sans-serif; font-size: 8pt;
       color: #666; border-bottom: 1px solid #ccc; padding-bottom: 8px;
       margin-bottom: 14px; }
h1,h2,h3,h4 { font-family: Helvetica, Arial, sans-serif; line-height: 1.25;
       page-break-after: avoid; }
h2 { font-size: 12.5pt; margin-top: 15px; }
h3 { font-size: 11pt; margin-top: 12px; }
ul, ol { margin: 5px 0 5px 18px; padding-left: 12px; }
img { max-width: 100%; height: auto; }
table { border-collapse: collapse; max-width: 100%; margin: 8px 0;
        page-break-inside: auto; font-size: 8.5pt; }
td, th { border: 1px solid #bbb; padding: 2px 5px; vertical-align: top; }
th { background: #f0f0f0; }
tr { page-break-inside: avoid; }
a { color: #1a1a1a; text-decoration: none; }
.mw-editsection, .navbox, .toc, .metadata, .noprint { display: none !important; }
"""

ZOS_JUNK = ("script, style, nav, header, footer, aside, form, noscript, iframe, "
            "[class*=nav], [class*=menu], [class*=footer], [class*=header], "
            "[class*=cookie], [class*=social], [class*=share], [class*=promo], "
            "[class*=carousel], [role=navigation], [role=banner]")

ZOS_CANDIDATES = ("article", "main", "[class*=article-body]", "[class*=articleBody]",
                  "[class*=post-body]", "[class*=entry-content]",
                  "[class*=content-body]", "[itemprop=articleBody]",
                  "[class*=rich-text]", "[class*=wysiwyg]", "[class*=content]")


def _best_block(soup):
    best, best_score = None, 0
    for sel in ZOS_CANDIDATES:
        for el in soup.select(sel):
            text = " ".join(p.get_text(" ", strip=True)
                            for p in el.find_all(["p", "li", "h2", "h3"]))
            if len(text) > best_score:
                best, best_score = el, len(text)
    return best, best_score


def _doc(title: str, meta: str, body: str) -> str:
    return (f"<!doctype html><html><head><meta charset=\"utf-8\">"
            f"<title>{title}</title><style>{PAGE_CSS}</style></head><body>"
            f"<h1 class=\"archive-title\">{title}</h1>"
            f"<div class=\"archive-meta\">{meta}</div>{body}</body></html>")


def collect_records(paths: Paths, keep_images: bool) -> list[dict]:
    today = f"{dt.date.today():%Y-%m-%d}"
    records = []

    for f in sorted(paths.raw_uesp.glob("*.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        soup = _soup(rec.get("html", ""))
        for bad in soup.select(".mw-editsection, .navbox, .toc, .noprint, "
                               "table.metadata, #toc"):
            bad.decompose()
        if not keep_images:
            for img in soup.select("img"):
                img.decompose()
        else:
            for img in soup.select("img[src^='/']"):
                img["src"] = "https://en.uesp.net" + img["src"]
        body = soup.decode_contents()
        words = len(soup.get_text(" ", strip=True).split())
        if words < 60:
            continue
        records.append({"source": "uesp", "tier": "uesp",
                        "title": rec["title"].replace("Online:", ""),
                        "url": rec.get("url", ""), "words": words,
                        "html": _doc(rec["title"],
                                     f"UESP &middot; {rec.get('url','')} "
                                     f"&middot; archived {today}", body)})

    for f in sorted(paths.raw_zos.glob("*.html")):
        if f.name.startswith("index_"):
            continue
        meta = {}
        mp = f.with_suffix(".json")
        if mp.exists():
            try:
                meta = json.loads(mp.read_text(encoding="utf-8"))
            except Exception:
                pass
        raw = f.read_text(encoding="utf-8", errors="replace")
        soup = _soup(raw)
        title = meta.get("title") or ""
        og = soup.select_one('meta[property="og:title"]')
        if og and og.get("content"):
            title = og["content"].strip()
        if not title:
            h1 = soup.select_one("h1")
            title = h1.get_text(strip=True) if h1 else f.stem
        title = re.sub(r"\s*[-–—|]\s*The Elder Scrolls Online.*$", "", title,
                       flags=re.I).strip()
        date = ""
        t = soup.select_one("time[datetime]")
        if t:
            date = (t.get("datetime") or "")[:10]
        if not date:
            m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', raw)
            if m:
                date = m.group(1)
        for bad in soup.select(ZOS_JUNK):
            bad.decompose()
        block, score = _best_block(soup)
        if block is None or score < 250:
            continue
        if not keep_images:
            for img in block.select("img"):
                img.decompose()
        records.append({"source": "zos", "tier": meta.get("tier", "zos"),
                        "title": title, "url": meta.get("url", ""),
                        "words": len(block.get_text(" ", strip=True).split()),
                        "html": _doc(title,
                                     f"{meta.get('tier','official')} &middot; "
                                     f"{date or 'date unknown'} &middot; "
                                     f"{meta.get('url','')} &middot; archived {today}",
                                     block.decode_contents())})

    for f in sorted(paths.raw_esolog.glob("*.html")):
        soup = _soup(f.read_text(encoding="utf-8", errors="replace"))
        for bad in soup.select("script, style, nav, header, footer, form"):
            bad.decompose()
        body = soup.body.decode_contents() if soup.body else ""
        records.append({"source": "esolog", "tier": "esolog",
                        "title": f.stem.replace("_", " ").title(),
                        "url": ESOLOG_PAGES.get(f.stem, ""),
                        "words": len(soup.get_text(" ", strip=True).split()),
                        "html": _doc(f.stem.replace("_", " ").title(),
                                     f"UESP esolog &middot; archived {today}", body)})

    records.sort(key=lambda r: (r["source"], r["tier"], r["title"]))
    return records


def render(paths: Paths, keep_images: bool) -> None:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        die("playwright is not installed.")
    paths.mkdirs()
    records = collect_records(paths, keep_images)
    if not records:
        die("nothing harvested yet. Run a harvest phase first.")

    stale = re.compile(r"^\d{3}_")
    for folder, suffix in ((paths.pdf, ".pdf"), (paths.clean, ".html")):
        for old in folder.glob(f"*{suffix}"):
            if stale.match(old.name):
                old.unlink()

    # A single enormous page (the skill coefficient dump is around half a
    # million words) will exhaust the renderer and poison every page after
    # it. Those live in the CSVs anyway, so they are not worth a PDF.
    HUGE = 120_000

    failures = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(120_000)
        since_restart = 0

        for i, rec in enumerate(records, 1):
            stem = f"{i:03d}_{rec['source']}_{safe_name(rec['title'], 60)}"
            hpath = paths.clean / f"{stem}.html"
            ppath = paths.pdf / f"{stem}.pdf"
            hpath.write_text(rec["html"], encoding="utf-8")
            rec["pdf"] = ppath.name

            if rec["words"] > HUGE:
                rec["pdf"] = ""
                log(f"[{i}/{len(records)}] {stem}: {rec['words']} words, too "
                    f"large for one PDF. The HTML and the CSV tables have it.")
                continue

            # Recycle the renderer periodically. Chromium leaks across many
            # print jobs and a wedged renderer times out every later page.
            if since_restart >= 40:
                try:
                    page.close()
                    browser.close()
                except Exception:
                    pass
                browser = pw.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(120_000)
                since_restart = 0

            try:
                page.goto(hpath.as_uri(), wait_until="domcontentloaded",
                          timeout=60_000)
                try:
                    # Images are a nicety. Never let one stall the run.
                    page.wait_for_load_state("load", timeout=15_000)
                except Exception:
                    pass
                page.pdf(path=str(ppath), format="A4", print_background=True,
                         margin={"top": "16mm", "bottom": "16mm",
                                 "left": "14mm", "right": "14mm"})
                since_restart += 1
                log(f"[{i}/{len(records)}] {ppath.name}  ({rec['words']} words)")
            except Exception as exc:
                rec["pdf"] = ""
                failures.append((stem, str(exc)[:90]))
                log(f"[{i}/{len(records)}] {stem}: FAILED, continuing")
                try:
                    page.close()
                    browser.close()
                except Exception:
                    pass
                browser = pw.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(120_000)
                since_restart = 0
        try:
            browser.close()
        except Exception:
            pass

    if failures:
        log(f"{len(failures)} page(s) could not be rendered:")
        for stem, err in failures[:10]:
            log(f"    {stem}: {err}")

    with paths.manifest.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["seq", "source", "tier", "title", "words", "pdf", "url"])
        for i, r in enumerate(records, 1):
            w.writerow([i, r["source"], r["tier"], r["title"], r["words"],
                        r.get("pdf", ""), r["url"]])
    log(f"Rendered {len(records)} PDFs into {paths.pdf}")


def merge(paths: Paths) -> None:
    try:
        from pypdf import PdfWriter, PdfReader  # type: ignore
    except ImportError:
        die("pypdf is not installed.  pip install pypdf")
    files = sorted(paths.pdf.glob("*.pdf"))
    if not files:
        die("no PDFs to merge. Run render first.")
    writer = PdfWriter()
    n = 0
    for f in files:
        r = PdfReader(str(f))
        for pg in r.pages:
            writer.add_page(pg)
        writer.add_outline_item(re.sub(r"^\d+_", "", f.stem).replace("_", " ")[:110], n)
        n += len(r.pages)
    with paths.merged.open("wb") as fh:
        writer.write(fh)
    log(f"Merged {len(files)} documents, {n} pages -> {paths.merged.name}")


def inspect(paths: Paths) -> None:
    print(f"raw UESP pages   : {len(list(paths.raw_uesp.glob('*.json')))}")
    print(f"raw ZOS pages    : {len(list(paths.raw_zos.glob('*.html')))}")
    print(f"raw esolog pages : {len(list(paths.raw_esolog.glob('*.html')))}")
    print(f"CSV tables       : {len(list(paths.tables.glob('*.csv')))}")
    idx = paths.data / "tables_index.json"
    if idx.exists():
        data = json.loads(idx.read_text(encoding="utf-8"))
        data.sort(key=lambda d: -d["rows"])
        print("\nbiggest tables:")
        for d in data[:12]:
            print(f"  {d['rows']:>5} rows  {d['page'][:38]:<38} "
                  f"{', '.join(d['header'][:4])[:60]}")
    f = next(iter(sorted(paths.raw_zos.glob("news-*.html"))), None)
    if f:
        soup = _soup(f.read_text(encoding="utf-8", errors="replace"))
        for bad in soup.select(ZOS_JUNK):
            bad.decompose()
        b, s = _best_block(soup)
        print(f"\nZOS parser check on {f.name}: "
              f"<{b.name if b is not None else None}> score={s}")


# ======================================================================

REQUIRED = {"playwright": "playwright", "bs4": "beautifulsoup4", "pypdf": "pypdf"}


def check_dependencies(offer_install: bool) -> bool:
    import importlib.util
    import subprocess
    missing = [p for m, p in REQUIRED.items() if importlib.util.find_spec(m) is None]
    if not missing:
        return True
    print("\nMissing packages: " + ", ".join(missing))
    if not offer_install:
        print(f'  "{sys.executable}" -m pip install {" ".join(missing)} lxml')
        return False
    if (input("\nInstall them now? [Y/n] ").strip().lower() or "y").startswith("n"):
        return False
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing, "lxml"])
    if "playwright" in missing:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    return True


MENU = """
ESO reference archive
=====================

  1  Test run        a small slice of each source, to check the output
  2  Full archive    everything: every set, every skill, systems, ZOS
  3  UESP only       the mechanics data, no browser needed at all
  4  ZOS only        deep dives and guides, browser, asks your age once
  5  Rebuild offline re-extract data and PDFs from what is saved
  6  Inspect         what is harvested, and the biggest data tables
  q  Quit

UESP runs through their API. It pulls system pages one at a time, then
every item set and every ability, morph and passive fifty pages per
request, so the full run is minutes rather than an hour.

The ZOS site is age gated and asks for your date of birth once. The script
will not answer that for you, so type it in the browser window when it
appears. If you skip it or close the window, the run keeps the UESP data
and carries on instead of failing.
"""


def run(paths: Paths, uesp: bool, browser: bool, limit: int | None,
        refresh: bool = False, include_all: bool = False) -> None:
    if uesp:
        harvest_uesp(paths, refresh, limit)
    if browser:
        try:
            harvest_browser(paths, refresh, include_all, limit)
        except Exception as exc:
            # The age gate or a dropped browser must not cost you the
            # UESP data that already downloaded.
            log(f"ZOS harvest did not finish ({exc}).")
            log("Carrying on with everything else that was collected.")
    build_data(paths)
    render(paths, keep_images=True)
    merge(paths)


def interactive(out: str) -> None:
    print(MENU)
    choice = (input("Choose [1]: ").strip().lower() or "1")
    if choice.startswith("q"):
        return
    if not check_dependencies(True):
        input("\nPress Enter to close.")
        return
    paths = Paths(Path(out))
    paths.mkdirs()
    try:
        if choice == "1":
            run(paths, True, True, limit=8)
            print(f"\nCheck the PDFs in: {paths.pdf}\nand the CSVs in: {paths.tables}")
        elif choice == "2":
            run(paths, True, True, limit=None)
        elif choice == "3":
            run(paths, True, False, limit=None)
        elif choice == "4":
            run(paths, False, True, limit=None)
        elif choice == "5":
            build_data(paths)
            render(paths, True)
            merge(paths)
        elif choice == "6":
            inspect(paths)
        else:
            print("Unrecognised choice.")
    except KeyboardInterrupt:
        print("\nStopped. Rerun to pick up where it left off.")
    except Exception as exc:
        print(f"\nFAILED: {type(exc).__name__}: {exc}")
    input("\nPress Enter to close.")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Archive ESO reference material from UESP and ZOS")
    ap.add_argument("phase", nargs="?",
                    choices=["harvest", "data", "render", "merge", "all", "inspect"])
    ap.add_argument("--source", choices=["uesp", "zos", "esolog", "both"],
                    default="both")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--include-all", action="store_true",
                    help="keep every ZOS news post, not just combat ones")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--no-images", action="store_true")
    args = ap.parse_args()

    if args.phase is None:
        interactive(args.out)
        return
    if not check_dependencies(sys.stdin.isatty()):
        sys.exit(1)

    paths = Paths(Path(args.out))
    paths.mkdirs()
    want_uesp = args.source in ("uesp", "both")
    want_browser = args.source in ("zos", "esolog", "both")

    if args.phase in ("harvest", "all"):
        if want_uesp:
            harvest_uesp(paths, args.refresh, args.limit)
        if want_browser:
            harvest_browser(paths, args.refresh, args.include_all, args.limit,
                            do_zos=args.source in ("zos", "both"),
                            do_esolog=args.source in ("esolog", "both"))
    if args.phase in ("data", "all"):
        build_data(paths)
    if args.phase in ("render", "all"):
        render(paths, keep_images=not args.no_images)
    if args.phase in ("merge", "all"):
        merge(paths)
    if args.phase == "inspect":
        inspect(paths)


if __name__ == "__main__":
    main()
