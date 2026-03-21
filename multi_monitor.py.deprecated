#!/usr/bin/env python3
"""
Main orchestrator for multi-source university admission monitoring
"""
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import scrapers
try:
    from scrapers.adiga_scraper import AdigaScraper
    HAS_ADIGA = True
except ImportError as e:
    print(f"⚠️ Adiga scraper import error: {e}")
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
    print("⚠️ Telegram config not found. Console-only mode.")

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
            self.scrapers.append(AdigaScraper())
            print(f"✅ Loaded Adiga scraper")
        
        print(f"📊 Total scrapers: {len(self.scrapers)}")
    
    def run_all(self):
        """Run all scrapers and return aggregated results"""
        print(f"\n🚀 Starting multi-source monitoring")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        all_programs = []
        all_new_programs = []
        
        for scraper in self.scrapers:
            source_name = scraper.source_config.get('name', scraper.source_name)
            print(f"\n🔍 {source_name}...")
            
            try:
                programs = scraper.scrape()
                
                if not programs:
                    print(f"   ℹ️ No programs found")
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
        
        return {
            'all_programs': all_programs,
            'new_programs': all_new_programs,
            'total_scrapers': len(self.scrapers),
            'timestamp': datetime.now().isoformat(),
        }
    
    def send_alerts(self, results):
        """Send alerts based on monitoring results"""
        new_programs = results.get('new_programs', [])
        
        if not new_programs:
            print("\n✅ No new programs to alert")
            return False
        
        print(f"\n📨 Preparing alerts for {len(new_programs)} new programs")
        
        message = self.formatter.format_alert(new_programs, "new_programs")
        
        if not message:
            print("❌ Failed to format alert message")
            return False
        
        if self.enable_telegram:
            return self._send_telegram_alert(message)
        else:
            print("\n" + "=" * 60)
            print("📱 CONSOLE ALERT (Telegram would send):")
            print("=" * 60)
            print(message)
            print("=" * 60)
            return True
    
    def _send_telegram_alert(self, message):
        """Send formatted message via Telegram"""
        try:
            import requests
            
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': CHAT_ID,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True,
            }
            
            response = requests.post(telegram_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Telegram alert sent")
                return True
            else:
                print(f"❌ Telegram error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send Telegram: {e}")
            return False
    
    def print_summary(self, results):
        """Print monitoring summary"""
        print("\n" + "=" * 50)
        print("📊 MONITORING SUMMARY")
        print("=" * 50)
        
        total_programs = len(results.get('all_programs', []))
        new_programs = len(results.get('new_programs', []))
        
        print(f"Scrapers run: {results.get('total_scrapers', 0)}")
        print(f"Total programs found: {total_programs}")
        print(f"New programs detected: {new_programs}")
        
        if new_programs > 0:
            print(f"\n🎯 NEW PROGRAMS BY SOURCE:")
            by_source = {}
            for program in results['new_programs']:
                source = program.get('source', 'unknown')
                by_source[source] = by_source.get(source, 0) + 1
            
            for source, count in by_source.items():
                source_name = SOURCE_CONFIG.get(source, {}).get('name', source)
                print(f"  {source_name}: {count}")
        
        print(f"\n⏰ Completed: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)

def main():
    """Main entry point"""
    enable_telegram = HAS_TELEGRAM_CONFIG
    
    if not enable_telegram:
        print("⚠️ Running in console-only mode (no Telegram alerts)")
        print("   Set BOT_TOKEN and CHAT_ID in config.py for alerts\n")
    
    monitor = MultiMonitor(enable_telegram=enable_telegram)
    
    results = monitor.run_all()
    
    if results.get('new_programs'):
        monitor.send_alerts(results)
    
    monitor.print_summary(results)
    
    return results

if __name__ == "__main__":
    main()
