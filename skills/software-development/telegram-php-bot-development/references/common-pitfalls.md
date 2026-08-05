# Common Pitfalls & Fixes for Telegram PHP Bot Development

## PHP 8.4+ String Interpolation Errors

**Problem:** Complex expressions like `{$config['limits']['max_file_size'] / 1024 / 1024 / 1024}` cause parse errors: `unexpected token "/", expecting "->" or "?->" or "["`

**Fix:** Extract to variable first:
```php
$maxFileSizeGB = $this->config['limits']['max_file_size'] / 1024 / 1024 / 1024;
$help .= "• حجم ماکسیمم: {$maxFileSizeGB} گیگ\n";
```

## Null Response from `sendMessage()`

**Problem:** `sendMessage()` can return `null` on network failure or API error.

**Fix:** Always check:
```php
$msg = $this->telegram->sendMessage($chatId, "...");
if (!$msg || !$msg->getResult()) {
    $this->db->updateDownload($downloadId, ['status' => 'failed', 'error_message' => 'Failed to send message']);
    return;
}
```

## Missing `is_banned` in User Array

**Problem:** New user creation missing `is_banned` field causes "Undefined array key" warning.

**Fix:** Include `is_banned => 0` in new user array:
```php
return [
    'id' => $this->pdo->lastInsertId(),
    'telegram_id' => $telegramId,
    'username' => $username,
    'first_name' => $firstName,
    'daily_downloads' => 0,
    'last_download_date' => null,
    'is_banned' => 0,
];
```

## longman/telegram-bot Version Pinning

**Problem:** `"^1.0"` resolves to unstable `dev-master`/`v1.x-dev`.

**Fix:** Use stable version:
```json
"longman/telegram-bot": "0.83.*"
```

## Database Migration After Composer

**Problem:** Schema not created after `composer install`.

**Fix:** Run explicitly:
```bash
sqlite3 database/bot.sqlite < database/schema.sql
```

## Binary Paths for yt-dlp/ffmpeg

**Problem:** Binaries not in PATH on production.

**Fix:** Set explicit paths in `.env`:
```env
YT_DLP_PATH=/usr/local/bin/yt-dlp
FFMPEG_PATH=/usr/bin/ffmpeg
```

## Telegram Webhook "chat not found"

**Problem:** User hasn't started chat with bot yet.

**Fix:** User must send `/start` to bot before API calls work. Handle gracefully:
```php
try {
    $result = Request::sendMessage($data);
} catch (TelegramException $e) {
    if (str_contains($e->getMessage(), 'chat not found')) {
        // User needs to start bot first
    }
}
```