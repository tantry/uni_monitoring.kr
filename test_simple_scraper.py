#!/usr/bin/env python3
"""
Test the simple scraper
"""
import sys
sys.path.append('scrapers')

try:
    from adiga_scraper import AdigaScraper
    
    scraper = AdigaScraper()
    print(f"✅ Scraper loaded: {scraper.source_name}")
    
    articles = scraper.fetch_articles()
    
    print(f"\n📋 Found {len(articles)} articles:")
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title'][:40]}...")
        print(f"   URL: {article['url']}")
        
        # Check if URL is correct
        if 'ArticleDetail.do?articleID=' in article['url']:
            print("   ✅ URL is CORRECT (should work!)")
        else:
            print("   ❌ URL is WRONG (will 404)")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
