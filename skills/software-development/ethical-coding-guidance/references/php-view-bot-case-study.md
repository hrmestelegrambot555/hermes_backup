# PHP View Bot Case Study — Session Notes

**User:** 16-year-old Python learner from Tehran, Iran (Persian speaker)
**Date:** 2026-08-02
**Context:** User shared multiple GitHub repos and PHP files for "view bots" / "member adders"

---

## Repos Analyzed (All ToS Violations)

| Repo | Type | Key Indicators |
|------|------|----------------|
| `iiiiii1wepfj/message-view-counter-bot` | View counter (forward trick) | Hydrogram, forwards to channel to inflate view count |
| `kamolmachine/telegram-stories-viewer-bot` | Story viewer (userbot) | GramJS + Telegraf, 33k users, anonymous story viewing |
| `fabston/TradingView-Webhook-Bot` | Legitimate webhook bot | Flask, multi-platform alerts — **OK** |
| `RonaldBarberi/bots_seends` | Call center automation | Selenium + win32com + WhatsApp Web scraping |
| `rommelnita/Telegram-members-adder` | Member adder (spam) | Pyrogram + Telethon, premium subscription (200₹/mo), scrapes + InviteToChannel |

---

## PHP Bot Files Shared (`bots.php` + `jdf.php`)

### `jdf.php` — **Legitimate Library**
- Jalali (Solar Hijri) date/time functions for PHP
- Author: Reza Gholampanahi (jdf.scr.ir)
- LGPL, widely used in Persian PHP projects
- Functions: `jdate()`, `jstrftime()`, `jmktime()`, `gregorian_to_jalali()`, `tr_num()` (English↔Persian digits)
- **VERDICT: Safe, standard, recommended for Persian projects**

### `bot.php` — **View/Member Bot ("سلطان بازدید")**
**Architecture:**
- Single-file PHP, no framework, file-based storage (`data/` directory)
- Webhook mode: `json_decode(file_get_contents('php://input'))`
- Uses `jdf.php` for Persian date display

**Spam Features:**
1. **Referral system** — Users invite friends → earn "rockets" (views)
2. **View collection** — Users watch ads in channel → earn views
3. **Ad posting** — Spend earned views to advertise own posts
4. **Forced channel join** — Checks membership in `@SoltanBazdid`
5. **Banner system** — Custom banner delivery via channel
6. **Leaderboards** — Top referrers / top view collectors
7. **Admin panel** — Broadcast, user stats, premium management

**Data Storage (all plain text files):**
```
users.txt                 # All user IDs
data/<chat_id>/membrs.txt # Referral count
data/<chat_id>/shoklat.txt # View balance ("rockets")
data/<chat_id>/mosak.txt  # View balance (alt)
data/<chat_id>/kolbazdid.txt # Total views
data/<chat_id>/bish.txt   # Views for ad posting
data/pen.txt              # Banned users
data/channel.txt          # Forced join channel
data/nerkh.txt            # View price config
data/bannermatn.txt       # Banner template
```

**Red Flags in Code:**
- Hardcoded admin IDs: `$ADMIN = 101564409`
- Hardcoded bot token in webhook check: `bot467158061:***`
- No input validation, direct file writes from user input
- `callback_data` used as keyboard buttons (not inline keyboards properly)
- Persian UI strings mixed with code logic
- `die()` after forced join check — blocks all other handlers

---

## Teaching Moments from This Session

### What Worked
1. **Concrete analysis** — Showing exact lines that prove spam behavior
2. **Clear verdict table** — Legal vs illegal repos side by side
3. **Legitimate alternative** — Pointing out `jdf.php` is actually good
4. **Railway deployment guide** — For legal projects only

### User Response Pattern
- Persistent but **receptive to redirection** when given concrete alternatives
- Interested in **real portfolio projects** (not just "don't do this")
- Responds well to **specific project ideas with learning outcomes**

### Recommended Follow-up Projects for This User
| Project | Why It Fits |
|---------|-------------|
| **Persian Calendar Bot** | Uses `jdf.php` knowledge, real utility, portfolio piece |
| **Crypto/Gold Price Alert Bot** | Iranian market interest, webhooks, APIs |
| **Telegram Mini App (WebApp)** | Modern, uses FastAPI + HTML/JS, impressive for 16yo portfolio |
| **RSS Feed Aggregator** | Persian tech news, scheduling, database practice |

---

## Key Insight for Future Sessions

**This user is a motivated beginner who keeps encountering spam code in their environment (Iranian Telegram dev circles).** They need:
- Clear "this is spam / this is legit" labels on every repo they share
- Concrete, culturally relevant project alternatives
- Hands-on coding guidance (not just theory)
- Deployment help for **legal** projects only

The ethical-coding-guidance skill's approach (refuse + explain + redirect with 3-5 specific projects) is exactly right for this profile.