import httpx

from .config import BASE_URL, MIRROR_LIST
from .helpers import build_detail_url, check_mirrors, sanitize_search_query
from .models import Category, FullTorrent, MirrorList, SearchResult
from .parsers import _parse_mirror_list, _parse_search_results, _parse_torrent_page


class TorrentClient:
    Category = Category

    def __init__(
        self,
        url: str = BASE_URL,
        **httpx_kwargs,
    ) -> None:
        self.base_url = url
        self.session = httpx.Client(**{"timeout": 10, **httpx_kwargs})

    def __enter__(self):
        return self

    def __exit__(self,*args):
        self.close()

    def __repr__(self) -> str:
        return f"TorrentClient(base_url={self.base_url!r})"

    def close(self) -> None:
        """Closes the session."""
        self.session.close()

    def search(
        self,
        query: str,
        category: Category = Category.ALL,
        page: int = 1,
    ) -> SearchResult:
        """Search a specific page of what you want."""
        query = sanitize_search_query(query)
        url = f"{self.base_url}/search/{query}/{page}/99/{category}"
        res = self.session.get(url)
        return _parse_search_results(res.text, self.base_url)

    def detail(
        self,
        torrent_id: str | int,
    ) -> FullTorrent:
        """Fetches and parses a torrent's page."""
        url = build_detail_url(self.base_url, torrent_id)
        res = self.session.get(url)
        return _parse_torrent_page(res.text)

    def mirrors(self) -> MirrorList:
        """Fetches and parses the mirror list, use one of the mirrors as base url if the default fails."""
        res = self.session.get(MIRROR_LIST)
        urls = _parse_mirror_list(res.text)
        return check_mirrors(urls, self.session)

    def browse(
        self,
        category: Category,
        page: int = 1,
    ) -> None: ...
    def top(
        self,
        category: Category,
        page: int = 1,
    ) -> None: ...
    def recent(
        self,
        category: Category,
        page: int = 1,
    ) -> None: ...
