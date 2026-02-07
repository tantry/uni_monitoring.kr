#!/bin/bash
echo "=== Fixing Telegram Chat ID ==="
echo ""
echo "Your current chat_id: 440747849"
echo ""
echo "Channel IDs should look like: -1001234567890"
echo "Group IDs are negative numbers: -123456789"
echo ""
echo "To get correct chat ID:"
echo "1. Add your bot to the channel/group as admin"
echo "2. Send a message to the channel/group"
echo "3. Run this command:"
echo ""
echo "curl -s \"https://api.telegram.org/bot$(grep -A2 'telegram:' config/config.yaml | grep 'bot_token' | cut -d'"' -f2)/getUpdates\" | python3 -m json.tool"
echo ""
echo "Look for 'chat': {'id': -1001234567890}"
echo ""
echo "Alternatively, test with these common formats:"
echo "1. Add -100 prefix: -100440747849"
echo "2. Make it negative: -440747849"
echo ""
echo "Let's test both:"

BOT_TOKEN=$(grep -A2 'telegram:' config/config.yaml | grep 'bot_token' | cut -d'"' -f2)

# Test format 1: -100 prefix
echo ""
echo "Testing: -100440747849"
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": -100440747849, "text": "Test 1: -100 prefix format", "parse_mode": "Markdown"}' | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin), indent=2))"

# Test format 2: Negative
echo ""
echo "Testing: -440747849"
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": -440747849, "text": "Test 2: Negative format", "parse_mode": "Markdown"}' | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin), indent=2))"
