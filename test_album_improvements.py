#!/usr/bin/env python3
"""
Test script for the improved album search functionality
"""

from irish_metal_app import IrishMetalArchive

def test_album_search_improvements():
    print("Testing improved album search functionality...")
    print("=" * 60)
    
    archive = IrishMetalArchive()
    
    # Test 1: Basic album search
    print("\n🧪 Test 1: Basic album search for 'metal'")
    try:
        results = archive.search_albums("metal")
        print(f"✅ Found {len(results)} albums")
        
        if results:
            print("\n📊 First 3 results:")
            for i, album in enumerate(results[:3], 1):
                print(f"  {i}. {album.title}")
                if album.band:
                    print(f"     Band: {album.band}")
                if album.type:
                    print(f"     Type: {album.type}")
                if album.year:
                    print(f"     Year: {album.year}")
                if album.genre:
                    print(f"     Genre: {album.genre}")
                print()
    except Exception as e:
        print(f"❌ Error in basic search: {e}")
    
    # Test 2: Search with band filter
    print("\n🧪 Test 2: Album search with band filter")
    try:
        results = archive.search_albums("metal", band_filter="primordial")
        print(f"✅ Found {len(results)} albums by bands containing 'primordial'")
        
        if results:
            print("\n📊 Results:")
            for i, album in enumerate(results, 1):
                print(f"  {i}. {album.title} - {album.band}")
                if album.type:
                    print(f"     Type: {album.type}")
                if album.year:
                    print(f"     Year: {album.year}")
                print()
    except Exception as e:
        print(f"❌ Error in band filter search: {e}")
    
    # Test 3: Search albums by band
    print("\n🧪 Test 3: Search albums by specific band")
    try:
        results = archive.search_albums_by_band("primordial")
        print(f"✅ Found {len(results)} albums by 'primordial'")
        
        if results:
            print("\n📊 Results:")
            for i, album in enumerate(results, 1):
                print(f"  {i}. {album.title}")
                if album.type:
                    print(f"     Type: {album.type}")
                if album.year:
                    print(f"     Year: {album.year}")
                print()
    except Exception as e:
        print(f"❌ Error in band-specific search: {e}")
    
    # Test 4: Album details
    print("\n🧪 Test 4: Get album details")
    try:
        # Get some albums first
        albums = archive.search_albums("storm")
        if albums:
            print(f"✅ Testing album details for: {albums[0].title}")
            detailed_album = archive.get_album_details(albums[0])
            
            print(f"\n📊 Album Details:")
            print(f"  Title: {detailed_album.title}")
            print(f"  Band: {detailed_album.band}")
            print(f"  Type: {detailed_album.type}")
            print(f"  Year: {detailed_album.year}")
            print(f"  Genre: {detailed_album.genre}")
            if detailed_album.description:
                print(f"  Description: {detailed_album.description[:100]}...")
        else:
            print("❌ No albums found to test details")
    except Exception as e:
        print(f"❌ Error getting album details: {e}")
    
    # Test 5: Deduplication
    print("\n🧪 Test 5: Test deduplication")
    try:
        results1 = archive.search_albums("darkness")
        results2 = archive.search_albums("dark")
        
        print(f"✅ Search 'darkness': {len(results1)} results")
        print(f"✅ Search 'dark': {len(results2)} results")
        
        # Check for potential duplicates
        titles1 = set([r.title.lower() for r in results1])
        titles2 = set([r.title.lower() for r in results2])
        overlap = titles1.intersection(titles2)
        
        print(f"📊 Overlapping titles: {len(overlap)}")
        if overlap:
            print(f"  Examples: {list(overlap)[:3]}")
            
    except Exception as e:
        print(f"❌ Error in deduplication test: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Album search improvement tests completed!")

if __name__ == "__main__":
    test_album_search_improvements()