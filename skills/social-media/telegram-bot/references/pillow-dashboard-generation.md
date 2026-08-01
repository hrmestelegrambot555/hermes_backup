# Pillow Dashboard Image Generation

When no browser/screenshot tools are available, use Python Pillow to generate dashboard images.

## Basic Pattern

```python
from PIL import Image, ImageDraw, ImageFont

W, H = 800, 1100
img = Image.new('RGB', (W, H), '#0a0b0d')
draw = ImageDraw.Draw(img)

# Load fonts
font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

# Draw rounded rectangle
def draw_rounded_rect(draw, xy, fill, radius=12):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0+radius, y0, x1-radius, y1], fill=fill)
    draw.rectangle([x0, y0+radius, x1, y1-radius], fill=fill)
    draw.pieslice([x0, y0, x0+2*radius, y0+2*radius], 180, 270, fill=fill)
    draw.pieslice([x1-2*radius, y0, x1, y0+2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1-2*radius, x0+2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1-2*radius, y1-2*radius, x1, y1], 0, 90, fill=fill)

# Draw badge
def draw_badge(draw, x, y, text, color, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw_rounded_rect(draw, (x, y, x+tw+20, y+24), fill=color)
    draw.text((x+10, y+4), text, fill='#0a0b0d', font=font)

# Save
img.save('dashboard.png', 'PNG')
```

## Common Pitfalls

1. **Rectangle coordinates**: Use `[(x0, y0), (x1, y1)]` NOT `[(x0, y0, x1, y1)]`
2. **Font not found**: Fall back to `ImageFont.load_default()` if custom font unavailable
3. **Text alignment**: Use `anchor='mt'` for center-aligned text: `draw.text((x, y), text, anchor='mt')`

## Sending Images via Telegram Bot API

```bash
curl -s -X POST "https://api.telegram.org/botTOKEN/sendPhoto" \
  -F chat_id=CHAT_ID \
  -F photo=@/path/to/image.png \
  -F caption="Caption text"
```
