from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from normalize import dedupe_records, normalize_record, now_iso, sort_records
from sources.defacernet import DefacerNetAdapter
from sources.ownzyou import OwnzYouAdapter
from sources.zoneh import ZoneHAdapter
from sources.zonexsec import ZoneXsecAdapter


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "public" / "data" / "records.json"


def load_previous_records() -> list[dict]:
    if not OUTPUT_PATH.exists():
        return []
    try:
        return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def write_records(records: list[dict]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = OUTPUT_PATH.with_suffix(".json.tmp")
    temp_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(OUTPUT_PATH)


def generate_records() -> list[dict]:
    adapters = [
        OwnzYouAdapter(),
        ZoneXsecAdapter(),
        ZoneHAdapter(),
        DefacerNetAdapter(),
    ]
    fetched_at = now_iso()
    records: list[dict] = []

    for adapter in adapters:
        try:
            raw_records = adapter.fetch()
        except Exception as exc:
            print(f"[source-error] {adapter.name}: {exc}", file=sys.stderr)
            continue

        normalized = [normalize_record(record, fetched_at) for record in raw_records]
        valid = [record for record in normalized if record is not None]
        print(f"[source-ok] {adapter.name}: {len(valid)} records", file=sys.stderr)
        records.extend(valid)

    return sort_records(dedupe_records(records))


def main() -> int:
    previous = load_previous_records()
    try:
        records = generate_records()
    except Exception as exc:
        print(f"Failed to generate records; keeping previous records.json: {exc}", file=sys.stderr)
        return 1 if not previous else 0

    if not records:
        print("No records generated; keeping previous records.json", file=sys.stderr)
        return 1 if not previous else 0

    limit = int(os.environ.get("WEB_GRAFFITI_RECORD_LIMIT", "100"))
    write_records(records[:limit])
    print(f"Wrote {min(len(records), limit)} records to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
