---
name: fastapi-htmx-web-apps
description: "Build FastAPI+HTMX apps: dark theme, RTL, API fallbacks."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [fastapi, htmx, jinja2, web, dark-theme, rtl, translator]
    related_skills: [claude-design, popular-web-designs]
---

# FastAPI + HTMX Web Apps

Build modern, responsive web applications with FastAPI backend, HTMX frontend, and Jinja2 templates. Includes dark theme, RTL support, multiple API fallbacks, history, keyboard shortcuts.

## Quick Start

```bash
pip install fastapi uvicorn jinja2 python-multipart requests
```

```python
# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/translate")
async def translate(text: str = Form(...), source: str = Form("auto"), target: str = Form("en")):
    for name, func in [("Google", google_translate), ("MyMemory", mymemory_translate)]:
        result = await func(text, source, target)
        if result: return {"translated": result, "backend": name}
    return {"translated": text, "backend": "failed"}
```

## Dark Theme CSS Variables

```css
:root {
  --bg: #0f0f1a;
  --bg-elevated: #161622;
  --card: #1c1c2e;
  --card-hover: #24243e;
  --border: #2d2d44;
  --accent: #a855f7;
  --accent-glow: #c084fc;
  --text: #f1f5f9;
  --text-dim: #71718a;
  --success: #22c55e;
  --error: #ef4444;
}
```

## RTL Support

```html
<html lang="fa" dir="rtl">
```

```css
[dir="rtl"] .lang-select { padding-left: 48px; padding-right: 16px; }
```

## Jinja2 Template Cache Fix

**Error:** `TypeError: unhashable type: 'dict'` from Jinja2 template caching when iterating dicts in templates.

**⚠️ PITFALL:** `templates.env.cache = {}` does NOT reliably fix this. Even with cache cleared, passing dicts as template context variables triggers the same error in Starlette's `TemplateResponse` because cache key generation includes context variables. `import jinja2; jinja2.environment.Environment.cache = {}` also fails. `auto_reload=True` is not a valid kwarg for Jinja2Templates.

**Reliable Fix:** Abandon Jinja2 templates entirely. Use string replacement (see section below).

**If you must use Jinja2:** Pass only flat strings/lists, never dicts. Use `.items()` in the template and pass the result as a list of tuples:
```python
# Instead of: {"languages": LANGUAGES}  ← causes unhashable dict
# Do: {"lang_pairs": list(LANGUAGES.items())}  ← list of tuples, hashable
```

## Alternative: String Replacement Templates (No Jinja2)

**When Jinja2 cache issues persist**, use simple string replacement:

```python
# Load template at startup
with open("templates/index.html", "r") as f:
    HTML_TEMPLATE = f.read()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    html = HTML_TEMPLATE
    # Replace placeholders
    src_options = ''.join(f'<option value="{code}"{" selected" if code=="auto" else ""}>{name}</option>'
                          for code, name in LANGUAGES.items())
    tgt_options = ''.join(f'<option value="{code}"{" selected" if code=="fa" else ""}>{name}</option>'
                          for code, name in LANGUAGES.items())
    html = html.replace("{{SOURCE_OPTIONS}}", src_options)
    html = html.replace("{{TARGET_OPTIONS}}", tgt_options)
    return HTMLResponse(html)
```

**Template uses placeholders:**
```html
<select id="sourceLang">{{SOURCE_OPTIONS}}</select>
<select id="targetLang">{{TARGET_OPTIONS}}</select>
```

**Benefits:** Zero dependencies, no cache issues, faster, simpler debugging.

## Session String Auth for Railway

**Never use phone+code on Railway.** Generate session string locally, set as env var.

```python
# gen_session.py
from telethon.sync import TelegramClient
API_ID = 31844510
API_HASH = "your_hash"
PHONE = "+19432518923"
with TelegramClient('session_gen', API_ID, API_HASH) as client:
    client.start(phone=PHONE)
    print(client.session.save())
```

```python
# In app
SESSION_STRING = os.environ.get("SESSION_STRING")
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
```

**Railway env vars:**
```
API_ID=31844510
API_HASH=your_hash
SESSION_STRING=1AgAOMTQ5...
OPENROUTER_API_KEY=sk-or-v1-...
```
## Multiple API Fallbacks

