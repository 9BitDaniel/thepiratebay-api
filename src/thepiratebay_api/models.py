from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Any


class BaseTorrent(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    title: str | None = None
    category: str | None = None
    size: str | None = None
    seeders: int | None = None
    leechers: int | None = None
    magnet_link: str | None = None
    uploader: str | None = None
    date: str | None = Field(default=None, alias="date_uploaded")


class BriefTorrent(BaseTorrent):
    """Holds searched torrents info"""

    torrent_id: int | None = None
    url: str | None = None

    @field_validator("torrent_id", mode="before")
    @classmethod
    def parse_id(cls, v: Any):
        try:
            return int(v)
        except (ValueError, TypeError):
            return None


class FullTorrent(BaseTorrent):
    """Holds full information about a torrent on its particular page"""

    description: str | None = None
    images: list[str] | None = None
    info_hash: str | None = None
    num_files: int | None = Field(default=None, alias="Files")
    is_vip: bool = False
    is_trusted: bool = False
    additional_info: dict[str, str] = Field(default_factory=dict)


class SearchResult(BaseModel):
    """Holds all of searched torrents for a single page"""

    torrents: list[BriefTorrent]
    current_page: int = 1
    page_count: int = 1
