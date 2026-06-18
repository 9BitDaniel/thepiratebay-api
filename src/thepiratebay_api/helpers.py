import httpx
from .models import MirrorStatus, MirrorList


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


def _check_mirrors(urls: list[str], client: httpx.Client) -> MirrorList:
    """Checks all mirrors and returns a MirrorList."""
    return MirrorList(
        mirrors=[_check_mirror(url, client) for url in urls]
    )