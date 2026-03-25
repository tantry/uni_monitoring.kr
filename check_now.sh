#!/bin/bash
cd ~/uni_monitoring.kr

echo "==============================================="
echo "   UNIVERSITY ADMISSION MONITOR"
echo "   Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "==============================================="

python3 core/monitor_engine.py

# Run deadline alerts on Wednesdays only
if [ $(date +%u) -eq 3 ]; then
    echo ""
    echo "--- Running Wednesday deadline alerts ---"
    python3 deadline_alerts.py
fi

echo ""
echo "==============================================="
echo "   Completed: $(date '+%Y-%m-%d %H:%M:%S')"
echo "==============================================="
