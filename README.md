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

OwnzYou and Defacer.Net currently provide records. Zone-Xsec and Zone-H have adapters but currently block automated listing requests. Both working sources include an additional public `.jp` search. The Japan-related filter matches archive country code JP or a hostname ending in `.jp`; this does not establish Japanese ownership.

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
