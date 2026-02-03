#!/usr/bin/env python3
"""
Investigate why we're getting 500 errors on article links
"""
import requests
from bs4 import BeautifulSoup
import re

def investigate():
    print("🔍 Investigating 500 error on article links...\n")
    
    AJAX_URL = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
    REFERER_URL = "https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000"
    
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': REFERER_URL
    }
    
    form_data = {'menuId': 'PCUCTNMG2000', 'currentPage': '1', 'cntPerPage': '5'}
    
    try:
        response = requests.post(AJAX_URL, headers=headers, data=form_data, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        title_tags = soup.find_all(class_='uctCastTitle')
        
        print(f"Found {len(title_tags)} articles in list\n")
        
        for i, title_tag in enumerate(title_tags[:3]):
            title = title_tag.get_text(strip=True)
            print(f"=== Article {i+1}: {title[:50]}... ===")
            
            # Get the onclick value
            element = title_tag
            onclick_content = ""
            for _ in range(5):
                if element is None:
                    break
                onclick = element.get('onclick', '')
                if onclick:
                    onclick_content = onclick
                    break
                element = element.parent
            
            print(f"onclick: {onclick_content[:80]}...")
            
            # Extract article ID
            match = re.search(r'fnDetailPopup\("([^"]+)"\)', onclick_content)
            if match:
                article_id = match.group(1)
                print(f"Extracted Article ID: {article_id}")
                
                # Test the direct link
                direct_link = f"https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBbsId={article_id}"
                
                # Try with session to maintain context
                session = requests.Session()
                session.headers.update(headers)
                
                # First visit the main page to establish session
                try:
                    main_page = session.get(REFERER_URL, timeout=10)
                    print(f"Main page status: {main_page.status_code}")
                except:
                    pass
                
                # Now try the article
                try:
                    article_resp = session.get(direct_link, timeout=10, allow_redirects=False)
                    print(f"Article direct status: {article_resp.status_code}")
                    
                    if article_resp.status_code == 302:
                        redirect = article_resp.headers.get('Location', '')
                        print(f"Redirect location: {redirect}")
                        
                        if '500.html' in redirect:
                            print("❌ REDIRECTS TO 500 ERROR PAGE")
                            
                            # Maybe we need additional parameters?
                            print("\nTrying with additional parameters...")
                            
                            # Try with menuId parameter
                            link_with_menu = f"{direct_link}&menuId=PCUCTNMG2000"
                            test2 = session.get(link_with_menu, timeout=10, allow_redirects=False)
                            print(f"With menuId status: {test2.status_code}")
                            
                            # Try the main list view instead
                            list_link = f"https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000&prtlBbsId={article_id}"
                            test3 = session.get(list_link, timeout=10, allow_redirects=False)
                            print(f"List view status: {test3.status_code}")
                            
                    elif article_resp.status_code == 200:
                        print("✅ Direct access works!")
                    else:
                        print(f"Status: {article_resp.status_code}")
                        
                except Exception as e:
                    print(f"Error testing article: {e}")
            
            print()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    investigate()
