#!/usr/bin/env python3
"""
Main orchestrator for multi-source university admission monitoring
UPDATED: Uses LegacyAdigaScraper for backward compatibility with migrated architecture
"""
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import scrapers - UPDATED: Import LegacyAdigaScraper for backward compatibility
try:
    from scrapers.adiga_scraper import LegacyAdigaScraper
    HAS_ADIGA = True
    print("✅ Loaded LegacyAdigaScraper (migrated architecture)")
except ImportError as e:
    print(f"⚠ Adiga scraper import error: {e}")
    HAS_ADIGA = False

# Import utilities
from sources import SOURCE_CONFIG
from telegram_formatter import TelegramFormatter

# Import Telegram config
try:
    from config import BOT_TOKEN, CHAT_ID
    HAS_TELEGRAM_CONFIG = True
except ImportError:
    HAS_TELEGRAM_CONFIG = False
    print("⚠ Telegram config not found. Console-only mode.")

class MultiMonitor:
    """Main monitoring orchestrator"""
    
    def __init__(self, enable_telegram=True):
        self.enable_telegram = enable_telegram and HAS_TELEGRAM_CONFIG
        self.scrapers = []
        self.formatter = TelegramFormatter()
        
        self._init_scrapers()
    
    def _init_scrapers(self):
        """Initialize all available scrapers"""
        if HAS_ADIGA:
            # UPDATED: Use LegacyAdigaScraper for backward compatibility
            self.scrapers.append(LegacyAdigaScraper())
            print(f"✅ Loaded Adiga scraper (Legacy wrapper for migrated architecture)")
        
        print(f"📊 Total scrapers: {len(self.scrapers)}")
    
    def run_all(self):
        """Run all scrapers and process results"""
        print(f"\n🚀 Starting monitoring run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        all_programs = []
        all_new_programs = []
        
        for scraper in self.scrapers:
            source_name = scraper.source_config.get('name', scraper.source_name)
            print(f"\n🔍 {source_name}...")
            
            try:
                programs = scraper.scrape()
                
                if not programs:
                    print(f"   ℹ No programs found")
                    continue
                
                print(f"   ✅ Found {len(programs)} programs")
                
                new_programs = scraper.find_new_programs(programs)
                
                if new_programs:
                    print(f"   🎯 {len(new_programs)} new programs detected")
                    all_new_programs.extend(new_programs)
                    scraper.save_detected(programs)
                else:
                    print(f"   🔄 No new programs")
                
                all_programs.extend(programs)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n{'=' * 60}")
        print(f"📈 Run completed:")
        print(f"   Total programs found: {len(all_programs)}")
        print(f"   New programs detected: {len(all_new_programs)}")
        
        if all_new_programs and self.enable_telegram:
            self._send_telegram_alerts(all_new_programs)
        elif all_new_programs and not self.enable_telegram:
            print(f"\n📢 {len(all_new_programs)} new programs found (Telegram disabled)")
        
        return all_new_programs
    
    def _send_telegram_alerts(self, programs):
        """Send Telegram alerts for new programs"""
        print(f"\n📤 Sending Telegram alerts...")
        
        for program in programs:
            try:
                # Format message
                message = self.formatter.format_program(program)
                
                # Send to Telegram
                from telegram_formatter import send_telegram_message
                success = send_telegram_message(message)
                
                if success:
                    print(f"   ✅ Sent: {program.get('title', 'Unknown')[:50]}...")
                else:
                    print(f"   ❌ Failed to send")
                    
            except Exception as e:
                print(f"   ⚠ Telegram error: {e}")
                continue
    
    def run_once(self):
        """Run one monitoring cycle"""
        return self.run_all()


def main():
    """Main entry point"""
    monitor = MultiMonitor()
    monitor.run_all()


if __name__ == "__main__":
    main()
