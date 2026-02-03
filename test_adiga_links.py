import requests
from bs4 import BeautifulSoup
import re

AJAX_URL = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
REFERER_URL = "https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000"

headers = {
    'User-Agent': 'Mozilla/5.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': REFERER_URL
}

form_data = {
    'menuId': 'PCUCTNMG2000',
    'currentPage': '1',
    'cntPerPage': '5',
}

print("Testing Adiga article structure...\n")
response = requests.post(AJAX_URL, headers=headers, data=form_data)
soup = BeautifulSoup(response.content, 'html.parser')
articles = soup.find_all(class_='uctCastTitle')

for i, title_tag in enumerate(articles[:3]):
    title = title_tag.get_text(strip=True)
    print(f"=== Article {i+1}: {title[:50]}... ===")
    
    # Check for onclick in parent chain
    element = title_tag
    found_onclick = False
    for level in range(5):
        if element is None:
            break
        onclick = element.get('onclick', '')
        if onclick and 'fnDetailPopup' in onclick:
            print(f"  Level {level}: Found onclick!")
            print(f"  onclick: {onclick}")
            match = re.search(r"fnDetailPopup\('([^']+)'\)", onclick)
            if match:
                article_id = match.group(1)
                print(f"  ✅ Article ID: {article_id}")
                direct_link = f"https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBbsId={article_id}"
                print(f"  🔗 Direct link: {direct_link}")
            found_onclick = True
            break
        element = element.parent
    
    if not found_onclick:
        print("  ❌ No onclick found in parent chain")
        
        # Check for href
        link_tag = title_tag.find_parent('a')
        if link_tag and link_tag.has_attr('href'):
            href = link_tag['href']
            print(f"  Found href: {href}")
        else:
            print("  No href found either")
    
    print()
