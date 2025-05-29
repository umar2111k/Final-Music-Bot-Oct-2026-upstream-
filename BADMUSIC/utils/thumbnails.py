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

def add_controls(img: Image.Image, artist_img: Image.Image, song_name: str, channel_name: str) -> Image.Image:
    """Add blur and overlay controls + artist + song info to thumbnail background."""
    img = img.filter(ImageFilter.GaussianBlur(25))
    
    controls = Image.open("BADMUSIC/assets/thum.png").convert("RGBA")
    ctrl_w, ctrl_h = controls.size

    # Center coordinates for box
    center_x = img.width // 2
    center_y = img.height // 2
    left = center_x - ctrl_w // 2
    top = center_y - ctrl_h // 2
    right = left + ctrl_w
    bottom = top + ctrl_h
    box = (left, top, right, bottom)

    # Crop region, darken and mask
    region = img.crop(box)
    dark_region = ImageEnhance.Brightness(region).enhance(0.5)
    mask = Image.new("L", dark_region.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, ctrl_w, ctrl_h), 40, fill=255)
    img.paste(dark_region, box, mask)

    # Paste artist image (left top corner inside box)
    artist_resized = artist_img.resize((90, 90)).convert("RGBA")
    artist_pos = (left + 20, top + 20)
    img.paste(artist_resized, artist_pos, artist_resized)

    # Text section (right of artist)
    draw = ImageDraw.Draw(img)
    font_bold = ImageFont.truetype("BADMUSIC/assets/font.ttf", 26)
    font_song = ImageFont.truetype("BADMUSIC/assets/font2.otf", 22)
    font_channel = ImageFont.truetype("BADMUSIC/assets/font2.otf", 18)

    text_x = artist_pos[0] + artist_resized.width + 20
    text_y = artist_pos[1]

    draw.text((text_x, text_y), "BAD MUSIC", font=font_bold, fill="white")
    draw.text((text_x, text_y + 32), song_name, font=font_song, fill="white")
    draw.text((text_x, text_y + 62), channel_name, font=font_channel, fill="lightgray")

    # Paste thumb.png at center bottom of box
    thumb_pos_x = center_x - ctrl_w // 2
    thumb_pos_y = bottom - controls.height - 10
    img.paste(controls, (thumb_pos_x, thumb_pos_y), controls)

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


async def fetch_image(url: str) -> Image.Image | None:
    """Fetch image from URL asynchronously."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    return Image.open(BytesIO(data)).convert("RGBA")
    except Exception:
        return None

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
    thumbnail_url = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0] or YOUTUBE_IMG_URL

    thumb = await fetch_image(thumbnail_url)
    if not thumb:
        return YOUTUBE_IMG_URL

    # Background blur
    bg = thumb.copy()

    # Artist art
    artist_img = make_sq(thumb, size=100)

    # Add everything in box
    bg = add_controls(bg, artist_img, clean_text(title, 35), clean_text(channel, 25))

    os.makedirs("cache", exist_ok=True)
    bg.save(save_path)
    return save_path
