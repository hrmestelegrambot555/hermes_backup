---
name: telegram-userbot-development
description: "Telegram bots with Telethon: session auth, Railway, AI fix."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [telegram, telethon, userbot, session-string, railway, spellcheck, ai-fallback, oom, database-locking]
    related_skills: [fastapi-htmx-web-apps, systematic-debugging, python-debugpy]
---

# Telegram Userbot Development with Telethon

Build production-ready Telegram userbots with Telethon: session string authentication, Railway deployment, AI spell-check with local fallback, OOM crash recovery, SQLite database locking fixes.

## Quick Start

```bash
pip install telethon==1.44.0 requests
```

```python
import os, json, asyncio, requests
from telethon import TelegramClient, events, StringSession

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

with open("persian_dict.json") as f:
    LOCAL_FIXES = json.load(f)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

async def ai_fix(text):
    if not OPENROUTER_API_KEY: return None
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        json={"model": "google/gemma-4-26b-a4b-it:free", "messages": [{"role": "user", "content": f"Fix Persian spelling: {text}"}], "max_tokens": 500, "temperature": 0.1},
        timeout=15
    )
    return response.json()["choices"][0]["message"]["content"].strip() if response.status_code == 200 else None

def local_fix(text):
    words = text.split()
    fixed = []
    for word in words:
        if word in LOCAL_FIXES:
            fixed.append(LOCAL_FIXES[word])
        else:
            fixed.append(word)
    return " ".join(fixed)

@client.on(events.NewMessage(outgoing=True))
async def handler(event):
    if not event.is_private: return
    text = event.message.text
    if not text or len(text) < 2: return
    
    ai_fixed = await ai_fix(text)
    if ai_fixed and ai_fixed != text:
        await event.message.edit(ai_fixed)
        return
    local_fixed = local_fix(text)
    if local_fixed != text:
        await event.message.edit(local_fixed)

async def main():
    await client.start()
    print(f"Logged in as: {await client.get_me()}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
```

## Session String Authentication (Railway-Ready)

**Never use phone+code on Railway.** Generate a session string locally, then set it as env var.

```python
# gen_session_string.py
from telethon.sync import TelegramClient

API_ID = 31844510
API_HASH = "your_api_hash"
PHONE = "+19432518923"

with TelegramClient('session_gen', API_ID, API_HASH) as client:
    client.start(phone=PHONE)
    string = client.session.save()
    print("SESSION_STRING:", string)
```

**Railway Environment Variables:**
```
API_ID=31844510
API_HASH=your_hash
SESSION_STRING=1AgAOMTQ5... (long string)
OPENROUTER_API_KEY=sk-or-v1-...
```

## AI + Local Dictionary Fallback Pattern

```python
async def translate(text, source, target):
    # Try AI first (smart, handles context)
    ai_result = await ai_translate(text, source, target)
    if ai_result and ai_result != text:
        return ai_result, "ai"
    
    # Fallback to local dict (fast, offline, preserves elongations/swear words)
    local_result = local_fix(text)
    if local_result != text:
        return local_result, "local"
    
    return text, "none"
```

## Elongation & Protected Words Preservation

```python
PROTECTED_WORDS = ["کص", "کیر", "کون", "فاک", "شیت"]  # Never modify

def has_elongation(word):
    return any(word[i] == word[i+1] == word[i+2] for i in range(len(word)-2))

def get_base_form(word):
    if not word: return word
    base = word[0]
    for i in range(1, len(word)):
        if word[i] != word[i-1]:
            base += word[i]
    return base

def is_protected(word):
    return any(p in word.lower() for p in PROTECTED_WORDS)

def local_fix(text):
    words = text.split()
    fixed = []
    for word in words:
        if is_protected(word):
            fixed.append(word)
            continue
        if word in LOCAL_FIXES:
            fixed.append(LOCAL_FIXES[word])
            continue
        if has_elongation(word):
            base = get_base_form(word)
            if base in LOCAL_FIXES:
                corrected = LOCAL_FIXES[base]
                if len(word) > len(base):
                    fixed.append(corrected + corrected[-1])
                else:
                    fixed.append(corrected)
                continue
        fixed.append(word)
    return " ".join(fixed)
```

