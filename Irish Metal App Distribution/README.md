# Irish Metal Archive Search App

A simple Python application to search and explore Irish metal bands from [irishmetalarchive.com](https://irishmetalarchive.com/).

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   python irish_metal_app.py
   ```

## Features

- 🔍 **Search for bands** by name
- 📚 **Browse all bands** in the archive
- 📋 **Get detailed information** about bands
- 🎸 **Interactive menu** for easy navigation

## Usage

The app provides an interactive menu with the following options:

1. **Search for bands** - Enter a band name to find matching Irish metal bands
2. **Browse all bands** - View the complete list of bands in the archive
3. **Get band details** - Get detailed information about a specific band
4. **Exit** - Close the application

## Requirements

- Python 3.6+
- `requests` library
- `pyquery` library (optional, basic HTML parsing used as fallback)

## Example

```
🎸============================================================🤘
      IRISH METAL ARCHIVE SEARCH APP
      Search and explore Irish metal bands
🤘============================================================🎸

🌐 Testing connection to Irish Metal Archive...
✅ Connected successfully!

📋 MENU:
1. Search for bands
2. Browse all bands
3. Get band details
4. Exit
```

## About

This app scrapes data from the Irish Metal Archive to provide an easy way to discover and learn about Irish metal bands. It's a standalone Python script that requires no complex setup.

## Install

`pip install python-metallum`

## Usage

Artist search

```python
import metallum


# Search bands matching term
bands = metallum.band_search('metallica')
# -> [<SearchResult: Metallica | Thrash Metal (early), Hard Rock/Heavy/Thrash Metal (later) | United States>]

bands[0].name
# -> 'Metallica'

# Fetch band page
band = bands[0].get()

# Get all albums
band.albums
# -> [<Album: No Life 'til Leather (Demo)>, <Album: Kill 'Em All (Full-length)>, ...]

# Get only full-length albums
full_length = band.albums.search(type=metallum.AlbumTypes.FULL_LENGTH)
# -> [<Album: Kill 'Em All (Full-length)>, <Album: Ride the Lightning (Full-length)>, <Album: Master of Puppets (Full-length)>, <Album: ...and Justice for All (Full-length)>, <Album: Metallica (Full-length)>, <Album: Load (Full-length)>, <Album: ReLoad (Full-length)>, <Album: Garage Inc. (Full-length)>, <Album: St. Anger (Full-length)>, <Album: Death Magnetic (Full-length)>, <Album: Hardwired... to Self-Destruct (Full-length)>]

album = full_length[2]
album.title
# -> 'Master of Puppets'

album.date
# -> datetime.datetime(1986, 3, 3, 0, 0)

# Get all tracks
album.tracks
# -> [<Track: Battery (313)>, <Track: Master of Puppets (516)>, <Track: The Thing That Should Not Be (397)>, <Track: Welcome Home (Sanitarium) (388)>, <Track: Disposable Heroes (497)>, <Track: Leper Messiah (341)>, <Track: Orion (508)>, <Track: Damage, Inc. (330)>]
```

Album search

```python
import metallum

# Search albums matching term
metallum.album_search('seventh')
# -> []

# Search albums containing term
metallum.album_search('seventh', strict=False)
# -> [<SearchResult: Beherit | Seventh Blasphemy | Demo>, <SearchResult: Black Sabbath | Seventh Star | Full-length>, ...]

# Search albums by band
metallum.album_search('seventh', band='iron maiden', strict=False)
# -> [<SearchResult: Iron Maiden | Seventh Son of a Seventh Son | Full-length>]

```

Refer to source and doctests for detailed usage

