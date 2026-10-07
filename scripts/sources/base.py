from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import requests
from bs4 import BeautifulSoup


USER_AGENT = (
    "WebGraffitiResearchBot/0.1 "
    "(+https://github.com/Hib3/Web-Graffiti; public defacement archive research; no victim crawling)"
)


@dataclass(frozen=True)
class FetchSettings:
    max_pages: int
    delay_seconds: float
    timeout_seconds: float


class SourceAdapter(ABC):
    name: str
    base_url: str
    source_url: str
    env_prefix: str

    def __init__(self) -> None:
        self.warnings: list[str] = []
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml",
            }
        )

    def settings(self) -> FetchSettings:
        prefix = self.env_prefix
        return FetchSettings(
            max_pages=int(os.environ.get(f"{prefix}_MAX_PAGES", "1")),
            delay_seconds=float(os.environ.get(f"{prefix}_DELAY_SECONDS", "2")),
            timeout_seconds=float(os.environ.get(f"{prefix}_TIMEOUT_SECONDS", "30")),
        )

    def get_soup(self, url: str, timeout_seconds: float) -> BeautifulSoup:
        response = self.session.get(url, timeout=timeout_seconds, allow_redirects=False)
        if 300 <= response.status_code < 400:
            raise RuntimeError(f"{self.name}: unexpected redirect; not followed")
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")

    def wait_between_pages(self, page: int, delay_seconds: float) -> None:
        if page > 1 and delay_seconds > 0:
            time.sleep(delay_seconds)

    @abstractmethod
    def fetch(self) -> list[dict[str, Any]]:
        raise NotImplementedError
