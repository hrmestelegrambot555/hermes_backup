# Hermes Spell-Check Userbot - Railway Deploy

## Quick Start

### 1. Generate Session String (Local)
```bash
pip install telethon==1.44.0
python3 gen_session_string.py
```
Copy the output string.

### 2. Upload to GitHub
```bash
git init
git add .
git commit -m "spellcheck bot"
git remote add origin https://github.com/YOUR_USER/spellcheck-bot.git
git push -u origin main
```

### 3. Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select your repo

### 4. Set Environment Variables
| Variable | Value |
|----------|-------|
| `API_ID` | `31844510` |
| `API_HASH` | `b1722fa9a615a9cdf394ee3886765b97` |
| `SESSION_STRING` | (from step 1) |
| `OPENROUTER_API_KEY` | `sk-or-v1-...` |

### 5. Update Dictionary
Replace `persian_dict.json` with your latest version and redeploy.

## Files
- `spellcheck_userbot.py` — Main bot script
- `gen_session_string.py` — Session string generator
- `persian_dict.json` — Typo dictionary (44MB)
- `requirements.txt` — Python dependencies

## Notes
- First deployment needs a valid session string
- Dictionary loads in ~0.9s at startup
- AI is optional — local fixes work without API key
