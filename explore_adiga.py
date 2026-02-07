#!/usr/bin/env python3
"""
Manual exploration of Adiga.kr structure
"""
import requests
from bs4 import BeautifulSoup
import re

def explore_adiga():
    print("=== Manual Adiga.kr Exploration ===")
    
    base_url = "https://www.adiga.kr"
    desktop_url = f"{base_url}/man/inf/mainView.do?menuId=PCMANINF1000"
    
    # Create session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    # Get main page
    print(f"\n1. Fetching main desktop page: {desktop_url}")
    response = session.get(desktop_url)
    print(f"   Status: {response.status_code}, Size: {len(response.content)} bytes")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all links
    all_links = soup.find_all('a')
    print(f"\n2. Total links found: {len(all_links)}")
    
    # Categorize links
    categories = {
        'menu_id_links': [],
        'article_links': [],
        'admission_links': [],
        'other_links': []
    }
    
    admission_keywords = ['입학', '모집', '공고', '전형', '원서', '모집요강']
    
    for link in all_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if not href:
            continue
        
        # Categorize
        if 'menuId=' in href:
            categories['menu_id_links'].append((text, href))
        elif 'Article' in href:
            categories['article_links'].append((text, href))
        elif any(keyword in text for keyword in admission_keywords):
            categories['admission_links'].append((text, href))
        elif text and len(text) > 3:
            categories['other_links'].append((text, href))
    
    # Print categories
    print("\n3. Link Categories:")
    print(f"   - Menu ID links: {len(categories['menu_id_links'])}")
    print(f"   - Article links: {len(categories['article_links'])}")
    print(f"   - Admission links: {len(categories['admission_links'])}")
    print(f"   - Other links: {len(categories['other_links'])}")
    
    # Show admission links
    if categories['admission_links']:
        print("\n4. Admission-related links found:")
        for text, href in categories['admission_links'][:10]:
            print(f"   - {text[:50]}... -> {href[:80]}")
    
    # Show menu ID links
    print("\n5. Menu ID links (first 20):")
    for i, (text, href) in enumerate(categories['menu_id_links'][:20]):
        print(f"   {i+1:2d}. {text[:40]:40} -> {href[:60]}")
    
    # Try to find announcement/notice sections
    print("\n6. Searching for announcement sections...")
    
    # Look for common announcement patterns
    announcement_patterns = [
        '공지사항', '새소식', '입학소식', '모집공고', 
        '학사공지', '대학소식', '입학안내', '공지'
    ]
    
    for pattern in announcement_patterns:
        elements = soup.find_all(string=re.compile(pattern, re.I))
        if elements:
            print(f"   Found '{pattern}' in {len(elements)} places")
            for elem in elements[:3]:
                parent = elem.parent
                print(f"     - Parent: {parent.name}, Text: {elem[:50]}...")
    
    # Look for board/list structures
    print("\n7. Looking for board/list structures...")
    
    board_classes = ['board', 'list', 'news', 'notice', 'bbs', 'article']
    for cls in board_classes:
        elements = soup.find_all(class_=re.compile(cls, re.I))
        if elements:
            print(f"   Found {len(elements)} elements with class containing '{cls}'")
    
    # Save the HTML for manual inspection
    with open('adiga_exploration.html', 'w', encoding='utf-8') as f:
        f.write(response.text[:10000])
    
    print(f"\n8. Saved exploration to 'adiga_exploration.html'")
    
    # Test some promising menu IDs
    print("\n9. Testing promising menu IDs...")
    
    promising_menus = [
        ('PCMANINF2000', '공지사항'),
        ('PCMANINF3000', '새소식'),
        ('PCUVTINF2000', '대학정보'),
        ('PCCLSINF2000', '학과정보'),
    ]
    
    for menu_id, description in promising_menus:
        test_url = f"{base_url}/man/inf/mainView.do?menuId={menu_id}"
        try:
            test_resp = session.get(test_url, timeout=10)
            print(f"   {menu_id} ({description}): {test_resp.status_code}, {len(test_resp.content)} bytes")
            
            # Check for admission content
            test_soup = BeautifulSoup(test_resp.content, 'html.parser')
            admission_count = len(test_soup.find_all(string=re.compile('|'.join(admission_keywords), re.I)))
            if admission_count > 0:
                print(f"     Found {admission_count} admission-related terms")
                
        except Exception as e:
            print(f"   {menu_id}: Error - {e}")
    
    return categories

if __name__ == "__main__":
    explore_adiga()
