"""
UNN News RSS Scraper
Fetches articles from https://news.unn.net/rss/allArticle.xml
"""
import time
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import feedparser

from core.base_scraper import BaseScraper
from models.article import Article

logger = logging.getLogger(__name__)

class UNNNewsScraper(BaseScraper):
    """
    Scraper for UNN News RSS feed
    
    RSS Structure Confirmed:
    - 50 entries per feed
    - Fields: title, link, summary, authors, published
    - NO 'content' field - using 'summary' as content
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_name = "unn_news"
        self.base_url = config.get('url', 'https://news.unn.net/rss/allArticle.xml')
        
        # Configure headers for RSS feed access
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; uni_monitoring.kr/1.0; +https://github.com/tantry/uni_monitoring.kr)',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        })
    
    def get_source_name(self) -> str:
        """Return source identifier"""
        return self.source_name
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """
        Main method to fetch articles from RSS feed
        """
        logger.info(f"Starting RSS scrape for {self.source_name}")
        
        articles = []
        
        try:
            # Parse RSS feed
            feed = feedparser.parse(self.base_url)
            
            if not feed.entries:
                logger.warning(f"No entries found in RSS feed for {self.source_name}")
                return articles
            
            logger.info(f"Found {len(feed.entries)} entries in RSS feed")
            
            # Process each entry
            for idx, entry in enumerate(feed.entries, 1):
                try:
                    article_data = self._parse_rss_entry(entry, idx)
                    if article_data:
                        articles.append(article_data)
                            
                except Exception as e:
                    logger.error(f"Error parsing RSS entry {idx}: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(articles)} articles from RSS feed")
            
        except Exception as e:
            logger.error(f"Failed to fetch RSS feed {self.base_url}: {e}")
        
        return articles
    
    def _parse_rss_entry(self, entry, entry_num: int = 0) -> Optional[Dict[str, Any]]:
        """Parse individual RSS entry into standardized format"""
        try:
            # Extract title and URL
            title = entry.get('title', '').strip()
            if not title:
                return None
            
            # Get link
            url = self._extract_link(entry)
            if not url:
                logger.warning(f"Entry {entry_num}: No valid link for '{title[:50]}...'")
                return None
            
            # Extract content from summary field
            content = self._extract_content(entry)
            
            # Get author
            author = self._extract_author(entry)
            
            # Parse published date
            published_date = self._parse_published_date(entry)
            
            # Create article data
            article_data = {
                'title': title,
                'url': url,
                'content': content,
                'summary': content[:500] + "..." if len(content) > 500 else content,
                'published_date': published_date,
                'source': self.source_name,
                'author': author,
                'categories': [],
                'rss_id': entry.get('id', f'unn_{entry_num}'),
            }
            
            return article_data
            
        except Exception as e:
            logger.error(f"Error parsing RSS entry {entry_num}: {e}")
            return None
    
    def _extract_link(self, entry) -> str:
        """Extract URL from RSS entry"""
        if hasattr(entry, 'link') and entry.link:
            return entry.link
        
        if hasattr(entry, 'links') and entry.links:
            for link in entry.links:
                if hasattr(link, 'href') and link.href:
                    return link.href
        
        return ""
    
    def _extract_content(self, entry) -> str:
        """Extract content from RSS entry"""
        if hasattr(entry, 'summary') and entry.summary:
            content = entry.summary.strip()
            
            # Clean HTML tags if present
            if '<' in content and '>' in content:
                content = self._clean_html(content)
            
            return content
        
        if hasattr(entry, 'title') and entry.title:
            return entry.title.strip()
        
        return ""
    
    def _clean_html(self, html_text: str) -> str:
        """Clean HTML tags from text"""
        import re
        html_text = re.sub(r'<(script|style).*?>.*?</\1>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
        html_text = re.sub(r'<[^>]+>', ' ', html_text)
        html_text = re.sub(r'\s+', ' ', html_text).strip()
        return html_text
    
    def _extract_author(self, entry) -> str:
        """Extract author information"""
        if hasattr(entry, 'authors') and entry.authors:
            authors = []
            for author in entry.authors:
                if hasattr(author, 'name') and author.name:
                    authors.append(author.name)
            if authors:
                return ', '.join(authors)
        
        if hasattr(entry, 'author') and entry.author:
            if hasattr(entry.author, 'name'):
                return entry.author.name
            return str(entry.author)
        
        return "UNN 뉴스"
    
    def _parse_published_date(self, entry) -> str:
        """Parse published date from RSS entry"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                dt = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            if hasattr(entry, 'published') and entry.published:
                date_str = entry.published
                
                # Try dateutil if available
                try:
                    from dateutil import parser
                    dt = parser.parse(date_str)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ImportError:
                    # Fallback to string
                    return date_str
                
        except Exception as e:
            logger.warning(f"Could not parse date: {e}")
        
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """Parse raw article data into Article object"""
        return Article(
            title=raw_data.get('title', 'No Title'),
            url=raw_data.get('url', ''),
            content=raw_data.get('content', ''),
            source=self.source_name,
            published_date=raw_data.get('published_date', datetime.now().strftime('%Y-%m-%d')),
            metadata={
                'author': raw_data.get('author', ''),
                'categories': raw_data.get('categories', []),
                'summary': raw_data.get('summary', ''),
                'rss_id': raw_data.get('rss_id', '')
            }
        )
