#!/bin/bash
echo "=== UNIVERSITY CHECK - $(date '+%Y-%m-%d %A %H:%M') ==="
echo ""

echo "1. 📰 Checking Adiga for new articles..."
python3 uni_monitor.py

echo ""
echo "2. 📅 Checking deadlines..."
if [ "$(date +%u)" -eq 3 ]; then  # 3=Wednesday
    echo "   ✅ Today is Wednesday - running deadline check"
    python3 deadline_alerts.py
else
    day_name=$(LANG=ko_KR.UTF-8 date '+%A' 2>/dev/null || date '+%A')
    echo "   ⏸️  Today is $day_name - deadline check runs on Wednesdays only"
fi

echo ""
echo "=== CHECK COMPLETE ==="
echo "Run this script again when you want another check."
