from thepiratebay_api.parsers import _parse_search_results, _parse_torrent_page
from thepiratebay_api.models import SearchResult, BriefTorrent, FullTorrent

BASE_URL = "https://thepiratebay10.info"


class TestParseSearchResults:

    def test_returns_search_result_type(self, search_html):
        result = _parse_search_results(search_html, BASE_URL, "search")
        assert isinstance(result, SearchResult)

    def test_returns_torrents(self, search_html):
        result = _parse_search_results(search_html, BASE_URL, "search")
        assert len(result.torrents) > 0

    def test_each_item_is_brief_torrent(self, search_html):
        result = _parse_search_results(search_html, BASE_URL, "search")
        assert all(isinstance(t, BriefTorrent) for t in result.torrents)

    def test_torrents_have_titles(self, search_html):
        result = _parse_search_results(search_html, BASE_URL, "search")
        assert all(t.title is not None for t in result.torrents)

    def test_torrents_have_magnet_links(self, search_html):
        result = _parse_search_results(search_html, BASE_URL, "search")
        torrents_with_magnets = [t for t in result.torrents if t.magnet_link]
        assert len(torrents_with_magnets) > 0
        assert all(t.magnet_link.startswith("magnet:?") for t in torrents_with_magnets)

    def test_torrent_ids_are_integers(self, search_html):
        result = _parse_search_results(search_html, BASE_URL, "search")
        ids = [t.torrent_id for t in result.torrents if t.torrent_id is not None]
        assert len(ids) > 0
        assert all(isinstance(i, int) for i in ids)

    def test_urls_start_with_base(self, search_html):
        result = _parse_search_results(search_html, BASE_URL, "search")
        urls = [t.url for t in result.torrents if t.url]
        assert all(u.startswith(BASE_URL) for u in urls)

    def test_seeders_and_leechers_are_integers(self, search_html):
        result = _parse_search_results(search_html, BASE_URL, "search")
        for t in result.torrents:
            if t.seeders is not None:
                assert isinstance(t.seeders, int)
            if t.leechers is not None:
                assert isinstance(t.leechers, int)

    def test_pagination_defaults(self, search_html):
        result = _parse_search_results(search_html, BASE_URL, "search")
        assert result.current_page >= 1
        assert result.page_count >= result.current_page

    def test_empty_html_returns_empty_result(self):
        result = _parse_search_results("<html></html>", BASE_URL, "search")
        assert result.torrents == []
        assert result.current_page == 1
        assert result.page_count == 1


class TestParseTorrentPage:

    def test_returns_full_torrent(self, torrent_vip_html):
        result = _parse_torrent_page(torrent_vip_html)
        assert isinstance(result, FullTorrent)

    def test_title_is_parsed(self, torrent_vip_html):
        result = _parse_torrent_page(torrent_vip_html)
        assert result.title is not None
        assert len(result.title) > 0

    def test_magnet_link_is_valid(self, torrent_vip_html):
        result = _parse_torrent_page(torrent_vip_html)
        assert result.magnet_link is not None
        assert result.magnet_link.startswith("magnet:?xt=urn:btih:")

    def test_vip_flag(self, torrent_vip_html):
        result = _parse_torrent_page(torrent_vip_html)
        assert result.is_vip is True
        assert result.is_trusted is False

    def test_regular_uploader_not_vip(self, torrent_regular_html):
        result = _parse_torrent_page(torrent_regular_html)
        assert result.is_vip is False
        assert result.is_trusted is False

    def test_size_is_present(self, torrent_vip_html):
        result = _parse_torrent_page(torrent_vip_html)
        assert result.size is not None

    def test_seeders_leechers_are_integers(self, torrent_vip_html):
        result = _parse_torrent_page(torrent_vip_html)
        if result.seeders is not None:
            assert isinstance(result.seeders, int)
        if result.leechers is not None:
            assert isinstance(result.leechers, int)

    def test_invalid_html_returns_none(self):
        result = _parse_torrent_page("<html><body>nothing here</body></html>")
        assert result is None
