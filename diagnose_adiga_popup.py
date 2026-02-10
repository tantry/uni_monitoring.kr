#!/usr/bin/env python3
"""
ADIGA CONTENT DIAGNOSTIC
Run this once, show output, then we'll fix based on what we see
"""
import sys
sys.path.insert(0, '/home/bushgrad/uni_monitoring.kr')

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

print("=" * 80)
print("ADIGA POPUP CONTENT DIAGNOSTIC")
print("=" * 80)

# Initialize Selenium
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.binary_location = '/usr/bin/google-chrome-stable'

driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(30)

try:
    # Load Adiga page
    url = "https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000"
    print(f"\n1. Loading: {url}")
    driver.get(url)
    time.sleep(2)
    print("   ✓ Page loaded")
    
    # Find first popup link
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    import re
    links = soup.find_all(attrs={'onclick': re.compile(r'fnDetailPopup')})
    
    if not links:
        print("   ✗ No popup links found")
        driver.quit()
        sys.exit(1)
    
    first_link = links[0]
    onclick = first_link.get('onclick', '')
    match = re.search(r"fnDetailPopup\s*\(\s*['\"]?(\d+)", onclick)
    article_id = match.group(1) if match else None
    title = first_link.get_text(strip=True)
    
    print(f"\n2. Found first article:")
    print(f"   Title: {title[:60]}")
    print(f"   Article ID: {article_id}")
    
    # Click the popup
    print(f"\n3. Clicking popup...")
    clickable = driver.find_element(By.XPATH, f"//a[contains(@onclick, '{article_id}')]")
    driver.execute_script("arguments[0].click();", clickable)
    time.sleep(2)
    print("   ✓ Popup clicked")
    
    # Get popup HTML
    print(f"\n4. Analyzing popup structure...")
    popup_html = driver.page_source
    soup = BeautifulSoup(popup_html, 'html.parser')
    
    # Check for popup container
    popup_div = soup.find('div', id='newsPopCont')
    if popup_div:
        print("   ✓ Found newsPopCont div")
        
        # Show all divs with classes
        print("\n5. DIV elements in popup:")
        for div in popup_div.find_all('div', class_=True):
            classes = ' '.join(div.get('class', []))
            text_preview = div.get_text(strip=True)[:50]
            print(f"   - div.{classes}")
            print(f"     Text: {text_preview}...")
        
        # Get all visible text
        print("\n6. All visible text in popup:")
        all_text = popup_div.get_text(separator='\n', strip=True)
        lines = [l for l in all_text.split('\n') if l.strip()]
        for i, line in enumerate(lines[:20], 1):
            print(f"   {i:2d}. {line}")
        
        if len(lines) > 20:
            print(f"   ... ({len(lines) - 20} more lines)")
        
        # Check for specific content areas
        print("\n7. Content area selectors found:")
        selectors_to_try = [
            'div.ArchiveDtContent',
            'div.popCont',
            'div.scroll',
            'div.modDivision',
            'div.titleWordInfo',
        ]
        
        for selector in selectors_to_try:
            elements = popup_div.select(selector)
            if elements:
                text = elements[0].get_text(strip=True)[:100]
                print(f"   ✓ {selector}: {len(elements)} found")
                print(f"     Text: {text}...")
    else:
        print("   ✗ newsPopCont div not found")
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("Share this output so we can create the proper fix")
    print("=" * 80)
    
finally:
    driver.quit()
