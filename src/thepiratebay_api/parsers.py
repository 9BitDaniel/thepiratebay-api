from bs4 import BeautifulSoup, Tag
import re
from .config import DIRECT_IMAGE_PATTERN, IMAGE_PATH_PATTERN
from typing import Dict, List, Any

def _parse_dl(dl: Tag | None) -> dict[str, str]:
    """Turns a <dl> into {label: value} pairs."""
    result = {}
    if not dl:
        return result
    dts = dl.find_all("dt")
    dds = dl.find_all("dd")
    for dt, dd in zip(dts, dds):
        key = dt.get_text(strip=True).rstrip(":")
        result[key] = dd.get_text(strip=True)
    return result

def _parse_row(row, base_url) -> dict[str, Any] | None:
    """Parses a single search result row into a dict."""

    # finds all the rows and checks if they have the expected number of cells (8) and don't contain header or "no results" cells
    cells = row.find_all("td")
    if len(cells) < 8:
        return None
    
    category_tag = cells[0].find("a")
    category = category_tag.get_text(strip=True) if category_tag else None

    name_tag = cells[1].find("a", href=re.compile(r"/torrent/"))
    if not name_tag:
        return None
    name = name_tag.get_text(strip=True)
    url = base_url + name_tag["href"] if name_tag["href"].startswith("/") else name_tag["href"]

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
    uploader_link = uploader_tag["href"] if uploader_tag else None
    if uploader_link and uploader_link.startswith("/"):
        uploader_link = base_url + uploader_link

    return {
        "title": name,
        "torrent_id": torrent_id,
        "url": url,
        "category": category,
        "time": time,
        "magnet_link": magnet_link,
        "size": size,
        "seeders": seeders,
        "leechers": leechers,
        "uploader": uploader,
        "uploader_link": uploader_link,
    }


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
    return {
        "description": text.strip() or None,
        "images": _extract_images_from_text(text),
    }


def _parse_search_results(html: str, base_url: str) -> list[dict[str, Any]]:
    """Parses the HTML of a search results page into a list of dicts."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", {"id": "searchResult"})
    if not table:
        return []
    rows = [
        tr for tr in table.find_all("tr")
        if not tr.find("th")
        and not tr.find("td", {"colspan": True})
    ]
    results = []
    for row in rows:
        item = _parse_row(row, base_url)
        if item:
            results.append(item)
    return results


def _parse_torrent_page(html: str) -> dict[str, Any] | None:
    """Parses a torrent page into a dict."""
    soup = BeautifulSoup(html, "lxml")
    detail_frame = soup.find("div", {"id": "detailsframe"})
    if not detail_frame:
        return None

    title_tag = detail_frame.find("h1", {"id": "title"})
    name = title_tag.get_text(strip=True) if title_tag else None

    col1 = detail_frame.find("dl", {"class": "col1"})
    col2 = detail_frame.find("dl", {"class": "col2"})
    col1_data = _parse_dl(col1)
    col2_data = _parse_dl(col2)

    category_tag = col1.find("a") if col1 else None
    category = category_tag.get_text(strip=True) if category_tag else None

    magnet_tag = detail_frame.find("a", href=re.compile(r"^magnet:"))
    magnet_link = magnet_tag["href"] if magnet_tag else None

    nfo_tag = detail_frame.find("div", {"class": "nfo"})
    pre_tag = nfo_tag.find("pre") if nfo_tag else None
    pre_data = _extract_pre_data(pre_tag)

    return {
        "title": name,
        "category": category,
        "size": col1_data.get("Size"),
        "date_uploaded": col2_data.get("Uploaded"),
        "uploader": col2_data.get("By"),
        "seeders": col2_data.get("Seeders"),
        "leechers": col2_data.get("Leechers"),
        "magnet_link": magnet_link,
        "description": pre_data["description"],
        "images": pre_data["images"],
    }
