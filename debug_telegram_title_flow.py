#!/usr/bin/env python3
"""
Debug telegram_title flow
"""
import sys
import os
sys.path.insert(0, '.')

print("Debugging telegram_title flow...")
print("=" * 60)

# Import the scraper class directly
from scrapers.adiga_complete_fixed import AdigaCompleteScraper

scraper = AdigaCompleteScraper()

# Get raw articles before parsing
print("1. Checking fetch_articles() output...")
raw_articles = scraper.fetch_articles()

if raw_articles:
    raw_article = raw_articles[0]
    print(f"Raw article keys: {list(raw_article.keys())}")
    print(f"Has 'telegram_title': {'telegram_title' in raw_article}")
    print(f"Has 'title': {'title' in raw_article}")
    
    if 'telegram_title' in raw_article:
        print(f"telegram_title value: {raw_article['telegram_title']}")
        print(f"title value: {raw_article.get('title')}")
    
    print(f"\n2. Checking parse_article() output...")
    parsed_article = scraper.parse_article(raw_article)
    print(f"Parsed article keys: {list(parsed_article.keys())}")
    print(f"Has 'telegram_title' in parsed: {'telegram_title' in parsed_article}")
    
    if 'telegram_title' in parsed_article:
        print(f"telegram_title value: {parsed_article['telegram_title']}")
    
    print(f"\n3. Full parsed article:")
    for key, value in parsed_article.items():
        if key not in ['metadata', 'department']:
            print(f"  {key}: {value}")
    
    print(f"\n4. Checking the actual problem...")
    # The issue might be in how the article is returned
    print("Testing direct scrape() method...")
    final_articles = scraper.scrape()
    if final_articles:
        final_article = final_articles[0]
        print(f"Final article has telegram_title: {'telegram_title' in final_article}")
        if 'telegram_title' in final_article:
            print(f"Value: {final_article['telegram_title']}")

else:
    print("No articles found")

print(f"\n" + "=" * 60)
