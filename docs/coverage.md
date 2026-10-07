# Coverage and freshness

Verified on 2026-10-07, from the development machine:

- Zone-Xsec `/archive` returns HTTP 403 with a challenge page.
- Zone-H `/archive` returns HTTP 200 with a JavaScript challenge, not archive rows.
- OwnzYou `/archive.php?per=20&q=.jp` exposes its public archive search (20 rows observed).
- Defacer.Net `/search/?query=.jp` exposes its public archive search (30 rows observed).

Each working source now fetches its bounded general listings plus one Japanese-domain search page, with a delay between requests. These searches run on archives, never on victim sites. Search results may also match `.jp` inside other text. The frontend Japan-related filter uses only the masked hostname ending in `.jp`, or the archive's `JP` location code. Neither signal proves that the victim is a Japanese organization; the country can describe hosting location. Japanese organizations using other domains and overseas hosting can be missed.

Collection runs every six hours. GitHub Actions schedules may be delayed; this is not real-time monitoring. Collection timestamps and newest report timestamps are separate. The UI warns after 12 hours without a collection or seven days without a newer report. Successful HTTP responses and unchanged old records do not establish current threat coverage.

Fresh records merge with the previous dataset, deduplicated by source and mirror URL, retaining at most 5,000 newest records. Old observations retain their fetchedAt. Zero parsed records are a source failure. Failure of all sources fails the workflow and preserves the last dataset. Minimum fresh-record checks cannot be satisfied by historical records alone. Additional listing request failures are marked partial in source status.

## Blocked-source alternatives

1. Ordinary browser rendering could handle a JavaScript-only interstitial, but automated access and parsing have not been verified for Zone-H. It must not be reported as restored.
2. A documented API/feed or an operator-approved export would be more stable than parsing challenge pages. Availability for Zone-H and Zone-Xsec remains unknown. No proxy rotation, copied authentication cookies, or CAPTCHA-solving service has been added.
3. The verified OwnzYou and Defacer.Net search routes provide additional Japan-related records now; they do not reproduce the missing archives' coverage.

## Broader Japanese security information

JPCERT/CC publishes official RSS for alerts, emergency reports and weekly vulnerability information: https://www.jpcert.or.jp/rss/ . These are valuable supplementary security reports, but are not defacement mirrors or a complete list of Japanese incidents. They should use a separate feed/view if added, not invented attacker names or mirror URLs in records.json. The existing mirror-only navigation is unchanged.

## Remaining limits

Archive attacker names are source claims, not independently verified attribution. Mirror links are supplied by the archive; per-mirror availability and screenshots are not verified by this listing-only collector. Thumbnail placeholders remain. Source publication delay, unknown source time zones (currently normalized as UTC), blocked sources, bounded page depth, and the retention cap limit coverage. No claim of comprehensive or real-time Japanese incident detection is made.
