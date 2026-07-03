from __future__ import annotations

from typing import Any

from .base import SourceAdapter


class ZoneHAdapter(SourceAdapter):
    name = "Zone-H"
    base_url = "https://www.zone-h.org/"
    source_url = "https://www.zone-h.org/archive"
    env_prefix = "ZONEH"

    def page_url(self, page: int) -> str:
        if page <= 1:
            return self.source_url
        return f"{self.base_url}archive/page%3D{page}"

    def fetch(self) -> list[dict[str, Any]]:
        settings = self.settings()
        output: list[dict[str, Any]] = []

        for page in range(1, settings.max_pages + 1):
            self.wait_between_pages(page, settings.delay_seconds)
            soup = self.get_soup(self.page_url(page), settings.timeout_seconds)
            page_text = soup.get_text(" ", strip=True)
            if "slowAES.decrypt" in str(soup) or "ZHE=" in str(soup):
                raise RuntimeError(f"{self.name}: JavaScript challenge encountered")

            rows = soup.find_all("tr")
            for row in rows:
                links = row.find_all("a")
                mirror_link = next((link for link in links if "mirror" in link.get_text(" ", strip=True).lower()), None)
                if not mirror_link:
                    continue
                cells = row.find_all("td")
                if len(cells) < 4:
                    continue
                output.append(
                    {
                        "source": self.name,
                        "sourceBaseUrl": self.base_url,
                        "sourceUrl": self.source_url,
                        "thumbnailUrl": None,
                        "hackerName": cells[1].get_text(" ", strip=True),
                        "hackedUrl": cells[-2].get_text(" ", strip=True),
                        "countryCode": cells[2].get_text(" ", strip=True),
                        "mirrorUrl": mirror_link.get("href"),
                        "mirrorAccessible": True,
                        "reportedAt": cells[0].get_text(" ", strip=True),
                    }
                )

        return output
