#!/usr/bin/env python3
"""
The All Ireland Metal Project - Modern GUI App
A modern tkinter-based GUI for searching Irish metal bands

Usage: python irish_metal_gui.py
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import ssl
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import re
import random
import webbrowser
import threading
from dataclasses import dataclass, field
from typing import List

# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = 'https://irishmetalarchive.com'

@dataclass
class Band:
    name: str
    genre: str = ""
    county: str = ""
    url: str = ""
    year_formed: str = ""
    description: str = ""
    albums: List['Release'] = field(default_factory=list)

@dataclass
class Release:
    title: str
    band: str
    genre: str = ""
    year: str = ""
    type: str = ""
    url: str = ""

class IrishMetalArchive:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        
    def _get_page(self, url):
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                try:
                    from pyquery import PyQuery as pq
                    return pq(response.content)
                except ImportError:
                    return response.text
            return None
        except Exception as e:
            return None

    def search_bands(self, search_term):
        search_url = f"{BASE_URL}/?s={search_term}"
        page = self._get_page(search_url)
        
        if not page:
            return []
            
        bands = []
        try:
            if hasattr(page, 'find'):
                links = page('a[href*="/artists/"]')
                for link in links:
                    elem = page(link)
                    name = elem.text().strip()
                    url = elem.attr('href')
                    if name and url and name.lower() != 'artists':
                        if not any(b.name.lower() == name.lower() for b in bands):
                            bands.append(Band(name=name, url=url))
            else:
                matches = re.findall(r'<a[^>]*href="([^"]*\/artists\/[^"]*)"[^>]*>([^<]+)</a>', str(page))
                for url, name in matches:
                    name = name.strip()
                    if name and name.lower() != 'artists':
                        if not url.startswith('http'):
                            url = BASE_URL + url
                        if not any(b.name.lower() == name.lower() for b in bands):
                            bands.append(Band(name=name, url=url))
        except:
            pass
        return bands

    def get_band_details(self, band):
        page = self._get_page(band.url)
        if not page:
            return band
            
        try:
            if hasattr(page, 'find'):
                title_elem = page('h1, .entry-title, .post-title')
                if title_elem and len(title_elem) > 0:
                    page_title = title_elem.eq(0).text().strip()
                    if page_title and page_title.lower() != 'artists':
                        band.name = page_title
                
                content_elem = page('.entry-content, .post-content, .content')
                content_text = content_elem.eq(0).text() if content_elem and len(content_elem) > 0 else page.text()
            else:
                content_text = str(page)
            
            # Extract information using regex patterns
            patterns = {
                'genre': [r'Genre:\s*([^\n,.]+)', r'\b(Black Metal|Death Metal|Thrash Metal|Heavy Metal|Power Metal|Progressive Metal|Doom Metal|Folk Metal|Gothic Metal|Symphonic Metal|Metalcore|Hardcore)\b'],
                'county': [r'County:\s*([^\n,.]+)', r'From:\s*([^\n,.]+)', r'\bfrom\s+Co\.?\s*([^\n,.]+)', r'\b(Co\.\s*\w+)'],
                'year_formed': [r'Formed:\s*([^\n,.]+)', r'formed in\s+(\d{4})', r'since\s+(\d{4})']
            }
            
            for field, field_patterns in patterns.items():
                for pattern in field_patterns:
                    match = re.search(pattern, content_text, re.IGNORECASE)
                    if match:
                        setattr(band, field, match.group(1).strip())
                        break
            
            # Extract description
            paragraphs = content_text.split('\n')
            for para in paragraphs:
                para = para.strip()
                if (len(para) > 30 and 
                    not para.lower().startswith(('genre:', 'county:', 'formed:')) and
                    'metal' in para.lower()):
                    band.description = para[:200] + ("..." if len(para) > 200 else "")
                    break
                    
        except:
            pass
            
        return band

    def get_band_albums(self, band):
        page = self._get_page(band.url)
        if not page:
            return []
            
        albums = []
        found_titles = []
        
        try:
            if hasattr(page, 'find'):
                selectors = ['a[href*="/releases/"]', 'a[href*="/album/"]', '.discography a', '.releases a']
                for selector in selectors:
                    links = page(selector)
                    for link in links:
                        elem = page(link)
                        title = elem.text().strip()
                        url = elem.attr('href')
                        
                        if title and url and title not in found_titles:
                            found_titles.append(title)
                            if not url.startswith('http'):
                                url = BASE_URL + url
                            
                            album_type = ""
                            if "/album/" in url.lower():
                                album_type = "Album"
                            elif "/ep/" in url.lower():
                                album_type = "EP"
                                
                            parent_text = elem.parent().text() if elem.parent() else ""
                            year_match = re.search(r'\b(19|20)\d{2}\b', parent_text)
                            year = year_match.group(0) if year_match else ""
                            
                            albums.append(Release(title=title, band=band.name, type=album_type, year=year, url=url))
                            
        except:
            pass
            
        band.albums = albums
        return albums

    def get_random_band(self):
        genres = ['death metal', 'black metal', 'heavy metal', 'thrash metal', 'doom metal']
        for genre in random.sample(genres, 2):
            results = self.search_bands(genre)
            if results:
                return random.choice(results)
        
        letters = ['a', 'b', 'c', 'd', 'm', 's', 'r']
        for letter in random.sample(letters, 3):
            results = self.search_bands(letter)
            if results:
                return random.choice(results)
                
        fallback_terms = ['metal', 'irish', 'band']
        for term in fallback_terms:
            results = self.search_bands(term)
            if results:
                return random.choice(results)
                
        return None

    def search_albums_by_year(self, year):
        """Search for albums released in a specific year"""
        search_url = f"{BASE_URL}/?s={year}"
        page = self._get_page(search_url)
        
        if not page:
            print(f"DEBUG: Failed to get page for {search_url}")
            return []
            
        albums = []
        found_titles = []
        
        # Debug: Print the raw content to understand the structure
        print(f"DEBUG: Searching for albums from year {year}")
        print(f"DEBUG: Search URL: {search_url}")
        
        try:
            if hasattr(page, 'find'):
                # Remove script tags and other unwanted content
                page('script').remove()
                page('style').remove()
                page('noscript').remove()
                
                # Debug: Let's see what content areas exist
                content_areas = page('.entry-content, .post-content, .search-results, .content, article, main')
                print(f"DEBUG: Found {len(content_areas)} content areas")
                
                if content_areas and len(content_areas) > 0:
                    content_text = content_areas.text()
                    print(f"DEBUG: Content area text length: {len(content_text)}")
                else:
                    content_text = page('body').text()
                    print(f"DEBUG: Body text length: {len(content_text)}")
                
                # Debug: Show first 500 chars of content
                print(f"DEBUG: First 500 chars of content:")
                print(repr(content_text[:500]))
                
                # Clean up the text
                lines = content_text.split('\n')
                clean_lines = []
                
                for line in lines:
                    line = line.strip()
                    # Skip empty lines, JavaScript, and tracking code
                    if (not line or 
                        len(line) < 5 or
                        'javascript' in line.lower() or
                        'gtag' in line.lower() or
                        'dataLayer' in line or
                        line.startswith('var ') or
                        line.startswith('function ') or
                        'cookie' in line.lower() or
                        'tracker' in line.lower() or
                        line.count('{') > 2 or
                        line.count('[') > 2):
                        continue
                    clean_lines.append(line)
                
                print(f"DEBUG: Clean lines count: {len(clean_lines)}")
                
                # Debug: Show lines that contain the year
                year_lines = [line for line in clean_lines if str(year) in line]
                print(f"DEBUG: Found {len(year_lines)} lines containing year {year}")
                for i, line in enumerate(year_lines[:5]):  # Show first 5
                    print(f"DEBUG: Year line {i+1}: {repr(line)}")
                
                # Look for album patterns in clean content
                for line in clean_lines:
                    if str(year) not in line:
                        continue
                    
                    # The issue is we're getting lines like:
                    # "by Aborted Earth (Death Metal, 2020) An Spailpín Fánach, Cork (2024)"
                    # We need to parse this correctly to extract the album name
                    
                    # Pattern 1: Look for "Album Title" by Band (Genre, Year) format
                    pattern1 = rf'"([^"]+)"\s+by\s+([^(]+?)\s*\([^)]*{year}[^)]*\)'
                    match1 = re.search(pattern1, line)
                    if match1:
                        album_title = match1.group(1).strip()
                        band_name = match1.group(2).strip()
                        
                        if album_title and album_title not in found_titles:
                            found_titles.append(album_title)
                            albums.append(Release(title=album_title, band=band_name, type="Release", year=str(year), url=search_url))
                    
                    # Pattern 2: Look for Band – "Album Title" (Year) format
                    pattern2 = rf'([^–\-]+?)\s*[–\-]\s*"([^"]+)"\s*\([^)]*{year}[^)]*\)'
                    match2 = re.search(pattern2, line)
                    if match2:
                        band_name = match2.group(1).strip()
                        album_title = match2.group(2).strip()
                        
                        if album_title and album_title not in found_titles:
                            found_titles.append(album_title)
                            albums.append(Release(title=album_title, band=band_name, type="Release", year=str(year), url=search_url))
                    
                    # Pattern 3: The problematic format we're seeing
                    # "by Band (Genre, Year) Album Title, Location (Year)"
                    # We need to extract the album title that comes after the band info
                    pattern3 = rf'by\s+([^(]+?)\s*\([^)]*\)\s+([^,(]+?)(?:,|\s+\([^)]*{year}[^)]*\))'
                    match3 = re.search(pattern3, line)
                    if match3:
                        band_name = match3.group(1).strip()
                        album_title = match3.group(2).strip()
                        
                        # Clean up the album title
                        album_title = re.sub(r'^\d+\.\s*', '', album_title)
                        album_title = album_title.strip()
                        
                        if (album_title and album_title not in found_titles and 
                            len(album_title) > 2 and not album_title.isdigit()):
                            found_titles.append(album_title)
                            albums.append(Release(title=album_title, band=band_name, type="Release", year=str(year), url=search_url))
                    
                    # Pattern 4: Try to find album titles that appear before " by "
                    # This handles cases where album comes first: "Album Title by Band (Genre, Year)"
                    pattern4 = rf'^([^"]+?)\s+by\s+([^(]+?)\s*\([^)]*{year}[^)]*\)'
                    match4 = re.search(pattern4, line)
                    if match4:
                        potential_title = match4.group(1).strip()
                        band_name = match4.group(2).strip()
                        
                        # Clean up potential title
                        potential_title = re.sub(r'^\d+\.\s*', '', potential_title)
                        potential_title = potential_title.strip('"\'')
                        
                        # Check if this looks like an album title (not starting with "by")
                        if (potential_title and not potential_title.lower().startswith('by') and
                            potential_title not in found_titles and 
                            len(potential_title) > 2 and not potential_title.isdigit()):
                            found_titles.append(potential_title)
                            albums.append(Release(title=potential_title, band=band_name, type="Release", year=str(year), url=search_url))
                
                # Additional search using links if we still don't have good results
                if len(albums) < 3:
                    release_links = page('a[href*="/releases/"], a[href*="/album/"], a[href*="/ep/"]')
                    for link in release_links:
                        elem = page(link)
                        link_text = elem.text().strip()
                        link_url = elem.attr('href')
                        
                        if not link_text or len(link_text) < 2 or link_text in found_titles:
                            continue
                        
                        # Get parent context to check for year
                        parent_context = ""
                        if elem.parent():
                            parent_context = elem.parent().text()
                            
                        if str(year) in parent_context:
                            # Try to extract band from URL
                            band_name = "Unknown"
                            if '/artists/' in link_url:
                                try:
                                    url_parts = link_url.split('/')
                                    artist_idx = url_parts.index('artists')
                                    if artist_idx + 1 < len(url_parts):
                                        band_name = url_parts[artist_idx + 1].replace('-', ' ').title()
                                except:
                                    pass
                            
                            found_titles.append(link_text)
                            full_url = link_url if link_url.startswith('http') else BASE_URL + link_url
                            albums.append(Release(title=link_text, band=band_name, type="Release", year=str(year), url=full_url))
                            
        except Exception as e:
            print(f"DEBUG: Error in search_albums_by_year: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"DEBUG: Final results - Found {len(albums)} albums")
        for i, album in enumerate(albums[:5]):  # Show first 5
            print(f"DEBUG: Album {i+1}: {album.title} by {album.band}")
            
        return albums

class IrishMetalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("All Ireland Metal Project APP")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')
        
        # Shutdown management
        self.is_shutting_down = False
        self.running_threads = []
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Custom colors
        self.colors = {
            'bg': '#1a1a1a',
            'fg': '#ffffff',
            'accent': '#d4af37',
            'red': '#ff4444',
            'button_bg': '#333333',
            'entry_bg': '#2a2a2a'
        }
        
        self.configure_styles()
        
        self.archive = IrishMetalArchive()
        self.current_bands = []
        
        # Set up window close protocol for clean shutdown
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        
        # Test connection on startup
        self.test_connection()
    
    def configure_styles(self):
        # Configure styles for dark theme
        self.style.configure('Title.TLabel', 
                           foreground=self.colors['accent'], 
                           background=self.colors['bg'],
                           font=('Arial', 16, 'bold'))
        
        self.style.configure('Heading.TLabel', 
                           foreground=self.colors['fg'], 
                           background=self.colors['bg'],
                           font=('Arial', 12, 'bold'))
        
        self.style.configure('Custom.TLabel', 
                           foreground=self.colors['fg'], 
                           background=self.colors['bg'],
                           font=('Arial', 10))
        
        self.style.configure('Custom.TButton',
                           foreground=self.colors['fg'],
                           background=self.colors['button_bg'],
                           font=('Arial', 10, 'bold'),
                           relief='flat',
                           borderwidth=1)
        
        self.style.map('Custom.TButton',
                      background=[('active', self.colors['accent']),
                                ('pressed', self.colors['red'])])
        
        self.style.configure('Custom.TFrame',
                           background=self.colors['bg'],
                           relief='solid',
                           borderwidth=1)
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, style='Custom.TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(title_frame, 
                              text="ALL IRELAND METAL PROJECT GUI APP", 
                              style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, 
                                 text="Search and explore Irish metal bands via The Irish Metal Archive", 
                                 style='Custom.TLabel')
        subtitle_label.pack()
        
        # Connection status
        self.status_label = ttk.Label(title_frame, 
                                    text="🌐 Testing connection...", 
                                    style='Custom.TLabel')
        self.status_label.pack(pady=(5, 0))
        
        # Search section
        search_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        search_frame.pack(fill='x', pady=(0, 10))
        
        search_label = ttk.Label(search_frame, text="🔍 Search Bands:", style='Heading.TLabel')
        search_label.pack(anchor='w')
        
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill='x', pady=(5, 0))
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_input_frame, 
                                   textvariable=self.search_var,
                                   bg=self.colors['entry_bg'],
                                   fg=self.colors['fg'],
                                   insertbackground=self.colors['fg'],
                                   font=('Arial', 12),
                                   relief='flat',
                                   bd=5)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.search_bands())
        
        search_btn = ttk.Button(search_input_frame, 
                              text="Search", 
                              command=self.search_bands,
                              style='Custom.TButton')
        search_btn.pack(side='right')
        
        random_btn = ttk.Button(search_input_frame, 
                              text="🎲 Random Band", 
                              command=self.find_random_band,
                              style='Custom.TButton')
        random_btn.pack(side='right', padx=(0, 10))
        
        # Year search section
        year_search_frame = ttk.Frame(search_frame)
        year_search_frame.pack(fill='x', pady=(10, 0))
        
        year_label = ttk.Label(year_search_frame, text="📅 Search For Releases By Year:", style='Heading.TLabel')
        year_label.pack(anchor='w')
        
        year_input_frame = ttk.Frame(year_search_frame)
        year_input_frame.pack(fill='x', pady=(5, 0))
        
        self.year_var = tk.StringVar()
        self.year_entry = tk.Entry(year_input_frame, 
                                 textvariable=self.year_var,
                                 bg=self.colors['entry_bg'],
                                 fg=self.colors['fg'],
                                 insertbackground=self.colors['fg'],
                                 font=('Arial', 12),
                                 relief='flat',
                                 bd=5,
                                 width=8)
        self.year_entry.pack(side='left', padx=(0, 10))
        self.year_entry.bind('<Return>', lambda e: self.search_albums_by_year())
        
        year_search_btn = ttk.Button(year_input_frame, 
                                   text="Search Albums", 
                                   command=self.search_albums_by_year,
                                   style='Custom.TButton')
        year_search_btn.pack(side='left')
        
        year_help_label = ttk.Label(year_input_frame, 
                                   text="(e.g. 2020, 1995, 2010)", 
                                   style='Custom.TLabel')
        year_help_label.pack(side='left', padx=(10, 0))
        
        # Results section
        results_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        results_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        results_label = ttk.Label(results_frame, text="📋 Results:", style='Heading.TLabel')
        results_label.pack(anchor='w')
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill='both', expand=True, pady=(5, 0))
        
        # Bands tab
        self.bands_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bands_frame, text="🎸 Bands")
        
        # Band listbox with scrollbar
        bands_list_frame = ttk.Frame(self.bands_frame)
        bands_list_frame.pack(fill='both', expand=True)
        
        self.bands_listbox = tk.Listbox(bands_list_frame,
                                      bg=self.colors['entry_bg'],
                                      fg=self.colors['fg'],
                                      selectbackground=self.colors['accent'],
                                      selectforeground=self.colors['bg'],
                                      font=('Arial', 10),
                                      relief='flat')
        self.bands_listbox.pack(side='left', fill='both', expand=True)
        self.bands_listbox.bind('<Double-1>', self.on_band_select)
        
        bands_scrollbar = ttk.Scrollbar(bands_list_frame, orient='vertical', command=self.bands_listbox.yview)
        bands_scrollbar.pack(side='right', fill='y')
        self.bands_listbox.configure(yscrollcommand=bands_scrollbar.set)
        
        # Details tab
        self.details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.details_frame, text="📝 Band Details")
        
        self.details_text = scrolledtext.ScrolledText(self.details_frame,
                                                    bg=self.colors['entry_bg'],
                                                    fg=self.colors['fg'],
                                                    font=('Arial', 11),
                                                    relief='flat',
                                                    wrap=tk.WORD,
                                                    cursor='arrow')
        self.details_text.pack(fill='both', expand=True)
        
        # Configure clickable URL styling
        self.details_text.tag_configure('url', foreground=self.colors['accent'], underline=True)
        self.details_text.tag_bind('url', '<Button-1>', self.open_url)
        self.details_text.tag_bind('url', '<Enter>', lambda e: self.details_text.config(cursor='hand2'))
        self.details_text.tag_bind('url', '<Leave>', lambda e: self.details_text.config(cursor='arrow'))
        
        # Albums tab
        self.albums_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.albums_frame, text="💿 Albums")
        
        self.albums_text = scrolledtext.ScrolledText(self.albums_frame,
                                                   bg=self.colors['entry_bg'],
                                                   fg=self.colors['fg'],
                                                   font=('Arial', 11),
                                                   relief='flat',
                                                   wrap=tk.WORD,
                                                   cursor='arrow')
        self.albums_text.pack(fill='both', expand=True)
        
        # Configure clickable URL styling
        self.albums_text.tag_configure('url', foreground=self.colors['accent'], underline=True)
        self.albums_text.tag_bind('url', '<Button-1>', self.open_url)
        self.albums_text.tag_bind('url', '<Enter>', lambda e: self.albums_text.config(cursor='hand2'))
        self.albums_text.tag_bind('url', '<Leave>', lambda e: self.albums_text.config(cursor='arrow'))
        
        # Bottom buttons
        bottom_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        bottom_frame.pack(fill='x')
        
        # Left side buttons
        left_buttons = ttk.Frame(bottom_frame, style='Custom.TFrame')
        left_buttons.pack(side='left')
        
        about_btn = ttk.Button(left_buttons, 
                              text="📖 About Project", 
                              command=self.open_about_page,
                              style='Custom.TButton')
        about_btn.pack(side='left', padx=(0, 10))
        
        community_btn = ttk.Button(left_buttons, 
                                 text="🌐 AllIrelandMetal.com", 
                                 command=self.visit_community,
                                 style='Custom.TButton')
        community_btn.pack(side='left')
        
        exit_btn = ttk.Button(bottom_frame, 
                            text="Exit", 
                            command=self.clean_shutdown,
                            style='Custom.TButton')
        exit_btn.pack(side='right')
    
    def on_closing(self):
        """Handle window close event with clean shutdown"""
        self.clean_shutdown()
    
    def clean_shutdown(self):
        """Perform clean shutdown with user confirmation"""
        if self.is_shutting_down:
            return
        
        # Ask for confirmation if there are running operations
        if self.running_threads and any(thread.is_alive() for thread in self.running_threads):
            response = messagebox.askyesno(
                "Confirm Exit", 
                "There are ongoing operations. Are you sure you want to exit?"
            )
            if not response:
                return
        
        self.is_shutting_down = True
        
        try:
            # Update status
            if hasattr(self, 'status_label'):
                self.status_label.configure(text="🔄 Shutting down...", foreground=self.colors['accent'])
            
            # Close any open connections
            if hasattr(self.archive, 'session'):
                self.archive.session.close()
            
            # Wait for threads to finish (with timeout)
            for thread in self.running_threads:
                if thread.is_alive():
                    thread.join(timeout=2.0)  # Wait max 2 seconds per thread
            
            # Clear references
            self.running_threads.clear()
            
            # Destroy the window
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            # Force quit if cleanup fails
            print(f"Error during shutdown: {e}")
            self.root.quit()
    
    def add_thread(self, thread):
        """Add thread to tracking list for clean shutdown"""
        self.running_threads.append(thread)
        # Clean up finished threads
        self.running_threads = [t for t in self.running_threads if t.is_alive()]

    def test_connection(self):
        def test():
            if self.is_shutting_down:
                return
            try:
                page = self.archive._get_page(BASE_URL)
                if not self.is_shutting_down:
                    if page:
                        self.root.after(0, lambda: self.status_label.configure(
                            text="✅ Connected to Irish Metal Archive", 
                            foreground=self.colors['accent']))
                    else:
                        self.root.after(0, lambda: self.status_label.configure(
                            text="❌ Connection failed", 
                            foreground=self.colors['red']))
            except:
                if not self.is_shutting_down:
                    self.root.after(0, lambda: self.status_label.configure(
                        text="❌ Connection failed", 
                        foreground=self.colors['red']))
        
        thread = threading.Thread(target=test, daemon=True)
        self.add_thread(thread)
        thread.start()
    
    def search_bands(self):
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term")
            return
        
        if self.is_shutting_down:
            return
        
        self.status_label.configure(text="🔍 Searching...", foreground=self.colors['fg'])
        
        def search():
            if self.is_shutting_down:
                return
            try:
                bands = self.archive.search_bands(search_term)
                if not self.is_shutting_down:
                    self.root.after(0, lambda: self.display_bands(bands, f"Search results for '{search_term}'"))
            except Exception as e:
                if not self.is_shutting_down:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Search failed: {str(e)}"))
                    self.root.after(0, lambda: self.status_label.configure(
                        text="❌ Search failed", foreground=self.colors['red']))
        
        thread = threading.Thread(target=search, daemon=True)
        self.add_thread(thread)
        thread.start()
    
    def search_albums_by_year(self):
        year_text = self.year_var.get().strip()
        if not year_text:
            messagebox.showwarning("Warning", "Please enter a year")
            return
        
        try:
            year = int(year_text)
            if year < 1950 or year > 2030:
                messagebox.showwarning("Warning", "Please enter a valid year (1950-2030)")
                return
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid year (numbers only)")
            return
        
        if self.is_shutting_down:
            return
        
        self.status_label.configure(text=f"📅 Searching albums from {year}...", foreground=self.colors['fg'])
        
        def search():
            if self.is_shutting_down:
                return
            try:
                albums = self.archive.search_albums_by_year(year)
                if not self.is_shutting_down:
                    self.root.after(0, lambda: self.display_year_albums(albums, year))
            except Exception as e:
                if not self.is_shutting_down:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Year search failed: {str(e)}"))
                    self.root.after(0, lambda: self.status_label.configure(
                        text="❌ Year search failed", foreground=self.colors['red']))
        
        thread = threading.Thread(target=search, daemon=True)
        self.add_thread(thread)
        thread.start()
    
    def find_random_band(self):
        if self.is_shutting_down:
            return
        
        self.status_label.configure(text="🎲 Finding random band...", foreground=self.colors['fg'])
        
        def find():
            if self.is_shutting_down:
                return
            try:
                band = self.archive.get_random_band()
                if not self.is_shutting_down:
                    if band:
                        bands = [band]
                        self.root.after(0, lambda: self.display_bands(bands, "Random band discovery"))
                        self.root.after(0, lambda: self.show_band_details(band))
                    else:
                        self.root.after(0, lambda: messagebox.showinfo("Info", "No random band found"))
            except Exception as e:
                if not self.is_shutting_down:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Random search failed: {str(e)}"))
                    self.root.after(0, lambda: self.status_label.configure(
                        text="❌ Random search failed", foreground=self.colors['red']))
        
        thread = threading.Thread(target=find, daemon=True)
        self.add_thread(thread)
        thread.start()
    
    def display_bands(self, bands, title):
        self.current_bands = bands
        self.bands_listbox.delete(0, tk.END)
        
        if bands:
            for i, band in enumerate(bands):
                self.bands_listbox.insert(tk.END, f"{i+1:2d}. {band.name}")
            self.status_label.configure(
                text=f"✅ Found {len(bands)} band(s)", 
                foreground=self.colors['accent'])
            self.notebook.select(0)  # Switch to bands tab
        else:
            self.bands_listbox.insert(tk.END, "No bands found")
            self.status_label.configure(
                text="❌ No bands found", 
                foreground=self.colors['red'])
    
    def on_band_select(self, event):
        selection = self.bands_listbox.curselection()
        if selection and self.current_bands:
            idx = selection[0]
            if idx < len(self.current_bands):
                band = self.current_bands[idx]
                self.show_band_details(band)
    
    def show_band_details(self, band):
        if self.is_shutting_down:
            return
        
        self.status_label.configure(text="📋 Getting band details...", foreground=self.colors['fg'])
        
        def get_details():
            if self.is_shutting_down:
                return
            try:
                detailed_band = self.archive.get_band_details(band)
                albums = self.archive.get_band_albums(detailed_band)
                
                if not self.is_shutting_down:
                    self.root.after(0, lambda: self.display_band_details(detailed_band))
                    self.root.after(0, lambda: self.display_albums(albums))
                    self.root.after(0, lambda: self.status_label.configure(
                        text="✅ Band details loaded", foreground=self.colors['accent']))
            except Exception as e:
                if not self.is_shutting_down:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to get details: {str(e)}"))
        
        thread = threading.Thread(target=get_details, daemon=True)
        self.add_thread(thread)
        thread.start()
    
    def display_band_details(self, band):
        self.details_text.delete(1.0, tk.END)
        
        details = f"🎸 BAND: {band.name}\n"
        details += "=" * 50 + "\n\n"
        
        if band.genre:
            details += f"🎵 Genre: {band.genre}\n"
        if band.county:
            details += f"📍 County: {band.county}\n"
        if band.year_formed:
            details += f"📅 Formed: {band.year_formed}\n"
        if band.description:
            details += f"\n📝 Description:\n{band.description}\n"
        
        # Insert text up to the URL
        self.details_text.insert(tk.END, details)
        
        # Add clickable URL
        if band.url:
            self.details_text.insert(tk.END, "\n🔗 URL: ")
            url_start = self.details_text.index(tk.END + "-1c")
            self.details_text.insert(tk.END, band.url)
            url_end = self.details_text.index(tk.END + "-1c") 
            self.details_text.tag_add('url', url_start, url_end)
            self.details_text.insert(tk.END, "\n")
        
        self.notebook.select(1)  # Switch to details tab
    
    def display_albums(self, albums):
        self.albums_text.delete(1.0, tk.END)
        
        if albums:
            albums_info = f"💿 ALBUMS/RELEASES ({len(albums)} found)\n"
            albums_info += "=" * 50 + "\n\n"
            
            self.albums_text.insert(tk.END, albums_info)
            
            for i, album in enumerate(albums, 1):
                # Insert album title
                self.albums_text.insert(tk.END, f"{i:2d}. {album.title}\n")
                
                if album.type:
                    self.albums_text.insert(tk.END, f"     Type: {album.type}\n")
                if album.year:
                    self.albums_text.insert(tk.END, f"     Year: {album.year}\n")
                
                # Add clickable URL if available
                if hasattr(album, 'url') and album.url:
                    self.albums_text.insert(tk.END, "     🔗 Link: ")
                    url_start = self.albums_text.index(tk.END + "-1c")
                    self.albums_text.insert(tk.END, album.url)
                    url_end = self.albums_text.index(tk.END + "-1c")
                    self.albums_text.tag_add('url', url_start, url_end)
                    self.albums_text.insert(tk.END, "\n")
                
                self.albums_text.insert(tk.END, "\n")
        else:
            albums_info = "💿 No albums found for this band"
            self.albums_text.insert(tk.END, albums_info)
    
    def display_year_albums(self, albums, year):
        """Display albums found for a specific year"""
        self.albums_text.delete(1.0, tk.END)
        
        if albums:
            albums_info = f"📅 ALBUMS RELEASED IN {year} ({len(albums)} found)\n"
            albums_info += "=" * 60 + "\n\n"
            
            self.albums_text.insert(tk.END, albums_info)
            
            for i, album in enumerate(albums, 1):
                self.albums_text.insert(tk.END, f"{i:2d}. {album.title}\n")
                if album.band and album.band != "Unknown":
                    self.albums_text.insert(tk.END, f"     Band: {album.band}\n")
                if album.type:
                    self.albums_text.insert(tk.END, f"     Type: {album.type}\n")
                self.albums_text.insert(tk.END, f"     Year: {album.year}\n")
                
                # Add clickable URL if available
                if hasattr(album, 'url') and album.url and album.url != BASE_URL:
                    self.albums_text.insert(tk.END, "     🔗 Link: ")
                    url_start = self.albums_text.index(tk.END + "-1c")
                    self.albums_text.insert(tk.END, album.url)
                    url_end = self.albums_text.index(tk.END + "-1c")
                    self.albums_text.tag_add('url', url_start, url_end)
                    self.albums_text.insert(tk.END, "\n")
                
                self.albums_text.insert(tk.END, "\n")
            
            self.status_label.configure(
                text=f"✅ Found {len(albums)} album(s) from {year}", 
                foreground=self.colors['accent'])
        else:
            albums_info = f"📅 No albums found for {year}\n\n"
            albums_info += "Try searching for different years or check if the year is correct."
            self.albums_text.insert(tk.END, albums_info)
            
            self.status_label.configure(
                text=f"❌ No albums found for {year}", 
                foreground=self.colors['red'])
        
        self.notebook.select(2)  # Switch to albums tab
    
    def open_url(self, event):
        """Open URL when clicked"""
        widget = event.widget
        # Get the index of the click
        index = widget.index(tk.CURRENT)
        # Get all URL tags at this position
        tags = widget.tag_names(index)
        
        if 'url' in tags:
            # Find the range of the URL tag
            ranges = widget.tag_ranges('url')
            for i in range(0, len(ranges), 2):
                start, end = ranges[i], ranges[i+1]
                if widget.compare(start, '<=', index) and widget.compare(index, '<', end):
                    url = widget.get(start, end)
                    try:
                        webbrowser.open(url)
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not open URL: {e}")
                    break

    def open_about_page(self):
        """Open the local about page in the default browser"""
        import os
        import pathlib
        
        # Get the absolute path to the HTML file
        script_dir = pathlib.Path(__file__).parent.absolute()
        html_file = script_dir / "about_project.html"
        
        if html_file.exists():
            try:
                # Convert to file URL for cross-platform compatibility
                file_url = html_file.as_uri()
                webbrowser.open(file_url)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open about page: {e}")
        else:
            messagebox.showerror("Error", "About page file not found")

    def visit_community(self):
        webbrowser.open("https://linktr.ee/AllIrelandMetal")
        messagebox.showinfo("Browser", "Opening All Ireland Metal community page in browser...")

def main():
    root = tk.Tk()
    app = IrishMetalGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()