# Railway Deployment for Telegram Bots/Userbots

Railway is a cloud platform ideal for deploying Python Telegram bots and userbots that need 24/7 uptime.

## When to Use
- Spellcheck userbots that must run continuously
- News forwarding bots
- Any bot that needs to survive server restarts
- Free tier: 500 hours/month (enough for 1 bot 24/7)

## Required Files

### requirements.txt
```
telethon==1.44.0
requests>=2.31.0
```

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### main.py
Your bot script. Key considerations:
- Hardcode API keys as fallback: `os.environ.get("KEY", "fallback-value")`
- No interactive input — handle Telethon auth via file-based IPC
- Include `.session` file in repo for Telethon (avoids re-auth)

### Session String (RECOMMENDED for Telethon)

Instead of including a `.session` file in the repo (security risk, hard to update), use a **session string** — an encoded string that contains all auth data:

**Step 1: Generate session string LOCALLY**
```python
# gen_session_string.py - run this on your local machine
from telethon.sync import TelegramClient

API_ID = 31844510
API_HASH = "your_api_hash"
PHONE = "+1234567890"

with TelegramClient('session_gen', API_ID, API_HASH) as client:
    client.start(phone=PHONE)
    string = client.session.save()
    print(f"SESSION_STRING={string}")
```

**Step 2: Set as Railway environment variable**
- Variable name: `SESSION_STRING`
- Value: the long string from step 1

**Step 3: Use in your bot**
```python
from telethon import TelegramClient, StringSession
import os

SESSION_STRING = os.environ.get("SESSION_STRING", "")
client = StringSession(SESSION_STRING)
await client.connect()

# No re-auth needed!
if not await client.is_user_authorized():
    print("Session expired - regenerate with gen_session_string.py")
    return
```

**Why session strings are better for cloud deployment:**
- No `.session` file to manage (security risk if pushed to GitHub)
- Easy to update — just change the env var
- Works across container restarts
- Can be rotated without code changes

**Pitfall**: Session strings can expire. If bot fails with auth errors, regenerate the string.

### Legacy: Session File (not recommended)

If you must use a session file (e.g., for local testing):

```bash
# Include in repo
cp ~/.local/share/telethon/*.session ./hermes_spellcheck.session
```

**CRITICAL**: Add `.session` to `.gitignore` and NEVER push to GitHub. Use Railway's file mounting or environment variables instead.

### Environment Variables (Railway)

Set these in Railway dashboard under Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | `123456:ABC-DEF...` |
| `OPENROUTER_API_KEY` | For AI-powered features (optional) | `sk-or-v1-...` |

**Important**: Never hardcode secrets in code that will be pushed to GitHub. Use environment variables with fallbacks.

```python
import os
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
```

### Deployment Steps

1. Create GitHub repo with all files
2. Go to railway.app → Login with GitHub
3. New Project → Deploy from GitHub repo
4. Select repo → Railway auto-builds and deploys
5. Check logs in Railway dashboard

## Pitfalls

1. **Session files**: Telethon `.session` files must be in the repo. Without it, bot will try to authenticate interactively and fail. **Better approach**: Use session strings (see above).

2. **Environment variables**: Railway provides a clean environment. If bot uses `os.environ.get()`, hardcode fallback values.

3. **Free tier limits**: 500 hours/month. Multiple bots share this quota. Monitor usage in Railway dashboard.

4. **No persistent filesystem**: Railway containers restart. Don't rely on local files for state — use Redis, databases, or GitHub for persistence.

5. **Port binding**: Railway assigns a PORT env var. For webhooks, bind to `0.0.0.0:$PORT`. For polling bots (getUpdates), no port needed.

6. **Build failures**: Check build logs. Common issues:
   - Missing `requirements.txt`
   - Python version mismatch (add `runtime.txt` with `python-3.11`)
   - System dependencies not available (use pure Python packages)

7. **Dictionary size and memory**: Large dictionaries (1M+ entries, ~44MB JSON) work on Railway's free tier (512MB RAM), but test first. If OOM, reduce to ~400K entries (~16MB). Score entries by priority: short words = highest, character conversions = high, half-space fixes = medium, long phrases = lower.

8. **Zombie processes cause SQLite locks**: Before assuming OOM, check for zombie Python processes. Scan `/proc/*/cmdline` for leftover `spellcheck_userbot.py` and kill them. The SQLite `database is locked` error causes Telethon to crash, which looks like OOM but isn't.

9. **Database checkpoint before restart**: If Telethon's session database is locked, checkpoint it before restarting:
   ```python
   import sqlite3
   conn = sqlite3.connect('session.session')
   conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
   conn.close()
   ```
