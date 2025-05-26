import os, re, random, aiofiles, aiohttp, math
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch
from BADMUSIC import app
from config import YOUTUBE_IMG_URL

# Fonts load karo
arial = ImageFont.truetype("BADMUSIC/assets/font2.ttf", 30)
font = ImageFont.truetype("BADMUSIC/assets/font.ttf", 30)
title_font = ImageFont.truetype("BADMUSIC/assets/font3.ttf", 45)

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))

def truncate(text):
    words = text.split(" ")
    text1, text2 = "", ""
    for word in words:
        if len(text1) + len(word) < 30:
            text1 += " " + word
        elif len(text2) + len(word) < 30:
            text2 += " " + word
    return [text1.strip(), text2.strip()]

def generate_light_dark_color():
    return (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))

def get_neon_colors(n):
    # 10-11 rang ki list banayenge (hue rotation)
    colors = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        r = int((math.sin(angle) * 127) + 128)
        g = int((math.sin(angle + 2*math.pi/3) * 127) + 128)
        b = int((math.sin(angle + 4*math.pi/3) * 127) + 128)
        colors.append((r, g, b))
    return colors

def create_rgb_neon_circle(image, center, radius, border_width, steps=11):
    # Steps = colors ki sankhya (10-11)
    draw = ImageDraw.Draw(image)
    colors = get_neon_colors(steps)
    for step in range(steps):
        offset = step * 2  # Chhota difference
        draw.ellipse([
            center[0] - radius - border_width + offset,
            center[1] - radius - border_width + offset,
            center[0] + radius + border_width - offset,
            center[1] + radius + border_width - offset
        ], outline=colors[step % len(colors)], width=border_width)
    return image

def crop_center_circle(img, output_size, border, crop_scale=1.5):
    half_width, half_height = img.size[0] / 2, img.size[1] / 2
    larger_size = int(output_size * crop_scale)
    img = img.crop((
        half_width - larger_size / 2,
        half_height - larger_size / 2,
        half_width + larger_size / 2,
        half_height + larger_size / 2
    ))
    img = img.resize((output_size - 2 * border, output_size - 2 * border))
    final_img = Image.new("RGBA", (output_size, output_size), (0,0,0,0))
    mask_main = Image.new("L", (output_size - 2 * border, output_size - 2 * border), 0)
    draw_main = ImageDraw.Draw(mask_main)
    draw_main.ellipse((0, 0, output_size - 2 * border, output_size - 2 * border), fill=255)
    final_img.paste(img, (border, border), mask_main)
    # Ab border bhi colorful banayenge
    mask_border = Image.new("L", (output_size, output_size), 0)
    draw_border = ImageDraw.Draw(mask_border)
    draw_border.ellipse((0, 0, output_size, output_size), fill=255)
    result = Image.composite(final_img, Image.new("RGBA", final_img.size, (0, 0, 0, 0)), mask_border)
    center = (output_size // 2, output_size // 2)
    radius = (output_size - 2 * border) // 2
    # Neon circle ka size chhota kar diya
    return create_rgb_neon_circle(result, center, radius-12, 7, steps=11)

async def get_thumb(videoid):
    # Check cache
    if os.path.isfile(f"cache/{videoid}_v4.png"):
        return f"cache/{videoid}_v4.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = await VideosSearch(url, limit=1).next()
        if not results or not results.get("result"):
            return YOUTUBE_IMG_URL
        result = results["result"][0]
    except Exception as e:
        print(f"Error fetching YouTube results: {e}")
        return YOUTUBE_IMG_URL

    title = re.sub("\W+", " ", result.get("title", "Unsupported Title")).title()
    duration = result.get("duration", "Unknown Mins")
    thumbnail = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0] or YOUTUBE_IMG_URL
    views = result.get("viewCount", {}).get("short", "Unknown Views")
    channel = result.get("channel", {}).get("name", "Unknown Channel")

    # Download thumbnail
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                async with aiofiles.open(f"cache/thumb{videoid}.png", mode="wb") as f:
                    await f.write(await resp.read())

    try:
        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        # Aur zyada blur (abhi 20 tha, ab 40)
        background = image2.filter(filter=ImageFilter.BoxBlur(40))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.55)
        draw = ImageDraw.Draw(background)

        # Song ki circular DP chhota aur attractive
        circle_thumbnail = crop_center_circle(youtube, 220, 12)  # Pehle 400 tha, ab 220 aur border 12
        circle_thumbnail = circle_thumbnail.resize((220, 220))
        # Placement mast: left-center side
        background.paste(circle_thumbnail, (80, 250), circle_thumbnail)

        # Song details (title, channel, views) attractive style
        title1 = truncate(title)
        # White ki jagah now gradient color
        text_color = (255, 222, 89)
        shadow_color = (50, 10, 80)
        # Shadow for title
        for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]:
            draw.text((320+dx, 260+dy), title1[0], font=title_font, fill=shadow_color)
        draw.text((320, 260), title1[0], font=title_font, fill=text_color)
        if title1[1]:
            for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]:
                draw.text((320+dx, 310+dy), title1[1], font=title_font, fill=shadow_color)
            draw.text((320, 310), title1[1], font=title_font, fill=text_color)

        # Channel + views
        info_text = f"{channel}  |  {views[:23]}"
        draw.text((320, 360), info_text, (224, 255, 255), font=arial)

        # BAD watermark
        draw.text((20, 20), "BAD", fill=(255, 100, 60), font=font)

        # Progress bar (gradient style)
        line_length = 550
        red_length = int(line_length * 0.6)
        grad_start = (255, 120, 140)
        grad_end = (80, 200, 255)
        for i in range(red_length):
            color = (
                grad_start[0] + (grad_end[0] - grad_start[0]) * i // red_length,
                grad_start[1] + (grad_end[1] - grad_start[1]) * i // red_length,
                grad_start[2] + (grad_end[2] - grad_start[2]) * i // red_length,
            )
            draw.line([(320+i, 420), (320+i, 420+7)], fill=color, width=7)
        draw.line([(320+red_length, 420), (320+line_length, 420)], fill=(255,255,255), width=6)
        draw.ellipse([320+red_length-10, 420-8, 320+red_length+10, 420+10], fill=(255, 99, 71))
        draw.text((320, 440), "00:00", (255, 255, 255), font=arial)
        draw.text((320+line_length-80, 440), duration, (255, 255, 255), font=arial)

        # Play icons
        play_icons = Image.open("BADMUSIC/assets/play_icons.png").resize((line_length, 52))
        background.paste(play_icons, (320, 480), play_icons)

        # Stroke effect (ab colorful, not white)
        stroke_width = 18
        stroke_color = generate_light_dark_color()
        stroke_image = Image.new("RGBA", (1280 + 2 * stroke_width, 720 + 2 * stroke_width), stroke_color)
        stroke_image.paste(background, (stroke_width, stroke_width))

        os.remove(f"cache/thumb{videoid}.png")
        stroke_image.save(f"cache/{videoid}_v4.png")
        return f"cache/{videoid}_v4.png"
    except Exception as e:
        print(f"Error processing thumbnail: {e}")
        return YOUTUBE_IMG_URL
    
