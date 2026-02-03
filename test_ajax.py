import requests
from bs4 import BeautifulSoup

url = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
headers = {
    'User-Agent': 'Mozilla/5.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000'
}
data = {
    'menuId': 'PCUCTNMG2000',
    'currentPage': '1',
    'cntPerPage': '10',
    'searchKeywordType': 'title',
    'searchKeyword': ''
}

print("Testing AJAX endpoint...")
response = requests.post(url, headers=headers, data=data)
print(f"Status: {response.status_code}")
print(f"Response size: {len(response.text)} chars")

# Save to check
with open('ajax_test.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

soup = BeautifulSoup(response.text, 'html.parser')

# Look for titles
titles = soup.find_all(class_='uctCastTitle')
print(f"\nFound {len(titles)} titles:")
for i, title in enumerate(titles[:5]):
    print(f"  {i+1}. {title.get_text(strip=True)[:60]}...")

# Look for container
container = soup.find(id='tbResult')
if container:
    print(f"\nContainer found: #{container.get('id')}")
    print(f"Container HTML tag: {container.name}")
    print(f"Container classes: {container.get('class')}")

print("\nSaved AJAX response to 'ajax_test.html'")
