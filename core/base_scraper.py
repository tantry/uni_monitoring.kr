#!/usr/bin/env python3
"""
Base scraper abstract class for all university admission scrapers
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional, Any
import hashlib
import json
from pathlib import Path
import logging

class BaseScraper(ABC):
    """Abstract base class for all university admission scrapers"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize scraper with configuration
        
        Args:
            config: Dictionary with scraper configuration including:
                   - name: Display name of source
                   - base_url: Base URL for scraping
                   - timeout: Request timeout in seconds
                   - retry_attempts: Number of retry attempts
        """
        self.config = config
        self.name = config.get('name', 'Unknown')
        self.base_url = config.get('base_url', '')
        self.timeout = config.get('timeout', 30)
        self.retry_attempts = config.get('retry_attempts', 3)
        
        # Setup logging
        self.logger = logging.getLogger(f"scraper.{self.name}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Setup storage
        self.storage_path = Path("data") / self.name
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Initialized scraper for {self.name}")
    
    @abstractmethod
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """
        Fetch raw articles from source
        
        Returns:
            List of raw article data dictionaries
        """
        pass
    
    @abstractmethod
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw article data into standardized format
        
        Args:
            raw_data: Raw article data from fetch_articles()
            
        Returns:
            Standardized article dictionary with required fields
        """
        pass
    
    def normalize_program_data(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize a list of articles to ensure consistent format
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of normalized article dictionaries
        """
        normalized = []
        for article in articles:
            normalized.append(self._ensure_article_format(article))
        return normalized
    
    def _ensure_article_format(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure article has all required fields
        
        Args:
            article: Article dictionary
            
        Returns:
            Article with all required fields
        """
        # Required fields
        required = {
            'id': article.get('id') or self.generate_id(article),
            'title': article.get('title', ''),
            'url': article.get('url', ''),
            'source': self.name,
            'scraped_at': datetime.now().isoformat(),
        }
        
        # Optional fields with defaults
        optional = {
            'content': article.get('content', ''),
            'published_date': article.get('published_date'),
            'deadline': article.get('deadline'),
            'university': article.get('university'),
            'department': article.get('department'),
            'metadata': article.get('metadata', {}),
        }
        
        return {**required, **optional}
    
    def generate_id(self, article: Dict[str, Any]) -> str:
        """
        Generate unique ID for an article
        
        Args:
            article: Article dictionary
            
        Returns:
            Unique ID string
        """
        content = f"{article.get('title', '')}{article.get('url', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method that orchestrates fetching and parsing
        
        Returns:
            List of normalized article dictionaries
        """
        self.logger.info(f"Starting scrape for {self.name}")
        
        try:
            # Fetch raw articles
            raw_articles = self.fetch_articles()
            self.logger.info(f"Fetched {len(raw_articles)} raw articles")
            
            # Parse each article
            parsed_articles = []
            for raw_article in raw_articles:
                try:
                    parsed = self.parse_article(raw_article)
                    parsed_articles.append(parsed)
                except Exception as e:
                    self.logger.error(f"Failed to parse article: {e}")
                    continue
            
            # Normalize to ensure consistent format
            normalized_articles = self.normalize_program_data(parsed_articles)
            self.logger.info(f"Successfully processed {len(normalized_articles)} articles")
            
            return normalized_articles
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            return []
    
    def save_detected(self, articles: List[Dict[str, Any]]) -> bool:
        """
        Save detected articles to persistent storage
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            state_file = self.storage_path / f"detected_{datetime.now().date().isoformat()}.json"
            
            state_data = {
                'last_updated': datetime.now().isoformat(),
                'source': self.name,
                'total_articles': len(articles),
                'articles': articles
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Saved {len(articles)} articles to {state_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save detected articles: {e}")
            return False
    
    def load_previous(self) -> List[Dict[str, Any]]:
        """
        Load previously detected articles
        
        Returns:
            List of previously detected article dictionaries
        """
        try:
            # Look for the most recent state file
            state_files = list(self.storage_path.glob("detected_*.json"))
            if not state_files:
                return []
            
            # Get the most recent file
            latest_file = max(state_files, key=lambda p: p.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            return state_data.get('articles', [])
            
        except Exception as e:
            self.logger.warning(f"Could not load previous state: {e}")
            return []
    
    def find_new_programs(self, current_programs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find new programs compared to previous runs
        
        Args:
            current_programs: List of current article dictionaries
            
        Returns:
            List of new article dictionaries
        """
        previous = self.load_previous()
        previous_ids = {p.get('id', '') for p in previous}
        
        new_programs = []
        for program in current_programs:
            program_id = program.get('id', '')
            if program_id and program_id not in previous_ids:
                new_programs.append(program)
        
        self.logger.info(f"Found {len(new_programs)} new programs out of {len(current_programs)}")
        return new_programs
