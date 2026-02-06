#!/usr/bin/env python3
"""
Final system test with updated Adiga scraper
"""
import sys
import os
sys.path.insert(0, '.')

print("🚀 FINAL SYSTEM TEST: Updated Adiga Scraper")
print("=" * 60)

# Test 1: Import and create scraper
try:
    from scrapers.adiga_scraper_updated import LegacyAdigaScraper
    print("✅ Imported updated LegacyAdigaScraper")
    
    scraper = LegacyAdigaScraper()
    print("✅ Created scraper instance")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Scrape articles
print("\n📊 Testing scrape()...")
articles = scraper.scrape()

print(f"Found {len(articles)} articles")

if not articles:
    print("❌ No articles found")
    sys.exit(1)

# Test 3: Analyze first article
article = articles[0]
print(f"\n📰 First article analysis:")
print(f"Title: {article.get('title')}")
print(f"URL: {article.get('url')}")
print(f"Content length: {len(article.get('content', ''))} chars")

metadata = article.get('metadata', {})
print(f"Has actual content: {metadata.get('has_actual_content', False)}")
print(f"Extraction method: {metadata.get('content_extraction_method', 'unknown')}")
print(f"Article ID: {metadata.get('article_id', 'N/A')}")

# Test 4: Check URL structure
url = article.get('url')
if url:
    print(f"\n🔗 URL structure check:")
    print(f"URL: {url}")
    
    if 'prtlBbsId=' in url:
        print("✅ URL contains prtlBbsId parameter")
    
    if url.startswith('https://www.adiga.kr/uct/nmg/enw/newsDetail.do'):
        print("✅ URL uses correct detail endpoint")
    
    # Test URL accessibility
    import requests
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        print(f"URL accessibility: HTTP {response.status_code}")
        
        if response.status_code == 200:
            print("✅ URL is accessible")
            
            # Check for content
            if len(response.text) > 1000:
                print("✅ Page has substantial content")
                
                # Check for hidden field
                if 'lnaCn1' in response.text:
                    print("✅ Page contains hidden content field")
                else:
                    print("⚠ No hidden field found")
        else:
            print(f"⚠ URL returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ URL test error: {e}")

# Test 5: Telegram formatting
print(f"\n📱 Testing Telegram formatting...")
try:
    from telegram_formatter import TelegramFormatter
    formatter = TelegramFormatter()
    telegram_msg = formatter.format_program(article)
    
    print(f"Telegram message length: {len(telegram_msg)} chars")
    
    # Check for key elements
    checks = {
        'Contains title': article.get('title') in telegram_msg,
        'Contains URL': url in telegram_msg if url else False,
        'Contains article ID': metadata.get('article_id', '') in telegram_msg,
        'Has navigation instructions': 'Adiga.kr 페이지 안내' in telegram_msg,
        'Reasonable length': 100 < len(telegram_msg) < 4096
    }
    
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
    
    print(f"\n📝 Telegram preview:")
    print("-" * 40)
    print(telegram_msg[:200] + "..." if len(telegram_msg) > 200 else telegram_msg)
    print("-" * 40)
    
except Exception as e:
    print(f"❌ Telegram formatting failed: {e}")

print(f"\n" + "=" * 60)
print("🎯 TEST COMPLETE")

# Summary
print(f"\n📋 SUMMARY:")
print(f"Articles found: {len(articles)}")
print(f"Content extracted: {metadata.get('has_actual_content', False)}")
print(f"URL works: {'prtlBbsId=' in url if url else False}")

if metadata.get('has_actual_content') and url and 'prtlBssId=' in url:
    print("\n✅ SYSTEM READY: Telegram alerts will work with actual content!")
else:
    print("\n⚠ SYSTEM NEEDS ADJUSTMENT: Some components not working")

print(f"\n" + "=" * 60)
