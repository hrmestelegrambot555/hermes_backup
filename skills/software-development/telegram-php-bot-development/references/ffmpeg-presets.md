# FFmpeg Presets for Telegram Bot Media Processing

## Audio Extraction (MP3)

```bash
# Standard MP3 192kbps
ffmpeg -y -i input.mp4 -vn -acodec libmp3lame -ab 192k output.mp3

# High quality MP3 320kbps
ffmpeg -y -i input.mp4 -vn -acodec libmp3lame -ab 320k output.mp3

# Variable bitrate (better quality/size)
ffmpeg -y -i input.mp4 -vn -acodec libmp3lame -q:a 2 output.mp3
```

## Video Compression

```bash
# 720p compression (good balance)
ffmpeg -y -i input.mp4 \
  -vf scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2 \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 128k \
  output.mp4

# 480p compression (smaller)
ffmpeg -y -i input.mp4 \
  -vf scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2 \
  -c:v libx264 -preset fast -crf 25 \
  -c:a aac -b:a 96k \
  output.mp4

# 360p compression (minimum for Telegram)
ffmpeg -y -i input.mp4 \
  -vf scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2 \
  -c:v libx264 -preset fast -crf 28 \
  -c:a aac -b:a 64k \
  output.mp4
```

## CRF Quality Guide

| CRF | Quality | File Size | Use Case |
|-----|---------|-----------|----------|
| 18-20 | Visually lossless | Large | Archival |
| 21-23 | High | Medium | **Default for 720p** |
| 24-26 | Medium | Smaller | **Default for 480p** |
| 27-30 | Low | Small | **Default for 360p** |
| 31+ | Poor | Tiny | Emergency only |

## Preset Speed/Quality Tradeoff

| Preset | Speed | Quality | Use Case |
|--------|-------|---------|----------|
| `ultrafast` | Fastest | Larger | Real-time |
| `superfast` | Very fast | Larger | Live |
| `veryfast` | Fast | Good | Batch |
| `faster` | Moderate | Good | **Default** |
| `fast` | Moderate | Better | **Recommended** |
| `medium` | Slow | Better | Quality |
| `slow` | Slower | Best | Archive |
| `veryslow` | Slowest | Best | Archive |

## Telegram-Specific Optimizations

### Max 2GB File Size (Bot API Limit)

```bash
# Target ~1.8GB for safety
ffmpeg -y -i input.mp4 \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 128k \
  -fs 1.8G \
  output.mp4
```

### Streaming Support (moov atom at start)

```bash
ffmpeg -y -i input.mp4 \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  output.mp4
```

## PHP Integration

```php
// In Converter.php

// MP3 extraction
public function toAudio(string $inputPath, string $format = 'mp3', int $bitrate = 192): ?string {
    $outputPath = $this->tempDir . '/' . pathinfo($inputPath, PATHINFO_FILENAME) . ".{$format}";
    $cmd = "{$this->ffmpegPath} -y -i " . escapeshellarg($inputPath) . " ";
    $cmd .= "-vn -acodec libmp3lame -ab {$bitrate}k ";
    $cmd .= escapeshellarg($outputPath) . " 2>&1";
    $output = shell_exec($cmd);
    return file_exists($outputPath) ? $outputPath : null;
}

// Video compression with quality preset
public function compressVideo(string $inputPath, string $quality = '720p'): ?string {
    $presets = [
        '1080p' => ['scale' => '1920:1080', 'crf' => 22, 'audio' => '128k'],
        '720p'  => ['scale' => '1280:720',  'crf' => 23, 'audio' => '128k'],
        '480p'  => ['scale' => '854:480',   'crf' => 25, 'audio' => '96k'],
        '360p'  => ['scale' => '640:360',   'crf' => 28, 'audio' => '64k'],
    ];
    
    $p = $presets[$quality] ?? $presets['720p'];
    $outputPath = $this->tempDir . '/' . pathinfo($inputPath, PATHINFO_FILENAME) . "_compressed.mp4";
    
    $cmd = "{$this->ffmpegPath} -y -i " . escapeshellarg($inputPath) . " ";
    $cmd .= "-vf scale={$p['scale']}:force_original_aspect_ratio=decrease,pad={$p['scale']}:(ow-iw)/2:(oh-ih)/2 ";
    $cmd .= "-c:v libx264 -preset fast -crf {$p['crf']} ";
    $cmd .= "-c:a aac -b:a {$p['audio']} ";
    $cmd .= "-movflags +faststart ";
    $cmd .= escapeshellarg($outputPath) . " 2>&1";
    
    $output = shell_exec($cmd);
    return file_exists($outputPath) ? $outputPath : null;
}

// Get video duration
public function getDuration(string $path): int {
    $cmd = "{$this->ffmpegPath} -i " . escapeshellarg($path) . " 2>&1";
    $output = shell_exec($cmd);
    if (preg_match('/Duration: (\d{2}):(\d{2}):(\d{2})/', $output, $matches)) {
        return (int)$matches[1] * 3600 + (int)$matches[2] * 60 + (int)$matches[3];
    }
    return 0;
}
```

## Debugging FFmpeg

```bash
# Verbose output
ffmpeg -v verbose -i input.mp4 ...

# Show only errors
ffmpeg -v error -i input.mp4 ...

# Dry run (validate only)
ffmpeg -i input.mp4 -f null -

# Benchmark encoding speed
ffmpeg -i input.mp4 -c:v libx264 -preset fast -f null -
```