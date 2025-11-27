#!/usr/bin/env python3
"""
Simple build script for creating a macOS executable of the Irish Metal App
"""

import subprocess
import sys
import os
import shutil

def install_pyinstaller():
    """Install PyInstaller"""
    print("📦 Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install PyInstaller: {e}")
        return False

def install_requirements():
    """Install required packages"""
    print("📋 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def clean_build_directories():
    """Clean up previous build directories"""
    directories_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for directory in directories_to_clean:
        if os.path.exists(directory):
            print(f"🧹 Cleaning {directory}/")
            shutil.rmtree(directory)
    
    # Clean spec files
    for spec_file in ['irish_metal_app.spec', 'IrishMetalApp.spec']:
        if os.path.exists(spec_file):
            print(f"🧹 Removing {spec_file}")
            os.remove(spec_file)

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console", 
        "--name", "IrishMetalApp",
        "--hidden-import", "urllib3",
        "--hidden-import", "pyquery", 
        "--hidden-import", "lxml",
        "--hidden-import", "cssselect",
        "--hidden-import", "requests",
        "irish_metal_app.py"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Executable built successfully!")
            return True
        else:
            print("❌ Build failed:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during build: {e}")
        return False

def test_executable():
    """Test the built executable"""
    exe_path = "dist/IrishMetalApp"
    if os.path.exists(exe_path):
        # Make it executable
        os.chmod(exe_path, 0o755)
        
        print("✅ Executable created successfully!")
        print(f"📁 Location: {os.path.abspath(exe_path)}")
        print("\n🎯 You can now run the app with:")
        print(f"   {os.path.abspath(exe_path)}")
        print("\n📦 To distribute, copy the executable to other Macs")
        
        return True
    else:
        print("❌ Executable not found")
        return False

def main():
    """Main build process"""
    print("🎸 Irish Metal App - Executable Builder 🤘")
    print("=" * 50)
    
    # Install dependencies
    if not install_pyinstaller():
        return 1
    
    if not install_requirements():
        return 1
    
    # Clean previous builds
    clean_build_directories()
    
    # Build the executable
    if build_executable() and test_executable():
        print("\n🎉 Build completed successfully!")
        
        # Ask if user wants to test it
        test_now = input("\n🧪 Would you like to test the executable now? (y/n): ").strip().lower()
        if test_now == 'y':
            print("\nStarting the app... (Press Ctrl+C to exit)")
            try:
                subprocess.run(["./dist/IrishMetalApp"])
            except KeyboardInterrupt:
                print("\n✅ Test completed!")
        
        return 0
    else:
        print("\n❌ Build failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)