## OOM Crash Recovery (VPS Memory Limits)

**Problem:** 1.3M-entry JSON dictionary (38MB) → 500MB+ in Python dict → OOM kill (exit code 137)

**Solutions:**
1. **Reduce dictionary** - Keep only high-value entries (common typos, character variants, half-space fixes)
2. **SQLite with WAL mode** - Disk-based, memory-efficient
3. **Compressed pickle** - Faster load, smaller memory

```python
# Option 1: Reduce to ~400K entries (16MB file, ~100MB RAM)
# Keep: common typos, Arab→Persian variants, half-space fixes, compounds

# Option 2: SQLite (recommended for 1M+)
import sqlite3
conn = sqlite3.connect("dictionary.db")
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("CREATE TABLE IF NOT EXISTS dict (wrong TEXT PRIMARY KEY, correct TEXT)")
conn.executemany("INSERT OR IGNORE INTO dict VALUES (?, ?)", LOCAL_FIXES.items())
conn.commit()

def local_fix(text):
    words = text.split()
    fixed = []
    for word in words:
        cursor = conn.execute("SELECT correct FROM dict WHERE wrong=?", (word,))
        row = cursor.fetchone()
        fixed.append(row[0] if row else word)
    return " ".join(fixed)
```

## SQLite Database Locking Fix

**Error:** `sqlite3.OperationalError: database is locked`

**Cause:** Zombie process holding the session file lock

```bash
# Find and kill zombie processes
ps aux | grep python | grep spellcheck
kill -9 <PID>

# Remove lock files
rm -f hermes_spellcheck.session-journal
rm -f hermes_spellcheck.session-wal
rm -f hermes_spellcheck.session-shm

# Fix session file
python3 -c "
import sqlite3, shutil
shutil.copy2('hermes_spellcheck.session', '/tmp/session_fix.db')
conn = sqlite3.connect('/tmp/session_fix.db')
conn.execute('PRAGMA journal_mode=DELETE')
conn.execute('DELETE FROM sessions')
conn.commit()
conn.execute('VACUUM')
conn.close()
shutil.copy2('/tmp/session_fix.db', 'hermes_spellcheck.session')
"
chmod 666 hermes_spellcheck.session
```

## Persistent Process with systemd (VPS)

```ini
# /etc/systemd/system/spellcheck.service
[Unit]
Description=Hermes Spellcheck Userbot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.hermes/scripts
ExecStart=/usr/bin/python3 spellcheck_userbot.py
Restart=always
RestartSec=10
Environment=API_ID=31844510
Environment=API_HASH=your_hash
Environment=SESSION_STRING=1AgAOMTQ5...
Environment=OPENROUTER_API_KEY=sk-or-v1-...

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable spellcheck
systemctl start spellcheck
systemctl status spellcheck
```

