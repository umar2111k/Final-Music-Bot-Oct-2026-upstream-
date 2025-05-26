import os
import math
import textwrap
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

async def fetch_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.read()

async def gen_thumb(videoid, title, views, duration, channel):
    try:
        thumb_url = f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg"
        thumb_data = await fetch_image(thumb_url)
        image = Image.open(BytesIO(thumb_data)).convert("RGB")
    except:
        thumb_url = f"https://img.youtube.com/vi/{videoid}/hqdefault.jpg"
        thumb_data = await fetch_image(thumb_url)
        image = Image.open(BytesIO(thumb_data)).convert("RGB")

    image = image.resize((1280, 720))
    draw = ImageDraw.Draw(image)

    # Load fonts
    title_font = ImageFont.truetype("assets/font2.ttf", 70)
    info_font = ImageFont.truetype("assets/font2.ttf", 40)
    small_font = ImageFont.truetype("assets/font2.ttf", 35)

    # Blur background strip for text
    text_bg = image.crop((0, 550, 1280, 720)).filter(ImageFilter.GaussianBlur(10))
    image.paste(text_bg, (0, 550))

    # Gradient bar
    bar = Image.new("RGB", (1280, 20), color=0)
    gradient = ImageDraw.Draw(bar)
    for i in range(1280):
        r = int(255 * (i / 1280))
        g = int(255 * ((1280 - i) / 1280))
        b = 255
        gradient.line([(i, 0), (i, 20)], fill=(r, g, b))
    image.paste(bar, (0, 700))

    # Channel, views, duration
    draw.text((30, 560), f"Channel: {channel}", font=info_font, fill="white")
    draw.text((30, 610), f"Views: {views}", font=info_font, fill="white")
    draw.text((30, 660), f"Duration: {duration}", font=info_font, fill="white")

    # Title wrap
    wrapped_title = textwrap.fill(title, width=35)
    draw.text((30, 30), wrapped_title, font=title_font, fill="white")

    # Watermark
    draw.text((1000, 670), "MyMusicBot", font=small_font, fill="lightgray")

    # Optional neon ring or profile photo (extend here as needed)

    out_path = f"downloads/thumb_{videoid}.png"
    image.save(out_path, "PNG")
    return out_path
