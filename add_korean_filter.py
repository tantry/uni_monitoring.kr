import re

with open('uni_monitor.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add KOREAN_KEYWORDS after ENGLISH_KEYWORDS
content = re.sub(
    r'(ENGLISH_KEYWORDS = \[.*?\])',
    r'\1\nKOREAN_KEYWORDS = ["한국어", "한국어학과", "한국어교육", "한국어문학", "한글", "한국언어"]',
    content,
    flags=re.DOTALL
)

# 2. Add has_korean variable in analyze_article function
content = re.sub(
    r'(has_english = any\(kw in title for kw in ENGLISH_KEYWORDS\))',
    r'\1\n    has_korean = any(kw in title for kw in KOREAN_KEYWORDS)',
    content
)

# 3. Update Priority 1 check to include Korean
content = re.sub(
    r'if has_target_uni and \(has_english or has_music\) and has_admission:',
    'if has_target_uni and (has_english or has_korean or has_music) and has_admission:',
    content
)

# 4. Update Telegram alert to show Korean detection
content = re.sub(
    r'if any\(kw in title for kw in ENGLISH_KEYWORDS\):',
    'if any(kw in title for kw in ENGLISH_KEYWORDS):\n        detected.append("영어 프로그램")\n    if any(kw in title for kw in KOREAN_KEYWORDS):\n        detected.append("한국어 프로그램")',
    content
)

with open('uni_monitor.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added Korean language filtering!")
print("Korean keywords: 한국어, 한국어학과, 한국어교육, 한국어문학, 한글, 한국언어")
print("Now alerts will trigger for: Target University + (English OR Korean OR Music) + Admission")
