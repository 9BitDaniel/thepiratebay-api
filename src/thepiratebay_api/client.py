import httpx
from typing import Any
from .config import BASE_URL
from .parsers import _parse_search_results, _parse_torrent_page
from .models import SearchResult, FullTorrent


class TorrentClient:

    def __init__(self, url: str = BASE_URL, **httpx_kwargs) -> None:
        self.base_url = url
        self.session = httpx.Client(**{"timeout": 10, **httpx_kwargs})

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    def __repr__(self) -> str:
        return f"TorrentClient(base_url={self.base_url!r})"
    
    def search(self, query: str, page: int = 1) -> SearchResult:
        """Search a query with a page number"""
        url = f"{self.base_url}/search/{query}/{page}/99/0"
        res = self.session.get(url)
        return _parse_search_results(res.text, self.base_url)
    
    def detail(self, torrent_url: str) -> FullTorrent:
        """Fetches and parses a torrent detail page."""
        res = self.session.get(torrent_url)
        return _parse_torrent_page(res.text)