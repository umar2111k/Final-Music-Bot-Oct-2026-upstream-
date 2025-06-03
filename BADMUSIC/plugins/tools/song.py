import os
import re
import asyncio
import requests
import aiohttp
from time import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from BADMUSIC import app

API_KEY = "badmusic_ytstream_apikey_2025"
BASE_URL = "http://3.0.146.239:1470/youtube"
YOUTUBE_URL_PATTERN = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

# Spam protection
user_last_message_time = {}
user_command_count = {}
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5

async def download_and_send(client, message, user_input, format):
    await message.reply_text(f"🔎 Fetching {format.upper()} for: `{user_input}`")

    params = {
        "format": format,
        "download": True,
        "api_key": API_KEY,
    }
    # Check if input is a YouTube URL
    if re.match(YOUTUBE_URL_PATTERN, user_input.strip()):
        params["url"] = user_input.strip()
    else:
        params["query"] = user_input.strip()

    try:
        response = requests.get(BASE_URL, params=params)
        try:
            data = response.json()
        except Exception:
            return await message.reply_text(f"❌ Error: API se invalid response aaya: {response.text}")

        if response.status_code != 200:
            return await message.reply_text(f"❌ Error: {data.get('detail', 'API error')}")

        if not data.get("stream_url"):
            return await message.reply_text(f"❌ Error: Song ka stream_url nahi mila. API ka response: {data}")

        # create downloads folder if not exists
        os.makedirs("downloads", exist_ok=True)

        # prepare filename & path
        safe_title = re.sub(r'[\\/*?:"<>|]', "", data.get('title', 'unknown'))
        filename = f"{safe_title}.{data.get('format', format)}"
        filepath = os.path.join("downloads", filename)

        # download file via aiohttp (async)
        async with aiohttp.ClientSession() as session:
            async with session.get(data["stream_url"]) as resp:
                if resp.status != 200:
                    return await message.reply_text(f"❌ Error: File stream download failed. HTTP code: {resp.status}")
                with open(filepath, 'wb') as f:
                    while True:
                        chunk = await resp.content.read(1024 * 512)
                        if not chunk:
                            break
                        f.write(chunk)

        caption = f"{data.get('title','Unknown')}\nRequested by ➪ {message.from_user.mention}\nChannel ➪ {data.get('channel','Unknown')}\nViews ➪ {data.get('views','')}"
        thumb_url = data.get("thumbnail")

        if format == "mp3":
            await message.reply_audio(
                audio=filepath,
                thumb=thumb_url,
                caption=caption,
                title=data.get("title"),
                duration=data.get("duration"),
            )
        else:
            await message.reply_video(
                video=filepath,
                thumb=thumb_url,
                caption=caption,
                duration=data.get("duration"),
            )

        # cleanup local file
        if os.path.exists(filepath):
            os.remove(filepath)

    except Exception as e:
        await message.reply_text(f"⚠️ **An error occurred!**\n{str(e)}")

# ----------- HANDLERS -----------

@app.on_message(filters.command("song"))
async def song_handler(client, message: Message):
    user_id = message.from_user.id
    current_time = time()

    # Spam protection
    last_message_time = user_last_message_time.get(user_id, 0)
    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            hu = await message.reply_text(f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ ᴅᴏ sᴘᴀᴍ, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ**")
            await asyncio.sleep(3)
            await hu.delete()
            return
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    query = " ".join(message.command[1:])
    if not query:
        await message.reply("Please provide a song name or YouTube URL.")
        return

    await download_and_send(client, message, query, "mp3")

@app.on_message(filters.command("video"))
async def video_handler(client, message: Message):
    user_id = message.from_user.id
    current_time = time()

    # Spam protection
    last_message_time = user_last_message_time.get(user_id, 0)
    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            hu = await message.reply_text(f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ ᴅᴏ sᴘᴀᴍ, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ**")
            await asyncio.sleep(3)
            await hu.delete()
            return
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    query = " ".join(message.command[1:])
    if not query:
        await message.reply("Please provide a video name or YouTube URL.")
        return

    await download_and_send(client, message, query, "mp4")
