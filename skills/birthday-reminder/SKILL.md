---
name: birthday-reminder
description: "用自然语言管理生日提醒。存储生日到 /Users/xiaodongmei/.openclaw/workspace/data/birthdays.md，获取即将到来的生日、计算年龄。当用户提到生日、想要记录某人生日、查看即将到来的生日、询问某人年龄时使用。触发词：生日、birthday、记住生日、下一个生日、谁的生日、多大了。"
---

# Birthday Reminder Skill

Manage birthdays naturally. Store in data/birthdays.md, query with natural language.

## Storage

Birthdays are stored in /Users/xiaodongmei/.openclaw/workspace/data/birthdays.md:

Format: - **Name** - DD.MM.YYYY (今年X岁) or - **Name** - DD.MM.

## Adding Birthdays
When user says things like:
- 记住：小明的生日是3月15号
- X的生日是1985年5月10日
- Valentina hat am 14. Februar Geburtstag

Action: Parse name+date, extract year if provided, calculate upcoming age, append to /Users/xiaodongmei/.openclaw/workspace/data/birthdays.md, confirm.

## Querying Birthdays
When user asks:
- 小明的生日是什么时候？
- 接下来谁过生日？
- 小明今年多大了？

Action: Read /Users/xiaodongmei/.openclaw/workspace/data/birthdays.md, parse entries, calculate days until each birthday, sort by upcoming date, show age.

## Listing All
When user says: 列出所有生日 / 我记录了哪些生日

## Date Parsing
Support: 3月15日, 1990年3月15日, 15.03.1990, 1990-03-15

## Age Calculation
If birth year is known, calculate current/upcoming age.

## Automatic Reminders
For cron/reminders, check birthdays daily and notify if: 7 days before, 1 day before, on the day.

## File Format
Each line: - **Name** - DD.MM.YYYY (今年X岁) or - **Name** - DD.MM.
Keep sorted by date (month/day).
