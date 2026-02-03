#!/usr/bin/env python3
"""
Test that links are now correct
"""
import requests
from bs4 import BeautifulSoup
import re

def extract_article_link_test(title_tag):
    """
    Test version of the extract_article_link function
    """
    # Look for onclick with fnDetailPopup in parent chain
    element = title_tag
    for _ in range(5):  # Check up to 5 parent levels
        if element is None:
            break
            
        # Check for onclick with fnDetailPopup
        onclick = element.get('onclick', '')
        if onclick and 'fnDetailPopup' in onclick:
            match = re.search(r'fnDetailPopup\("([^"]+)"\)', onclick)
            if match:
                article_id = match.group(1)
                # Create direct article link
                direct_link = f"https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBbsId={article_id}"
                return direct_link
        
        # Move to parent
        element = element.parent
    
    return "https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000"

# Simulate getting an article
AJAX_URL = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
headers = {
    'User-Agent': 'Mozilla/5.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000'
}
form_data = {'menuId': 'PCUCTNMG2000', 'currentPage': '1', 'cntPerPage': '3'}

print("Testing corrected link generation...")
print("=" * 60)

try:
    response = requests.post(AJAX_URL, headers=headers, data=form_data, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    title_tags = soup.find_all(class_='uctCastTitle')
    
    if title_tags:
        print(f"Found {len(title_tags)} articles")
        print()
        
        for i, title_tag in enumerate(title_tags[:3]):  # Test first 3
            title = title_tag.get_text(strip=True)
            link = extract_article_link_test(title_tag)
            
            print(f"Article {i+1}: {title[:50]}...")
            print(f"Generated link: {link}")
            
            # Check if it's correct
            if 'uct/nmg/enw/newsDetail.do?prtlBbsId=' in link:
                print("✅ LINK IS CORRECT!")
                print("   - Path: uct/nmg/enw/ ✓")
                print("   - Parameter: prtlBbsId= ✓")
                
                # Extract article ID
                article_id = link.split('=')[-1]
                print(f"   - Article ID: {article_id} ✓")
                
                # Test if link works
                try:
                    test_response = requests.head(link, timeout=5)
                    status = test_response.status_code
                    print(f"   - HTTP Status: {status}")
                    
                    if status == 200:
                        print("   - Link is accessible ✓")
                    elif status == 404:
                        print("   - ⚠️  Link returns 404 (page not found)")
                    else:
                        print(f"   - ⚠️  Unexpected status: {status}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"   - ❌ Could not access link: {e}")
            else:
                print("❌ LINK IS STILL WRONG!")
                print(f"   Problem: Missing correct pattern")
            
            print("-" * 40)
            
    else:
        print("Could not find articles to test")
        
except Exception as e:
    print(f"Error during test: {e}")

print("=" * 60)
print("Test complete.")
