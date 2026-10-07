"""Render saved mirror snapshots with scripts and non-archive requests blocked."""
import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse, urljoin

from playwright.sync_api import sync_playwright
from sources.base import USER_AGENT
from generate_records import write_json
from normalize import mask_hacked_url

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "public/data/records.json"
ALLOWED_HOSTS = {"hack-mirror.com", "ownzyou.com", "defacer.net"}


def allowed(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in ALLOWED_HOSTS and not parsed.username


def sanitize_snapshot(html: str | bytes, frame_url: str) -> str:
    snapshot = BeautifulSoup(html, 'lxml')
    for node in snapshot.select('script, base, meta[http-equiv], iframe, object, embed'):
        node.decompose()
    for node in list(snapshot.find_all(string=True)):
        if node.parent.name in {'style', 'head', 'title'}:
            continue
        text = re.sub(r'https?://[^\s<>"\']+', lambda m: mask_hacked_url(m[0]), str(node))
        text = re.sub(r'/(?:admin|wp-admin|shell|exploit|cgi-bin)\b[^\s<>]*', '[masked path]', text, flags=re.I)
        node.replace_with(text)
    base = snapshot.new_tag('base', href=frame_url)
    (snapshot.head or snapshot).insert(0, base)
    return str(snapshot)


def main():
    records = json.loads(RECORDS.read_text(encoding="utf-8"))
    for record in records:
        if not record['mirrorAccessible']:
            record['thumbnailUrl'] = None
    candidates = []
    per_source = {}
    for record in records:
        source = record['source']
        if record['mirrorAccessible'] and allowed(record['mirrorUrl']) and per_source.get(source, 0) < 4:
            candidates.append(record)
            per_source[source] = per_source.get(source, 0) + 1
    limit = int(os.environ.get("THUMBNAIL_LIMIT", "12"))
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 960, "height": 600},
                                      java_script_enabled=False, service_workers="block", user_agent=USER_AGENT)
        context.route("**/*", lambda route: route.continue_() if allowed(route.request.url) and not route.request.is_navigation_request() else route.abort())
        page = context.new_page()
        for record in candidates[:limit]:
            path = ROOT / "public/thumbnails" / f"{record['id']}.jpg"
            time.sleep(2)
            try:
                response = session.get(record['mirrorUrl'], timeout=15, allow_redirects=False)
                if response.status_code != 200:
                    raise RuntimeError("mirror wrapper unavailable")
                wrapper = BeautifulSoup(response.text, 'lxml')
                frame = wrapper.select_one('iframe[src]')
                frame_url = frame.get('src') if frame else None
                frame_url = urljoin(record['mirrorUrl'], frame_url) if frame_url else None
                if not frame_url or not allowed(frame_url):
                    raise RuntimeError("no approved archived snapshot")
                time.sleep(2)
                response = session.get(frame_url, timeout=15, allow_redirects=False)
                if response.status_code != 200:
                    raise RuntimeError("archived snapshot unavailable")
                page.set_content(sanitize_snapshot(response.content, frame_url), wait_until='domcontentloaded', timeout=15000)
                text = page.locator("body").inner_text().strip()
                if not text and page.locator("img").count() == 0:
                    raise RuntimeError("empty archived snapshot")
                path.parent.mkdir(parents=True, exist_ok=True)
                attacker = page.get_by_text(record['hackerName'], exact=False)
                if attacker.count() and attacker.last.is_visible():
                    attacker.last.scroll_into_view_if_needed(timeout=3000)
                page.screenshot(path=str(path), type="jpeg", quality=70, animations="disabled")
                record["thumbnailUrl"] = f"thumbnails/{path.name}"
                print(f"[thumbnail-ok] {record['id']}")
            except Exception as exc:
                print(f"[thumbnail-error] {record['id']}: {str(exc)[:200]}")
                record["mirrorAccessible"] = False
                record["thumbnailUrl"] = None
        browser.close()
    write_json(RECORDS, records)
    used = {r['thumbnailUrl'].rsplit('/', 1)[-1] for r in records if r.get('thumbnailUrl')}
    for path in (ROOT / 'public/thumbnails').glob('wg-*.jpg'):
        if path.name not in used:
            path.unlink()
    if not any(r['source'] == 'Hack Mirror' and r.get('thumbnailUrl') and r['mirrorAccessible'] for r in candidates):
        raise RuntimeError("No new-source snapshots could be rendered; deployment stopped")


if __name__ == "__main__":
    main()
