#!/bin/bash
echo "=== Testing JavaScript Scraper ==="

# First test the scraper directly
python3 -c "
import sys
sys.path.insert(0, '.')
print('Testing AdigaJsScraper import...')
try:
    from scrapers.adiga_js_scraper import AdigaJsScraper
    print('✓ Import successful')
    
    config = {
        'url': 'https://adiga.kr',
        'name': 'Adiga JS'
    }
    
    scraper = AdigaJsScraper(config)
    print(f'✓ Scraper initialized')
    
    print('\\nFetching articles...')
    articles = scraper.fetch_articles()
    print(f'Found {len(articles)} articles')
    
    if articles:
        print('\\nFirst 3 articles:')
        for i, article in enumerate(articles[:3]):
            print(f'{i+1}. {article[\"title\"][:60]}...')
            print(f'   URL: {article[\"url\"]}')
        
        print('\\nParsing first article...')
        if articles:
            parsed = scraper.parse_article(articles[0])
            print(f'Title: {parsed.title}')
            print(f'URL: {parsed.url}')
            print(f'Content length: {len(parsed.content)} chars')
            if parsed.content:
                print(f'Preview: {parsed.content[:100]}...')
    else:
        print('\\nNo articles found. Possible issues:')
        print('1. Website structure changed')
        print('2. JavaScript blocking detected')
        print('3. Need different selectors')
        print('\\nCheck generated files:')
        print('- adiga_selenium_screenshot.png')
        print('- adiga_selenium_source.html')
    
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
"

# Test with monitor engine
echo -e "\n=== Testing with Monitor Engine ==="
python3 core/monitor_engine_js.py --test

echo -e "\n=== Files Generated ==="
ls -la | grep -E "(adiga|debug|screenshot|html)"
