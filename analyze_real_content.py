#!/usr/bin/env python3
"""
Analyze where the real article content actually is
"""
import requests
from bs4 import BeautifulSoup
import re

url = "https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBbsId=26546"

print("Analyzing actual article page structure...")
print("=" * 60)

# Fetch with proper headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.adiga.kr/',
}

response = requests.get(url, headers=headers, timeout=10)
print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)} chars")

if response.status_code != 200:
    print("❌ Failed to fetch page")
    exit()

soup = BeautifulSoup(response.text, 'html.parser')

# 1. Check for popup structure
print(f"\n1. Looking for popup structure...")
popup = soup.find('div', id='newsPopCont')
if popup:
    print(f"✅ Found newsPopCont div")
    
    # Look for all divs inside
    all_divs = popup.find_all('div')
    print(f"   Contains {len(all_divs)} div elements")
    
    for div in all_divs:
        div_class = div.get('class', [])
        if div_class:
            print(f"   Div class: {div_class}")
    
    # Look for iframes or external content
    iframes = popup.find_all('iframe')
    print(f"   Contains {len(iframes)} iframes")
    
    # Look for JavaScript that loads content
    scripts = popup.find_all('script')
    print(f"   Contains {len(scripts)} script tags")
    
    # Get all text
    all_text = popup.get_text(separator='\n', strip=True)
    lines = [line for line in all_text.split('\n') if line.strip()]
    print(f"   Text has {len(lines)} non-empty lines")
    
    print(f"\n   First 10 lines of text:")
    for i, line in enumerate(lines[:10]):
        print(f"   {i+1}: {line}")
else:
    print("❌ No newsPopCont found")

# 2. Look for actual article content patterns
print(f"\n2. Searching for article content patterns...")

# Look for common content containers
content_selectors = [
    'div.content', 'div.article', 'div.article-content',
    'div.post-content', 'div.entry-content', 'div.story-content',
    '#content', '#article', '#articleBody'
]

for selector in content_selectors:
    elements = soup.select(selector)
    if elements:
        print(f"✅ Found {len(elements)} elements with {selector}")
        for elem in elements[:2]:
            text = elem.get_text(strip=True)[:100]
            print(f"   Preview: {text}...")

# 3. Look for meta tags with description
print(f"\n3. Checking meta tags...")
meta_desc = soup.find('meta', attrs={'name': 'description'})
if meta_desc and meta_desc.get('content'):
    desc = meta_desc['content']
    print(f"✅ Meta description: {desc[:150]}...")
else:
    print("❌ No meta description")

# 4. Look for Open Graph tags (often used by news sites)
print(f"\n4. Checking Open Graph tags...")
og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
for tag in og_tags[:5]:
    prop = tag.get('property', '')
    content = tag.get('content', '')
    if content:
        print(f"   {prop}: {content[:100]}...")

# 5. Look for JSON-LD or structured data
print(f"\n5. Checking for structured data...")
json_ld = soup.find_all('script', type='application/ld+json')
if json_ld:
    print(f"✅ Found {len(json_ld)} JSON-LD scripts")
    # Try to parse first one
    import json
    try:
        data = json.loads(json_ld[0].string)
        print(f"   JSON-LD type: {data.get('@type', 'unknown')}")
        if 'articleBody' in data:
            print(f"   Has articleBody: {data['articleBody'][:100]}...")
    except:
        print("   Could not parse JSON-LD")

# 6. Check for AJAX endpoints in scripts
print(f"\n6. Looking for AJAX/API endpoints...")
all_scripts = soup.find_all('script')
ajax_patterns = [
    r'ajax.*?url.*?["\']([^"\']+)["\']',
    r'fetch.*?["\']([^"\']+\.(?:do|json|ajax))["\']',
    r'\.get.*?["\']([^"\']+\.(?:do|json|ajax))["\']',
    r'\.post.*?["\']([^"\']+\.(?:do|json|ajax))["\']'
]

for script in all_scripts:
    if script.string:
        content = script.string
        for pattern in ajax_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                for match in matches[:3]:
                    print(f"   Potential endpoint: {match}")

print(f"\n" + "=" * 60)
print("Analysis complete. Key findings:")
print("1. The hidden field (lnaCn1) only contains the snippet, not full article")
print("2. Need to investigate JavaScript loading or different endpoint")
print("3. May need to use the snippet as fallback content")
