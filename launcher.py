#!/usr/bin/env python3
"""
Launcher script for the Irish Metal App executable
This ensures proper initialization and error handling
"""

import sys
import os

def main():
    """Main launcher function"""
    try:
        # Add the current directory to the Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Import and run the main application
        from irish_metal_app import main as app_main
        app_main()
        
    except KeyboardInterrupt:
        print("\n\n🤘 Thanks for using The All Ireland Metal Search Tool!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()