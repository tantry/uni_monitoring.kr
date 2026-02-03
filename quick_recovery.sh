#!/bin/bash
# Quick recovery script for new chat sessions
echo "=== UNIVERSITY MONITOR QUICK RECOVERY ==="
echo ""
echo "PROJECT STATUS SUMMARY:"
echo "-----------------------"
echo "Project: University Admission Monitor"
echo "Location: ~/uni_monitoring"
echo "Current Phase: Fixing Adiga article links"
echo ""
echo "CORE FILES:"
echo "-----------"
for file in uni_monitor.py deadline_alerts.py check_now.sh FUTURE_PROJECTS.md; do
    if [ -f "$file" ]; then
        size=$(stat -c%s "$file")
        lines=$(wc -l < "$file" 2>/dev/null || echo "N/A")
        echo "✓ $file (${size} bytes, ${lines} lines)"
    else
        echo "✗ $file (MISSING)"
    fi
done
echo ""
echo "LAST TEST:"
echo "----------"
if [ -f "test_link_extraction.py" ]; then
    echo "Test script exists, last run:"
    python3 test_link_extraction.py 2>&1 | tail -10
else
    echo "No recent test found"
fi
echo ""
echo "TELEGRAM CONFIG:"
echo "----------------"
grep -E "(BOT_TOKEN|CHANNEL_ID)" uni_monitor.py deadline_alerts.py | head -4
echo ""
echo "NEXT ACTION:"
echo "------------"
echo "Run: ./check_now.sh"
echo "Or: python3 uni_monitor.py"
echo ""
echo "GITHUB READY: Use this output for new chat"
