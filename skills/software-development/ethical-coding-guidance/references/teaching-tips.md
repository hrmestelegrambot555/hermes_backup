# Teaching Tips for Young Beginners (13-18)

## Mindset & Approach

### Do's
- **Code together, line by line** — They type, you explain each line's purpose
- **Ask "what do you think happens here?"** before explaining — builds mental model
- **Let them debug first** — "What error do you see? What line? What does it mean?"
- **Celebrate real, working projects** — A bot that echoes messages > 1000 fake views
- **Portfolio from day one** — Every project: GitHub repo, README, .gitignore
- **Teach safety early** — `.env` for tokens, never commit secrets, `pip freeze > requirements.txt`

### Don'ts
- Don't give copy-paste solutions they don't understand
- Don't fix their bugs for them — guide with questions
- Don't use jargon without defining it (async, handler, decorator, API)
- Don't rush — 20 min of deep understanding > 1 hour of shallow copying

## Session Structure (45-60 min)

| Phase | Time | Activity |
|-------|------|----------|
| **Hook** | 5 min | Show working demo of what they'll build |
| **Concept** | 10 min | One new concept (e.g., "what is a handler?") with tiny example |
| **Build** | 25 min | Write code together — they type, you guide |
| **Test** | 5 min | Run it, break it, fix it |
| **Extend** | 5 min | "What if we added X?" — plant seeds for next time |
| **Wrap** | 5 min | Commit to GitHub, summarize what they learned |

## Language-Specific Tips (Python)

### Concepts to Introduce Gradually
| Week | Concepts | Example Project |
|------|----------|-----------------|
| 1-2 | Variables, types, print, input, if/else | Calculator, guess-the-number |
| 3-4 | Loops (for/while), lists, functions | Todo list, rock-paper-scissors |
| 5-6 | Dicts, sets, file I/O, JSON | Contact book, quiz game |
| 7-8 | Modules, pip, virtualenv, requests | Weather app, price checker |
| 9-10 | Classes, OOP basics | Text RPG, bank account sim |
| 11-12 | Async, APIs, telegram bot | Echo bot, poll bot |
| 13+ | Databases, web frameworks, deployment | Mini App, full project |

### Common Beginner Confusions (Address Proactively)
- `=` vs `==` — assignment vs comparison
- Indentation = scope (not braces)
- `list.append()` returns `None` — `x = lst.append(1)` breaks
- Mutable default args: `def f(x=[]):` — use `def f(x=None): x = x or []`
- `async`/`await` — not magic, just "pause here until ready"
- Virtual environments — why, how, `source venv/bin/activate`

## Motivational Anchors

### Show, Don't Just Tell
- "This bot you're building? Real people use bots like this for businesses."
- "That JSON file? That's how real apps store data."
- "Your GitHub profile with 5 projects? That's a portfolio for internships."

### Connect to Their Interests
- Gamer? → Build a game stats tracker
- Crypto curious? → Price alert bot
- Meme lover? → Meme generator bot
- Student? → Homework reminder / schedule bot

### Handle Frustration
- "Errors are normal. Every pro sees 50 errors a day."
- "That error message? It's telling you exactly where to look."
- "Let's read it together. What line? What type?"

## Safety & Ethics (Reinforce Every Session)
- Never share tokens, passwords, session strings
- `.gitignore` includes `.env`, `*.session`, `__pycache__/`
- Don't scrape aggressively — respect `robots.txt`, rate limits
- Don't automate what ToS forbids — build with official APIs
- Code you write = your responsibility

## Resources to Recommend
- **Python:** `python.org`, `realpython.com`, `automatetheboringstuff.com`
- **Telegram Bot:** `core.telegram.org/bots`, `python-telegram-bot.org`
- **Practice:** `exercism.org`, `codewars.com`, `leetcode.com` (easy)
- **Persian:** `faradars.org`, `maktabkhooneh.org`, `github.com/...` (awesome-python-fa)

## Red Flags in Their Code (Teach Them to Spot)
- `eval(input())` → "Never trust user input"
- `requests.get(url, verify=False)` → "Don't disable SSL"
- Hardcoded tokens → "Use .env"
- Infinite loops without exit → "Always have a break condition"
- Copy-pasted code they can't explain → "Delete it, write your own"