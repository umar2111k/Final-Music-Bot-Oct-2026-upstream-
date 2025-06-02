import os
import requests
from pyrogram import Client, filters
from BADMUSIC import app

API_URL = "http://3.0.146.239:1470/youtube"
API_KEY = "badmusic_ytstream_apikey_2025"

def fetch_media(query, req_format="mp3"):
    """
    query: song name or YouTube URL
    req_format: "mp3" for audio, "mp4" for video
    """
    params = {
        "query": query,
        "format": req_format,
        "api_key": API_KEY,
        "download": "true"
    }
    try:
        response = requests.get(API_URL, params=params, timeout=30)
        if response.status_code == 200 and "stream_url" in response.json():
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"API Error: {e}")
        return None

async def download_and_send(message, query, req_format="mp3"):
    media_info = fetch_media(query, req_format)
    if not media_info or not media_info.get("stream_url"):
        await message.reply(f"Sorry, couldn't find or download: '{query}'.")
        return

    filename = f"{media_info['title']}.{media_info['format']}"
    download_url = media_info['stream_url']

    # Download file
    try:
        with requests.get(download_url, stream=True) as r, open(filename, "wb") as file:
            for chunk in r.iter_content(1024 * 1024):  # 1MB chunks
                if chunk:
                    file.write(chunk)
    except Exception as e:
        await message.reply("Download failed. Please try again later.")
        print(f"Download error: {e}")
        return

    caption = (
        f"<b>Title:</b> {media_info['title']}\n"
        f"<b>Author:</b> {media_info.get('author', 'N/A')}\n"
        f"<b>Duration:</b> {media_info.get('duration', 'N/A')} sec\n"
        f"<b>Type:</b> {media_info['type']}\n"
        f"<b>Source:</b> <a href='{media_info['watch_url']}'>YouTube</a>"
    )

    # Send file
    try:
        if req_format == "mp3":
            await message.reply_audio(audio=open(filename, "rb"), caption=caption, parse_mode="html", thumb=media_info.get("thumbnail"))
        else:
            await message.reply_video(video=open(filename, "rb"), caption=caption, parse_mode="html", thumb=media_info.get("thumbnail"))
    except Exception as e:
        await message.reply("Failed to send file.")
        print(f"Send error: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# /song command (audio)
@app.on_message(filters.command("song", prefixes=["/", "!", ".", ""]))
async def song_command(client, message):
    query = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else None
    if not query:
        await message.reply("Please provide a song name or YouTube URL after the /song command.")
        return
    await download_and_send(message, query, req_format="mp3")

# /video command (video)
@app.on_message(filters.command("video", prefixes=["/", "!", ".", ""]))
async def video_command(client, message):
    query = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else None
    if not query:
        await message.reply("Please provide a song name or YouTube URL after the /video command.")
        return
    await download_and_send(message, query, req_format="mp4")
