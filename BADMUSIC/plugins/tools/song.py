import os
import asyncio
import yt_dlp
from time import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch
import requests
from BADMUSIC import app

# Define a dictionary to track the last message timestamp for each user
user_last_message_time = {}
user_command_count = {}

# Define the threshold for command spamming (e.g., 2 commands within 5 seconds)
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5

# Path to the cookies file (make sure you have the cookies.txt file in the same directory or provide the full path)
COOKIES_FILE = 'cookies/example.txt'

# Quality options for songs
SONG_QUALITY_OPTIONS = {
    'low': 'worstaudio',
    'medium': 'bestaudio[ext=m4a]',
    'high': 'bestaudio'
}

# Quality options for videos
VIDEO_QUALITY_OPTIONS = {
    '144p': '144',
    '240p': '240',
    '360p': '360',
    '480p': '480',
    '720p': '720',
    '1080p': '1080',
    '1440p': '1440',
    '2160p': '2160',
}

async def send_quality_buttons(message: Message, query: str, type: str, thumbnail: str, sizes: list):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{size} MB", callback_data=f"{type}_{query}_{index}")]
        for index, size in enumerate(sizes)
    ])
    await message.reply_photo(photo=thumbnail, caption="ꜱᴇʟᴇᴄᴛ Qᴜᴀʟɪᴛʏ ᴍᴘ3:", reply_markup=keyboard)

async def send_video_quality_buttons(message: Message, query: str, thumbnail: str):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"144p", callback_data=f"video_{query}_144p"), 
         InlineKeyboardButton(f"240p", callback_data=f"video_{query}_240p"),
         InlineKeyboardButton(f"360p", callback_data=f"video_{query}_360p")],
        [InlineKeyboardButton(f"480p", callback_data=f"video_{query}_480p"), 
         InlineKeyboardButton(f"720p", callback_data=f"video_{query}_720p"),
         InlineKeyboardButton(f"1080p", callback_data=f"video_{query}_1080p")],
        [InlineKeyboardButton(f"1440p", callback_data=f"video_{query}_1440p"), 
         InlineKeyboardButton(f"2160p", callback_data=f"video_{query}_2160p")]
    ])
    await message.reply_photo(photo=thumbnail, caption="ꜱᴇʟᴇᴄᴛ Qᴜᴀʟɪᴛʏ ᴍᴘ4:", reply_markup=keyboard)

@app.on_message(filters.command("song"))
async def download_song(_, message: Message):
    user_id = message.from_user.id
    current_time = time()
    
    # Spam protection: Prevent multiple commands within a short time
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
    
    # Extract query from the message
    query = " ".join(message.command[1:])
    if not query:
        await message.reply("Please provide a song name or URL to search for.")
        return

    # Delete the command message
    await message.delete()

    # Searching for the song using YouTubeSearch
    results = YoutubeSearch(query, max_results=1).to_dict()
    if not results:
        await message.reply("⚠️ No results found. Please make sure you typed the correct name.")
        return

    thumbnail = results[0]["thumbnails"][0]
    
    # Calculate the size of the song for each quality
    sizes = []
    for quality in SONG_QUALITY_OPTIONS.values():
        ydl_opts = {
            "format": quality,
            "noplaylist": True,
            "quiet": True,
            "logtostderr": False,
            "cookiefile": COOKIES_FILE,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(f"https://youtube.com{results[0]['url_suffix']}", download=False)
            size = info_dict.get('filesize') or info_dict.get('filesize_approx') or 0
            sizes.append(size / (1024 * 1024))  # Convert bytes to MB

    # Sending quality selection buttons with sizes
    await send_quality_buttons(message, query, 'song', thumbnail, [f"{size:.2f}" for size in sizes])

@app.on_message(filters.command("video"))
async def download_video(_, message: Message):
    user_id = message.from_user.id
    current_time = time()
    
    # Spam protection: Prevent multiple commands within a short time
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
    
    # Extract query from the message
    query = " ".join(message.command[1:])
    if not query:
        await message.reply("Please provide a video name or URL to search for.")
        return

    # Delete the command message
    await message.delete()

    # Searching for the video using YouTubeSearch
    results = YoutubeSearch(query, max_results=1).to_dict()
    if not results:
        await message.reply("⚠️ No results found. Please make sure you typed the correct name.")
        return

    thumbnail = results[0]["thumbnails"][0]
    
    # Sending quality selection buttons
    await send_video_quality_buttons(message, query, thumbnail)

@app.on_callback_query(filters.regex(r"^(song|video)_(.+)_(\d+)$"))
async def callback_query_handler(client, query):
    type, query_text, quality_index = query.data.split("_")
    
    if type == "song":
        quality = list(SONG_QUALITY_OPTIONS.values())[int(quality_index)]
        ydl_opts = {
            "format": quality,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "noplaylist": True,
            "quiet": True,
            "logtostderr": False,
            "cookiefile": COOKIES_FILE,
        }
    else:
        quality = list(VIDEO_QUALITY_OPTIONS.values())[int(quality_index)]
        ydl_opts = {
            "format": f"bestvideo[ext=mp4][height<={quality}]+bestaudio/best[ext=mp4][height<={quality}]",
            "noplaylist": True,
            "quiet": True,
            "logtostderr": False,
            "cookiefile": COOKIES_FILE,
        }

    try:
        # Searching for the song or video using YouTubeSearch
        m = await query.message.reply("🔄 **Searching...**")
        results = YoutubeSearch(query_text, max_results=1).to_dict()
        if not results:
            await m.edit("**⚠️ No results found. Please make sure you typed the correct name.**")
            return

        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"{title}.jpg"
        
        # Download thumbnail
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]
        views = results[0]["views"]
        channel_name = results[0]["channel"]

        # Now, download the audio or video using yt_dlp
        await m.edit("📥 **Downloading...**")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            file = ydl.prepare_filename(info_dict)
            ydl.download([link])

        # Parsing duration (in seconds)
        dur = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration.split(":"))))
        
        # Sending the audio or video to the user
        await m.edit("📤 **Uploading...**")
        if type == "song":
            await query.message.reply_audio(
                file,
                thumb=thumb_name,
                title=title,
                caption=f"{title}\nRequested by ➪ {query.from_user.mention}\nViews ➪ {views}\nChannel ➪ {channel_name}",
                duration=dur
            )
        else:
            await query.message.reply_video(
                file,
                thumb=thumb_name,
                caption=f"{title}\nRequested by ➪ {query.from_user.mention}\nViews ➪ {views}\nChannel ➪ {channel_name}",
                duration=dur
            )

        # Cleanup downloaded files
        os.remove(file)
        os.remove(thumb_name)
        await m.delete()

    except Exception as e:
        await m.edit("⚠️ **An error occurred!**")
        print(f"Error: {str(e)}")
