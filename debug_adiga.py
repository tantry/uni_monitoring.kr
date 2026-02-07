#!/usr/bin/env python3
"""
Debug script for Adiga scraper
"""
import sys
sys.path.insert(0, '.')

from bs4 import BeautifulSoup
import requests
import re

def test_adiga_direct():
    """Test direct access to Adiga.kr"""
    print("=== Testing direct access to Adiga.kr ===")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    try:
        # Test basic connection
        url = "https://adiga.kr"
        print(f"Fetching: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Save for inspection
        with open('adiga_debug.html', 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print("Saved HTML to adiga_debug.html")
        
        # Look for ANY links
        print("\n=== Analyzing page structure ===")
        
        # Find all links
        all_links = soup.find_all('a')
        print(f"Total <a> tags found: {len(all_links)}")
        
        # Check first 20 links
        print("\nFirst 20 links:")
        for i, link in enumerate(all_links[:20]):
            href = link.get('href', '')
            onclick = link.get('onclick', '')
            text = link.get_text(strip=True)
            
            print(f"{i+1:2d}. Text: {text[:50]}...")
            print(f"    Href: {href}")
            print(f"    Onclick: {onclick[:50]}..." if onclick else "    Onclick: (none)")
            print()
        
        # Look for ArticleDetail links specifically
        print("\n=== Looking for ArticleDetail links ===")
        article_links = []
        
        # Method 1: href containing ArticleDetail
        href_matches = soup.find_all('a', href=re.compile('ArticleDetail', re.I))
        print(f"Links with 'ArticleDetail' in href: {len(href_matches)}")
        
        # Method 2: onclick containing fnDetailPopup
        onclick_matches = soup.find_all('a', onclick=re.compile('fnDetailPopup', re.I))
        print(f"Links with 'fnDetailPopup' in onclick: {len(onclick_matches)}")
        
        # Method 3: Common patterns
        patterns = [
            'article', 'news', 'board', 'list', 'view', 'detail',
            '공지', '공고', '안내', '입학', '모집'
        ]
        
        for pattern in patterns:
            matches = soup.find_all('a', string=re.compile(pattern, re.I))
            if matches:
                print(f"Links with '{pattern}' in text: {len(matches)}")
        
        # Show detailed info for fnDetailPopup links
        if onclick_matches:
            print("\n=== Detailed fnDetailPopup links ===")
            for i, link in enumerate(onclick_matches[:5]):
                onclick = link.get('onclick', '')
                text = link.get_text(strip=True)
                
                # Extract article ID
                match = re.search(r"fnDetailPopup\s*\(\s*['\"]?(\d+)['\"]?\s*\)", onclick)
                article_id = match.group(1) if match else "N/A"
                
                print(f"{i+1}. Text: {text}")
                print(f"   Onclick: {onclick}")
                print(f"   Article ID: {article_id}")
                print(f"   Constructed URL: https://adiga.kr/ArticleDetail.do?articleID={article_id}")
                print()
        
        # Test JavaScript link resolution
        print("\n=== Testing JavaScript link resolution ===")
        
        class MockElement:
            def __init__(self, href='', onclick=''):
                self.href = href
                self.onclick = onclick
            
            def get(self, attr, default=''):
                if attr == 'href':
                    return self.href
                elif attr == 'onclick':
                    return self.onclick
                return default
        
        test_cases = [
            ("", "fnDetailPopup('12345')"),
            ("", "fnDetailPopup('67890')"),
            ("ArticleDetail.do?articleID=55555", ""),
            ("/ArticleDetail.do?articleID=66666", ""),
            ("javascript:void(0)", "fnDetailPopup('77777')"),
        ]
        
        base_url = "https://adiga.kr"
        
        for href, onclick in test_cases:
            element = MockElement(href, onclick)
            
            # Simple resolution logic
            result_url = base_url
            
            if onclick:
                match = re.search(r"fnDetailPopup\s*\(\s*['\"]?(\d+)['\"]?\s*\)", onclick)
                if match:
                    article_id = match.group(1)
                    result_url = f"{base_url}/ArticleDetail.do?articleID={article_id}"
            elif href:
                if href.startswith('javascript:'):
                    result_url = base_url
                elif not href.startswith(('http://', 'https://')):
                    if href.startswith('/'):
                        result_url = f"{base_url}{href}"
                    else:
                        result_url = f"{base_url}/{href}"
                else:
                    result_url = href
            
            print(f"Href: {href:30} Onclick: {onclick:30} -> {result_url}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_fixed_scraper():
    """Test the fixed scraper logic"""
    print("\n=== Testing fixed scraper logic ===")
    
    from scrapers.adiga_scraper import AdigaScraper
    
    config = {
        'url': 'https://adiga.kr',
        'name': 'Adiga Test'
    }
    
    scraper = AdigaScraper(config)
    
    # Test link resolution directly
    print("\nTesting resolve_link method:")
    
    test_links = [
        ("", "fnDetailPopup('12345')"),
        ("", "fnDetailPopup( '67890' )"),
        ("", "fnDetailPopup(\"99999\")"),
        ("ArticleDetail.do?articleID=55555", ""),
        ("/board/view.php?idx=777", ""),
        ("javascript:void(0)", "fnDetailPopup('88888')"),
        ("https://adiga.kr/full/url", ""),
    ]
    
    for href, onclick in test_links:
        result = scraper.resolve_link(href, onclick)
        print(f"Href: {href:35} Onclick: {onclick:35} -> {result}")
    
    # Try to scrape
    print("\nTrying to scrape...")
    try:
        articles = scraper.scrape()
        print(f"Scraped {len(articles)} articles")
        
        for i, article in enumerate(articles[:3]):
            print(f"\n{i+1}. {article.title}")
            print(f"   URL: {article.url}")
            if article.content:
                print(f"   Content: {article.content[:100]}...")
    except Exception as e:
        print(f"Scraping error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_adiga_direct()
    test_fixed_scraper()
