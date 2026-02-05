#!/usr/bin/env python3
"""
Test the URL fix
"""

import sys
sys.path.append('scrapers')

print("🧪 TESTING URL FIX")
print("=" * 50)

try:
    # Import the fixed scraper
    from adiga_scraper import AdigaScraper
    
    scraper = AdigaScraper()
    print(f"✅ Scraper: {scraper.source_name}")
    
    # Fetch articles
    articles = scraper.fetch_articles()
    print(f"✅ Got {len(articles)} articles")
    
    if articles:
        print("\n📋 Article URLs (should NOT give 404):")
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title'][:40]}...")
            print(f"   URL: {article['url']}")
            print(f"   Pattern: {'✅ ArticleDetail.do' if 'ArticleDetail.do' in article['url'] else '❌ Wrong pattern'}")
            print()
        
        # Test if URLs look correct
        correct_urls = all('ArticleDetail.do?articleID=' in a['url'] for a in articles)
        if correct_urls:
            print("🎉 ALL URLs ARE CORRECTLY FORMATTED!")
            print("   They should not give 404 errors")
        else:
            print("⚠️ Some URLs still have wrong format")
            
except ImportError as e:
    print(f"❌ Cannot import: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("To run the monitor:")
print("rm -f state.json && python3 multi_monitor.py")
