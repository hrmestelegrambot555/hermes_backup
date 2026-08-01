# PIL/Pillow Persian/Arabic Text Limitation

## Problem

PIL/Pillow cannot render Persian/Arabic RTL text correctly. Characters appear:
- Reversed (right-to-left becomes left-to-right)
- Disconnected (ligatures broken)
- As boxes (missing glyphs □□□)

## Tested & Failed

| Font/Approach | Result |
|---------------|--------|
| `NotoSansArabic.ttf` (from pip) | Base chars OK, reshaped forms → boxes |
| `NotoSansArabic-Bold.ttf` (from apt) | Same issue |
| `NotoKufiArabic-Bold.ttf` (from apt) | Same issue |
| `NotoNaskhArabic-Bold.ttf` (from apt) | Same issue |
| `Vazirmatn.ttf` (variable font) | PIL can't load ("unknown file format") |
| `DejaVuSans.ttf` | No Persian character support |
| `arabic_reshaper` + PIL | Creates presentation forms fonts can't render → boxes |
| `bidi.algorithm.get_display()` + PIL | Doesn't fix RTL layout |
| Direct text (no reshaping) | Renders backwards (LTR) |

**VERDICT**: Do NOT use PIL for Persian text. Ever. Use Telegram Markdown instead.

## Root Cause

1. **`arabic_reshaper` library** creates Arabic presentation forms (e.g., ﭖ, ﭺ) that standard fonts don't support
2. **Font limitations** — Even `NotoSansArabic`, `NotoKufiArabic`, `NotoNaskhArabic` fail to render Persian characters correctly in PIL
3. **No built-in RTL support** — PIL doesn't handle bidirectional text
4. **Variable fonts** (.ttf with weight axis) cause PIL to crash entirely

## Solution: Use Telegram Markdown

For Persian/Farsi content, use Telegram's native Markdown formatting instead of images:

```python
lessons = [
    """🐍 *درس ۱: Hello World*
━━━━━━━━━━━━━━━
`print()` براي چاپ متن استفاده ميشه:
```python
print("Hello, World!")
```
💡 *نکته:* `#` براي توضيح استفاده ميشه""",
]

for lesson in lessons:
    requests.post(f"{API}/sendMessage", json={
        "chat_id": CHAT_ID,
        "text": lesson,
        "parse_mode": "Markdown"
    })
```

## What Works

- ✅ `parse_mode="Markdown"` — Persian renders perfectly
- ✅ `parse_mode="HTML"` — Persian renders perfectly
- ✅ `bold/italic/code` — All formatting works
- ❌ PIL/Pillow images — Persian broken

## Verification

Always test Persian text rendering before generating images. If PIL shows boxes or reversed text, switch to Markdown messages.
