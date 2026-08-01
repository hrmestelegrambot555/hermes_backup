#!/usr/bin/env python3
"""
Telegram News Forwarder - Template with Image Support
Replace BOT_TOKEN, TARGET_CHAT_ID, SOURCE_CHANNELS, and filter keywords.
"""
import requests
import re
import json
import time
import os
from datetime import datetime, timezone

BOT_TOKEN = "YOUR_BOT_TOKEN"
TARGET_CHAT_ID = -100XXXXXXXXXX  # Get via getUpdates after bot joins channel

SOURCE_CHANNELS = ["channel1", "channel2"]
SENT_FILE = "/path/to/sent_news.json"
TEMP_DIR = "/tmp/news_images"

os.makedirs(TEMP_DIR, exist_ok=True)

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
        html = resp.text
        posts = []
        
        # Find all message IDs
        post_ids = re.findall(r'data-post="([^"]+)"', html)
        
        for post_id in post_ids:
            # Find text for this post
            text_pattern = rf'data-post="{re.escape(post_id)}".*?js-message_text[^>]*>(.*?)</div>'
            text_match = re.search(text_pattern, html, re.DOTALL)
            
            if not text_match:
                continue
            
            text_html = text_match.group(1)
            text = re.sub(r'<[^>]+>', '', text_html)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Find actual image (not emoji)
            image_url = None
            
            # Look for tgme_widget_message_photo (actual post images)
            photo_pattern = rf'data-post="{re.escape(post_id)}".*?tgme_widget_message_photo[^>]*background-image:url\([\'"]?([^\'")\s]+)[\'"]?\)'
            photo_match = re.search(photo_pattern, html, re.DOTALL)
            
            if photo_match:
                image_url = photo_match.group(1)
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
            else:
                # Look for any large image (not emoji)
                img_pattern = rf'data-post="{re.escape(post_id)}".*?background-image:url\([\'"]?([^\'")\s]+)[\'"]?\)'
                img_match = re.search(img_pattern, html, re.DOTALL)
                if img_match:
                    url_candidate = img_match.group(1)
                    if url_candidate.startswith('//'):
                        url_candidate = 'https:' + url_candidate
                    # Skip emoji images
                    if 'telegram.org/img/emoji' not in url_candidate:
                        image_url = url_candidate
            
            if text and len(text) > 10:
                posts.append({
                    "id": post_id,
                    "text": text,
                    "channel": channel_username,
                    "image_url": image_url
                })
        
        return posts
    except Exception as e:
        print(f"Error fetching {channel_username}: {e}")
        return []

def is_important(text):
    """Customize this filter for your use case"""
    keywords = ["فوری", "🚨", "‼️", "حمله", "توافق"]
    return any(kw.lower() in text.lower() for kw in keywords)

def download_image(url, post_id):
    """Download image to temp file"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://t.me/',
        }
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        # Safe filename (replace / with _)
        safe_id = post_id.replace('/', '_')
        ext = '.jpg'
        if 'png' in resp.headers.get('content-type', ''):
            ext = '.png'
        
        filepath = os.path.join(TEMP_DIR, f"{safe_id}{ext}")
        with open(filepath, 'wb') as f:
            f.write(resp.content)
        
        return filepath
    except Exception as e:
        print(f"  Download error: {e}")
        return None

def send_photo_file(chat_id, filepath, caption):
    """Send photo as file upload"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        with open(filepath, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': chat_id,
                'caption': caption[:1024],  # Telegram caption limit
                'parse_mode': 'HTML'
            }
            resp = requests.post(url, files=files, data=data, timeout=30)
            result = resp.json()
            if result.get("ok"):
                return True
            else:
                print(f"  Upload error: {result.get('description', 'unknown')}")
                return False
    except Exception as e:
        print(f"  Upload exception: {e}")
        return False

def send_message(chat_id, text):
    """Send text message"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
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
        posts = fetch_channel_posts(channel)
        all_posts.extend(posts)
        time.sleep(1)
    
    sent_count = 0
    
    for post in all_posts:
        if post["id"] in sent_ids:
            continue
        
        if is_important(post["text"]):
            success = False
            
            # Try with image first
            if post.get("image_url"):
                filepath = download_image(post["image_url"], post["id"])
                if filepath:
                    success = send_photo_file(TARGET_CHAT_ID, filepath, post["text"])
                    if success:
                        print(f"✅ Sent with image: {post['id']}")
                    # Clean up
                    try:
                        os.remove(filepath)
                    except:
                        pass
                
                # Fallback to text if image failed
                if not success:
                    success = send_message(TARGET_CHAT_ID, post["text"])
                    if success:
                        print(f"✅ Sent text only: {post['id']}")
            else:
                # Text only
                success = send_message(TARGET_CHAT_ID, post["text"])
                if success:
                    print(f"✅ Sent text: {post['id']}")
            
            if success:
                sent_count += 1
                time.sleep(1)
            else:
                print(f"❌ Failed: {post['id']}")
        
        sent_ids.add(post["id"])
    
    sent_data["sent_ids"] = list(sent_ids)[-500:]
    save_sent(sent_data)
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n📊 {now} - Checked {len(all_posts)}, sent {sent_count} important news")

if __name__ == "__main__":
    main()
