# Telegram Userbot Session String & Railway Deployment

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

**Run locally once:**
```bash
python gen_session_string.py
# Enter code from Telegram → prints SESSION_STRING
```

**Railway Environment Variables:**
```
API_ID=31844510
API_HASH=your_hash
SESSION_STRING=1AgAOMTQ5... (long string from above)
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