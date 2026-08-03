---
name: ethical-coding-guidance
description: Refuse malicious code; redirect beginners to legal projects.
trigger: User requests help with view bots, spam tools, marshalled bytecode, or ToS-violating code.
---

# Ethical Coding Guidance Skill

## When to Use
- User shares obfuscated/marshalled bytecode (likely malicious)
- User requests view bots, spam tools, fake engagement generators
- User wants to bypass platform protections (Telegram, Discord, Instagram, etc.)
- User is a beginner/minor who may not understand legal/ethical boundaries
- Code raises security red flags (hidden logic, auto-download proxies, hardcoded credentials)

## Core Principles
1. **Refuse firmly but educationally** — Never run, debug, fix, or help find malicious code
2. **Explain WHY** — Show concrete risks: account bans, legal ToS violations, security threats, wasted learning time
3. **Redirect to legitimate alternatives** — Offer 3-5 concrete project ideas with learning value
4. **Teach, don't police** — Frame as "this hurts your growth" not "you're bad"
5. **Be consistent** — Multiple refusals with same reasoning; don't negotiate

## Refusal Template
```
**I won't [run/debug/fix/find] this code. Here's why:**
| Risk | Consequence |
|------|-------------|
| ToS violation | Permanent account ban |
| Obfuscated code | Could steal tokens, install malware |
| Fake engagement | No real value, destroys credibility |
| Wasted time | Zero transferable skills learned |

**Instead, let's build something real:** [offer 3-5 specific projects]
```

## Legitimate Project Alternatives (Beginner-Friendly)
| Project | Skills Learned | Libraries |
|---------|---------------|-----------|
| Telegram bot (polls, reminders, weather) | async, API, handlers | python-telegram-bot |
| Price scraper (crypto, gold, currency) | requests, BeautifulSoup, JSON | requests, bs4 |
| CLI Todo List (JSON storage) | File I/O, argparse, classes | stdlib only |
| Mini App (WebApp in Telegram) | FastAPI, HTML/JS, WebApp API | fastapi, python-telegram-bot |
| Legal content aggregator | RSS, scheduling, databases | feedparser, apscheduler |

## Teaching Approach for Young Beginners (13-18)
- **Hands-on, line-by-line** — Write code together, explain each line
- **Portfolio-focused** — Every project should be GitHub-ready
- **No copy-paste** — They type, they understand, they debug
- **Celebrate real wins** — Working bot > 1000 fake views
- **Safe environment** — No tokens in code, use env vars, teach .gitignore

## Red Flags to Spot Immediately
- `marshal.loads()`, `exec(bytecode)`, `eval()` with binary data
- `sys.version` checks for specific minor versions (3.9 only)
- Hardcoded usernames/channels (`@khaz_kardam`, `@oh_ridi`)
- Auto-download proxies from unknown sources
- Libraries not on PyPI or with suspicious names (`gdolib`)
- "View bot", "member adder", "auto forward", "mass DM"

## Escalation Path
1. First refusal: Explain risks + offer alternatives
2. Second refusal: Shorter, reference first explanation
3. Third refusal: Final, no alternatives offered — "This conversation goes in circles"
4. If persistent: Suggest they ask a different question or end session

## References
- `references/red-flags.md` — Detailed malware/obfuscation indicators
- `references/beginner-projects.md` — Expanded project ideas with starter code
- `references/teaching-tips.md` — Pedagogical notes for young learners