# Vera Merchant Console

Static frontend prototype for magicpin's Vera merchant assistant dashboard.

## Run

Preferred: run the combined backend + frontend server from the repo root:

```bash
python3 bot.py --host 127.0.0.1 --port 8080
```

Then visit `http://127.0.0.1:8080`.

You can still open `index.html` directly for UI-only viewing, but the `/v1/*` backend endpoints are available only through `bot.py`.

## Included

- Responsive SaaS dashboard layout with sidebar, chat, and right context panel
- Dark mode toggle
- Search and category filters
- WhatsApp-style merchant conversation bubbles
- Trigger cards, suggested actions, merchant statistics, and customer context
- Toasts, loading skeletons, typing indicators, auto-scroll, expandable panels
- Animated metric cards and SVG trend chart
