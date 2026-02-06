#!/usr/bin/env python3
"""
Analyze the current adiga_structure.html to understand its format
"""
from bs4 import BeautifulSoup
import re

print("Analyzing adiga_structure.html...")
print("=" * 60)

with open('adiga_structure.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# 1. Check file size
print(f"File size: {len(html_content)} characters")

# 2. Look for any table structures
tables = soup.find_all('table')
print(f"\nFound {len(tables)} table elements")

for i, table in enumerate(tables[:3]):  # Show first 3 tables
    print(f"\nTable {i+1}:")
    rows = table.find_all('tr')
    print(f"  Rows: {len(rows)}")
    
    # Check for onclick in rows
    onclick_rows = table.find_all('tr', onclick=True)
    print(f"  Rows with onclick: {len(onclick_rows)}")
    
    if onclick_rows:
        for j, row in enumerate(onclick_rows[:2]):  # Show first 2
            onclick = row.get('onclick', '')
            print(f"    Row {j+1} onclick: {onclick[:50]}...")

# 3. Look for any clickable elements
print(f"\nLooking for clickable elements...")
clickable_elements = soup.find_all(onclick=True)
print(f"Total elements with onclick: {len(clickable_elements)}")

for i, elem in enumerate(clickable_elements[:5]):  # Show first 5
    elem_name = elem.name
    elem_class = elem.get('class', [''])[0] if elem.get('class') else ''
    onclick = elem.get('onclick', '')
    print(f"\nElement {i+1}: {elem_name} (class: {elem_class})")
    print(f"  onclick: {onclick[:80]}...")

# 4. Look for article content or lists
print(f"\nLooking for list containers...")
lists = soup.find_all(['ul', 'ol'])
print(f"List elements (ul/ol): {len(lists)}")

# 5. Look for divs that might contain articles
article_divs = soup.find_all('div', class_=re.compile(r'article|content|list|item|news', re.I))
print(f"\nDivs with article/content/list/news in class: {len(article_divs)}")

for i, div in enumerate(article_divs[:3]):  # Show first 3
    div_class = div.get('class', [''])[0] if div.get('class') else ''
    print(f"\nDiv {i+1}: class={div_class}")
    # Look for links inside
    links = div.find_all('a')
    print(f"  Links inside: {len(links)}")
    for link in links[:2]:  # Show first 2 links
        href = link.get('href', '')
        text = link.get_text(strip=True)[:50]
        print(f"    - '{text}...' -> {href[:50]}...")

# 6. Check for JavaScript data
print(f"\nLooking for JavaScript data...")
script_tags = soup.find_all('script')
print(f"Script tags: {len(script_tags)}")

for i, script in enumerate(script_tags[:3]):  # Check first 3 scripts
    script_content = script.string
    if script_content and 'goDetail' in script_content:
        print(f"\nScript {i+1} contains 'goDetail':")
        lines = script_content.split('\n')
        for line in lines:
            if 'goDetail' in line:
                print(f"  {line.strip()[:100]}...")

# 7. Look for article IDs in any form
print(f"\nSearching for article IDs...")
all_text = soup.get_text()
article_id_matches = re.findall(r'\d{4,}', all_text)  # Look for 4+ digit numbers
print(f"Potential article IDs found: {len(article_id_matches)}")
if article_id_matches:
    print(f"Sample IDs: {article_id_matches[:10]}")

print("\n" + "=" * 60)
print("Analysis complete!")
