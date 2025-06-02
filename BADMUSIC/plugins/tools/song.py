from pyrogram import Client, filters
import requests
import aiohttp
import os
import re
from BADMUSIC import app

API_KEY = "badmusic_ytstream_apikey_2025"
BASE_URL = "http://3.0.146.239:1470/youtube"  # 👈 updated URL
YOUTUBE_URL_PATTERN = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'



async def download_and_send(client, message, user_input, format):
    await message.reply_text(f"🔎 Fetching {format.upper()} for: `{user_input}`")

    # check if input is URL or query
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
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if response.status_code != 200 or "stream_url" not in data:
            return await message.reply_text(f"❌ Error: {data.get('detail', 'Unknown error')}")

        # create downloads folder if not exists
        os.makedirs("downloads", exist_ok=True)

        # prepare filename & path
        filename = f"{data['title']}.{data['format']}"
        filepath = os.path.join("downloads", filename)

        # download file
        async with aiohttp.ClientSession() as session:
            async with session.get(data["stream_url"]) as resp:
                with open(filepath, 'wb') as f:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)

        # send file
        if format == "mp3":
            await message.reply_audio(audio=filepath, title=data['title'], performer=data.get("author"))
        else:
            await message.reply_video(video=filepath, caption=data['title'])

        os.remove(filepath)

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

                                           
