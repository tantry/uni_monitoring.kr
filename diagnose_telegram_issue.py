#!/usr/bin/env python3
"""
Diagnose Telegram integration issues after project refactoring
"""

import sys
import os
import json
import hashlib
from datetime import datetime

# Add current directory to path to import modules
sys.path.append('.')

print("🔍 DIAGNOSING TELEGRAM INTEGRATION ISSUE")
print("=" * 50)

# 1. Check if config exists and is valid
print("\n1. Checking config.py...")
try:
    import config
    print(f"   ✅ config.py found")
    print(f"   Bot token: {config.BOT_TOKEN[:10]}...")
    print(f"   Chat ID: {config.CHAT_ID}")
except ImportError:
    print("   ❌ config.py not found or can't be imported")
    sys.exit(1)
except AttributeError as e:
    print(f"   ❌ Missing attribute in config.py: {e}")
    sys.exit(1)

# 2. Check telegram_formatter module
print("\n2. Checking telegram_formatter.py...")
try:
    from telegram_formatter import format_telegram_message
    print("   ✅ telegram_formatter imported successfully")
    
    # Test formatting
    test_msg = format_telegram_message(
        "Test Title", 
        "Test content for diagnostics", 
        "https://example.com",
        "music"
    )
    print(f"   ✅ Message formatted ({len(test_msg)} chars)")
    print(f"   Preview: {test_msg[:80]}...")
except ImportError as e:
    print(f"   ❌ Cannot import telegram_formatter: {e}")
except Exception as e:
    print(f"   ❌ Error in telegram_formatter: {type(e).__name__}: {e}")

# 3. Check if send_telegram_alert function exists
print("\n3. Checking multi_monitor.py structure...")
try:
    with open('multi_monitor.py', 'r') as f:
        content = f.read()
        
    if 'def send_telegram_alert' in content:
        print("   ✅ send_telegram_alert function found")
    else:
        print("   ❌ send_telegram_alert function NOT FOUND")
        
    if 'import requests' in content:
        print("   ✅ requests module imported")
    else:
        print("   ❌ requests module not imported")
        
    # Check for common issues in the function
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'sendMessage' in line:
            print(f"   📍 Line {i+1}: {line.strip()}")
            
except FileNotFoundError:
    print("   ❌ multi_monitor.py not found")

# 4. Check scraper integration
print("\n4. Checking scraper integration...")
try:
    from scrapers.adiga_scraper import AdigaScraper
    print("   ✅ AdigaScraper imported")
    
    scraper = AdigaScraper()
    print(f"   ✅ Scraper initialized: {scraper.source_name}")
except ImportError as e:
    print(f"   ❌ Scraper import failed: {e}")
except Exception as e:
    print(f"   ❌ Error initializing scraper: {type(e).__name__}: {e}")

# 5. Check state file
print("\n5. Checking state management...")
state_file = 'state.json'
if os.path.exists(state_file):
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
        print(f"   ✅ state.json exists with {len(state.get('sent_articles', []))} sent articles")
    except Exception as e:
        print(f"   ❌ Error reading state.json: {e}")
else:
    print("   ℹ️ state.json does not exist (this is normal for first run)")

# 6. Test actual Telegram sending
print("\n6. Testing actual Telegram API call...")
try:
    import requests
    
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getMe"
    response = requests.get(url, timeout=5)
    
    if response.status_code == 200:
        bot_info = response.json()
        print(f"   ✅ Bot connection successful")
        print(f"   🤖 Bot: @{bot_info['result']['username']} ({bot_info['result']['first_name']})")
    else:
        print(f"   ❌ Bot connection failed: {response.status_code}")
        print(f"   Error: {response.text}")
        
except Exception as e:
    print(f"   ❌ Telegram API test failed: {type(e).__name__}: {e}")

print("\n" + "=" * 50)
print("🎯 DIAGNOSIS COMPLETE")
print("\nNext steps:")
print("1. Run: python3 diagnose_telegram_issue.py")
print("2. Check the output above for '❌' errors")
print("3. Run the monitor with debug: python3 multi_monitor.py --debug")
