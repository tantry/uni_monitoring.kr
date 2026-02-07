#!/usr/bin/env python3
"""
Monitor engine with JavaScript support
"""
import yaml
import logging
import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.article import Article
from scrapers.adiga_js_scraper import AdigaJsScraper
from notifiers.telegram_notifier import TelegramNotifier

class JsMonitorEngine:
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
        except Exception as e:
            self.logger.error(f"Error marking article: {e}")
        finally:
            conn.close()
    
    def load_filters(self) -> Dict[str, List[str]]:
        with open('config/filters.yaml', 'r') as f:
            filters = yaml.safe_load(f)
        
        department_filters = {}
        for dept, config in filters.get('departments', {}).items():
            department_filters[dept] = config.get('keywords', [])
        
        return department_filters
    
    def filter_article(self, article: Article, filters: Dict[str, List[str]]) -> str:
        text_to_check = f"{article.title} {article.content}".lower()
        
        for department, keywords in filters.items():
            for keyword in keywords:
                if keyword.lower() in text_to_check:
                    return department
        
        return "general"
    
    def format_message(self, article: Article, department: str) -> str:
        content = article.content
        if len(content) > 300:
            content = content[:297] + "..."
        
        message = f"""
🎓 <b>새 입학 공고</b>

<b>제목:</b> {article.title}

<b>부서:</b> {department}
<b>내용:</b> {content}

<b>링크:</b> {article.url}

<b>출처:</b> {article.source}
#{department} #{article.source}
"""
        return message.strip()
    
    def run(self, test_mode: bool = False):
        self.logger.info("Starting JavaScript-aware Monitor")
        
        # Test Telegram
        if not self.telegram.test_connection():
            self.logger.error("Telegram connection failed")
            return
        
        self.logger.info("Telegram connection successful")
        
        # Load configs
        with open('config/sources.yaml', 'r') as f:
            sources_config = yaml.safe_load(f)
        
        department_filters = self.load_filters()
        
        # Initialize scraper
        scrapers = []
        if 'adiga' in sources_config.get('sources', {}):
            adiga_config = sources_config['sources']['adiga']
            if adiga_config.get('enabled', True):
                self.logger.info("Initializing Adiga JavaScript scraper...")
                scrapers.append(AdigaJsScraper(adiga_config))
        
        if not scrapers:
            self.logger.error("No scrapers configured")
            return
        
        # Scrape
        all_articles = []
        for scraper in scrapers:
            self.logger.info(f"Scraping from {scraper.get_source_name()}")
            articles = scraper.scrape()
            all_articles.extend(articles)
            self.logger.info(f"Found {len(articles)} articles from {scraper.get_source_name()}")
        
        # Filter and process
        new_articles = []
        for article in all_articles:
            department = self.filter_article(article, department_filters)
            article.department = department
            
            if not self.is_duplicate(article.get_hash()):
                new_articles.append(article)
                self.mark_as_sent(article)
        
        # Send notifications
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
                    if self.telegram.send_message(message):
                        self.logger.info(f"Notification sent: {article.title}")
                    else:
                        self.logger.error(f"Failed to send: {article.title}")
                    
                    import time
                    time.sleep(1)
            else:
                self.logger.info("No new articles to notify")
        
        self.logger.info("Monitoring completed")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='JavaScript-aware Monitor')
    parser.add_argument('--test', action='store_true', help='Test mode (no notifications)')
    
    args = parser.parse_args()
    
    monitor = JsMonitorEngine()
    monitor.run(test_mode=args.test)

if __name__ == "__main__":
    main()
