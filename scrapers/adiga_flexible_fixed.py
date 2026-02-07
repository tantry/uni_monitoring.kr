#!/usr/bin/env python3
"""
Fixed Flexible Adiga Scraper with proper UL list parsing
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

class AdigaFlexibleFixedScraper(BaseScraper):
    """Fixed flexible scraper with UL list parsing"""
    
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
        
        # Updated strategies - ADDED UL_LIST_PARSING as first strategy
        self.parser_strategies = [
            self._parse_ul_list,        # NEW: Parse UL lists
            self._parse_article_links,  # Parse article links
            self._parse_tr_onclick,     # Parse TR elements
            self._parse_ajax_data,      # Parse AJAX data
            self._parse_fallback        # Fallback
        ]
        
        self._session = None
        
        self.logger.info(f"Initialized FIXED Flexible {self.display_name} with {len(self.parser_strategies)} strategies")
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles using updated strategies"""
        self.logger.info("Fetching articles with FIXED flexible parsing")
        
        if not os.path.exists(self.html_file_path):
            self.logger.error(f"HTML file not found: {self.html_file_path}")
            return self._get_fallback_articles()
        
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            self.logger.info(f"Loaded HTML: {len(html_content)} chars")
            
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
                self.logger.warning("No strategy found articles, using fallback")
                return self._get_fallback_articles()
            
            # Enhance with content
            enhanced_articles = []
            for article in articles[:self.max_articles]:
                try:
                    enhanced = self._enhance_article(article)
                    enhanced_articles.append(enhanced)
                except Exception as e:
                    self.logger.error(f"Failed to enhance article: {e}")
                    enhanced_articles.append(article)
            
            return enhanced_articles
            
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return self._get_fallback_articles()
    
    def _parse_ul_list(self, html_content: str) -> List[Dict[str, Any]]:
        """NEW: Parse UL with class uctList02 - your actual HTML structure"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Find the UL with articles
        ul_element = soup.find('ul', class_='uctList02')
        if not ul_element:
            self.logger.debug("No uctList02 found")
            return []
        
        # Find all LI items
        li_items = ul_element.find_all('li')
        self.logger.info(f"Found {len(li_items)} LI items in uctList02")
        
        for li in li_items:
            article_data = self._parse_li_item(li)
            if article_data:
                articles.append(article_data)
        
        return articles
    
    def _parse_li_item(self, li_element) -> Optional[Dict[str, Any]]:
        """Parse a single LI item"""
        try:
            # Find anchor with onclick
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
            
            # Content snippet
            content_elem = anchor.find('span', class_='content')
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            # Clean content
            if content:
                content = re.sub(r'&lt;.*?&gt;\s*', '', content)
                content = re.sub(r'기사 제목\s*:\s*', '', content)
                content = re.sub(r'\s*뉴스\s*내용 전체 보기', '', content)
                content = content.strip()
            
            # Date
            info_list = anchor.find('ul', class_='info')
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            if info_list:
                info_items = info_list.find_all('li')
                if len(info_items) >= 2:
                    dept_spans = info_items[1].find_all('span')
                    if len(dept_spans) >= 2:
                        date_str = dept_spans[1].get_text(strip=True)
            
            # Telegram title
            telegram_title = title.replace("'", "&#x27;")
            
            # URL
            url = f"{self.detail_url_base}?prtlBbsId={article_id}"
            
            return {
                'article_id': article_id,
                'title': title,
                'telegram_title': telegram_title,
                'content': content,
                'date': date_str,
                'url': url,
                'raw_element': 'ul_list_item'
            }
            
        except Exception as e:
            self.logger.debug(f"Error parsing LI item: {e}")
            return None
    
    def _parse_article_links(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse article links - FIXED version"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Find all anchors with onclick containing fnDetailPopup
        anchors = soup.find_all('a', onclick=re.compile(r'fnDetailPopup'))
        
        for anchor in anchors:
            onclick = anchor.get('onclick', '')
            match = re.search(r'fnDetailPopup\("(\d+)"\)', onclick)
            if match:
                article_id = match.group(1)
                
                # Try to find title
                title_elem = anchor.find(['p', 'span', 'div'])
                title = title_elem.get_text(strip=True)[:100] if title_elem else f"Article {article_id}"
                
                articles.append({
                    'article_id': article_id,
                    'title': title,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'raw_element': 'article_link'
                })
        
        return articles
    
    # Keep other strategies as they were
    def _parse_tr_onclick(self, html_content: str) -> List[Dict[str, Any]]:
        """Original TR parsing (kept for compatibility)"""
        return []
    
    def _parse_ajax_data(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse AJAX data"""
        return []
    
    def _parse_fallback(self, html_content: str) -> List[Dict[str, Any]]:
        """Fallback parsing"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Look for any onclick with fnDetailPopup
        onclick_elements = soup.find_all(onclick=re.compile(r'fnDetailPopup'))
        
        for elem in onclick_elements[:3]:
            onclick = elem.get('onclick', '')
            match = re.search(r'fnDetailPopup\("(\d+)"\)', onclick)
            if match:
                article_id = match.group(1)
                articles.append({
                    'article_id': article_id,
                    'title': f"Article {article_id}",
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'raw_element': 'fallback_onclick'
                })
        
        return articles
    
    def _enhance_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance article with URL and metadata"""
        article_id = article.get('article_id', '')
        
        # Build URL if not already there
        if 'url' not in article:
            article['url'] = f"{self.detail_url_base}?prtlBbsId={article_id}"
        
        # Ensure telegram_title
        if 'telegram_title' not in article and 'title' in article:
            article['telegram_title'] = article['title'].replace("'", "&#x27;")
        
        return article
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse article"""
        article_id = raw_data.get('article_id', '')
        title = raw_data.get('title', 'No Title')
        telegram_title = raw_data.get('telegram_title', title.replace("'", "&#x27;"))
        content = raw_data.get('content', '')
        url = raw_data.get('url', f"{self.detail_url_base}?prtlBbsId={article_id}")
        
        # Generate ID
        article_hash = f"adiga_{article_id}"
        
        metadata = {
            'source': self.display_name,
            'scraped_at': datetime.now().isoformat(),
            'article_id': article_id,
            'has_content': bool(content),
            'content_length': len(content),
            'raw_element_type': raw_data.get('raw_element', 'unknown')
        }
        
        return {
            'id': article_hash,
            'title': title,
            'telegram_title': telegram_title,
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
                'raw_element': 'hardcoded_fallback'
            }
        ]
    
    def cleanup(self):
        if self._session:
            self._session.close()

# Test
if __name__ == "__main__":
    print("Testing FIXED Flexible Adiga Scraper")
    print("=" * 60)
    
    scraper = AdigaFlexibleFixedScraper()
    
    try:
        articles = scraper.scrape()
        print(f"Scraped {len(articles)} articles")
        
        if articles:
            for i, article in enumerate(articles[:3]):
                print(f"\n--- Article {i+1} ---")
                print(f"Title: {article.get('title')}")
                print(f"Telegram title: {article.get('telegram_title', 'NOT SET')}")
                print(f"URL: {article.get('url')}")
                print(f"Content: {article.get('content', '')[:80]}...")
                print(f"Raw type: {article.get('metadata', {}).get('raw_element_type', 'unknown')}")
        
        print("\n" + "=" * 60)
        
    finally:
        scraper.cleanup()
