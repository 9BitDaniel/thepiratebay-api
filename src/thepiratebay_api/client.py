import httpx
from typing import Any
from .config import BASE_URL
from .parsers import _parse_search_results, _parse_torrent_page



class PirateBay:

    def __init__(self, url: str = BASE_URL) -> None:
        
        self.base_url = url
        self.session = httpx.Client()

    def search(self, query: str, page: int = 1) -> list[dict[str, Any]]:
        """Scrapes search results for a query and page number."""
        url = f"{self.base_url}/search/{query}/{page}/99/0"
        res = self.session.get(url)
        return _parse_search_results(res.text, self.base_url)
    
    def info(self, torrent_url: str) -> dict[str, Any] | None:
        """Fetches and parses a torrent detail page."""
        res = self.session.get(torrent_url)
        return _parse_torrent_page(res.text)