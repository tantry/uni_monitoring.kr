import requests
from bs4 import BeautifulSoup

print("=== Testing URL Issue ===")

# Test with different session setups
test_cases = [
    {
        'name': 'Default session',
        'session': requests.Session(),
        'headers': {}
    },
    {
        'name': 'Session with headers',
        'session': requests.Session(),
        'headers': {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
    }
]

url = "https://adiga.kr"

for test in test_cases:
    print(f"\n--- {test['name']} ---")
    session = test['session']
    
    if test['headers']:
        session.headers.update(test['headers'])
    
    try:
        print(f"Fetching {url}...")
        response = session.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")
        
        # Save the response
        filename = f"debug_{test['name'].replace(' ', '_').lower()}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved to: {filename}")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for links
        links = soup.find_all('a')
        print(f"Total links found: {len(links)}")
        
        # Show first 5 links with href
        print("\nFirst 5 links with href:")
        count = 0
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if href:
                print(f"  Text: {text[:30]}...")
                print(f"  Href: {href}")
                count += 1
                if count >= 5:
                    break
        
        # Check for onclick with fnDetailPopup
        print("\nChecking for fnDetailPopup...")
        onclick_elements = soup.find_all(attrs={'onclick': True})
        fn_detail_count = 0
        for element in onclick_elements:
            onclick = element.get('onclick', '')
            if 'fnDetailPopup' in onclick:
                fn_detail_count += 1
                if fn_detail_count <= 3:
                    text = element.get_text(strip=True)
                    print(f"  Found: {onclick[:50]}...")
                    print(f"  Text: {text[:30]}...")
        
        print(f"Total fnDetailPopup elements: {fn_detail_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

print("\n=== Checking base_scraper session ===")
try:
    from core.base_scraper import BaseScraper
    
    class TestScraper(BaseScraper):
        def get_source_name(self):
            return 'test'
        
        def fetch_articles(self):
            return []
        
        def parse_article(self, raw_data):
            return None
    
    scraper = TestScraper({'url': 'https://adiga.kr'})
    print(f"Scraper session headers: {dict(scraper.session.headers)}")
    
    # Try to fetch
    try:
        response = scraper.session.get('https://adiga.kr', timeout=10)
        print(f"BaseScraper session status: {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")
    except Exception as e:
        print(f"BaseScraper session error: {e}")
        
except ImportError as e:
    print(f"Could not import BaseScraper: {e}")

print("\n=== Debug Complete ===")
