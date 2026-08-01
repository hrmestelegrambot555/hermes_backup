# Telegram Game API Reference

Telegram Games are HTML5 games launched via `t.me/BotName?game=short_name`. They use a dedicated Bot API subset and must be registered with @BotFather.

## Registration with @BotFather

1. `/newgame` → select bot
2. Enter short name (3-30 chars, `a-zA-Z0-9_`) — becomes the URL identifier
3. Enter game description
4. Enter game URL (**must be HTTPS**)
5. Upload cover image (846×320 recommended)
6. Optional: upload GIF demo

Result: `t.me/YourBot?game=short_name`

## Bot API Methods

### sendGame

Sends a game message to a chat.

```python
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

await bot.send_game(
    chat_id=chat_id,
    game_short_name="deadzone",
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Play", callback_game={})]
    ])
)
```

### answerCallbackQuery (for game buttons)

When user taps the game button, answer with a URL to launch:

```python
@dp.callback_query(F.game)
async def game_callback(callback: types.CallbackQuery):
    await callback.answer(
        url=f"https://t.me/YourBot?game=deadzone"
    )
```

### setGameScore

Record a user's score. Returns the updated `InlineMessage` if bot sent the game in a private chat.

```python
result = await bot.set_game_score(
    user_id=user_id,
    score=1000,
    force=False,           # don't set if user already has higher
    disable_edit_message=True
)
```

Parameters:
- `force=True` — overwrites even higher scores
- `disable_edit_message=True` — don't edit the game message (returns None)
- `inline_message_id` — for inline mode games

### getGameHighScores

Get leaderboard for a user:

```python
scores = await bot.get_game_high_scores(
    user_id=user_id
)
# Returns list of GameHighScore objects
for entry in scores:
    print(f"Position {entry.position}: {entry.score}")
```

## Game URL Requirements

1. **HTTPS is mandatory** — Telegram will not load HTTP game URLs
2. **Must be publicly accessible** — localhost won't work
3. **No special headers needed** — standard web server works

### Quick Tunnel for Development

```bash
# localtunnel (no auth needed)
npm install -g localtunnel
lt --port 8080
# Returns: https://random-name.loca.lt

# Then register this URL with @BotFather
```

### Production Hosting Options

- GitHub Pages (free HTTPS)
- Netlify / Vercel (free HTTPS)
- Cloudflare Pages (free HTTPS)
- Cloudflare Workers (free HTTPS, upload single HTML via dash.cloudflare.com) — **BEST for single-file games**
- Any VPS with Let's Encrypt

**Cloudflare Workers quick deploy (worked perfectly in this session):**
1. Go to `dash.cloudflare.com` → Workers & Pages → Create application → Upload assets
2. Upload your `index.html` (must be named `index.html`)
3. Get instant permanent URL: `https://your-name.workers.dev`
4. Register this URL with @BotFather during `/newgame`

**Why Cloudflare Workers is ideal for Telegram Games:**
- Free tier is generous (100k requests/day)
- Single HTML file upload — no build step
- Permanent URL (unlike localtunnel which changes on restart)
- Global CDN + HTTPS out of the box
- No server management

### LocalTunnel Security Gate

When using localtunnel (`lt --port`), users see a security page requiring them to enter the server's IP address before proceeding.

**Tell users**: "Enter IP: YOUR_SERVER_IP"

**Pitfall**: Tunnels can go stale. If user reports "Bad Gateway", restart both the HTTP server and the tunnel.

### Persistent vs Ephemeral URLs

| Hosting | URL Behavior |
|---------|--------------|
| Cloudflare Workers/Pages | Permanent, permanent URL |
| GitHub Pages | Permanent |
| localtunnel | **Changes on every restart** — must re-register with @BotFather |

**Rule**: For production games, use permanent hosting (Cloudflare Workers, GitHub Pages, Netlify).

## Game HTML Structure

Games run in Telegram's built-in browser (WebView). Standard HTML5/Canvas/WebGL works.

```html
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
</head>
<body>
    <canvas id="game"></canvas>
    <script>
        // Telegram bridge
        const TG = window.Telegram?.WebApp;
        if (TG) {
            TG.ready();
            TG.expand();
        }
        
        // Haptic feedback
        function haptic(type) {
            TG?.HapticFeedback?.impactOccurred(type);
        }
        
        // Game logic here...
        
        // Send score back (optional)
        function submitScore(score) {
            // Via bot API call from your server
            fetch('https://your-server.com/score', {
                method: 'POST',
                body: JSON.stringify({ score, userId: TG?.initDataUnsafe?.user?.id })
            });
        }
    </script>
</body>
</html>
```

