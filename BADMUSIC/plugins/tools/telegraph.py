import os
import requests
from pyrogram import filters
from pyrogram.enums import ParseMode
from BADMUSIC import app

# 🔠 Small caps helper
def to_small_caps(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    small_caps = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ" * 2
    return text.translate(str.maketrans(normal, small_caps))

# 🔗 Upload to your FastAPI server
def upload_to_my_api(file_path):
    url = "http://13.213.46.226:5050/upload"
    api_key = "badtelegrapfapikey"
    with open(file_path, "rb") as file:
        files = {"file": file}
        params = {"api_key": api_key}
        response = requests.post(url, files=files, params=params)

    if response.status_code == 200:
        result = response.json()
        return True, result.get("download_url", "❌ No URL returned.")
    else:
        return False, f"❌ Error {response.status_code} - {response.text}"

# 🎯 Telegram Command Handler
@app.on_message(filters.command(["tgm", "tgt", "telegraph", "tl"]))
async def upload_media(client, message):
    if not message.reply_to_message:
        return await message.reply_text(
            to_small_caps("please reply to a media file to upload.")
        )

    media = message.reply_to_message
    file_size = 0

    if media.photo:
        file_size = media.photo.file_size
    elif media.video:
        file_size = media.video.file_size
    elif media.document:
        file_size = media.document.file_size
    else:
        return await message.reply_text(
            to_small_caps("unsupported media type.")
        )

    if file_size > 200 * 1024 * 1024:
        return await message.reply_text(
            to_small_caps("please provide a media file under 200mb.")
        )

    text = await message.reply(to_small_caps("processing..."))

    async def progress(current, total):
        try:
            await text.edit_text(to_small_caps(f"📥 downloading... {current * 100 / total:.1f}%"))
        except Exception:
            pass

    try:
        local_path = await media.download(progress=progress)
        await text.edit_text(to_small_caps("📤 uploading to server..."))

        success, result = upload_to_my_api(local_path)

        if success:
            await text.edit_text(
                f"**✅ {to_small_caps('uploaded successfully!')}**\n\n**🔗 {to_small_caps('url')}:** `{result}`",
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await text.edit_text(to_small_caps(f"upload failed:\n{result}"))

        try:
            os.remove(local_path)
        except Exception:
            pass

    except Exception as e:
        await text.edit_text(
            f"{to_small_caps('file upload failed')}:\n\n<code>{str(e)}</code>"
        )
        try:
            os.remove(local_path)
        except Exception:
            pass
