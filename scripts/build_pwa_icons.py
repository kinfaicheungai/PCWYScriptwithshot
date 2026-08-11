from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SITE = Path(__file__).resolve().parents[1]
font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
for size in (192, 512):
    image = Image.new("RGB", (size, size), "#17191c")
    draw = ImageDraw.Draw(image)
    margin = round(size * 0.08)
    draw.rectangle((margin, margin, size - margin, size - margin), outline="#a92324", width=max(3, size // 64))
    font = ImageFont.truetype(font_path, round(size * 0.25))
    text = "PC"
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(((size - (box[2] - box[0])) / 2, (size - (box[3] - box[1])) / 2 - box[1]), text, fill="#f4f0e7", font=font)
    image.save(SITE / f"public/pwa-{size}.png", optimize=True)

