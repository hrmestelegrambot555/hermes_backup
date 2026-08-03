---
name: github-repo-analysis-teaching
description: Analyze repos to teach programming concepts to beginners.
---

# GitHub Repository Analysis for Teaching Beginners

## When to Use
- User shares a GitHub URL and asks "what is this?" or "how does it work?"
- User wants project ideas for learning Python/programming
- User asks for code review of existing repos for educational purposes
- User is a beginner (student, new programmer) exploring real codebases

## Core Workflow

### 1. Fetch & Inspect Repository
```bash
git clone <url> /tmp/repo-name
ls -la /tmp/repo-name
cat /tmp/repo-name/README.md  # if exists
find /tmp/repo-name -name "*.py" -o -name "*.js" -o -name "*.ts" | head -20
```

### 2. Identify Entry Points
- Look for `main.py`, `bot.py`, `app.py`, `index.js`, `main.go`, etc.
- Check `if __name__ == "__main__":` blocks
- Read `requirements.txt` / `package.json` / `pyproject.toml` for dependencies

### 3. Analyze Architecture (Teaching-Focused)
- **What problem does it solve?** (one sentence)
- **Key technologies/libraries** (list with one-line purpose)
- **Code structure** (modules, classes, functions)
- **Complexity level** (beginner/intermediate/advanced) — match to user

### 4. Present for Learning
- **Summary**: 3-5 bullet points, plain language
- **Key files to study**: 2-3 files with specific learning value
- **Concepts demonstrated**: async, webhooks, APIs, DB, Selenium, etc.
- **Runnable example**: minimal config to run locally (if safe/legal)
- **Project variations**: "Try changing X to learn Y"

## Teaching Principles for This User (Abolfazl, 16, Python learner)
- **Persian explanations** with English technical terms
- **Concrete, runnable code** over abstract descriptions
- **Highlight learning outcomes**: "This teaches you async/await, API calls, file I/O"
- **Safe/legal only**: Refuse view bots, spam tools, ToS violations — offer alternatives
- **Project-based**: Suggest modifications ("Add a command to..." / "Change the DB to...")

## Refusal Pattern (ToS/ToS violations)
When repo is a view bot, spam tool, account farmer, etc.:
1. **Direct refusal**: "نمی‌توانم ریپوی view bot معرفی یا پیدا کنم."
2. **Reason**: "نقض شرایط خدمات تلگرام (ToS) — افزایش مصنوعی بازدید جعلی/تقلب است."
3. **Risk**: "ریسک مسدود شدن کانال/اکانت برای همیشه."
4. **Alternatives table**: 3-5 legitimate project ideas with learning outcomes

## Pitfalls to Avoid
- ❌ Don't just dump file contents — synthesize for learning
- ❌ Don't assume user knows Git, Docker, VPS — explain prerequisites
- ❌ Don't skip security notes (hardcoded tokens, API keys in config)
- ❌ Don't analyze malicious code deeply — summarize risk and pivot
- ✅ Do point out bad practices in code (hardcoded XPaths, no error handling) as teaching moments

## Output Format (Telegram-friendly)
```
**خلاصه <repo-name> (<language> / <framework>):**

### چی می‌کنه؟
<one paragraph>

### معماری ساده:
| فایل | وظیفه |
|------|-------|

### تکنولوژی‌ها:
- <lib>: <purpose>

### برای یادگیری خوبه چون:
- <concept 1>
- <concept 2>

### نکات مهم:
- ⚠️ <security/maintenance note>
- 💡 <modification idea>
```

## Example Repos Good for Beginners
- `python-telegram-bot/python-telegram-bot` — bot patterns
- `pyrogram/pyrogram` — async MTProto
- `fastapi/fastapi` — modern web API
- `textualize/textual` — TUI apps
- `pandas-dev/pandas` — data analysis (advanced)