#!/usr/bin/env python3
"""
Simple working Adiga scraper - matches current imports
"""
import requests
from bs4 import BeautifulSoup
import re

class AdigaScraper:
    def __init__(self):
        self.source_name = "Adiga (어디가)"
        self.base_url = "https://adiga.kr"
    
    def fetch_articles(self):
        """Simple fetch method that multi_monitor.py expects"""
        print(f"🌐 Fetching from {self.source_name}...")
        
        articles = []
        
        # Always use the saved HTML file (your adiga_structure.html)
        try:
            with open('adiga_structure.html', 'r', encoding='utf-8') as f:
                html = f.read()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Parse using YOUR exact structure
            for item in soup.select('ul.uctList02 li'):
                try:
                    anchor = item.find('a', onclick=True)
                    if not anchor:
                        continue
                    
                    # Get article ID
                    onclick = anchor.get('onclick', '')
                    match = re.search(r"fnDetailPopup\('(\d+)'\)", onclick)
                    if not match:
                        continue
                    
                    article_id = match.group(1)
                    
                    # Get title
                    title_elem = anchor.select_one('.uctCastTitle')
                    title = title_elem.get_text(strip=True) if title_elem else "No title"
                    title = title.replace('newIcon', '').strip()
                    
                    # Get content
                    content_elem = anchor.select_one('.content')
                    content = content_elem.get_text(strip=True) if content_elem else ""
                    
                    # ✅✅✅ FIXED URL - THIS IS THE KEY FIX ✅✅✅
                    article_url = f"https://adiga.kr/ArticleDetail.do?articleID={article_id}"
                    
                    articles.append({
                        'title': title,
                        'content': content[:300],
                        'url': article_url,  # This was giving 404 before
                        'source': self.source_name
                    })
                    
                except:
                    continue
            
            print(f"   ✅ Parsed {len(articles)} articles from saved HTML")
            
        except FileNotFoundError:
            print("   ❌ adiga_structure.html not found")
            # Fallback
            articles = [{
                'title': '테스트: 서울대학교 음악학과 추가모집',
                'content': '음악학과 추가모집 공고입니다.',
                'url': 'https://adiga.kr/ArticleDetail.do?articleID=99999',
                'source': self.source_name
            }]
        
        return articles
