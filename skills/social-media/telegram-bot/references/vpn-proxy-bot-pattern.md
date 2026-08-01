# VPN/Proxy Bot Design Pattern

Complete aiogram bot template for VPN/proxy distribution bots with colored inline buttons.

## Architecture

```
/start → Main Menu (colored buttons) → Proxy List → Random Config → Copy & Use
                                  → Tutorial → Platform-specific guides
                                  → Server Status → Live stats
```

## Key Design Elements

### 1. Random Config Generation

Each click generates a new random config with different server IPs:

```python
import random

def get_random_proxy(proto):
    servers = ["🇩🇪 DE-1", "🇩🇪 DE-2", "🇺🇸 US-1", "🇳🇱 NL-1"]
    server = random.choice(servers)
    
    configs = {
        "vless": f"""🟣 **VLESS - {server}**

```
vless://uuid@185.234.72.{random.randint(10,250)}:443?...#Config-{server.replace(' ', '')}
```

⏱️ **پینگ:** {random.randint(20,80)}ms
👥 **کاربران:** {random.randint(10,200)}/500""",
    }
    return configs.get(proto, "کانفیگ موجود نیست")
```

### 2. Color-Coded Server Status

```python
def status_keyboard():
    kb = [
        [InlineKeyboardButton(text="🟢 آلمان", callback_data="de", style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton(text="🟡 هلند", callback_data="nl", style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text="🔴 فرانسه", callback_data="fr", style=ButtonStyle.DANGER)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
```

### 3. Platform-Specific Tutorials

Store tutorials as dictionary keys, serve via callback:

```python
TUTORIALS = {
    "tut_android": """📱 **آموزش اندروید**
1. دانلود v2rayNG از Google Play
2. کانفیگ رو کپی کنید
3. Import from clipboard""",
    "tut_ios": """🍎 **آموزش iOS**
1. دانلود Streisand از App Store
2. + → Import from Clipboard""",
}
```

## Color Usage Convention

| Color | ButtonStyle | Use Case |
|-------|-------------|----------|
| 🔵 Blue | `PRIMARY` | Main actions, navigation |
| 🟢 Green | `SUCCESS` | Online servers, positive actions |
| 🔴 Red | `DANGER` | Offline servers, premium, warnings |

## Complete Bot Skeleton

```python
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ButtonStyle
import asyncio

bot = Bot(token="TOKEN")
dp = Dispatcher()

def main_menu():
    kb = [
        [InlineKeyboardButton(text="🔥 پروکسی", callback_data="proxy", style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text="📊 وضعیت", callback_data="status", style=ButtonStyle.SUCCESS)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("منو:", reply_markup=main_menu())

@dp.callback_query(F.data == "proxy")
async def proxy(callback: types.CallbackQuery):
    await callback.message.edit_text("کانفیگ...", reply_markup=main_menu())
    await callback.answer()

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
```

## Pitfalls

1. **Enum UPPERCASE**: `ButtonStyle.PRIMARY` not `ButtonStyle.primary`
2. **edit_text requires same parse_mode**: If original used Markdown, edit must too
3. **callback.answer() required**: Without it, loading spinner shows indefinitely
4. **URL buttons with style**: Style may not render on all clients
5. **Channel URL button**: Use `url=` parameter, not `callback_data=`
