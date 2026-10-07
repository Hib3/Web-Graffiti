from __future__ import annotations

import time
from urllib.parse import urljoin
from .base import SourceAdapter


class HackMirrorAdapter(SourceAdapter):
    name = "Hack Mirror"
    base_url = "https://hack-mirror.com/"
    source_url = "https://hack-mirror.com/archive"
    env_prefix = "HACKMIRROR"

    def parse_listing(self, soup):
        records = []
        for row in soup.select('tr'):
            cells = row.find_all('td', recursive=False)
            mirror = row.select_one('a[href^="/mirror/"]')
            if len(cells) != 11 or mirror is None:
                continue
            flag = cells[6].find('img')
            code = flag['src'].rsplit('/', 1)[-1].split('.')[0].upper() if flag else None
            records.append(dict(source=self.name, sourceBaseUrl=self.base_url, sourceUrl=self.source_url,
                                hackerName=cells[2].get_text(' ', strip=True), hackedUrl=cells[1].get_text(' ', strip=True),
                                countryCode=code, mirrorUrl=urljoin(self.base_url, mirror['href']),
                                reportedAt=None, mirrorAccessible=False, thumbnailUrl=None))
        return records

    def fetch(self):
        settings = self.settings()
        records = self.parse_listing(self.get_soup(self.source_url, settings.timeout_seconds))[:12]
        output = []
        for record in records:
            time.sleep(settings.delay_seconds)
            try:
                detail = self.get_soup(record['mirrorUrl'], settings.timeout_seconds)
                frame = detail.select_one('iframe[src^="/storage/defacements/"]')
                if not frame:
                    raise RuntimeError('No archived snapshot')
                time.sleep(settings.delay_seconds)
                snapshot = self.get_soup(urljoin(self.base_url, frame['src']), settings.timeout_seconds)
                if not snapshot.get_text(strip=True) and not snapshot.find('img'):
                    raise RuntimeError('Empty archived snapshot')
                label = detail.find('span', string='Created:')
                date = label.parent.find('strong') if label else None
                record['reportedAt'] = date.get_text(strip=True) if date else None
                record['mirrorAccessible'] = True
                output.append(record)
            except Exception as exc:
                self.warnings.append(f'Mirror detail failed: {exc}')
        if not output:
            raise RuntimeError('Hack Mirror: no accessible archive details')
        return output
