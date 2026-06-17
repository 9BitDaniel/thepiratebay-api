from pydantic import BaseModel, Field, ConfigDict, field_validator


class BaseTorrent(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    title: str | None = None
    category: str | None = None
    size: str | None = None
    seeders: int | None = None
    leechers: int | None = None
    magnet_link: str | None = None
    uploader: str | None = None


class BriefTorrent(BaseTorrent):
    torrent_id : int | None = None
    url : str | None = None
    date : str | None = None

    @field_validator("torrent_id", mode="before")
    @classmethod
    def parse_id(cls, v):
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

class FullTorrent(BaseTorrent):
    description: str | None = None
    images: list[str] | None = None
    date: str | None = Field(default=None, alias="date_uploaded")

class SearchResult(BaseModel):
    torrents: list[BriefTorrent]
    current_page: int = 1
    page_count: int = 1