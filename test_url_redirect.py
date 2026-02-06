#!/usr/bin/env python3
"""
Test if the URL actually works with redirect following
"""
import requests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing URL with redirect following...")
print("=" * 50)

# Create session like the scraper does
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000'
})

# First establish session
print("1. Establishing session...")
main_response = session.get('https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000', timeout=10)
print(f"   Main page: {main_response.status_code}")
print(f"   Cookies: {len(session.cookies)}")

# Test the article URL with redirect following
test_url = "https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBbsId=26546"

print(f"\n2. Testing URL: {test_url}")
print("   Without redirects (HEAD request):")
head_response = session.head(test_url, timeout=5, allow_redirects=False)
print(f"   Status: {head_response.status_code}")
if head_response.status_code == 302:
    print(f"   Redirect location: {head_response.headers.get('Location', 'None')}")

print("\n3. Testing with redirects (GET request):")
get_response = session.get(test_url, timeout=10, allow_redirects=True)
print(f"   Final status: {get_response.status_code}")
print(f"   Final URL: {get_response.url}")
print(f"   Content length: {len(get_response.text)} chars")

if get_response.status_code == 200:
    print("\n✅ URL WORKS when following redirects!")
    # Check if it's the article page
    if "정시 등록" in get_response.text:
        print("✅ Correct article content found!")
    else:
        print("⚠ Content check inconclusive")
else:
    print(f"\n❌ URL failed with status: {get_response.status_code}")

print("\n" + "=" * 50)
print("Test complete - Telegram links should work!")
