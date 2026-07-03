from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from html import unescape
from typing import Any
from urllib.parse import urljoin, urlparse

from dateutil import parser as date_parser


COUNTRY_NAMES = {
    "BE": "Belgium",
    "BR": "Brazil",
    "DE": "Germany",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "GB": "United Kingdom",
    "ID": "Indonesia",
    "IE": "Ireland",
    "IN": "India",
    "NL": "Netherlands",
    "RU": "Russia",
    "SE": "Sweden",
    "US": "United States",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_space(value: str | None) -> str:
    return " ".join(unescape(value or "").split())


def mask_hacked_url(url: str | None) -> str:
    parsed = urlparse(normalize_space(url))
    host = parsed.netloc or parsed.path.split("/", 1)[0]
    host = host.lower().strip()
    return f"{host}/..." if host else "unknown/..."


def normalize_url(base_url: str, href: str | None) -> str:
    return urljoin(base_url, normalize_space(href))


def normalize_reported_at(value: str | None) -> str | None:
    text = normalize_space(value)
    if not text:
        return None
    try:
        parsed = date_parser.parse(text)
    except (ValueError, TypeError, OverflowError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def make_record_id(source: str, mirror_url: str, hacked_url: str) -> str:
    digest = hashlib.sha256(f"{source}|{mirror_url}|{hacked_url}".encode("utf-8")).hexdigest()
    return f"wg-{digest[:12]}"


def normalize_record(raw: dict[str, Any], fetched_at: str) -> dict[str, Any] | None:
    source = normalize_space(raw.get("source"))
    source_url = normalize_url(raw.get("sourceBaseUrl", ""), raw.get("sourceUrl"))
    mirror_url = normalize_url(raw.get("sourceBaseUrl", ""), raw.get("mirrorUrl") or raw.get("mirrorHref"))
    hacked_url_raw = normalize_space(raw.get("hackedUrl"))
    hacked_url = mask_hacked_url(hacked_url_raw)
    hacker_name = normalize_space(raw.get("hackerName")) or "Unknown"
    country_code = normalize_space(raw.get("countryCode")).upper() or None

    if not source or not mirror_url or not hacked_url_raw:
        return None

    return {
        "id": make_record_id(source, mirror_url, hacked_url_raw.lower()),
        "source": source,
        "sourceUrl": source_url,
        "thumbnailUrl": raw.get("thumbnailUrl") or None,
        "hackerName": hacker_name,
        "hackedUrl": hacked_url,
        "country": COUNTRY_NAMES.get(country_code, country_code) if country_code else None,
        "countryCode": country_code,
        "mirrorUrl": mirror_url,
        "mirrorAccessible": bool(raw.get("mirrorAccessible", True)),
        "reportedAt": normalize_reported_at(raw.get("reportedAt")),
        "fetchedAt": fetched_at,
    }


def dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    output: list[dict[str, Any]] = []
    for record in records:
        key = f"{record.get('source')}|{record.get('mirrorUrl')}"
        fallback = f"hackedUrl|{record.get('hackedUrl')}"
        dedupe_key = key if record.get("mirrorUrl") else fallback
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        output.append(record)
    return output


def sort_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(records, key=lambda record: record.get("reportedAt") or "", reverse=True)
