#!/usr/bin/env python3
"""
Fix Telegram links to be proper HTML links
"""
import os
import re

formatter_path = 'telegram_formatter.py'

with open(formatter_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix the URL line in format_telegram_message
# Look for: message += f"🔗 <b>링크</b>: {safe_url}\\n"
# Change to: message += f"🔗 <b>링크</b>: <a href=\\"{safe_url}\\">기사 보기</a>\\n"

# Find the pattern
pattern = r'(message\s*\+=.*?링크.*?\{safe_url\}.*?\n)'
match = re.search(pattern, content, re.IGNORECASE)

if match:
    old_line = match.group(1)
    print(f"Found URL line: {old_line.strip()}")
    
    # Create new line with HTML link
    new_line = '    message += f"🔗 <b>링크</b>: <a href=\\"{safe_url}\\">기사 보기</a>\\n"\n'
    
    # Replace
    updated_content = content.replace(old_line, new_line)
    
    # Backup
    backup_path = f'{formatter_path}.backup_links'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backed up to {backup_path}")
    
    # Write updated
    with open(formatter_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"✅ Updated Telegram formatter")
    print(f"\nChanged:")
    print(f"FROM: {old_line.strip()}")
    print(f"TO:   {new_line.strip()}")
    
else:
    print("❌ Could not find the URL line to update")
    print("Looking for line containing: 링크 and {safe_url}")
    
    # Try alternative approach - show the function
    print("\nCurrent format_telegram_message function:")
    print("-" * 40)
    lines = content.split('\n')
    in_function = False
    for i, line in enumerate(lines):
        if 'def format_telegram_message' in line:
            in_function = True
        if in_function and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            if i > 0 and 'def format_telegram_message' not in lines[i-1]:
                in_function = False
        
        if in_function and ('링크' in line or '🔗' in line):
            print(f"{i+1}: {line}")
