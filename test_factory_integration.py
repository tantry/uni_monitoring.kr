#!/usr/bin/env python3
"""
Test integration of migrated AdigaScraper with ScraperFactory
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.scraper_factory import ScraperFactory

def test_factory_integration():
    print("Testing ScraperFactory Integration with AdigaScraper")
    print("=" * 60)
    
    try:
        # Create factory
        print("\n1. Creating ScraperFactory...")
        factory = ScraperFactory()
        
        # Check available sources
        print("\n2. Checking available sources...")
        sources = factory.get_available_sources()
        print(f"   Available sources: {sources}")
        
        # Check enabled sources
        enabled = factory.get_enabled_sources()
        print(f"   Enabled sources: {enabled}")
        
        if 'adiga' in enabled:
            print("\n3. Testing Adiga scraper creation...")
            
            # Create Adiga scraper
            scraper = factory.create_scraper('adiga')
            if scraper:
                print(f"   ✅ Successfully created scraper: {scraper.__class__.__name__}")
                print(f"   Display name: {scraper.display_name if hasattr(scraper, 'display_name') else 'N/A'}")
                print(f"   Base URL: {scraper.base_url}")
                
                # Test health
                print("\n4. Checking scraper health...")
                health = factory.get_scraper_health('adiga')
                print(f"   Health info: {health}")
                
                # Test scraping
                print("\n5. Testing scrape() method...")
                articles = scraper.scrape()
                print(f"   ✅ Scraped {len(articles)} articles")
                
                if articles:
                    print(f"   First article:")
                    print(f"     ID: {articles[0].get('id')}")
                    print(f"     Title: {articles[0].get('title')[:50]}...")
                    print(f"     URL: {articles[0].get('url')}")
                    
                    # Test state management
                    print("\n6. Testing state management...")
                    new_articles = scraper.find_new_programs(articles)
                    print(f"   New articles found: {len(new_articles)}")
                    
                    print("\n" + "=" * 60)
                    print("✅ Factory integration test passed!")
                    
                    # Show next steps
                    print("\nNext steps for full integration:")
                    print("1. Update multi_monitor.py to use ScraperFactory")
                    print("2. Create monitor_engine.py for new architecture")
                    print("3. Test Telegram notifications with new architecture")
                    print("4. Update check_now.sh to use new system")
            else:
                print("   ❌ Failed to create Adiga scraper")
        else:
            print("   ℹ️ Adiga source is not enabled in config/sources.yaml")
            
    except Exception as e:
        print(f"\n❌ Factory integration test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if 'factory' in locals():
            factory.cleanup()

if __name__ == "__main__":
    test_factory_integration()
