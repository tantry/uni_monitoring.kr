#!/usr/bin/env python3
"""Fix Telegram config issue"""
import sys
import os

# Read multi_monitor.py
with open('multi_monitor.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check what config it expects
if 'CHAT_ID' in content:
    print("multi_monitor.py expects: CHAT_ID")
if 'CHANNEL_ID' in content:
    print("multi_monitor.py expects: CHANNEL_ID")

# Check config.py
try:
    with open('config.py', 'r', encoding='utf-8') as f:
        config_content = f.read()
        if 'CHAT_ID' in config_content:
            print("config.py has: CHAT_ID")
        if 'CHANNEL_ID' in config_content:
            print("config.py has: CHANNEL_ID")
        if 'BOT_TOKEN' in config_content:
            print("config.py has: BOT_TOKEN")
except:
    print("Could not read config.py")
