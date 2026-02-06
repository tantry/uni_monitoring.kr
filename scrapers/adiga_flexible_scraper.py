#!/usr/bin/env python3
"""
Flexible Adiga Scraper that adapts to different HTML structures
"""
import re
import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_scraper import BaseScraper
from scrapers.adiga_content_extractor import extract_content

class FlexibleAdigaScraper(BaseScraper):
    """Flexible scraper that adapts to Adiga's HTML structure"""
    
    def __init__(self, config: Dict[str, Any] = None):
        config = config or {
            'name': 'adiga',
            'base_url': 'https://adiga.kr',
            'html_file_path': 'adiga_structure.html',
            'max_articles': 20,  # Increased for more coverage
            'display_name': 'Adiga (어디가)',
            'timeout': 30,
            'retry_attempts': 3,
            'debug': True
        }
        
        super().__init__(config)
        
        self.html_file_path = config.get('html_file_path', 'adiga_structure.html')
        self.max_articles = config.get('max_articles', 20)
        self.display_name = config.get('display_name', 'Adiga (어디가)')
        self.debug_mode = config.get('debug', True)
        
        # URLs
        self.detail_url_base = "https://www.adiga.kr/uct/nmg/enw/newsDetail.do"
        
        # Session
        self._session = None
        
        # Parser strategies
        self.parser_strategies = [
            self._parse_tr_onclick,      # Strategy 1: tr with onclick
            self._parse_ajax_data,       # Strategy 2: AJAX data in scripts
            self._parse_article_links,   # Strategy 3: Direct article links
            self._parse_json_data,       # Strategy 4: JSON data
            self._parse_fallback         # Strategy 5: Fallback
        ]
        
        self.logger.info(f"Initialized Flexible {self.display_name} with {len(self.parser_strategies)} strategies")
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles using multiple parsing strategies"""
        self.logger.info("Fetching articles with flexible parsing")
        
        if not os.path.exists(self.html_file_path):
            self.logger.error(f"HTML file not found: {self.html_file_path}")
            return self._get_fallback_articles()
        
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            self.logger.info(f"Loaded HTML: {len(html_content)} chars")
            
            # Try each parsing strategy until one works
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
                self.logger.warning("No parsing strategy found articles, using fallback")
                return self._get_fallback_articles()
            
            # Enhance articles with content
            enhanced_articles = []
            for article in articles[:self.max_articles]:
                try:
                    enhanced = self._enhance_article_with_content(article)
                    enhanced_articles.append(enhanced)
                except Exception as e:
                    self.logger.error(f"Failed to enhance article: {e}")
                    enhanced_articles.append(article)  # Keep without enhancement
            
            self.logger.info(f"Successfully processed {len(enhanced_articles)} articles using '{strategy_used}'")
            return enhanced_articles
            
        except Exception as e:
            self.logger.error(f"Error in fetch_articles: {e}")
            return self._get_fallback_articles()
    
    def _parse_tr_onclick(self, html_content: str) -> List[Dict[str, Any]]:
        """Strategy 1: Parse tr elements with onclick"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Find all tr elements with onclick
        tr_elements = soup.find_all('tr', onclick=True)
        
        for tr in tr_elements:
            onclick = tr.get('onclick', '')
            
            # Look for goDetail function call
            match = re.search(r"goDetail\('(\d+)'\)", onclick)
            if match:
                article_id = match.group(1)
                
                # Extract title from td elements
                title_cell = tr.find('td', class_=re.compile(r'subject|title|tit', re.I))
                if not title_cell:
                    # Try any td with text
                    tds = tr.find_all('td')
                    for td in tds:
                        text = td.get_text(strip=True)
                        if text and len(text) > 10:  # Reasonable title length
                            title_cell = td
                            break
                
                title = title_cell.get_text(strip=True) if title_cell else f"Article {article_id}"
                
                # Extract date
                date_cell = tr.find('td', class_=re.compile(r'date|time|reg', re.I))
                date_str = date_cell.get_text(strip=True) if date_cell else datetime.now().strftime('%Y-%m-%d')
                
                articles.append({
                    'article_id': article_id,
                    'title': title,
                    'date': date_str,
                    'raw_element': 'tr_onclick'
                })
        
        return articles
    
    def _parse_ajax_data(self, html_content: str) -> List[Dict[str, Any]]:
        """Strategy 2: Parse AJAX data from scripts"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Look for scripts containing article data
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            script_content = script.string
            if not script_content:
                continue
            
            # Look for article data patterns
            # Pattern 1: goDetail calls
            goDetail_matches = re.findall(r"goDetail\('(\d+)'\)", script_content)
            for article_id in goDetail_matches:
                # Try to find associated title
                title_match = re.search(rf"['\"]{{0,1}}[^'\"]*{article_id}[^'\"]*['\"]{{0,1}}\s*:\s*['\"]([^'\"]+)['\"]", script_content)
                title = title_match.group(1) if title_match else f"Article {article_id}"
                
                articles.append({
                    'article_id': article_id,
                    'title': title,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'raw_element': 'ajax_script'
                })
            
            # Pattern 2: JSON-like data
            json_patterns = re.findall(r'\{\s*["\']id["\']\s*:\s*["\']?(\d+)["\']?\s*,\s*["\']title["\']\s*:\s*["\']([^"\']+)["\']', script_content)
            for article_id, title in json_patterns:
                articles.append({
                    'article_id': article_id,
                    'title': title,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'raw_element': 'json_pattern'
                })
        
        return articles[:self.max_articles]  # Limit results
    
    def _parse_article_links(self, html_content: str) -> List[Dict[str, Any]]:
        """Strategy 3: Parse article links"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Find all links that might point to articles
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Check if this looks like an article link
            if 'prtlBbsId=' in href and text and len(text) > 5:
                # Extract article ID from URL
                match = re.search(r'prtlBbsId=(\d+)', href)
                if match:
                    article_id = match.group(1)
                    
                    articles.append({
                        'article_id': article_id,
                        'title': text,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'raw_element': 'article_link',
                        'full_url': href if href.startswith('http') else f"https://www.adiga.kr{href}"
                    })
        
        return articles[:self.max_articles]
    
    def _parse_json_data(self, html_content: str) -> List[Dict[str, Any]]:
        """Strategy 4: Parse embedded JSON data"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Look for script tags with JSON
        script_tags = soup.find_all('script', type=re.compile(r'application/json|text/json', re.I))
        
        for script in script_tags:
            try:
                script_content = script.string
                if script_content:
                    # Try to parse as JSON
                    data = json.loads(script_content)
                    articles.extend(self._extract_from_json(data))
            except:
                continue
        
        # Also look for JavaScript variables
        all_scripts = soup.find_all('script')
        for script in all_scripts:
            script_content = script.string
            if not script_content:
                continue
            
            # Look for var articles = [...];
            var_patterns = [
                r'var\s+articles\s*=\s*(\[.*?\]);',
                r'const\s+articleList\s*=\s*(\[.*?\]);',
                r'let\s+data\s*=\s*(\[.*?\]);'
            ]
            
            for pattern in var_patterns:
                matches = re.search(pattern, script_content, re.DOTALL)
                if matches:
                    try:
                        json_str = matches.group(1)
                        data = json.loads(json_str)
                        articles.extend(self._extract_from_json(data))
                    except:
                        continue
        
        return articles[:self.max_articles]
    
    def _extract_from_json(self, data: Any) -> List[Dict[str, Any]]:
        """Extract articles from JSON data"""
        articles = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    article_id = item.get('id') or item.get('articleId') or item.get('bbsId')
                    title = item.get('title') or item.get('subject') or item.get('name')
                    
                    if article_id and title:
                        articles.append({
                            'article_id': str(article_id),
                            'title': str(title),
                            'date': item.get('date') or item.get('regDate') or datetime.now().strftime('%Y-%m-%d'),
                            'raw_element': 'json_data'
                        })
        
        return articles
    
    def _parse_fallback(self, html_content: str) -> List[Dict[str, Any]]:
        """Strategy 5: Fallback - look for any numeric IDs in the page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Extract all text and look for patterns
        all_text = soup.get_text()
        
        # Look for 5+ digit numbers (potential article IDs)
        id_matches = re.findall(r'\b(\d{5,})\b', all_text)
        
        # Also look for titles near these IDs
        lines = all_text.split('\n')
        
        for i, line in enumerate(lines):
            # Look for numeric IDs in line
            line_ids = re.findall(r'\b(\d{5,})\b', line)
            
            for article_id in line_ids:
                # Use the line as title, or combine with next line
                title = line.strip()
                if len(title) < 10 and i + 1 < len(lines):
                    title = f"{title} {lines[i + 1].strip()}"
                
                if len(title) > 5:  # Reasonable title
                    articles.append({
                        'article_id': article_id,
                        'title': title[:100],  # Limit title length
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'raw_element': 'fallback_text'
                    })
        
        return articles[:10]  # Limit fallback results
    
    def _enhance_article_with_content(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance article by fetching actual content"""
        article_id = article.get('article_id', '')
        
        # Build URL if not already provided
        url = article.get('full_url')
        if not url:
            url = f"{self.detail_url_base}?prtlBbsId={article_id}"
        
        # Fetch and extract content
        content_info = self._fetch_article_content(url, article_id)
        
        # Update article with content
        article.update({
            'url': url,
            'content_data': content_info,
            'enhanced_at': datetime.now().isoformat()
        })
        
        return article
    
    def _fetch_article_content(self, url: str, article_id: str) -> Dict[str, Any]:
        """Fetch content from article URL"""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            })
        
        try:
            response = self._session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Use content extractor
                extraction_result = extract_content(response.text, url)
                
                if self.debug_mode:
                    self.logger.info(
                        f"Content for {article_id}: "
                        f"method={extraction_result.get('extraction_method')}, "
                        f"length={extraction_result.get('content_length', 0)}"
                    )
                
                return extraction_result
            else:
                self.logger.warning(f"HTTP {response.status_code} for {url}")
                
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
        
        return {'has_content': False, 'clean_content': ''}
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse enhanced article data"""
        article_id = raw_data.get('article_id', '')
        title = raw_data.get('title', 'No Title')
        url = raw_data.get('url', '')
        content_data = raw_data.get('content_data', {})
        
        # Get content
        content = content_data.get('clean_content', '')
        has_actual_content = content_data.get('has_content', False)
        extraction_method = content_data.get('extraction_method', 'none')
        
        # Extract metadata
        university = self._extract_university(title)
        department = self._extract_department(title, content)
        
        # Generate ID
        article_hash = f"adiga_{article_id}"
        
        # Metadata
        metadata = {
            'source': self.display_name,
            'scraped_at': datetime.now().isoformat(),
            'article_id': article_id,
            'has_actual_content': has_actual_content,
            'content_length': len(content),
            'extraction_method': extraction_method,
            'university': university,
            'department': department,
            'raw_element_type': raw_data.get('raw_element', 'unknown'),
            'debug_info': content_data.get('debug', {})
        }
        
        return {
            'id': article_hash,
            'title': title,
            'content': content,
            'url': url,
            'published_date': raw_data.get('date'),
            'university': university,
            'department': department if department else {'name': 'general'},
            'metadata': metadata,
            'source': self.name
        }
    
    def _extract_university(self, title: str) -> Optional[str]:
        """Extract university name"""
        univ_patterns = [
            (r'서울대', '서울대학교'),
            (r'연세대', '연세대학교'),
            (r'고려대', '고려대학교'),
            (r'카이스트', '한국과학기술원'),
            (r'포스텍', '포항공과대학교'),
        ]
        
        for pattern, full_name in univ_patterns:
            if re.search(pattern, title):
                return full_name
        return None
    
    def _extract_department(self, title: str, content: str) -> Optional[str]:
        """Extract department"""
        text_to_check = f"{title} {content}".lower()
        
        dept_keywords = {
            'music': ['음악', '실용음악', '성악', '작곡'],
            'korean': ['한국어', '국어', '국어국문', '국문학'],
            'english': ['영어', '영어영문', '영문학'],
        }
        
        for dept, keywords in dept_keywords.items():
            for keyword in keywords:
                if keyword in text_to_check:
                    return dept
        return None
    
    def _get_fallback_articles(self) -> List[Dict[str, Any]]:
        """Fallback articles"""
        self.logger.warning("Using fallback articles")
        return [
            {
                'article_id': '26546',
                'title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'raw_element': 'fallback',
                'content_data': {
                    'clean_content': '정시 등록이 오늘부터 시작됩니다. 대학별 등록 마감일 확인.',
                    'has_content': True,
                    'extraction_method': 'fallback'
                }
            }
        ]
    
    def cleanup(self):
        """Cleanup"""
        if self._session:
            self._session.close()
            self._session = None

# Test
if __name__ == "__main__":
    print("Testing Flexible Adiga Scraper")
    print("=" * 60)
    
    scraper = FlexibleAdigaScraper()
    
    try:
        articles = scraper.scrape()
        print(f"Scraped {len(articles)} articles")
        
        if articles:
            for i, article in enumerate(articles[:3]):  # Show first 3
                print(f"\n--- Article {i+1} ---")
                print(f"Title: {article.get('title')}")
                
                metadata = article.get('metadata', {})
                print(f"ID: {metadata.get('article_id', 'N/A')}")
                print(f"Has content: {metadata.get('has_actual_content', False)}")
                print(f"Method: {metadata.get('extraction_method', 'unknown')}")
                print(f"Content length: {metadata.get('content_length', 0)} chars")
                
                if metadata.get('has_actual_content'):
                    content = article.get('content', '')
                    print(f"Content preview: {content[:100]}...")
                
                print(f"URL: {article.get('url')}")
                print(f"Raw type: {metadata.get('raw_element_type', 'unknown')}")
        
        print("\n" + "=" * 60)
        
    finally:
        scraper.cleanup()
