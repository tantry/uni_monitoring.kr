#!/usr/bin/env python3
"""
Debug: Check what's in the hidden field
"""
import sys
import os
sys.path.insert(0, '.')

from scrapers.adiga_scraper_updated import LegacyAdigaScraper
import requests

print("Debugging hidden field content...")
print("=" * 60)

# Get first article URL
scraper = LegacyAdigaScraper()
articles = scraper.scrape()

if articles:
    article = articles[0]
    url = article.get('url')
    print(f"URL: {url}")
    
    # Fetch the page
    response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
    
    if response.status_code == 200:
        from bs4 import BeautifulSoup
        import html
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find hidden input
        hidden_input = soup.find('input', id='lnaCn1')
        if hidden_input:
            value = hidden_input.get('value', '')
            print(f"\nHidden field found!")
            print(f"Value length: {len(value)} chars")
            print(f"\nFirst 500 chars of raw value:")
            print("-" * 40)
            print(value[:500])
            print("-" * 40)
            
            # Decode and parse
            decoded = html.unescape(value)
            print(f"\nDecoded length: {len(decoded)} chars")
            
            inner_soup = BeautifulSoup(decoded, 'html.parser')
            text = inner_soup.get_text(separator=' ', strip=True)
            
            print(f"\nExtracted text length: {len(text)} chars")
            print(f"\nFirst 200 chars of text:")
            print("-" * 40)
            print(text[:200])
            print("-" * 40)
            
            # Look for specific elements
            print(f"\nLooking for specific tags:")
            if inner_soup.find('title'):
                print(f"  Title: {inner_soup.find('title').get_text(strip=True)}")
            
            # Count paragraphs
            paragraphs = inner_soup.find_all('p')
            print(f"  Paragraphs: {len(paragraphs)}")
            
            for i, p in enumerate(paragraphs[:3]):
                text = p.get_text(strip=True)
                if text:
                    print(f"  Para {i+1}: {text[:100]}...")
        
        else:
            print("❌ No hidden input found")
            
            # Look for other content
            popup = soup.find('div', id='newsPopCont')
            if popup:
                print(f"\nFound popup content, length: {len(popup.get_text())}")
                print(f"\nPopup text preview:")
                print(popup.get_text()[:200])
    
    else:
        print(f"❌ Failed to fetch: HTTP {response.status_code}")
else:
    print("❌ No articles found")
