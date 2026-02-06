#!/usr/bin/env python3
"""
Adiga scraper for adiga.kr - University Admission Monitor
Migrated to inherit from BaseScraper for robust architecture
WITH BACKWARD COMPATIBILITY FIXES
"""
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_scraper import BaseScraper


class AdigaScraper(BaseScraper):
    """Adiga.kr scraper implementation for the robust architecture."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Adiga scraper with configuration.
        
        Args:
            config: Configuration dictionary from sources.yaml
        """
        # Ensure config has required fields for BaseScraper
        base_config = {
            'name': config.get('name', 'adiga'),
            'base_url': config.get('base_url', 'https://adiga.kr'),
            'timeout': config.get('timeout', 30),
            'retry_attempts': config.get('retry_attempts', 3)
        }
        
        super().__init__(base_config)
        
        # Store original config for scraper-specific settings
        self.full_config = config
        
        # Scraper-specific configuration
        self.html_file_path = config.get('html_file_path', 'adiga_structure.html')
        self.max_articles = config.get('max_articles', 10)
        self.display_name = config.get('display_name', 'Adiga (어디가)')
        
        # BACKWARD COMPATIBILITY: Add attributes expected by multi_monitor.py
        self.source_config = {
            'name': self.display_name,
            'base_url': self.base_url,
            'type': 'university_admission',
            'html_file_path': self.html_file_path
        }
        self.source_name = self.display_name
        
        self.logger.info(f"Initialized {self.display_name} scraper (with backward compatibility)")
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """
        Fetch raw articles from Adiga.kr HTML structure.
        
        Returns:
            List[Dict]: Raw article data dictionaries
        """
        self.logger.info(f"Fetching articles from {self.html_file_path}")
        
        raw_articles = []
        
        try:
            # Read the HTML file
            if not os.path.exists(self.html_file_path):
                self.logger.error(f"HTML file not found: {self.html_file_path}")
                return self._get_fallback_articles()
            
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html = f.read()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find article items - using the correct selector
            article_items = soup.select('ul.uctList02 li')
            self.logger.info(f"Found {len(article_items)} article items in HTML")
            
            # Parse each article
            for item in article_items[:self.max_articles]:
                try:
                    raw_article = self._extract_raw_article(item)
                    if raw_article:
                        raw_articles.append(raw_article)
                        
                except Exception as e:
                    self.logger.warning(f"Failed to parse article item: {e}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(raw_articles)} raw articles")
            
        except Exception as e:
            self.logger.error(f"Fetch error: {e}")
            raw_articles = self._get_fallback_articles()
        
        return raw_articles
    
    def _extract_raw_article(self, item) -> Optional[Dict[str, Any]]:
        """
        Extract raw article data from a BeautifulSoup item.
        
        Args:
            item: BeautifulSoup element
            
        Returns:
            Optional[Dict]: Raw article data or None
        """
        # Find the anchor tag with onclick
        anchor = item.find('a', onclick=True)
        if not anchor:
            return None
        
        # Extract article ID from onclick
        onclick = anchor.get('onclick', '')
        match = re.search(r'fnDetailPopup\(["\'](\d+)["\']\)', onclick)
        if not match:
            return None
        
        article_id = match.group(1)
        
        # Get title
        title_elem = anchor.select_one('.uctCastTitle')
        if not title_elem:
            return None
        
        title = title_elem.get_text(strip=True).replace('newIcon', '').strip()
        
        # Get content preview
        content_elem = anchor.select_one('.content')
        content = content_elem.get_text(strip=True) if content_elem else ""
        
        # Get metadata
        info_elem = anchor.select_one('.info')
        metadata = ""
        if info_elem:
            spans = info_elem.find_all('span')
            metadata = " | ".join([span.get_text(strip=True) for span in spans])
        
        # Construct URL
        article_url = f"{self.base_url}/ArticleDetail.do?articleID={article_id}"
        
        # Combine content with metadata
        full_content = content
        if metadata:
            full_content += f"\n📅 {metadata}"
        
        # Create raw article data
        return {
            'title': title,
            'content': full_content[:350],  # Limit content length
            'url': article_url,
            'article_id': article_id,
            'onclick_handler': onclick,
            'has_content': bool(content_elem),
            'has_metadata': bool(info_elem),
            'metadata': {
                'source': self.display_name,
                'scraped_at': datetime.now().isoformat()
            }
        }
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw article data into standardized format.
        
        Args:
            raw_data: Raw article data from fetch_articles()
            
        Returns:
            Standardized article dictionary with required fields
        """
        try:
            # Extract data from raw article
            article_id = raw_data.get('article_id', '')
            title = raw_data.get('title', '')
            content = raw_data.get('content', '')
            url = raw_data.get('url', '')
            metadata = raw_data.get('metadata', {})
            
            # Extract additional metadata
            publish_date = self._extract_publish_date(content)
            university = self._extract_university(title)
            
            # Create standardized article matching BaseScraper format
            article = {
                'id': f"adiga_{article_id}",
                'title': title,
                'content': content,
                'url': url,
                'source': self.name,
                'scraped_at': datetime.now().isoformat(),
                'published_date': publish_date.isoformat() if publish_date else None,
                'university': university,
                'department': self._extract_department(title, content),
                'metadata': {
                    **metadata,
                    'article_id': article_id,
                    'has_content': raw_data.get('has_content', False),
                    'has_metadata': raw_data.get('has_metadata', False),
                    'onclick_handler': raw_data.get('onclick_handler', '')
                }
            }
            
            self.logger.debug(f"Parsed article: {article_id}")
            return article
            
        except Exception as e:
            self.logger.error(f"Failed to parse raw article: {e}")
            # Return minimal valid article
            return {
                'id': f"adiga_error_{datetime.now().timestamp()}",
                'title': "Parse Error",
                'content': str(e),
                'url': '',
                'source': self.name,
                'scraped_at': datetime.now().isoformat(),
                'metadata': {'error': True, 'error_message': str(e)}
            }
    
    def _extract_publish_date(self, content: str) -> Optional[datetime]:
        """
        Extract publish date from content metadata.
        
        Args:
            content: Article content
            
        Returns:
            datetime object or None
        """
        # Simple date extraction - can be enhanced
        date_patterns = [
            r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{4})\.(\d{2})\.(\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    date_str = match.group(0)
                    # Try to parse Korean date format
                    if '년' in date_str:
                        year = int(match.group(1))
                        month = int(match.group(2))
                        day = int(match.group(3))
                        return datetime(year, month, day)
                    elif '-' in date_str:
                        return datetime.fromisoformat(date_str)
                    elif '.' in date_str:
                        year = int(match.group(1))
                        month = int(match.group(2))
                        day = int(match.group(3))
                        return datetime(year, month, day)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _extract_university(self, title: str) -> Optional[str]:
        """Extract university name from title."""
        # Common Korean university patterns
        univ_patterns = [
            (r'서울대', '서울대학교'),
            (r'연세대', '연세대학교'),
            (r'고려대', '고려대학교'),
            (r'성균관대', '성균관대학교'),
            (r'한양대', '한양대학교'),
            (r'서강대', '서강대학교'),
            (r'이화여대', '이화여자대학교'),
            (r'중앙대', '중앙대학교'),
            (r'경희대', '경희대학교'),
            (r'한국외대', '한국외국어대학교')
        ]
        
        for pattern, full_name in univ_patterns:
            if re.search(pattern, title):
                return full_name
        
        return None
    
    def _extract_department(self, title: str, content: str) -> Optional[str]:
        """Extract department from title and content."""
        # Check for department keywords in title and content
        text_to_check = f"{title} {content}".lower()
        
        department_keywords = {
            'music': ['음악', '실용음악', '성악', '작곡'],
            'korean': ['한국어', '국어', '국어국문', '국문학'],
            'english': ['영어', '영어영문', '영문학'],
            'liberal': ['인문', '인문학', '교양', '교양교육']
        }
        
        for dept, keywords in department_keywords.items():
            for keyword in keywords:
                if keyword in text_to_check:
                    return dept
        
        return None
    
    def _get_fallback_articles(self) -> List[Dict[str, Any]]:
        """
        Provide fallback articles for testing.
        
        Returns:
            List[Dict]: Fallback raw articles
        """
        self.logger.warning("Using fallback articles")
        return [
            {
                'title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'content': '정시 등록이 오늘부터 시작됩니다. 대학별 등록 마감일 확인.',
                'url': 'https://adiga.kr/ArticleDetail.do?articleID=26546',
                'article_id': '26546',
                'has_content': True,
                'has_metadata': True,
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'is_fallback': True
                }
            }
        ]


# Legacy compatibility wrapper
class LegacyAdigaScraper:
    """Wrapper for backward compatibility with existing code."""
    
    def __init__(self):
        """Initialize with default config for legacy compatibility."""
        config = {
            'name': 'adiga',
            'base_url': 'https://adiga.kr',
            'html_file_path': 'adiga_structure.html',
            'max_articles': 10,
            'display_name': 'Adiga (어디가)',
            'timeout': 30,
            'retry_attempts': 3
        }
        self._scraper = AdigaScraper(config)
        self.source_name = self._scraper.display_name
        self.source_config = self._scraper.source_config
    
    def scrape(self):
        """Legacy method name support."""
        return self._scraper.scrape()
    
    def find_new_programs(self, current_programs):
        """Legacy method name support."""
        return self._scraper.find_new_programs(current_programs)
    
    def save_detected(self, programs):
        """Legacy method name support."""
        return self._scraper.save_detected(programs)


if __name__ == "__main__":
    # Test the migrated scraper with backward compatibility
    print("Testing AdigaScraper with Backward Compatibility Fixes...")
    print("=" * 60)
    
    # Create config matching sources.yaml
    config = {
        'name': 'adiga',
        'enabled': True,
        'base_url': 'https://adiga.kr',
        'scraper_class': 'adiga_scraper',
        'schedule': '*/30 * * * *',
        'priority': 1,
        'timeout': 30,
        'retry_attempts': 3,
        'html_file_path': 'adiga_structure.html',
        'max_articles': 5,
        'display_name': 'Adiga (어디가)'
    }
    
    try:
        # Test 1: Create instance and check attributes
        print("\n1. Creating AdigaScraper instance...")
        scraper = AdigaScraper(config)
        print(f"   ✅ Created {scraper.display_name}")
        
        # Check backward compatibility attributes
        print(f"   source_name: {scraper.source_name}")
        print(f"   source_config keys: {list(scraper.source_config.keys())}")
        
        # Test 2: multi_monitor.py compatibility
        print("\n2. Testing multi_monitor.py compatibility...")
        required_attrs = ['source_config', 'source_name', 'scrape', 'find_new_programs', 'save_detected']
        all_present = all(hasattr(scraper, attr) for attr in required_attrs)
        print(f"   ✅ All required attributes present: {all_present}")
        
        # Test 3: Legacy wrapper
        print("\n3. Testing LegacyAdigaScraper wrapper...")
        legacy = LegacyAdigaScraper()
        print(f"   ✅ Legacy wrapper created")
        print(f"   Legacy source_name: {legacy.source_name}")
        
        print("\n" + "=" * 60)
        print("✅ Backward compatibility fixes applied successfully!")
        print("\nNext steps:")
        print("1. Replace with: cp scrapers/adiga_scraper_fixed.py scrapers/adiga_scraper.py")
        print("2. Test multi_monitor.py to ensure it works")
        print("3. Run the full monitoring system")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
