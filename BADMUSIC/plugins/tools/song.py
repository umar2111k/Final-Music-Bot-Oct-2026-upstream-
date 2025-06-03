from pyrogram import Client, filters
import requests
import aiohttp
import os
import re
from BADMUSIC import app

API_KEY = "badmusic_ytstream_apikey_2025"
BASE_URL = "http://3.0.146.239:1470/youtube"
YOUTUBE_URL_PATTERN = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

async def download_and_send(client, message, user_input, format):
    await message.reply_text(f"🔎 ꜰᴇᴛᴄʜɪɴɢ {format.upper()} ꜰᴏʀ: `{user_input}`")

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
            return await message.reply_text(f"❌ ᴇʀʀᴏʀ: ᴀᴘɪ ꜱᴇ ɪɴᴠᴀʟɪᴅ {response.text}")

        if response.status_code != 200:
            return await message.reply_text(f"❌ ᴇʀʀᴏʀ: {data.get('detail', 'API error')}")

        if not data.get("stream_url"):
            return await message.reply_text(f"❌ ᴇʀʀᴏʀ:  ꜱᴏɴɢ ɴᴏᴛ ꜰᴏᴜɴᴅ ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ {data}")

        # create downloads folder if not exists
        os.makedirs("downloads", exist_ok=True)

        # prepare filename & path
        safe_title = re.sub(r'[\\/*?:"<>|]',"", data.get('title','unknown'))
        filename = f"{safe_title}.{data.get('format', format)}"
        filepath = os.path.join("downloads", filename)

        # download file
        async with aiohttp.ClientSession() as session:
            async with session.get(data["stream_url"]) as resp:
                if resp.status != 200:
                    return await message.reply_text(f"❌ ᴇʀʀᴏʀ: ꜰɪʟᴇ ꜱᴛʀᴇᴀᴍ ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ. ʜᴛᴛᴘ ᴄᴏᴅᴇ: {resp.status}")
                with open(filepath, 'wb') as f:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)

        # send file
        if format == "mp3":
            await message.reply_audio(audio=filepath, title=data.get('title'), performer=data.get("author"))
        else:
            await message.reply_video(video=filepath, caption=data.get('title'))

        os.remove(filepath)

    except Exception as e:
        await message.reply_text(f"⚠️ ꜰᴀɪʟᴇᴅ: `{str(e)}`")

@app.on_message(filters.command("song"))
async def song_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❗ ᴜꜱᴀɢᴇ: /song ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ꜱᴏɴɢ ɴᴀᴍᴇ ᴏʀ ᴜʀʟ ᴛᴏ ꜱᴇᴀʀᴄʜ ꜰᴏʀ.")
    user_input = message.text.split(None, 1)[1]
    await download_and_send(client, message, user_input, "mp3")

@app.on_message(filters.command("video"))
async def video_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❗ ᴜꜱᴀɢᴇ: /video ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ꜱᴏɴɢ ɴᴀᴍᴇ ᴏʀ ᴜʀʟ ᴛᴏ ꜱᴇᴀʀᴄʜ ꜰᴏʀ.")
    user_input = message.text.split(None, 1)[1]
    await download_and_send(client, message, user_input, "mp4")
    
