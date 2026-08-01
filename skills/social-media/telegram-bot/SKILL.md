---
name: telegram-bot
description: "Telegram Bot API for channels and posting."
version: 1.0.0
author: hermes-agent
license: MIT
platforms: [linux, macos]
prerequisites:
  commands: [curl, jq]
  credentials: [telegram_bot_token]
metadata:
  hermes:
    tags: [telegram, bot, channel, messaging, news]
    homepage: https://core.telegram.org/bots/api
---

# Telegram Bot API Operations

Use this skill for:
- Reading public Telegram channels (web scraping or Bot API)
- Posting messages to channels via Bot API
- Setting up bots as channel admins
- Monitoring channels for news/content and forwarding

## Reading Public Channels

Public Telegram channels have a web preview at `https://t.me/s/channelname`.

### Method 1: Web Scraping (no bot needed)

```bash
curl -s "https://t.me/s/channelname" > /tmp/channel.html
```

Key HTML elements to parse:
- `tgme_widget_message_text` — message content (HTML with tags)
- `tgme_widget_message_date` — timestamp (datetime attribute)
- `tgme_widget_message_views` — view count
- `data-post="channel/id"` — post identifier

Extract text with Python:
```python
import re, html
with open("/tmp/channel.html") as f:
    content = f.read()
messages = re.findall(r'tgme_widget_message_text[^>]*>(.*?)</div>', content, re.DOTALL)
for msg in messages:
    clean = re.sub(r'<[^>]+>', '', msg).strip()
    clean = html.unescape(clean)
    if clean:
        print(clean)
        print("---")
```

### Method 2: Bot API (bot must be channel member)

```bash
curl -s "https://api.telegram.org/botTOKEN/getUpdates"
```

Note: `getUpdates` only returns messages sent AFTER the bot was added. For history, use web scraping.

## Posting to Channels

### Prerequisites
1. Bot must be added as **admin** to the channel
2. Bot must have **"Post Messages"** permission enabled

### Setup Steps (manual, by channel owner)
1. Open channel → tap channel name → Settings (gear icon)
2. Administrators → Add Admin
3. Search bot by username (e.g., `@your_bot_name`)
4. Enable "Post Messages" permission
5. Save

### Send Message

```bash
curl -s "https://api.telegram.org/botTOKEN/sendMessage" \
  -d "chat_id=@channelname" \
  -d "text=Your message here" \
  -d "parse_mode=HTML"
```

With numeric chat_id (channels use -100 prefix):
```bash
curl -s "https://api.telegram.org/botTOKEN/sendMessage" \
  -d "chat_id=-1001234567890" \
  -d "text=Your message here"
```

### Verify Bot Works

```bash
# Check bot info
curl -s "https://api.telegram.org/botTOKEN/getMe"

# Check bot is admin in channel
curl -s "https://api.telegram.org/botTOKEN/getChatMember" \
  -d "chat_id=@channelname" \
  -d "user_id=BOT_USER_ID"
```

## Common Pitfalls

1. **Bot not admin → 403 error**: `Forbidden: bot is not a member of the channel` or `can't post messages`. Fix: add bot as admin with Post Messages permission.

2. **PIL/Pillow cannot render Persian RTL text correctly** — characters appear reversed, disconnected, or as boxes. Don't use images for Persian/Farsi content. Use Telegram's native Markdown formatting instead (see "Sending Educational Content via Markdown" section).

3. **LocalTunnel security gate** — When users visit the tunnel URL, they see a security page asking for the server IP. Tell the user: "Enter this IP: `YOUR_SERVER_IP`" before they can access the tunnel.

4. **Proxy sources are unreliable in Iran** — Public Telegram channels for proxies are rare or private. Use GitHub sources like V2RayAggregator for reliable proxy lists. See `references/proxy-discovery-v2ray.md`.

### Group Chat Privacy Mode

By default, Telegram bots have **privacy mode enabled** — they only see:
- Commands starting with `/`
- Messages that explicitly mention the bot (`@botname`)
- Replies to the bot's messages

To receive ALL messages in groups:

1. **@BotFather** → `/setprivacy` → Select bot → **Disable**
2. **Remove bot from group** → **Re-add bot** (privacy change only applies to new additions)
3. Bot must receive `my_chat_member` updates to detect when added

