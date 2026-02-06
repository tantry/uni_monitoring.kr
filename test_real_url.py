#!/usr/bin/env python3
"""
Test what URL actually works with session
"""
import requests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try the working pattern from uni_monitor.py
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000'
})

print("Testing URL access with session...")
print("=" * 50)

# First establish session
print("1. Establishing session...")
main_response = session.get('https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000', timeout=10)
print(f"   Main page: {main_response.status_code}")
print(f"   Cookies: {len(session.cookies)}")

# Get articles via AJAX
print("\n2. Getting articles via AJAX...")
form_data = {
    'menuId': 'PCUCTNMG2000',
    'currentPage': '1',
    'cntPerPage': '20',
    'searchKeywordType': 'title',
    'searchKeyword': '',
}

response = session.post('https://www.adiga.kr/uct/nmg/enw/newsAjax.do', data=form_data, timeout=15)
print(f"   AJAX response: {response.status_code}")

if response.status_code == 200:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find first article link
    articles = soup.find_all(class_='uctCastTitle')
    print(f"\n3. Found {len(articles)} articles")
    
    if articles:
        first_article = articles[0]
        # Try to find onclick
        parent = first_article.find_parent(['li', 'tr', 'div'])
        if parent:
            onclick_elem = parent.find(onclick=True)
            if onclick_elem:
                onclick = onclick_elem.get('onclick', '')
                print(f"   onclick: {onclick}")
                
                # Extract article ID
                import re
                match = re.search(r'fnDetailPopup\(["\'](\d+)["\']\)', onclick)
                if match:
                    article_id = match.group(1)
                    print(f"   Article ID: {article_id}")
                    
                    # Test different URL patterns
                    print("\n4. Testing URL patterns:")
                    
                    patterns = [
                        f"https://adiga.kr/ArticleDetail.do?articleID={article_id}",
                        f"https://www.adiga.kr/uct/nmg/enw/newsView.do?articleID={article_id}",
                        f"https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000&articleID={article_id}",
                        f"https://www.adiga.kr/BoardView.do?articleID={article_id}",
                    ]
                    
                    for pattern in patterns:
                        print(f"\n   Testing: {pattern}")
                        test_response = session.get(pattern, timeout=10)
                        print(f"   Status: {test_response.status_code}")
                        if test_response.status_code == 200:
                            print(f"   ✅ WORKING! Title: {test_response.text[:100]}...")
                            break
                        else:
                            print(f"   ❌ {test_response.status_code}")
                
print("\n" + "=" * 50)
print("Test complete")
