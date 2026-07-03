from __future__ import annotations

from typing import Any

from .base import SourceAdapter


class DefacerNetAdapter(SourceAdapter):
    name = "Defacer.Net"
    base_url = "https://defacer.net/"
    source_url = "https://defacer.net/archive/"
    env_prefix = "DEFACERNET"

    def page_url(self, page: int) -> str:
        if page <= 1:
            return self.source_url
        return f"{self.source_url}{page - 1}"

    def fetch(self) -> list[dict[str, Any]]:
        settings = self.settings()
        output: list[dict[str, Any]] = []

        for page in range(1, settings.max_pages + 1):
            self.wait_between_pages(page, settings.delay_seconds)
            soup = self.get_soup(self.page_url(page), settings.timeout_seconds)
            tables = soup.find_all("table")
            archive_table = next((table for table in tables if "Date & Time" in table.get_text(" ", strip=True)), None)
            if archive_table is None:
                raise RuntimeError(f"{self.name}: archive table not found on page {page}")

            cells = archive_table.find_all("td")
            if len(cells) < 10:
                raise RuntimeError(f"{self.name}: no archive rows found on page {page}")

            for index in range(0, len(cells) - 9, 10):
                row = cells[index : index + 10]
                date_cell, attacker, _team, _mass, _rede, _home, location, _star, website, mirror = row
                website_link = website.find("a")
                mirror_link = mirror.find("a")
                flag = location.find("img")
                country_code = None
                if flag and flag.get("src"):
                    country_code = flag["src"].rsplit("/", 1)[-1].split(".", 1)[0].upper()
                    if country_code == "STRIP":
                        country_code = None

                hacked_url = website_link.get_text(" ", strip=True) if website_link else website.get_text(" ", strip=True)
                mirror_url = mirror_link.get("href") if mirror_link else None

                if not hacked_url or not mirror_url:
                    continue

                output.append(
                    {
                        "source": self.name,
                        "sourceBaseUrl": self.base_url,
                        "sourceUrl": self.source_url,
                        "thumbnailUrl": None,
                        "hackerName": attacker.get_text(" ", strip=True),
                        "hackedUrl": hacked_url,
                        "countryCode": country_code,
                        "mirrorUrl": mirror_url,
                        "mirrorAccessible": True,
                        "reportedAt": date_cell.get_text(" ", strip=True),
                    }
                )

        return output
