import pytest
from thepiratebay_api.helpers import _sanitize_search_query, _build_detail_url


class TestSanitizeSearchQuery:

    def test_basic_query(self):
        result = _sanitize_search_query("ubuntu")
        assert result == "ubuntu"

    def test_spaces_are_encoded(self):
        result = _sanitize_search_query("lord of the rings")
        assert " " not in result

    def test_slash_is_replaced(self):
        # Forward slashes should not break the URL path
        result = _sanitize_search_query("AC/DC")
        assert "/" not in result

    def test_special_characters_encoded(self):
        result = _sanitize_search_query("it's alive")
        assert "'" not in result

    def test_strips_whitespace(self):
        result = _sanitize_search_query("  ubuntu  ")
        assert result == _sanitize_search_query("ubuntu")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            _sanitize_search_query("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            _sanitize_search_query("   ")


class TestBuildDetailUrl:

    def test_builds_correct_url(self):
        url = _build_detail_url("https://thepiratebay10.info", 443495)
        assert url == "https://thepiratebay10.info/torrent/443495"

    def test_accepts_string_id(self):
        url = _build_detail_url("https://thepiratebay10.info", "6902184")
        assert "6902184" in url

    def test_rejects_non_numeric_id(self):
        with pytest.raises((ValueError, TypeError)):
            _build_detail_url("https://thepiratebay10.info", "notanid")

    def test_trailing_slash_on_base(self):
        # should work regardless of trailing slash
        url = _build_detail_url("https://thepiratebay10.info/", 443495)
        assert "torrent/443495" in url
