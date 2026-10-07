# Web Graffiti

Web Graffiti is a static GitHub Pages app for recognizing web defacement activity through public archive mirrors. It uses Vite, React, TypeScript, and local JSON data only.

## Features

- Responsive record cards with mirror thumbnails or a clear placeholder.
- Newest-first sorting by `reportedAt`.
- Search across hacker name, masked hacked URL, country, and source.
- Filters for country and accessible mirrors.
- Mirror-only external links for checking archived defacement pages.
- Loading, empty, and error states.
- Python data acquisition from public defacement mirror archives.

## Safety Boundaries

- No backend.
- No login.
- No Cloudflare Worker.
- Only public archive listings are collected; no victim crawling, live discovery, Google dorking, or vulnerable site search.
- Victim URLs are masked, display-only, and must not be clickable.
- Admin paths, shell paths, exploit methods, and vulnerability details must not be added.
- Hacker rankings and gamified leaderboards are out of scope.

## Development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## Data

Records live in `public/data/records.json`. See `docs/data-schema.md`.

Each record can have a local thumbnail under `public/thumbnails/`. If it is missing, the app shows a placeholder. The app is mirror-first: the only outbound user action is opening `mirrorUrl`.

Generate records from public archive sources:

```bash
python scripts/generate_records.py
```

OwnzYou, Defacer.Net, and Hack Mirror provide records. Hack Mirror adds up to 12 records per run after checking both archive details and saved snapshots. Its current records are historical, not a current incident feed. Zone-Xsec and Zone-H currently block automated listing requests. OwnzYou and Defacer.Net include an additional public `.jp` search. The Japan-related filter matches archive country code JP or a hostname ending in `.jp`; this does not establish Japanese ownership.

For thumbnail generation install `playwright` with the Python dependencies, then run `python -m playwright install chromium` and `python scripts/create_thumbnails.py` after generating records. Chromium disables JavaScript and blocks requests except HTTPS to `hack-mirror.com`, `ownzyou.com`, and `defacer.net`. No victim domain is fetched. Up to four screenshots per source are created (12 total per run). Thumbnail failures disable that mirror button; zero renderable Hack Mirror snapshots fail deployment. The source selector and thumbnail count expose coverage in the UI.

GitHub Actions collects every six hours, merges previous records (up to 5,000 newest), validates and deploys. Total collection failure preserves the dataset and fails the workflow. See [coverage and alternatives](docs/coverage.md) for measured limitations, blocked-source options, and Japanese official security feeds.

The app fetches data from:

```ts
`${import.meta.env.BASE_URL}data/records.json`
```

## GitHub Pages Deployment

The Vite base path is configured as `/Web-Graffiti/` in `vite.config.ts`.

The update workflow builds and deploys `dist` using GitHub Pages artifacts.

1. Push the source branch to GitHub as `main`.
2. In GitHub Pages settings, select GitHub Actions as the source.
3. Run the Update Records workflow manually under Actions, or wait for its schedule.
4. Confirm collection, checks, build, and deployment all succeed.

No Cloudflare Worker or backend is required for the MVP.
