import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.adiga.kr"

def explore_menu():
    """Explore Adiga's menu structure."""
    print("Exploring Adiga website structure...\n")
    
    # Try to find sitemap or main page
    urls_to_check = [
        "https://www.adiga.kr",
        "https://www.adiga.kr/sitemap.xml",
        "https://www.adiga.kr/main.do",
        "https://www.adiga.kr/index.do",
    ]
    
    for url in urls_to_check:
        print(f"Checking: {url}")
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for menu items
                menu_items = soup.find_all(['a', 'li'], class_=re.compile(r'menu|nav|tab', re.I))
                print(f"  Found {len(menu_items)} potential menu items")
                
                # Look for links containing keywords
                keywords = ["대학", "입학", "모집", "공지", "추가", "입시", "announce", "notice", "admission"]
                for keyword in keywords:
                    links = soup.find_all('a', string=re.compile(keyword, re.I))
                    if links:
                        print(f"  Links with '{keyword}':")
                        for link in links[:3]:  # Just show 3
                            href = link.get('href', '')
                            if href and not href.startswith('javascript'):
                                full_url = href if href.startswith('http') else BASE_URL + href
                                print(f"    - {link.get_text(strip=True)[:30]} -> {full_url[:50]}...")
                print()
                
        except Exception as e:
            print(f"  Error: {e}")

def search_adiga_for_keywords():
    """Search Adiga for relevant keywords."""
    print("\n" + "="*60)
    print("SEARCHING FOR KEYWORDS IN ADIGA:")
    print("="*60)
    
    # Test search on Adiga
    search_keywords = ["추가모집", "입시공고", "대학공지", "입학안내"]
    
    for keyword in search_keywords:
        encoded_keyword = requests.utils.quote(keyword)
        search_url = f"https://www.adiga.kr/search.do?searchKeyword={encoded_keyword}"
        
        print(f"\nSearching for '{keyword}':")
        print(f"  URL: {search_url}")
        try:
            response = requests.get(search_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for result items
                results = soup.find_all(['a', 'div'], class_=re.compile(r'result|item|list', re.I))
                print(f"  Found {len(results)} potential result items")
                
                # Extract links
                links = soup.find_all('a', href=True)
                relevant_links = []
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()
                    if keyword.lower() in text or '공고' in text or '모집' in text:
                        if href and not href.startswith('javascript'):
                            full_url = href if href.startswith('http') else BASE_URL + href
                            relevant_links.append((text[:40], full_url))
                
                if relevant_links:
                    print(f"  Relevant links found:")
                    for text, url in relevant_links[:3]:  # Just show 3
                        print(f"    - {text}...")
                        print(f"      -> {url}")
                else:
                    print(f"  No obvious relevant links found")
                    
        except Exception as e:
            print(f"  Search error: {e}")

def test_potential_urls():
    """Test some potential URLs we already know about."""
    print("\n" + "="*60)
    print("TESTING KNOWN POTENTIAL URLS:")
    print("="*60)
    
    urls_to_test = [
        ("University Search", "https://www.adiga.kr/man/inf/mainView.do?menuId=PCMANINF1000"),
        ("University View", "https://www.adiga.kr/ucp/uvt/uni/univView.do?menuId=PCUVTINF2000"),
        ("News View (current)", "https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000"),
    ]
    
    for name, url in urls_to_test:
        print(f"\nTesting: {name}")
        print(f"  URL: {url}")
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for keywords in page
                content = soup.get_text()
                keywords = ["추가모집", "국립대", "공고", "모집", "입학"]
                found_keywords = []
                for kw in keywords:
                    if kw in content:
                        found_keywords.append(kw)
                
                if found_keywords:
                    print(f"  Found keywords: {', '.join(found_keywords)}")
                
                # Check page title
                title = soup.find('title')
                if title:
                    print(f"  Page title: {title.get_text(strip=True)[:50]}...")
                
                # Estimate content size
                print(f"  Content size: {len(content)} characters")
                
                # Look for list/table structures
                lists = soup.find_all(['ul', 'ol', 'table'])
                print(f"  Found {len(lists)} list/table elements")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    print("="*60)
    print("ADIGA WEBSITE EXPLORATION TOOL")
    print("="*60)
    
    explore_menu()
    search_adiga_for_keywords()
    test_potential_urls()
    
    print("\n" + "="*60)
    print("MANUAL INVESTIGATION CHECKLIST:")
    print("="*60)
    print("""
PLEASE CHECK THESE MANUALLY IN YOUR BROWSER:

1. UNIVERSITY SEARCH PAGES:
   - https://www.adiga.kr/man/inf/mainView.do?menuId=PCMANINF1000
   - Can you search for specific universities here?
   - Does it show individual university profiles?

2. UNIVERSITY DETAIL PAGES:
   - https://www.adiga.kr/ucp/uvt/uni/univView.do?menuId=PCUVTINF2000
   - Try entering a university name (e.g., "경상국립대학교")
   - Look for "공지사항" or "입학공고" tabs

3. DIRECT SEARCHES:
   - https://www.adiga.kr/search.do?searchKeyword=추가모집
   - https://www.adiga.kr/search.do?searchKeyword=국립대+입학공고
   - Do these show actual university announcements?

4. LOOK FOR:
   - Bulletin boards (/bbs/, /board/, /list.do)
   - Notice sections ("공지사항", "새소식", "입학안내")
   - University-specific pages

WHEN YOU FIND A PROMISING PAGE:
1. Right-click → "Inspect" on the announcement list
2. Find the container (like <ul class="list"> or <div class="board">)
3. Share the URL and container info with me
    """)
