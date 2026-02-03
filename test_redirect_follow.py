#!/usr/bin/env python3
"""
Test where the 302 redirects actually go
"""
import requests
from bs4 import BeautifulSoup
import re

def test_article_access():
    print("🔍 Testing article access with redirect following...\n")
    
    AJAX_URL = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000'
    }
    
    form_data = {'menuId': 'PCUCTNMG2000', 'currentPage': '1', 'cntPerPage': '3'}
    
    try:
        response = requests.post(AJAX_URL, headers=headers, data=form_data, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        title_tags = soup.find_all(class_='uctCastTitle')
        
        for i, title_tag in enumerate(title_tags[:2]):  # Test first 2
            title = title_tag.get_text(strip=True)
            
            # Extract article ID
            element = title_tag
            article_id = None
            for _ in range(5):
                if element is None:
                    break
                onclick = element.get('onclick', '')
                if onclick and 'fnDetailPopup' in onclick:
                    match = re.search(r'fnDetailPopup\("([^"]+)"\)', onclick)
                    if match:
                        article_id = match.group(1)
                        break
                element = element.parent
            
            if article_id:
                link = f"https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBbsId={article_id}"
                print(f"=== Testing: {title[:50]}... ===")
                print(f"Link: {link}")
                
                # Try with redirect following
                try:
                    # First, try without following redirects
                    session = requests.Session()
                    initial_response = session.head(link, allow_redirects=False, timeout=5)
                    print(f"Initial status: {initial_response.status_code}")
                    
                    if initial_response.status_code == 302:
                        redirect_url = initial_response.headers.get('Location', 'No redirect URL')
                        print(f"Redirects to: {redirect_url}")
                        
                        # Try to follow the redirect
                        try:
                            final_response = session.get(link, timeout=10)
                            print(f"Final status after redirect: {final_response.status_code}")
                            
                            if final_response.status_code == 200:
                                # Check if we got actual content
                                final_soup = BeautifulSoup(final_response.content, 'html.parser')
                                
                                # Look for article content
                                content_div = final_soup.find(class_='boardView')
                                if content_div:
                                    print("✅ Found article content!")
                                    # Get first 200 chars of content
                                    text = content_div.get_text(strip=True)[:200]
                                    print(f"Content preview: {text}...")
                                else:
                                    # Maybe check for other content structures
                                    body_text = final_soup.find('body').get_text(strip=True)[:200]
                                    print(f"Page body preview: {body_text}...")
                                    
                        except Exception as e:
                            print(f"Error following redirect: {e}")
                    
                    elif initial_response.status_code == 200:
                        print("✅ Direct access works!")
                    else:
                        print(f"⚠️  Status: {initial_response.status_code}")
                        
                except Exception as e:
                    print(f"Error accessing link: {e}")
                
                print()
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_article_access()
