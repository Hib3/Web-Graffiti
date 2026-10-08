# Agent Handoff Notes

Handoff for the next coding agent (e.g. Codex). This file captures an
investigation of the data pipeline, the confirmed issues, environment
constraints, and a recommended plan. No changes to the pipeline or data have
been made yet — the working tree was clean at handoff time.

## Purpose (do not violate)

Web Graffiti is a **defensive, awareness-only** viewer of *public* web
defacement mirror archives. It is not a discovery, scanning, exploitation, or
ranking tool. Preserve every safety invariant in `docs/safety-policy.md`:

- No crawling of victim sites; only read the public archive listing pages.
- Victim URLs are masked, display-only, and never clickable.
- Only `mirrorUrl` may be a clickable outbound link.
- No admin/shell paths, exploit methods, payloads, or vulnerability details.
- No rankings, scores, badges, or leaderboards.

## Environment constraints (important)

- **The dev/CI sandbox used for investigation cannot reach any source host.**
  Outbound egress policy returns HTTP 403 for `ownzyou.com`, `defacer.net`,
  `zone-xsec.com`, and `zone-h.org` (curl and any HTTP fetch). Live scraping
  therefore cannot be tested from that sandbox — only from the GitHub Actions
  runner, which is where the committed data was actually produced.
- **GitHub Pages is only deployed by the Actions runner.** The
  `Update Records` workflow (`.github/workflows/update-records.yml`) does
  data generation → validation → `npm run build` → Pages deploy. An agent
  cannot deploy Pages directly; push to the branch and let the workflow run
  (via `workflow_dispatch` or the daily schedule).
- Because sources are anti-bot protected AND egress-blocked in the sandbox,
  **parsing must be verifiable offline via HTML fixtures**, not live requests.

## How the pipeline works today

1. `scripts/generate_records.py` drives four `SourceAdapter`s (OwnzYou,
   Zone-Xsec, Zone-H, Defacer.Net). Each `fetch()`es archive listing pages
   with `requests` + BeautifulSoup (`lxml`).
2. `scripts/normalize.py` masks the victim URL, maps country, hashes a stable
   id, parses `reportedAt`, then records are deduped and sorted newest-first.
3. Output is written to `public/data/records.json` and
   `public/data/source-status.json`, gated by `WEB_GRAFFITI_MIN_RECORDS` and
   `WEB_GRAFFITI_MIN_SUCCESSFUL_SOURCES`; on failure the previous data is kept.
4. `scripts/check_records.py` validates schema, key set, and sort order.
5. The React/TS frontend (`src/`) fetches both JSON files and renders
   mirror-only cards with search/filter.

## Source appropriateness (researched)

All four configured sources are real, researcher-used public defacement
archives. Findings:

- **Zone-H** (`zone-h.org`) is the canonical/authoritative archive, but it
  serves a JavaScript/anti-bot challenge to non-browser clients, so the plain
  `requests` adapter currently fails against it.
- **Zone-Xsec** (`zone-xsec.com`) is behind a Cloudflare "Just a moment"
  challenge and, per public notices, is **shutting down and migrating its data
  to a static archive on GitHub**. That static export would be a more stable,
  ToS-friendly source than live scraping — worth adopting when available.
- **OwnzYou** and **Defacer.Net** are the only two sources that currently
  produce data from the CI runner.

Owner decision at handoff: **keep all four sources and focus on hardening**
(retries, robust parsing, data-quality fixes), rather than dropping/replacing
sources for now. Revisit the Zone-Xsec static-archive migration later.

## Confirmed issues to fix

1. **Incomplete country map (data-quality bug, provable).**
   `scripts/normalize.py` `COUNTRY_NAMES` has only ~14 entries. Any ISO code
   outside it (e.g. TW, PL, KZ, SG, CA, HK, RO) falls back to showing the raw
   two-letter code as the country *name*, so the UI renders e.g. "TW (TW)".
   Fix: replace with a complete ISO 3166-1 alpha-2 → name map (dependency-free
   static dict, e.g. a new `scripts/countries.py`). Also handle the case where
   a source supplies a full country *name* instead of a code.

2. **Duplicated write logic.** `generate_records.py` has both `write_json` and
   `write_records`; they do the same atomic temp-file write. Collapse to one.

3. **Stale per-source counts after truncation.** `records[:limit]` is applied
   after building the per-source `recordCount`s, so `source-status.json`
   per-source counts can no longer sum to `totalRecords`. Recompute the status
   from the final limited record set. `check_records.py` does not currently
   catch this inconsistency; consider adding that check.

4. **Duplicated adapter boilerplate.** All four adapters repeat the same
   page-loop, wait, challenge detection, and record-dict construction. Refactor
   into a template method on `SourceAdapter` in `scripts/sources/base.py`:
   a base `fetch()` that loops pages / waits / detects challenge / calls an
   abstract `parse_page(soup, page)`, plus a `build_record(...)` helper and a
   `challenge_markers` class attribute. Keep each adapter's proven CSS/DOM
   selectors unchanged — do not "fix" selectors blind, since they can only be
   validated against the live/fixture HTML.

5. **Dead code.** `scripts/sources/zoneh.py` computes `page_text` but then
   tests `str(soup)`; remove the unused variable when refactoring challenge
   detection into the base class.

6. **No retry/backoff.** `base.get_soup` does a single request. Add bounded
   retries with backoff for transient network errors (not for 403/anti-bot,
   which should fail fast and be recorded in `source-status.json`).

7. **No tests / no offline verifiability (biggest gap).** Add `unittest`-based
   tests (no new dependency) under `scripts/tests/` with small **synthetic
   HTML fixtures** matching each adapter's expected table structure, plus tests
   for `normalize.py` (masking stays display-safe, country mapping, id
   stability, date parsing) and `check_records.py`. Wire a test step into the
   workflow before the generate step. Fixtures let future selector fixes be
   validated without network access.

8. **Doc drift.** `docs/safety-policy.md` still says records are "manually
   curated" and `README.md` says "the current MVP source is OwnzYou", but the
   pipeline is multi-source and generated. Reconcile the docs and document the
   offline-fixture testing approach and the source notes above.

## Suggested order

countries map + normalize fix → base template-method refactor → slim the four
adapters → generate_records cleanup (single writer, recompute status) →
offline fixture tests + workflow test step → doc reconciliation.

## Safety reminders for output

When echoing progress, do **not** paste raw dataset contents (attacker
handles, victim domains, full mirror listings) into logs or chat — summarize
with counts/types only. Handle raw values inside files/processing, not in
human-facing output.
