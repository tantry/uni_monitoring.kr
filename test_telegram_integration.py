#!/usr/bin/env python3
"""
Test Telegram integration with migrated AdigaScraper
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_telegram_config():
    print("Testing Telegram Configuration...")
    print("=" * 50)
    
    try:
        # Try to import config
        from config import BOT_TOKEN, CHAT_ID
        print(f"✅ BOT_TOKEN loaded: {'*' * 10}{BOT_TOKEN[-5:] if BOT_TOKEN else 'NOT SET'}")
        print(f"✅ CHAT_ID loaded: {CHAT_ID}")
        
        # Test telegram_formatter import
        try:
            from telegram_formatter import TelegramFormatter, send_telegram_message
            print("✅ telegram_formatter imports successful")
            
            # Create formatter
            formatter = TelegramFormatter()
            print("✅ TelegramFormatter instantiated")
            
            # Test with a sample article from migrated scraper
            print("\nTesting with migrated scraper article...")
            from scrapers.adiga_scraper import LegacyAdigaScraper
            
            scraper = LegacyAdigaScraper()
            programs = scraper.scrape()
            
            if programs:
                print(f"✅ Retrieved {len(programs)} articles from migrated scraper")
                
                # Get first article
                sample_article = programs[0]
                print(f"\nSample article from migrated scraper:")
                print(f"  Title: {sample_article.get('title', 'No title')[:50]}...")
                print(f"  URL: {sample_article.get('url', 'No URL')}")
                print(f"  Source: {sample_article.get('source', 'No source')}")
                
                # Test formatting
                try:
                    formatted_message = formatter.format_program(sample_article)
                    print(f"\n✅ Article formatted for Telegram")
                    print(f"Message preview (first 100 chars):")
                    print(f"  {formatted_message[:100]}...")
                    
                    # Test sending (optional - can be commented out for safety)
                    print("\n📤 Testing Telegram send (will only print, not actually send)")
                    print("To actually send, uncomment the send_telegram_message() call")
                    
                    # Uncomment to actually test sending:
                    # success = send_telegram_message(formatted_message)
                    # if success:
                    #     print("✅ Telegram message sent successfully!")
                    # else:
                    #     print("❌ Failed to send Telegram message")
                    
                except Exception as e:
                    print(f"❌ Formatting error: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ No articles retrieved from scraper")
                
        except ImportError as e:
            print(f"❌ Telegram formatter import error: {e}")
        except Exception as e:
            print(f"❌ Telegram test error: {e}")
            import traceback
            traceback.print_exc()
            
    except ImportError as e:
        print(f"❌ Config import error: {e}")
        print("\nMake sure config.py has:")
        print("  BOT_TOKEN = 'your_bot_token_here'")
        print("  CHAT_ID = 'your_chat_id_here'")
    
    print("\n" + "=" * 50)
    print("Telegram integration test complete")

if __name__ == "__main__":
    test_telegram_config()
