#!/bin/bash
# University Admission Monitor - Multi-Source Version

cd ~/uni_monitoring.kr

echo "==============================================="
echo "   UNIVERSITY ADMISSION MONITOR - MULTI-SOURCE"
echo "   Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "==============================================="

python3 multi_monitor.py

echo ""
echo "==============================================="
echo "   Completed: $(date '+%Y-%m-%d %H:%M:%S')"
echo "==============================================="
