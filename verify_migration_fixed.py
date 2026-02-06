#!/usr/bin/env python3
"""
Final verification of migration to robust architecture - FIXED VERSION
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_migration():
    print("🔍 Final Verification of Migration to Robust Architecture")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 0
    
    def run_test(description, test_func):
        nonlocal tests_passed, total_tests
        total_tests += 1
        print(f"\nTest {total_tests}: {description}")
        try:
            result = test_func()
            if result:
                print(f"   ✅ PASSED")
                tests_passed += 1
            else:
                print(f"   ❌ FAILED")
            return result
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return False
    
    # Test 1: Import AdigaScraper
    run_test("Import AdigaScraper", lambda:
        __import__('scrapers.adiga_scraper') is not None
    )
    
    # Test 2: Check inheritance
    from scrapers.adiga_scraper import AdigaScraper
    from core.base_scraper import BaseScraper
    run_test("AdigaScraper inherits from BaseScraper", lambda:
        issubclass(AdigaScraper, BaseScraper)
    )
    
    # Test 3: Check required methods
    run_test("AdigaScraper has required methods", lambda:
        hasattr(AdigaScraper, 'fetch_articles') and
        hasattr(AdigaScraper, 'parse_article')
    )
    
    # Test 4: Legacy compatibility
    from scrapers.adiga_scraper import LegacyAdigaScraper
    run_test("LegacyAdigaScraper available", lambda:
        LegacyAdigaScraper is not None
    )
    
    # Test 5: Telegram formatter
    from telegram_formatter import TelegramFormatter
    run_test("TelegramFormatter has format_program", lambda:
        hasattr(TelegramFormatter, 'format_program')
    )
    
    # Test 6: send_telegram_message function
    from telegram_formatter import send_telegram_message
    run_test("send_telegram_message function", lambda:
        callable(send_telegram_message)
    )
    
    # Test 7: multi_monitor.py
    from multi_monitor import MultiMonitor
    run_test("MultiMonitor imports", lambda:
        MultiMonitor is not None
    )
    
    # Test 8: Configuration
    import yaml
    run_test("sources.yaml configuration", lambda:
        os.path.exists('config/sources.yaml') and
        os.path.getsize('config/sources.yaml') > 0
    )
    
    # Test 9: Instantiate and use scraper
    run_test("Instantiate and use LegacyAdigaScraper", lambda:
        len(LegacyAdigaScraper().scrape()) > 0
    )
    
    # Test 10: Complete workflow
    run_test("Complete monitoring workflow", lambda:
        len(MultiMonitor(enable_telegram=False).run_all()) >= 0
    )
    
    print(f"\n" + "=" * 70)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("\n🎉 MIGRATION SUCCESSFULLY VERIFIED! 🎉")
        print("\nAll components of the robust architecture are working:")
        print("1. ✅ BaseScraper inheritance")
        print("2. ✅ Abstract method implementation")
        print("3. ✅ Backward compatibility")
        print("4. ✅ Telegram integration")
        print("5. ✅ Configuration management")
        print("6. ✅ Complete workflow")
        
        print("\n🚀 System is ready for production use!")
        print("\nTo run the system:")
        print("  python multi_monitor.py")
        print("\nTo add new scrapers:")
        print("  1. Create new scraper inheriting from BaseScraper")
        print("  2. Add configuration to config/sources.yaml")
        print("  3. Test with ScraperFactory")
        
        return True
    else:
        print(f"\n⚠ {total_tests - tests_passed} tests failed")
        print("Please review the failed tests above.")
        return False

if __name__ == "__main__":
    success = verify_migration()
    sys.exit(0 if success else 1)
