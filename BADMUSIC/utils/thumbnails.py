import os
import re
import asyncio
from io import BytesIO

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
    "title": ImageFont.truetype("BADMUSIC/assets/font3.ttf", 32),
    "arial": ImageFont.truetype("BADMUSIC/assets/font2.ttf", 30),
    "mainfont": ImageFont.truetype("BADMUSIC/assets/font.ttf", 30),
}


def get_fitting_font(font_path, text, box_width, max_font_size=20, min_font_size=10):
    """Returns a font size that fits the text in the given width."""
    font_size = max_font_size
    while font_size >= min_font_size:
        font = ImageFont.truetype(font_path, font_size)
        if font.getlength(text) <= box_width:
            return font
        font_size -= 1
    return ImageFont.truetype(font_path, min_font_size)


def truncate_text_to_fit(font_path, text, box_width, max_font_size=20, min_font_size=10):
    """Truncates and resizes text to fit the width limit."""
    font = get_fitting_font(font_path, text, box_width, max_font_size, min_font_size)
    if font.getlength(text) <= box_width:
        return text, font
    for i in range(len(text), 0, -1):
        truncated = text[:i] + "..."
        font = get_fitting_font(font_path, truncated, box_width, max_font_size, min_font_size)
        if font.getlength(truncated) <= box_width:
            return truncated, font
    return "...", font


from PIL import Image

def resize_youtube_thumbnail(img: Image.Image) -> Image.Image:
    """Resize thumbnail to 1280x720 (YouTube standard size)."""
    target_width, target_height = 1280, 720
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        new_height = target_height
        new_width = int(new_height * img_ratio)
    else:
        new_width = target_width
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    left = (img.width - target_width) // 2
    top = (img.height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    return img.crop((left, top, right, bottom))


def clean_text(text: str, limit: int = 17) -> str:
    return f"{text.strip()[:limit - 3]}..." if len(text.strip()) > limit else text.strip()

def add_controls(img: Image.Image) -> Image.Image:
    """Add blur and overlay controls to thumbnail background."""
    img = img.filter(ImageFilter.GaussianBlur(25))
    box = (120, 120, 520, 480)

    region = img.crop(box)
    controls = Image.open("BADMUSIC/assets/thum.png").convert("RGBA")
    dark_region = ImageEnhance.Brightness(region).enhance(0.5)
    mask = Image.new("L", dark_region.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, box[2] - box[0], box[3] - box[1]), 40, fill=255)


    img.paste(dark_region, box, mask)
    img.paste(controls, (135, 305), controls)
    return img


def make_sq(image: Image.Image, size: int = 125) -> Image.Image:
    """Make square rounded album art image."""
    width, height = image.size
    side = min(width, height)
    crop = image.crop(((width - side) // 2, (height - side) // 2,
                       (width + side) // 2, (height + side) // 2))
    resize = crop.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), 30, fill=255)
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


async def get_thumb(videoid: str) -> str:
    save_path = f"cache/{videoid}_v5.png"
    if os.path.exists(save_path):
        return save_path

    # YouTube data fetch
    try:
        results = await VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1).next()
        result = results.get("result", [{}])[0]
    except Exception:
        return YOUTUBE_IMG_URL

    title = re.sub(r"\W+", " ", result.get("title", "Unknown Title")).title()
    channel = result.get("channel", {}).get("name", "Unknown Channel")
    duration_str = result.get("duration", "0:00")
    parts = list(map(int, duration_str.split(":")))
    duration = sum(part * 60 ** i for i, part in enumerate(reversed(parts)))
    thumbnail_url = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0] or YOUTUBE_IMG_URL

    thumb = await fetch_image(thumbnail_url)
    if not thumb:
        return YOUTUBE_IMG_URL

    bg = add_controls(thumb)
    draw = ImageDraw.Draw(bg)

    # Make square album art (left side)
    art = make_sq(thumb, size=180)
    art_pos = (60, (bg.height - art.height) // 2)  # Left margin 60 px, vertically center
    bg.paste(art, art_pos, art)

    center_x = bg.width // 2

    # Title (top center)
    safe_title, font_title = truncate_text_to_fit(
        "BADMUSIC/assets/font.ttf", title, box_width=600, max_font_size=28, min_font_size=14
    )
    title_size = font_title.getsize(safe_title)
    title_x = center_x - title_size[0] // 2
    title_y = 50
    draw.text((title_x, title_y), safe_title, (255, 255, 255), font=font_title)

    # Channel and Duration on the right side of album art (vertical stack)
    right_x = art_pos[0] + art.width + 30  # 30 px gap from album art
    total_text_height = 0

    # Channel Name
    channel_text = clean_text(channel, 30)
    font_channel = get_fitting_font("BADMUSIC/assets/font2.otf", channel_text, 350, 20, 12)
    channel_size = font_channel.getsize(channel_text)
    channel_y = (bg.height - channel_size[1] * 2 - 10) // 2  # leave 10 px gap between channel and duration
    draw.text((right_x, channel_y), channel_text, (200, 200, 200), font=font_channel)

    # Duration below channel
    duration_text = get_duration(duration)
    font_duration = get_fitting_font("BADMUSIC/assets/font2.otf", duration_text, 350, 20, 12)
    dur_size = font_duration.getsize(duration_text)
    duration_y = channel_y + channel_size[1] + 10
    draw.text((right_x, duration_y), duration_text, (192, 192, 192), font=font_duration)

    os.makedirs("cache", exist_ok=True)
    bg.save(save_path)
    return save_path
