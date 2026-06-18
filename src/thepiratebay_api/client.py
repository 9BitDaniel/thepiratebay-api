import httpx
from .config import BASE_URL, MIRROR_LIST
from .parsers import _parse_search_results, _parse_torrent_page, _parse_mirror_list
from .models import SearchResult, FullTorrent, MirrorList, Category
from .helpers import _check_mirrors

class TorrentClient:
    Category = Category
    def __init__(self, url: str = BASE_URL, **httpx_kwargs) -> None:
        self.base_url = url
        self.session = httpx.Client(**{"timeout": 10, **httpx_kwargs})

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self) -> str:
        return f"TorrentClient(base_url={self.base_url!r})"

    def close(self) -> None:
        """Closes the session."""
        self.session.close()

    def search(self, query: str, category: Category = Category.ALL, page: int = 1) -> SearchResult:
        """Search a specific page of what you want."""
        url = f"{self.base_url}/search/{query}/{page}/99/{category}"
        res = self.session.get(url)
        return _parse_search_results(res.text, self.base_url)

    def detail(self, torrent_url: str) -> FullTorrent:
        """Fetches and parses a torrent's page."""
        res = self.session.get(torrent_url)
        return _parse_torrent_page(res.text)

    def mirrors(self) -> MirrorList:
        """Fetches and parses the mirror list, use one of the mirrors as base url if the default fails."""
        res = self.session.get(MIRROR_LIST)
        urls = _parse_mirror_list(res.text)
        return _check_mirrors(urls, self.session)
