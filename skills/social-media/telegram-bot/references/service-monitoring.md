# Service Monitoring for Telegram Bots

When running long-lived Telegram bots (userbots, polling bots) on a server, they can crash silently. A monitoring cron job restarts them automatically.

## Pattern: Self-Healing Script Monitor

Create a monitor script and schedule it via cron every 2-3 hours:

```bash
#!/bin/bash
# monitor.sh - Check and restart key services

check_and_restart() {
    local name="$1"
    local cmd="$2"
    local found=false
    
    for pid in /proc/[0-9]*/cmdline; do
        if cat "$pid" 2>/dev/null | tr '\0' ' ' | grep -q "$name"; then
            found=true
            break
        fi
    done
    
    if $found; then
        echo "✅ $name"
    else
        eval "$cmd"
        echo "🔄 $name (restarted)"
    fi
}

check_and_restart "spellcheck_userbot" "cd /root/.hermes/scripts && nohup python3 spellcheck_userbot.py >/tmp/spellcheck.log 2>&1 &"
check_and_restart "lt --port" "nohup lt --port 8080 >/tmp/tunnel.log 2>&1 &"
```

### Hermes Cron Job

```
Schedule: every 3h
Deliver: local (silent unless issues)
Prompt: "Check if spellcheck_userbot.py and lt tunnel are running. If stopped, restart them. Report only issues."
```

## Key Pitfalls

1. **Multiple instances accumulate**: Each restart attempt may leave orphan processes. Always `pkill -9 -f "script_name"` before starting a new instance.

2. **Port conflicts after kill**: Even after killing a process, ports stay in `TIME_WAIT`. Use `fuser -k PORT/tcp` or switch to a different port.

3. **Environment variables lost in background**: `nohup` and background processes don't inherit shell exports. Hardcode API keys as fallback in scripts.

4. **Polling conflicts**: Two instances of a polling bot cause `TelegramConflictError`. Monitor should verify only ONE instance is running.

5. **Hermes cron `no_agent=True` script path resolution**: When using `no_agent=True` with a script, Hermes resolves the path under `/data/.hermes/scripts/` NOT `/root/.hermes/scripts/`. If your script is in `/root/.hermes/scripts/`, copy it to `/data/.hermes/scripts/` first. Example error: `Script not found: /data/.hermes/scripts/my_script.sh`.

6. **Hermes cron AI model requirement**: AI-based cron jobs (with `no_agent=False`) require a model to be configured. Without it, jobs fail with `RuntimeError: Cron job has no model configured`. Fix: set `model` in the cronjob update call, or use `no_agent=True` with a shell script to bypass AI entirely. Example: `cronjob action=update job_id=XXX model={"model":"google/gemma-4-26b-a4b-it:free","provider":"openrouter"}`

## Quick Health Check Commands

```bash
# Check if a process is running (no pgrep needed)
python3 -c "
import os
name = 'spellcheck_userbot'
print(any(name in open(f'/proc/{p}/cmdline').read() 
    for p in os.listdir('/proc') if p.isdigit() 
    and os.path.exists(f'/proc/{p}/cmdline')))
"

# Kill all instances of a script
pkill -9 -f "script_name.py"

# Check port usage
fuser 8080/tcp 2>/dev/null
```
