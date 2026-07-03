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
STATUS_PATH = ROOT / "public" / "data" / "source-status.json"


def load_previous_records() -> list[dict]:
    if not OUTPUT_PATH.exists():
        return []
    try:
        return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)


def write_records(records: list[dict]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = OUTPUT_PATH.with_suffix(".json.tmp")
    temp_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(OUTPUT_PATH)


def generate_records() -> tuple[list[dict], dict]:
    adapters = [
        OwnzYouAdapter(),
        ZoneXsecAdapter(),
        ZoneHAdapter(),
        DefacerNetAdapter(),
    ]
    fetched_at = now_iso()
    records: list[dict] = []
    sources: list[dict] = []

    for adapter in adapters:
        try:
            raw_records = adapter.fetch()
        except Exception as exc:
            print(f"[source-error] {adapter.name}: {exc}", file=sys.stderr)
            sources.append(
                {
                    "source": adapter.name,
                    "ok": False,
                    "recordCount": 0,
                    "error": str(exc),
                    "fetchedAt": fetched_at,
                }
            )
            continue

        normalized = [normalize_record(record, fetched_at) for record in raw_records]
        valid = [record for record in normalized if record is not None]
        print(f"[source-ok] {adapter.name}: {len(valid)} records", file=sys.stderr)
        sources.append(
            {
                "source": adapter.name,
                "ok": True,
                "recordCount": len(valid),
                "error": None,
                "fetchedAt": fetched_at,
            }
        )
        records.extend(valid)

    deduped = sort_records(dedupe_records(records))
    status = {
        "generatedAt": fetched_at,
        "totalRecords": len(deduped),
        "successfulSources": sum(1 for source in sources if source["ok"] and source["recordCount"] > 0),
        "sources": sources,
    }
    return deduped, status


def main() -> int:
    previous = load_previous_records()
    try:
        records, status = generate_records()
    except Exception as exc:
        print(f"Failed to generate records; keeping previous records.json: {exc}", file=sys.stderr)
        return 1 if not previous else 0

    if not records:
        print("No records generated; keeping previous records.json", file=sys.stderr)
        return 1 if not previous else 0

    limit = int(os.environ.get("WEB_GRAFFITI_RECORD_LIMIT", "100"))
    min_records = int(os.environ.get("WEB_GRAFFITI_MIN_RECORDS", "20"))
    min_sources = int(os.environ.get("WEB_GRAFFITI_MIN_SUCCESSFUL_SOURCES", "1"))
    limited_records = records[:limit]
    status["totalRecords"] = len(limited_records)

    if len(limited_records) < min_records:
        print(
            f"Only {len(limited_records)} records generated; minimum is {min_records}. Keeping previous records.json",
            file=sys.stderr,
        )
        return 1
    if status["successfulSources"] < min_sources:
        print(
            f"Only {status['successfulSources']} successful sources; minimum is {min_sources}. Keeping previous records.json",
            file=sys.stderr,
        )
        return 1

    write_records(limited_records)
    write_json(STATUS_PATH, status)
    print(f"Wrote {len(limited_records)} records to {OUTPUT_PATH}")
    print(f"Wrote source status to {STATUS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
