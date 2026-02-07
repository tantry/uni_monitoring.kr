#!/bin/bash
echo "=== Test and Run University Monitor ==="

# Test the scraper first
echo -e "\n1. Testing scraper..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from scrapers.adiga_working import AdigaWorkingScraper, test_scraper
    print('✓ Scraper imported successfully')
    
    print('\\nRunning test...')
    articles = test_scraper()
    
    if articles:
        print(f'\\n✅ SUCCESS! Found {len(articles)} articles')
        for i, a in enumerate(articles[:3]):
            print(f'{i+1}. {a[\"title\"][:60]}...')
            print(f'   URL: {a[\"url\"]}')
        
        # Save test results
        with open('test_results.txt', 'w') as f:
            f.write(f'Found {len(articles)} articles\\n')
            for a in articles:
                f.write(f'- {a[\"title\"]}\\n  {a[\"url\"]}\\n')
    else:
        print('\\n⚠ No articles found. Check debug_last_response.html')
        
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
"

# Update the main scraper
echo -e "\n2. Updating main scraper..."
cp scrapers/adiga_working.py scrapers/adiga_scraper.py

# Test with monitor engine
echo -e "\n3. Testing with monitor engine..."
python3 core/monitor_engine.py --test 2>&1 | tail -20

# Show debug files
echo -e "\n4. Generated debug files:"
ls -la debug_*.html 2>/dev/null || echo "No debug files found"

# Instructions
echo -e "\n=== Next Steps ==="
echo "If articles were found:"
echo "   python3 core/monitor_engine.py"
echo ""
echo "If no articles found, check:"
echo "   cat debug_last_response.html"
echo "   curl -s 'https://adiga.kr' | head -100"
echo ""
echo "To manually test the site:"
echo "   curl -v 'https://adiga.kr'"
echo "   wget -O test.html 'https://adiga.kr' && wc -l test.html"