```python
async def translate(text, source, target):
    for name, func in TRANSLATORS:
        try:
            result = await func(text, source, target)
            if result and result != text:
                return result, name
        except: continue
    return text, "failed"
```

## Form Data Encoding Fix (Persian/Arabic Text)

**Problem:** FastAPI form data mangles RTL text → `Ø³ÙØ§Ù...`

**Fix:** Decode latin1 → utf-8 before processing

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

## History Persistence

```python
HISTORY_FILE = Path.home() / ".app_history.json"
HISTORY_LIMIT = 100

def add_history(item):
    history = load_history()
    history.insert(0, item)
    save_history(history[:HISTORY_LIMIT])
```

## Keyboard Shortcuts

```javascript
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.shiftKey) {
    if (e.key === 'C') copyBtn.click();
    if (e.key === 'X') clearBtn.click();
    if (e.key === 'S') swapBtn.click();
  }
});
```

## Responsive Layout

```css
main { display: grid; grid-template-columns: 1fr 380px; gap: 24px; }
@media (max-width: 1024px) {
  main { grid-template-columns: 1fr; }
  .history-panel { order: -1; position: static; }
}
```

## Headless Server Dependencies

```bash
apt-get install -y libgl1 libegl1 libfontconfig1 libglib2.0-0 libdbus-1-3 \
  libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
  libxcb-render-util0 libxcb-shape0 libxcb-sync1 libxcb-xfixes0 \
  libxcb-xinerama0 libxcb-xinput0 libxcb1 libxkbcommon0
```

## Railway Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Port handling (Railway sets `PORT` env var):**
```python
import os
port = int(os.environ.get("PORT", 8080))
uvicorn.run(app, host="0.0.0.0", port=port)
```

## Cloudflare Workers Deployment (Single-File)

When Railway is overkill or you need free global edge deployment, use Cloudflare Workers.

**Single-file pattern** — all HTML/CSS/JS inline in one `index.js`:

```javascript
// index.js — Cloudflare Worker
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // API endpoint
    if (url.pathname === '/api/translate' && request.method === 'POST') {
      const body = await request.text();
      const params = new URLSearchParams(body);
      const result = await translate(params.get('text'), params.get('source'), params.get('target'));
      return new Response(JSON.stringify(result), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      });
    }

    // Serve HTML page (all inline)
    return new Response(HTML_PAGE, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  }
};

async function translate(text, source, target) {
  try {
    const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${source}&tl=${target}&dt=t&q=${encodeURIComponent(text)}`;
    const r = await fetch(url);
    const data = await r.json();
    if (data && data[0]) return { translated: data[0][0][0], backend: 'Google' };
  } catch (e) {}
  return { translated: 'Translation failed', backend: 'Error' };
}

const HTML_PAGE = `<!DOCTYPE html><html>...</html>`;  // Full HTML inline
```

**Deploy steps:**
1. `wrangler init translator` or paste in Cloudflare Dashboard → Workers → Create Worker
2. Paste `index.js` → Save & Deploy
3. Free tier: 100K requests/day

**Benefits:** Zero config, no server, global CDN, free tier, instant deploy.

## Google Translate Free API

**Endpoint:** `https://translate.googleapis.com/translate_a/single?client=gtx`

**Response parsing:** `result[0][0][0]` = translated text

```python
import requests

def google_translate(text, source="fa", target="en"):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {"client": "gtx", "sl": source, "tl": target, "dt": "t", "q": text}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 200:
        result = r.json()
        if result and result[0] and result[0][0]:
            return result[0][0][0]  # ← translated text here
    return None
```

**Note:** `requests.get(url, params=...)` handles URL encoding automatically. Do NOT use `urllib.parse.quote()` with `params=` — it double-encodes.

## Files from This Session

- `translator_web.py` — FastAPI backend with 3 translation backends
- `templates/index.html` — Dark theme UI with HTMX, particles, animations
- `cf_translator.js` — Cloudflare Worker single-file version
- Deployed: `https://github.com/hrmestelegrambot555/hermes-spellcheck`