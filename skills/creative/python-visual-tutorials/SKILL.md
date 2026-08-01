---
name: python-visual-tutorials
description: Generate Persian tutorial images with syntax highlighting.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Python, Tutorial, Images, Persian, Education]
---

# Python Visual Tutorial Generator

Generate beautiful tutorial images with Persian/Farsi text and Python syntax highlighting. Dark theme with professional colors. Use `terminal` tool to run the generator script.

## When to Use

- User wants Python tutorial images
- User asks for visual/animated Python lessons
- User wants Persian/Farsi Python documentation
- User asks for "تصویر آموزشی پایتون"

## Prerequisites

```bash
pip install pillow
```

Font: Download `NotoSansArabic.ttf` from Google Fonts:
```bash
mkdir -p fonts
curl -sL "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic.ttf" -o fonts/NotoSansArabic.ttf
```

## Quick Reference

| Color | Usage |
|-------|-------|
| `BG_COLOR = (30, 30, 45)` | Dark background |
| `HEADER_COLOR = (88, 166, 255)` | Blue header bar |
| `CODE_BG = (40, 44, 52)` | Code block background |
| `KEYWORD_COLOR = (198, 120, 221)` | Purple keywords |
| `STRING_COLOR = (152, 195, 121)` | Green strings |
| `COMMENT_COLOR = (92, 99, 112)` | Gray comments |
| `ACCENT_COLOR = (86, 182, 194)` | Cyan accent |

## Procedure

1. Create `gen_tutorial_images.py` using the script in `scripts/`
2. Run via `terminal` tool: `python3 gen_tutorial_images.py`
3. Images saved to `images/` directory
4. Send via Telegram bot API using `sendPhoto` endpoint

## How to Send Images

```python
import requests

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_image(filepath, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(filepath, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': CHAT_ID, 'caption': caption}
        return requests.post(url, files=files, data=data)
```

## Pitfalls

- **PIL/Pillow CANNOT reliably render Persian/Arabic RTL text** — This is a fundamental limitation confirmed by extensive testing:
  - `arabic_reshaper` creates Arabic presentation forms (initial/medial/final) that fonts can't render → boxes □□□
  - `bidi.algorithm.get_display()` doesn't help — PIL doesn't handle RTL layout
  - `NotoSansArabic.ttf` — has Persian base characters but fails on reshaped forms
  - `NotoSansArabic-Bold.ttf` from apt `fonts-noto-core` — same issue
  - `Vazirmatn.ttf` (variable font) — PIL can't load it at all ("unknown file format")
  - `DejaVuSans.ttf` — doesn't support Persian characters
  - Direct text (no reshaping) — renders backwards (LTR instead of RTL)
  - **VERDICT: Do NOT use PIL for Persian text. Ever.**
- **Recommenced alternative: Use Telegram Markdown messages** — for Persian educational content, send formatted text via `sendMessage` with `parse_mode: Markdown`. This renders Persian text correctly and looks professional. Use code blocks for Python code examples.
- **Don't use `arabic_reshaper` with Persian text in PIL** — it creates Arabic presentation forms that fonts don't support, resulting in boxes.
- **Don't use `bidi.algorithm.get_display()`** — PIL doesn't handle RTL properly regardless.
- **Variable fonts (.ttf with weight axis)** like Vazirmatn variable don't work with PIL.
- **System fonts from apt (fonts-noto-core) don't render Persian correctly in PIL either** — NotoSansArabic-Bold.ttf was tested and still had issues.
- **Telegram caption limit is 1024 characters** — use sendMessage for longer content.
- **For Persian educational content, always prefer text messages over images** — user explicitly requested this after image attempts failed. The user said "ریدی بابا" (you messed up) after multiple failed image attempts.

## Verification

```bash
python3 gen_tutorial_images.py
ls -la images/
# Should show .png files for each lesson
```
