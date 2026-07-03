# Source Research

## OwnzYou

Initial source: `https://ownzyou.com/archive`

OwnzYou exposes approved public mirror records in an archive table with these columns:

- `Location`
- `Attacker Name`
- `Web URL`
- `Server`
- `Date`
- `Preview`

The fetcher reads only the public archive listing pages. It does not request victim websites. `Preview` links are normalized to OwnzYou mirror URLs such as `https://ownzyou.com/zone/<id>`.

## Current Fetch Policy

- Default to one archive page per run.
- Wait between pages when more than one page is configured.
- Send a clear archival/research user-agent.
- Do not follow victim URLs.
- Mask victim URL paths before writing public UI fields.
- Fail safely and keep the previous `records.json` when parsing fails.

## Later Sources

Adapters exist for:

- Zone-Xsec
- Zone-H
- Defacer.Net

Zone-Xsec and Zone-H can return anti-bot or JavaScript challenge pages from non-browser automation. In that case the adapter logs a source error and generation continues with other sources. Defacer.Net is parsed from its public archive table when reachable.

Each source should follow the same mirror-only policy and avoid exploit details, vulnerable-site discovery, and live victim crawling.
