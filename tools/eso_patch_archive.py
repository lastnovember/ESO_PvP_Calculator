#!/usr/bin/env python3
"""
ESO patch note archiver (Xbox / console / all-platform).

Builds a local PDF archive of every Elder Scrolls Online patch note that
applied to Xbox, sourced from the official "Patch Notes & Hotfixes" forum
category.

Why it works the way it does
----------------------------
The ESO forums sit behind Cloudflare bot verification, so plain HTTP
scraping (requests, headless browsers) gets a "Just a moment..." wall.
This script therefore runs a REAL, VISIBLE browser window for the
harvest phase. If a verification check appears, you click it yourself,
once. The clearance cookie is stored in a local profile folder, so later
runs go straight through.

Everything after the harvest is offline. Raw HTML is saved to disk, so
parsing, PDF rendering and merging can be re-run any number of times
without touching the network again.

Phases
------
  harvest   Save raw HTML of the category index and every matching thread.
  render    Parse the saved HTML, build one clean PDF per patch.
  merge     Combine the PDFs into one bookmarked master volume.
  all       harvest, then render, then merge.
  inspect   Print the detected HTML structure of one saved thread
            (use this if parsing looks wrong, and send me the output).

Usage
-----
  python eso_patch_archive.py all
  python eso_patch_archive.py harvest --refresh
  python eso_patch_archive.py render
  python eso_patch_archive.py inspect

Setup
-----
  pip install playwright beautifulsoup4 pypdf
  playwright install chromium
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path

BASE = "https://forums.elderscrollsonline.com"
CATEGORY = "/en/categories/patch-notes"

# --- thread classification, tuned against all 712 threads in the category ---
#
# Xbox-specific threads.
RX_XBOX = re.compile(r"xbox", re.I)

# Notes ZOS published for every platform at once, plus console-only hotfixes.
RX_ALL_PLATFORM = re.compile(
    r"all-platform|console|all-realm|all-megaserver|all-server", re.I)

# Explicitly somebody else's platform, or PC-only plumbing.
RX_OTHER = re.compile(
    r"pc-mac|pc-na|pc-eu|pc-server|pc-and|-pc-|^pc-|(^|-)mac(-|$)"
    r"|playstation|(^|-)ps[45](-|$)|(^|-)pts(-|$)"
    r"|patcher|launcher|stadia|store-account", re.I)

# Thread ids rise over time. This is the first Xbox thread ever posted
# ("Xbox One Patch Notes v1.0.0.5", console launch, June 2015), so anything
# below it predates consoles and cannot be an Xbox note.
CONSOLE_ERA_ID = 184843


def classify(tid: int, slug: str) -> str | None:
    """Return 'xbox', 'all-platform', 'unlabeled', or None to skip."""
    if RX_XBOX.search(slug):
        return "xbox"
    if RX_OTHER.search(slug):
        return None
    if RX_ALL_PLATFORM.search(slug):
        return "all-platform"
    if tid >= CONSOLE_ERA_ID:
        # An unlabeled hotfix from the console era. ZOS usually names the
        # platform when a fix is PC-only, so these are probably relevant.
        return "unlabeled"
    return None

REQUEST_DELAY = 2.5     # seconds between page loads, be polite
MAX_THREAD_PAGES = 12   # safety cap per thread
NAV_TIMEOUT = 60_000    # ms

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR / "ESO Patch Notes Archive"


# ----------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------

def log(msg: str) -> None:
    print(f"[{dt.datetime.now():%H:%M:%S}] {msg}", flush=True)


def die(msg: str) -> None:
    print(f"\nERROR: {msg}\n", file=sys.stderr)
    sys.exit(1)


def safe_name(s: str, limit: int = 90) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")
    return s[:limit] or "untitled"


class Paths:
    def __init__(self, out: Path):
        out = Path(out).expanduser().resolve()
        self.out = out
        self.raw_index = out / "raw" / "index"
        self.raw_threads = out / "raw" / "threads"
        self.clean = out / "clean_html"
        self.pdf = out / "pdf"
        self.profile = out / "_browser_profile"
        self.manifest = out / "manifest.csv"
        self.merged = out / "ESO_Xbox_Patch_Notes_Complete.pdf"
        self.thread_list = out / "raw" / "threads.json"

    def mkdirs(self) -> None:
        for p in (self.raw_index, self.raw_threads, self.clean,
                  self.pdf, self.profile):
            p.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------
# phase 1: harvest
# ----------------------------------------------------------------------

CHALLENGE_MARKERS = ("just a moment", "checking your browser",
                     "performing security verification",
                     "verify you are human")


def _looks_challenged(title: str, body: str) -> bool:
    t = (title or "").lower()
    b = (body or "")[:600].lower()
    return any(m in t or m in b for m in CHALLENGE_MARKERS)


def _get_html(page, url: str, wait_for_human: bool = True) -> str:
    """Load a URL and return its HTML, pausing for a human if Cloudflare
    shows a verification check."""
    page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)

    deadline = time.time() + (300 if wait_for_human else 30)
    warned = False
    while time.time() < deadline:
        try:
            title = page.title()
            body = page.evaluate("document.body ? document.body.innerText : ''")
        except Exception:
            time.sleep(1.5)
            continue

        if not _looks_challenged(title, body):
            return page.content()

        if not warned:
            log("Cloudflare verification shown. Click it in the browser "
                "window. Waiting up to 5 minutes...")
            warned = True
        time.sleep(2.0)

    raise RuntimeError(f"stuck on a verification page at {url}")


def _index_page_url(n: int) -> str:
    return f"{BASE}{CATEGORY}" if n == 1 else f"{BASE}{CATEGORY}/p{n}"


# The forum writes absolute URLs in listings, relative ones elsewhere.
THREAD_HREF = re.compile(
    r'href="(?:https?://forums\.elderscrollsonline\.com)?'
    r'/en/discussion/(\d+)/([a-z0-9-]+)', re.I)
INDEX_PAGER = re.compile(re.escape(CATEGORY) + r"/p(\d+)")
THREAD_PAGER = re.compile(r"/en/discussion/\d+/[a-z0-9-]+/p(\d+)")


def _threads_from_index(html: str) -> list[tuple[int, str]]:
    seen: dict[int, str] = {}
    for tid, slug in THREAD_HREF.findall(html):
        seen.setdefault(int(tid), slug)
    return sorted(seen.items())


def harvest(paths: Paths, refresh: bool, include_all: bool,
            limit: int | None, strict: bool = False) -> None:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        die("playwright is not installed.\n"
            "  pip install playwright beautifulsoup4 pypdf\n"
            "  playwright install chromium")

    paths.mkdirs()

    with sync_playwright() as pw:
        ctx = None
        for channel in ("chrome", "msedge", None):
            try:
                ctx = pw.chromium.launch_persistent_context(
                    user_data_dir=str(paths.profile),
                    headless=False,
                    channel=channel,
                    viewport={"width": 1280, "height": 900},
                    args=["--disable-blink-features=AutomationControlled"],
                )
                break
            except Exception:
                continue
        if ctx is None:
            die("could not launch a browser. Run: playwright install chromium")

        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_default_timeout(NAV_TIMEOUT)

        # --- category index ------------------------------------------------
        log("Loading the patch notes category...")
        first = _get_html(page, _index_page_url(1))
        (paths.raw_index / "p1.html").write_text(first, encoding="utf-8")

        pages = max([int(n) for n in INDEX_PAGER.findall(first)] or [1])
        log(f"Category has {pages} index pages.")

        threads: dict[int, str] = dict(_threads_from_index(first))
        for n in range(2, pages + 1):
            target = paths.raw_index / f"p{n}.html"
            if target.exists() and not refresh:
                html = target.read_text(encoding="utf-8")
            else:
                time.sleep(REQUEST_DELAY)
                log(f"Index page {n}/{pages}")
                html = _get_html(page, _index_page_url(n))
                target.write_text(html, encoding="utf-8")
            threads.update(dict(_threads_from_index(html)))

        log(f"Found {len(threads)} threads in total.")

        # --- filter ----------------------------------------------------------
        tiers: dict[int, str] = {}
        for tid, slug in sorted(threads.items()):
            tier = "everything" if include_all else classify(tid, slug)
            if tier:
                tiers[tid] = tier

        if strict:
            tiers = {t: v for t, v in tiers.items() if v != "unlabeled"}

        picked = [(tid, threads[tid]) for tid in sorted(tiers)]
        counts: dict[str, int] = {}
        for v in tiers.values():
            counts[v] = counts.get(v, 0) + 1
        log(f"{len(picked)} threads selected "
            + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))

        paths.thread_list.write_text(
            json.dumps([{"id": t, "slug": threads[t], "tier": tiers[t]}
                        for t in sorted(tiers)], indent=2),
            encoding="utf-8")

        if limit:
            picked = picked[-limit:]
            log(f"Limited to the {len(picked)} most recent for this run.")

        # --- threads ---------------------------------------------------------
        for i, (tid, slug) in enumerate(picked, 1):
            tdir = paths.raw_threads / f"{tid}_{safe_name(slug)}"
            tdir.mkdir(parents=True, exist_ok=True)
            p1 = tdir / "p1.html"

            if p1.exists() and not refresh:
                html = p1.read_text(encoding="utf-8")
            else:
                time.sleep(REQUEST_DELAY)
                log(f"[{i}/{len(picked)}] {slug}")
                html = _get_html(page, f"{BASE}/en/discussion/{tid}/{slug}")
                p1.write_text(html, encoding="utf-8")

            npages = min(max([int(n) for n in THREAD_PAGER.findall(html)] or [1]),
                         MAX_THREAD_PAGES)

            # Later pages are only worth fetching when the whole first page is
            # still the ZOS author, meaning the notes may continue onto page 2.
            # Once players have started replying, there is nothing left to add.
            if npages > 1:
                try:
                    authors = [a for a, _ in _extract_posts(html)]
                    if authors and any(a and a != authors[0] for a in authors):
                        npages = 1
                except Exception:
                    pass

            for n in range(2, npages + 1):
                target = tdir / f"p{n}.html"
                if target.exists() and not refresh:
                    continue
                time.sleep(REQUEST_DELAY)
                log(f"      page {n}/{npages}")
                target.write_text(
                    _get_html(page, f"{BASE}/en/discussion/{tid}/{slug}/p{n}"),
                    encoding="utf-8")

        ctx.close()
    log("Harvest complete.")


# ----------------------------------------------------------------------
# phase 2: parse + render
# ----------------------------------------------------------------------

PAGE_CSS = """
@page { size: A4; margin: 18mm 15mm; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10.5pt;
       line-height: 1.45; color: #1a1a1a; }
h1.archive-title { font-family: Helvetica, Arial, sans-serif; font-size: 17pt;
       margin: 0 0 4px 0; }
.archive-meta { font-family: Helvetica, Arial, sans-serif; font-size: 8.5pt;
       color: #666; border-bottom: 1px solid #ccc; padding-bottom: 8px;
       margin-bottom: 16px; }
.archive-part { border-top: 1px dashed #ddd; margin-top: 18px; padding-top: 10px; }
h1, h2, h3, h4 { font-family: Helvetica, Arial, sans-serif; line-height: 1.25;
       page-break-after: avoid; }
h2 { font-size: 13pt; margin-top: 16px; }
h3 { font-size: 11.5pt; margin-top: 13px; }
ul, ol { margin: 6px 0 6px 18px; padding-left: 12px; }
li { margin: 2px 0; }
img { max-width: 100%; height: auto; }
table { border-collapse: collapse; max-width: 100%; }
td, th { border: 1px solid #bbb; padding: 3px 6px; font-size: 9.5pt; }
blockquote { border-left: 3px solid #ddd; margin-left: 0; padding-left: 10px;
       color: #444; }
a { color: #1a1a1a; text-decoration: none; }
pre, code { font-family: Consolas, monospace; font-size: 9pt;
       white-space: pre-wrap; }
"""

POST_SELECTORS = [
    ".ItemDiscussion, .ItemComment",
    "li.Item",
    ".Discussion, .Comment",
]


def _soup(html: str):
    from bs4 import BeautifulSoup  # type: ignore
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html.parser")


def _post_author(node) -> str:
    for sel in ("a.Username", ".Author a", ".PhotoWrap + a", "[data-username]"):
        el = node.select_one(sel)
        if el:
            return (el.get("data-username") or el.get_text(strip=True) or "").strip()
    return ""


def _post_body(node):
    for sel in (".Message.userContent", "div.Message", ".userContent",
                ".Item-Body .Message"):
        el = node.select_one(sel)
        if el:
            return el
    return None


def _extract_posts(html: str) -> list[tuple[str, object]]:
    """Return [(author, body_element), ...] in document order."""
    soup = _soup(html)
    for sel in POST_SELECTORS:
        nodes = soup.select(sel)
        out = []
        for n in nodes:
            body = _post_body(n)
            if body is not None:
                out.append((_post_author(n), body))
        if out:
            return out
    # last resort: every message block, author unknown
    return [("", el) for el in soup.select("div.Message, .userContent")]


def _thread_meta(html: str) -> tuple[str, str]:
    soup = _soup(html)
    title = ""
    og = soup.select_one('meta[property="og:title"]')
    if og and og.get("content"):
        title = og["content"].strip()
    if not title:
        h1 = soup.select_one("h1")
        if h1:
            title = h1.get_text(strip=True)
    title = re.sub(r"\s*[-–—|]\s*Elder Scrolls Online.*$", "",
                   title, flags=re.I).strip()
    title = re.sub(r"\s*—\s*", " - ", title).strip(" -|")

    date = ""
    t = soup.select_one("time[datetime]")
    if t:
        date = (t.get("datetime") or "")[:10]
    if not date:
        m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', html)
        if m:
            date = m.group(1)
    return title or "Untitled", date


def _clean_body(el, keep_images: bool) -> str:
    from bs4 import Tag  # type: ignore
    for bad in el.select("script, style, .Quote .QuoteAuthor, .ReactButton, "
                         ".Reactions, .AttachFileWrap"):
        bad.decompose()
    if not keep_images:
        for img in el.select("img"):
            img.decompose()
    for a in el.select("a"):
        if isinstance(a, Tag):
            a.attrs = {k: v for k, v in a.attrs.items() if k == "href"}
    return el.decode_contents()


def build_clean_html(tdir: Path, keep_images: bool) -> dict | None:
    page_files = sorted(tdir.glob("p*.html"),
                        key=lambda p: int(re.sub(r"\D", "", p.stem) or 1))
    if not page_files:
        return None

    first_html = page_files[0].read_text(encoding="utf-8", errors="replace")
    title, date = _thread_meta(first_html)

    posts = _extract_posts(first_html)
    if not posts:
        return None

    op_author = posts[0][0]
    parts = [_clean_body(posts[0][1], keep_images)]

    # Long patch notes continue in the author's own following posts.
    for author, body in posts[1:]:
        if op_author and author and author != op_author:
            break
        parts.append(_clean_body(body, keep_images))

    # Continuation can also spill onto later thread pages.
    if len(parts) == len(posts) and len(page_files) > 1:
        for pf in page_files[1:]:
            more = _extract_posts(pf.read_text(encoding="utf-8", errors="replace"))
            stop = False
            for author, body in more:
                if op_author and author and author != op_author:
                    stop = True
                    break
                parts.append(_clean_body(body, keep_images))
            if stop:
                break

    tid = int(tdir.name.split("_", 1)[0])
    body_html = "".join(
        f'<div class="archive-part">{p}</div>' if i else p
        for i, p in enumerate(parts))

    doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>{PAGE_CSS}</style></head><body>
<h1 class="archive-title">{title}</h1>
<div class="archive-meta">
Posted {date or 'date unknown'} by {op_author or 'ZOS staff'} &middot;
forums.elderscrollsonline.com/en/discussion/{tid} &middot;
archived {dt.date.today():%Y-%m-%d}
</div>
{body_html}
</body></html>"""

    return {"id": tid, "title": title, "date": date, "author": op_author,
            "parts": len(parts), "html": doc,
            "url": f"{BASE}/en/discussion/{tid}",
            "words": len(re.sub(r"<[^>]+>", " ", body_html).split())}


def render(paths: Paths, keep_images: bool) -> None:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        die("playwright is not installed. See the setup notes at the top.")

    paths.mkdirs()
    tdirs = sorted([d for d in paths.raw_threads.iterdir() if d.is_dir()],
                   key=lambda d: int(d.name.split("_", 1)[0]))
    if not tdirs:
        die("no harvested threads found. Run the harvest phase first.")

    tiers: dict[int, str] = {}
    if paths.thread_list.exists():
        try:
            tiers = {e["id"]: e.get("tier", "")
                     for e in json.loads(paths.thread_list.read_text("utf-8"))}
        except Exception:
            pass

    records = []
    for d in tdirs:
        rec = build_clean_html(d, keep_images)
        if not rec:
            log(f"could not parse {d.name}, skipping")
            continue
        rec["tier"] = tiers.get(rec["id"], "")
        records.append(rec)

    records.sort(key=lambda r: (r["date"] or "", r["id"]))

    # Clear previously rendered output. Numbering is positional, so leftovers
    # from a smaller run would otherwise survive as duplicates.
    stale = re.compile(r"^\d{3}_")
    for folder, suffix in ((paths.pdf, ".pdf"), (paths.clean, ".html")):
        for old in folder.glob(f"*{suffix}"):
            if stale.match(old.name):
                old.unlink()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        for i, rec in enumerate(records, 1):
            stem = f"{i:03d}_{rec['date'] or 'undated'}_{safe_name(rec['title'], 70)}"
            hpath = paths.clean / f"{stem}.html"
            ppath = paths.pdf / f"{stem}.pdf"
            hpath.write_text(rec["html"], encoding="utf-8")
            rec["pdf"] = ppath.name

            page.goto(hpath.as_uri(), wait_until="load")
            page.pdf(path=str(ppath), format="A4", print_background=True,
                     margin={"top": "18mm", "bottom": "18mm",
                             "left": "15mm", "right": "15mm"})
            log(f"[{i}/{len(records)}] {ppath.name}  ({rec['words']} words, "
                f"{rec['parts']} post part(s))")
        browser.close()

    with paths.manifest.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["seq", "date", "title", "applies_to", "words",
                    "post_parts", "pdf", "source_url"])
        for i, r in enumerate(records, 1):
            w.writerow([i, r["date"], r["title"], r.get("tier", ""),
                        r["words"], r["parts"], r.get("pdf", ""), r["url"]])

    log(f"Rendered {len(records)} PDFs into {paths.pdf}")


# ----------------------------------------------------------------------
# phase 3: merge
# ----------------------------------------------------------------------

def merge(paths: Paths) -> None:
    try:
        from pypdf import PdfWriter, PdfReader  # type: ignore
    except ImportError:
        die("pypdf is not installed.  pip install pypdf")

    files = sorted(paths.pdf.glob("*.pdf"))
    if not files:
        die("no PDFs to merge. Run the render phase first.")

    writer = PdfWriter()
    page_no = 0
    for f in files:
        reader = PdfReader(str(f))
        for pg in reader.pages:
            writer.add_page(pg)
        label = re.sub(r"^\d+_", "", f.stem).replace("_", " ")
        writer.add_outline_item(label[:110], page_no)
        page_no += len(reader.pages)

    with paths.merged.open("wb") as fh:
        writer.write(fh)
    log(f"Merged {len(files)} documents, {page_no} pages -> {paths.merged.name}")


# ----------------------------------------------------------------------
# inspect
# ----------------------------------------------------------------------

def inspect(paths: Paths) -> None:
    tdirs = sorted([d for d in paths.raw_threads.iterdir() if d.is_dir()])
    if not tdirs:
        die("nothing harvested yet.")
    d = tdirs[-1]
    html = (d / "p1.html").read_text(encoding="utf-8", errors="replace")
    soup = _soup(html)
    print(f"thread dir : {d.name}")
    print(f"meta       : {_thread_meta(html)}")
    for sel in POST_SELECTORS + ["div.Message", "a.Username", "time[datetime]"]:
        print(f"  {sel:<34} -> {len(soup.select(sel))} match(es)")
    posts = _extract_posts(html)
    print(f"posts found: {len(posts)}")
    for a, b in posts[:6]:
        print(f"   author={a!r:<22} chars={len(b.get_text())}")


# ----------------------------------------------------------------------

REQUIRED_PACKAGES = {
    "playwright": "playwright",
    "bs4": "beautifulsoup4",
    "pypdf": "pypdf",
}


def check_dependencies(offer_install: bool) -> bool:
    """Return True if everything needed is importable."""
    import importlib.util
    import subprocess

    missing = [pip_name for mod, pip_name in REQUIRED_PACKAGES.items()
               if importlib.util.find_spec(mod) is None]

    if not missing:
        return True

    print("\nMissing packages: " + ", ".join(missing))
    print(f"Interpreter: {sys.executable}")

    if not offer_install:
        print("\nInstall them with:")
        print(f'  "{sys.executable}" -m pip install playwright beautifulsoup4 pypdf lxml')
        print(f'  "{sys.executable}" -m playwright install chromium')
        return False

    answer = input("\nInstall them now? [Y/n] ").strip().lower()
    if answer and not answer.startswith("y"):
        return False

    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           *missing, "lxml"])
    if "playwright" in missing:
        print("\nDownloading the browser engine (one time, about 150 MB)...")
        subprocess.check_call([sys.executable, "-m", "playwright",
                               "install", "chromium"])
    print("\nDependencies installed.\n")
    return True


MENU = """
ESO Xbox patch note archive
===========================

  1  Test run      3 threads only, so you can check the output first
  2  Full archive  harvest everything, render PDFs, merge   (45 to 90 min)
  3  Render only   rebuild PDFs from already harvested pages, no network
  4  Merge only    rebuild the single combined PDF
  5  Inspect       print parser diagnostics for the last harvested thread
  q  Quit

A browser window will open during harvesting. If a "verify you are human"
box appears, click it once and the script carries on by itself.
"""


def interactive(out: str) -> None:
    print(MENU)
    choice = input("Choose [1]: ").strip().lower() or "1"
    if choice.startswith("q"):
        return

    if not check_dependencies(offer_install=True):
        input("\nPress Enter to close.")
        return

    paths = Paths(Path(out))
    paths.mkdirs()

    try:
        if choice == "1":
            harvest(paths, refresh=False, include_all=False, limit=3)
            render(paths, keep_images=True)
            print(f"\nCheck the PDFs in: {paths.pdf}")
        elif choice == "2":
            harvest(paths, refresh=False, include_all=False, limit=None)
            render(paths, keep_images=True)
            merge(paths)
        elif choice == "3":
            render(paths, keep_images=True)
        elif choice == "4":
            merge(paths)
        elif choice == "5":
            inspect(paths)
        else:
            print("Unrecognised choice.")
    except KeyboardInterrupt:
        print("\nStopped. Rerun to pick up where it left off.")
    except Exception as exc:
        print(f"\nFAILED: {type(exc).__name__}: {exc}")

    input("\nPress Enter to close.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Archive ESO Xbox patch notes as PDFs")
    ap.add_argument("phase", nargs="?",
                    choices=["harvest", "render", "merge", "all", "inspect"],
                    help="omit this to get an interactive menu")
    ap.add_argument("--out", default=str(DEFAULT_OUT),
                    help="output folder (default: next to this script)")
    ap.add_argument("--refresh", action="store_true",
                    help="re-download pages already saved")
    ap.add_argument("--include-all", action="store_true",
                    help="harvest every thread in the category, no filter")
    ap.add_argument("--strict", action="store_true",
                    help="only threads that name Xbox or all platforms, "
                         "skipping unlabeled console-era hotfixes")
    ap.add_argument("--limit", type=int,
                    help="only the N most recent matching threads (for a test run)")
    ap.add_argument("--no-images", action="store_true",
                    help="strip images from the PDFs (smaller, faster)")
    args = ap.parse_args()

    if args.phase is None:
        interactive(args.out)
        return

    if not check_dependencies(offer_install=sys.stdin.isatty()):
        sys.exit(1)

    paths = Paths(Path(args.out))
    paths.mkdirs()

    if args.phase in ("harvest", "all"):
        harvest(paths, args.refresh, args.include_all, args.limit,
                strict=args.strict)
    if args.phase in ("render", "all"):
        render(paths, keep_images=not args.no_images)
    if args.phase in ("merge", "all"):
        merge(paths)
    if args.phase == "inspect":
        inspect(paths)


if __name__ == "__main__":
    main()
