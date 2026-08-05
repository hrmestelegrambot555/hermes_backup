---
name: telegram-php-bot-development
description: Build Telegram bots in PHP with yt-dlp, SQLite, Railway.
category: software-development
---

# Telegram PHP Bot Development

Build Telegram bots in PHP with modern tooling: `longman/telegram-bot` for Bot API, `yt-dlp`/`ffmpeg` for media processing, SQLite for persistence, Railway for deployment.

## When to Use
- Building a Telegram bot in PHP (not Python)
- Need media download/convert/upload pipeline (YouTube, Instagram, Twitter, TikTok)
- Want webhook-based deployment on Railway/Render/Fly.io
- Need persistent user data, rate limiting, admin commands

## Architecture Overview

```
User → Telegram → Webhook (PHP) → yt-dlp/ffmpeg → Telegram API → User
                    ↓
              SQLite Database
```

### Core Components
| Component | Purpose |
|-----------|---------|
| `longman/telegram-bot` | Telegram Bot API wrapper (webhook + commands) |
| `yt-dlp` | Universal media downloader (1000+ sites) |
| `ffmpeg` | Transcode, compress, extract audio |
| `vlucas/phpdotenv` | Environment config |
| SQLite (PDO) | Zero-config persistence |

## Project Structure

```
my-bot/
├── composer.json
├── config.php          # Config from $_ENV
├── .env.example
├── Procfile            # web: php -S 0.0.0.0:$PORT webhook.php
├── Dockerfile          # Railway deployment
├── database/
│   └── schema.sql
├── src/
│   ├── Database.php    # PDO wrapper + user/download CRUD
│   ├── Downloader.php  # yt-dlp wrapper
│   ├── Converter.php   # ffmpeg wrapper
│   ├── TelegramBot.php # longman/telegram-bot wrapper
│   └── Bot.php         # Main logic: commands, callbacks, flow
├── webhook.php         # Entry point
└── tmp/                # Temp files (auto-clean)
```

## Key Patterns

### Webhook Entry Point (`webhook.php`)
```php
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();
$config = require __DIR__ . '/config.php';

$bot = new Bot($config);
$update = json_decode(file_get_contents('php://input'), true);
if ($update) { $bot->handleUpdate($update); }
http_response_code(200);
```

### Database (SQLite + WAL mode)
```php
$pdo = new PDO("sqlite:{$dbPath}", null, null, [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
]);
$pdo->exec('PRAGMA journal_mode=WAL;');
$pdo->exec('PRAGMA busy_timeout=5000;');
```

### yt-dlp Wrapper
```php
$cmd = "yt-dlp --dump-json --no-download " . escapeshellarg($url);
$output = shell_exec($cmd);
$data = json_decode($output, true); // title, duration, formats, extractor

$cmd = "yt-dlp -f 'bestvideo[height<=720]+bestaudio' -o 'tmp/%(id)s.%(ext)s' " . escapeshellarg($url);
shell_exec($cmd);
```

### ffmpeg Wrapper
```php
// MP3 extraction
$cmd = "ffmpeg -y -i " . escapeshellarg($in) . " -vn -acodec libmp3lame -ab 192k " . escapeshellarg($out);

// Compress video
$cmd = "ffmpeg -y -i " . escapeshellarg($in) . " -vf scale=1280:720 -c:v libx264 -crf 23 " . escapeshellarg($out);
```

### Telegram Bot Wrapper (longman/telegram-bot)
```php
$telegram = new Longman\TelegramBot\Telegram($token, $username);
$telegram->addCommandsPaths([__DIR__ . '/Commands']);

Request::sendMessage(['chat_id' => $id, 'text' => $text, 'parse_mode' => 'Markdown']);
Request::sendVideo(['chat_id' => $id, 'video' => new CURLFile($path)]);
Request::editMessageText(['chat_id' => $id, 'message_id' => $mid, 'text' => $new]);
```

### Callback Query Flow (Inline Keyboards)
```php
// Button: callback_data => "dl_123_720p"
$parts = explode('_', $data); // ["dl", "123", "720p"]
$downloadId = (int)$parts[1];
$quality = $parts[2];
$isAudio = $quality === 'mp3';
```

## Railway Deployment

1. Push to GitHub
2. Railway → New Project → Deploy from GitHub
3. Set Environment Variables:
   - `BOT_TOKEN`, `BOT_USERNAME`, `ADMIN_ID`
   - `MAX_FILE_SIZE_GB=2`, `MAX_DURATION_MIN=60`, `DAILY_LIMIT_PER_USER=10`
4. Railway builds Dockerfile, exposes `$PORT`
5. Set webhook: `curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<DOMAIN>/webhook.php"`

## Local Development Setup

```bash
# Install dependencies
composer install --no-dev --optimize-autoloader

# Run migrations
sqlite3 database/bot.sqlite < database/schema.sql

# Start dev server
php -S localhost:8000 webhook.php
```

## Common Pitfalls & Fixes

### PHP 8.4+ String Interpolation Errors
Complex expressions like `{$config['limits']['max_file_size'] / 1024 / 1024 / 1024}` cause parse errors.
**Fix:** Extract to variable first:
```php
$maxFileSizeGB = $this->config['limits']['max_file_size'] / 1024 / 1024 / 1024;
$help .= "• حجم ماکسیمم: {$maxFileSizeGB} گیگ\n";
```

### Null Response from `sendMessage()`
`sendMessage()` can return `null` on network failure. Always check:
```php
$msg = $this->telegram->sendMessage($chatId, "...");
if (!$msg || !$msg->getResult()) {
    // Handle failure
    return;
}
```

### Missing `is_banned` in User Array
When creating new user, include `is_banned => 0`:
```php
return [
    'id' => $this->pdo->lastInsertId(),
    // ...
    'is_banned' => 0,
];
```

### longman/telegram-bot Version Pinning
Use `"longman/telegram-bot": "0.83.*"` instead of `"^1.0"` to avoid dev-master instability.

### Database Migration After Composer
Run schema creation after `composer install`:
```bash
sqlite3 database/bot.sqlite < database/schema.sql
```

### Binary Paths for yt-dlp/ffmpeg
Set explicit paths in `.env`:
```env
YT_DLP_PATH=/usr/local/bin/yt-dlp
FFMPEG_PATH=/usr/bin/ffmpeg
```

## Rate Limiting & Safety
- Daily download limit per user (configurable)
- Max file size (Telegram bot limit: 2GB)
- Max duration filter
- Ban system (`is_banned` flag)
- Flood protection via `answerCallbackQuery` + status edits

## References
- `references/longman-telegram-bot.md` — API cheatsheet
- `references/yt-dlp-formats.md` — Format selection guide
- `references/ffmpeg-presets.md` — Compression presets
- `references/railway-deployment.md` — Step-by-step deploy
- `templates/bot-structure/` — Starter project template
- `scripts/setup-dev-env.sh` — One-command dev setup