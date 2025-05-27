import os
import re
import random
import math
import asyncio
from io import BytesIO

import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL

# ---- FONTS ----
FONTS = {
    "cfont": ImageFont.truetype("BADMUSIC/assets/cfont.ttf", 15),
    "dfont": ImageFont.truetype("BADMUSIC/assets/font2.otf", 12),
    "nfont": ImageFont.truetype("BADMUSIC/assets/font.ttf", 10),
    "tfont": ImageFont.truetype("BADMUSIC/assets/font.ttf", 20),
    "title": ImageFont.truetype("BADMUSIC/assets/font3.ttf", 45),
    "arial": ImageFont.truetype("BADMUSIC/assets/font2.ttf", 30),
    "mainfont": ImageFont.truetype("BADMUSIC/assets/font.ttf", 30),
}

def get_fitting_font(font_path, text, box_width, max_font_size=20, min_font_size=10):
    """
    Dynamically adjust font size to fit text within the given box width.
    """
    font_size = max_font_size
    while font_size >= min_font_size:
        font = ImageFont.truetype(font_path, font_size)
        text_width, _ = font.getsize(text)
        if text_width <= box_width:
            return font
        font_size -= 1
    return ImageFont.truetype(font_path, min_font_size)

def truncate_text_to_fit(font_path, text, box_width, max_font_size=20, min_font_size=10):
    """
    Truncate and resize the text so it fits in the box.
    """
    font = get_fitting_font(font_path, text, box_width, max_font_size, min_font_size)
    text_width, _ = font.getsize(text)
    if text_width <= box_width:
        return text, font
    # If still not fitting, truncate and add ...
    for i in range(len(text), 0, -1):
        truncated = text[:i] + "..."
        font = get_fitting_font(font_path, truncated, box_width, max_font_size, min_font_size)
        text_width, _ = font.getsize(truncated)
        if text_width <= box_width:
            return truncated, font
    return "...", font  # fallback

def resize_youtube_thumbnail(img: Image.Image) -> Image.Image:
    target_size = 640
    aspect_ratio = img.width / img.height
    if aspect_ratio > 1:
        new_width = int(target_size * aspect_ratio)
        new_height = target_size
    else:
        new_width = target_size
        new_height = int(target_size / aspect_ratio)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    left = (img.width - target_size) // 2
    top = (img.height - target_size) // 2
    right = left + target_size
    bottom = top + target_size
    return img.crop((left, top, right, bottom))

def clean_text(text: str, limit: int = 17) -> str:
    text = text.strip()
    return f"{text[:limit - 3]}..." if len(text) > limit else text

def add_controls(img: Image.Image) -> Image.Image:
    img = img.filter(ImageFilter.GaussianBlur(25))
    box = (120, 120, 520, 480)
    region = img.crop(box)
    controls = Image.open("BADMUSIC/assets/thum.png").convert("RGBA")
    dark_region = ImageEnhance.Brightness(region).enhance(0.5)
    mask = Image.new("L", dark_region.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, box[2] - box[0], box[3] - box[1]), 40, fill=255
    )
    img.paste(dark_region, box, mask)
    img.paste(controls, (135, 305), controls)
    return img

def make_sq(image: Image.Image, size: int = 125) -> Image.Image:
    width, height = image.size
    side_length = min(width, height)
    crop = image.crop(
        (
            (width - side_length) // 2,
            (height - side_length) // 2,
            (width + side_length) // 2,
            (height + side_length) // 2,
        )
    )
    resize = crop.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=30, fill=255)
    rounded = ImageOps.fit(resize, (size, size))
    rounded.putalpha(mask)
    return rounded

def get_duration(duration: int, time: str = "0:24") -> str:
    try:
        m1, s1 = divmod(duration, 60)
        m2, s2 = map(int, time.split(":"))
        sec = (m1 * 60 + s1) - (m2 * 60 + s2)
        _min, sec = divmod(sec, 60)
        return f"{_min}:{sec:02d}"
    except Exception:
        return "0:00"

async def fetch_image(url: str) -> Image.Image | None:
    if not url:
        return None
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=5) as response:
                if response.status != 200:
                    return None
                data = await response.read()
                img = Image.open(BytesIO(data)).convert("RGBA")
                if url.startswith("https://i.ytimg.com"):
                    img = resize_youtube_thumbnail(img)
                return img
        except Exception:
            return None

async def get_thumb(videoid: str) -> str:
    """
    Generates and saves a new styled YouTube thumbnail for the given videoid.
    Returns the path to the generated image.
    """
    save_dir = f"cache/{videoid}_v5.png"
    if os.path.isfile(save_dir):
        return save_dir

    # Fetch video details from YouTube
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = await VideosSearch(url, limit=1).next()
        if not results or not results.get("result"):
            return YOUTUBE_IMG_URL
        result = results["result"][0]
    except Exception as e:
        print(f"Error fetching YouTube results: {e}")
        return YOUTUBE_IMG_URL

    # Extract info
    title = re.sub(r"\W+", " ", result.get("title", "Unsupported Title")).title()
    channel = result.get("channel", {}).get("name", "Unknown Channel")
    duration_str = result.get("duration", "0:00")
    try:
        parts = [int(p) for p in duration_str.split(":")]
        duration = 0
        if len(parts) == 3:
            duration = parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            duration = parts[0] * 60 + parts[1]
        else:
            duration = 0
    except Exception:
        duration = 0
    thumbnail_url = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0] or YOUTUBE_IMG_URL

    # Download & process thumbnail
    thumb = await fetch_image(thumbnail_url)
    if not thumb:
        return YOUTUBE_IMG_URL

    # Compose background and controls
    bg = add_controls(thumb)
    image = make_sq(thumb)

    # Paste album art
    paste_x, paste_y = 145, 155
    bg.paste(image, (paste_x, paste_y), image)

    # Draw text
    draw = ImageDraw.Draw(bg)

    # BADMUSIC label
    draw.text((285, 180), "BADMUSIC", (192, 192, 192), font=FONTS["nfont"])
    # Title (dynamic sized font and truncation now)
    title_box_x = 285
    title_box_y = 200
    title_box_width = 230  # max width for title
    safe_title, fitting_title_font = truncate_text_to_fit("BADMUSIC/assets/font.ttf", title, title_box_width, max_font_size=10, min_font_size=5)
    draw.text((title_box_x, title_box_y), safe_title, (255, 255, 255), font=fitting_title_font)
    # Channel
    draw.text((287, 235), clean_text(channel, 20), (255, 255, 255), font=FONTS["cfont"])
    # Duration
    draw.text((478, 321), get_duration(duration), (192, 192, 192), font=FONTS["dfont"])

    bg.save(save_dir)
    return save_dir

# Example usage:
# path = await get_thumb("dQw4w9WgXcQ")
