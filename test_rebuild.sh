#!/bin/bash
echo "=== Testing Rebuilt System ==="
echo "1. Testing Python imports..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from models.article import Article
    from scrapers.adiga_scraper import AdigaScraper
    from notifiers.telegram_notifier import TelegramNotifier
    print('✓ All imports successful')
    
    # Test Article model
    article = Article('Test', 'https://example.com', 'Content', 'test')
    print(f'✓ Article model works: {article.get_hash()}')
    
except ImportError as e:
    print(f'✗ Import error: {e}')
    import traceback
    traceback.print_exc()
"

echo -e "\n2. Testing configuration..."
if [ -f "config/config.yaml" ]; then
    echo "✓ config/config.yaml exists"
    python3 -c "
import yaml
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print('  Telegram configured:', 'bot_token' in config.get('telegram', {}))
    print('  Database path:', config.get('database', {}).get('path', 'Not set'))
"
else
    echo "✗ config/config.yaml missing"
fi

echo -e "\n3. Testing Adiga scraper..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from scrapers.adiga_scraper import AdigaScraper
    
    config = {
        'url': 'https://adiga.kr',
        'name': 'Test Adiga'
    }
    
    scraper = AdigaScraper(config)
    print(f'✓ AdigaScraper initialized: {scraper.get_source_name()}')
    
    # Test link resolution
    test_onclick = \"fnDetailPopup('12345')\"
    resolved = scraper.resolve_link('', test_onclick)
    print(f'✓ JavaScript link resolution: {test_onclick} -> {resolved}')
    
except Exception as e:
    print(f'✗ Error: {e}')
"

echo -e "\n4. Directory structure:"
find . -type d -maxdepth 2 | sort

echo -e "\n=== Rebuild Complete ==="
echo -e "\nNext steps:"
echo "1. Edit config/config.yaml with your Telegram bot credentials"
echo "2. Test scraping: python core/monitor_engine.py --scrape-test"
echo "3. Test with notifications: python core/monitor_engine.py --test"
echo "4. Run for real: python core/monitor_engine.py"
