# Topic-Based Notification Setup Guide

## Current Topics

| Topic | Thread ID | Content |
|-------|-----------|---------|
| Education & Training | 4 | University admissions, academic announcements |
| Finance | 5 | Finance, accounting, business, general jobs, bilingual jobs |
| Biology | 6 | Biology, pharma, biotech jobs |

## Department to Topic Mapping

| Department | Topic |
|------------|-------|
| jobs, jobs_bilingual, accounting, finance, business | Finance |
| jobs_biology | Biology |
| student_affairs, music, korean, english, liberal | Education & Training |

## How Classification Works

1. Article content is checked against department keywords
2. Requires at least 2 keyword matches to classify
3. Best matching department is selected (most matches, then lowest priority)
4. Department is mapped to topic name, then to thread ID
5. Message sent to that topic

## Priority System

Lower number = higher priority. Used when article matches multiple departments.

| Priority | Department |
|----------|------------|
| 5 | student_affairs |
| 8 | jobs_biology |
| 9 | jobs |
| 10 | jobs_bilingual |
| 11 | accounting |
| 12 | finance |
| 13 | business |
| 21 | music |
| 22 | korean |
| 23 | english |
| 24 | liberal |

## Adding a New Topic

1. Create topic in Telegram: Group → Manage Topics → Create Topic
2. Send a test message in the new topic
3. Get thread ID from: https://api.telegram.org/bot[YOUR_BOT_TOKEN]/getUpdates
4. Add to config/config.yaml under topics:
5. Add mapping under department_mapping:
6. Add department to config/filters.yaml with keywords and priority
7. Test: python3 core/monitor_engine.py --test

## Adding Keywords

Edit config/filters.yaml and add to the keywords list of the relevant department.

Example:
  jobs_biology:
    keywords: ["바이오", "제약", "임상", "새로운키워드"]

## Testing Commands

Test mode (no real notifications):
  python3 core/monitor_engine.py --test

See classification distribution:
  python3 core/monitor_engine.py --test 2>&1 | grep "부서/학과" | sed 's/.*<b>부서\/학과<\/b>: //' | sort | uniq -c

Clear database and resend all:
  rm data/state.db && python3 core/monitor_engine.py

## Troubleshooting

Job going to wrong topic:
  - Check department: grep "부서/학과" logs/monitor.log | tail -20
  - If department wrong, add keywords to correct department
  - If department correct but topic wrong, check mapping in config.yaml

Get thread IDs:
  curl "https://api.telegram.org/bot[TOKEN]/getUpdates" | python3 -m json.tool | grep -E "message_thread_id|forum_topic_created"

Check if scrapers are finding content:
  python3 core/monitor_engine.py --test 2>&1 | grep -E "adiga|khcu|Seoul"
