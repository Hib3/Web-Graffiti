from __future__ import annotations

from typing import Any

from .base import SourceAdapter


class ZoneXsecAdapter(SourceAdapter):
    name = "Zone-Xsec"
    base_url = "https://zone-xsec.com/"
    source_url = "https://zone-xsec.com/archive"
    env_prefix = "ZONEXSEC"

    def page_url(self, page: int) -> str:
        if page <= 1:
            return self.source_url
        return f"{self.base_url}archive/page={page}"

    def fetch(self) -> list[dict[str, Any]]:
        settings = self.settings()
        output: list[dict[str, Any]] = []

        for page in range(1, settings.max_pages + 1):
            self.wait_between_pages(page, settings.delay_seconds)
            soup = self.get_soup(self.page_url(page), settings.timeout_seconds)
            page_text = soup.get_text(" ", strip=True)
            if "Just a moment" in page_text:
                raise RuntimeError(f"{self.name}: anti-bot challenge encountered")

            rows = soup.find_all("tr")
            for row in rows:
                text = row.get_text(" ", strip=True)
                if "Mirror" not in text:
                    continue
                cells = row.find_all("td")
                if len(cells) < 5:
                    continue
                links = row.find_all("a")
                mirror_link = next((link for link in links if "mirror" in link.get_text(" ", strip=True).lower()), None)
                website_link = links[-2] if len(links) >= 2 else None
                if not mirror_link or not website_link:
                    continue
                output.append(
                    {
                        "source": self.name,
                        "sourceBaseUrl": self.base_url,
                        "sourceUrl": self.source_url,
                        "thumbnailUrl": None,
                        "hackerName": cells[1].get_text(" ", strip=True),
                        "hackedUrl": website_link.get_text(" ", strip=True),
                        "countryCode": cells[0].get_text(" ", strip=True),
                        "mirrorUrl": mirror_link.get("href"),
                        "mirrorAccessible": True,
                        "reportedAt": cells[-2].get_text(" ", strip=True),
                    }
                )

        return output