```python
# In getUpdates, request my_chat_member updates
params = {"allowed_updates": json.dumps(["message", "callback_query", "my_chat_member"])}
```

**Pitfall**: Even after disabling privacy, some group types may not deliver all messages. Test by sending `/start` in the group and checking bot logs.

2. **Wrong chat_id format**: Channel usernames use `@channelname`. Numeric IDs start with `-100`. Use `getChat` to find the correct ID.

3. **Rate limits**: Telegram limits ~30 messages/second to different chats, ~20 messages/minute to same chat. Add delays for bulk operations.

4. **HTML entities in scraped content**: Web preview HTML encodes special characters. Use `html.unescape()` in Python or `sed` to decode.

5. **Web preview may be outdated**: The `/s/` preview shows recent messages but may not include all history. For older messages, paginate with `?before=MESSAGE_ID`.

6. **Token in curl commands**: When running in LLM sessions, avoid embedding tokens directly in commands visible to context. Use environment variables: `TOKEN=$BOT_TOKEN curl ...`

7. **Bot API cannot edit user messages**: Bots (using bot tokens) cannot edit messages sent by users. Only userbots (Telethon with real user account) can edit. Workaround: send a new message with the correction instead of trying to edit.

## Example: News Monitor + Forward Script

```bash
#!/bin/bash
# Monitor channel and forward important messages

SOURCE_CHANNEL="source_channel"
TARGET_CHANNEL="@target_channel"
BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
LAST_ID_FILE="/tmp/last_seen_id.txt"

# Initialize last seen ID
[ -f "$LAST_ID_FILE" ] || echo "0" > "$LAST_ID_FILE"
LAST_ID=$(cat "$LAST_ID_FILE")

# Fetch recent posts
curl -s "https://t.me/s/$SOURCE_CHANNEL" > /tmp/channel.html

# Extract and process messages
python3 << 'EOF'
import re, html, json, subprocess, os

with open("/tmp/channel.html") as f:
    content = f.read()

# Extract post IDs and text
posts = re.findall(r'data-post="' + os.environ['SOURCE_CHANNEL'] + r'/(\d+)".*?tgme_widget_message_text[^>]*>(.*?)</div>', content, re.DOTALL)

last_id = int(open("/tmp/last_seen_id.txt").read().strip())

for post_id, text in posts:
    post_id = int(post_id)
    if post_id <= last_id:
        continue
    
    clean = re.sub(r'<[^>]+>', '', text).strip()
    clean = html.unescape(clean)
    
    if not clean:
        continue
    
    # Define importance criteria here
    important_keywords = ["فوری", "breaking", "🚨", "‼️"]
    if any(kw in clean for kw in important_keywords):
        # Forward to target channel
        subprocess.run([
            "curl", "-s",
            f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/sendMessage",
            "-d", f"chat_id={os.environ['TARGET_CHANNEL']}",
            "-d", f"text={clean}",
            "-d", "parse_mode=HTML"
        ])
    
    # Update last seen
    with open("/tmp/last_seen_id.txt", "w") as f:
        f.write(str(post_id))
EOF
```

## Telethon Userbot Setup

For editing your own messages (e.g., auto-spellcheck), you need a **userbot** using Telethon. Bots cannot edit other users' messages.

### Private Messages Only

To skip groups and channels, check `event.is_private`:

```python
@client.on(events.NewMessage(outgoing=True))
async def handler(event):
    # Only check private messages (not groups or channels)
    if not event.is_private:
        return
    # ... rest of handler
```

### Authentication Challenge

Telethon's `client.start()` requires interactive input (verification code, 2FA password). When running in an agent session without stdin:

**Workaround: File-based IPC**

1. Run the auth script in background
2. Write code/password to temp files
3. Script polls the files until content appears

```python
async def code_callback():
    while True:
        if os.path.exists("/tmp/tg_code.txt"):
            with open("/tmp/tg_code.txt") as f:
                code = f.read().strip()
            if code:
                os.remove("/tmp/tg_code.txt")
                return code
        await asyncio.sleep(1)

# After starting script in background, from agent:
# echo "12345" > /tmp/tg_code.txt
```

Same pattern for 2FA password via `/tmp/tg_pass.txt`.

### Pitfalls

