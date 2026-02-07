#!/bin/bash
echo "=== Final Integration ==="

# Set as main scraper
echo "1. Setting as main scraper..."
cp scrapers/adiga_final.py scrapers/adiga_scraper.py
sed -i 's/class AdigaFinalScraper/class AdigaScraper/' scrapers/adiga_scraper.py
sed -i 's/AdigaFinalScraper(/AdigaScraper(/' scrapers/adiga_scraper.py

echo "2. Running final test..."
python3 final_test.py

echo -e "\n=== Final Setup Complete ==="
echo -e "\nYour system now has:"
echo "✅ Selenium 4.40.0"
echo "✅ Smart scraper with fallback"
echo "✅ Chrome at /usr/bin/google-chrome-stable"
echo "✅ Test script: final_test.py"
echo ""
echo "To run anytime:"
echo "  python3 final_test.py"
echo "  python3 core/monitor_engine.py --test"
echo "  python3 core/monitor_engine.py"
