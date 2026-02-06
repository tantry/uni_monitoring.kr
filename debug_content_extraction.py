#!/usr/bin/env python3
"""
Debug why content extraction isn't working
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Debugging Content Extraction")
print("=" * 50)

from scrapers.adiga_scraper_with_content import AdigaScraper

scraper = AdigaScraper()

# Test with a specific article URL
test_url = "https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBbsId=26546"

print(f"1. Testing URL: {test_url}")
print(f"   Session cookies: {len(scraper.session.cookies)}")

# Fetch the page
response = scraper.session.get(test_url, timeout=10, allow_redirects=True)
print(f"2. Response status: {response.status_code}")
print(f"   Content length: {len(response.text)} chars")

# Save for analysis
with open('debug_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

# Check for hidden content
from bs4 import BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

print("\n3. Looking for hidden content...")
hidden_input = soup.find('input', {'id': 'lnaCn1'})
if hidden_input:
    print(f"   Found lnaCn1 input!")
    value = hidden_input.get('value', '')
    print(f"   Value length: {len(value)} chars")
    print(f"   First 200 chars: {value[:200]}...")
    
    # Try to decode
    import html
    try:
        decoded = html.unescape(value)
        print(f"\n   Decoded length: {len(decoded)} chars")
        
        # Parse decoded HTML
        content_soup = BeautifulSoup(decoded, 'html.parser')
        text = content_soup.get_text()
        print(f"   Extracted text length: {len(text)} chars")
        print(f"   First 200 chars: {text[:200]}...")
    except Exception as e:
        print(f"   Decode error: {e}")
else:
    print("   ❌ No lnaCn1 input found!")
    
    # List all inputs
    inputs = soup.find_all('input')
    print(f"   Found {len(inputs)} input elements")
    for inp in inputs[:5]:
        inp_id = inp.get('id', 'no-id')
        print(f"   - Input id: {inp_id}")

print("\n4. Testing _enhance_with_actual_content method...")
test_article = {
    'title': 'Test Article',
    'content': 'Preview content',
    'url': test_url,
    'article_id': '26546',
    'metadata': {}
}

try:
    enhanced = scraper._enhance_with_actual_content(test_article)
    print(f"   Enhanced content length: {len(enhanced.get('content', ''))} chars")
    print(f"   Has actual content: {enhanced.get('metadata', {}).get('has_actual_content', False)}")
    print(f"   Content source: {enhanced.get('metadata', {}).get('content_source', 'none')}")
except Exception as e:
    print(f"   Enhancement error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Debug complete")
