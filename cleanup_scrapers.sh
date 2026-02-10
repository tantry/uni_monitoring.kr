#!/bin/bash

# KHCU Scraper Cleanup Script
# Removes unnecessary scrapers, keeps only what you need

echo "🧹 Cleaning up scrapers directory..."
echo "======================================"
echo ""

cd ~/uni_monitoring.kr/scrapers/

echo "Current files:"
ls -la
echo ""

# Backup list
echo "FILES TO REMOVE:"
echo "❌ khcu.ac.kr_scraper.py      (old incomplete KHCU)"
echo " scraper_base.py             (deprecated)"
echo " rss_feed_scraper.py         (deprecated)"
echo "❌ unn_news_scraper.py         (not used)"
echo "❌ unn_news_scraper_fixed.py   (not used)"
echo "❌ __pycache__                 (auto-regenerates)"
echo ""

echo "FILES TO KEEP:"
echo "✅ __init__.py"
echo "✅ adiga_scraper.py"
echo "✅ khcu_scraper.py"
echo "✅ scraper_template.py"
echo " scraper_base.py"
echo " rss_feed_scraper.py"

# Ask for confirmation
read -p "Remove the files listed above? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing files..."
    
    # Remove individual files
    rm -f khcu.ac.kr_scraper.py
    echo "✓ Removed khcu.ac.kr_scraper.py"
    
    rm -f unn_news_scraper.py
    echo "✓ Removed unn_news_scraper.py"
    
    rm -f unn_news_scraper_fixed.py
    echo "✓ Removed unn_news_scraper_fixed.py"
    
    # Remove cache
    rm -rf __pycache__
    echo "✓ Removed __pycache__"
    
    echo ""
    echo "✅ Cleanup complete!"
    echo ""
    echo "Remaining files:"
    ls -la
    echo ""
    echo "✅ Your scrapers directory is now clean and focused!"
    
else
    echo "Cleanup cancelled. No files were removed."
fi
