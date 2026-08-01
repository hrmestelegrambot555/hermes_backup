# Cloudflare Workers Single-File Translator

## Pattern
All HTML/CSS/JS in one `index.js` file. No build step, no framework.

## Architecture
```javascript
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // API endpoint
    if (url.pathname === '/api/translate' && request.method === 'POST') {
      const body = await request.text();
      const params = new URLSearchParams(body);
      // ... translate logic
      return new Response(JSON.stringify(result), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      });
    }
    
    // Serve HTML page (inline string)
    return new Response(HTML_PAGE, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  }
};
```

## Key Patterns
1. **HTML as const string** — embed full HTML/CSS/JS in a template literal
2. **Fetch from inside Worker** — can call external APIs (Google Translate, etc.)
3. **CORS headers** — add `Access-Control-Allow-Origin: *` for API responses
4. **No environment variables needed** for basic usage (free Google Translate API)
5. **localStorage** for client-side state (language preferences, history)

## Deployment
1. Go to https://dash.cloudflare.com
2. Workers & Pages → Create Worker
3. Paste `index.js` content
4. Save & Deploy

## Limitations
- No GPU (CPU only)
- No persistent storage (use KV for that)
- 10ms CPU time on free plan
- 128MB memory limit

## Translation Backends (Free)
1. **Google Translate** — `https://translate.googleapis.com/translate_a/single?client=gtx&sl={src}&tl={tgt}&dt=t&q={text}`
2. **MyMemory** — `https://api.mymemory.translated.net/get?q={text}&langpair={src}|{tgt}`
3. **LibreTranslate** — self-hosted or public instances
