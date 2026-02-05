#!/usr/bin/env python3
"""
Test complete import chain
"""
import sys
sys.path.append('scrapers')

print("🧪 COMPLETE IMPORT TEST")
print("=" * 50)

try:
    # Test all imports
    import config
    print("✅ config.py")
    
    from filters import filter_by_department
    print("✅ filters.py")
    
    from telegram_formatter import TelegramFormatter
    print("✅ telegram_formatter.TelegramFormatter")
    
    from scrapers.adiga_scraper import AdigaScraper
    print("✅ scrapers.adiga_scraper.AdigaScraper")
    
    # Test instantiation
    formatter = TelegramFormatter()
    print("✅ TelegramFormatter instantiated")
    
    scraper = AdigaScraper()
    print(f"✅ Scraper: {scraper.source_name}")
    
    # Test message formatting
    msg = formatter.format_message("Test", "Content", "https://test.com", "music")
    print(f"✅ Message formatted ({len(msg)} chars)")
    
    # Test filtering
    test_article = {'title': '음악학과 공고', 'content': '음악'}
    dept = filter_by_department(test_article)
    print(f"✅ Filter test: {dept}")
    
    print("\n🎉 ALL TESTS PASSED!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
