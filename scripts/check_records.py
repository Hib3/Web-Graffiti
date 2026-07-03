from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECORDS_PATH = ROOT / "public" / "data" / "records.json"
REQUIRED_KEYS = {
    "id",
    "source",
    "sourceUrl",
    "thumbnailUrl",
    "hackerName",
    "hackedUrl",
    "country",
    "countryCode",
    "mirrorUrl",
    "mirrorAccessible",
    "reportedAt",
    "fetchedAt",
}


def parse_iso(value: Any, nullable: bool = False) -> bool:
    if value is None:
        return nullable
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False
    return True


def main() -> int:
    records = json.loads(RECORDS_PATH.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not records:
        print("records.json must be a non-empty array", file=sys.stderr)
        return 1

    seen_ids: set[str] = set()
    for index, record in enumerate(records):
        if set(record.keys()) != REQUIRED_KEYS:
            print(f"record {index} has invalid keys: {sorted(record.keys())}", file=sys.stderr)
            return 1
        if record["id"] in seen_ids:
            print(f"duplicate id: {record['id']}", file=sys.stderr)
            return 1
        seen_ids.add(record["id"])
        for key in ["id", "source", "sourceUrl", "hackerName", "hackedUrl", "mirrorUrl", "fetchedAt"]:
            if not isinstance(record[key], str) or not record[key].strip():
                print(f"record {index} invalid {key}", file=sys.stderr)
                return 1
        if record["thumbnailUrl"] is not None and not isinstance(record["thumbnailUrl"], str):
            print(f"record {index} invalid thumbnailUrl", file=sys.stderr)
            return 1
        if record["country"] is not None and not isinstance(record["country"], str):
            print(f"record {index} invalid country", file=sys.stderr)
            return 1
        if record["countryCode"] is not None and not isinstance(record["countryCode"], str):
            print(f"record {index} invalid countryCode", file=sys.stderr)
            return 1
        if not isinstance(record["mirrorAccessible"], bool):
            print(f"record {index} invalid mirrorAccessible", file=sys.stderr)
            return 1
        if not parse_iso(record["reportedAt"], nullable=True):
            print(f"record {index} invalid reportedAt", file=sys.stderr)
            return 1
        if not parse_iso(record["fetchedAt"]):
            print(f"record {index} invalid fetchedAt", file=sys.stderr)
            return 1
        if "://" in record["hackedUrl"]:
            print(f"record {index} hackedUrl must be display-safe text, not a URL", file=sys.stderr)
            return 1

    sorted_records = sorted(records, key=lambda item: item["reportedAt"] or "", reverse=True)
    if records != sorted_records:
        print("records.json is not sorted by reportedAt descending", file=sys.stderr)
        return 1

    print(f"Validated {len(records)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
