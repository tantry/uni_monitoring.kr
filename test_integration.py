#!/usr/bin/env python3
"""
Test integration of all components after refactoring
"""

import sys
import os

print("🧪 INTEGRATION TEST - POST REFACTORING")
print("=" * 50)

# Test 1: Import chain
print("\n1. Testing import chain...")
try:
    import config
    print("   ✅ config.py")
    
    from filters import filter_by_department, DEPARTMENT_KEYWORDS
    print("   ✅ filters.py")
    
    from telegram_formatter import format_telegram_message
    print("   ✅ telegram_formatter.py")
    
    from scrapers.adiga_scraper import AdigaScraper
    print("   ✅ scrapers.adiga_scraper")
    
    from scrapers.scraper_base import BaseScraper
    print("   ✅ scrapers.scraper_base")
    
    print("   ✅ ALL MODULES IMPORT SUCCESSFULLY")
    
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Test filter function
print("\n2. Testing filter function...")
test_article = {
    'title': '서울대학교 음악학과 추가모집 공고',
    'content': '음악학과에서 추가모집을 실시합니다.',
    'url': 'https://example.com'
}

department = filter_by_department(test_article)
print(f"   Test article title: {test_article['title']}")
print(f"   Detected department: {department}")
print(f"   ✅ Filter working" if department else "   ❌ Filter not detecting department")

# Test 3: Test message formatting
print("\n3. Testing Telegram formatting...")
try:
    formatted = format_telegram_message(
        "Test University 음악학과",
        "Test admission announcement",
        "https://test.com",
        "music"
    )
    print(f"   Formatted message length: {len(formatted)} chars")
    print(f"   First line: {formatted.split('\\n')[0]}")
    print("   ✅ Formatting working")
except Exception as e:
    print(f"   ❌ Formatting failed: {e}")

# Test 4: Test scraper initialization
print("\n4. Testing scraper...")
try:
    scraper = AdigaScraper()
    print(f"   Scraper name: {scraper.source_name}")
    print(f"   Scraper URL: {scraper.base_url}")
    print("   ✅ Scraper initialized")
    
    # Test fetch without actual HTTP call
    print(f"   Fetch method exists: {hasattr(scraper, 'fetch_articles')}")
    
except Exception as e:
    print(f"   ❌ Scraper failed: {e}")

# Test 5: Test actual Telegram connection
print("\n5. Testing Telegram API...")
try:
    import requests
    
    # Simple test - get bot info
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getMe"
    response = requests.get(url, timeout=5)
    
    if response.status_code == 200:
        print(f"   ✅ Telegram API accessible")
        print(f"   Bot: {response.json()['result']['username']}")
    else:
        print(f"   ❌ Telegram API error: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Telegram test failed: {e}")

print("\n" + "=" * 50)
print("🎯 INTEGRATION TEST COMPLETE")
print("\nTo run the fixed monitor:")
print("python3 multi_monitor_fixed.py")
print("\nTo test with debug output:")
print("python3 multi_monitor_fixed.py 2>&1 | grep -E '(Sending|✅|❌|KEPT|Filtered)'")
