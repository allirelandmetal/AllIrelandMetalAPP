# All Ireland Metal Project

A comprehensive Python application to search and explore Irish metal bands from [irishmetalarchive.com](https://irishmetalarchive.com/).

## Quick Start

1. **Download or clone the repository:**
   ```bash
   git clone <repository-url>
   cd All-Ireland-Metal-Project
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   python3 irish_metal_app.py
   ```

   Or run the GUI version:
   ```bash
   python3 irish_metal_gui.py
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
## Available Versions

This project includes two versions of the application:

### 1. Command Line Interface (CLI)
```bash
python irish_metal_app.py
```
- Simple text-based interface
- Menu-driven navigation
- Perfect for terminal users

### 2. Graphical User Interface (GUI)
```bash
python irish_metal_gui.py
```
- Modern tkinter-based interface
- Point-and-click navigation
- User-friendly for all users

## Example Output

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

## Building Executable

To create a standalone executable:

### Quick Build (macOS/Linux)
```bash
chmod +x build.sh
./build.sh
```

### Cross-platform Build
```bash
python build_executable.py
```

### Manual Build
```bash
pip install pyinstaller
pyinstaller --onefile --console --name "IrishMetalApp" irish_metal_app.py
```

## Project Structure

## Project Structure

```
All-Ireland-Metal-Project/
├── irish_metal_app.py      # CLI version
├── irish_metal_gui.py      # GUI version
├── requirements.txt        # Python dependencies
├── build.sh               # Build script (Unix)
├── build_executable.py    # Cross-platform build script
├── cleanup.sh             # Cleanup script
├── SETUP.md              # Detailed setup guide
├── test_*.py             # Test files
├── LICENSE               # MIT License
└── README.md             # This file
```

## About

This app provides access to the Irish Metal Archive, allowing users to discover and learn about Irish metal bands. It's designed to be simple, standalone, and require minimal setup.

The application scrapes data from [irishmetalarchive.com](https://irishmetalarchive.com/) to provide:
- Band search functionality
- Detailed band information
- Album and release data
- Member information
- Genre and location details

## License

See LICENSE file for details.

## Contributing

1. Fork or download the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

For detailed setup instructions, see `SETUP.md`.

