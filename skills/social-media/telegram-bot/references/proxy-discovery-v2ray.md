# Proxy Discovery and V2Ray Configuration

## Proxy Sources (Reliable)

| Source | Type | Reliability | Notes |
|--------|------|-------------|-------|
| V2RayAggregator | VMess/SS/Trojan | High | Most comprehensive, 4000+ configs |
| ErcinDedeoglu/proxies | VMess/SS | Medium | Smaller but curated |
| barry-far/V2ray-Configs | Mixed | Medium | May have stale entries |
| mahdibland/V2RayAggregator | Mixed | High | sub_merge.txt has all proxies |

## Reliable Source URLs

```python
sources = [
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/all",
]
```

## Extracting VMess Proxies

VMess configs are base64-encoded JSON:

```python
import base64, json, re

def extract_vmess(text):
    matches = re.findall(r'vmess://([A-Za-z0-9+/=]+)', text)
    proxies = []
    for encoded in matches:
        try:
            data = json.loads(base64.b64decode(encoded))
            proxies.append({
                "server": data.get("add", ""),
                "port": int(data.get("port", 0)),
                "uuid": data.get("id", ""),
                "alterId": data.get("aid", 0),
                "net": data.get("net", "tcp"),
                "host": data.get("host", ""),
                "path": data.get("path", ""),
                "tls": data.get("tls", "none"),
                "name": data.get("ps", "vmess")
            })
        except:
            pass
    return proxies
```

## Extracting Shadowsocks Proxies

```python
def extract_ss(text):
    matches = re.findall(r'ss://([A-Za-z0-9+/=]+)@([0-9.]+):(\d+)#(.+)', text)
    return [{"password": enc, "server": srv, "port": int(port), "name": name}
            for enc, srv, port, name in matches]
```

## Extracting Trojan Proxies

```python
def extract_trojan(text):
    matches = re.findall(r'trojan://([^@]+)@([0-9.]+):(\d+)\?([^#]*)#(.+)', text)
    return [{"password": pwd, "server": srv, "port": int(port), "name": name}
            for pwd, srv, port, params, name in matches]
```

## Testing Proxy Connectivity

```python
import socket, time

def test_proxy(server, port, timeout=3):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start = time.time()
        result = sock.connect_ex((server, port))
        elapsed = (time.time() - start) * 1000
        sock.close()
        return result == 0, elapsed
    except:
        return False, 0
```

## Creating V2Ray Config

```python
def create_v2ray_config(proxies):
    """Create V2Ray JSON config from proxy list"""
    inbound = [
        {"port": 10808, "protocol": "socks", "settings": {"udp": True}, "tag": "in"},
        {"port": 10809, "protocol": "http", "settings": {}, "tag": "http-in"}
    ]
    
    outbounds = []
    for i, p in enumerate(proxies):
        if p.get("type") == "vmess":
            outbounds.append({
                "protocol": "vmess",
                "settings": {
                    "vnext": [{
                        "address": p["server"],
                        "port": p["port"],
                        "users": [{"id": p["uuid"], "alterId": p.get("alterId", 0), "security": "auto"}]
                    }]
                },
                "streamSettings": {
                    "network": p.get("net", "tcp"),
                    "security": p.get("tls", "none"),
                    "wsSettings": {"path": p.get("path", ""), "headers": {"Host": p.get("host", "")}}
                },
                "tag": f"proxy-{i}"
            })
        elif p.get("type") == "ss":
            outbounds.append({
                "protocol": "shadowsocks",
                "settings": {"servers": [{"address": p["server"], "port": p["port"], "method": "aes-256-gcm", "password": p["password"]}]},
                "tag": f"proxy-{i}"
            })
    
    outbounds.append({"protocol": "freedom", "settings": {}, "tag": "direct"})
    
    return {
        "log": {"loglevel": "warning"},
        "inbounds": inbound,
        "outbounds": outbounds,
        "routing": {
            "domainStrategy": "IPIfNonMatch",
            "rules": [
                {"type": "field", "outboundTag": "direct", "domain": ["domain:ir"]},
                {"type": "field", "outboundTag": "proxy-0", "domain": ["geosite:telegram", "geosite:google"]}
            ]
        }
    }
```

## Creating Clash Config

```python
def create_clash_config(proxies):
    """Create Clash YAML config from proxy list"""
    import yaml
    
    clash_proxies = []
    for p in proxies:
        if p.get("type") == "vmess":
            clash_proxies.append({
                "name": p.get("name", f"VMess-{p['server'][:10]}"),
                "type": "vmess",
                "server": p["server"],
                "port": p["port"],
                "uuid": p["uuid"],
                "alterId": p.get("alterId", 0),
                "cipher": "auto",
                "network": p.get("net", "tcp"),
                "udp": True
            })
        elif p.get("type") == "ss":
            clash_proxies.append({
                "name": p.get("name", f"SS-{p['server'][:10]}"),
                "type": "ss",
                "server": p["server"],
                "port": p["port"],
                "password": p["password"],
                "cipher": "aes-256-gcm",
                "udp": True
            })
    
    return {
        "port": 7890,
        "socks-port": 7891,
        "allow-lan": False,
        "mode": "rule",
        "proxies": clash_proxies,
        "proxy-groups": [{"name": "Proxy", "type": "select", "proxies": [p["name"] for p in clash_proxies] + ["DIRECT"]}],
        "rules": [
            "DOMAIN-SUFFIX,t.me,Proxy",
            "DOMAIN-SUFFIX,telegram.org,Proxy",
            "GEOIP,IR,DIRECT",
            "MATCH,Proxy"
        ]
    }
```

## Key Pitfalls

1. **Public Telegram channels for proxies are rare** — Most are private or have stale content. Use GitHub sources instead.

2. **`t.me/s/` preview shows only ~20 recent posts** — For older messages, use `?before=MESSAGE_ID` pagination.

3. **Known unreliable sources** — These sites do NOT contain usable proxy links in their HTML:
   - `mtpro.xyz` — returns empty HTML
   - `mtproto.me` — returns empty HTML
   - `t.me/s/Chrome_Proxy` — contains gambling/motivational content, not proxies
   - `t.me/s/proxy_mtm`, `t.me/s/irproxy`, `t.me/s/mtproto_proxy` — exist but no proxies in recent posts
   - **Don't waste time scraping these** — go straight to GitHub sources.

3. **Iran filtering is aggressive** — Some proxies that work internationally may be blocked. Test latency from Iran or use Iran-friendly sources.

4. **Proxy passwords in GitHub repos are public** — Don't use these for sensitive traffic. For production, use self-hosted or paid proxies.

5. **VMess configs may have invalid UUIDs** — Always test connectivity before adding to config.

6. **Port 443 is often better** — TLS on port 443 is harder to block than other ports.

## Quick Test Script

```bash
#!/bin/bash
# Quick proxy test
SERVER=$1
PORT=$2
TIMEOUT=3

if timeout $TIMEOUT bash -c "echo >/dev/tcp/$SERVER/$PORT" 2>/dev/null; then
    echo "✅ $SERVER:$PORT is OPEN"
else
    echo "❌ $SERVER:$PORT is CLOSED"
fi
```
