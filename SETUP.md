# Setup Guide

This guide will help you set up the Irish Metal Archive Search App for development or usage.

## Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd all-ireland-metal-project
```

### 2. Create a Virtual Environment (Recommended)

Creating a virtual environment isolates your project dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\\Scripts\\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

**Command Line Interface:**
```bash
python3 irish_metal_app.py
```

**Graphical User Interface:**
```bash
python3 irish_metal_gui.py
```

## Building an Executable

To create a standalone executable that doesn't require Python to be installed:

### Using the Build Script (macOS/Linux)

```bash
chmod +x build.sh
./build.sh
```

### Using the Python Build Script (Cross-platform)

```bash
python3 build_executable.py
```

### Manual PyInstaller Build

```bash
pip install pyinstaller
pyinstaller --onefile --console --name "IrishMetalApp" irish_metal_app.py
```

## Development

### Project Structure

- `irish_metal_app.py` - Main command-line application
- `irish_metal_gui.py` - GUI version of the application
- `requirements.txt` - Python dependencies
- `build.sh` - Build script for macOS/Linux
- `build_executable.py` - Cross-platform build script
- `test_*.py` - Test files

### Dependencies

The main dependencies are:
- `requests` - HTTP library for API calls
- `pyquery` - jQuery-like library for HTML parsing
- `lxml` - XML and HTML parser
- `urllib3` - HTTP client
- `cssselect` - CSS selectors for HTML parsing

## Troubleshooting

### SSL Certificate Issues

If you encounter SSL certificate errors, the app is configured to handle them automatically. However, if you experience issues, you may need to:

1. Update certificates: `pip install --upgrade certifi`
2. Check your internet connection
3. Verify the Irish Metal Archive website is accessible

### Virtual Environment Issues

If you have trouble with virtual environments:

1. Make sure Python is installed correctly
2. Try using `python3` instead of `python`
3. On some systems, use `virtualenv` instead of `venv`:
   ```bash
   pip install virtualenv
   virtualenv venv
   ```

### Import Errors

If you get import errors:

1. Make sure you've activated your virtual environment
2. Reinstall requirements: `pip install -r requirements.txt --force-reinstall`
3. Check Python version compatibility

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues or questions, please open an issue on the GitHub repository.