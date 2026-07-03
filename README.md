# Web Graffiti

Web Graffiti is a static GitHub Pages app for browsing public web defacement traces in reverse chronological order. It uses Vite, React, TypeScript, and local JSON data only.

## Features

- Responsive record cards with thumbnails.
- Newest-first sorting by `reportedAt`.
- Search across hacker name, masked hacked URL display, country, and tags.
- Filters for country and accessible mirrors.
- Mirror-only external links.
- Loading, empty, and error states.

## Safety Boundaries

- No backend.
- No login.
- No Cloudflare Worker.
- No scraping, crawling, live discovery, Google dorking, or vulnerable site search.
- Victim URLs are display-only and must not be clickable.
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

The app fetches data from:

```ts
`${import.meta.env.BASE_URL}data/records.json`
```

## GitHub Pages Deployment

The Vite base path is configured as `/Web-Graffiti/` in `vite.config.ts`.

This repository can be deployed by publishing the built `dist` directory to a `gh-pages` branch.

1. Push the source branch to GitHub as `main`.
2. Run `npm run build`.
3. Publish `dist` to the `gh-pages` branch.
4. In GitHub Pages settings, set the source to `gh-pages` and `/`.

No Cloudflare Worker or backend is required for the MVP.
