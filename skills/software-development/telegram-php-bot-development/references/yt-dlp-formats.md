# yt-dlp Format Selection Guide

## Common Format Selectors

| Selector | Description |
|----------|-------------|
| `best` | Best quality single file (video+audio) |
| `worst` | Worst quality single file |
| `bestvideo` | Best video-only |
| `bestaudio` | Best audio-only |
| `bestvideo+bestaudio` | Best video + best audio (merged) |

## Quality-Based Selection

```bash
# Specific height
yt-dlp -f "bestvideo[height<=720]+bestaudio" URL

# Max height
yt-dlp -f "bestvideo[height<=1080]+bestaudio" URL

# Specific format ID
yt-dlp -f "137+140" URL  # 1080p video + m4a audio
```

## Codec-Based Selection

```bash
# Prefer av01/VP9 for video, opus for audio
yt-dlp -f "bestvideo[vcodec^=av01]+bestaudio[acodec=opus]" URL

# Avoid HEVC/H.265 (hardware decoding issues)
yt-dlp -f "bestvideo[vcodec!=hevc]+bestaudio" URL
```

## File Size Limits

```bash
# Max 50MB total
yt-dlp -f "best[filesize<50M]" URL

# Max 2GB (Telegram bot limit)
yt-dlp -f "best[filesize<2G]" URL
```

## Audio Extraction

```bash
# MP3 192kbps
yt-dlp -x --audio-format mp3 --audio-quality 192K URL

# Best audio (no conversion)
yt-dlp -f "bestaudio" URL
```

## PHP Integration Examples

```php
// In Downloader.php

// For video with quality limit
$format = "bestvideo[height<={$quality}]+bestaudio/best[height<={$quality}]";

// For MP3 extraction
$format = "bestaudio/best";

// For compressed video (360p)
$format = "bestvideo[height<=360]+bestaudio/best[height<=360]";
```

## Useful Flags

| Flag | Purpose |
|------|---------|
| `--no-playlist` | Download single video only |
| `--no-warnings` | Suppress warnings |
| `--dump-json` | Output video info as JSON |
| `-o 'tmp/%(id)s.%(ext)s'` | Output template |
| `--merge-output-format mp4` | Force MP4 container |

## Platform-Specific Notes

| Platform | Notes |
|----------|-------|
| YouTube | Use `youtube.com` / `youtu.be` extractors |
| Instagram | Requires login for private content |
| Twitter/X | Video/GIF extraction works |
| TikTok | Watermark-free with `-f "bestvideo"` |
| Facebook | May require cookies |

## Debugging

```bash
# Verbose output
yt-dlp -v URL

# List all formats
yt-dlp -F URL

# Test format selector
yt-dlp -f "bestvideo[height<=720]+bestaudio" --dry-run URL
```