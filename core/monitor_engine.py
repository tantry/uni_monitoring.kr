#!/usr/bin/env python3
"""
University Admission Monitor - Main Engine
"""
import yaml
import logging
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.article import Article
from notifiers.telegram_notifier import TelegramNotifier

class MonitorEngine:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.telegram = TelegramNotifier(self.config['telegram'])
        self.db_path = self.config['database']['path']
        self.setup_database()
        
    def load_config(self, config_path: str) -> dict:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        log_config = self.config['logging']
        logging.basicConfig(
            level=log_config['level'],
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config['file']),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            source TEXT NOT NULL,
            department TEXT,
            sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash ON articles (hash)')
        conn.commit()
        conn.close()
    
    def is_duplicate(self, article_hash: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM articles WHERE hash = ?', (article_hash,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def mark_as_sent(self, article: Article):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO articles (hash, title, url, source, department)
            VALUES (?, ?, ?, ?, ?)
            ''', (article.get_hash(), article.title, article.url, article.source, article.department))
            conn.commit()
            self.logger.debug(f"Marked as sent: {article.title}")
        except Exception as e:
            self.logger.error(f"Error marking article: {e}")
        finally:
            conn.close()
    
    def load_filters(self) -> tuple:
        with open('config/filters.yaml', 'r') as f:
            filters_config = yaml.safe_load(f)
        global_min = filters_config.get('matching', {}).get('min_confidence', 0.10)
        keywords = {}
        configs = {}
        for dept, config in filters_config.get('departments', {}).items():
            keywords[dept] = config.get('keywords', [])
            configs[dept] = {
                'threshold': config.get('confidence_threshold', global_min),
                'priority': config.get('priority', 99)
            }
        return keywords, configs, global_min
    
    def filter_article(self, article: Article, filters: Dict[str, List[str]], configs: Dict, min_conf: float) -> str:
        """Filter article using minimum keyword matches for all departments"""
        text_to_check = f"{article.title} {article.content}".lower()
        
        matches = {}
        for dept, keywords in filters.items():
            keyword_matches = sum(1 for kw in keywords if kw.lower() in text_to_check)
            min_required = 2
            if keyword_matches >= min_required:
                matches[dept] = {
                    'matches': keyword_matches,
                    'priority': configs.get(dept, {}).get('priority', 99)
                }
        
        if not matches:
            return "general"
        
        best = max(matches.items(), key=lambda x: (x[1]['matches'], -x[1]['priority']))[0]
        return best

    def format_message(self, article: Article, department: str) -> str:
        """Format article as Telegram message with HTML links"""
        content = article.content
        if len(content) > 250:
            content = content[:247] + "..."

        message = f"""🎓 <b>[새 입학 공고] {article.title}</b>

📌 <b>부서/학과</b>: {department}
🔗 <a href="{article.url}">기사 보기</a>

<b>💡 URL 확인 - 열기:</b>
뉴스 링크 찾고 - 길게 누르고 - '다음으로 열기'

#대학입시 #{department}"""
        return message.strip()
    
    def test_scraping(self) -> List[Article]:
        self.logger.info("=== TEST MODE: Scraping without notifications ===")
        with open('config/sources.yaml', 'r') as f:
            sources_config = yaml.safe_load(f)
        articles = []
        if 'adiga' in sources_config.get('sources', {}):
            from scrapers.adiga_scraper import AdigaScraper
            adiga_config = sources_config['sources']['adiga']
            scraper = AdigaScraper(adiga_config)
            self.logger.info(f"Testing scraper: {scraper.get_source_name()}")
            scraped = scraper.scrape()
            articles.extend(scraped)
            for article in scraped:
                self.logger.info(f"  Found: {article.title}")
                if article.content:
                    self.logger.info(f"    Content preview: {article.content[:100]}...")
        return articles
    
    def run(self, test_mode: bool = False):
        self.logger.info("Starting University Admission Monitor")
        
        if not self.telegram.test_connection():
            self.logger.error("Telegram connection failed. Check bot token.")
            return
        
        self.logger.info("Telegram connection successful")
        
        with open('config/sources.yaml', 'r') as f:
            sources_config = yaml.safe_load(f)
        
        filters, configs, min_conf = self.load_filters()
        
        from core.scraper_factory import ScraperFactory
        factory = ScraperFactory()
        scrapers = factory.create_all_enabled()
        
        if not scrapers:
            self.logger.error("No scrapers configured or enabled")
            return
        
        all_articles = []
        for scraper in scrapers:
            self.logger.info(f"Scraping from {scraper.get_source_name()}")
            articles = scraper.scrape()
            all_articles.extend(articles)
            self.logger.info(f"Found {len(articles)} articles from {scraper.get_source_name()}")
        
        new_articles = []
        for article in all_articles:
            department = self.filter_article(article, filters, configs, min_conf)
            if department == "general":
                self.logger.debug(f"Skipping article with no department match: {article.title}")
                continue
            article.department = department
            if not self.is_duplicate(article.get_hash()):
                new_articles.append(article)
                self.mark_as_sent(article)
        
        if test_mode:
            self.logger.info(f"TEST MODE: Would send {len(new_articles)} notifications")
            for article in new_articles:
                message = self.format_message(article, article.department)
                self.logger.info(f"Would send:\n{message}\n")
        else:
            if new_articles:
                self.logger.info(f"Sending {len(new_articles)} notifications")
                for article in new_articles:
                    message = self.format_message(article, article.department)
                    if self.telegram.send_message(message, department=article.department):
                        self.logger.info(f"Notification sent: {article.title}")
                    else:
                        self.logger.error(f"Failed to send: {article.title}")
                    import time
                    time.sleep(1)
            else:
                self.logger.info("No new articles to notify")
        
        self.logger.info("Monitoring cycle completed")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='University Admission Monitor')
    parser.add_argument('--test', action='store_true', help='Test mode (no notifications)')
    parser.add_argument('--scrape-test', action='store_true', help='Test scraping only')
    args = parser.parse_args()
    monitor = MonitorEngine()
    if args.scrape_test:
        articles = monitor.test_scraping()
        print(f"\nTotal articles found: {len(articles)}")
    else:
        monitor.run(test_mode=args.test)

if __name__ == "__main__":
    main()
