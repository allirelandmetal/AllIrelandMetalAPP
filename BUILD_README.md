# Building Irish Metal App as macOS Executable

This guide explains how to create a standalone executable version of the Irish Metal App that can run natively on macOS without requiring Python to be installed.

## Quick Start

### Option 1: Using the Python Build Script (Recommended)

```bash
python build_executable.py
```

### Option 2: Using the Bash Script

```bash
./build.sh
```

### Option 3: Manual Build

```bash
# Install PyInstaller
pip install pyinstaller

# Install requirements
pip install -r requirements.txt

# Build the executable
pyinstaller --onefile --console --name "IrishMetalApp" irish_metal_app.py

# Your executable will be in dist/IrishMetalApp
```

## What You'll Get

After building, you'll have:
- `dist/IrishMetalApp` - A single executable file
- The executable is ~15-25MB and contains everything needed to run
- Works on any macOS system (no Python installation required)

## Distribution

To share your app:

1. **Simple Distribution**: Just copy the `dist/IrishMetalApp` file to another Mac
2. **Professional Distribution**: Code sign the executable (see below)

## Code Signing (Optional)

For distribution outside the Mac App Store:

```bash
# Sign the executable
codesign --force --sign "Developer ID Application: Your Name" dist/IrishMetalApp

# Verify the signature
codesign --verify --verbose dist/IrishMetalApp
```

## Creating a macOS App Bundle (.app)

To create a proper macOS application bundle:

```bash
pyinstaller --windowed --onedir --name "Irish Metal Archive Search" irish_metal_app.py
```

This creates `dist/Irish Metal Archive Search.app` that users can drag to Applications.

## Troubleshooting

### Build Fails
- Make sure you're in the virtual environment
- Install all requirements: `pip install -r requirements.txt`
- Try the manual build method

### Executable Won't Run
- Check macOS security settings (System Preferences → Security & Privacy)
- Try running from Terminal first: `./dist/IrishMetalApp`

### Large File Size
- The executable includes the Python interpreter and all dependencies
- This is normal for PyInstaller builds (15-25MB is typical)

## File Structure After Build

```
all-ireland-metal-project/
├── irish_metal_app.py          # Original source
├── build_executable.py         # Python build script
├── build.sh                   # Bash build script  
├── requirements.txt           # Dependencies
├── build/                     # Temporary build files
├── dist/
│   └── IrishMetalApp         # Your executable! 🎸
└── irish_metal_app.spec      # PyInstaller spec (auto-generated)
```

## Advanced Options

### Customize the Build

Edit the build script to add:
- Custom icon: `--icon=icon.icns`
- Hide console: `--windowed` 
- Include data files: `--add-data`
- Different name: `--name "CustomName"`

### Create App Store Version

For Mac App Store distribution, additional steps are needed:
1. Apple Developer account
2. Proper code signing certificates
3. App Store review process

## Performance Notes

- First startup might be slightly slower (2-3 seconds)
- Subsequent runs are fast
- Memory usage is similar to running the Python version directly

## Support

If you encounter issues:
1. Check the Terminal output for error messages
2. Verify all requirements are installed
3. Try the manual build process
4. Check macOS version compatibility (works on macOS 10.13+)

---

🎸🤘 Rock on with your distributable Irish Metal App! 🤘🎸