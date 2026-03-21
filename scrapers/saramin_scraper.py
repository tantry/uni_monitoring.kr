"""
Saramin job search scraper - fetches all jobs from search results
Filtering happens in filter_engine, not here
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_scraper import BaseScraper
from models.article import Article
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class SaraminScraper(BaseScraper):
    """
    Fetches job listings from Saramin search
    Returns ALL jobs - filtering is done by filter_engine
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_name = "Saramin Jobs"
        self.base_url = "https://www.saramin.co.kr/zf_user/search"
        
        # Search keyword - broad to get all jobs
        self.search_keyword = config.get('search_keyword', '')
        self.max_pages = config.get('max_pages', 3)
        self.jobs_per_page = config.get('jobs_per_page', 30)
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        })
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch all jobs from Saramin search"""
        all_jobs = []
        
        for page in range(1, self.max_pages + 1):
            jobs = self._fetch_page(page)
            if not jobs:
                break
            all_jobs.extend(jobs)
            logger.info(f"Page {page}: found {len(jobs)} jobs")
            time.sleep(1)  # Be nice to server
        
        logger.info(f"Total jobs fetched: {len(all_jobs)}")
        return all_jobs
    
    def _fetch_page(self, page: int) -> List[Dict[str, Any]]:
        """Fetch a single page of search results"""
        try:
            params = {
                'searchType': 'search',
                'searchword': self.search_keyword,
                'recruitPage': page,
                'recruitSort': 'reg_dt',
                'recruitPageCount': self.jobs_per_page,
            }
            
            response = self.session.get(self.base_url, params=params, timeout=15)
            if response.status_code != 200:
                logger.warning(f"Page {page} failed: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            job_items = soup.select('.item_recruit') or soup.select('.list_item')
            
            jobs = []
            for job in job_items:
                parsed = self._parse_job(job)
                if parsed:
                    jobs.append(parsed)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error fetching page {page}: {e}")
            return []
    
    def _parse_job(self, job_element) -> Dict[str, Any]:
        """Parse a single job listing into article format"""
        try:
            title_elem = job_element.select_one('.job_tit a, .title a')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            if link and not link.startswith('http'):
                link = 'https://www.saramin.co.kr' + link
            
            company_elem = job_element.select_one('.corp_name a, .company a')
            company = company_elem.get_text(strip=True) if company_elem else ''
            
            # Extract requirements (학력, 경력, etc.)
            requirements = []
            spec_elem = job_element.select_one('.job_spec, .spec')
            if spec_elem:
                for spec in spec_elem.select('span'):
                    requirements.append(spec.get_text(strip=True))
            
            # Extract location
            location_elem = job_element.select_one('.work_place, .loc')
            location = location_elem.get_text(strip=True) if location_elem else ''
            
            # Build content for filtering
            content = f"{title} {company} {' '.join(requirements)} {location}"
            
            return {
                'title': title,
                'url': link,
                'content': content,
                'company': company,
                'location': location,
                'requirements': requirements,
                'published_date': datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.debug(f"Parse error: {e}")
            return None
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        return Article(
            title=raw_data.get('title', 'No Title'),
            url=raw_data.get('url', ''),
            content=raw_data.get('content', ''),
            source=self.source_name,
            published_date=raw_data.get('published_date', ''),
            metadata={
                'company': raw_data.get('company', ''),
                'location': raw_data.get('location', ''),
                'requirements': raw_data.get('requirements', []),
            }
        )
    
    def get_source_name(self) -> str:
        return self.source_name


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scraper = SaraminScraper({
        'search_keyword': '',  # Empty = all jobs
        'max_pages': 2,
        'jobs_per_page': 30
    })
    
    jobs = scraper.fetch_articles()
    print(f"\nFound {len(jobs)} jobs")
    for j in jobs[:5]:
        print(f"\n- {j['title']}")
        print(f"  {j.get('company', 'N/A')}")
