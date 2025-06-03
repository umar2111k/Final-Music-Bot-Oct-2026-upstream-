from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import aiohttp
import os
import re
import asyncio
from BADMUSIC import app

API_KEY = "badmusic_ytstream_apikey_2025"
BASE_URL = "http://3.0.146.239:1470/youtube"
YOUTUBE_URL_PATTERN = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

async def fetch_formats(user_input, req_format):
    params = {
        "format": req_format,
        "download": False,
        "api_key": API_KEY,
    }
    if re.match(YOUTUBE_URL_PATTERN, user_input.strip()):
        params["url"] = user_input.strip()
    else:
        params["query"] = user_input.strip()
    r = requests.get(BASE_URL, params=params)
    data = r.json()
    return data

async def download_and_send(client, message, user_input, req_format, format_id=None, song_info=None):
    params = {
        "format": req_format,
        "download": True,
        "api_key": API_KEY,
    }
    if format_id:
        params["format_id"] = format_id
    if re.match(YOUTUBE_URL_PATTERN, user_input.strip()):
        params["url"] = user_input.strip()
    else:
        params["query"] = user_input.strip()

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        if response.status_code != 200:
            return await message.reply_text(f"❌ ᴇʀʀᴏʀ: {data.get('detail', 'API error')}")
        if not data.get("selected_stream_url"):
            return await message.reply_text(f"❌ ᴇʀʀᴏʀ:  ꜱᴏɴɢ ɴᴏᴛ ꜰᴏᴜɴᴅ ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ {data}")

        os.makedirs("downloads", exist_ok=True)
        safe_title = re.sub(r'[\\/*?:"<>|]',"", data.get('title','unknown'))
        filename = f"{safe_title}.{data.get('selected_ext', req_format)}"
        filepath = os.path.join("downloads", filename)

        async with aiohttp.ClientSession() as session:
            async with session.get(data["selected_stream_url"]) as resp:
                if resp.status != 200:
                    return await message.reply_text(f"❌ ᴇʀʀᴏʀ: ꜰɪʟᴇ ꜱᴛʀᴇᴀᴍ ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ. ʜᴛᴛᴘ ᴄᴏᴅᴇ: {resp.status}")
                with open(filepath, 'wb') as f:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)

        # Caption block
        cap = (
            f"<blockquote>❖ sᴏɴɢ ɴᴀᴍᴇ ➥ {data.get('title','')}</blockquote>\n"
            f"<blockquote>● ᴀʟʙᴜᴍ ➥ {song_info.get('album','-') if song_info else '-'}\n"
            f"● ʀᴇʟᴇᴀꜱᴇ ᴅᴀᴛᴇ ➥ {song_info.get('releaseDate','-') if song_info else '-'}\n"
            f"● ʀᴇǫᴜᴇꜱᴛᴇᴅ ʙʏ ➥ {message.from_user.mention}</blockquote>\n"
            f"<blockquote>❖ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ➥ @pb_sukh </blockquote>"
        )

        if req_format == "mp3":
            await message.reply_audio(audio=filepath, title=data.get('title'), performer=data.get("author"), caption=cap, parse_mode="HTML")
        else:
            await message.reply_video(video=filepath, caption=cap, parse_mode="HTML")
        os.remove(filepath)
    except Exception as e:
        await message.reply_text(f"⚠️ ꜰᴀɪʟᴇᴅ: `{str(e)}`")

@app.on_message(filters.command("song"))
async def song_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❗ ᴜꜱᴀɢᴇ: /song ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ꜱᴏɴɢ ɴᴀᴍᴇ ᴏʀ ᴜʀʟ ᴛᴏ ꜱᴇᴀʀᴄʜ ꜰᴏʀ.")
    user_input = message.text.split(None, 1)[1]
    msg = await message.reply_text("🔎 ꜰᴇᴛᴄʜɪɴɢ ᴀᴜᴅɪᴏ ꜰᴏʀᴍᴀᴛꜱ...")
    data = await fetch_formats(user_input, "mp3")
    btns = []
    for f in data.get("formats", {}).get("audio", []):
        size_mb = f.get("filesize", 0)
        if size_mb:
            size_str = f"{round(size_mb/1024/1024,1)} MB"
        else:
            size_str = "?"
        note = f"{f.get('abr','?')}kbps" if f.get("abr") else f.get("format_note", "")
        btns.append([
            InlineKeyboardButton(
                f"{note} ({size_str})",
                callback_data=f"aud|{user_input}|{f['format_id']}"
            )
        ])
    if not btns:
        return await msg.edit_text("😒 ᴀᴜᴅɪᴏ ꜰᴏʀᴍᴀᴛꜱ ɴᴏᴛ ꜰᴏᴜɴᴅ.")
    await msg.edit_text("🎧 ᴄʜᴏᴏꜱᴇ ᴀᴜᴅɪᴏ Qᴜᴀʟɪᴛʏ:", reply_markup=InlineKeyboardMarkup(btns))

@app.on_message(filters.command("video"))
async def video_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❗ ᴜꜱᴀɢᴇ: /video ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ꜱᴏɴɢ ɴᴀᴍᴇ ᴏʀ ᴜʀʟ ᴛᴏ ꜱᴇᴀʀᴄʜ ꜰᴏʀ.")
    user_input = message.text.split(None, 1)[1]
    msg = await message.reply_text("🔎 ꜰᴇᴛᴄʜɪɴɢ ᴠɪᴅᴇᴏ ꜰᴏʀᴍᴀᴛꜱ...")
    data = await fetch_formats(user_input, "mp4")
    btns = []
    for f in data.get("formats", {}).get("video", []):
        size_mb = f.get("filesize", 0)
        if size_mb:
            size_str = f"{round(size_mb/1024/1024,1)} MB"
        else:
            size_str = "?"
        note = f"{f.get('resolution','?')}p" if f.get("resolution") else f.get("format_note", "")
        btns.append([
            InlineKeyboardButton(
                f"{note} ({size_str})",
                callback_data=f"vid|{user_input}|{f['format_id']}"
            )
        ])
    if not btns:
        return await msg.edit_text("😒 ᴠɪᴅᴇᴏ ꜰᴏʀᴍᴀᴛꜱ ɴᴏᴛ ꜰᴏᴜɴᴅ.")
    await msg.edit_text("🎬 ᴄʜᴏᴏꜱᴇ ᴠɪᴅᴇᴏ Qᴜᴀʟɪᴛʏ:", reply_markup=InlineKeyboardMarkup(btns))

@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    if data.startswith("aud|"):
        _, user_input, format_id = data.split("|", 2)
        await callback_query.answer("⏬ Downloading...")
        await download_and_send(client, callback_query.message, user_input, "mp3", format_id=format_id)
    elif data.startswith("vid|"):
        _, user_input, format_id = data.split("|", 2)
        await callback_query.answer("⏬ Downloading...")
        await download_and_send(client, callback_query.message, user_input, "mp4", format_id=format_id)
    await callback_query.message.delete()
