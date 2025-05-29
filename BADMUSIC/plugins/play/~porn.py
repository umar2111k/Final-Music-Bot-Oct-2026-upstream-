from pyrogram import filters
from pyrogram.types import Message
from BADMUSIC import app
from BADMUSIC.core.call import Bad
from pytgcalls.exceptions import NoActiveGroupCall
from yt_dlp import YoutubeDL
from bs4 import BeautifulSoup
import os
import random
import requests


def get_video_info(title: str):
    url_base = f'https://www.xnxx.com/search/{title}'
    try:
        with requests.Session() as s:
            r = s.get(url_base)
            soup = BeautifulSoup(r.text, "html.parser")
            video_list = soup.findAll('div', attrs={'class': 'thumb-block'})
            if video_list:
                random_video = random.choice(video_list)
                link = random_video.find('div', class_="thumb-under").find('a').get("href")
                if link and 'https://' not in link:
                    return 'https://www.xnxx.com' + link
    except Exception as e:
        print(f"[ERROR] ꜱᴇᴀʀᴄʜ ꜰᴀɪʟᴇᴅ: 🥲 {e}")
    return None


async def get_stream_link(url: str):
    try:
        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "geo_bypass": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict["url"]
    except Exception as e:
        print(f"[ERROR] ʏᴛ-ᴅʟᴘ ꜱᴛʀᴇᴀᴍ ᴇxᴛʀᴀᴄᴛ:😂 {e}")
        return None


@app.on_message(filters.command("xxnx") & filters.group)
async def stream_porn_to_vc(_, message: Message):
    chat_id = message.chat.id

    if len(message.command) < 2:
        return

    query = " ".join(message.command[1:])
    video_url = get_video_info(query)
    if not video_url:
        return

    stream_url = await get_stream_link(video_url)
    if not stream_url:
        return

    try:
        await PRO.join_group_call(
            chat_id,
            stream_url,
            stream_type="video"
        )
    except NoActiveGroupCall:
        await message.reply("ᴠᴄ ɪꜱ ɴᴏᴛ ᴀᴄᴛɪᴠᴇ. ꜱᴛᴀʀᴛ ᴀ ᴠᴄ ʙᴇꜰᴏʀᴇ ᴜꜱɪɴɢ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ🥹.")
        return
    except Exception as e:
        await message.reply(f"ᴇʀʀᴏʀ: {e}")
        return

    # Delete user command and bot reply (if any)
    try:
        await message.delete()
    except:
        pass
