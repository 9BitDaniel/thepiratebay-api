import re

from bs4 import BeautifulSoup, Tag

from .config import DIRECT_IMAGE_PATTERN, IMAGE_PATH_PATTERN
from .models import BriefTorrent, FullTorrent, SearchResult


def _parse_dl(dl: Tag | None) -> dict[str, str]:
    """Turns a <dl> into {label: value} pairs."""
    result = {}
    if not dl:
        return result
    for dt in dl.find_all("dt"):
        key = dt.get_text(strip=True).rstrip(":")
        dd = dt.find_next_sibling("dd")
        if dd is None:
            continue

        value = dd.get_text(separator=" ", strip=True)
        if key == "Info Hash" and not value:
            next_node = dd.next_sibling
            if next_node and isinstance(next_node, str):
                value = next_node.strip()
        result[key] = value
    return result


def _parse_pagination(table) -> tuple[int, int]:
    """
    Extracts current page and total page count from the pagination row,
    since the pagination roww might exceed 30 and not show it isn't
    very accurate.
    """
    pagination_td = table.find("td", {"colspan": True})
    if not pagination_td:
        return 1, 1

    current_tag = pagination_td.find("b")
    try:
        current_page = int(current_tag.get_text(strip=True)) if current_tag else 1
    except ValueError:
        current_page = 1

    page_numbers = []
    for a in pagination_td.find_all("a", href=re.compile(r"/search/")):
        try:
            page_numbers.append(int(a.get_text(strip=True)))
        except ValueError:
            continue

    page_count = max(page_numbers) if page_numbers else current_page
    return current_page, page_count


def _parse_row(row, base_url) -> BriefTorrent | None:
    """Parses a single search result row into a dict."""

    # Finds all the rows and checks if number of cells is unusual
    cells = row.find_all("td")
    if len(cells) < 8:
        return None

    category_tag = cells[0].find("a")
    category = category_tag.get_text(strip=True) if category_tag else None

    name_tag = cells[1].find("a", href=re.compile(r"/torrent/"))
    if not name_tag:
        return None
    name = name_tag.get_text(strip=True)
    url = (
        base_url + name_tag["href"]
        if name_tag["href"].startswith("/")
        else name_tag["href"]
    )

    torrent_id_match = re.search(r"/torrent/(\d+)/", url)
    torrent_id = torrent_id_match.group(1) if torrent_id_match else ""

    # Date which the torrent was uploaded
    time = cells[2].get_text(strip=True)

    magnet_tag = cells[3].find("a", href=re.compile(r"^magnet:"))
    magnet_link = magnet_tag["href"] if magnet_tag else None

    size = cells[4].get_text(strip=True)
    seeders = cells[5].get_text(strip=True)
    leechers = cells[6].get_text(strip=True)

    uploader_tag = cells[7].find("a")
    uploader = uploader_tag.get_text(strip=True) if uploader_tag else "Anonymous"

    return BriefTorrent(
        title=name,
        torrent_id=torrent_id,
        url=url,
        category=category,
        date=time,
        magnet_link=magnet_link,
        size=size,
        seeders=seeders,
        leechers=leechers,
        uploader=uploader,
    )


def _extract_images_from_text(text: str) -> list[str]:
    """Seeks & extracts image URLs from plain text — direct file links and image-path links."""
    seen = set()
    images = []
    for pattern in (DIRECT_IMAGE_PATTERN, IMAGE_PATH_PATTERN):
        for url in pattern.findall(text):
            if url not in seen:
                images.append(url)
                seen.add(url)
    return images


def _extract_pre_data(pre_tag: Tag | None) -> dict[str, str | list[str] | None]:
    """Stores plain text description and extracts any image links found in it."""
    if not pre_tag:
        return {"description": None, "images": []}
    text = pre_tag.get_text(strip=False)
    extracted_images = _extract_images_from_text(text)

    return {
        "description": text.strip() or None,
        "images": extracted_images if extracted_images else None,
    }


def _parse_search_results(html: str, base_url: str) -> SearchResult:
    """Parses the HTML of a search results page into a search result."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", {"id": "searchResult"})
    if not table:
        return SearchResult(torrents=[])
    current_page, page_count = _parse_pagination(table)
    rows = [
        tr
        for tr in table.find_all("tr")
        if not tr.find("th") and not tr.find("td", {"colspan": True})
    ]
    results = []
    for row in rows:
        item = _parse_row(row, base_url)
        if item:
            results.append(item)
    return SearchResult(
        torrents=results, current_page=current_page, page_count=page_count
    )


def _parse_torrent_page(html: str) -> FullTorrent | None:
    """Parses a torrent page into a FullTorrent Model."""

    soup = BeautifulSoup(html, "lxml")
    detail_frame = soup.find("div", {"id": "detailsframe"})

    if not detail_frame:
        return None

    title_tag = detail_frame.find("h1", {"id": "title"})
    name = title_tag.get_text(strip=True) if title_tag else None

    col1 = detail_frame.find("dl", {"class": "col1"})
    col2 = detail_frame.find("dl", {"class": "col2"})

    raw_metadata = {}
    raw_metadata.update(_parse_dl(col1))
    raw_metadata.update(_parse_dl(col2))

    is_vip = False
    is_trusted = False
    # Checking if the uploader is vip or trusted
    if col2:
        dt = col2.find("dt", string=re.compile(r"By"))
        if dt:
            dd = dt.find_next_sibling("dd")
            if dd:
                if dd.find("img", alt="VIP"):
                    is_vip = True
                if dd.find("img", alt="Trusted"):
                    is_trusted = True

    category_tag = col1.find("a") if col1 else None
    category = category_tag.get_text(strip=True) if category_tag else None

    magnet_tag = detail_frame.find("a", href=re.compile(r"^magnet:"))
    magnet_link = magnet_tag["href"] if magnet_tag else None

    nfo_tag = detail_frame.find("div", {"class": "nfo"})
    pre_tag = nfo_tag.find("pre") if nfo_tag else None
    pre_data = _extract_pre_data(pre_tag)

    category = raw_metadata.pop("Type", None)
    size = raw_metadata.pop("Size", None)
    uploaded = raw_metadata.pop("Uploaded", None)
    uploader = raw_metadata.pop("By", None)
    seeders = raw_metadata.pop("Seeders", None)
    leechers = raw_metadata.pop("Leechers", None)
    info_hash = raw_metadata.pop("Info Hash", None)
    num_files = raw_metadata.pop("Files", None)
    # Keeping the metadata clean
    raw_metadata.pop("Comments", None)

    return FullTorrent(
        title=name,
        category=category,
        size=size,
        date_uploaded=uploaded,
        uploader=uploader,
        seeders=seeders,
        leechers=leechers,
        magnet_link=magnet_link,
        description=pre_data["description"],
        images=pre_data["images"],
        info_hash=info_hash,
        Files=num_files,
        is_trusted=is_trusted,
        is_vip=is_vip,
        additional_info=raw_metadata,
    )


def _parse_mirror_list(html: str) -> list[str]:
    """Parses the mirror list page into a list of URLs."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", {"id": "searchResult"})
    if not table:
        return []

    urls = []
    for tr in table.find_all("tr"):
        td = tr.find("td", class_="site")
        if not td:
            continue
        a = td.find("a", href=True)
        if not a:
            continue
        url = a["href"].strip()
        if url:
            urls.append(url)

    return urls
