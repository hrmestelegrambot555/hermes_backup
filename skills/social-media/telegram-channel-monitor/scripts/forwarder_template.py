#!/usr/bin/env python3
"""
Telegram News Forwarder - Template
Replace BOT_TOKEN, TARGET_CHAT_ID, SOURCE_CHANNELS, and filter keywords.
"""
import requests
import re
import json
import time
from datetime import datetime, timezone

BOT_TOKEN = "YOUR_BOT_TOKEN"
TARGET_CHAT_ID = -100XXXXXXXXXX  # Get via getUpdates after bot joins channel

SOURCE_CHANNELS = ["channel1", "channel2"]
SENT_FILE = "/path/to/sent_news.json"

def load_sent():
    try:
        with open(SENT_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"sent_ids": []}

def save_sent(data):
    with open(SENT_FILE, 'w') as f:
        json.dump(data, f)

def fetch_channel_posts(channel_username):
    url = f"https://t.me/s/{channel_username}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        posts = []
        blocks = re.findall(
            r'data-post="([^"]+)".*?js-message_text[^>]*>(.*?)</div>',
            resp.text, re.DOTALL
        )
        for post_id, text_html in blocks:
            text = re.sub(r'<[^>]+>', '', text_html)
            text = re.sub(r'\s+', ' ', text).strip()
            if text and len(text) > 10:
                posts.append({"id": post_id, "text": text, "channel": channel_username})
        return posts
    except Exception as e:
        print(f"Error fetching {channel_username}: {e}")
        return []

def is_important(text):
    """Customize this filter for your use case"""
    keywords = ["فوری", "🚨", "‼️", "حمله", "توافق"]
    return any(kw.lower() in text.lower() for kw in keywords)

def send_to_channel(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TARGET_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.json().get("ok", False)
    except:
        return False

def main():
    sent_data = load_sent()
    sent_ids = set(sent_data.get("sent_ids", []))
    
    all_posts = []
    for channel in SOURCE_CHANNELS:
        all_posts.extend(fetch_channel_posts(channel))
        time.sleep(1)
    
    sent_count = 0
    for post in all_posts:
        if post["id"] in sent_ids:
            continue
        if is_important(post["text"]):
            if send_to_channel(post["text"]):
                print(f"✅ Sent: {post['id']}")
                sent_count += 1
                time.sleep(1)
        sent_ids.add(post["id"])
    
    sent_data["sent_ids"] = list(sent_ids)[-500:]
    save_sent(sent_data)
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"📊 {now} - Checked {len(all_posts)}, sent {sent_count}")

if __name__ == "__main__":
    main()
