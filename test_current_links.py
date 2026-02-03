import requests
from bs4 import BeautifulSoup

print("Testing Adiga link structure on YOUR system...\n")

url = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
headers = {'X-Requested-With': 'XMLHttpRequest'}
data = {'menuId': 'PCUCTNMG2000', 'currentPage': '1', 'cntPerPage': '3'}

try:
    response = requests.post(url, headers=headers, data=data)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = soup.find_all(class_='uctCastTitle')
    print(f"Found {len(articles)} articles\n")
    
    for i, title_tag in enumerate(articles[:2]):
        title = title_tag.get_text(strip=True)[:50]
        print(f"Article {i+1}: {title}...")
        
        # Check current link extraction
        link = "https://www.adiga.kr"  # Default
        link_tag = title_tag.find_parent('a')
        if link_tag and link_tag.has_attr('href'):
            link = link_tag['href']
            if link.startswith('/'):
                link = f'https://www.adiga.kr{link}'
        
        print(f"  Current link: {link}")
        
        # Check parent for onclick
        parent = title_tag.parent
        if parent and 'onclick' in parent.attrs:
            print(f"  Found onclick: {parent['onclick'][:80]}...")
        else:
            print(f"  No onclick found in parent")
        
        print()
        
except Exception as e:
    print(f"Error: {e}")
