#!/bin/bash
echo "🧪 COMPLETE SYSTEM TEST"
echo "========================"

# 1. Test basic imports
echo "1. Testing module imports..."
python3 -c "
import sys
sys.path.append('.')
try:
    import config
    print('   ✅ config.py')
    
    from filters import filter_by_department
    print('   ✅ filters.filter_by_department')
    
    from telegram_formatter import format_telegram_message
    print('   ✅ telegram_formatter.format_telegram_message')
    
    print('   ✅ ALL CORE IMPORTS WORKING')
except Exception as e:
    print(f'   ❌ Import error: {e}')
"

# 2. Test Telegram formatting
echo -e "\n2. Testing Telegram formatting..."
python3 -c "
from telegram_formatter import format_telegram_message
msg = format_telegram_message('Test Title', 'Test Content', 'https://test.com', 'music')
print(f'   Message length: {len(msg)} chars')
print(f'   First line: {msg.split(chr(10))[0]}')
"

# 3. Test filtering
echo -e "\n3. Testing filtering..."
python3 -c "
from filters import filter_by_department
article = {'title': '서울대학교 음악학과 공고', 'content': '음악학과 모집'}
dept = filter_by_department(article)
print(f'   Test article: {article[\"title\"]}')
print(f'   Detected department: {dept}')
print(f'   ✅ Filter working' if dept == 'music' else '   ❌ Filter not working')
"

# 4. Test the fixed monitor
echo -e "\n4. Testing fixed monitor..."
echo "   Clearing state for fresh test..."
rm -f state.json

echo -e "\n   Running monitor (will send actual Telegram alerts)..."
python3 multi_monitor_fixed.py

# 5. Verify state was saved
echo -e "\n5. Verifying state..."
if [ -f "state.json" ]; then
    echo "   ✅ state.json created"
    echo "   Content:"
    cat state.json
else
    echo "   ❌ state.json not created"
fi

echo -e "\n🎯 TEST COMPLETE"
echo "========================"
echo "If you received Telegram alerts, the system is working!"
echo "Check your Telegram channel: @ReiUniMonitor_bot"
