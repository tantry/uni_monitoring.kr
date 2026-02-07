import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests
from urllib.parse import urljoin
from models.article import Article

class BaseScraper(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get('url', '')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with proper headers"""
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        session.headers.update(headers)
        return session
    
    def resolve_link(self, href: str, onclick: str = '') -> str:
        """Resolve JavaScript links like fnDetailPopup('12345')"""
        import re
        
        # Check for JavaScript links
        js_patterns = [
            r"fnDetailPopup\s*\(\s*['\"]?(\d+)['\"]?\s*\)",
            r"location\.href\s*=\s*['\"]([^'\"]+)['\"]",
            r"open\s*\(\s*['\"]([^'\"]+)['\"]"
        ]
        
        for pattern in js_patterns:
            match = re.search(pattern, onclick)
            if match:
                article_id = match.group(1)
                if 'fnDetailPopup' in onclick:
                    return f"{self.base_url}/ArticleDetail.do?articleID={article_id}"
                return urljoin(self.base_url, article_id)
        
        # Handle regular links
        if href and href.startswith('javascript:'):
            return self.base_url
        
        if href and not href.startswith(('http://', 'https://')):
            return urljoin(self.base_url, href)
        
        return href if href else self.base_url
    
    @abstractmethod
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch raw article data from source"""
        pass
    
    @abstractmethod
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """Parse raw data into Article object"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Return unique source identifier"""
        pass
    
    def scrape(self) -> List[Article]:
        """Main scraping method"""
        try:
            raw_articles = self.fetch_articles()
            articles = []
            
            for raw in raw_articles:
                try:
                    article = self.parse_article(raw)
                    if article and article.title and article.url:
                        articles.append(article)
                        self.logger.debug(f"Parsed: {article.title}")
                except Exception as e:
                    self.logger.error(f"Error parsing article: {e}")
            
            self.logger.info(f"Scraped {len(articles)} articles from {self.get_source_name()}")
            return articles
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            return []
