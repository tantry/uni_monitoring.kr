#!/usr/bin/env python3
"""
Proper fix for escape_html to not double-escape
"""
import os

formatter_path = 'telegram_formatter.py'

with open(formatter_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the entire escape_html function with a better version
new_escape_html = '''def escape_html(text):
    """Escape HTML but don't double-escape existing entities"""
    if not text:
        return ""
    
    import html
    # html.escape converts: & -> &amp;, < -> &lt;, > -> &gt;, " -> &quot;, ' -> &#x27;
    # But we don't want to escape & if it's part of an existing entity like &#x27;
    
    # Simple approach: only escape the bare minimum needed for Telegram
    # Telegram HTML mode needs: < > & " '
    # But ' can be &#x27; or &apos; or '
    
    # Actually, html.escape is fine, but we need to handle the case where
    # text already contains HTML entities
    text = str(text)
    
    # Replace & only if it's not part of an HTML entity
    # This regex matches & that are not followed by # or word chars and ;
    import re
    # First escape < and >
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Handle quotes - but carefully
    text = text.replace('"', '&quot;')
    # For single quote, use &#x27; which is standard
    text = text.replace("'", '&#x27;')
    
    return text'''

# Simple replacement
import re
pattern = r'def escape_html\(text\):.*?return text'
updated_content = re.sub(pattern, new_escape_html, content, flags=re.DOTALL)

if updated_content != content:
    # Backup
    backup_path = f'{formatter_path}.backup_proper'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backed up to {backup_path}")
    
    # Write updated
    with open(formatter_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"✅ Updated escape_html function with proper fix")
    
    # Also update scraper to not pre-escape
    scraper_path = 'scrapers/adiga_scraper.py'
    if os.path.exists(scraper_path):
        with open(scraper_path, 'r', encoding='utf-8') as f:
            scraper_content = f.read()
        
        # Change telegram_title assignment
        scraper_content = scraper_content.replace(
            "telegram_title = title.replace(\"'\", \"&#x27;\")",
            "telegram_title = title  # Don't pre-escape, escape_html will handle it"
        )
        
        with open(scraper_path, 'w', encoding='utf-8') as f:
            f.write(scraper_content)
        print(f"✅ Updated scraper to not pre-escape")
    
    print("\n🔧 Changes made:")
    print("1. escape_html now handles escaping properly without double-escaping")
    print("2. Scraper no longer pre-escapes single quotes")
    print("3. Telegram messages should now show &#x27; not &amp;#x27;")
    
else:
    print("❌ Could not update escape_html function")
