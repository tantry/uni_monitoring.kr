#!/usr/bin/env python3
"""
Analyze the exact structure of adiga_structure.html
"""
from bs4 import BeautifulSoup

print("🔍 ANALYZING HTML STRUCTURE")
print("=" * 60)

try:
    with open('adiga_structure.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    print("1. Total HTML length:", len(html))
    print("2. Looking for article containers...")
    
    # Try different selectors
    selectors = [
        'ul.uctList02 li',
        '.uctList02 li',
        'li',  # All li elements
        'a[onclick]',  # All anchors with onclick
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        print(f"   '{selector}': {len(elements)} found")
        
        if elements and selector == 'a[onclick]':
            print(f"   First onclick: {elements[0].get('onclick', 'none')[:50]}...")
            print(f"   First title: {elements[0].get_text(strip=True)[:50]}...")
    
    # Look specifically for the structure
    print("\n3. Examining specific structure...")
    
    # Find the ul with class uctList02
    ul_elements = soup.find_all('ul', class_='uctList02')
    print(f"   ul.uctList02 elements: {len(ul_elements)}")
    
    if ul_elements:
        ul = ul_elements[0]
        li_elements = ul.find_all('li')
        print(f"   li elements inside: {len(li_elements)}")
        
        if li_elements:
            first_li = li_elements[0]
            print(f"   First li HTML preview: {str(first_li)[:200]}...")
            
            # Find anchor
            anchor = first_li.find('a')
            if anchor:
                print(f"   Anchor onclick: {anchor.get('onclick', 'none')}")
                print(f"   Anchor text: {anchor.get_text(strip=True)[:50]}...")
    
    print("\n4. Debug: Show first 500 chars of HTML...")
    print(html[:500])
    
except FileNotFoundError:
    print("❌ adiga_structure.html not found!")
    print("Current directory:", __file__)
    import os
    print("Files in current directory:")
    for f in os.listdir('.'):
        if '.html' in f or '.py' in f:
            print(f"  - {f}")

print("\n" + "=" * 60)
print("🎯 ANALYSIS COMPLETE")
