# Python Visual Tutorial Examples

## IMPORTANT: Use Telegram Markdown, Not PIL Images

PIL/Pillow CANNOT render Persian/Arabic RTL text correctly. After extensive testing (NotoSansArabic, Vazirmatn, DejaVu, arabic_reshaper, bidi), all approaches fail with boxes, reversed text, or crashes.

**Use Telegram formatted messages instead:**

```python
import requests

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

lessons = [
    """🐍 *درس ۱: Hello World*
━━━━━━━━━━━━━━━━━━━━━━━━

\`print()\` براي چاپ متن استفاده ميشه:

\`\`\`python
print("Hello, World!")
\`\`\`

💡 *نکته:* \`#\` براي توضيح استفاده ميشه""",

    """🐍 *درس ۲: متغيرها*
━━━━━━━━━━━━━━━━━━━━━━━━

\`\`\`python
name = "Python"
age = 25
\`\`\`

\`type()\` براي فهميدن نوع متغير استفاده ميشه""",
]

for lesson in lessons:
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
        "chat_id": CHAT_ID,
        "text": lesson,
        "parse_mode": "Markdown"
    })
```

## Why Telegram Markdown Works

- ✅ Persian renders perfectly (RTL handled by Telegram client)
- ✅ Code blocks with syntax highlighting
- ✅ Bold, italic, inline code
- ✅ Works on all devices (mobile, desktop, web)
- ❌ PIL images — Persian broken (boxes, reversed, disconnected)

## Lessons (15 topics)

| # | Topic | Key Concepts |
|---|-------|--------------|
| 1 | Hello World | print(), comments |
| 2 | Variables | str, int, float, bool, type() |
| 3 | Input/Output | input(), type conversion |
| 4 | Operators | +, -, *, /, //, %, ** |
| 5 | Conditions | if/elif/else, and/or/not |
| 6 | Loops | for, while, range(), break |
| 7 | Functions | def, return, default args |
| 8 | Lists | [], append, pop, slice |
| 9 | Dictionaries | {}, keys/values/items |
| 10 | Classes | class, __init__, self |
| 11 | f-strings | f"", .format() |
| 12 | File I/O | with open(), json |
| 13 | Exceptions | try/except, raise |
| 14 | Decorators | @decorator, functools |
| 15 | Lambdas | lambda, map, filter |

## Old Approach (BROKEN — DO NOT USE)

The PIL-based image generation approach has been abandoned due to fundamental Persian text rendering limitations. See `references/pil-persian-limitation.md` in the `telegram-bot` skill for detailed test results.