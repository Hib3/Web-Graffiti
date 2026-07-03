from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

from .base import SourceAdapter


class OwnzYouAdapter(SourceAdapter):
    name = "OwnzYou"
    base_url = "https://ownzyou.com/"
    source_url = "https://ownzyou.com/archive"
    env_prefix = "OWNZYOU"

    def page_url(self, page: int) -> str:
        if page <= 1:
            return self.source_url
        return urljoin(self.base_url, f"archive.php?page={page}&per=20")

    def fetch(self) -> list[dict[str, Any]]:
        settings = self.settings()
        output: list[dict[str, Any]] = []

        for page in range(1, settings.max_pages + 1):
            self.wait_between_pages(page, settings.delay_seconds)
            soup = self.get_soup(self.page_url(page), settings.timeout_seconds)
            rows = soup.select("table.archive-table tbody tr")
            if not rows:
                raise RuntimeError(f"{self.name}: no archive rows found on page {page}")

            for row in rows:
                cells = row.find_all("td")
                if len(cells) < 6:
                    continue
                location, attacker, web_url, _server, date_cell, preview = cells[:6]
                web_link = web_url.find("a")
                preview_link = preview.find("a")
                hacked_url = web_link.get_text(" ", strip=True) if web_link else web_url.get_text(" ", strip=True)
                mirror_href = preview_link.get("href") if preview_link else None

                if not hacked_url or not mirror_href:
                    continue

                output.append(
                    {
                        "source": self.name,
                        "sourceBaseUrl": self.base_url,
                        "sourceUrl": self.source_url,
                        "thumbnailUrl": None,
                        "hackerName": attacker.get_text(" ", strip=True).replace("Verified", "").strip(),
                        "hackedUrl": hacked_url,
                        "countryCode": location.get_text(" ", strip=True),
                        "mirrorUrl": mirror_href,
                        "mirrorAccessible": True,
                        "reportedAt": date_cell.get_text(" ", strip=True),
                    }
                )

        return output
