# thepiratebay-api

[![codecov](https://codecov.io/github/9BitDaniel/thepiratebay-api/graph/badge.svg?token=ZEHPPXOGP6)](https://github.com/9BitDaniel/thepiratebay-api)

An unofficial Python API wrapper for The Pirate Bay.

>**Beta** — Please [open an issue](https://github.com/9BitDaniel/thepiratebay-api/issues) if something's not working.

## Installation

```bash
pip install thepiratebay-api
```
```bash
uv add thepiratebay-api
```

Or directly from GitHub:

```bash
pip install git+https://github.com/9BitDaniel/thepiratebay-api.git
```
```bash
uv add git+https://github.com/9BitDaniel/thepiratebay-api.git
```

## Quick Start

```python
from thepiratebay_api import TorrentClient

with TorrentClient() as client:
    results = client.search("ubuntu")

    for torrent in results.torrents:
        print(torrent.title, torrent.seeders)
```

## Usage

### Search

```python
# Basic search
results = client.search("ubuntu")

# With category
results = client.search("Tenet", category=TorrentClient.Category.Video.HD_MOVIES)

# With pagination
results = client.search("ubuntu", page=2)

print(f"Page {results.current_page} of {results.page_count}")
```

## Working with Results

All results are [Pydantic](https://docs.pydantic.dev) models, so you can serialize them however you need:

```python
results = client.search("Bomber Mafia")

# Convert to dict
results.model_dump()

# Convert to JSON string
results.model_dump_json()

# Individual torrent
torrent = results.torrents[0]
torrent.model_dump()
torrent.model_dump_json()

# Full torrent details
details = client.detail(torrent.torrent_id)
details.model_dump()
details.model_dump_json()
```


### Categories
You could use all the major categories found in The Pirate Bay along with some of the sub categories
```python
TorrentClient.Category.ALL

TorrentClient.Category.Audio.MUSIC
TorrentClient.Category.Audio.FLAC
TorrentClient.Category.Audio.AUDIOBOOKS

TorrentClient.Category.Video.MOVIES
TorrentClient.Category.Video.TV_SHOWS
TorrentClient.Category.Video.HD_MOVIES
TorrentClient.Category.Video.HD_TV_SHOW
TorrentClient.Category.Video.UHD_MOVIES

TorrentClient.Category.Games.PC
TorrentClient.Category.Apps.WIN
TorrentClient.Category.Other.EBOOKS
```

### Torrent Details

```python
# Pass a torrent ID from search results
details = client.detail(torrent.torrent_id)

print(details.title)
print(details.size)
print(details.seeders)
print(details.magnet_link)
print(details.info_hash)
print(details.num_files)
print(details.uploader)
print(details.is_vip)
print(details.is_trusted)
print(details.description)
print(details.images)         # image URLs found in the description
print(details.additional_info) # extra metadata that differ across torrents
```

### Browse & Discover

```python
# Browse a category (category has to be specified)
results = client.browse(TorrentClient.Category.Video.HD_MOVIES)

# Top torrents in a category (category has to be specified)
results = client.top(TorrentClient.Category.Audio.MUSIC)

# Recently uploaded torrents
results = client.recent()
results = client.recent(page=2)
```

### Mirror Sites

If the default URL is blocked or unreachable:

```python
mirrors = client.mirrors()
alive = mirrors.alive  # only working mirrors

if alive:
    client = TorrentClient(url=alive[0].url)
```

### Custom HTTP Options

Any keyword argument is passed directly to `httpx.Client`:

```python
# Custom timeout
client = TorrentClient(timeout=30)

# Custom headers
client = TorrentClient(headers={"User-Agent": "Mozilla/5.0"})

# Through a proxy
client = TorrentClient(proxy="http://localhost:8080")

# Custom mirror as base URL
client = TorrentClient(url="https://thepiratebay.bond")
```

## Requirements

- Python 3.10+
- httpx
- beautifulsoup4
- lxml
- pydantic

## Contributing

Contributions are welcome

## License

This project is licensed under the [MIT License](LICENSE).
