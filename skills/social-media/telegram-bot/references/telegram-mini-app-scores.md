# Mini App Score Tracking Pattern

When using Mini Apps (not Game API), there's no built-in score system. You need a custom backend.

## Architecture

```
Mini App (browser) → POST /score → Your Server → Telegram Bot API (setGameScore)
```

## Score Server (Python)

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests, json, threading

BOT_TOKEN = "your_token"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
scores = {}  # Use a database in production

class ScoreHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        user_id = str(data.get('user_id'))
        score = data.get('score', 0)
        username = data.get('username', 'Unknown')
        
        # Keep highest score
        if user_id not in scores or score > scores[user_id].get('score', 0):
            scores[user_id] = {'score': score, 'username': username}
        
        # Set score via Telegram API
        requests.post(f"{API_URL}/setGameScore", json={
            "user_id": int(user_id), "score": score,
            "force": False, "disable_edit_message": True
        }, timeout=10)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'ok': True}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args): pass

server = HTTPServer(('0.0.0.0', 8081), ScoreHandler)
threading.Thread(target=server.serve_forever, daemon=True).start()
```

## Game Side (JavaScript)

```javascript
// In your game's gameOver() function:
function submitScore(score) {
    const user = Telegram?.WebApp?.initDataUnsafe?.user;
    if (!user) return;
    
    fetch('https://your-server.com/score', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user_id: user.id,
            username: user.username || user.first_name,
            score: score
        })
    });
}
```

## Bot Command for Leaderboard

```python
def send_scoreboard(chat_id):
    top = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)[:10]
    medals = ["🥇", "🥈", "🥉"]
    text = "🏆 **تالار افتخارات**\n\n"
    for i, (uid, data) in enumerate(top):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} **{data['username']}**: {data['score']}\n"
    
    requests.post(f"{API_URL}/sendMessage", json={
        "chat_id": chat_id, "text": text, "parse_mode": "Markdown"
    })
```

## Pitfalls

1. **CORS headers required**: Browser requests from Mini App need `Access-Control-Allow-Origin: *` on your server
2. **HTTPS required for score server**: Mini App runs in HTTPS context, can't POST to HTTP (mixed content blocked)
3. **Use `localtunnel` for dev**: `lt --port 8081` gives free HTTPS tunnel
4. **`setGameScore` only works if bot sent the game**: If game was shared via link, score won't update the message
5. **Score server must be reachable from Mini App browser**: localhost won't work from mobile — use tunnel or deploy
