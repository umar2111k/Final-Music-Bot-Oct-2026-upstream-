from pyrogram import Client, filters
import aiohttp
import os
import re
import asyncio
from BADMUSIC import app as bot

API_KEY = "badmusic_ytstream_apikey_2025"
BASE_URL = "http://3.0.146.239:1470/youtube"
YOUTUBE_URL_PATTERN = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'

def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

async def download_and_send(client, message, user_input, format):
    try:
        # Show chat action (Fix 1: string as argument)
        await message.reply_chat_action("upload_audio" if format == "mp3" else "upload_video")
    except Exception:
        pass  # Ignore if not available

    await message.reply_text(f"🔎 Fetching {format.upper()} for: `{user_input}`")

    params = {
        "format": format,
        "download": True,
        "api_key": API_KEY
    }

    if re.match(YOUTUBE_URL_PATTERN, user_input):
        params["url"] = user_input
    else:
        params["query"] = user_input

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL, params=params, timeout=60) as resp:
                if resp.status != 200:
                    return await message.reply_text(f"❌ API Error: {resp.status}")
                data = await resp.json()

            if "stream_url" not in data or not data.get("stream_url"):
                return await message.reply_text(f"❌ Stream URL missing: {data.get('detail', 'Unknown error')}")

            os.makedirs("downloads", exist_ok=True)
            filename = safe_filename(f"{data.get('title', 'audio')}.{data.get('format', format)}")
            filepath = os.path.join("downloads", filename)

            headers = {"User-Agent": "Mozilla/5.0"}
            async with session.get(data["stream_url"], headers=headers, timeout=120) as download_resp:
                if download_resp.status != 200:
                    return await message.reply_text(f"❌ Failed to download file. HTTP {download_resp.status}")
                with open(filepath, 'wb') as f:
                    while True:
                        chunk = await download_resp.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)

        # Double-check file exists
        if not os.path.exists(filepath):
            return await message.reply_text("❌ File not found after download.")

        # Fix 2: Only send valid str, int, float in arguments
        send_args = {}
        title = data.get("title")
        author = data.get("author")
        if title and isinstance(title, str):
            send_args["title"] = title
        if author and isinstance(author, str):
            send_args["performer"] = author

        if format == "mp3":
            await message.reply_audio(audio=filepath, **send_args)
        else:
            # For video, only use caption if string
            caption = data.get("title")
            if caption and isinstance(caption, str):
                await message.reply_video(video=filepath, caption=caption)
            else:
                await message.reply_video(video=filepath)

        os.remove(filepath)

    except asyncio.TimeoutError:
        await message.reply_text("⏱️ Timeout while downloading. Try again later.")
    except Exception as e:
        await message.reply_text(f"⚠️ Failed: `{str(e)}`")


@bot.on_message(filters.command("song") & filters.private)
async def song_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❗ Usage: /song <query or YouTube URL>")
    user_input = message.text.split(None, 1)[1]
    await download_and_send(client, message, user_input, "mp3")


@bot.on_message(filters.command("video") & filters.private)
async def video_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❗ Usage: /video <query or YouTube URL>")
    user_input = message.text.split(None, 1)[1]
    await download_and_send(client, message, user_input, "mp4")
