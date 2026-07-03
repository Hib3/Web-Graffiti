# Web Graffiti Data Schema

Records are stored in `public/data/records.json` and loaded by the static app at runtime. The file contains an array of records sorted in the UI by `reportedAt` descending.

```json
{
  "id": "wg-000001",
  "source": "OwnzYou",
  "sourceUrl": "https://ownzyou.com/archive",
  "thumbnailUrl": null,
  "hackerName": "ExampleHacker",
  "hackedUrl": "example.jp/...",
  "country": "Japan",
  "countryCode": "JP",
  "mirrorUrl": "https://example.invalid/mirror/12345",
  "mirrorAccessible": true,
  "reportedAt": "2026-07-04T12:00:00+09:00",
  "fetchedAt": "2026-07-04T12:30:00+09:00"
}
```

## Fields

- `id`: Stable record ID.
- `thumbnailUrl`: Optional public thumbnail path under the deployed app base. If empty, the UI shows a placeholder.
- `hackerName`: Display name from the source record.
- `hackedUrl`: Masked victim URL string for UI/search use.
- `country` / `countryCode`: Nullable country label and ISO-style country code.
- `mirrorUrl`: Only external URL that may be clickable in the UI.
- `mirrorAccessible`: Controls whether the mirror button is enabled.
- `source` / `sourceUrl`: Source metadata. The UI always shows `source`.
- `reportedAt`: Timestamp used for newest-first sorting.
- `fetchedAt`: Timestamp showing when the record metadata was fetched or checked.
