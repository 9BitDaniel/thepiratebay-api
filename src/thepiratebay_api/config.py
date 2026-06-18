import re

BASE_URL = "https://thepiratebay10.info"
MIRROR_LIST = "https://piratebay-proxylist.com/"

DIRECT_IMAGE_PATTERN = re.compile(
    r'https?://[^\s<>"\']+\.(?:jpg|jpeg|png|gif|webp|bmp|tiff|avif|jfif)(?:\?[^\s<>"\']*)?',
    re.IGNORECASE,
)

IMAGE_PATH_PATTERN = re.compile(
    r'https?://[^\s<>"\']*(?:/image|/img|/photo|/pic|/upload|/media|/i)/[^\s<>"\']+',
    re.IGNORECASE,
)
