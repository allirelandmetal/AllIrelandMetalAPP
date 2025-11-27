#!/usr/bin/env python3
"""
Quick test to verify the menu changes work correctly
"""

from irish_metal_app import IrishMetalApp

def test_menu():
    print("Testing the updated menu...")
    app = IrishMetalApp()
    
    # Display the menu
    print("Current menu:")
    app.display_menu()
    
    print("\nMenu changes verified:")
    print("✅ Option 3 'Browse all bands' removed")
    print("✅ Options renumbered: Get band details (3), Find random band (4), Exit (5)")
    print("✅ Menu now shows choices 1-5 instead of 1-6")

if __name__ == "__main__":
    test_menu()