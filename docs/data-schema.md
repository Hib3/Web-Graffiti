# Web Graffiti Data Schema

Records are stored in `public/data/records.json` and loaded by the static app at runtime. The file contains an array of records sorted in the UI by `reportedAt` descending.

```json
{
  "id": "wg-000001",
  "thumbnailUrl": "/web-graffiti/thumbnails/sample-001.jpg",
  "hackerName": "ExampleHacker",
  "hackedUrlDisplay": "example.jp/...",
  "hackedUrlHash": "sha256:replace-with-real-hash",
  "country": "Japan",
  "countryCode": "JP",
  "mirrorUrl": "https://example.invalid/mirror/12345",
  "mirrorAccessible": true,
  "source": "manual",
  "sourceUrl": "https://example.invalid/source",
  "reportedAt": "2026-07-04T12:00:00+09:00",
  "fetchedAt": "2026-07-04T12:30:00+09:00",
  "tags": ["black-background", "hacked-by", "plain-text"],
  "safetyFlags": ["victim-url-masked"]
}
```

## Fields

- `id`: Stable record ID.
- `thumbnailUrl`: Public thumbnail path. If omitted, the UI shows a placeholder.
- `hackerName`: Display name from the source record.
- `hackedUrlDisplay`: Masked, display-safe victim URL string. This must never be clickable.
- `hackedUrlHash`: Hash for deduplication without exposing the original victim URL.
- `country` / `countryCode`: Country label and ISO-style country code.
- `mirrorUrl`: Only external URL that may be clickable in the UI.
- `mirrorAccessible`: Controls whether the mirror button is enabled.
- `source` / `sourceUrl`: Source metadata. The UI always shows `source`.
- `reportedAt`: Timestamp used for newest-first sorting.
- `fetchedAt`: Timestamp showing when the record metadata was fetched or checked.
- `tags`: Searchable descriptive labels.
- `safetyFlags`: Internal safety notes, such as `victim-url-masked`.
