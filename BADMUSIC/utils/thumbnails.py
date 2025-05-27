import os
import re
import math
import asyncio
from io import BytesIO

import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from config import YOUTUBE_IMG_URL
from youtubesearchpython.__future__ import VideosSearch
from BADMUSIC import app

# --- Font loading utility (robust fallback) ---
def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

FONTS = {
    "title": load_font("BADMUSIC/assets/font3.ttf", 50),    # Bold, large
    "info": load_font("BADMUSIC/assets/font2.ttf", 35),     # Clean info
    "time": load_font("BADMUSIC/assets/font.ttf", 30),      # Duration
}

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight), Image.LANCZOS)

def truncate(text, max_length=25):
    words = text.split(" ")
    text1, text2 = "", ""
    for word in words:
        if len(text1) + len(word) < max_length:
            text1 += " " + word
        elif len(text2) + len(word) < max_length:
            text2 += " " + word
    return [text1.strip(), text2.strip()]

def create_gradient_background(width, height, color1, color2):
    base = Image.new('RGBA', (width, height), color1)
    top = Image.new('RGBA', (width, height), color2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        v = int(255 * (y / (height - 1)))
        mask_data.extend([v] * width)
    mask.putdata(mask_data)
    return Image.composite(top, base, mask)

def create_rgb_neon_circle(image, center, radius, border_width, steps=40):
    draw = ImageDraw.Draw(image)
    for step in range(steps):
        t = step / steps * math.pi * 2
        red = int((math.sin(t) * 127) + 128)
        green = int((math.sin(t + math.pi / 3) * 127) + 128)
        blue = int((math.sin(t + math.pi * 2 / 3) * 127) + 128)
        alpha = int(255 * (1 - step / steps))
        draw.ellipse([
            center[0] - radius - border_width + step,
            center[1] - radius - border_width + step,
            center[0] + radius + border_width - step,
            center[1] + radius + border_width - step
        ], outline=(red, green, blue, alpha), width=max(border_width // steps, 1))
    return image

def crop_center_circle(img, output_size, border, crop_scale=1.4):
    half_width, half_height = img.size[0] / 2, img.size[1] / 2
    larger_size = int(output_size * crop_scale)
    img = img.crop((
        half_width - larger_size / 2,
        half_height - larger_size / 2,
        half_width + larger_size / 2,
        half_height + larger_size / 2
    ))
    img = img.resize((output_size - 2 * border, output_size - 2 * border), Image.LANCZOS)
    final_img = Image.new("RGBA", (output_size, output_size), (0, 0, 0, 0))
    mask_main = Image.new("L", (output_size - 2 * border, output_size - 2 * border), 0)
    draw_main = ImageDraw.Draw(mask_main)
    draw_main.ellipse((0, 0, output_size - 2 * border, output_size - 2 * border), fill=255)
    final_img.paste(img, (border, border), mask_main)
    mask_border = Image.new("L", (output_size, output_size), 0)
    draw_border = ImageDraw.Draw(mask_border)
    draw_border.ellipse((0, 0, output_size, output_size), fill=255)
    result = Image.composite(final_img, Image.new("RGBA", final_img.size, (0, 0, 0, 0)), mask_border)
    center = (output_size // 2, output_size // 2)
    radius = (output_size - 2 * border) // 2
    return create_rgb_neon_circle(result, center, radius, 15)

async def get_thumb(videoid):
    """
    Generate a vibrant YouTube thumbnail in BADMUSIC/assets style.
    Returns path to saved image.
    """
    cache_path = f"cache/{videoid}_ytthumb.png"
    if os.path.isfile(cache_path):
        return cache_path

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = await VideosSearch(url, limit=1).next()
        if not results or not results.get("result"):
            return YOUTUBE_IMG_URL
        result = results["result"][0]
    except Exception as e:
        print(f"Error fetching YouTube results: {e}")
        return YOUTUBE_IMG_URL

    title = re.sub(r"\W+", " ", result.get("title", "Unsupported Title")).title()
    duration = result.get("duration", "Unknown Mins")
    thumbnail = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0] or YOUTUBE_IMG_URL
    views = result.get("viewCount", {}).get("short", "Unknown Views")
    channel = result.get("channel", {}).get("name", "Unknown Channel")

    temp_thumb = f"cache/thumb_{videoid}.png"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(temp_thumb, mode="wb") as f:
                        await f.write(await resp.read())
                else:
                    return YOUTUBE_IMG_URL

        youtube = Image.open(temp_thumb).convert("RGBA")
        image = changeImageSize(1280, 720, youtube)
        image = image.convert("RGBA")

        # Gradient background
        gradient_bg = create_gradient_background(1280, 720, (50, 0, 100), (0, 150, 255))
        background = gradient_bg.filter(ImageFilter.GaussianBlur(10))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.8)
        draw = ImageDraw.Draw(background)

        # Neon circular thumbnail
        circle_thumbnail = crop_center_circle(youtube, 450, 25)
        background.paste(circle_thumbnail, (100, 135), circle_thumbnail)

        # Title (shadow + main)
        title_lines = truncate(title, 25)
        shadow_offset = 3
        for i, line in enumerate(title_lines):
            if line:
                x, y = 600, 150 + i * 60
                draw.text((x + shadow_offset, y + shadow_offset), line, fill=(0, 0, 0, 128), font=FONTS["title"])
                draw.text((x, y), line, fill=(255, 255, 255), font=FONTS["title"])

        # Channel and views
        info_text = f"{channel} | {views[:20]}"
        draw.text((600 + shadow_offset, 270 + shadow_offset), info_text, fill=(0, 0, 0, 128), font=FONTS["info"])
        draw.text((600, 270), info_text, fill=(255, 255, 255), font=FONTS["info"])

        # Progress bar
        line_length = 600
        progress = int(line_length * 0.7)
        draw.rectangle([(600, 350, 600 + line_length, 360)], fill=(50, 50, 50))
        draw.rectangle([(600, 350, 600 + progress, 360)], fill=(255, 50, 50))
        draw.ellipse([600 + progress - 10, 350 - 5, 600 + progress + 10, 360 + 5], fill=(255, 50, 50))
        draw.text((600, 370), "00:00", (255, 255, 255), font=FONTS["time"])
        draw.text((1100, 370), duration, (255, 255, 255), font=FONTS["time"])

        # Play icons (optional)
        try:
            play_icons = Image.open("BADMUSIC/assets/play_icons.png").resize((600, 70), Image.LANCZOS)
            if play_icons.mode != "RGBA":
                play_icons = play_icons.convert("RGBA")
            background.paste(play_icons, (600, 420), play_icons)
        except FileNotFoundError:
            print("Play icons file not found, skipping.")

        # Border glow
        border_width = 20
        border_color = (255, 50, 100, 200)
        final_image = Image.new("RGBA", (1280 + 2 * border_width, 720 + 2 * border_width), border_color)
        final_image.paste(background, (border_width, border_width))

        # Clean up and save
        if os.path.exists(temp_thumb):
            os.remove(temp_thumb)
        final_image.save(cache_path, quality=95)
        return cache_path
    except Exception as e:
        print(f"Error processing thumbnail: {e}")
        if os.path.exists(temp_thumb):
            os.remove(temp_thumb)
        return YOUTUBE_IMG_URL
