from urllib.parse import quote

import httpx

from .models import MirrorList, MirrorStatus


def _check_mirror(url: str, client: httpx.Client) -> MirrorStatus:
    """Checks a single mirror URL and returns its status."""
    try:
        res = client.get(url, follow_redirects=True)
        return MirrorStatus(
            url=url,
            status_code=res.status_code,
            is_alive=res.status_code < 400,
        )
    except httpx.TimeoutException:
        return MirrorStatus(url=url, status_code=None, is_alive=False)
    except httpx.RequestError:
        return MirrorStatus(url=url, status_code=None, is_alive=False)


def check_mirrors(urls: list[str], client: httpx.Client) -> MirrorList:
    """Checks all mirrors and returns a MirrorList."""
    return MirrorList(mirrors=[_check_mirror(url, client) for url in urls])


def sanitize_search_query(query: str) -> str:
    """Checks if there's no traversal bugs and percent-encodes the query."""
    if not query:
        return ""

    query = query.strip()
    # Fixes traversal bugs
    cleaned = query.replace("/", " ")

    return quote(cleaned, safe="")


def build_detail_url(base_url: str, torrent_id: int | str) -> str:
    """Return a valid URL to the torrent's page"""
    clean_id = int(torrent_id)

    base = httpx.URL(base_url)
    return str(base.join(f"/torrent/{clean_id}"))