- **Telegram rate limits auth requests**: If code is rejected, Telegram may throttle. Wait 30s before retrying.
- **AuthRestartError**: Telegram internal issue — retry after a few seconds.
- **Session file**: First successful auth saves a `.session` file. Reuse it for subsequent runs (no re-auth needed).
- **2FA password required**: If account has two-factor authentication enabled, the password callback fires after code verification.
- **Must delete stale session file on auth failure**: `rm -f *.session*` before retry.
- **Session file locking**: If `database is locked` error occurs, kill ALL processes using that session file first (`pkill -f "script_name.py"`) then wait 2 seconds before retrying. SQLite only allows one writer at a time.
- **Read-only database**: Fix with `chmod 666 *.session*`. Common when files are copied from read-only sources.

### Telethon TypeNotFoundError Recovery

When Telethon crashes with `TypeNotFoundError: Could not find a matching Constructor ID for the TLObject that was supposed to be read with ID ...`, it means the Telegram API schema has been updated but the installed Telethon version doesn't recognize the new constructor.

**Fix sequence:**
```bash
# 1. Upgrade Telethon to latest
pip install --upgrade telethon

# 2. Search for valid session files elsewhere on disk
find /root -name "*.session" -size +10k 2>/dev/null

# 3. Copy a valid session (larger file = more likely has full auth data)
cp /path/to/valid.session /root/.hermes/scripts/hermes_spellcheck.session

# 4. Restart the bot
```

**Why this happens**: Telegram regularly updates their API schema. When the server sends a new constructor ID that the local Telethon library doesn't recognize, it throws this error. Upgrading Telethon fixes the schema mismatch. If the session file is also corrupted (e.g., from a previous crash mid-write), you need a valid one from a previous successful run.

**Pitfall**: If no valid session file exists anywhere on disk, you must re-authenticate interactively (code + 2FA). This cannot be done from an agent session without stdin — use the file-based IPC pattern described above.

## AI-Powered Spell Checking

For userbots that auto-correct messages, see:
- `references/persian-typo-dictionary.md` — Common Persian typos and ZWNJ patterns
- `references/ai-text-correction.md` — OpenRouter integration for AI-powered correction
- `references/persian-spellcheck-userbot.md` — Complete working pattern with elongation + swear word preservation

Two-tier approach: local dictionary for speed, AI fallback for complex errors.

**Key learning**: Preserve intentional elongations (سلامممم) and protected words (swear words, informal expressions). Check `has_elongation()` and `is_protected()` before applying any fixes.

## Telegram Mini Apps (Web Apps)

For creating interactive HTML/CSS/JS apps inside Telegram:
- `references/telegram-mini-apps.md` — Complete guide: bot setup, HTML side, hosting, data flow
- `references/telegram-mini-app-scores.md` — Score tracking pattern for Mini Apps (no built-in score API)

