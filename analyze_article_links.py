import re

# Read the HTML file
with open('adiga_desktop_full.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all article links with prtlBbsId
article_links = re.findall(r'href="([^"]*prtlBbsId=\d+[^"]*)"', content)

print(f"Found {len(article_links)} article links with prtlBbsId")
print("\nArticle links found:")
for i, link in enumerate(article_links[:10]):
    print(f"{i+1}. {link}")
    
    # Extract the article title around this link
    # Find context (100 chars before and after)
    start = max(0, content.find(link) - 100)
    end = min(len(content), content.find(link) + 300)
    context = content[start:end]
    
    # Clean up context
    context = re.sub(r'\s+', ' ', context)
    print(f"   Context: {context[:150]}...")
    print()
