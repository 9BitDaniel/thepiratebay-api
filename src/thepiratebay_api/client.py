import httpx

from .config import BASE_URL, MIRROR_LIST_URL
from .helpers import _build_detail_url, _check_mirrors, _sanitize_search_query
from .models import Category, SortBy, FullTorrent, MirrorList, SearchResult
from .parsers import _parse_mirror_list, _parse_search_results, _parse_torrent_page


class TorrentClient:
    Category = Category
    SortBy = SortBy
    def __init__(
        self,
        url: str = BASE_URL,
        **httpx_kwargs,
    ) -> None:
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

    def search(
        self,
        query: str,
        category: Category = Category.ALL,
        sort_by: SortBy = SortBy.RELEVANCE,
        page: int = 1,
    ) -> SearchResult:
        """Search a specific page of what you want."""
        query = _sanitize_search_query(query)
        url = f"{self.base_url}/search/{query}/{page}/{sort_by}/{category}"
        res = self.session.get(url)
        return _parse_search_results(res.text, self.base_url, pattern="search")

    def detail(
        self,
        torrent_id: str | int,
    ) -> FullTorrent:
        """Fetches and parses a torrent's page."""
        url = _build_detail_url(self.base_url, torrent_id)
        res = self.session.get(url)
        return _parse_torrent_page(res.text)

    def mirrors(self) -> MirrorList:
        """Fetches and parses the mirror list, use one of the mirrors as base url if the default fails."""
        res = self.session.get(MIRROR_LIST_URL)
        urls = _parse_mirror_list(res.text)
        return _check_mirrors(urls, self.session)

    def top(
        self,
        category: Category,
    ) -> SearchResult:
        """Returns the SearchResult for top torrents of a category."""
        url = f"{self.base_url}/top/{category}"
        res = self.session.get(url)
        return _parse_search_results(res.text, self.base_url, pattern="top")
    def browse(
        self,
        category: Category,
        sort_by: SortBy = SortBy.RELEVANCE,
        page: int = 1,
    ) -> SearchResult:
        """Browses a category of torrents & returns the SearchResult."""
        url = f"{self.base_url}/browse/{category}/{page}/{sort_by}"
        res = self.session.get(url)
        return _parse_search_results(res.text, self.base_url, pattern="browse")
    def recent(
        self,
        page: int = 1,
    ) -> SearchResult:
        """Returns the SearchResult for recent torrents."""
        url = f"{self.base_url}/recent/{page}"
        res = self.session.get(url)
        return _parse_search_results(res.text, self.base_url, pattern="recent")
