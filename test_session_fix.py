#!/usr/bin/env python3
"""
Test session fix with Telegram
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Session Fix with Telegram")
print("=" * 50)

try:
    from scrapers.adiga_scraper import LegacyAdigaScraper
    from telegram_formatter import TelegramFormatter, send_telegram_message
    
    print("1. Creating scraper with session support...")
    scraper = LegacyAdigaScraper()
    
    print("2. Scraping articles (should be live now)...")
    programs = scraper.scrape()
    print(f"   Found {len(programs)} articles")
    
    if programs:
        new_programs = scraper.find_new_programs(programs)
        print(f"3. New programs found: {len(new_programs)}")
        
        if new_programs:
            program = new_programs[0]
            formatter = TelegramFormatter()
            message = formatter.format_program(program)
            
            print(f"\n4. Article details:")
            print(f"   Title: {program.get('title', 'Unknown')}")
            print(f"   URL: {program.get('url', 'No URL')}")
            print(f"   Method: {program.get('metadata', {}).get('scrape_method', 'unknown')}")
            print(f"\n   Message preview (first 100 chars):")
            print(f"   {message[:100]}...")
            
            # Ask before sending
            response = input("\nSend test Telegram alert? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                print("Sending...")
                success = send_telegram_message(message)
                if success:
                    print("✅ Telegram alert sent!")
                    print("   Check if link works in your channel")
                    scraper.save_detected(programs)
                else:
                    print("❌ Failed to send")
            else:
                print("Test cancelled")
        else:
            print("No new programs (state might exist)")
    else:
        print("No articles scraped")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete!")
