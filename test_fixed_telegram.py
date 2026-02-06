#!/usr/bin/env python3
"""
Test fixed Telegram formatter
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing FIXED Telegram Formatter")
print("=" * 50)

try:
    from scrapers.adiga_scraper import LegacyAdigaScraper
    from telegram_formatter import TelegramFormatter, send_telegram_message
    
    scraper = LegacyAdigaScraper()
    programs = scraper.scrape()
    
    if programs:
        program = programs[0]
        formatter = TelegramFormatter()
        message = formatter.format_program(program)
        
        print(f"1. Title: {program.get('title', 'Unknown')}")
        print(f"2. URL: {program.get('url', 'No URL')}")
        print(f"\n3. Formatted message length: {len(message)} chars")
        print("\n4. Message preview (first 200 chars):")
        print("-" * 50)
        print(message[:200])
        print("-" * 50)
        
        print("\n5. Testing message validity...")
        # Check for common HTML issues
        issues = []
        if '<' in message and '>' in message:
            # Check for unescaped HTML
            import re
            tags = re.findall(r'<[^>]+>', message)
            valid_tags = ['<b>', '</b>', '<i>', '</i>', '<u>', '</u>', '<s>', '</s>', 
                         '<a href=', '</a>', '<code>', '</code>', '<pre>', '</pre>']
            for tag in tags:
                if not any(tag.startswith(valid) for valid in valid_tags):
                    issues.append(f"Invalid HTML tag: {tag}")
        
        if issues:
            print("⚠ Potential issues found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ Message looks valid")
        
        # Ask to send
        response = input("\nSend test message? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            print("Sending...")
            success = send_telegram_message(message)
            if success:
                print("✅ Telegram message sent successfully!")
                scraper.save_detected(programs)
            else:
                print("❌ Failed to send")
        else:
            print("Test cancelled")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete!")
