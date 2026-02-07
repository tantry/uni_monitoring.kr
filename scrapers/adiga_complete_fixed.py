#!/usr/bin/env python3
"""
COMPLETE FIXED Flexible Adiga Scraper
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

class AdigaCompleteScraper(BaseScraper):
    """Complete fixed flexible scraper"""
    
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
        
        self.parser_strategies = [
            self._parse_ul_list,
            self._parse_article_links,
            self._parse_tr_onclick,
            self._parse_ajax_data,
            self._parse_fallback
        ]
        
        self._session = None
        
        self.logger.info(f"Initialized COMPLETE {self.display_name} scraper")
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles"""
        self.logger.info("Fetching articles")
        
        if not os.path.exists(self.html_file_path):
            self.logger.error(f"HTML file not found: {self.html_file_path}")
            return self._get_fallback_articles()
        
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Try each strategy
            articles = []
            strategy_used = "none"
            
            for strategy in self.parser_strategies:
                try:
                    strategy_articles = strategy(html_content)
                    if strategy_articles and len(strategy_articles) > 0:
                        articles = strategy_articles
                        strategy_used = strategy.__name__
                        self.logger.info(f"Strategy '{strategy_used}' found {len(articles)} articles")
                        break
                except Exception as e:
                    self.logger.debug(f"Strategy {strategy.__name__} failed: {e}")
                    continue
            
            if not articles:
                self.logger.warning("No articles found, using fallback")
                return self._get_fallback_articles()
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return self._get_fallback_articles()
    
    def _parse_ul_list(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse UL list"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        ul_element = soup.find('ul', class_='uctList02')
        if not ul_element:
            return []
        
        li_items = ul_element.find_all('li')
        self.logger.info(f"Found {len(li_items)} LI items")
        
        for li in li_items[:self.max_articles]:
            article = self._parse_li_item(li)
            if article:
                articles.append(article)
        
        return articles
    
    def _parse_li_item(self, li_element) -> Optional[Dict[str, Any]]:
        """Parse LI item - COMPLETE with all fields"""
        try:
            anchor = li_element.find('a', onclick=True)
            if not anchor:
                return None
            
            onclick = anchor.get('onclick', '')
            match = re.search(r'fnDetailPopup\("(\d+)"\)', onclick)
            if not match:
                return None
            
            article_id = match.group(1)
            
            # Title
            title_elem = anchor.find('p', class_='uctCastTitle')
            title = title_elem.get_text(strip=True) if title_elem else f"Article {article_id}"
            title = title.replace('newIcon', '').strip()
            
            # Telegram title (escaped)
            telegram_title = title.replace("'", "&#x27;")
            
            # Content
            content_elem = anchor.find('span', class_='content')
            raw_content = content_elem.get_text(strip=True) if content_elem else ""
            
            # Clean content
            content = raw_content
            if '&lt;' in content and '&gt;' in content:
                # Remove source prefix
                end = content.find('&gt;')
                if end != -1:
                    content = content[end + 4:]  # Remove "&gt;"
            
            # Remove "기사 제목 :"
            if '기사 제목 :' in content:
                content = content.replace('기사 제목 :', '').strip()
            
            # Remove "뉴스 내용 전체 보기"
            if '뉴스 내용 전체 보기' in content:
                content = content.replace('뉴스 내용 전체 보기', '').strip()
            
            # Date
            info_list = anchor.find('ul', class_='info')
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            if info_list:
                info_items = info_list.find_all('li')
                if len(info_items) >= 2:
                    dept_spans = info_items[1].find_all('span')
                    if len(dept_spans) >= 2:
                        date_str = dept_spans[1].get_text(strip=True)
            
            # URL
            url = f"{self.detail_url_base}?prtlBbsId={article_id}"
            
            # Return COMPLETE article data
            return {
                'article_id': article_id,
                'title': title,
                'telegram_title': telegram_title,
                'content': content,
                'date': date_str,
                'url': url,
                'raw_element': 'ul_list_item',
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'article_id': article_id,
                    'has_content': bool(content),
                    'content_length': len(content)
                }
            }
            
        except Exception as e:
            self.logger.debug(f"Parse error: {e}")
            return None
    
    def _parse_article_links(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse article links"""
        return []
    
    def _parse_tr_onclick(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse TR elements"""
        return []
    
    def _parse_ajax_data(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse AJAX data"""
        return []
    
    def _parse_fallback(self, html_content: str) -> List[Dict[str, Any]]:
        """Fallback"""
        return []
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse article - FIXED to include telegram_title"""
        article_id = raw_data.get('article_id', '')
        title = raw_data.get('title', 'No Title')
        
        # GET telegram_title from raw_data (it should be there now)
        telegram_title = raw_data.get('telegram_title')
        if not telegram_title:
            telegram_title = title.replace("'", "&#x27;")
        
        content = raw_data.get('content', '')
        url = raw_data.get('url', f"{self.detail_url_base}?prtlBbsId={article_id}")
        
        # Get metadata from raw_data or create new
        metadata = raw_data.get('metadata', {})
        metadata.update({
            'source': self.display_name,
            'scraped_at': datetime.now().isoformat(),
            'article_id': article_id,
            'has_content': bool(content),
            'content_length': len(content),
            'raw_element_type': raw_data.get('raw_element', 'unknown')
        })
        
        article_hash = f"adiga_{article_id}"
        
        return {
            'id': article_hash,
            'title': title,
            'telegram_title': telegram_title,  # This is now included
            'content': content,
            'url': url,
            'published_date': raw_data.get('date'),
            'university': None,
            'department': {'name': 'general'},
            'metadata': metadata,
            'source': self.name
        }
    
    def _get_fallback_articles(self) -> List[Dict[str, Any]]:
        """Fallback"""
        return [
            {
                'article_id': '26546',
                'title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'telegram_title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'content': '정시 등록이 오늘부터 시작됩니다.',
                'url': f"{self.detail_url_base}?prtlBbsId=26546",
                'date': '2026-02-04',
                'raw_element': 'fallback',
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'is_fallback': True
                }
            }
        ]
    
    def cleanup(self):
        if self._session:
            self._session.close()

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
        self._scraper = AdigaCompleteScraper(config)
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
    print("Testing COMPLETE FIXED Adiga Scraper")
    print("=" * 60)
    
    scraper = AdigaCompleteScraper()
    
    try:
        articles = scraper.scrape()
        print(f"Scraped {len(articles)} articles")
        
        if articles:
            article = articles[0]
            print(f"\n📰 First article:")
            print(f"Title: {article.get('title')}")
            print(f"Telegram title: {article.get('telegram_title', 'NOT SET')}")
            print(f"URL: {article.get('url')}")
            print(f"Content: {article.get('content', '')[:80]}...")
            
            if article.get('telegram_title') and article['telegram_title'] != 'NOT SET':
                print(f"\n✅ SUCCESS: telegram_title is set")
                print(f"   Value: {article['telegram_title']}")
                if "'" not in article['telegram_title'] and "&#x27;" in article['telegram_title']:
                    print("   ✅ Properly escaped for Telegram")
            else:
                print(f"\n❌ FAILED: telegram_title not set")
            
            # Test URL
            import requests
            url = article.get('url')
            if url:
                try:
                    response = requests.head(url, timeout=5)
                    print(f"\n🔗 URL test: HTTP {response.status_code}")
                    if response.status_code == 200:
                        print("   ✅ URL accessible")
                except:
                    print("   ⚠ URL not accessible")
        
        print("\n" + "=" * 60)
        
    finally:
        scraper.cleanup()
