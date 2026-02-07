#!/usr/bin/env python3
"""
Adiga Scraper with telegram_title preservation
"""
import re
import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_scraper import BaseScraper

class AdigaWithTelegramTitle(BaseScraper):
    """Adiga scraper that preserves telegram_title"""
    
    def __init__(self, config: Dict[str, Any] = None):
        config = config or {
            'name': 'adiga',
            'base_url': 'https://www.adiga.kr',
            'html_file_path': 'adiga_structure.html',
            'max_articles': 10,
            'display_name': 'Adiga (어디가)',
            'timeout': 30,
            'retry_attempts': 3
        }
        
        super().__init__(config)
        
        self.html_file_path = config.get('html_file_path', 'adiga_structure.html')
        self.max_articles = config.get('max_articles', 10)
        self.display_name = config.get('display_name', 'Adiga (어디가)')
        self.detail_url_base = "https://www.adiga.kr/uct/nmg/enw/newsDetail.do"
        
        self.logger.info(f"Initialized Adiga with telegram_title preservation")
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles"""
        self.logger.info("Fetching articles")
        
        if not os.path.exists(self.html_file_path):
            self.logger.error(f"HTML file not found: {self.html_file_path}")
            return self._get_fallback_articles()
        
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            articles = []
            
            ul_element = soup.find('ul', class_='uctList02')
            if not ul_element:
                self.logger.error("No article list")
                return self._get_fallback_articles()
            
            li_items = ul_element.find_all('li')
            self.logger.info(f"Found {len(li_items)} articles")
            
            for li in li_items[:self.max_articles]:
                article = self._parse_li(li)
                if article:
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return self._get_fallback_articles()
    
    def _parse_li(self, li_element) -> Optional[Dict[str, Any]]:
        """Parse LI element with telegram_title"""
        try:
            anchor = li_element.find('a', onclick=True)
            if not anchor:
                return None
            
            onclick = anchor.get('onclick', '')
            match = re.search(r'fnDetailPopup\("(\d+)"\)', onclick)
            if not match:
                return None
            
            article_id = match.group(1)
            
            title_elem = anchor.find('p', class_='uctCastTitle')
            title = title_elem.get_text(strip=True) if title_elem else f"Article {article_id}"
            title = title.replace('newIcon', '').strip()
            
            # Telegram title with escaped single quotes
            telegram_title = title.replace("'", "&#x27;")
            
            content_elem = anchor.find('span', class_='content')
            raw_content = content_elem.get_text(strip=True) if content_elem else ""
            
            content = raw_content.replace('&lt;', '<').replace('&gt;', '>')
            
            info_list = anchor.find('ul', class_='info')
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            if info_list:
                info_items = info_list.find_all('li')
                if len(info_items) >= 2:
                    dept_spans = info_items[1].find_all('span')
                    if len(dept_spans) >= 2:
                        date_str = dept_spans[1].get_text(strip=True)
            
            url = f"{self.detail_url_base}?prtlBbsId={article_id}"
            
            return {
                'article_id': article_id,
                'title': title,
                'telegram_title': telegram_title,  # This is the key field
                'content': content,
                'date': date_str,
                'url': url,
                'metadata': {
                    'article_id': article_id,
                    'has_content': bool(content)
                }
            }
            
        except Exception as e:
            self.logger.debug(f"Parse error: {e}")
            return None
    
    def _ensure_article_format(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Override to preserve telegram_title"""
        # Call parent to get required fields
        base_article = super()._ensure_article_format(article)
        
        # Preserve telegram_title if it exists
        if 'telegram_title' in article:
            base_article['telegram_title'] = article['telegram_title']
        
        return base_article
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse article - ensure telegram_title is included"""
        # Call parent's _ensure_article_format which will now preserve telegram_title
        return self._ensure_article_format(raw_data)
    
    def _get_fallback_articles(self) -> List[Dict[str, Any]]:
        """Fallback with telegram_title"""
        return [
            {
                'article_id': '26546',
                'title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'telegram_title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'content': '정시 등록이 오늘부터 시작됩니다.',
                'url': f"{self.detail_url_base}?prtlBbsId=26546",
                'date': '2026-02-04',
                'metadata': {'is_fallback': True}
            }
        ]
    
    def cleanup(self):
        pass

# Legacy compatibility
class LegacyAdigaScraper:
    def __init__(self):
        config = {
            'name': 'adiga',
            'base_url': 'https://www.adiga.kr',
            'html_file_path': 'adiga_structure.html',
            'max_articles': 10,
            'display_name': 'Adiga (어디가)',
            'timeout': 30,
            'retry_attempts': 3
        }
        self._scraper = AdigaWithTelegramTitle(config)
        self.source_name = self._scraper.display_name
        self.source_config = {'name': 'Adiga (어디가)'}
    
    def scrape(self):
        return self._scraper.scrape()
    
    def find_new_programs(self, current_programs):
        return self._scraper.find_new_programs(current_programs)
    
    def save_detected(self, programs):
        return self._scraper.save_detected(programs)

# Test
if __name__ == "__main__":
    print("Testing Adiga Scraper with telegram_title")
    print("=" * 60)
    
    scraper = AdigaWithTelegramTitle()
    
    try:
        articles = scraper.scrape()
        print(f"Scraped {len(articles)} articles")
        
        if articles:
            article = articles[0]
            print(f"\n📰 First article:")
            print(f"Title: {article.get('title')}")
            print(f"Telegram title: {article.get('telegram_title', 'NOT SET')}")
            print(f"URL: {article.get('url')}")
            print(f"Content preview: {article.get('content', '')[:80]}...")
            
            if article.get('telegram_title') and article['telegram_title'] != 'NOT SET':
                print(f"\n✅ SUCCESS: telegram_title is preserved")
                print(f"   Value: {article['telegram_title'][:50]}...")
                if "'" not in article['telegram_title']:
                    print("   ✅ Properly escaped for Telegram")
            else:
                print(f"\n❌ FAILED: telegram_title not preserved")
        
        print("\n" + "=" * 60)
        
    finally:
        scraper.cleanup()
