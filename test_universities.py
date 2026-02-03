import requests
from bs4 import BeautifulSoup

# Get current articles
url = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
headers = {
    'User-Agent': 'Mozilla/5.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000'
}
data = {
    'menuId': 'PCUCTNMG2000',
    'currentPage': '1',
    'cntPerPage': '20',
    'searchKeywordType': 'title',
    'searchKeyword': '',
}

response = requests.post(url, headers=headers, data=data)
soup = BeautifulSoup(response.content, 'html.parser')
articles = soup.find_all(class_='uctCastTitle')

print("Checking for university mentions in current articles:\n")

# List of national universities to check for
universities = [
    "서울대", "경북대", "전남대", "충남대", "강원대",
    "경상국립대", "경상대", "전북대", "제주대", "충북대",
    "부산대", "인천대", "공주대", "국립대", "공립대"
]

for article in articles:
    title = article.get_text(strip=True)
    found_unis = []
    
    for uni in universities:
        if uni in title:
            found_unis.append(uni)
    
    if found_unis:
        print(f"✓ {title[:60]}...")
        print(f"  Contains: {', '.join(found_unis)}")
    else:
        # Check if it's admission-related
        if any(kw in title for kw in ["추가모집", "미충원", "모집", "입학"]):
            print(f"📝 {title[:60]}...")
            print(f"  (Admission-related but no university named)")

print(f"\nTotal articles: {len(articles)}")
