from pyrogram import filters
from pyrogram.types import Message
from BADMUSIC import app
from BADMUSIC.core.call import Bad
from pytgcalls.exceptions import NoActiveGroupCall
from yt_dlp import YoutubeDL
from bs4 import BeautifulSoup
import random
import requests
import asyncio

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
        print(f"[ERROR] Search failed: {e}")
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
            # Prefer direct video url, fallback to entries[0] if playlist
            if "url" in info_dict:
                return info_dict["url"], info_dict.get("duration", None)
            elif "entries" in info_dict and len(info_dict["entries"]) > 0:
                entry = info_dict["entries"][0]
                return entry["url"], entry.get("duration", None)
    except Exception as e:
        print(f"[ERROR] yt-dlp stream extract: {e}")
    return None, None

@app.on_message(filters.command("xxnx") & filters.group)
async def stream_xxnx_to_vc(client, message: Message):
    chat_id = message.chat.id

    if len(message.command) < 2:
        await message.reply_text("Kya dekhna hai? Example: `/xxnx sunny leone`")
        return

    query = " ".join(message.command[1:])
    mystic = await message.reply_text("🔍 Searching, please wait...")

    video_url = get_video_info(query)
    if not video_url:
        await mystic.edit_text("❌ No video found! Try something else.")
        return

    stream_url, duration = await get_stream_link(video_url)
    if not stream_url:
        await mystic.edit_text("❌ Unable to get stream link! Try again.")
        return

    try:
        # Use stream_on_video_call if you want to play video, or stream_call for audio
        await Bad.stream_on_video_call(chat_id, stream_url)
        await mystic.edit_text(
            f"✅ Now playing: `{query}` in VC!\n[Watch Video]({video_url})",
            disable_web_page_preview=True
        )

        # Wait for the duration of the video (if known) or set a max timeout (e.g. 10 min)
        if duration:
            await asyncio.sleep(duration)
        else:
            await asyncio.sleep(600)  # Default 10 min if unknown duration

        # Stop streaming and leave VC after video ends
        await Bad.leave_vc(chat_id)

    except NoActiveGroupCall:
        await mystic.edit_text("⚠️ No active group call! Start a VC first.")
    except Exception as e:
        await mystic.edit_text(f"❌ Error: `{type(e).__name__}` - {e}")

    # Optional: Delete user command message for privacy
    try:
        await message.delete()
    except:
        pass
