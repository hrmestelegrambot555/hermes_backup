# Telegram Mini Apps (Web Apps) Reference

Mini Apps (formerly Telegram Web Apps) are HTML/CSS/JS applications that run inside Telegram's built-in browser. They open from inline keyboard buttons.

## Architecture

```
Bot (aiogram) → InlineKeyboardButton with WebAppInfo → Telegram opens WebView → Your hosted HTML/CSS/JS
```

## Bot Side (aiogram)

```python
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="🎮 Play Game",
        web_app=WebAppInfo(url="https://your-domain.com/app")
    )]
])

await message.answer("Click to play!", reply_markup=keyboard)
```

## HTML Side

```html
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
</head>
<body>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script>
        Telegram.WebApp.ready();
        Telegram.WebApp.expand();
        
        // Get user data
        const user = Telegram.WebApp.initDataUnsafe?.user;
        // Send data back to bot
        Telegram.WebApp.sendData(JSON.stringify({action: 'score', value: 100}));
    </script>
</body>
</html>
```

## Hosting Requirements

1. **Must be publicly accessible** — `localhost` won't work from mobile
2. **HTTPS preferred** — Telegram may warn on HTTP
3. **Port must be standard** (80/443) or accessible

### Quick Python Server

```python
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/path/to/html", **kwargs)

server = HTTPServer(('0.0.0.0', 8080), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
```

## Receiving Data from Mini App

### Method 1: sendData → Bot Webhook/Polling

```python
@dp.message()
async def handle_miniapp_data(message: types.Message):
    if message.web_app_data:
        data = json.loads(message.web_app_data.data)
        await message.answer(f"Score: {data.get('score', 0)}")
```

### Method 2: HTTP API (if mini app calls your server)

```javascript
fetch('https://your-server.com/api/score', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({score: 100, userId: user.id})
});
```

## Common Pitfalls

1. **localhost doesn't work**: Mini apps must be served from a public URL. Use your server's public IP or a tunnel (ngrok, cloudflared).

2. **HTTP vs HTTPS**: Telegram may block HTTP WebView on some platforms. Use HTTPS in production.

3. **Viewport meta tag**: Always include `<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">` to prevent zoom issues on mobile.

4. **Touch events**: Use `touchstart`/`touchend` for better mobile responsiveness instead of just `click`.

5. **Haptic feedback**: Telegram WebApp API supports `Telegram.WebApp.HapticFeedback.impactOccurred('medium')` for tactile responses.

6. **Theme colors**: Use `Telegram.WebApp.backgroundColor`, `Telegram.WebApp.textColor` etc. for consistent theming with Telegram's dark/light mode.

7. **Close behavior**: Call `Telegram.WebApp.close()` when done, or user has to manually close the WebView.

8. **web_app buttons DON'T work in group chats**: The `web_app` field in `InlineKeyboardButton` is silently ignored in group chats — the button renders but does nothing when tapped. **Fix**: For group interactions, use regular inline buttons with `callback_data` or `callback_game` instead. For games in groups, use the Game API (`sendGame` + `callback_game`).

9. **localtunnel URLs change on restart**: `lt --port X` generates a new random URL each time. Previous URL dies. **Fix**: For persistent deployments, use Cloudflare Workers/Pages (free, permanent URLs). Upload `index.html` via dash.cloudflare.com → Workers & Pages → Create → Upload assets.

10. **Environment variables may not propagate**: When running scripts via agent terminal tools, `os.environ.get()` may return empty strings. **Fix**: Hardcode fallback values: `os.environ.get("KEY", "fallback-value")`.
