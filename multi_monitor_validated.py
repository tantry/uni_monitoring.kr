#!/usr/bin/env python3
"""
Multi-source university admission monitor with URL validation
"""
import sys
import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import scrapers
from scrapers.adiga_scraper_fixed import LegacyAdigaScraper

# Import formatter and utilities
try:
    from telegram_formatter import TelegramFormatter
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    print("Warning: Telegram formatter not available")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultiSourceMonitor:
    """Monitor multiple university admission sources"""
    
    def __init__(self):
        self.scrapers = []
        self.initialize_scrapers()
        
    def initialize_scrapers(self):
        """Initialize all scraper instances"""
        logger.info("Initializing scrapers...")
        
        # Adiga.kr scraper
        try:
            adiga_scraper = LegacyAdigaScraper()
            self.scrapers.append({
                'name': 'adiga',
                'scraper': adiga_scraper,
                'display_name': 'Adiga (어디가)'
            })
            logger.info("✓ Adiga scraper initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Adiga scraper: {e}")
    
    def scrape_all(self) -> List[Dict[str, Any]]:
        """Scrape all sources"""
        all_programs = []
        
        for source in self.scrapers:
            scraper = source['scraper']
            source_name = source['name']
            display_name = source['display_name']
            
            logger.info(f"Scraping {display_name}...")
            
            try:
                programs = scraper.scrape()
                logger.info(f"  Found {len(programs)} programs from {display_name}")
                
                # Add source information to each program
                for program in programs:
                    program['source_name'] = display_name
                    program['source_id'] = source_name
                
                all_programs.extend(programs)
                
                # Save detected programs
                if programs:
                    scraper.save_detected(programs)
                    
            except Exception as e:
                logger.error(f"  Error scraping {display_name}: {e}")
        
        logger.info(f"Total programs found: {len(all_programs)}")
        return all_programs
    
    def find_new_programs(self) -> List[Dict[str, Any]]:
        """Find new programs across all sources"""
        all_new_programs = []
        
        for source in self.scrapers:
            scraper = source['scraper']
            display_name = source['display_name']
            
            try:
                # Get current programs
                current_programs = scraper.scrape()
                
                if current_programs:
                    # Find new ones
                    new_programs = scraper.find_new_programs(current_programs)
                    
                    if new_programs:
                        logger.info(f"Found {len(new_programs)} new programs from {display_name}")
                        
                        # Add source information
                        for program in new_programs:
                            program['source_name'] = display_name
                        
                        all_new_programs.extend(new_programs)
                        
                        # Save the new state
                        scraper.save_detected(current_programs)
                
            except Exception as e:
                logger.error(f"Error finding new programs from {display_name}: {e}")
        
        return all_new_programs
    
    def format_for_telegram(self, programs: List[Dict[str, Any]]) -> List[str]:
        """Format programs for Telegram"""
        if not HAS_TELEGRAM:
            logger.error("Telegram formatter not available")
            return []
        
        formatter = TelegramFormatter()
        messages = []
        
        for program in programs:
            try:
                message = formatter.format_program(program)
                
                # Add URL validation note if available
                metadata = program.get('metadata', {})
                if metadata.get('url_validated'):
                    message += "\n\n✅ 링크 검증 완료"
                
                messages.append(message)
                
            except Exception as e:
                logger.error(f"Error formatting program for Telegram: {e}")
        
        return messages
    
    def send_to_telegram(self, messages: List[str]) -> bool:
        """Send messages to Telegram"""
        if not HAS_TELEGRAM:
            logger.error("Cannot send to Telegram: formatter not available")
            return False
        
        try:
            from telegram_formatter import send_telegram_message
            
            success_count = 0
            for i, message in enumerate(messages):
                logger.info(f"Sending message {i+1}/{len(messages)} to Telegram...")
                
                if send_telegram_message(message):
                    success_count += 1
                    # Small delay to avoid rate limiting
                    if i < len(messages) - 1:
                        time.sleep(1)
                else:
                    logger.error(f"Failed to send message {i+1}")
            
            logger.info(f"Sent {success_count}/{len(messages)} messages to Telegram")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending to Telegram: {e}")
            return False
    
    def run_once(self, send_alerts: bool = True) -> bool:
        """Run one monitoring cycle"""
        logger.info("=" * 60)
        logger.info(f"Starting monitoring cycle at {datetime.now()}")
        logger.info("=" * 60)
        
        # Find new programs
        new_programs = self.find_new_programs()
        
        if not new_programs:
            logger.info("No new programs found")
            return True
        
        # Format for Telegram
        messages = self.format_for_telegram(new_programs)
        
        # Send to Telegram if requested
        if send_alerts and messages:
            logger.info(f"Sending {len(messages)} alerts to Telegram...")
            return self.send_to_telegram(messages)
        
        return True
    
    def run_continuous(self, interval_minutes: int = 60, send_alerts: bool = True):
        """Run continuously with specified interval"""
        logger.info(f"Starting continuous monitoring (interval: {interval_minutes} minutes)")
        
        while True:
            try:
                self.run_once(send_alerts)
                
                logger.info(f"Next check in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                logger.info(f"Retrying in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="University Admission Monitor")
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--interval', type=int, default=60, help='Interval in minutes (default: 60)')
    parser.add_argument('--no-alerts', action='store_true', help='Do not send Telegram alerts')
    
    args = parser.parse_args()
    
    # Create monitor
    monitor = MultiSourceMonitor()
    
    if args.once:
        # Run once
        monitor.run_once(send_alerts=not args.no_alerts)
    else:
        # Run continuously
        monitor.run_continuous(
            interval_minutes=args.interval,
            send_alerts=not args.no_alerts
        )

if __name__ == "__main__":
    main()
