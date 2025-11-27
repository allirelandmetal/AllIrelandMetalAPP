#!/usr/bin/env python3
"""
The All Ireland Metal Project -  Irish Metal Archive Search App
A standalone Python application to search and explore Irish metal bands via an API to the Irish Metal Archive website.

Build on top of python-metallum: https://github.com/lcharlick/python-metallum

This application allows users to search for Irish metal bands, view band details, and explore album releases using data sourced from the Irish Metal Archive website only. 

Usage: python irish_metal_app.py or python3 irish_metal_app.py
"""

import requests
import ssl
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import time
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import json
import sys

# Disable SSL warnings for our simple app
urllib3.disable_warnings(InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = 'https://irishmetalarchive.com'

@dataclass
class Band:
    """Represents an Irish metal band"""
    name: str
    genre: str = ""
    county: str = ""
    url: str = ""
    year_formed: str = ""
    status: str = ""
    description: str = ""
    members: List[str] = field(default_factory=list)
    albums: List['Release'] = field(default_factory=list)

@dataclass
class Release:
    """Represents a band's release"""
    title: str
    band: str
    genre: str = ""
    year: str = ""
    type: str = ""
    url: str = ""
    description: str = ""

class IrishMetalArchive:
    """Main class for searching the Irish Metal Archive"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        self.session.verify = False
        self.last_request_time = 0
        self.min_delay = 1.0
    
    def _wait_between_requests(self):
        """Add delay between requests to be respectful"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _get_page(self, url):
        """Get a web page with error handling"""
        try:
            self._wait_between_requests()
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                # Try to import PyQuery, fallback to basic parsing if not available
                try:
                    from pyquery import PyQuery
                    return PyQuery(response.text)
                except ImportError:
                    # Fallback to basic text parsing if PyQuery not available
                    return response.text
            else:
                print(f"❌ HTTP Error {response.status_code} for {url}")
                return None
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def get_all_bands(self):
        """Get all bands from the artists page"""
        print("🔍 Fetching all Irish metal bands...")
        bands = []
        
        url = f"{BASE_URL}/artists"
        page = self._get_page(url)
        
        if page is None:
            return bands
        
        try:
            # Check if we have PyQuery object or just text
            if hasattr(page, 'find'):
                # PyQuery object
                artist_links = page('a[href*="/artist/"]')
                for link in artist_links:
                    link_elem = page(link)
                    band_name = link_elem.text().strip()
                    band_url = link_elem.attr('href')
                    if band_name and band_url:
                        bands.append(Band(
                            name=band_name,
                            url=band_url if band_url.startswith('http') else BASE_URL + band_url
                        ))
            else:
                # Fallback text parsing
                import re
                # Look for artist links in the HTML
                pattern = r'<a[^>]*href="(/artist/[^"]*)"[^>]*>([^<]+)</a>'
                matches = re.findall(pattern, page)
                for url_part, band_name in matches:
                    bands.append(Band(
                        name=band_name.strip(),
                        url=BASE_URL + url_part
                    ))
        
        except Exception as e:
            print(f"❌ Error parsing bands: {e}")
        
        return bands
    
    def search_bands(self, search_term):
        """Search for bands by name using the website's search function"""
        print(f"🔍 Searching for bands matching: '{search_term}'")
        
        # Use the website's built-in search
        search_url = f"{BASE_URL}/?s={search_term}"
        page = self._get_page(search_url)
        
        if page is None:
            print("❌ Could not access search results")
            return []
        
        bands = []
        try:
            # Check if we have PyQuery object or just text
            if hasattr(page, 'find') and callable(page):
                # PyQuery object - use PyQuery methods
                artist_links = page('a[href*="/artists/"]')
                
                for link in artist_links:
                    link_elem = page(link)
                    band_name = link_elem.text().strip()
                    band_url = link_elem.attr('href')
                    
                    if band_name and band_url and band_name.lower() != 'artists':
                        # Avoid duplicates
                        if not any(b.name.lower() == band_name.lower() for b in bands):
                            band = Band(
                                name=band_name,
                                url=band_url
                            )
                            bands.append(band)
            else:
                # Fallback to regex parsing for plain text
                import re
                html_content = str(page)
                
                # Look for artist links in the HTML
                artist_pattern = r'<a[^>]*href="([^"]*\/artists\/[^"]*)"[^>]*>([^<]+)</a>'
                matches = re.findall(artist_pattern, html_content)
                
                for url, band_name in matches:
                    band_name = band_name.strip()
                    if band_name and band_name.lower() != 'artists':
                        # Make sure URL is complete
                        if not url.startswith('http'):
                            url = BASE_URL + url if url.startswith('/') else BASE_URL + '/' + url
                        
                        # Avoid duplicates
                        if not any(b.name.lower() == band_name.lower() for b in bands):
                            band = Band(
                                name=band_name,
                                url=url
                            )
                            bands.append(band)
            
            # Also look for any other potential band mentions in the search results (only if PyQuery available)
            if hasattr(page, 'find') and callable(page):
                # Check for headings or titles that might contain band names
                headings = page('h1, h2, h3, h4, .entry-title, .post-title')
                for heading in headings:
                    heading_elem = page(heading)
                    heading_text = heading_elem.text().strip()
                    
                    # If this heading contains our search term and links to an artist page
                    if (search_term.lower() in heading_text.lower() and 
                        heading_text.lower() != search_term.lower()):
                        
                        # Look for links in or near this heading
                        heading_links = heading_elem.find('a[href*="/artists/"]')
                        if not heading_links:
                            heading_links = heading_elem.siblings().find('a[href*="/artists/"]')
                        
                        for link in heading_links:
                            link_elem = page(link)
                            band_url = link_elem.attr('href')
                            if band_url:
                                band_name = link_elem.text().strip() or heading_text
                                if not any(b.name.lower() == band_name.lower() for b in bands):
                                    band = Band(
                                        name=band_name,
                                        url=band_url
                                    )
                                    bands.append(band)
            
            # If no structured results found, try searching the raw HTML content
            if not bands:
                html_content = str(page)
                
                # Look for artist URLs in the HTML
                import re
                artist_url_pattern = r'href="(https://irishmetalarchive\.com/artists/[^"]+)"'
                urls = re.findall(artist_url_pattern, html_content)
                
                for url in urls:
                    # Extract band name from URL - more sophisticated extraction
                    url_parts = url.split('/artists/')[-1].replace('/', '')
                    
                    # Convert URL slug to proper band name
                    band_name = url_parts.replace('-', ' ').title()
                    
                    # Skip generic pages
                    if band_name.lower() in ['feed', 'page', 'category']:
                        continue
                    
                    # Check if this might be our search term
                    if search_term.lower() in band_name.lower():
                        if not any(b.name.lower() == band_name.lower() for b in bands):
                            band = Band(
                                name=band_name,
                                url=url
                            )
                            bands.append(band)
            
            # Final fallback: if still no bands found, try to extract from any content
            if not bands:
                # Look for the search term in the page and try to find associated artist links
                if hasattr(page, 'text') and callable(page.text):
                    text_content = page.text()
                else:
                    text_content = str(page)
                    
                if search_term.lower() in text_content.lower():
                    # Try to find all artist URLs and add them with names extracted from URLs
                    all_artist_links = re.findall(r'href="(https://irishmetalarchive\.com/artists/[^"]+)"', html_content)
                    
                    for url in set(all_artist_links):  # Remove duplicates
                        url_parts = url.split('/artists/')[-1].replace('/', '')
                        if url_parts and url_parts not in ['feed', 'page', 'category']:
                            band_name = url_parts.replace('-', ' ').title()
                            
                            band = Band(
                                name=band_name,
                                url=url
                            )
                            bands.append(band)
                            
                            # Limit to reasonable number of results
                            if len(bands) >= 10:
                                break
            
        except Exception as e:
            print(f"❌ Error parsing search results: {e}")
        
        return bands
    
    def search_albums(self, search_term, band_filter=None):
        """Search for albums/releases by name with optional band filtering"""
        if band_filter:
            print(f"🔍 Searching for albums by '{band_filter}' matching: '{search_term}'")
        else:
            print(f"🔍 Searching for albums matching: '{search_term}'")
        
        albums = []
        
        # Strategy 1: Search using website's search function
        albums.extend(self._search_albums_general(search_term, band_filter))
        
        # Strategy 2: Search specific release categories
        if len(albums) < 5:  # If we don't have many results, try more specific searches
            albums.extend(self._search_albums_by_category(search_term, band_filter))
        
        # Strategy 3: If still limited results, try broader searches
        if len(albums) < 3 and not band_filter:
            albums.extend(self._search_albums_partial_match(search_term))
        
        # Remove duplicates and sort by relevance
        albums = self._deduplicate_albums(albums, search_term)
        
        return albums[:20]  # Limit to top 20 results
    
    def _search_albums_general(self, search_term, band_filter=None):
        """General album search using website search"""
        search_url = f"{BASE_URL}/?s={search_term}"
        if band_filter:
            search_url += f"+{band_filter}"
            
        page = self._get_page(search_url)
        if page is None:
            return []
        
        albums = []
        try:
            # Check if we have PyQuery object or just text
            if hasattr(page, 'find') and callable(page):
                # PyQuery object - use PyQuery methods
                release_links = page('a[href*="/releases/"], a[href*="/album/"], a[href*="/ep/"], a[href*="/demo/"], a[href*="/single/"]')
                
                for link in release_links:
                    album = self._extract_album_from_pyquery_link(page, link, band_filter)
                    if album:
                        albums.append(album)
                        
                # Also look in article content and post titles
                content_links = page('article a, .post a, .entry-content a, h1 a, h2 a, h3 a')
                for link in content_links:
                    album = self._extract_album_from_pyquery_link(page, link, band_filter)
                    if album and album.url and any(keyword in album.url for keyword in ['/releases/', '/album/', '/ep/', '/demo/', '/single/']):
                        albums.append(album)
            else:
                # Fallback to regex parsing for plain text
                albums.extend(self._extract_albums_from_html(str(page), band_filter))
                
        except Exception as e:
            print(f"❌ Error in general album search: {e}")
        
        return albums
    
    def _search_albums_by_category(self, search_term, band_filter=None):
        """Search albums by specific categories (albums, EPs, demos, etc.)"""
        albums = []
        categories = ['albums', 'releases', 'discography']
        
        for category in categories:
            try:
                search_url = f"{BASE_URL}/{category}/?s={search_term}"
                if band_filter:
                    search_url += f"+{band_filter}"
                    
                page = self._get_page(search_url)
                if page is None:
                    continue
                
                if hasattr(page, 'find') and callable(page):
                    # Look for release links in category pages
                    links = page('a[href*="/releases/"], a[href*="/album/"], a[href*="/ep/"], a[href*="/demo/"]')
                    for link in links:
                        album = self._extract_album_from_pyquery_link(page, link, band_filter)
                        if album:
                            albums.append(album)
                else:
                    albums.extend(self._extract_albums_from_html(str(page), band_filter))
                    
            except Exception as e:
                print(f"❌ Error searching {category}: {e}")
                
        return albums
    
    def _search_albums_partial_match(self, search_term):
        """Search for albums using partial matching techniques"""
        albums = []
        
        # Try searching for individual words from the search term
        words = search_term.split()
        if len(words) > 1:
            for word in words:
                if len(word) > 3:  # Only search meaningful words
                    partial_results = self._search_albums_general(word)
                    # Filter results that contain the original search term
                    for album in partial_results:
                        if search_term.lower() in album.title.lower():
                            albums.append(album)
                            
        return albums
    
    def _extract_album_from_pyquery_link(self, page, link, band_filter=None):
        """Extract album information from a PyQuery link element"""
        try:
            link_elem = page(link)
            album_title = link_elem.text().strip()
            album_url = link_elem.attr('href')
            
            if not album_title or not album_url:
                return None
                
            # Skip if this doesn't look like a release URL
            if not any(keyword in album_url for keyword in ['/releases/', '/album/', '/ep/', '/demo/', '/single/']):
                return None
            
            # Try to extract band name from context
            band_name = ""
            
            # Look in parent elements for band information
            parent = link_elem.parent()
            context_text = ""
            
            # Try multiple parent levels to find context
            for _ in range(3):
                if parent and hasattr(parent, 'text'):
                    context_text = parent.text()
                    if context_text and len(context_text) > len(album_title):
                        break
                    parent = parent.parent() if hasattr(parent, 'parent') else None
                else:
                    break
            
            # Extract band name using various patterns
            import re
            band_patterns = [
                r'by\s+([^-\n\|•]+?)(?:\s*[-\|•]|\s*\d{4}|\s*$)',
                r'([^-\n\|•]+?)\s*[-\|•]\s*' + re.escape(album_title),
                r'^([^-\n\|•]+?)\s*[-\|•]',
            ]
            
            for pattern in band_patterns:
                match = re.search(pattern, context_text, re.IGNORECASE | re.MULTILINE)
                if match:
                    potential_band = match.group(1).strip()
                    # Clean up the band name
                    potential_band = re.sub(r'\s*\([^)]*\)', '', potential_band)  # Remove parentheses
                    potential_band = re.sub(r'\s+', ' ', potential_band)  # Normalize whitespace
                    if len(potential_band) > 1 and potential_band.lower() != album_title.lower():
                        band_name = potential_band
                        break
            
            # Apply band filter if specified
            if band_filter and band_name:
                if band_filter.lower() not in band_name.lower():
                    return None
            
            # Extract additional metadata
            album_type = self._extract_album_type(album_url, context_text)
            year = self._extract_year(context_text)
            genre = self._extract_genre(context_text)
            
            # Make sure URL is complete
            if not album_url.startswith('http'):
                album_url = BASE_URL + album_url if album_url.startswith('/') else BASE_URL + '/' + album_url
            
            return Release(
                title=album_title,
                band=band_name,
                type=album_type,
                year=year,
                genre=genre,
                url=album_url
            )
            
        except Exception as e:
            return None
    
    def _extract_albums_from_html(self, html_content, band_filter=None):
        """Extract albums from raw HTML using regex patterns"""
        albums = []
        import re
        
        # Enhanced patterns for different link types
        patterns = [
            r'<a[^>]*href="([^"]*\/(?:releases|album|ep|demo|single)\/[^"]*)"[^>]*>([^<]+)</a>',
            r'href="([^"]*\/(?:releases|album|ep|demo|single)\/[^"]*)"[^>]*>.*?([^<]+?)(?:</a>|<)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            for url, title in matches:
                title = re.sub(r'<[^>]+>', '', title).strip()  # Remove any remaining HTML
                if not title or len(title) < 2:
                    continue
                    
                # Extract context around the match for band name extraction
                match_pos = html_content.find(url)
                if match_pos != -1:
                    context_start = max(0, match_pos - 200)
                    context_end = min(len(html_content), match_pos + 200)
                    context = html_content[context_start:context_end]
                    
                    # Extract band name from context
                    band_name = self._extract_band_from_context(context, title)
                    
                    # Apply band filter
                    if band_filter and band_name:
                        if band_filter.lower() not in band_name.lower():
                            continue
                    
                    # Extract metadata
                    album_type = self._extract_album_type(url, context)
                    year = self._extract_year(context)
                    genre = self._extract_genre(context)
                    
                    # Make sure URL is complete
                    if not url.startswith('http'):
                        url = BASE_URL + url if url.startswith('/') else BASE_URL + '/' + url
                    
                    albums.append(Release(
                        title=title,
                        band=band_name,
                        type=album_type,
                        year=year,
                        genre=genre,
                        url=url
                    ))
                    
        return albums
    
    def _extract_band_from_context(self, context, album_title):
        """Extract band name from HTML context"""
        import re
        
        # Clean context of HTML tags
        context = re.sub(r'<[^>]+>', ' ', context)
        context = re.sub(r'\s+', ' ', context).strip()
        
        # Patterns to find band names
        patterns = [
            r'by\s+([^-\n\|•]+?)(?:\s*[-\|•]|\s*\d{4}|\s*$)',
            r'([^-\n\|•]+?)\s*[-\|•]\s*' + re.escape(album_title),
            r'artist[:\s]+([^-\n\|•]+?)(?:\s*[-\|•]|\s*\d{4}|\s*$)',
            r'band[:\s]+([^-\n\|•]+?)(?:\s*[-\|•]|\s*\d{4}|\s*$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                band_name = match.group(1).strip()
                band_name = re.sub(r'\s*\([^)]*\)', '', band_name)  # Remove parentheses
                band_name = re.sub(r'\s+', ' ', band_name)  # Normalize whitespace
                if len(band_name) > 1 and band_name.lower() != album_title.lower():
                    return band_name
        
        return ""
    
    def _extract_album_type(self, url, context):
        """Extract album type from URL or context"""
        import re
        
        # Extract from URL first
        if "/album/" in url.lower():
            return "Album"
        elif "/ep/" in url.lower():
            return "EP"
        elif "/demo/" in url.lower():
            return "Demo"
        elif "/single/" in url.lower():
            return "Single"
        elif "/split/" in url.lower():
            return "Split"
        
        # Extract from context
        type_patterns = [
            r'\b(Album|LP|Full[- ]?Length)\b',
            r'\b(EP|Extended[- ]?Play)\b',
            r'\b(Demo|Demonstration)\b',
            r'\b(Single)\b',
            r'\b(Split)\b',
            r'\b(Compilation|Comp)\b',
            r'\b(Live)\b'
        ]
        
        for pattern in type_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1).title()
        
        return ""
    
    def _extract_year(self, context):
        """Extract year from context"""
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', context)
        return year_match.group(0) if year_match else ""
    
    def _extract_genre(self, context):
        """Extract genre from context"""
        import re
        # Common metal genres
        genre_patterns = [
            r'\b(Black Metal|Death Metal|Thrash Metal|Heavy Metal|Progressive Metal|Power Metal|Doom Metal|Folk Metal|Gothic Metal|Symphonic Metal|Melodic Death Metal|Technical Death Metal|Brutal Death Metal|Blackened Death Metal|Post Metal|Post Rock|Metalcore|Deathcore|Grindcore|Hardcore|Alternative Metal|Nu Metal|Industrial Metal|Atmospheric Black Metal|Depressive Black Metal|Raw Black Metal)\b'
        ]
        
        for pattern in genre_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def _deduplicate_albums(self, albums, search_term):
        """Remove duplicate albums and sort by relevance"""
        seen = set()
        unique_albums = []
        
        # Sort by relevance first
        def relevance_score(album):
            score = 0
            title_lower = album.title.lower()
            search_lower = search_term.lower()
            
            # Exact match gets highest score
            if title_lower == search_lower:
                score += 100
            # Starts with search term
            elif title_lower.startswith(search_lower):
                score += 50
            # Contains search term
            elif search_lower in title_lower:
                score += 25
            
            # Bonus for having band name
            if album.band:
                score += 10
            
            # Bonus for having year
            if album.year:
                score += 5
            
            # Bonus for having type
            if album.type:
                score += 3
            
            return score
        
        albums.sort(key=relevance_score, reverse=True)
        
        for album in albums:
            # Create a unique key based on title and band
            key = f"{album.title.lower()}|{album.band.lower() if album.band else ''}"
            if key not in seen:
                seen.add(key)
                unique_albums.append(album)
        
        return unique_albums
    
    def get_band_albums(self, band):
        """Get albums/releases for a specific band"""
        print(f"💿 Getting albums for: {band.name}")
        
        page = self._get_page(band.url)
        if page is None:
            return []
        
        albums = []
        try:
            # Method 1: Look for release/album links in the page
            if hasattr(page, 'find'):
                # Try various selectors for release links
                release_selectors = [
                    'a[href*="/releases/"]', 'a[href*="/album/"]', 'a[href*="/ep/"]', 
                    'a[href*="/demo/"]', 'a[href*="/single/"]', 'a[href*="/split/"]',
                    'a[href*="discography"]', '.discography a', '.releases a', 
                    '.albums a', '.release-item a'
                ]
                
                found_releases = []
                for selector in release_selectors:
                    release_links = page(selector)
                    for link in release_links:
                        link_elem = page(link)
                        album_title = link_elem.text().strip()
                        album_url = link_elem.attr('href')
                        
                        if album_title and album_url and album_title not in found_releases:
                            found_releases.append(album_title)
                            
                            # Make sure URL is complete
                            if not album_url.startswith('http'):
                                album_url = BASE_URL + album_url if album_url.startswith('/') else BASE_URL + '/' + album_url
                            
                            # Try to get release type and year from context
                            parent_text = link_elem.parent().text() if link_elem.parent() else ""
                            
                            album_type = ""
                            year = ""
                            
                            # Extract type from URL or context
                            if "/album/" in album_url.lower():
                                album_type = "Album"
                            elif "/ep/" in album_url.lower():
                                album_type = "EP"
                            elif "/demo/" in album_url.lower():
                                album_type = "Demo"
                            elif "/single/" in album_url.lower():
                                album_type = "Single"
                            elif "/split/" in album_url.lower():
                                album_type = "Split"
                            
                            # Try to extract year from surrounding text
                            import re
                            year_match = re.search(r'\b(19|20)\d{2}\b', parent_text)
                            if year_match:
                                year = year_match.group(0)
                            
                            album = Release(
                                title=album_title,
                                band=band.name,
                                type=album_type,
                                year=year,
                                url=album_url
                            )
                            albums.append(album)
                
                # Method 2: Look for structured discography sections
                discography_selectors = [
                    '.discography', '#discography', '.releases', '#releases',
                    '.albums', '#albums', '.release-list', '.album-list'
                ]
                
                for selector in discography_selectors:
                    discography_section = page(selector)
                    if discography_section and len(discography_section) > 0:
                        # Look for lists or tables of releases
                        release_items = discography_section.find('li, tr, .release-item, .album-item, div')
                        for item in release_items:
                            item_elem = page(item)
                            item_text = item_elem.text()
                            
                            # Look for album links within this item
                            item_links = item_elem.find('a')
                            for link in item_links:
                                link_elem = page(link)
                                title = link_elem.text().strip()
                                url = link_elem.attr('href')
                                
                                if title and url and title not in found_releases:
                                    found_releases.append(title)
                                    
                                    if not url.startswith('http'):
                                        url = BASE_URL + url if url.startswith('/') else BASE_URL + '/' + url
                                    
                                    # Extract additional info from the item text
                                    import re
                                    year_match = re.search(r'\b(19|20)\d{2}\b', item_text)
                                    type_match = re.search(r'\b(Album|EP|Demo|Single|Split)\b', item_text, re.IGNORECASE)
                                    
                                    album = Release(
                                        title=title,
                                        band=band.name,
                                        type=type_match.group(0) if type_match else "",
                                        year=year_match.group(0) if year_match else "",
                                        url=url
                                    )
                                    albums.append(album)
                
                # Method 3: Look for any text mentioning releases/albums in the page content
                if not albums:
                    page_text = page.text()
                    import re
                    
                    # Look for album patterns in text
                    album_patterns = [
                        r'(?:album|ep|demo|single)\s*[":]\s*([^\n]+)',
                        r'released?\s+(?:the\s+)?(?:album|ep|demo)\s+["\']([^"\']+)["\']',
                        r'["\']([^"\']+)["\']\s+\(\d{4}\)',
                    ]
                    
                    for pattern in album_patterns:
                        matches = re.finditer(pattern, page_text, re.IGNORECASE)
                        for match in matches:
                            album_title = match.group(1).strip()
                            if album_title and len(album_title) > 2 and album_title not in found_releases:
                                found_releases.append(album_title)
                                
                                # Try to find year in context
                                context = page_text[max(0, match.start()-50):match.end()+50]
                                year_match = re.search(r'\b(19|20)\d{2}\b', context)
                                year = year_match.group(0) if year_match else ""
                                
                                album = Release(
                                    title=album_title,
                                    band=band.name,
                                    type="Release",
                                    year=year,
                                    url=band.url  # Link back to band page as fallback
                                )
                                albums.append(album)
        
        except Exception as e:
            print(f"❌ Error getting band albums: {e}")
            import traceback
            traceback.print_exc()
        
        # Update the band's albums list
        band.albums = albums
        return albums
    
    def get_album_details(self, album):
        """Get detailed information about a specific album"""
        print(f"💿 Getting details for: {album.title}")
        
        page = self._get_page(album.url)
        if page is None:
            return album
        
        try:
            # Check if we have PyQuery object or just text
            if hasattr(page, 'find') and callable(page):
                # Extract additional details using PyQuery
                
                # Look for description/review content
                description_selectors = [
                    '.entry-content', '.post-content', '.album-description', 
                    '.review-content', 'article', '.content'
                ]
                
                for selector in description_selectors:
                    description_elem = page(selector)
                    if description_elem:
                        description_text = description_elem.text().strip()
                        if len(description_text) > 50:  # Only use substantial descriptions
                            # Clean up the description
                            import re
                            # Remove excessive whitespace
                            description_text = re.sub(r'\s+', ' ', description_text)
                            # Truncate if too long
                            if len(description_text) > 500:
                                description_text = description_text[:500] + "..."
                            album.description = description_text
                            break
                
                # Look for metadata in structured data
                meta_selectors = [
                    '.album-meta', '.release-info', '.album-info', 
                    '.metadata', '.album-details'
                ]
                
                for selector in meta_selectors:
                    meta_elem = page(selector)
                    if meta_elem:
                        meta_text = meta_elem.text()
                        
                        # Extract year if not already found
                        if not album.year:
                            year_match = re.search(r'\b(19|20)\d{2}\b', meta_text)
                            if year_match:
                                album.year = year_match.group(0)
                        
                        # Extract genre if not already found
                        if not album.genre:
                            album.genre = self._extract_genre(meta_text)
                        
                        # Extract type if not already found
                        if not album.type:
                            album.type = self._extract_album_type(album.url, meta_text)
                        
                        break
                
                # Look for band information if not already found
                if not album.band:
                    band_selectors = [
                        '.artist-name', '.band-name', 'h1', 'h2', 
                        '.entry-title', '.post-title'
                    ]
                    
                    for selector in band_selectors:
                        band_elem = page(selector)
                        if band_elem:
                            band_text = band_elem.text().strip()
                            # Look for band patterns in the text
                            if band_text and len(band_text) < 100:  # Reasonable band name length
                                # Clean potential band name
                                band_text = re.sub(r'\s*[-–|]\s*.*$', '', band_text)  # Remove everything after dash
                                band_text = re.sub(r'\s*\([^)]*\)', '', band_text)  # Remove parentheses
                                if len(band_text) > 1:
                                    album.band = band_text
                                    break
            
            else:
                # Fallback to regex parsing for plain text
                html_content = str(page)
                
                # Extract description from common content areas
                content_patterns = [
                    r'<div[^>]*class="[^"]*(?:content|description|review)[^"]*"[^>]*>(.*?)</div>',
                    r'<article[^>]*>(.*?)</article>',
                    r'<p[^>]*>(.*?)</p>'
                ]
                
                for pattern in content_patterns:
                    matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
                    for match in matches:
                        # Clean HTML and extract text
                        text = re.sub(r'<[^>]+>', ' ', match)
                        text = re.sub(r'\s+', ' ', text).strip()
                        if len(text) > 50:
                            album.description = text[:500] + "..." if len(text) > 500 else text
                            break
                    if album.description:
                        break
                
                # Extract metadata
                if not album.year:
                    year_match = re.search(r'\b(19|20)\d{2}\b', html_content)
                    if year_match:
                        album.year = year_match.group(0)
                
                if not album.genre:
                    album.genre = self._extract_genre(html_content)
                
                if not album.type:
                    album.type = self._extract_album_type(album.url, html_content)
        
        except Exception as e:
            print(f"❌ Error getting album details: {e}")
        
        return album
    
    def search_albums_by_band(self, band_name, album_term=""):
        """Search for albums by a specific band with optional album name filter"""
        print(f"🔍 Searching for albums by '{band_name}'" + (f" matching '{album_term}'" if album_term else ""))
        
        # First try to find the band
        bands = self.search_bands(band_name)
        albums = []
        
        for band in bands[:3]:  # Check top 3 band matches
            try:
                band_albums = self.get_band_albums(band)
                if album_term:
                    # Filter albums by the album term
                    band_albums = [a for a in band_albums if album_term.lower() in a.title.lower()]
                albums.extend(band_albums)
            except Exception as e:
                print(f"❌ Error getting albums for {band.name}: {e}")
        
        # Also try general search with both band and album terms
        if album_term:
            general_results = self.search_albums(album_term, band_filter=band_name)
            albums.extend(general_results)
        
        # Remove duplicates
        albums = self._deduplicate_albums(albums, album_term or band_name)
        return albums[:15]  # Limit results
    
    def get_random_band(self):
        """Get a random Irish metal band"""
        print("🎲 Finding a random Irish metal band...")
        
        import random
        
        # Try different approaches to get a random band
        random_band = None
        
        try:
            # Method 1: Try searching for common metal genres first (more reliable)
            print("🔍 Searching by metal genres...")
            metal_genres = [
                'black metal', 'death metal', 'thrash metal', 'doom metal',
                'heavy metal', 'power metal', 'progressive metal', 'folk metal',
                'gothic metal', 'symphonic metal', 'metalcore', 'hardcore'
            ]
            
            random_genre = random.choice(metal_genres)
            genre_results = self.search_bands(random_genre)
            
            if genre_results:
                random_band = random.choice(genre_results)
            
            # Method 2: If genre search didn't work, try random letters
            if not random_band:
                print("🔍 Trying alphabetical random search...")
                random_letters = ['a', 'b', 'c', 'd', 'e', 'm', 'h', 's', 'r', 'p', 't', 'n']
                for letter in random.sample(random_letters, 4):  # Try 4 random letters
                    letter_results = self.search_bands(letter)
                    if letter_results and len(letter_results) > 0:
                        random_band = random.choice(letter_results)
                        break
            
            # Method 3: Try some common band name patterns
            if not random_band:
                print("🔍 Using pattern-based random search...")
                fallback_searches = ['metal', 'band', 'rock', 'the', 'irish', 'black', 'death', 'fire', 'dark']
                for search_term in random.sample(fallback_searches, 3):
                    results = self.search_bands(search_term)
                    if results and len(results) > 0:
                        random_band = random.choice(results)
                        break
                        
            # Method 4: Get a random page from the artists section (as last resort)
            if not random_band:
                print("🔍 Trying page-based random search...")
                page_number = random.randint(1, 5)  # Try pages 1-5
                
                potential_urls = [
                    f"{BASE_URL}/artists/page/{page_number}/",
                    f"{BASE_URL}/artists/?paged={page_number}",
                ]
                
                for url in potential_urls:
                    try:
                        page = self._get_page(url)
                        if page and hasattr(page, 'find'):
                            # Look for artist links on this page - be more specific
                            artist_links = page('a[href*="/artists/"][href*="/"]')
                            valid_links = []
                            
                            for link in artist_links:
                                link_elem = page(link)
                                band_name = link_elem.text().strip()
                                band_url = link_elem.attr('href')
                                
                                # Filter out navigation links and ensure we have real band names
                                if (band_name and band_url and 
                                    band_name.lower() not in ['artists', 'page', 'next', 'previous', '»', '«'] and
                                    not band_name.isdigit() and
                                    len(band_name) > 1 and
                                    '/artists/' in band_url and
                                    band_url.count('/') > 3):  # Ensure it's a specific artist page
                                    valid_links.append((band_name, band_url))
                            
                            if valid_links:
                                band_name, band_url = random.choice(valid_links)
                                random_band = Band(name=band_name, url=band_url)
                                break
                    except Exception as e:
                        print(f"🔍 Page method failed: {e}")
                        continue
        
        except Exception as e:
            print(f"❌ Error finding random band: {e}")
        
        if random_band:
            print(f"🎸 Random band found: {random_band.name}")
            return random_band
        else:
            print("❌ Could not find a random band. Try searching manually!")
            return None
    
    def get_band_details(self, band):
        """Get detailed information about a band"""
        print(f"📋 Getting details for: {band.name}")
        
        page = self._get_page(band.url)
        if page is None:
            return band
        
        try:
            if hasattr(page, 'find'):
                # PyQuery parsing - try to get page title/heading first for band name
                title_selectors = ['h1', '.entry-title', '.post-title', 'title', '.page-title', '.artist-name']
                for selector in title_selectors:
                    title_elem = page(selector)
                    if title_elem and len(title_elem) > 0:
                        page_title = title_elem.eq(0).text().strip()
                        if page_title and len(page_title) > 0 and page_title.lower() != 'artists':
                            band.name = page_title
                            break
                
                # Get all text content to parse
                content_selectors = ['.entry-content', '.post-content', '.content', '.artist-info', 'article', 'main']
                content_text = ""
                
                for selector in content_selectors:
                    content_elem = page(selector)
                    if content_elem and len(content_elem) > 0:
                        content_text = content_elem.eq(0).text().strip()
                        if content_text and len(content_text) > 50:  # Good content found
                            break
                
                # If no structured content found, get all page text
                if not content_text or len(content_text) < 50:
                    content_text = page.text()
                
                # Parse the content for band information using regex patterns
                import re
                
                # Extract genre/style
                genre_patterns = [
                    r'Genre:\s*([^\n,.]+)',
                    r'Style:\s*([^\n,.]+)', 
                    r'Musical style:\s*([^\n,.]+)',
                    r'Type:\s*([^\n,.]+)',
                    r'\b(Black Metal|Death Metal|Thrash Metal|Heavy Metal|Power Metal|Progressive Metal|Doom Metal|Folk Metal|Gothic Metal|Symphonic Metal|Metalcore|Hardcore|Grindcore|Sludge|Stoner|Post-Metal)\b'
                ]
                
                for pattern in genre_patterns:
                    genre_match = re.search(pattern, content_text, re.IGNORECASE)
                    if genre_match:
                        band.genre = genre_match.group(1).strip()
                        break
                
                # Extract county/location
                location_patterns = [
                    r'County:\s*([^\n,.]+)',
                    r'From:\s*([^\n,.]+)',
                    r'Location:\s*([^\n,.]+)',
                    r'Based in:\s*([^\n,.]+)',
                    r'\bfrom\s+Co\.?\s*([^\n,.]+)',
                    r'\b(Co\.\s*\w+)',
                    r'\b(County\s+\w+)',
                ]
                
                for pattern in location_patterns:
                    location_match = re.search(pattern, content_text, re.IGNORECASE)
                    if location_match:
                        band.county = location_match.group(1).strip()
                        break
                
                # Extract year formed
                year_patterns = [
                    r'Formed:\s*([^\n,.]+)',
                    r'Founded:\s*([^\n,.]+)',
                    r'Established:\s*([^\n,.]+)',
                    r'Started:\s*([^\n,.]+)',
                    r'formed in\s+(\d{4})',
                    r'since\s+(\d{4})',
                ]
                
                for pattern in year_patterns:
                    year_match = re.search(pattern, content_text, re.IGNORECASE)
                    if year_match:
                        band.year_formed = year_match.group(1).strip()
                        break
                
                # Create a description from the first meaningful paragraph
                paragraphs = content_text.split('\n')
                for paragraph in paragraphs:
                    para = paragraph.strip()
                    if (len(para) > 30 and 
                        not para.lower().startswith(('genre:', 'county:', 'formed:', 'style:')) and
                        not para.isdigit() and
                        'metal' in para.lower()):
                        band.description = para[:200] + ("..." if len(para) > 200 else "")
                        break
                
                # Fallback: try CSS selectors with more specific matching
                if not band.genre:
                    genre_elem = page('.genre, [class*="genre"], .style, [class*="style"], .musical-style')
                    if genre_elem and len(genre_elem) > 0:
                        genre_text = genre_elem.eq(0).text().strip()
                        if genre_text and genre_text.lower() not in ['genre', 'style']:
                            band.genre = genre_text
                
                if not band.county:
                    location_elem = page('.county, [class*="county"], .location, [class*="location"], .from')
                    if location_elem and len(location_elem) > 0:
                        location_text = location_elem.eq(0).text().strip()
                        if location_text and location_text.lower() not in ['county', 'location']:
                            band.county = location_text
                
                if not band.year_formed:
                    year_elem = page('.formed, [class*="formed"], .year, [class*="year"], .founded')
                    if year_elem and len(year_elem) > 0:
                        year_text = year_elem.eq(0).text().strip()
                        if year_text and year_text.lower() not in ['formed', 'year formed']:
                            band.year_formed = year_text
            
            else:
                # Fallback text parsing for non-PyQuery objects
                import re
                page_text = str(page)
                
                # Basic text extraction with improved patterns
                if 'Genre:' in page_text or 'Style:' in page_text:
                    genre_match = re.search(r'(?:Genre|Style):\s*([^\n<]+)', page_text)
                    if genre_match:
                        band.genre = genre_match.group(1).strip()
                
                if 'County:' in page_text or 'Location:' in page_text:
                    county_match = re.search(r'(?:County|Location):\s*([^\n<]+)', page_text)
                    if county_match:
                        band.county = county_match.group(1).strip()
                        
                if 'Formed:' in page_text:
                    year_match = re.search(r'Formed:\s*([^\n<]+)', page_text)
                    if year_match:
                        band.year_formed = year_match.group(1).strip()
        
        except Exception as e:
            print(f"❌ Error getting band details: {e}")
            import traceback
            traceback.print_exc()
        
        return band
class IrishMetalApp:
    """Main application class"""
    
    def __init__(self):
        self.archive = IrishMetalArchive()
        
    def display_welcome(self):
        """Display welcome message"""
        print("🎸" + "="*60 + "🤘")
        print("      WELCOME TO THE ALL IRISH METAL PROJECT SEARCH APP")
        print("      Search and explore Irish metal bands via the Irish Metal Archive")
        print("🤘" + "="*60 + "🎸")
        print()
    
    def display_menu(self):
        """Display main menu"""
        print("\n📋 MENU:")
        print("1. Search for bands")
        print("2. Search for albums 💿")
        print("3. Get band details")
        print("4. Find random band 🎲")
        print("5. Visit All Ireland Metal 🇮🇪")
        print("6. Exit")
        print("-" * 40)
    
    def visit_all_ireland_metal(self):
        """Find Out More About The All Ireland Metal Project"""
        import webbrowser
        url = "https://linktr.ee/AllIrelandMetal"
        
        print("\n🇮🇪 ALL IRELAND METAL")
        print("=" * 50)
        print("Opening the All Ireland Metal Linktree in your browser...")
        print(f"🔗 URL: {url}")
        print("\nThis community hub connects you to:")
        print("• Irish metal bands and artists")
        print("• Upcoming shows and events")
        print("• Irish metal news and updates")
        print("• Record labels and promoters")
        print("• Social media channels")
        print()
        
        try:
            webbrowser.open(url)
            print("✅ Browser opened successfully!")
        except Exception as e:
            print(f"❌ Could not open browser automatically: {e}")
            print(f"Please manually visit: {url}")
        
        input("\nPress Enter to continue...")
    
    def search_bands_interactive(self):
        """Interactive band search"""
        search_term = input("🔍 Enter band name to search: ").strip()
        if not search_term:
            print("❌ Please enter a search term")
            return
        
        results = self.archive.search_bands(search_term)
        
        if results:
            print(f"\n✅ Found {len(results)} band(s) matching '{search_term}':")
            print("-" * 50)
            for i, band in enumerate(results, 1):
                print(f"{i:2d}. {band.name}")
                if band.genre:
                    print(f"     Genre: {band.genre}")
                if band.county:
                    print(f"     County: {band.county}")
                print()
        else:
            print(f"❌ No bands found matching '{search_term}'")
        
        return results
    
    def search_albums_interactive(self):
        """Enhanced interactive album search with multiple search options"""
        print("\n💿 ALBUM SEARCH OPTIONS:")
        print("1. Search by album name")
        print("2. Search by band name")
        print("3. Search by band + album")
        print("4. Advanced search")
        
        choice = input("\nSelect search type (1-4): ").strip()
        
        if choice == '1':
            return self._search_albums_by_name()
        elif choice == '2':
            return self._search_albums_by_band()
        elif choice == '3':
            return self._search_albums_band_plus_album()
        elif choice == '4':
            return self._search_albums_advanced()
        else:
            print("❌ Invalid choice. Defaulting to album name search.")
            return self._search_albums_by_name()
    
    def _search_albums_by_name(self):
        """Search albums by name only"""
        search_term = input("💿 Enter album name to search: ").strip()
        if not search_term:
            print("❌ Please enter a search term")
            return []
        
        results = self.archive.search_albums(search_term)
        self._display_album_results(results, search_term)
        
        # Offer to get album details
        if results:
            self._offer_album_details(results)
        
        return results
    
    def _search_albums_by_band(self):
        """Search albums by band name"""
        band_name = input("🎸 Enter band name: ").strip()
        if not band_name:
            print("❌ Please enter a band name")
            return []
        
        results = self.archive.search_albums_by_band(band_name)
        self._display_album_results(results, f"albums by '{band_name}'")
        
        if results:
            self._offer_album_details(results)
        
        return results
    
    def _search_albums_band_plus_album(self):
        """Search albums by both band and album name"""
        band_name = input("🎸 Enter band name: ").strip()
        album_name = input("💿 Enter album name (or part of it): ").strip()
        
        if not band_name:
            print("❌ Please enter a band name")
            return []
        
        results = self.archive.search_albums_by_band(band_name, album_name)
        search_desc = f"albums by '{band_name}'" + (f" matching '{album_name}'" if album_name else "")
        self._display_album_results(results, search_desc)
        
        if results:
            self._offer_album_details(results)
        
        return results
    
    def _search_albums_advanced(self):
        """Advanced album search with filters"""
        print("\n🔍 ADVANCED ALBUM SEARCH:")
        
        album_name = input("💿 Album name (optional): ").strip()
        band_name = input("🎸 Band name (optional): ").strip()
        year = input("📅 Year (optional): ").strip()
        album_type = input("🎵 Type (Album/EP/Demo/Single, optional): ").strip()
        
        if not album_name and not band_name:
            print("❌ Please enter at least an album name or band name")
            return []
        
        # Start with basic search
        if album_name:
            results = self.archive.search_albums(album_name, band_filter=band_name if band_name else None)
        else:
            results = self.archive.search_albums_by_band(band_name)
        
        # Apply additional filters
        if year:
            results = [r for r in results if year in (r.year or "")]
        
        if album_type:
            results = [r for r in results if album_type.lower() in (r.type or "").lower()]
        
        search_desc = "albums matching advanced criteria"
        self._display_album_results(results, search_desc)
        
        if results:
            self._offer_album_details(results)
        
        return results
    
    def _display_album_results(self, results, search_description):
        """Display album search results in a formatted way"""
        if results:
            print(f"\n✅ Found {len(results)} album(s) for {search_description}:")
            print("=" * 60)
            for i, album in enumerate(results, 1):
                print(f"{i:2d}. 💿 {album.title}")
                if album.band:
                    print(f"     🎸 Band: {album.band}")
                if album.type:
                    print(f"     🎵 Type: {album.type}")
                if album.year:
                    print(f"     📅 Year: {album.year}")
                if album.genre:
                    print(f"     🏷️  Genre: {album.genre}")
                if album.url:
                    print(f"     🔗 URL: {album.url}")
                print()
        else:
            print(f"❌ No albums found for {search_description}")
    
    def _offer_album_details(self, albums):
        """Offer to show detailed information about selected albums"""
        while True:
            choice = input(f"\n📖 Get details for an album? (1-{len(albums)}, or 'n' to skip): ").strip().lower()
            
            if choice == 'n':
                break
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(albums):
                    album = albums[index]
                    print(f"\n🔍 Getting detailed information for '{album.title}'...")
                    detailed_album = self.archive.get_album_details(album)
                    self._display_album_details(detailed_album)
                else:
                    print(f"❌ Please enter a number between 1 and {len(albums)}")
            except ValueError:
                print("❌ Please enter a valid number or 'n'")
    
    def _display_album_details(self, album):
        """Display detailed album information"""
        print("\n" + "=" * 60)
        print(f"💿 ALBUM DETAILS: {album.title}")
        print("=" * 60)
        
        if album.band:
            print(f"🎸 Band: {album.band}")
        if album.type:
            print(f"🎵 Type: {album.type}")
        if album.year:
            print(f"📅 Year: {album.year}")
        if album.genre:
            print(f"🏷️  Genre: {album.genre}")
        if album.description:
            print(f"\n📝 Description:")
            print(album.description)
        if album.url:
            print(f"\n🔗 URL: {album.url}")
        
        print("=" * 60)
    
    def get_band_details_interactive(self, bands_list=None):
        """Interactive band details lookup"""
        if not bands_list:
            band_name = input("🔍 Enter exact band name: ").strip()
            if not band_name:
                print("❌ Please enter a band name")
                return
            
            # Create a simple band object for lookup
            band = Band(name=band_name, url=f"{BASE_URL}/artist/{band_name.lower().replace(' ', '-')}")
        else:
            try:
                choice = int(input(f"\nEnter band number (1-{len(bands_list)}): "))
                if 1 <= choice <= len(bands_list):
                    band = bands_list[choice - 1]
                else:
                    print("❌ Invalid choice")
                    return
            except ValueError:
                print("❌ Please enter a valid number")
                return
        
        detailed_band = self.archive.get_band_details(band)
        
        print(f"\n🎸 BAND DETAILS: {detailed_band.name}")
        print("=" * 50)
        if detailed_band.genre:
            print(f"🎵 Genre: {detailed_band.genre}")
        if detailed_band.county:
            print(f"📍 County: {detailed_band.county}")
        if detailed_band.year_formed:
            print(f"📅 Formed: {detailed_band.year_formed}")
        if detailed_band.status:
            print(f"📊 Status: {detailed_band.status}")
        if detailed_band.description:
            print(f"📝 Description: {detailed_band.description}")
        print(f"🔗 URL: {detailed_band.url}")
        print()
        
        # Ask if user wants to see albums
        show_albums = input("💿 Would you like to see this band's albums? (y/n): ").strip().lower()
        if show_albums == 'y':
            albums = self.archive.get_band_albums(detailed_band)
            if albums:
                print(f"\n💿 ALBUMS/RELEASES for {detailed_band.name}:")
                print("=" * 50)
                for i, album in enumerate(albums, 1):
                    print(f"{i:2d}. {album.title}")
                    if album.type:
                        print(f"     Type: {album.type}")
                    if album.year:
                        print(f"     Year: {album.year}")
                    if album.url:
                        print(f"     URL: {album.url}")
                    print()
            else:
                print(f"❌ No albums found for {detailed_band.name}")
        print()
    
    def find_random_band(self):
        """Find and display a random Irish metal band"""
        random_band = self.archive.get_random_band()
        
        if random_band:
            print(f"\n🎲 Random Band Discovery:")
            print("=" * 50)
            
            # Get detailed information about the random band
            detailed_band = self.archive.get_band_details(random_band)
            
            print(f"🎸 Band: {detailed_band.name}")
            if detailed_band.genre:
                print(f"🎵 Genre: {detailed_band.genre}")
            if detailed_band.county:
                print(f"📍 County: {detailed_band.county}")
            if detailed_band.year_formed:
                print(f"📅 Formed: {detailed_band.year_formed}")
            if detailed_band.description:
                print(f"📝 Description: {detailed_band.description}")
            print(f"🔗 URL: {detailed_band.url}")
            
            # Ask if user wants to see albums
            show_albums = input("\n💿 Would you like to see this band's albums? (y/n): ").strip().lower()
            if show_albums == 'y':
                albums = self.archive.get_band_albums(detailed_band)
                if albums:
                    print(f"\n💿 ALBUMS/RELEASES for {detailed_band.name}:")
                    print("=" * 50)
                    for i, album in enumerate(albums, 1):
                        print(f"{i:2d}. {album.title}")
                        if album.type:
                            print(f"     Type: {album.type}")
                        if album.year:
                            print(f"     Year: {album.year}")
                        print()
                else:
                    print(f"❌ No albums found for {detailed_band.name}")
            
            # Ask if user wants to discover another random band
            while True:
                choice = input("\n🎲 Find another random band? (y/n): ").strip().lower()
                if choice == 'y':
                    print()
                    self.find_random_band()
                    break
                elif choice == 'n':
                    break
                else:
                    print("❌ Please enter 'y' for yes or 'n' for no")
        else:
            print("❌ Could not find a random band at this time. Try again later!")
    
    def run(self):
        """Main application loop"""
        self.display_welcome()
        
        # Quick connectivity test
        print("🌐 Testing connection to Irish Metal Archive...")
        test_page = self.archive._get_page(BASE_URL)
        if test_page is None:
            print("❌ Cannot connect to irishmetalarchive.com")
            print("   Please check your internet connection and try again.")
            return
        else:
            print("✅ Connected successfully!")
        
        while True:
            self.display_menu()
            
            try:
                choice = input("Enter your choice (1-6): ").strip()
                
                if choice == '1':
                    results = self.search_bands_interactive()
                    if results:
                        follow_up = input("\nWould you like details on any band? (y/n): ")
                        if follow_up.lower() == 'y':
                            self.get_band_details_interactive(results)
                
                elif choice == '2':
                    results = self.search_albums_interactive()
                    # Could add album details functionality here in the future
                
                elif choice == '3':
                    self.get_band_details_interactive()
                
                elif choice == '4':
                    self.find_random_band()
                
                elif choice == '5':
                    self.visit_all_ireland_metal()
                
                elif choice == '6':
                    print("🤘 Thanks for using The All Ireland Metal Search Tool!")
                    print("   Keep supporting Irish metal! 🎸")
                    print("\n🇮🇪 Don't forget to check out All Ireland Metal:")
                    print("   🔗 https://linktr.ee/AllIrelandMetal")
                    print("   Connect with the Irish metal community!")
                    break
                
                else:
                    print("❌ Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")
            
            except KeyboardInterrupt:
                print("\n\n🤘 Thanks for using The All Ireland Metal Search Tool!")
                print("🇮🇪 Learn More About The All Ireland Metal Project: https://linktr.ee/AllIrelandMetal")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                print("   Please try again.")

def check_requirements():
    """Check if required modules are available"""
    missing_modules = []
    
    try:
        import requests
    except ImportError:
        missing_modules.append('requests')
    
    # PyQuery is optional, we have fallback parsing
    try:
        import pyquery
    except ImportError:
        print("ℹ️  Note: PyQuery not available, using basic HTML parsing")
    
    if missing_modules:
        print("❌ Missing required modules:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\nPlease install with:")
        print(f"   pip install {' '.join(missing_modules)}")
        return False
    
    return True

def main():
    """Main entry point"""
    if not check_requirements():
        sys.exit(1)
    
    app = IrishMetalApp()
    app.run()

if __name__ == "__main__":
    main()