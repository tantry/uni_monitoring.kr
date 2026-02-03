import requests
from bs4 import BeautifulSoup

url = "https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000"
headers = {'User-Agent': 'Mozilla/5.0'}

print("Testing Adiga page access...")
response = requests.get(url, headers=headers)
print(f"Status code: {response.status_code}")
print(f"Page size: {len(response.text)} characters")

# Save a sample to see what we're getting
with open('page_sample.html', 'w', encoding='utf-8') as f:
    f.write(response.text[:5000])  # First 5000 chars

print("\nLooking for containers...")
soup = BeautifulSoup(response.content, 'html.parser')

# Try different container searches
print("1. Looking for 'classList02':")
containers = soup.find_all(class_='classList02')
print(f"   Found {len(containers)} elements with class 'classList02'")

print("\n2. Looking for any <ul> elements:")
ul_elements = soup.find_all('ul')
print(f"   Found {len(ul_elements)} <ul> elements")
for i, ul in enumerate(ul_elements[:5]):
    print(f"   UL #{i+1}: classes = {ul.get('class', 'No class')}")

print("\n3. Looking for 'uctCastTitle' (article titles):")
titles = soup.find_all(class_='uctCastTitle')
print(f"   Found {len(titles)} titles")
for i, title in enumerate(titles[:3]):
    print(f"   Title #{i+1}: {title.get_text(strip=True)[:50]}...")

print("\nSample saved to 'page_sample.html'")
