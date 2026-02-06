#!/usr/bin/env python3
"""
Modern Adiga Scraper for the current HTML structure
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
from scrapers.adiga_content_extractor import extract_content

class ModernAdigaScraper(BaseScraper):
    """Modern Adiga scraper for current list-based HTML structure"""
    
    def __init__(self, config: Dict[str, Any] = None):
        config = config or {
            'name': 'adiga',
            'base_url': 'https://adiga.kr',
            'html_file_path': 'adiga_structure.html',
            'max_articles': 20,
            'display_name': 'Adiga (어디가)',
            'timeout': 30,
            'retry_attempts': 3,
            'detail_url_pattern': 'https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBbsId={article_id}'
        }
        
        super().__init__(config)
        
        self.html_file_path = config.get('html_file_path', 'adiga_structure.html')
        self.max_articles = config.get('max_articles', 20)
        self.display_name = config.get('display_name', 'Adiga (어디가)')
        self.detail_url_pattern = config.get('detail_url_pattern')
        
        # Session for fetching article content
        self._session = None
        
        self.logger.info(f"Initialized Modern {self.display_name} scraper")
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles from the modern list structure"""
        self.logger.info("Fetching articles from modern list structure")
        
        if not os.path.exists(self.html_file_path):
            self.logger.error(f"HTML file not found: {self.html_file_path}")
            return self._get_fallback_articles()
        
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            articles = []
            
            # Find all list items in the article list
            article_list = soup.find('ul', class_='uctList02')
            if not article_list:
                self.logger.error("Could not find uctList02 ul element")
                return self._get_fallback_articles()
            
            # Find all list items
            list_items = article_list.find_all('li')
            self.logger.info(f"Found {len(list_items)} list items")
            
            for li in list_items[:self.max_articles]:
                article_data = self._extract_from_list_item(li)
                if article_data:
                    articles.append(article_data)
            
            self.logger.info(f"Extracted {len(articles)} articles from list structure")
            
            if not articles:
                self.logger.warning("No articles extracted, using fallback")
                return self._get_fallback_articles()
            
            # Enhance articles with content
            enhanced_articles = []
            for article in articles:
                try:
                    enhanced = self._enhance_article_with_content(article)
                    enhanced_articles.append(enhanced)
                except Exception as e:
                    self.logger.error(f"Failed to enhance article: {e}")
                    enhanced_articles.append(article)
            
            return enhanced_articles
            
        except Exception as e:
            self.logger.error(f"Error fetching articles: {e}")
            return self._get_fallback_articles()
    
    def _extract_from_list_item(self, li_element) -> Optional[Dict[str, Any]]:
        """Extract article data from a list item"""
        try:
            # Find the anchor tag with onclick
            anchor = li_element.find('a', onclick=True)
            if not anchor:
                return None
            
            onclick = anchor.get('onclick', '')
            
            # Extract article ID from fnDetailPopup
            match = re.search(r'fnDetailPopup\("(\d+)"\)', onclick)
            if not match:
                return None
            
            article_id = match.group(1)
            
            # Extract title
            title_elem = anchor.find('p', class_='uctCastTitle')
            title = title_elem.get_text(strip=True) if title_elem else "No Title"
            
            # Remove "newIcon" class from title if present
            title = title.replace('newIcon', '').strip()
            
            # Extract content snippet
            content_elem = anchor.find('span', class_='content')
            content_snippet = content_elem.get_text(strip=True) if content_elem else ""
            
            # Clean content snippet
            if content_snippet:
                # Remove the boilerplate text
                content_snippet = re.sub(r'&lt;.*?&gt;', '', content_snippet)
                content_snippet = re.sub(r'기사 제목\s*:\s*', '', content_snippet)
                content_snippet = re.sub(r'뉴스\s*내용 전체 보기', '', content_snippet)
                content_snippet = content_snippet.strip()
            
            # Extract metadata from info list
            info_list = anchor.find('ul', class_='info')
            year = "2026"  # Default
            category = "공통"
            department = "대입상담센터"
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            if info_list:
                info_items = info_list.find_all('li')
                if len(info_items) >= 1:
                    # First li: year and category
                    year_spans = info_items[0].find_all('span')
                    if len(year_spans) >= 2:
                        year = year_spans[0].get_text(strip=True)
                        category = year_spans[1].get_text(strip=True)
                
                if len(info_items) >= 2:
                    # Second li: department and date
                    dept_spans = info_items[1].find_all('span')
                    if len(dept_spans) >= 2:
                        department = dept_spans[0].get_text(strip=True)
                        date_str = dept_spans[1].get_text(strip=True)
            
            return {
                'article_id': article_id,
                'title': title,
                'content_snippet': content_snippet,
                'year': year,
                'category': category,
                'department': department,
                'date': date_str,
                'raw_element': 'list_item'
            }
            
        except Exception as e:
            self.logger.debug(f"Error extracting from list item: {e}")
            return None
    
    def _enhance_article_with_content(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance article by fetching full content"""
        article_id = article.get('article_id', '')
        
        # Build URL using the pattern
        url = self.detail_url_pattern.format(article_id=article_id)
        
        # Fetch and extract content
        content_info = self._fetch_article_content(url, article_id)
        
        # Update article with content and URL
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
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.adiga.kr/',
            })
        
        try:
            response = self._session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Use content extractor
                extraction_result = extract_content(response.text, url)
                
                self.logger.info(
                    f"Content extraction for {article_id}: "
                    f"method={extraction_result.get('extraction_method')}, "
                    f"success={extraction_result.get('has_content')}, "
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
        content_snippet = raw_data.get('content_snippet', '')
        
        # Get content - prefer extracted content, fallback to snippet
        extracted_content = content_data.get('clean_content', '')
        if extracted_content:
            content = extracted_content
        else:
            content = content_snippet
        
        has_actual_content = content_data.get('has_content', False) or bool(content_snippet)
        extraction_method = content_data.get('extraction_method', 'snippet')
        
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
            'year': raw_data.get('year'),
            'category': raw_data.get('category'),
            'original_department': raw_data.get('department'),
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
        """Extract university name from title"""
        univ_patterns = [
            (r'서울대', '서울대학교'),
            (r'연세대', '연세대학교'),
            (r'고려대', '고려대학교'),
            (r'카이스트', '한국과학기술원'),
            (r'포스텍', '포항공과대학교'),
            (r'성균관대', '성균관대학교'),
            (r'한양대', '한양대학교'),
            (r'서강대', '서강대학교'),
            (r'이화여대', '이화여자대학교'),
            (r'숙명여대', '숙명여자대학교'),
            (r'경희대', '경희대학교'),
            (r'한국외대', '한국외국어대학교')
        ]
        
        for pattern, full_name in univ_patterns:
            if re.search(pattern, title):
                return full_name
        
        # Also check for "의대" which might indicate medical school announcements
        if '의대' in title or '의과대학' in title:
            return '의과대학'
        
        return None
    
    def _extract_department(self, title: str, content: str) -> Optional[str]:
        """Extract department from title and content"""
        text_to_check = f"{title} {content}".lower()
        
        department_keywords = {
            'music': ['음악', '실용음악', '성악', '작곡', '관현악'],
            'korean': ['한국어', '국어', '국어국문', '국문학', '한문'],
            'english': ['영어', '영어영문', '영문학', '영미'],
            'liberal': ['인문', '인문학', '교양', '교양교육', '철학', '역사'],
            'science': ['과학', '물리', '화학', '생물', '지구과학'],
            'engineering': ['공학', '기계', '전기', '전자', '컴퓨터', '소프트웨어'],
            'medical': ['의학', '의대', '간호', '약학', '치의학'],
            'education': ['교육', '교원', '교육학', '특수교육']
        }
        
        for dept, keywords in department_keywords.items():
            for keyword in keywords:
                if keyword in text_to_check:
                    return dept
        
        return None
    
    def _get_fallback_articles(self) -> List[Dict[str, Any]]:
        """Get fallback articles"""
        self.logger.warning("Using fallback articles")
        
        # Try to extract at least something from the HTML
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for any onclick with fnDetailPopup
            onclick_elements = soup.find_all(onclick=re.compile(r'fnDetailPopup'))
            
            articles = []
            for elem in onclick_elements[:3]:  # Get up to 3
                onclick = elem.get('onclick', '')
                match = re.search(r'fnDetailPopup\("(\d+)"\)', onclick)
                if match:
                    article_id = match.group(1)
                    
                    # Try to find title near the element
                    title_elem = elem.find(['p', 'span', 'div'])
                    title = title_elem.get_text(strip=True)[:100] if title_elem else f"Article {article_id}"
                    
                    articles.append({
                        'article_id': article_id,
                        'title': title,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'raw_element': 'fallback_onclick'
                    })
            
            if articles:
                return articles
                
        except Exception as e:
            self.logger.debug(f"Fallback extraction failed: {e}")
        
        # Ultimate fallback
        return [
            {
                'article_id': '26546',
                'title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'date': '2026-02-04',
                'content_snippet': '정시 등록이 오늘부터 시작됩니다.',
                'raw_element': 'hardcoded_fallback'
            }
        ]
    
    def cleanup(self):
        """Cleanup resources"""
        if self._session:
            self._session.close()
            self._session = None
    
    def find_new_programs(self, current_programs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find new programs (override if needed)"""
        return super().find_new_programs(current_programs)
    
    def save_detected(self, articles: List[Dict[str, Any]]) -> bool:
        """Save detected articles"""
        return super().save_detected(articles)

# Legacy compatibility wrapper
class LegacyAdigaScraper:
    def __init__(self):
        config = {
            'name': 'adiga',
            'base_url': 'https://adiga.kr',
            'html_file_path': 'adiga_structure.html',
            'max_articles': 20,
            'display_name': 'Adiga (어디가)',
            'timeout': 30,
            'retry_attempts': 3
        }
        self._scraper = ModernAdigaScraper(config)
        self.source_name = self._scraper.display_name
        self.source_config = self._scraper.source_config
    
    def scrape(self):
        return self._scraper.scrape()
    
    def find_new_programs(self, current_programs):
        return self._scraper.find_new_programs(current_programs)
    
    def save_detected(self, programs):
        return self._scraper.save_detected(programs)

# Test
if __name__ == "__main__":
    print("Testing Modern Adiga Scraper")
    print("=" * 60)
    
    scraper = ModernAdigaScraper()
    
    try:
        articles = scraper.scrape()
        print(f"Scraped {len(articles)} articles")
        
        if articles:
            for i, article in enumerate(articles[:3]):  # Show first 3
                print(f"\n--- Article {i+1} ---")
                print(f"Title: {article.get('title')}")
                
                metadata = article.get('metadata', {})
                print(f"ID: {metadata.get('article_id', 'N/A')}")
                print(f"Has actual content: {metadata.get('has_actual_content', False)}")
                print(f"Extraction method: {metadata.get('extraction_method', 'unknown')}")
                print(f"Content length: {metadata.get('content_length', 0)} chars")
                
                if metadata.get('has_actual_content'):
                    content = article.get('content', '')
                    if content:
                        print(f"Content preview: {content[:150]}...")
                
                print(f"URL: {article.get('url')}")
                print(f"Published: {article.get('published_date')}")
                print(f"University: {metadata.get('university', 'N/A')}")
                print(f"Department: {article.get('department', 'N/A')}")
        
        print("\n" + "=" * 60)
        
    finally:
        scraper.cleanup()
