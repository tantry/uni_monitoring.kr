#!/bin/bash
echo "=== CLEANING TO ROBUST STRUCTURE ==="
echo "Based on README.md project structure"
echo ""

# 1. Remove all test and temporary files
echo "1. Removing test/temp files..."
find . -type f \( -name "*test*" -o -name "*Test*" -o -name "*debug*" -o -name "*temp*" \) \
  ! -path "./.git/*" ! -name "*.gitignore" -delete 2>/dev/null
echo "   ✅ Done"

# 2. Clean scrapers - keep only files in README structure
echo ""
echo "2. Cleaning scrapers directory..."
cd scrapers

# Files that SHOULD be there according to README
README_FILES=("adiga_scraper.py" "scraper_base.py" "__init__.py")

# Remove everything else
for file in *.py; do
    keep=0
    for keep_file in "${README_FILES[@]}"; do
        if [ "$file" == "$keep_file" ]; then
            keep=1
            break
        fi
    done
    
    if [ $keep -eq 0 ]; then
        echo "   Removing: $file"
        rm -f "$file"
    else
        echo "   Keeping: $file"
    fi
done

cd ..

# 3. Check core directory structure
echo ""
echo "3. Checking core directory..."
if [ -d "core" ]; then
    echo "   Core directory exists"
    ls -la core/
else
    echo "   ⚠ Core directory missing - should exist per README"
fi

# 4. Final structure
echo ""
echo "=== FINAL STRUCTURE ==="
echo ""
find . -type f -name "*.py" | grep -v __pycache__ | sort
