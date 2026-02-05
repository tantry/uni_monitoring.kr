#!/usr/bin/env python3
"""
Test the FINAL correct scraper
"""
import sys
sys.path.append('scrapers')

print("🧪 FINAL CORRECT SCRAPER TEST")
print("=" * 60)

# Import the scraper
scraper_code = open('scrapers/adiga_scraper_correct_final.py').read()
exec(scraper_code)

scraper = AdigaScraper()
print(f"✅ Scraper: {scraper.source_name}")

articles = scraper.fetch_articles()

print(f"\n📊 RESULTS: {len(articles)} articles")
print("=" * 50)

for i, article in enumerate(articles, 1):
    print(f"\n{i}. {article['title'][:50]}...")
    print(f"   ID: {article.get('article_id', 'N/A')}")
    print(f"   URL: {article['url']}")
    
    # Check URL format
    if 'ArticleDetail.do?articleID=' in article['url']:
        print("   ✅ URL: CORRECT (will not 404)")
    else:
        print("   ❌ URL: WRONG (will 404)")
    
    # Show content preview
    if article.get('content'):
        print(f"   📝 {article['content'][:70]}...")

# Summary
correct_count = sum(1 for a in articles if 'ArticleDetail.do?articleID=' in a['url'])
print(f"\n🎯 SUMMARY: {correct_count}/{len(articles)} have correct URLs")

if correct_count == len(articles):
    print("✅ ALL URLs ARE CORRECT! Telegram will work!")
else:
    print("⚠️ Some URLs may still have issues")

print("\n" + "=" * 60)
print("🚀 Ready to run: rm -f state.json && python3 multi_monitor.py")
