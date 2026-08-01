# PTY Interactive Input Pattern for Hermes

## Problem
Scripts that call `input()` for SMS codes, passwords, or confirmation crash with `EOFError: EOF when reading a line` when run via `terminal(background=True)` without PTY.

## Solution: Use PTY mode

### Step 1: Start with PTY
```python
terminal(
    background=True,
    command="cd /root/.hermes/scripts && python3 gen_session_string.py",
    pty=True
)
# Returns session_id like "proc_abc123"
```

### Step 2: Poll for output
```python
process(action="poll", session_id="proc_abc123")
# Check if "Please enter the code you received:" appears
```

### Step 3: Submit input
```python
process(action="submit", session_id="proc_abc123", data="12345")
# data is the SMS code, automatically appended with Enter
```

### Step 4: Get final output
```python
process(action="poll", session_id="proc_abc123")
# Now shows SESSION_STRING output
```

## Complete Example: Telethon Session String Generation

```python
from hermes_tools import terminal, process

# Start interactive session generator
terminal(
    background=True,
    command="cd /root/.hermes/scripts && python3 gen_session_string.py",
    pty=True
)

# Wait for "Please enter the code" prompt
import time
time.sleep(3)  # Wait for script to start
result = process(action="poll", session_id="proc_xxx")

if "Please enter the code" in result.get("output", ""):
    # Submit SMS code
    process(action="submit", session_id="proc_xxx", data="YOUR_SMS_CODE")
    
    # Wait for output
    time.sleep(2)
    result = process(action="poll", session_id="proc_xxx")
    # Parse SESSION_STRING from output
```

## Alternative: Non-Interactive StringSession (Railway/VPS)

For background bots that don't need interaction:

```python
from telethon import TelegramClient
from telethon.sessions import StringSession

# Generate once with PTY, then use forever
client = TelegramClient(StringSession("SESSION_STRING_HERE"), API_ID, API_HASH)
await client.start()  # No phone parameter needed!
```

## Common Scripts That Need PTY
- `gen_session_string.py` — SMS code entry
- `python -c "input()"` — any interactive test
- `ssh user@host` — password entry (prefer key auth instead)
- Any script with `getpass.getpass()` — password prompts
