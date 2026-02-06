#!/usr/bin/env python3
"""
Test the simple working scraper
"""
import sys
import os
sys.path.insert(0, '.')

print("Testing SIMPLE Adiga Scraper")
print("=" * 60)

from scrapers.adiga_simple_working import SimpleAdigaScraper

scraper = SimpleAdigaScraper()
articles = scraper.scrape()

print(f"Found {len(articles)} articles")

if articles:
    article = articles[0]
    print(f"\n📰 Article details:")
    print(f"Title: {article.get('title')}")
    print(f"Telegram title: {article.get('telegram_title', 'NOT SET')}")
    print(f"URL: {article.get('url')}")
    print(f"Content: {article.get('content', '')[:100]}...")
    
    # Check if telegram_title is actually set
    if article.get('telegram_title') and article['telegram_title'] != 'NOT SET':
        print(f"\n✅ SUCCESS: telegram_title is set!")
        print(f"   Original: {article.get('title')}")
        print(f"   Telegram: {article.get('telegram_title')}")
        
        # Check if single quote is replaced
        if "'" not in article['telegram_title'] and "&#x27;" in article['telegram_title']:
            print("✅ Single quote properly escaped for Telegram")
        else:
            print("⚠ Single quote not properly escaped")
    else:
        print(f"\n❌ FAILED: telegram_title is not set")
        
    # Check URL
    url = article.get('url')
    if url and 'prtlBbsId=' in url:
        print(f"✅ URL has correct parameter: {url}")
        
        # Test if URL works
        import requests
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ URL accessible: HTTP {response.status_code}")
        except:
            print(f"⚠ URL not accessible")
    else:
        print(f"❌ URL incorrect: {url}")
        
else:
    print("❌ No articles found")

print(f"\n" + "=" * 60)
