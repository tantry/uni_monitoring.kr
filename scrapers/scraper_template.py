"""
Template for new scraper implementations
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Import from your project structure
try:
    from core.base_scraper import BaseScraper
    from models.article import Article
except ImportError:
    # Fallback for testing
    class BaseScraper:
        def __init__(self, config):
            self.config = config
    
    class Article:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

logger = logging.getLogger(__name__)

class TemplateScraper(BaseScraper):
    """Scraper template for new sources"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = "https://example.com"
        self.source_name = "template_source"
        self.session = None  # For requests session
        
    def fetch_articles(self) -> List[Dict]:
        """
        Fetch articles from the source.
        
        Returns:
            List of dictionaries with raw article data
            
        Structure for each article:
        {
            'title': 'Article Title',
            'url': 'https://example.com/article/123',
            'content': 'Article content or preview',
            'source': self.source_name,
            'published_date': '2026-02-07',
            'raw_html': '<html>...</html>'  # Optional
        }
        """
        articles = []
        
        try:
            # TODO: Implement actual fetching logic
            # Example:
            # 1. Setup requests session if needed
            # 2. Fetch the main page or API endpoint
            # 3. Parse HTML/JSON response
            # 4. Extract article elements
            # 5. Format into dictionary
            
            # Example mock data (remove in actual implementation):
            if self.config.get('test_mode', False):
                articles = [
                    {
                        'title': '[테스트] 서울대학교 음악학과 2026학년도 모집',
                        'url': f'{self.base_url}/article/123',
                        'content': '서울대학교 음악학과에서 2026학년도 수시모집을 실시합니다.',
                        'source': self.source_name,
                        'published_date': datetime.now().strftime('%Y-%m-%d'),
                    },
                    {
                        'title': '[테스트] 연세대학교 영어영문학과 편입학 안내',
                        'url': f'{self.base_url}/article/456',
                        'content': '2026학년도 편입학 모집 일정이 공개되었습니다.',
                        'source': self.source_name,
                        'published_date': datetime.now().strftime('%Y-%m-%d'),
                    }
                ]
            
            logger.info(f"Fetched {len(articles)} articles from {self.source_name}")
            
        except Exception as e:
            logger.error(f"Error fetching articles from {self.source_name}: {e}")
            import traceback
            traceback.print_exc()
        
        return articles
    
    def parse_article(self, raw_data: Dict) -> Article:
        """
        Parse raw article data into Article model.
        
        Args:
            raw_data: Dictionary with raw article data
            
        Returns:
            Article object
        """
        try:
            # Detect department
            department = self.detect_department(raw_data)
            
            # Create Article object
            article = Article(
                title=raw_data.get('title', ''),
                url=raw_data.get('url', ''),
                content=raw_data.get('content', ''),
                source=raw_data.get('source', self.source_name),
                published_date=raw_data.get('published_date'),
                department=department,
                metadata={
                    'fetched_at': datetime.now().isoformat(),
                    'source_name': self.source_name,
                }
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            # Return error article
            return Article(
                title="Parse Error",
                url=raw_data.get('url', ''),
                content=f"Error parsing article: {str(e)}",
                source=self.source_name,
                department=None
            )
    
    def detect_department(self, article_data: Dict) -> Optional[str]:
        """
        Detect which department this article belongs to.
        
        Args:
            article_data: Raw article data
            
        Returns:
            Department name or None
        """
        # Combine title and content for keyword search
        content = f"{article_data.get('title', '')} {article_data.get('content', '')}"
        content_lower = content.lower()
        
        # Department keyword mapping
        # Update this based on config/filters.yaml
        department_keywords = {
            'music': ['음악', '실용음악', '성악', '작곡', 'music'],
            'korean': ['한국어', '국어국문', '국문학', '국어'],
            'english': ['영어', '영어영문', '영문학', 'english'],
            'liberal': ['인문', '인문학', '교양교육', '교양'],
        }
        
        # Check each department
        for dept, keywords in department_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                logger.debug(f"Article matched department '{dept}': {article_data.get('title', '')[:50]}")
                return dept
        
        return None
    
    def get_source_name(self) -> str:
        """Return unique source identifier"""
        return self.source_name
    
    def test_connection(self) -> bool:
        """
        Test connection to the source.
        
        Returns:
            True if connection successful
        """
        try:
            # TODO: Implement actual connection test
            # Example: requests.get(self.base_url, timeout=5)
            return True
        except Exception:
            return False


# Test the scraper
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    print("Testing TemplateScraper...")
    
    # Create scraper with test mode
    config = {'test_mode': True}
    scraper = TemplateScraper(config)
    
    print(f"Source name: {scraper.get_source_name()}")
    print(f"Base URL: {scraper.base_url}")
    
    # Test fetching
    articles = scraper.fetch_articles()
    print(f"\nFetched {len(articles)} articles:")
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article.get('title')}")
        print(f"   URL: {article.get('url')}")
        
        # Test parsing
        parsed = scraper.parse_article(article)
        print(f"   Department: {parsed.department}")
    
    print("\n✅ Template scraper test complete")
    print("\nTo create a new scraper:")
    print("1. cp scrapers/scraper_template.py scrapers/your_source_scraper.py")
    print("2. Edit the class name and implementation")
    print("3. Test with: python scrapers/your_source_scraper.py")
