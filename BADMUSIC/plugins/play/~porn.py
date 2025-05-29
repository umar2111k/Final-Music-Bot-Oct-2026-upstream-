from pyrogram import filters
from pyrogram.types import Message
from BADMUSIC import app
from BADMUSIC.core.call import Bad
from pytgcalls.exceptions import NoActiveGroupCall
from yt_dlp import YoutubeDL
from bs4 import BeautifulSoup
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
            return info_dict["url"]
    except Exception as e:
        print(f"[ERROR] yt-dlp stream extract: {e}")
    return None

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

    stream_url = await get_stream_link(video_url)  
    if not stream_url:  
        await mystic.edit_text("❌ Unable to get stream link! Try again.")  
        return  

    try:  
        await Bad.stream_call(stream_url)  # FIX: Only pass stream_url
        await mystic.edit_text(
            f"✅ Now playing: `{query}` in VC!\n[Watch Video]({video_url})",
            disable_web_page_preview=True
        )  
    except NoActiveGroupCall:  
        await mystic.edit_text("⚠️ No active group call! Start a VC first.")  
    except Exception as e:  
        await mystic.edit_text(f"❌ Error: `{type(e).__name__}` - {e}")  

    # Optional: Delete user command message for privacy  
    try:  
        await message.delete()  
    except:  
        pass
