#!/usr/bin/env python3
"""
Send ONE Telegram alert to test
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing ONE Telegram Alert")
print("=" * 50)

try:
    from scrapers.adiga_scraper import LegacyAdigaScraper
    from telegram_formatter import TelegramFormatter, send_telegram_message
    
    print("1. Creating scraper...")
    scraper = LegacyAdigaScraper()
    
    print("2. Scraping articles...")
    programs = scraper.scrape()
    print(f"   Found {len(programs)} articles")
    
    if programs:
        new_programs = scraper.find_new_programs(programs)
        print(f"3. New programs found: {len(new_programs)}")
        
        if new_programs:
            # Just send the FIRST one
            program = new_programs[0]
            formatter = TelegramFormatter()
            message = formatter.format_program(program)
            
            print("\n4. SENDING Telegram alert...")
            print(f"   Title: {program.get('title', 'Unknown')}")
            print(f"   URL: {program.get('url', 'No URL')}")
            print("\n   Message preview:")
            print("   " + "-"*40)
            print(f"   {message[:150]}...")
            print("   " + "-"*40)
            
            # Ask for confirmation
            response = input("\nSend this Telegram alert? (yes/no): ")
            
            if response.lower() in ['yes', 'y']:
                print("Sending...")
                success = send_telegram_message(message)
                
                if success:
                    print("\n✅ Telegram alert sent successfully!")
                else:
                    print("\n❌ Failed to send Telegram alert")
                
                # Save state
                scraper.save_detected(programs)
                print("State saved - this won't be sent again")
            else:
                print("Cancelled - no message sent")
        else:
            print("No new programs found")
    else:
        print("No articles scraped")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete!")
