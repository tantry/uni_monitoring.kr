#!/usr/bin/env python3
"""
Final test script for University Monitor
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

print("=" * 60)
print("FINAL TEST - University Admission Monitor")
print("=" * 60)

# Test 1: Imports
print("\n1. Testing imports...")
try:
    from scrapers.adiga_final import AdigaFinalScraper, test_final_scraper
    from models.article import Article
    from notifiers.telegram_notifier import TelegramNotifier
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test 2: Config
print("\n2. Checking configuration...")
config_files = ['config/config.yaml', 'config/sources.yaml', 'config/filters.yaml']
all_good = True

for file in config_files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} missing")
        all_good = False

if not all_good:
    print("\n⚠ Some config files missing. Creating defaults...")
    
    # Create minimal config if missing
    if not os.path.exists('config/config.yaml'):
        os.makedirs('config', exist_ok=True)
        with open('config/config.yaml', 'w') as f:
            f.write("""telegram:
  bot_token: "YOUR_BOT_TOKEN_HERE"
  chat_id: "YOUR_CHAT_ID_HERE"
database:
  path: "data/state.db"
logging:
  level: "INFO"
  file: "logs/monitor.log"
""")
        print("   Created config/config.yaml")
    
    if not os.path.exists('config/sources.yaml'):
        with open('config/sources.yaml', 'w') as f:
            f.write("""sources:
  adiga:
    name: "Adiga University Portal"
    url: "https://adiga.kr"
    enabled: true
""")
        print("   Created config/sources.yaml")

# Test 3: Scraper
print("\n3. Testing scraper...")
try:
    print("   Creating scraper instance...")
    scraper = AdigaFinalScraper({'url': 'https://adiga.kr'})
    
    print("   Fetching articles (this may take 10-20 seconds)...")
    import time
    start_time = time.time()
    
    articles = scraper.fetch_articles()
    
    elapsed = time.time() - start_time
    print(f"   Fetch completed in {elapsed:.1f} seconds")
    print(f"   Found {len(articles)} articles")
    
    if articles:
        print("\n   First 3 articles:")
        for i, article in enumerate(articles[:3]):
            print(f"   {i+1}. {article['title'][:60]}...")
            print(f"      URL: {article['url']}")
            print(f"      Source: {article.get('source', 'unknown')}")
        
        # Test parsing first article
        print("\n   Testing article parsing...")
        parsed = scraper.parse_article(articles[0])
        print(f"      Title: {parsed.title[:50]}...")
        print(f"      Content length: {len(parsed.content)} characters")
        if parsed.content:
            print(f"      Preview: {parsed.content[:100]}...")
        
        print("\n✅ SCRAPER TEST PASSED!")
        
        # Ask user if they want to run monitor
        print("\n" + "=" * 60)
        print("READY TO RUN MONITOR")
        print("=" * 60)
        
        print("\nOptions:")
        print("1. Test mode (no Telegram messages)")
        print("2. Run for real (sends to Telegram)")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            print("\nStarting in TEST mode...")
            os.system('python3 core/monitor_engine.py --test')
        elif choice == '2':
            print("\nStarting monitor...")
            os.system('python3 core/monitor_engine.py')
        else:
            print("\nExiting. You can run manually:")
            print("  python3 core/monitor_engine.py --test")
            print("  python3 core/monitor_engine.py")
        
    else:
        print("\n⚠ No articles found.")
        print("\nDebug files created:")
        debug_files = [f for f in os.listdir('.') if f.startswith('final_')]
        for f in debug_files:
            print(f"  - {f}")
        
        print("\nCheck these files to see what the scraper received.")
        print("If files are very small, the site might be blocking requests.")
        
except Exception as e:
    print(f"\n❌ Scraper test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
