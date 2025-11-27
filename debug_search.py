#!/usr/bin/env python3
"""
Debug script to check what's happening with the Irish Metal Archive search
"""

import requests
import ssl
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

def test_website():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    })
    session.verify = False
    
    print("Testing Irish Metal Archive...")
    
    # Test main page
    try:
        response = session.get('https://irishmetalarchive.com/')
        print(f"Main page status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Main page accessible")
        else:
            print("❌ Main page not accessible")
            return
    except Exception as e:
        print(f"❌ Error accessing main page: {e}")
        return
    
    # Test artists page
    try:
        response = session.get('https://irishmetalarchive.com/artists/')
        print(f"Artists page status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Artists page accessible")
            
            # Look for band names in the content
            content = response.text.lower()
            test_bands = ['horrenda', 'primordial', 'mael mórdha', 'cruachan']
            
            print("\nLooking for test bands in artists page:")
            for band in test_bands:
                if band in content:
                    print(f"✅ Found '{band}' in page content")
                else:
                    print(f"❌ '{band}' not found in page content")
                    
            # Try to find any band links
            import re
            band_links = re.findall(r'href="[^"]*artists?/[^"]*"', response.text, re.IGNORECASE)
            print(f"\nFound {len(band_links)} potential artist links")
            if band_links:
                print("Sample links:")
                for link in band_links[:5]:
                    print(f"  {link}")
        else:
            print("❌ Artists page not accessible")
    except Exception as e:
        print(f"❌ Error accessing artists page: {e}")
    
    # Test searching for Horrenda specifically
    print(f"\n🔍 Testing search for 'Horrenda'...")
    try:
        # Try different potential search URLs
        search_urls = [
            'https://irishmetalarchive.com/search/?q=horrenda',
            'https://irishmetalarchive.com/?s=horrenda',
            'https://irishmetalarchive.com/artists/?search=horrenda'
        ]
        
        for url in search_urls:
            try:
                response = session.get(url)
                print(f"Search URL {url}: Status {response.status_code}")
                if response.status_code == 200 and 'horrenda' in response.text.lower():
                    print("✅ Found Horrenda in search results!")
                    break
            except:
                continue
                
    except Exception as e:
        print(f"❌ Error testing search: {e}")

if __name__ == "__main__":
    test_website()