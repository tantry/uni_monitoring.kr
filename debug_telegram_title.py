#!/usr/bin/env python3
"""
Debug why telegram_title isn't being set
"""
import sys
import os
sys.path.insert(0, '.')

from scrapers.adiga_fixed_completely import AdigaFixedScraper

print("Debugging telegram_title issue...")
print("=" * 60)

scraper = AdigaFixedScraper()

# Get raw articles before parsing
print("1. Checking fetch_articles() output...")
raw_articles = scraper.fetch_articles()

if raw_articles:
    raw_article = raw_articles[0]
    print(f"Raw article keys: {list(raw_article.keys())}")
    print(f"Has telegram_title in raw: {'telegram_title' in raw_article}")
    if 'telegram_title' in raw_article:
        print(f"telegram_title value: {raw_article['telegram_title']}")
    
    print(f"\n2. Checking parse_article() output...")
    parsed_article = scraper.parse_article(raw_article)
    print(f"Parsed article keys: {list(parsed_article.keys())}")
    print(f"Has telegram_title in parsed: {'telegram_title' in parsed_article}")
    if 'telegram_title' in parsed_article:
        print(f"telegram_title value: {parsed_article['telegram_title']}")
    
    print(f"\n3. Checking the actual data flow...")
    print(f"Raw article title: {raw_article.get('title')}")
    print(f"Raw telegram_title: {raw_article.get('telegram_title', 'NOT FOUND')}")
    
    # Manually check what should happen
    title = raw_article.get('title', '')
    expected_telegram_title = title.replace("'", "&#x27;")
    print(f"Expected telegram_title: {expected_telegram_title}")
    
    print(f"\n4. Testing the replacement logic...")
    test_title = "[입시의 정석] 정시 등록 오늘부터…'이중 등록' 유의해야"
    test_result = test_title.replace("'", "&#x27;")
    print(f"Test title: {test_title}")
    print(f"After replace: {test_result}")
    print(f"Single quote in original: {\"'\" in test_title}")
    print(f"Single quote in result: {\"'\" in test_result}")
    
else:
    print("❌ No articles found")

print(f"\n" + "=" * 60)
