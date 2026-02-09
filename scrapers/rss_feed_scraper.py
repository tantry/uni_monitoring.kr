from core.base_scraper import BaseScraper
from models.article import Article
from typing import List, Dict, Any
import feedparser
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RSSFeedScraper(BaseScraper):
    """Generic RSS feed scraper - works with any RSS/Atom feed"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_name = config.get('name', 'rss_feed')
        self.base_url = config.get('url', '')
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles from RSS feed"""
        try:
            logger.info(f"Fetching RSS feed: {self.base_url}")
            feed = feedparser.parse(self.base_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning: {feed.bozo_exception}")
            
            articles = []
            for entry in feed.entries:
                article_data = {
                    'title': entry.get('title', 'No Title'),
                    'url': entry.get('link', ''),
                    'content': entry.get('summary', entry.get('description', entry.get('title', ''))),  # Fallback to title if no summary
                    'published_date': self._parse_date(entry.get('published', '')),
                    'author': entry.get('author', ''),
                    'categories': [tag.get('term', '') for tag in entry.get('tags', [])],
                    'summary': entry.get('summary', ''),
                    'rss_id': entry.get('id', '')
                }
                articles.append(article_data)
            
            logger.info(f"Found {len(articles)} entries in RSS feed")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed: {e}")
            return []
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """Parse RSS entry into Article object"""
        try:
            return Article(
                title=raw_data.get('title', 'No Title'),
                url=raw_data.get('url', ''),
                content=raw_data.get('content', ''),
                source=self.source_name,
                published_date=raw_data.get('published_date'),
                metadata={
                    'author': raw_data.get('author', ''),
                    'categories': raw_data.get('categories', []),
                    'summary': raw_data.get('summary', ''),
                    'rss_id': raw_data.get('rss_id', '')
                }
            )
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return None
    
    def get_source_name(self) -> str:
        return self.source_name
    
    def _parse_date(self, date_str: str) -> str:
        """Convert RSS date to ISO format"""
        if not date_str:
            return datetime.now().isoformat()
        
        try:
            from dateutil import parser
            dt = parser.parse(date_str)
            return dt.isoformat()
        except:
            return datetime.now().isoformat()
