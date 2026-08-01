# Bale Bot API Integration Reference

Bale is an Iranian messaging app with a Bot API very similar to Telegram's.

## Base URL

```
https://tapi.bale.ai/bot<TOKEN>/METHOD_NAME
```

**NOT** `https://api.telegram.org` — Bale has its own API endpoint.

## Getting a Bot Token

1. Open Bale app
2. Search for `@BotFather`
3. Create a new bot with `/newbot`
4. Copy the token

## API Methods (Same as Telegram)

| Method | Description |
|--------|-------------|
| `getMe` | Get bot info |
| `sendMessage` | Send text message |
| `editMessageText` | Edit a message |
| `deleteMessage` | Delete a message |
| `getUpdates` | Poll for updates |
| `setWebhook` | Set webhook URL |

## Example: Send Message

```python
import requests

BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
BALE_API_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    url = f"{BALE_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    resp = requests.post(url, json=payload, timeout=10)
    return resp.json().get("ok", False)
```

## Example: Polling for Updates

```python
def get_updates(offset=None):
    url = f"{BALE_API_URL}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    resp = requests.get(url, params=params, timeout=35)
    return resp.json()
```

## Critical Limitations

### 1. Bot Cannot Edit User Messages

Just like Telegram, **bots cannot edit messages sent by users**. Only userbots (using real user accounts via Telethon) can edit messages.

**Workaround**: Send a new message with the correction:

```python
# ❌ FAILS:
edit_message(chat_id, msg_id, fixed_text)

# ✅ WORKS:
reply = f"✏️ اصلاح شد:\n\n{text}\n\n✅ {fixed_text}"
send_message(chat_id, reply)
```

### 2. aiogram Compatibility

aiogram's `base_url` parameter may not work reliably with Bale. Use **raw requests library** instead.

### 3. Chat Type Detection

To check if a message is private:

```python
if message.get("chat", {}).get("type") != "private":
    continue  # Skip groups and channels
```

## Comparison with Telegram

| Feature | Telegram | Bale |
|---------|----------|------|
| API Base | `api.telegram.org` | `tapi.bale.ai` |
| Bot Token | @BotFather (Telegram) | @BotFather (Bale) |
| Bot API | ✅ Full support | ✅ Similar |
| aiogram | ✅ Works | ⚠️ Use requests instead |
| Telethon | ✅ Works | ❓ Untested |
| Edit user messages | ❌ Bot can't | ❌ Bot can't |

## Pitfalls

1. **Wrong base URL**: Must use `https://tapi.bale.ai`, not `https://api.bel.ai`
2. **aiogram base_url**: Doesn't work reliably — use requests
3. **Bot can't edit user messages**: Send new message instead
4. **Token format**: Same as Telegram (`number:alphanumeric`)
