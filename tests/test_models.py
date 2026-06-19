from thepiratebay_api.models import BriefTorrent, Category


class TestBriefTorrentValidator:

    def test_string_id_coerced_to_int(self):
        t = BriefTorrent(title="test", torrent_id="12345")
        assert t.torrent_id == 12345
        assert isinstance(t.torrent_id, int)

    def test_invalid_id_becomes_none(self):
        t = BriefTorrent(title="test", torrent_id="notanid")
        assert t.torrent_id is None

    def test_whitespace_stripped(self):
        t = BriefTorrent(title="  test title  ")
        assert t.title == "test title"


class TestCategory:

    def test_all_is_zero(self):
        assert int(Category.ALL) == 0

    def test_video_hd_movies(self):
        assert int(Category.Video.HD_MOVIES) == 207

    def test_audio_music(self):
        assert int(Category.Audio.MUSIC) == 101

    def test_video_proxy_gives_all(self):
        assert int(Category.Video) == 200
