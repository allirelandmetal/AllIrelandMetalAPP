#!/usr/bin/env python3
"""
Quick test of the search functionality to verify the fix
"""

from irish_metal_app import IrishMetalArchive

def test_band_search():
    print("Testing band search functionality...")
    archive = IrishMetalArchive()
    
    # Test search for "horrenda"
    print("\n🔍 Testing search for 'horrenda'...")
    try:
        results = archive.search_bands("horrenda")
        print(f"✅ Search completed successfully!")
        print(f"📊 Found {len(results)} results")
        
        if results:
            print("\n🎵 Results:")
            for i, band in enumerate(results, 1):
                print(f"  {i}. {band.name}")
                if band.url:
                    print(f"     URL: {band.url}")
        else:
            print("❌ No bands found matching 'horrenda'")
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
    
    # Test search for a more common term
    print("\n🔍 Testing search for 'metal'...")
    try:
        results = archive.search_bands("metal")
        print(f"✅ Search completed successfully!")
        print(f"📊 Found {len(results)} results")
        
        if results:
            print("\n🎵 First 3 results:")
            for i, band in enumerate(results[:3], 1):
                print(f"  {i}. {band.name}")
                if band.url:
                    print(f"     URL: {band.url}")
        
    except Exception as e:
        print(f"❌ Error during search: {e}")

if __name__ == "__main__":
    test_band_search()