#!/usr/bin/env python3
"""
Test what articles Adiga currently has and what links we generate
"""
import requests
from bs4 import BeautifulSoup
import re

AJAX_URL = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
REFERER_URL = "https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000"

def test_articles():
    print("📰 Current Adiga articles and their links:\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': REFERER_URL
    }
    
    form_data = {
        'menuId': 'PCUCTNMG2000',
        'currentPage': '1',
        'cntPerPage': '10',
    }
    
    try:
        response = requests.post(AJAX_URL, headers=headers, data=form_data, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all(class_='uctCastTitle')
        
        print(f"Found {len(articles)} articles\n")
        
        for i, title_tag in enumerate(articles[:8]):  # Show first 8
            title = title_tag.get_text(strip=True)
            
            # Extract link the way our system does
            element = title_tag
            link = REFERER_URL  # Default fallback
            
            for _ in range(5):
                if element is None:
                    break
                onclick = element.get('onclick', '')
                if onclick and 'fnDetailPopup' in onclick:
                    match = re.search(r'fnDetailPopup\("([^"]+)"\)', onclick)
                    if match:
                        article_id = match.group(1)
                        link = f"https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBbsId={article_id}"
                        break
                element = element.parent
            
            # Check what keywords it has
            keywords = []
            if '추가모집' in title or '미충원' in title or '모집' in title or '입학' in title:
                keywords.append("입시")
            if '영어' in title or '음악' in title:
                keywords.append("전공")
            if any(uni in title for uni in ["홍익대", "한양대", "강원대", "경상국립대"]):
                keywords.append("관심대학")
            
            keyword_str = f" [Keywords: {', '.join(keywords)}]" if keywords else ""
            
            print(f"{i+1}. {title[:60]}...")
            print(f"   🔗 {link}")
            if 'newsDetail.do' in link:
                article_id = link.split('=')[-1]
                print(f"   📄 Direct article (ID: {article_id})")
            else:
                print(f"   📋 Fallback to list page")
            print(f"   🏷️ {keyword_str}" if keyword_str else "")
            print()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_articles()
