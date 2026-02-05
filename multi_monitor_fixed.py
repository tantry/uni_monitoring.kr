#!/usr/bin/env python3
"""
University Admission Monitor - FIXED VERSION
Multi-source scraper with Telegram alerts
"""

import json
import os
import sys
import time
import hashlib
from datetime import datetime
import requests

# Import project modules
import config
from filters import filter_by_department
from telegram_formatter import format_telegram_message

# Import scrapers - using the simple test version first
sys.path.append('scrapers')
try:
    from simple_adiga_scraper import SimpleAdigaScraper
    print("✅ Using test scraper")
except ImportError:
    # Fallback to actual scraper
    try:
        from adiga_scraper_fixed import AdigaScraper as SimpleAdigaScraper
        print("✅ Using fixed Adiga scraper")
    except ImportError:
        print("❌ No scraper available")
        sys.exit(1)

# State management
STATE_FILE = 'state.json'

def load_state():
    """Load sent articles from state file"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Warning: {STATE_FILE} is corrupt, starting fresh")
    return {'sent_articles': [], 'last_run': None}

def save_state(state):
    """Save state to file"""
    state['last_run'] = datetime.now().isoformat()
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def generate_article_id(article):
    """Generate unique ID for an article"""
    content = f"{article.get('title', '')}{article.get('url', '')}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def send_telegram_alert(title, content, url, department="general"):
    """Send alert to Telegram - FIXED VERSION"""
    try:
        message = format_telegram_message(title, content, url, department)
        
        telegram_url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"
        
        payload = {
            'chat_id': config.CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': False
        }
        
        print(f"📤 Sending Telegram alert: {title[:50]}...")
        print(f"   Department: {department}")
        print(f"   Chat ID: {config.CHAT_ID}")
        
        response = requests.post(telegram_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Telegram alert sent successfully!")
            return True
        else:
            print(f"❌ Telegram error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception sending Telegram alert: {type(e).__name__}: {e}")
        return False

def process_articles(articles, state, source_name):
    """Process and filter articles"""
    new_alerts = 0
    
    for article in articles:
        article_id = generate_article_id(article)
        
        # Check for duplicates
        if article_id in state['sent_articles']:
            print(f"⏭️ Skipping duplicate: {article.get('title', 'No title')[:50]}...")
            continue
        
        # Filter by department
        department = filter_by_department(article)
        if not department:
            print(f"🚫 Filtered out (no department match): {article.get('title', 'No title')[:50]}...")
            continue
        
        print(f"🎯 KEPT article: {article.get('title', 'No title')[:50]}...")
        print(f"   Department: {department}")
        print(f"   URL: {article.get('url', 'No URL')}")
        
        # Send Telegram alert
        success = send_telegram_alert(
            article.get('title', 'No title'),
            article.get('content', ''),
            article.get('url', ''),
            department
        )
        
        if success:
            state['sent_articles'].append(article_id)
            new_alerts += 1
        
        # Small delay between sends to avoid rate limiting
        time.sleep(0.5)
    
    return new_alerts

def main():
    """Main monitoring function"""
    print("=" * 60)
    print("🏫 UNIVERSITY ADMISSION MONITOR - FIXED VERSION")
    print("=" * 60)
    
    # Load state
    state = load_state()
    print(f"📊 Previously sent articles: {len(state.get('sent_articles', []))}")
    
    # Initialize scraper
    try:
        scraper = SimpleAdigaScraper()
        print(f"✅ Scraper initialized: {scraper.source_name}")
    except Exception as e:
        print(f"❌ Failed to initialize scraper: {e}")
        return 0
    
    total_new_alerts = 0
    
    # Process scraper
    print(f"\n🔍 Checking {scraper.source_name}...")
    
    try:
        articles = scraper.fetch_articles()
        print(f"   Found {len(articles)} articles")
        
        if articles:
            new_alerts = process_articles(articles, state, scraper.source_name)
            total_new_alerts += new_alerts
            print(f"   Sent {new_alerts} new alerts from {scraper.source_name}")
        else:
            print(f"   No articles found from {scraper.source_name}")
            
    except Exception as e:
        print(f"❌ Error with {scraper.source_name}: {type(e).__name__}: {e}")
    
    # Save state
    save_state(state)
    
    print("\n" + "=" * 60)
    print(f"📈 MONITORING COMPLETE")
    print(f"   Total new alerts sent: {total_new_alerts}")
    print(f"   Total articles tracked: {len(state.get('sent_articles', []))}")
    print(f"   State saved to: {STATE_FILE}")
    print("=" * 60)
    
    return total_new_alerts

if __name__ == "__main__":
    main()
