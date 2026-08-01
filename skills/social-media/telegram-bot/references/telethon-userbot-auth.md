# Telethon Userbot Authentication Reference

## Full Auth Script with File-based IPC

```python
#!/usr/bin/env python3
import asyncio, os
from telethon import TelegramClient

API_ID = YOUR_API_ID
API_HASH = "YOUR_API_HASH"
PHONE = "+1XXXXXXXXXX"
SESSION_NAME = "my_userbot"
CODE_FILE = "/tmp/tg_code.txt"
PASS_FILE = "/tmp/tg_pass.txt"

async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    async def code_callback():
        print("Waiting for code...")
        while True:
            if os.path.exists(CODE_FILE):
                with open(CODE_FILE) as f:
                    code = f.read().strip()
                if code:
                    os.remove(CODE_FILE)
                    return code
            await asyncio.sleep(1)
    
    async def password_callback():
        print("Waiting for password...")
        while True:
            if os.path.exists(PASS_FILE):
                with open(PASS_FILE) as f:
                    pw = f.read().strip()
                if pw:
                    os.remove(PASS_FILE)
                    return pw
            await asyncio.sleep(1)
    
    await client.start(phone=PHONE, code_callback=code_callback, password=password_callback)
    
    me = await client.get_me()
    print(f"Logged in as: {me.first_name} (@{me.username})")
    await client.disconnect()

asyncio.run(main())
```

## Alternative: PTY-Based Auth (Simpler)

When file-based IPC doesn't work (e.g., `code_callback` not being called), use PTY mode:

```python
# Start auth script in background with PTY
terminal(background=True, pty=True, command="python3 auth_script.py")

# Wait for "Enter the code" prompt
process(action="poll", session_id="...")

# Send code via submit
process(action="submit", data="12345", session_id="...")

# Check result
process(action="poll", session_id="...")
```

**When to use PTY-based vs file-based:**
- **PTY-based**: Simpler, works with any script using `input()`
- **File-based**: Better for production scripts that need to handle auth on every start

**Pitfall**: When using PTY-based auth, the code and password may be concatenated if sent too quickly. Wait for each prompt before submitting.

## Agent Workflow

1. Start script in background: `terminal(background=True)`
2. Wait for "Waiting for code..." output
3. Ask user for verification code
4. Write code: `echo "CODE" > /tmp/tg_code.txt`
5. Wait for "Waiting for password..." (if 2FA enabled)
6. Write password: `echo "PASSWORD" > /tmp/tg_pass.txt`
7. Confirm "Logged in as:" in output

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `AuthRestartError` | Telegram internal issue | Wait 30s, retry |
| `Invalid code` | Wrong code or expired | Ask user for new code |
| `Password hash invalid` | Wrong 2FA password | Ask user for correct password |
| `EOFError` | stdin not available | Use file-based IPC pattern |

## Session File Management

### Session File Locking (`database is locked`)

When multiple processes try to access the same `.session` SQLite database simultaneously, you get:
```
sqlite3.OperationalError: database is locked
```

**Cause**: Telethon uses SQLite for session storage. SQLite allows only one writer at a time. If a running bot holds a lock, a second process (auth script, another bot instance) cannot write.

**Fix sequence:**
```bash
# 1. Kill ALL running processes that use the session
pkill -f "spellcheck_userbot.py"
pkill -f "auth_spellcheck.py"

# 2. Wait for locks to release
sleep 2

# 3. Now run the auth/bot script
python3 auth_script.py
```

**Prevention**: Never run two processes with the same session file. Check for running instances before starting:
```bash
ps aux | grep -E "userbot|auth" | grep -v grep
```

### Read-Only Database (`attempt to write a readonly database`)

```bash
# Fix permissions
chmod 666 /path/to/session.session
chmod 666 /path/to/session.session-journal
```

**Cause**: Session file created with restrictive permissions, or copied from a read-only source.

### Corrupted Session File (`TypeNotFoundError`)

When Telethon crashes with `TypeNotFoundError: Could not find a matching Constructor ID`, the session file may be corrupted.

**Fix sequence:**
```bash
# 1. Find valid session files
find /root -name "*.session" -size +10k 2>/dev/null

# 2. Copy a valid one (larger = more likely has full auth data)
cp /path/to/valid.session /root/.hermes/scripts/my_userbot.session

# 3. Fix permissions
chmod 666 /root/.hermes/scripts/my_userbot.session
```

**If no valid session exists**: Must re-authenticate interactively (code + 2FA). Use PTY-based auth with `process(submit=code)`.

### Session File Path

Telethon creates the session file based on the `SESSION_NAME` parameter:
- `TelegramClient("my_bot", ...)` → creates `my_bot.session` in CWD
- `TelegramClient("/full/path/my_bot", ...)` → creates `/full/path/my_bot.session`

**Pitfall**: If you pass a relative path, the session file is created in whatever directory the script runs from. Always use absolute paths for reliability.
