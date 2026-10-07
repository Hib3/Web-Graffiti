"""Offline regression checks: python scripts/test_pipeline.py."""
from unittest.mock import patch
from normalize import normalize_record, dedupe_records, sort_records
import generate_records as pipeline


def main():
    raw = dict(source="OwnzYou", sourceBaseUrl="https://ownzyou.com/",
               sourceUrl="archive", mirrorUrl="zone/1", hackedUrl="https://example.jp/private/path",
               countryCode="JP", reportedAt="2026-01-02T00:00:00Z")
    record = normalize_record(raw, "2026-01-03T00:00:00+00:00")
    assert record["country"] == "Japan"
    assert record["hackedUrl"] == "example.jp/..."
    assert normalize_record({**raw, "mirrorUrl": "https://victim.invalid/"}, "now") is None
    assert normalize_record({**raw, "mirrorUrl": None}, "now") is None
    old = {**record, "id": "old", "mirrorUrl": "https://ownzyou.com/zone/2", "reportedAt": None}
    fresh = {**record, "fetchedAt": "2026-01-04T00:00:00+00:00"}
    merged = sort_records(dedupe_records([fresh, record, old]))
    assert merged == [fresh, old]
    assert old["fetchedAt"] == "2026-01-03T00:00:00+00:00"
    with patch.object(pipeline.OwnzYouAdapter, "fetch", return_value=[]), \
         patch.object(pipeline.ZoneXsecAdapter, "fetch", side_effect=ValueError("blocked")), \
         patch.object(pipeline.ZoneHAdapter, "fetch", return_value=[]), \
         patch.object(pipeline.DefacerNetAdapter, "fetch", return_value=[raw]):
        records, status = pipeline.generate_records()
        assert len(records) == 1 and status["successfulSources"] == 1
        assert all(not s["ok"] for s in status["sources"][:3])
    with patch.object(pipeline, "load_previous_records", return_value=[old]), \
         patch.object(pipeline, "generate_records", return_value=([], {})), \
         patch.object(pipeline, "write_records") as write:
        assert pipeline.main() == 1
        write.assert_not_called()
    print("Pipeline regression checks passed")


if __name__ == "__main__":
    main()
