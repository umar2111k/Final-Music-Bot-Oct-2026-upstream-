from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import aiohttp
import os
import re
from BADMUSIC import app

API_KEY = "badmusic_ytstream_apikey_2025"
BASE_URL = "http://3.0.146.239:1470/youtube"
YOUTUBE_URL_PATTERN = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

async def fetch_info(user_input, req_format):
    params = {
        "format": req_format,
        "download": False,
        "api_key": API_KEY,
    }
    if re.match(YOUTUBE_URL_PATTERN, user_input.strip()):
        params["url"] = user_input.strip()
    else:
        params["query"] = user_input.strip()
    resp = requests.get(BASE_URL, params=params)
    return resp.json(), resp.status_code

async def download_and_send(client, message, user_input, req_format, progress_msg=None):
    params = {
        "format": req_format,
        "download": True,
        "api_key": API_KEY,
    }
    if re.match(YOUTUBE_URL_PATTERN, user_input.strip()):
        params["url"] = user_input.strip()
    else:
        params["query"] = user_input.strip()

    try:
        resp = requests.get(BASE_URL, params=params)
        if resp.status_code != 200:
            try:
                detail = resp.json().get("detail", "API error")
            except Exception:
                detail = resp.text
            if progress_msg:
                await progress_msg.delete()
            return await message.reply_text(f"❌ Error: {detail}")

        data = resp.json()
        stream_url = data.get("stream_url")
        if not stream_url:
            if progress_msg:
                await progress_msg.delete()
            return await message.reply_text("❌ Song/Video not found ya download link nahi mila.")

        os.makedirs("downloads", exist_ok=True)
        safe_title = re.sub(r'[\\/*?:"<>|]', "", data.get('title', 'unknown'))
        ext = "mp3" if req_format == "mp3" else "mp4"
        filename = f"{safe_title}.{ext}"
        filepath = os.path.join("downloads", filename)

        async with aiohttp.ClientSession() as session:
            async with session.get(stream_url) as resp_stream:
                if resp_stream.status != 200:
                    if progress_msg:
                        await progress_msg.delete()
                    return await message.reply_text(f"❌ File download failed. HTTP Code: {resp_stream.status}")
                with open(filepath, "wb") as f:
                    while True:
                        chunk = await resp_stream.content.read(1024*32)
                        if not chunk:
                            break
                        f.write(chunk)

        caption = (
            f"<b>❖ Song/Video Name:</b> <i>{data.get('title','')}</i>\n"
            f"<b>● Uploader:</b> <i>{data.get('author','-')}</i>\n"
            f"<b>● Requested by:</b> <i>{message.from_user.mention}</i>\n"
            f"<b>❖ Powered by:</b> <i>@pb_sukh</i>"
        )

        if req_format == "mp3":
            await message.reply_audio(audio=filepath, title=data.get('title'), performer=data.get("author"), caption=caption)
        else:
            await message.reply_video(video=filepath, caption=caption)
        os.remove(filepath)
        if progress_msg:
            await progress_msg.delete()
    except Exception as e:
        if progress_msg:
            await progress_msg.delete()
        await message.reply_text(f"⚠️ Download failed: `{str(e)}`")

@app.on_message(filters.command("song"))
async def song_command(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❗ Usage: /song <song name or YouTube URL>")
    user_input = message.text.split(None, 1)[1]
    # Delete the user command message immediately
    try:
        await message.delete()
    except Exception:
        pass
    msg = await message.reply_text("🔎 Fetching audio info & download link...")
    info, status = await fetch_info(user_input, "mp3")
    if status != 200 or not info.get("stream_url"):
        await msg.edit_text(f"❌ Error: {info.get('detail') or 'Song not found'}")
        return
    progress_msg = await msg.edit_text("⏬ Downloading audio, please wait...")
    await download_and_send(client, message, user_input, "mp3", progress_msg=progress_msg)

@app.on_message(filters.command("video"))
async def video_command(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❗ Usage: /video <video name or YouTube URL>")
    user_input = message.text.split(None, 1)[1]
    # Delete the user command message immediately
    try:
        await message.delete()
    except Exception:
        pass
    msg = await message.reply_text("🔎 Fetching video info & download link...")
    info, status = await fetch_info(user_input, "mp4")
    if status != 200 or not info.get("stream_url"):
        await msg.edit_text(f"❌ Error: {info.get('detail') or 'Video not found'}")
        return
    progress_msg = await msg.edit_text("⏬ Downloading video, please wait...")
    await download_and_send(client, message, user_input, "mp4", progress_msg=progress_msg)
