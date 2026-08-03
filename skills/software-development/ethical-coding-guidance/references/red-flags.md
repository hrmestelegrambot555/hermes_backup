# Red Flags: Malicious/Obfuscated Code Indicators

## Immediate Red Flags (Stop Analysis)

| Pattern | Why It's Dangerous |
|---------|-------------------|
| `marshal.loads(bytes)` + `exec()` | Obfuscated bytecode — cannot be audited, likely malicious |
| `sys.version[:3] == '3.9'` (exact minor version) | Targets specific CPython build; bytecode incompatible elsewhere |
| Hardcoded usernames/channels (`@khaz_kardam`, `@oh_ridi`) | Tied to specific actor; likely part of botnet/spam network |
| Auto-download proxies from `api.proxyscrape.com` | Unverified proxies; traffic interception risk |
| Unknown PyPI packages (`gdolib==0.2.6`) | May not exist, may be typo-squatted, may contain malware |
| Keywords: "view bot", "member adder", "auto forward", "mass DM", "fake views" | Explicit ToS violation; spam tools |

## Secondary Red Flags (Investigate Further)

| Pattern | Concern |
|---------|---------|
| `eval()`, `exec()` with user input | Code injection |
| `os.system()`, `subprocess` with string interpolation | Command injection |
| Base64/hex encoded strings decoded at runtime | Hiding payloads |
| Anti-debugging: `sys.settrace`, `threading` checks | Evading analysis |
| Encrypted strings decrypted in memory | Hiding C2, tokens, URLs |
| Persistence mechanisms (cron, startup, services) | Malware behavior |

## Telegram-Specific Red Flags

- `python-telegram-bot` NOT used — raw API calls with `requests` + manual `getUpdates`
- `api.telegram.org/bot{token}/sendMessage` with hardcoded tokens
- `t.me/` links with `?embed=1` or `views` endpoints (view manipulation)
- Proxy rotation for Telegram API calls (evading rate limits)
- Multiple account handling (session files, StringSession)

## Action on Detection

1. **Immediate refusal** — Do not run, debug, deobfuscate, or explain the code
2. **Explain risks** — Account ban, malware, legal ToS violation, wasted learning
3. **Redirect** — Offer 3-5 legitimate beginner projects
4. **Document** — Save hash/pattern for future recognition