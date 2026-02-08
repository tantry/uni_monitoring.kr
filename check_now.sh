#!/bin/bash
# University Admission Monitor - Using New Architecture
cd ~/uni_monitoring.kr

echo "==============================================="
echo "   UNIVERSITY ADMISSION MONITOR"
echo "   Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "==============================================="

python3 core/monitor_engine.py

echo ""
echo "==============================================="
echo "   Completed: $(date '+%Y-%m-%d %H:%M:%S')"
echo "==============================================="
