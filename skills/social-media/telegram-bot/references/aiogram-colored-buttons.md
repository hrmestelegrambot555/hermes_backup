# aiogram Colored Inline Buttons

## ButtonStyle Enum

aiogram 3.30+ supports colored inline keyboard buttons via `ButtonStyle`:

```python
from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
```

### Available Styles

**IMPORTANT: Enum names are UPPERCASE** (`ButtonStyle.PRIMARY`, not `ButtonStyle.primary`)

| Style | Color | Use Case |
|-------|-------|----------|
| `ButtonStyle.PRIMARY` | 🔵 Blue | Main actions, navigation |
| `ButtonStyle.SUCCESS` | 🟢 Green | Positive actions, confirmations |
| `ButtonStyle.DANGER` | 🔴 Red | Destructive actions, warnings |

## Example: Colored Menu

```python
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ButtonStyle
import asyncio

bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher()

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton(text="🔥 پروکسی", callback_data="proxy", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="⚡ VPN", callback_data="vpn", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton(text="✅ فعالسازی", callback_data="activate", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text="❌ غیرفعال", callback_data="deactivate", style=ButtonStyle.DANGER),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("منو:", reply_markup=main_menu())

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
```

## Example: VPN Bot with Color-Coded Servers

```python
def server_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text="🟢 آلمان", callback_data="de", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text="🟢 آمریکا", callback_data="us", style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton(text="🟡 هلند", callback_data="nl", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="🔴 فرانسه", callback_data="fr", style=ButtonStyle.DANGER),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
```

## Pitfalls

1. **Style enum names are UPPERCASE**: Use `ButtonStyle.PRIMARY`, not `ButtonStyle.primary` — lowercase causes `AttributeError`
2. **Not all clients show colors**: Older Telegram clients may show default gray buttons
3. **URL buttons**: Style works with URL buttons too, but behavior varies by client
4. **Web App buttons**: Style may not apply to `web_app` type buttons

## Requirements

- aiogram >= 3.30 (check with `pip show aiogram`)
- Telegram Bot API 8.0+ (for colored button support)

## Quick Install

```bash
pip install aiogram --upgrade
```