## Railway Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "spellcheck_bot:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# railway.json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": { "builder": "DOCKERFILE" },
  "deploy": {
    "startCommand": "uvicorn spellcheck_bot:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

## Form Data Encoding Fix (Persian Text)

**Problem:** FastAPI form data mangles Persian text → `Ø³ÙØ§Ù...`

**Fix:** Decode latin1 → utf-8

```python
@app.post("/translate")
async def translate(text: str = Form(...), source: str = Form("auto"), target: str = Form("fa")):
    # Fix encoding issue
    try:
        text = text.encode('latin1').decode('utf-8')
        source = source.encode('latin1').decode('utf-8')
        target = target.encode('latin1').decode('utf-8')
    except:
        pass
    # ... rest of handler
```

## Jinja2 Template Cache Fix

**Error:** `TypeError: unhashable type: 'dict'` from template caching

**⚠️ PITFALL:** `templates.env.cache = {}` does NOT reliably fix this. Prefer string replacement (see `fastapi-htmx-web-apps` skill).

```python
# If you must try Jinja2 cache fix:
templates.env.cache = {}  # May not work — verify with a test request

# Better: use string replacement
with open("templates/index.html") as f:
    HTML_TEMPLATE = f.read()
@app.get("/")
async def home():
    return HTMLResponse(HTML_TEMPLATE.replace("{{OPTIONS}}", options_html))
```

## AuthKeyUnregisteredError Recovery

**Error:** `telethon.errors.rpcerrorlist.AuthKeyUnregisteredError: The key is not registered in the system`

**Cause:** Telegram invalidated the auth key (user logged in elsewhere, changed password, or session expired).

**PITFALL:** Restoring an older backup session WILL NOT fix this — backup sessions have different auth keys. You MUST regenerate a new session string.

```bash
# 1. Kill the crashed process
pkill -9 -f spellcheck_userbot

# 2. Regenerate session string (requires SMS code)
cd /root/.hermes/scripts
python3 gen_session_string.py
# Enter the SMS code when prompted
# Copy the new SESSION_STRING

# 3. Update env var / config and restart
```

**Prevention:** Use systemd with `Restart=always` so the bot auto-restarts. When it crashes with this error, it stays down until you regenerate the session — this is expected behavior, not a bug.

## PTY for Interactive SMS Code Entry (Headless Servers)

**Problem:** Telethon's `client.start(phone=PHONE)` calls `input()` for SMS code — crashes with `EOFError: EOF when reading a line` when running in background.

**Solution:** Use PTY mode to get an interactive terminal:

```python
# Start the bot with PTY for SMS code entry
terminal(background=True, command="cd /root/.hermes/scripts && python3 spellcheck_userbot.py", pty=True)
# Then use process(action='poll') to check output
# When "Please enter the code you received:" appears:
process(action='submit', session_id='proc_xxx', data='12345')  # SMS code
```

**Alternative:** Use `gen_session_string.py` to generate a SESSION_STRING, then use StringSession for non-interactive startup (Railway/VPS background).

**PITFALL:** After `input()` in background mode, the process crashes immediately with `EOFError`. Always use PTY for any script that needs interactive input.

## Systematic Debugging Applied

From [systematic-debugging](../systematic-debugging/SKILL.md):

1. **OOM kills** → Read error (exit code 137), traced to dict size, reduced entries, verified with `/proc/self/cgroup` memory limit
2. **Encoding bugs** → Built tight loop with `curl`, traced to form data parsing, fixed with latin1→utf8 decode
3. **Template cache errors** → `templates.env.cache = {}` failed repeatedly (7+ attempts). Read stack trace deeper: cache key includes context vars. Fixed by abandoning Jinja2, using string replacement instead.
4. **Database locking** → Traced to zombie process, killed and fixed session file
5. **API rate limits** → Read error message, implemented fallback chain
6. **AuthKeyUnregisteredError** → Session invalidated by Telegram. Backup sessions have different auth keys → cannot restore. Must regenerate session string with SMS verification.

## Files from This Session

- `spellcheck_userbot.py` — Main userbot with AI+local fallback
- `gen_session_string.py` — Session string generator for Railway
- `persian_dict.json` — 1.1M Persian typo corrections
- `translator_web.py` — FastAPI web translator (3 backends)
- `templates/index.html` — Dark theme RTL UI with particles
- `deploy_spellcheck/` — Railway deploy package
- `deploy_translator/` — Railway deploy for web translator

## Reference Files

- `references/pty-interactive-input.md` — PTY pattern for SMS codes & interactive scripts
- `references/cloudflare-workers-translator.md` — Single-file CF Worker translator pattern