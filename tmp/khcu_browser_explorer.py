#!/usr/bin/env python3
"""
KHCU Site Browser Explorer using Selenium
This script opens the KHCU site in a browser and analyzes its structure
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def explore_khcu():
    """Explore KHCU site structure using Selenium"""
    
    print("🔍 KHCU Site Browser Exploration")
    print("=" * 60)
    print("")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
    
    driver = None
    try:
        print("1️⃣  Starting Chrome browser...")
        driver = webdriver.Chrome(options=chrome_options)
        
        url = "https://khcu.ac.kr/schedule/index.do"
        print(f"   Loading: {url}")
        driver.get(url)
        
        print("   ✓ Page loaded, waiting for content to render...")
        time.sleep(3)  # Give JavaScript time to load
        
        # Get page info
        page_title = driver.title
        page_url = driver.current_url
        print(f"   Page title: {page_title}")
        print(f"   Current URL: {page_url}")
        print("")
        
        print("2️⃣  Analyzing page structure...")
        print("────────────────────────────────────")
        
        # Get all text content
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"   Total text content: {len(body_text)} characters")
        print("")
        
        # Look for table elements
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"   Found {len(tables)} <table> elements")
        if tables:
            print(f"   First table has {len(tables[0].find_elements(By.TAG_NAME, 'tr'))} rows")
        print("")
        
        # Look for divs with potential content classes
        print("3️⃣  Looking for announcement/schedule containers...")
        print("────────────────────────────────────────────────")
        
        potential_classes = [
            'notice', 'article', 'announcement', 'schedule', 'event', 
            'list', 'item', 'row', 'content', 'main', 'board'
        ]
        
        for class_name in potential_classes:
            elements = driver.find_elements(By.XPATH, f"//*[contains(@class, '{class_name}')]")
            if elements:
                print(f"   Found {len(elements)} elements with class containing '{class_name}'")
        print("")
        
        print("4️⃣  Looking for clickable elements (links)...")
        print("────────────────────────────────────────────")
        
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"   Total links found: {len(links)}")
        
        # Sample first 10 links
        print("   Sample links:")
        for i, link in enumerate(links[:10], 1):
            href = link.get_attribute("href")
            text = link.text[:50] if link.text else "(no text)"
            print(f"      {i}. {text}")
            print(f"         href: {href}")
        print("")
        
        print("5️⃣  Looking for date/schedule information...")
        print("────────────────────────────────────────────")
        
        # Check first 2000 chars of body text
        sample_text = body_text[:2000]
        print("   First 2000 chars of page:")
        print("   " + "-" * 56)
        for line in sample_text.split('\n')[:30]:
            if line.strip():
                print(f"   {line.strip()[:60]}")
        print("   " + "-" * 56)
        print("")
        
        print("6️⃣  HTML Structure Analysis...")
        print("────────────────────────────────")
        
        # Get page source
        page_source = driver.page_source
        
        # Count elements
        div_count = len(driver.find_elements(By.TAG_NAME, "div"))
        span_count = len(driver.find_elements(By.TAG_NAME, "span"))
        p_count = len(driver.find_elements(By.TAG_NAME, "p"))
        
        print(f"   <div> elements: {div_count}")
        print(f"   <span> elements: {span_count}")
        print(f"   <p> elements: {p_count}")
        print("")
        
        # Save full page source
        with open("khcu_rendered.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("7️⃣  Full rendered HTML saved to khcu_rendered.html")
        print("")
        
        print("=" * 60)
        print("✅ Exploration complete!")
        print("")
        print("📋 Next steps:")
        print("   1. Open khcu_rendered.html in your text editor")
        print("   2. Look for:")
        print("      - How announcements are structured")
        print("      - What classes/IDs contain the content")
        print("      - How to identify admission-related items")
        print("      - The pattern for extracting links and titles")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    explore_khcu()
