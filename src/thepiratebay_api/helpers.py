from urllib.parse import quote

import httpx

from .models import MirrorList, MirrorStatus
from .parsers import _parse_search_results

def _check_mirror(url: str, client: httpx.Client) -> MirrorStatus:
    """Checks a mirror by executing a test query and parsing the results."""
    try:
        test_url = f"{url.rstrip('/')}/search/ubuntu/1/99/0"
        res = client.get(test_url, follow_redirects=True)
        
        is_functional = False
        if res.status_code == 200:
            # Double check if the mirror has the same html structure
            result = _parse_search_results(res.text, url, pattern="search")
            if len(result.torrents) > 0:
                is_functional = True
                
        return MirrorStatus(
            url=url,
            status_code=res.status_code,
            is_alive=is_functional,
        )
    except Exception:
        return MirrorStatus(url=url, status_code=None, is_alive=False)


def _check_mirrors(urls: list[str], client: httpx.Client) -> MirrorList:
    """Checks all mirrors and returns a MirrorList."""
    return MirrorList(mirrors=[_check_mirror(url, client) for url in urls])


def _sanitize_search_query(query: str) -> str:
    """Checks if there's no traversal bugs and percent-encodes the query."""
    query = query.strip()
    if not query:
        raise ValueError("Search query cannot be empty.")
    # Fixes traversal bugs
    cleaned = query.replace("/", " ")

    return quote(cleaned, safe="")


def _build_detail_url(base_url: str, torrent_id: int | str) -> str:
    """Return a valid URL to the torrent's page"""
    clean_id = int(torrent_id)

    base = httpx.URL(base_url)
    return str(base.join(f"/torrent/{clean_id}"))