## Game vs Mini App: Key Differences

| Feature | Game (`?game=name`) | Mini App (`WebAppInfo`) |
|---------|--------------------|-----------------------|
| Registration | @BotFather `/newgame` | Just set URL |
| Launch | `sendGame` + `callback_game` | `WebAppInfo` button |
| Scores | Built-in `setGameScore` | Custom implementation |
| URL | `t.me/Bot?game=name` | Any HTTPS URL |
| Leaderboard | Built-in `getGameHighScores` | Custom |
| Best for | Simple games, leaderboards | Complex apps, tools |

## Common Pitfalls

1. **HTTP URL rejected**: @BotFather requires HTTPS for game URLs. Use localtunnel for dev.

2. **Game not loading**: Check that the HTTPS URL is accessible and returns valid HTML.

3. **callback_game vs callback_data**: Game buttons use `callback_game={}` (empty dict), NOT `callback_data="something"`. Mixing them up causes errors.

4. **answer() is required**: You MUST call `callback.answer()` when a game button is tapped, otherwise the loading spinner hangs forever.

5. **Score not updating**: `setGame_score` only works if the bot sent the game message. For inline mode, use `inline_message_id`.

6. **Multiple bot instances**: If two instances of the same bot run simultaneously, you get `TelegramConflictError`. Kill old processes before starting new ones.

7. **Game URL changes**: If you change the game URL after registration, use `/editgame` in @BotFather to update it.

8. **Game URL not asked during creation**: @BotFather may skip asking for the game URL during `/newgame`. If this happens, the game button will show a loading spinner but never open. **Fix**: Delete the game (`/deletegame`) and recreate it with `/newgame`, making sure to provide the HTTPS URL when prompted. There is NO separate `/setgameurl` command in BotFather.

9. **Game short name must match exactly**: The `game_short_name` parameter in `sendGame` must match EXACTLY what was registered in @BotFather. If BotFather shows `t.me/Bot?game=tetris`, use `tetris` — not `deadzone` or any other name. Wrong short name causes `Bad Request: wrong game short name specified`.

10. **aiogram `answer_game` may fail**: Even when the game is properly registered, aiogram's `answer_game` method can sometimes fail with "wrong game short name specified". If this happens, use the raw Telegram Bot API via `requests` library instead of aiogram for game-related operations.

11. **Multiple bot instances cause conflicts**: Running multiple instances of the same bot (e.g., after failed restarts) causes `TelegramConflictError: Conflict: terminated by other getUpdates request`. **Fix**: Kill ALL processes using the token before starting new ones: `pkill -9 -f "bot_script.py"` and verify with `ps aux | grep bot_script`. Old background processes accumulate across sessions.

12. **Ports get stuck after kills**: HTTP server ports (8080, 8081, etc.) may remain in `TIME_WAIT` state after killing the process. **Fix**: Use `fuser -k PORT/tcp` to force-kill, or use a different port number. Include port fallback logic in scripts.

13. **Environment variables not passed to child processes**: When running scripts via terminal/background tools, `os.environ.get()` may return empty strings even if the variable is set in the shell. **Fix**: Hardcode the value as fallback: `os.environ.get("KEY", "hardcoded-fallback-value")`.

14. **Mini App `web_app` buttons DON'T work in group chats**: The `web_app` field in `InlineKeyboardButton` is silently ignored in group chats — the button appears but does nothing when tapped. **Fix**: For group games, use the Game API (`callback_game={}` + `sendGame`) instead of Mini Apps. For groups, send a regular message with a deep link like `t.me/Bot?game=name`.

15. **localtunnel URLs change on restart**: Each time you run `lt --port X`, you get a different URL. Previous URL stops working. **Fix**: For persistent games, use Cloudflare Workers/Pages which give permanent URLs.

## Using Game/Mini App Bots in Groups

Game and Mini App bots work in groups but require extra setup:

1. **Disable privacy mode**: `@BotFather` → `/setprivacy` → Select bot → **Disable**
2. **Remove and re-add bot** to the group after changing privacy (critical — change only applies to new additions)
3. **Request `my_chat_member` updates** so the bot detects when it's added:
```python
params = {"allowed_updates": json.dumps(["message", "callback_query", "my_chat_member"])}
```

**Pitfall**: If the bot doesn't respond in groups but works in private chat, the #1 cause is privacy mode still being enabled. The bot must be removed and re-added after the change.
