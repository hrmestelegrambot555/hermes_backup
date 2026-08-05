# API Key Troubleshooting in Hermes Agent

## Common Issue: Keys Appear Truncated in Terminal Output

**Symptom:** API keys in `.env` or config files appear truncated (e.g., `sk-f3c...71d9`) when viewed with `cat`, `read_file`, or terminal output.

**Root Cause:** The terminal tool's output formatter intentionally truncates sensitive values (API keys, tokens, secrets) in tool output for security. The actual file contains the full key.

**Verification:**
```bash
# Check raw bytes - this bypasses the formatter
python3 -c "
with open('/data/.hermes/.env', 'rb') as f:
    content = f.read()
for line in content.split(b'\n'):
    if b'OPENROUTER' in line:
        print('Length:', len(line))
        print('Full:', line)
"
```

**Resolution:** The key is intact. Use the raw byte inspection method above or check with `env | grep KEY` after sourcing the file.

---

## Common Issue: Keys Not Loaded into Environment

**Symptom:** `hermes chat` returns "HTTP 401: Missing Authentication header" even after setting key in config.

**Root Causes (in order of likelihood):**

1. **Key stored in wrong location** - Hermes reads from:
   - `$HERMES_HOME/.env` (primary)
   - Process environment variables
   - `config.yaml` for non-secret settings only
   - Project `.env` as fallback only

2. **Entrypoint.sh overwrites .env on gateway restart** - The Docker entrypoint rewrites `.env` from environment variables on every gateway start. If the key isn't in the container's environment, it gets written as truncated or empty.

3. **Secret scope isolation** - Under multiplexing, `agent.secret_scope.get_secret()` is authoritative. Process env vars are only used as fallback when unscoped.

**Debugging Steps:**

```bash
# 1. Verify key exists in .env with full value
python3 -c "
with open('/data/.hermes/.env', 'rb') as f:
    print(f.read())
"

# 2. Check if process env has it
env | grep OPENROUTER

# 3. Check what hermes sees
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv('/data/.hermes/.env', override=True)
print('Loaded:', os.getenv('OPENROUTER_API_KEY', 'NOT SET')[:30])
"

# 4. Check if entrypoint.sh is the issue (Docker)
cat /proc/1/environ 2>/dev/null | tr '\0' '\n' | grep OPENROUTER
```

**Fix for Docker/entrypoint.sh environments:**

The entrypoint.sh reads from environment variables and writes to `.env`. You must either:
- Set the environment variable in the container (Docker `-e`, docker-compose `environment`, Railway variables, etc.)
- OR disable entrypoint's .env management (not recommended)

```bash
# Quick test: export and run hermes directly
export OPENROUTER_API_KEY=sk-your-full-key
hermes chat -q "test" --provider openrouter
```

---

## Common Issue: Config Key vs Env Var Confusion

**Symptom:** `hermes config set openrouter.api_key ...` shows warning "not a recognized config key"

**Root Cause:** Hermes uses `OPENROUTER_API_KEY` environment variable (in `.env`), not a config.yaml key. The config system only manages non-secret settings.

**Correct approach:**
```bash
# This writes to .env (correct)
hermes config set OPENROUTER_API_KEY sk-your-key

# This writes to config.yaml (wrong for secrets)
hermes config set openrouter.api_key sk-your-key  # WARNING: not recognized
```

---

## Quick Reference: Where Keys Live

| Key | Location | Managed By |
|-----|----------|------------|
| OPENROUTER_API_KEY | `.env` | `hermes config set OPENROUTER_API_KEY` / entrypoint.sh |
| OPENAI_API_KEY | `.env` | `hermes config set OPENAI_API_KEY` / entrypoint.sh |
| ANTHROPIC_API_KEY | `.env` | `hermes config set ANTHROPIC_API_KEY` / entrypoint.sh |
| TELEGRAM_BOT_TOKEN | `.env` | `hermes config set TELEGRAM_BOT_TOKEN` / entrypoint.sh |
| Model selection | `config.yaml` | `hermes model` / `hermes config set model` |
| Provider selection | `config.yaml` | `hermes config set provider` |

---

## Debugging Checklist for Auth Failures

- [ ] Key is full length in `.env` (verify with raw byte read)
- [ ] Key is in process environment (`env | grep KEY`)
- [ ] Correct provider specified (`--provider openrouter`)
- [ ] Model exists on provider (`openai/gpt-4o-mini` on OpenRouter)
- [ ] No entrypoint.sh overwrite (Docker: check container env vars)
- [ ] Secret scope not blocking (try unscoped CLI first)
- [ ] Key is valid (test with `curl` to provider's /models endpoint)