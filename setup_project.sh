#!/bin/bash
echo "=== Setting Up Project for Proper Imports ==="

# Create missing __init__.py files
echo "1. Creating package __init__.py files..."
for dir in core scrapers models notifiers filters; do
    if [ -d "$dir" ] && [ ! -f "$dir/__init__.py" ]; then
        echo "# $dir package" > "$dir/__init__.py"
        echo "__all__ = []" >> "$dir/__init__.py"
        echo "Created $dir/__init__.py"
    fi
done

# Create a proper setup.py
echo "2. Creating setup.py for proper package installation..."
cat > setup.py << 'SETUPEOF'
from setuptools import setup, find_packages

setup(
    name="uni_monitoring",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.0',
        'beautifulsoup4>=4.11.0',
        'pyyaml>=6.0',
        'python-telegram-bot>=20.0',
    ],
    python_requires='>=3.8',
)
SETUPEOF

echo "3. Installing in development mode..."
pip install -e . 2>/dev/null || python3 -m pip install -e .

echo "4. Creating test script..."
cat > test_all_imports.py << 'TESTEOF'
#!/usr/bin/env python3
"""Test all imports for the project"""
import sys
import os

print("Testing project imports...")
print(f"Python path: {sys.path}")

# Try importing core modules
try:
    from core.base_scraper import BaseScraper
    print("✓ Imported BaseScraper from core.base_scraper")
except ImportError as e:
    print(f"✗ Failed to import BaseScraper: {e}")

# Try importing models
try:
    from models.article import Article
    print("✓ Imported Article from models.article")
except ImportError as e:
    print(f"✗ Failed to import Article: {e}")

# Try importing scrapers
try:
    from scrapers.adiga_scraper import AdigaScraper
    print("✓ Imported AdigaScraper from scrapers.adiga_scraper")
except ImportError as e:
    print(f"✗ Failed to import AdigaScraper: {e}")

# Try importing notifiers
try:
    from notifiers.telegram_notifier import TelegramNotifier
    print("✓ Imported TelegramNotifier from notifiers.telegram_notifier")
except ImportError as e:
    print(f"✗ Failed to import TelegramNotifier: {e}")

print("\nCurrent working directory:", os.getcwd())
print("Directory contents:")
for item in os.listdir('.'):
    print(f"  {item}/" if os.path.isdir(item) else f"  {item}")
TESTEOF

echo "5. Running import test..."
python3 test_all_imports.py
