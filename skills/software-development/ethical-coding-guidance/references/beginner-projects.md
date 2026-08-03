# Beginner-Friendly Portfolio Projects

## 1. Telegram Bot: Polls & Reminders
**Skills:** async/await, python-telegram-bot, handlers, JobQueue
**Time:** 30-45 min

```python
# bot.py
from telegram import Update, Poll
from telegram.ext import Application, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Use /poll or /remind")

async def poll_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args) or "Favorite language?"
    options = ["Python", "JavaScript", "Rust", "Go"]
    await update.message.reply_poll(question, options)

async def remind_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /remind <seconds> <message>")
        return
    seconds = int(context.args[0])
    message = " ".join(context.args[1:])
    context.job_queue.run_once(
        lambda ctx: ctx.bot.send_message(update.effective_chat.id, f"⏰ {message}"),
        seconds,
        chat_id=update.effective_chat.id
    )
    await update.message.reply_text(f"Reminder set for {seconds}s")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("poll", poll_cmd))
    app.add_handler(CommandHandler("remind", remind_cmd))
    app.run_polling()

if __name__ == "__main__":
    main()
```

## 2. Price Scraper: Crypto/Gold/Currency
**Skills:** requests, BeautifulSoup, JSON, scheduling
**Time:** 20-30 min

```python
# scraper.py
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin,ethereum,solana", "vs_currencies": "usd,irr"}
    r = requests.get(url, params=params, timeout=10)
    return r.json()

def get_gold_price():
    url = "https://www.tgju.org/profile/geram18"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    # Parse logic here
    return {"gold_18k": "TODO"}

def main():
    data = {
        "timestamp": datetime.now().isoformat(),
        "crypto": get_crypto_prices(),
        "gold": get_gold_price()
    }
    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved to prices.json")

if __name__ == "__main__":
    main()
```

## 3. CLI Todo List (JSON Storage)
**Skills:** argparse, file I/O, JSON, classes, datetime
**Time:** 15-20 min
**Zero dependencies**

```python
# todo.py
import json, argparse, sys
from datetime import datetime
from pathlib import Path

FILE = Path("todos.json")

def load():
    if FILE.exists():
        return json.loads(FILE.read_text())
    return []

def save(todos):
    FILE.write_text(json.dumps(todos, ensure_ascii=False, indent=2))

def add(text):
    todos = load()
    todos.append({"id": len(todos)+1, "text": text, "done": False, "created": datetime.now().isoformat()})
    save(todos)

def list_todos():
    for t in load():
        status = "✅" if t["done"] else "⬜"
        print(f"{t['id']}. {status} {t['text']}")

def done(id_):
    todos = load()
    for t in todos:
        if t["id"] == id_:
            t["done"] = True
            break
    save(todos)

def delete(id_):
    todos = [t for t in load() if t["id"] != id_]
    for i, t in enumerate(todos, 1):
        t["id"] = i
    save(todos)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("list")
    a = sub.add_parser("add"); a.add_argument("text")
    d = sub.add_parser("done"); d.add_argument("id", type=int)
    x = sub.add_parser("del"); x.add_argument("id", type=int)
    args = p.parse_args()
    {"add": lambda: add(args.text),
     "list": list_todos,
     "done": lambda: done(args.id),
     "del": lambda: delete(args.id)}.get(args.cmd, p.print_help)()
```

## 4. Telegram Mini App (WebApp)
**Skills:** FastAPI, HTML/JS, Telegram WebApp API, HTTPS (ngrok)
**Time:** 30-45 min

```python
# webapp.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<!DOCTYPE html><html><head><title>Mini App</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>body{font-family:sans-serif;padding:20px;max-width:400px;margin:0 auto}
button{width:100%;padding:12px;font-size:16px;margin:8px 0;background:#2481cc;color:#fff;border:none;border-radius:8px}
button:active{background:#1a6ab8}</style></head><body>
<h2>🧮 Calculator</h2>
<input id="a" type="number" placeholder="Number 1" style="width:100%;padding:10px;margin-bottom:8px">
<input id="b" type="number" placeholder="Number 2" style="width:100%;padding:10px;margin-bottom:8px">
<button onclick="calc('+')">➕ Add</button>
<button onclick="calc('-')">➖ Subtract</button>
<button onclick="calc('*')">✖️ Multiply</button>
<button onclick="calc('/')">➗ Divide</button>
<div id="result" style="margin-top:16px;font-size:18px;font-weight:bold"></div>
<script>
function calc(op){const a=+document.getElementById('a').value,b=+document.getElementById('b').value;
let r;if(op==='+')r=a+b;else if(op==='-')r=a-b;else if(op==='*')r=a*b;else r=a/b;
document.getElementById('result').textContent='Result: '+r;
Telegram.WebApp.HapticFeedback.impactOccurred('light');}
</script></body></html>
"""

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 5. Legal Content Aggregator (RSS)
**Skills:** feedparser, apscheduler, database (sqlite3), Telegram bot
**Time:** 30-40 min

```python
# aggregator.py
import feedparser, sqlite3, requests
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

DB = "feeds.db"
BOT_TOKEN = "YOUR_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY, url TEXT UNIQUE, title TEXT, published TEXT
        )""")

def fetch_feed(url):
    feed = feedparser.parse(url)
    new_items = []
    with sqlite3.connect(DB) as conn:
        for entry in feed.entries[:5]:
            try:
                conn.execute("INSERT INTO items (url, title, published) VALUES (?, ?, ?)",
                           (entry.link, entry.title, entry.get("published", "")))
                new_items.append(entry)
            except sqlite3.IntegrityError:
                pass
    return new_items

def send_to_telegram(items):
    if not items: return
    text = "📰 New items:\n" + "\n".join(f"• {i.title}\n{i.link}" for i in items)
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                  json={"chat_id": CHAT_ID, "text": text})

def job():
    for url in ["https://example.com/rss", "https://another.com/feed"]:
        items = fetch_feed(url)
        send_to_telegram(items)

if __name__ == "__main__":
    init_db()
    sched = BlockingScheduler()
    sched.add_job(job, "interval", minutes=30)
    print("Running... Ctrl+C to stop")
    sched.start()
```

## Usage Instructions for All Projects
1. Create folder: `mkdir my-project && cd my-project`
2. Create venv: `python -m venv venv && source venv/bin/activate`
3. Install deps: `pip install python-telegram-bot requests beautifulsoup4 python-dotenv fastapi uvicorn feedparser apscheduler`
4. Copy code to file (e.g., `bot.py`)
5. Add `.env` with `BOT_TOKEN=your_token` (get from @BotFather)
6. Run: `python bot.py`
7. Commit to GitHub: `git init && git add . && git commit -m "Initial"`