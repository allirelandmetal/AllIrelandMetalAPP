# Quick Start Guide - Irish Metal Archive Search App

Your Irish Metal Archive search app is ready to use! 🎸

## ✅ What You Have

A single-file Python application that searches the Irish Metal Archive for Irish metal bands.

## 🚀 Quick Start

### 1. Install dependencies:
```bash
source metal/bin/activate  # If using virtual environment
pip install -r requirements.txt
```

### 2. Run the app:
```bash
python irish_metal_app.py
```

### 3. Use the interactive menu:
- **Option 1**: Search for specific bands
- **Option 2**: Browse all bands
- **Option 3**: Get detailed band information
- **Option 4**: Exit

## 📁 Clean Project Structure

```
all-ireland-metal-project/
├── metal/                    # Virtual environment
├── irish_metal_app.py       # Main application (standalone)
├── requirements.txt         # Dependencies
├── README.md               # Documentation
├── QUICKSTART.md           # This file
└── LICENSE                 # MIT License
```

## 🎯 Features

- ✅ **Single file app** - Everything in one Python file
- ✅ **No complex setup** - Just install requirements and run
- ✅ **Interactive menu** - Easy to use interface
- ✅ **Real data** - Scrapes live data from irishmetalarchive.com
- ✅ **Error handling** - Graceful handling of network issues
- ✅ **Respectful scraping** - Includes delays between requests

## 🛠️ How It Works

1. **Connects** to irishmetalarchive.com
2. **Scrapes** the artists page to get band lists
3. **Searches** through bands based on your input
4. **Fetches** detailed information from individual band pages
5. **Displays** results in a clean, readable format

## 🐛 Troubleshooting

### Network Issues
If you get connection errors:
- Check your internet connection
- The site might be temporarily down
- Try again in a few minutes

### Missing Dependencies
If you get import errors:
```bash
pip install requests pyquery
```

## 🎸 Happy Exploring!

Discover Irish metal bands and support the local scene! 🤘