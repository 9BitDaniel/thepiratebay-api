from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def search_html() -> str:
    return (FIXTURES / "search_results.html").read_text(encoding="utf-8")


@pytest.fixture
def torrent_vip_html() -> str:
    return (FIXTURES / "torrent_page_vip.html").read_text(encoding="utf-8")

@pytest.fixture
def torrent_regular_html() -> str:
    return (FIXTURES / "torrent_page_regular.html").read_text(encoding="utf-8")
