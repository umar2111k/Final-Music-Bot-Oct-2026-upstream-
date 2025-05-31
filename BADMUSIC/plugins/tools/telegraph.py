import os
import requests
from pyrogram import filters
from pyrogram.enums import ParseMode
from BADMUSIC import app

# Small caps conversion helper
def to_small_caps(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    small_caps = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ" * 2
    return text.translate(str.maketrans(normal, small_caps))

# Upload function
def upload_file(file_path):
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload"}
    with open(file_path, "rb") as file:
        files = {"fileToUpload": file}
        response = requests.post(url, data=data, files=files)

    if response.status_code == 200:
        text = response.text.strip()
        if text.startswith("http"):
            return True, text  # Valid URL
        else:
            return False, f"❌ Unexpected response: {text}"
    else:
        return False, f"❌ ᴇʀʀᴏʀ {response.status_code} - {response.text}"

# Bot command handler
@app.on_message(filters.command(["tgm", "tgt", "telegraph", "tl"]))
async def get_link_group(client, message):
    if not message.reply_to_message:
        return await message.reply_text(
            to_small_caps("please reply to a media file to upload on catbox.")
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
        await text.edit_text(to_small_caps("📤 uploading to catbox..."))

        success, url = upload_file(local_path)

        if success:
            await text.edit_text(
                f"**💫 {to_small_caps('uploaded to Catbox!')}**\n\n**🔗 {to_small_caps('URL')}:** `{url}`",
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await text.edit_text(to_small_caps(f"upload failed:\n{url}"))

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
