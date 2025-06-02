from pyrogram import Client, filters
import requests
import aiohttp
import aiofiles
import os
import re
import asyncio
from BADMUSIC import app as bot

API_KEY = "badmusic_ytstream_apikey_2025"
BASE_URL = "http://3.0.146.239:1470/youtube"  # 👈 updated URL
YOUTUBE_URL_PATTERN = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'

async def get_song_info(title, author, album=None, release_date=None):
    # Dummy function, replace with real metadata extraction if needed
    return {
        "trackName": title,
        "album": album or "Unknown",
        "releaseDate": release_date or "Unknown",
        "author": author or "Unknown"
    }

def build_caption(song_info, requested_by):
    return (
        f"<blockquote>❖ sᴏɴɢ ɴᴀᴍᴇ ➥ {song_info['trackName']}</blockquote>\n"
        f"<blockquote>● ᴀʟʙᴜᴍ ➥ {song_info['album']}\n"
        f"● ʀᴇʟᴇᴀsᴇ ᴅᴀᴛᴇ ➥ {song_info['releaseDate']}\n"
        f"● ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ ➥ {requested_by}</blockquote>\n"
        f"<blockquote>❖ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ➥ @Gaana_MusicBot </blockquote>"
    )

async def download_file(url, filepath):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=300)) as resp:
                if resp.status != 200:
                    return False, f"Failed to download file. HTTP status: {resp.status}"
                async with aiofiles.open(filepath, 'wb') as f:
                    async for chunk in resp.content.iter_chunked(1024 * 32):
                        await f.write(chunk)
        return True, None
    except Exception as e:
        return False, str(e)

async def download_and_send(client, message, user_input, format_):
    await message.reply_chat_action("upload_audio" if format_ == "mp3" else "upload_video")
    info_msg = await message.reply_text(f"🔎 Fetching {format_.upper()} for: `{user_input}`")
    params = {
        "format": format_,
        "download": True,
        "api_key": API_KEY
    }

    if re.match(YOUTUBE_URL_PATTERN, user_input):
        params["url"] = user_input
    else:
        params["query"] = user_input

    try:
        response = requests.get(BASE_URL, params=params, timeout=60)
        data = response.json()
        if response.status_code != 200 or "stream_url" not in data:
            await info_msg.edit_text(f"❌ Error: {data.get('detail', 'Unknown error')}")
            return

        # Prepare paths
        os.makedirs("downloads", exist_ok=True)
        filename = f"{data['title']}.{data['format']}"
        filepath = os.path.join("downloads", filename)

        # Download file
        success, err = await download_file(data["stream_url"], filepath)
        if not success:
            await info_msg.edit_text(f"⚠️ Failed: `{err}`")
            # Clean up partial file if exists
            if os.path.exists(filepath):
                os.remove(filepath)
            return

        # Build caption
        requested_by = message.from_user.mention if message.from_user else "Unknown User"
        song_info = await get_song_info(data['title'], data.get('author'), data.get('album'), data.get('release_date'))
        caption = build_caption(song_info, requested_by)

        # Send file
        if format_ == "mp3":
            await message.reply_audio(
                audio=filepath,
                title=data['title'],
                performer=data.get("author"),
                caption=caption,
                parse_mode="html"
            )
        else:
            await message.reply_video(
                video=filepath,
                caption=caption,
                parse_mode="html"
            )
        await info_msg.delete()
        # Remove file after sending
        os.remove(filepath)

    except Exception as e:
        await info_msg.edit_text(f"⚠️ Failed: `{str(e)}`")

# Handlers: Allow in both groups and private chats
@bot.on_message(filters.command("song") & (filters.group | filters.private))
async def song_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❗ Usage: /song <query or YouTube URL>")
    user_input = message.text.split(None, 1)[1]
    await download_and_send(client, message, user_input, "mp3")

@bot.on_message(filters.command("video") & (filters.group | filters.private))
async def video_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❗ Usage: /video <query or YouTube URL>")
    user_input = message.text.split(None, 1)[1]
    await download_and_send(client, message, user_input, "mp4")
