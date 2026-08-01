# LocalTunnel Security Gate

## The Issue

When using `lt` (localtunnel) for HTTPS tunnels, users see a security page before accessing the tunnel:

```
┌─────────────────────────────────────────┐
│  You are about to visit:                │
│  https://random-name.loca.lt            │
│                                         │
│  This is a Localtunnel security check.  │
│  Please enter the server IP below.      │
│                                         │
│  Server IP: [____________________]      │
│         [Continue]                      │
└─────────────────────────────────────────┘
```

## Solution

**Tell the user the IP upfront**:

> "Enter this IP: `YOUR_SERVER_IP`"

## Example

If your server IP is `152.55.176.2`, send:

> "✅ Tunnel active: https://rare-jokes-share.loca.lt
> 
> 🔐 **Security gate**: Enter `152.55.176.2` when prompted"

## Why This Exists

Localtunnel added this to prevent malicious tunnels. The IP must match the server's public IP.

## Common Issues

| Issue | Fix |
|-------|-----|
| User gets "Bad Gateway" | Tunnel or HTTP server died — restart both |
| User can't access | They didn't enter the IP correctly |
| Tunnel goes stale | Tunnels timeout after inactivity — restart |

## Automation Tip

```bash
# Start both together
nohup python3 -m http.server 8080 >/tmp/server.log 2>&1 &
sleep 2
nohup lt --port 8080 >/tmp/tunnel.log 2>&1 &
```

## Note

This security gate is unavoidable with free `lt`. For production, use:
- Cloudflare Tunnel (`cloudflared`)
- Ngrok (paid for custom domains)
- Direct VPS with Nginx + Let's Encrypt