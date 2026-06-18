from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import IntEnum
from typing import Any


class BaseTorrent(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    title: str | None = Field(
        default=None,
        description="Title of the torrent", 
    )
    category: str | None = Field(
        default=None,
        description="Category of the torrent",
    )
    size: str | None = Field(
        default=None,
        description="Total size of all files contained in the torrent",
    )
    seeders: int | None = Field(
        default=None,
        description="Number of users who have the entire torrent and are uploading it to others.",
    )
    leechers: int | None = Field(
        default=None,
        description="Number of peers currently downloading the torrent.",
    )
    magnet_link: str | None = Field(
        default=None,
        description="Magnet URI used to download or share the torrent.",
    )
    uploader: str | None = Field(
        default=None,
        description="Who uploaded this torrent?",
    )
    date: str | None = Field(
        default=None, 
        alias="date_uploaded"
    )


class BriefTorrent(BaseTorrent):
    """Holds the searched torrents info"""

    torrent_id: int | None = Field(
        default=None,
        description="Unique identifier of the torrent.",
    )
    url: str | None = Field(
        default=None,
        description="URL of the torrent's page.",
    )

    @field_validator("torrent_id", mode="before")
    @classmethod
    def parse_id(cls, v: Any):
        try:
            return int(v)
        except (ValueError, TypeError):
            return None


class FullTorrent(BaseTorrent):
    """Holds full information about a torrent on its particular page"""

    description: str | None = Field(
        default=None,
        description="Text description provided for the torrent.",
    )

    images: list[str] | None = Field(
        default=None,
        description="URLs of images found in description of the torrent.",
    )
    info_hash: str | None = Field(
        default=None,
        description="BitTorrent info hash that uniquely identifies the torrent.",
    )
    num_files: int | None = Field(
        default=None,
        alias="Files",
        description="Number of files contained in the torrent.",
    )
    is_vip: bool = Field(
        default=False,
        description="Whether the torrent is marked as VIP on the pirate bay.",
    )

    is_trusted: bool = Field(
        default=False,
        description="Whether the torrent is marked as trusted by the pirate bay.",
    )

    additional_info: dict[str, str] = Field(
        default_factory=dict,
        description="Additional metadata extracted from the torrent details page that differ from torrent page to torrent page and are not constant.",
    )


class SearchResult(BaseModel):
    """Holds all of searched torrents for a single page"""

    torrents: list[BriefTorrent]
    current_page: int = 1
    page_count: int = 1


class _Audio(IntEnum):
    ALL       = 100
    MUSIC     = 101
    AUDIOBOOKS= 102
    FLAC      = 104
    OTHER     = 105

class _Video(IntEnum):
    ALL         = 200
    MOVIES      = 201
    DVDRS       = 202
    CLIPS       = 204
    TV_SHOWS    = 205
    HD_MOVIES   = 207
    HD_TV_SHOW  = 208
    M3D         = 209
    UHD_MOVIES  = 211
    UHD_TV_SHOW = 212
    OTHER       = 299

class _Apps(IntEnum):
    ALL    = 300
    WIN    = 301
    MAC    = 302
    UNIX   = 303
    IOS    = 305
    ANDROID= 306

class _Games(IntEnum):
    ALL     = 400
    PC      = 401
    MAC     = 402
    PSX     = 403
    XBOX360 = 404
    WII     = 405
    HANDHEL = 406
    IOS     = 407
    ANDROID = 408
    OTHER   = 499

class _XXX(IntEnum):
    ALL     = 500
    MOVIES  = 501
    DVDR    = 502
    PICTURES= 503
    GAMES   = 504
    HD      = 505
    CLIPS   = 506
    UHD     = 507
    OTHER   = 599

class _Other(IntEnum):
    ALL      = 600
    EBOOKS   = 601
    COMICS   = 602
    PICTURES = 603
    COVERS   = 604
    OTHER    = 699

# Defaulting to ALL value of the subclass if it's not specified 
class CategoryMeta(type):
    def __getattribute__(cls, name):
        
        val = super().__getattribute__(name)

        if isinstance(val, type) and issubclass(val, IntEnum):
            class EnumProxy:
                def __getattr__(self, attr):
                    return getattr(val, attr)
        
                def __int__(self):
                    return int(val.ALL)
                
                def __eq__(self, other):
                    return val.ALL == other or int(val.ALL) == other
                
                def __repr__(self):
                    return repr(val.ALL)
                
                def __str__(self):
                    return str(val.ALL)

            return EnumProxy()
        
        return val

class Category(metaclass=CategoryMeta):
    ALL   = 0
    Audio = _Audio
    Video = _Video
    Apps  = _Apps
    Games = _Games
    Porn  = _XXX
    Other = _Other