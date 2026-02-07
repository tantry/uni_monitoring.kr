#!/usr/bin/env python3
"""
Examine how URLs are formatted in telegram_formatter.py
"""
import os

formatter_path = 'telegram_formatter.py'

with open(formatter_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the format_telegram_message function
import re
match = re.search(r'def format_telegram_message\(.*?\):.*?(?=\n\S)', content, re.DOTALL)
if match:
    function_text = match.group(0)
    print("Current format_telegram_message function:")
    print("=" * 60)
    print(function_text[:500] + "..." if len(function_text) > 500 else function_text)
    print("=" * 60)
    
    # Look for the URL line
    lines = function_text.split('\n')
    for i, line in enumerate(lines):
        if '링크' in line or 'url' in line.lower() or '🔗' in line:
            print(f"\nLine {i}: {line.strip()}")
            
            # Show context
            for j in range(max(0, i-2), min(len(lines), i+3)):
                print(f"  {j}: {lines[j].rstrip()}")
else:
    print("Could not find format_telegram_message function")
