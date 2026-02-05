#!/usr/bin/env python3
"""
Adiga.kr scraper for university admission announcements
"""

import requests
from bs4 import BeautifulSoup
import time
from .scraper_base import BaseScraper

class AdigaScraper(BaseScraper):
    """Scraper for Adiga.kr university admission news"""
    
    def __init__(self):
        super().__init__(
            source_name="Adiga (어디가)",
            base_url="https://adiga.kr"
        )
    
    def fetch_articles(self):
        """Fetch admission articles from Adiga.kr"""
        articles = []
        
        try:
            print(f"🌐 Fetching from {self.source_name}...")
            
            # Adiga.kr typically has admission announcements at this path
            url = f"{self.base_url}/BoardList.do?boardID=21&category=1"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article containers - this selector might need adjustment
            article_containers = soup.select('.board-list tbody tr')
            
            for container in article_containers[:10]:  # Limit to 10 articles
                try:
                    # Extract title and link
                    title_elem = container.select_one('.title a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href')
                    
                    if link and not link.startswith('http'):
                        link = self.base_url + link if link.startswith('/') else f"{self.base_url}/{link}"
                    
                    # Extract basic info
                    date_elem = container.select_one('.date')
                    date = date_elem.get_text(strip=True) if date_elem else "날짜 정보 없음"
                    
                    # For Adiga, we might need to visit each article page for full content
                    # For now, use title as content placeholder
                    content = f"{title} - 게시일: {date}"
                    
                    article = {
                        'title': title,
                        'content': content,
                        'url': link,
                        'date': date,
                        'source': self.source_name
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"⚠️ Error parsing article: {e}")
                    continue
            
            print(f"   Found {len(articles)} articles from {self.source_name}")
            
        except Exception as e:
            print(f"❌ Error fetching from {self.source_name}: {type(e).__name__}: {e}")
            # Return empty list on error
            return []
        
        return articles

# For backward compatibility with existing code
def create_adiga_scraper():
    """Factory function for backward compatibility"""
    return AdigaScraper()