**Key learnings**:
- Mini apps MUST be hosted on a public URL (localhost won't work from mobile)
- Use `WebAppInfo` in `InlineKeyboardButton` to open the mini app
- Mini Apps have NO built-in score tracking — you need a custom backend server
- Include viewport meta tag for mobile: `<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">`

## Telegram Games API

For HTML5 games launched via `t.me/Bot?game=name` with built-in score tracking:
- `references/telegram-game-api.md` — @BotFather registration, sendGame, setGameScore, hosting, game vs mini-app comparison

**Key learnings**:
- Games must be registered with @BotFather via `/newgame`
- **Game URL is set DURING `/newgame` — there is NO separate `/setgameurl` command.** If you missed it, delete the game with `/deletegame` and recreate with `/newgame`.
- Game short names are case-sensitive (`Game1234` ≠ `game1234`)
- Game URL must be HTTPS — use `localtunnel` (`lt --port 8080`) for dev tunnels without auth
- Game buttons use `callback_game={}` (empty dict), NOT `callback_data`
- MUST call `callback.answer(url=...)` when game button tapped or loading spinner hangs
- `setGame_score` only works if bot sent the game message

### Games vs Mini Apps — When to Use Which

| Feature | Game API | Mini App |
|---------|----------|----------|
| Registration | Requires `/newgame` in BotFather | No registration needed |
| Score tracking | Built-in (`setGameScore`) | Custom backend required |
| Group support | Works in groups | `web_app` buttons don't work in groups |
| URL setup | Set during `/newgame` | Just point to any HTTPS URL |
| Link format | `t.me/Bot?game=name` | Custom (e.g. `t.me/Bot/app`) |

**Recommendation**: Use Mini Apps for simplicity. Use Game API only if you need built-in leaderboard (`setGameScore`).

### Common Game API Errors

- `Bad Request: wrong game short name specified` → Game not registered or wrong name
- `BUTTON_TYPE_INVALID` → `web_app` button used in group chat (not supported)
- `Conflict: terminated by other getUpdates request` → Multiple bot instances running — kill all others first

## Hermes Cron Job Configuration

Hermes cron jobs require either a model configured or `no_agent=True` for script-only execution.

### Script-Only Cron Jobs (no AI needed)

For simple scripts that don't need AI reasoning:

```python
# Create with no_agent=True and script parameter
cronjob(action='create', name='My Monitor', schedule='every 3h', 
        script='my_script.sh', no_agent=True, deliver='local')
```

**CRITICAL**: Scripts must be in `/data/.hermes/scripts/` (NOT `/root/.hermes/scripts/`). Copy scripts to the correct path:
```bash
cp /root/.hermes/scripts/myscript.py /data/.hermes/scripts/
```

Reference by filename only: `script='myscript.py'` (no absolute path).

### AI-Powered Cron Jobs

For jobs that need AI reasoning, configure a model:
```python
cronjob(action='update', job_id='xxx', 
        model={'model': 'google/gemma-4-26b-a4b-it:free', 'provider': 'openrouter'})
```

**Pitfall**: Without model configuration, cron jobs fail with: `RuntimeError: Cron job has no model configured`

### Common Cron Pitfalls

- `Script not found` → Script not in `/data/.hermes/scripts/` or wrong filename
- `Missing Authentication header` → Model provider not configured or API key missing
- Jobs run in isolated sessions — no access to parent session's environment variables
- **Script path issue**: Scripts must be in `/data/.hermes/scripts/` (NOT `/root/.hermes/scripts/`). Always copy: `cp /root/.hermes/scripts/myscript.py /data/.hermes/scripts/`

## File Delivery Workarounds

When you can't send files directly via Telegram (e.g., from agent session), use temporary file hosting:

### tmpfiles.org (recommended)
```bash
# Upload file
curl -s --max-time 30 -F "file=@/path/to/file.zip" https://tmpfiles.org/api/v1/upload
# Returns: {"status":"success","data":{"url":"https://tmpfiles.org/XXXX/file.zip"}}
```

**Pitfall**: Links are temporary — tell user to download immediately.

### Alternatives (if tmpfiles.org is down)
- `file.io` — may timeout on large files
- `transfer.sh` — often unreliable
- `0x0.st` — currently disabled due to spam

**Pattern**: Upload → get URL → send URL to user in chat.

## Sending Educational Content via Markdown

For Persian/Farsi educational content (or any text-heavy content), use Telegram's Markdown formatting instead of images. This renders Persian text correctly and looks professional.

### Format Template for Tutorials

```python
lessons = [
"""🐍 *درس ۱: عنوان*
━━━━━━━━━━━━━━━

*توضیح فارسی:*

```python
code_example()
```

*خروجی:*
```
output
```

💡 *نکته مهم:* ...""",
]

for lesson in lessons:
    requests.post(f"{API}/sendMessage", json={
        "chat_id": CHAT_ID,
        "text": lesson,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    })
```

### Markdown Features for Education
- `*bold*` for key terms and headers
- `code blocks with language` for syntax-highlighted code
- `inline code` for function names and variables
- `💡` emojis for tips and notes
- Tables with `|` for comparisons

### Why Not Images for Persian Content
PIL/Pillow cannot render Persian RTL text correctly — characters appear reversed or as boxes. Telegram's native Markdown formatting handles Persian text perfectly. See `references/pil-persian-limitation.md` for details.

## Process Management for Bots

When running multiple bots/processes, avoid zombie processes and port conflicts.

### Kill All Instances Before Starting

```bash
# Kill by process name
pkill -9 -f "game_bot.py"

# Kill by port
fuser -k 8080/tcp

# Check for zombies
ls /proc/*/cmdline 2>/dev/null | xargs grep -l "bot_name"
```

### Detect Running Processes (no pgrep needed)

```python
import os
def is_running(name):
    for pid in os.listdir('/proc'):
        try:
            if name in open(f'/proc/{pid}/cmdline').read():
                return True
        except: pass
    return False
```

### Port Conflict Pattern

```bash
# Always kill port before starting server
fuser -k 8080/tcp 2>/dev/null
sleep 1
python3 -m http.server 8080 &
```

**Pitfall**: `fuser` may not be available. Fallback: `kill $(lsof -t -i:8080)` or scan `/proc/*/fd` symlink targets.

## LocalTunnel Security Gate

When using `lt` (localtunnel) for HTTPS tunnels, users see a security page requiring them to enter the server IP before proceeding.

**User experience**: Page shows "You are about to visit..." with an IP input field. User must type the server IP (e.g. `152.55.176.2`) and click Continue.

**Tell the user**: "IP address to enter: `YOUR_SERVER_IP`"

**Pitfall**: Tunnels can go stale. If user reports "Bad Gateway", restart both the HTTP server and the tunnel.

See `references/localtunnel-security-gate.md` for full details.

## Forwarding Telegram CDN Images

Images from `cdn4.telesco.pe` can't be sent directly via Bot API — must download first:
- `references/telegram-cdn-images.md` — Complete pattern for download+upload, filtering emoji images

## Colored Inline Buttons (aiogram)

For bots with colored inline keyboard buttons, see:
- `references/aiogram-colored-buttons.md` — ButtonStyle enum (PRIMARY, SUCCESS, DANGER)
- `references/vpn-proxy-bot-pattern.md` — Complete VPN/proxy bot template with colored buttons

**IMPORTANT**: Enum names are UPPERCASE: `ButtonStyle.PRIMARY`, `ButtonStyle.SUCCESS`, `ButtonStyle.DANGER` (not lowercase — causes AttributeError).

## Cloud Deployment (Railway, Render, etc.)

For deploying bots to cloud platforms with 24/7 uptime:
- `references/railway-deployment.md` — Railway deployment: files needed, pitfalls, free tier limits
- `templates/spellcheck-railway/` — Complete spellcheck bot template for Railway deployment

**Key pattern**: Create a GitHub repo with `main.py`, `requirements.txt`, `railway.json`. Deploy via Railway dashboard. For Telethon userbots, use **session strings** (not `.session` files) — generate locally with `gen_session_string.py` and set as `SESSION_STRING` environment variable.

## Service Monitoring & Self-Healing

For keeping Telegram bots running 24/7:
- `references/service-monitoring.md` — Cron-based health checks, auto-restart patterns, port conflict resolution

## Proxy Discovery & V2Ray Configuration

For setting up proxies in restricted environments (Iran, etc.):
- `references/proxy-discovery-v2ray.md` — Complete guide: finding proxies, extracting VMess/SS/Trojan, testing latency, creating V2Ray/Clash configs

**Key pattern**: Create a monitor script that checks process existence via `/proc/*/cmdline` (not `pgrep` which may not be available), restarts if stopped, and run it via Hermes cron every 3 hours.

## OpenRouter Free Models

For AI-powered features using free models:
- `references/openrouter-free-models.md` — How to discover and use free models
- `references/openrouter-rate-limits.md` — Rate limit handling and graceful degradation

**CRITICAL**: Free tier has TWO rate limits:
1. **Short-term throttle** (~5 min cooldown) — from too many rapid requests
2. **Daily cap** (`free-models-per-day`) — resets at midnight UTC, NOT after 5 minutes

The daily cap error includes `X-RateLimit-Reset` (Unix ms) in metadata. Calculate remaining wait:
```python
reset_ms = error["metadata"]["headers"]["X-RateLimit-Reset"]
remaining = datetime.fromtimestamp(reset_ms/1000) - datetime.now()
```

**Pitfall**: When daily limit is hit, ALL free models fail simultaneously. Switching models does NOT help. Either wait until midnight UTC or add $10 credits.

## Bale App Compatibility

The Bale messaging app (Iranian) has a Bot API similar to Telegram's:
- `references/bale-bot-api.md` — Complete Bale Bot API reference with examples

**Key learning**: aiogram's `base_url` parameter doesn't work reliably with Bale. Use raw requests library for Bale bot development.

## Security Notes

- Bot tokens grant full access to the bot's capabilities — treat as secrets
- Never log tokens in plain text or expose in LLM context
- Use environment variables for tokens in scripts
- Rotate tokens if compromised via @BotFather
