# Source Research

## OwnzYou

Current source: `https://ownzyou.com/archive`

OwnzYou exposes approved public mirror records in an archive table with these columns:

- `Location`
- `Attacker Name`
- `Web URL`
- `Server`
- `Date`
- `Preview`

The fetcher reads only the public archive listing pages. It does not request victim websites. `Preview` links are normalized to OwnzYou mirror URLs such as `https://ownzyou.com/zone/<id>`.

## Defacer.Net

Current source: `https://defacer.net/archive/`

Defacer.Net exposes public archive rows with date, attacker, team, location flag, website, and mirror link. The adapter reads the listing table only and normalizes `Mirror` links such as `https://defacer.net/view/<id>/`.

## Zone-Xsec

Configured source: `https://zone-xsec.com/archive`

The adapter is present, but this source can return anti-bot challenge pages to non-browser automation. When that happens, generation records a source error and continues.

## Zone-H

Configured source: `https://www.zone-h.org/archive`

The adapter is present, but this source can return JavaScript challenge pages to non-browser automation. When that happens, generation records a source error and continues.

## Current Fetch Policy

- Limit pages per source with environment variables.
- Wait between pages when more than one page is configured.
- Send a clear archival/research user-agent.
- Do not follow victim URLs.
- Mask victim URL paths before writing public UI fields.
- Fail safely and keep the previous `records.json` when the minimum viable dataset is not met.
- Publish `source-status.json` so unavailable sources are visible instead of hidden.

## Minimum Viable Dataset

The scheduled workflow must not deploy an empty or misleading site. It requires:

- At least `WEB_GRAFFITI_MIN_RECORDS` records.
- At least `WEB_GRAFFITI_MIN_SUCCESSFUL_SOURCES` source adapters with records.
- Valid `records.json` and `source-status.json`.

Each source follows the same mirror-only policy and avoids exploit details, vulnerable-site discovery, and live victim crawling.
