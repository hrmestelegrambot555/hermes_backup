# Railway Deployment Guide for Telegram PHP Bot

## Prerequisites
- GitHub account
- Railway account (railway.app)
- Bot token from @BotFather

## Step 1: Prepare Repository

```bash
# Initialize git
git init
git add .
git commit -m "Initial commit: Telegram PHP uploader bot"

# Create GitHub repo (via web or CLI)
gh repo create telegram-uploader-bot --public --push --source=.
```

## Step 2: Railway Project Setup

1. Go to https://railway.app
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repository
4. Railway auto-detects Dockerfile

## Step 3: Environment Variables

In Railway Dashboard → **Variables**, add:

| Variable | Value | Notes |
|----------|-------|-------|
| `BOT_TOKEN` | `123456:ABC...` | From @BotFather |
| `BOT_USERNAME` | `MyBot` | Without @ |
| `ADMIN_ID` | `123456789` | Your user ID |
| `WEBHOOK_URL` | `https://xxx.up.railway.app/webhook.php` | Get after first deploy |
| `MAX_FILE_SIZE_GB` | `2` | Telegram bot limit |
| `MAX_DURATION_MIN` | `60` | Max video duration |
| `DAILY_LIMIT_PER_USER` | `10` | Rate limit |

## Step 4: First Deploy & Get Domain

1. Click **Deploy**
2. Wait for build (installs PHP, ffmpeg, yt-dlp, composer deps)
3. After deploy, go to **Settings** → **Domains**
4. Copy the generated domain (e.g., `https://uploader-bot-production.up.railway.app`)

## Step 5: Set Webhook

```bash
# Replace with your actual token and domain
curl "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<YOUR_DOMAIN>/webhook.php"
```

Expected response:
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

## Step 6: Test

1. Open Telegram, find your bot
2. Send `/start`
3. Send a YouTube link
4. Select quality → wait for download → receive file

## Troubleshooting

### Build Fails: Missing Dependencies
Ensure Dockerfile has all system packages:
```dockerfile
RUN apt-get update && apt-get install -y \
    ffmpeg python3 python3-pip sqlite3 libsqlite3-dev \
    && pip3 install --no-cache-dir yt-dlp
```

### Webhook Not Working
1. Check Railway logs for PHP errors
2. Verify `WEBHOOK_URL` matches deployed domain exactly
3. Ensure webhook.php returns 200 OK within 30s

### Large File Uploads Fail
- Telegram bot limit: 2GB
- Increase PHP limits in webhook.php:
```php
ini_set('upload_max_filesize', '2048M');
ini_set('post_max_size', '2048M');
ini_set('memory_limit', '512M');
ini_set('max_execution_time', 300);
```

### Database Locked Errors
SQLite with WAL mode handles concurrency, but for high traffic:
```php
$pdo->exec('PRAGMA journal_mode=WAL;');
$pdo->exec('PRAGMA busy_timeout=5000;');
```

### yt-dlp Fails on Some Videos
Update yt-dlp in Dockerfile:
```dockerfile
RUN pip3 install --no-cache-dir --upgrade yt-dlp
```

## Monitoring

### Railway Logs
- **Deployments** tab → Click deployment → **Logs**
- Real-time stdout/stderr from PHP server

### Health Check Endpoint
Add to webhook.php:
```php
if (isset($_GET['health'])) {
    echo 'OK';
    http_response_code(200);
    exit;
}
```
Then Railway can ping `/webhook.php?health`

## Custom Domain (Optional)

1. Railway → Settings → Domains → **Custom Domain**
2. Add CNAME record in DNS
3. Update webhook URL and re-set webhook

## Cost Optimization

| Resource | Free Tier | Notes |
|----------|-----------|-------|
| CPU | 500h/mo | Enough for moderate use |
| RAM | 1GB | PHP + ffmpeg fit |
| Network | 100GB/mo | Video uploads count |
| Storage | 1GB | DB + temp files |

## Redeployment

Push to GitHub → Railway auto-deploys → webhook persists (same domain).

```bash
git add . && git commit -m "Update" && git push
```