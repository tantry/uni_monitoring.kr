#!/usr/bin/env python3
"""
Test what the actual page content looks like
"""
import requests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Actual Page Content")
print("=" * 50)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000'
})

# Establish session
session.get('https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000', timeout=10)

# Test article URL
test_url = "https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBbsId=26546"

print(f"Fetching: {test_url}")
response = session.get(test_url, timeout=10, allow_redirects=True)

print(f"Status: {response.status_code}")
print(f"URL: {response.url}")
print(f"Content length: {len(response.text)} chars")

# Save to file for examination
with open('test_page_output.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print("\nAnalyzing page content...")
print("-" * 50)

from bs4 import BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Remove scripts and styles
for script in soup(["script", "style"]):
    script.decompose()

# Get text and split into lines
text = soup.get_text()
lines = [line.strip() for line in text.split('\n') if line.strip()]

print("First 20 lines of page text:")
for i, line in enumerate(lines[:20], 1):
    print(f"{i:2}. {line}")

print("\nLooking for common elements...")
print("-" * 50)

# Check for specific elements
checks = {
    'Title tags': len(soup.find_all(['h1', 'h2', 'h3'])),
    'Paragraphs': len(soup.find_all('p')),
    'Divs with content': len([d for d in soup.find_all('div') if len(d.get_text(strip=True)) > 100]),
    'Tables': len(soup.find_all('table')),
    'Iframes': len(soup.find_all('iframe')),
}

for item, count in checks.items():
    print(f"{item}: {count}")

# Look for the text you mentioned
if "공통" in response.text:
    print("\nFound '공통' in page")
if "입시용어 따라잡기" in response.text:
    print("Found '입시용어 따라잡기' in page")

print("\n" + "=" * 50)
print(f"Page saved to: test_page_output.html")
print("Check this file to see full page structure")
