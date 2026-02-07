#!/usr/bin/env python3
"""
Fix escape_html function in telegram_formatter.py
"""
import os
import re

formatter_path = 'telegram_formatter.py'

with open(formatter_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the escape_html function
new_escape_html = '''def escape_html(text):
    if not text:
        return ""
    # Don't escape existing HTML entities
    # First, protect existing HTML entities
    import re
    html_entities = re.findall(r'&[#\\w]+;', text)
    for i, entity in enumerate(html_entities):
        text = text.replace(entity, f'__HTML_ENTITY_{i}__')
    
    # Escape the text
    import html
    text = html.escape(text)
    
    # Restore HTML entities
    for i, entity in enumerate(html_entities):
        text = text.replace(f'__HTML_ENTITY_{i}__', entity)
    
    return text'''

# Replace the function
import re
updated_content = re.sub(r'def escape_html\(text\):.*?return text', new_escape_html, content, flags=re.DOTALL)

if updated_content != content:
    # Backup
    backup_path = f'{formatter_path}.backup_escape'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backed up to {backup_path}")
    
    # Write updated
    with open(formatter_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"✅ Updated escape_html function")
    
    # Show the change
    print("\nBefore:")
    print("  def escape_html(text):")
    print("      if not text:")
    print("          return \"\"")
    print("      text = html.escape(text)")
    print("      text = text.replace('\"', '&quot;')")
    print("      text = text.replace(\"'\", '&apos;')")
    print("      return text")
    
    print("\nAfter:")
    print("  def escape_html(text):")
    print("      if not text:")
    print("          return \"\"")
    print("      # Don't escape existing HTML entities")
    print("      import re")
    print("      html_entities = re.findall(r'&[#\\\\w]+;', text)")
    print("      for i, entity in enumerate(html_entities):")
    print("          text = text.replace(entity, f'__HTML_ENTITY_{i}__')")
    print("      ")
    print("      # Escape the text")
    print("      import html")
    print("      text = html.escape(text)")
    print("      ")
    print("      # Restore HTML entities")
    print("      for i, entity in enumerate(html_entities):")
    print("          text = text.replace(f'__HTML_ENTITY_{i}__', entity)")
    print("      ")
    print("      return text")
else:
    print("❌ Could not find escape_html function to update")
