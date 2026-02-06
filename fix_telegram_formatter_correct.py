#!/usr/bin/env python3
"""
Correct fix for telegram_formatter.py
"""
import os

formatter_path = 'telegram_formatter.py'

if not os.path.exists(formatter_path):
    print(f"❌ {formatter_path} not found")
    exit(1)

with open(formatter_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the format_program function
lines = content.split('\n')
updated_lines = []
in_format_program = False
changed = False

for i, line in enumerate(lines):
    updated_lines.append(line)
    
    # Check if we're entering format_program function
    if line.strip().startswith('def format_program('):
        in_format_program = True
    
    # Inside format_program, find the title line
    if in_format_program and 'title = program_data.get(' in line and not changed:
        # We need to replace this line with telegram_title check
        indent = ' ' * (len(line) - len(line.lstrip()))
        
        # Remove the current title line
        updated_lines.pop()  # Remove the line we just added
        
        # Insert the new code
        updated_lines.append(f"{indent}# Use telegram_title if available (for Adiga compatibility)")
        updated_lines.append(f"{indent}telegram_title = program_data.get('telegram_title')")
        updated_lines.append(f"{indent}if telegram_title:")
        updated_lines.append(f"{indent}    title = telegram_title")
        updated_lines.append(f"{indent}else:")
        updated_lines.append(f"{indent}    title = program_data.get('title', 'No Title')")
        
        changed = True
        
        print(f"✅ Found and updated line {i+1}: {line.strip()}")
    
    # Check if we're leaving the function (next function or class)
    if in_format_program and i > 0 and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
        if line.strip().startswith('def ') or line.strip().startswith('class '):
            in_format_program = False

if changed:
    # Backup
    backup_path = f'{formatter_path}.backup_fix'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backed up to {backup_path}")
    
    # Write updated
    with open(formatter_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines))
    print(f"✅ Updated {formatter_path}")
    
    print("\n🔧 Changes made:")
    print("Before:")
    print("  title = program_data.get('title', 'No Title')")
    print("\nAfter:")
    print("  # Use telegram_title if available (for Adiga compatibility)")
    print("  telegram_title = program_data.get('telegram_title')")
    print("  if telegram_title:")
    print("      title = telegram_title")
    print("  else:")
    print("      title = program_data.get('title', 'No Title')")
    
else:
    print("❌ Could not find the title line to update")
    print("Looking for: title = program_data.get('title', 'No Title')")
