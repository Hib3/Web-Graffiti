# Safety Policy

Web Graffiti is a static mirror-first archive viewer for defensive awareness. It is not a discovery, scanning, exploitation, or ranking tool.

## Allowed

- Display manually curated defacement records from `public/data/records.json`.
- Show masked victim URL strings through `hackedUrlDisplay`.
- Link only to `mirrorUrl` when `mirrorAccessible` is true.
- Use local thumbnails to help users decide which mirror record to inspect.
- Show `source` and `fetchedAt` on every record card.
- Filter and search local JSON fields.

## Not Allowed

- Crawling live victim websites.
- Live discovery, Google dorking, vulnerable site search, or scraping adapters.
- Making victim URLs clickable.
- Exposing admin paths, shell paths, exploit methods, payloads, or vulnerability details.
- Creating hacker rankings, scores, badges, leaderboards, or other gamified views.
- Adding a backend or Cloudflare Worker in the initial MVP.

## Data Handling

Use `hackedUrlDisplay` for UI rendering. Use `hackedUrlHash` for deduplication if needed. Do not store or render full victim URLs unless they are already safely masked for public display.

The primary workflow is: review thumbnail, confirm hacker name and masked target context, then open the public mirror. There should be no other outbound route from a record card.
