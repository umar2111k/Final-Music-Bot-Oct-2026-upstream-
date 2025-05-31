import os
import requests
from pyrogram import filters
from BADMUSIC import app

# Smallcaps font converter
def to_smallcaps(text):
    smallcaps_map = {
        "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ғ", "g": "ɢ",
        "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
        "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "s", "t": "ᴛ", "u": "ᴜ",
        "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ",
        "A": "ᴀ", "B": "ʙ", "C": "ᴄ", "D": "ᴅ", "E": "ᴇ", "F": "ғ", "G": "ɢ",
        "H": "ʜ", "I": "ɪ", "J": "ᴊ", "K": "ᴋ", "L": "ʟ", "M": "ᴍ", "N": "ɴ",
        "O": "ᴏ", "P": "ᴘ", "Q": "ǫ", "R": "ʀ", "S": "s", "T": "ᴛ", "U": "ᴜ",
        "V": "ᴠ", "W": "ᴡ", "X": "x", "Y": "ʏ", "Z": "ᴢ"
    }
    return "".join(smallcaps_map.get(c, c) for c in text)

# Upload to catbox
def upload_file(file_path):
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload", "json": "true"}
    with open(file_path, "rb") as file:
        files = {"fileToUpload": file}
        response = requests.post(url, data=data, files=files)

    if response.status_code == 200 and "url" in response.text:
        import json
        return True, json.loads(response.text)["url"]
    else:
        return False, f"❌ Error: {response.status_code} - {response.text}"

@app.on_message(filters.command(["tgm", "tgt", "telegraph", "tl"]))
async def get_link_group(client, message):
    if not message.reply_to_message:
        return await message.reply_text("📌 ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇᴅɪᴀ ғɪʟᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴏɴ ᴄᴀᴛʙᴏx.")

    media = message.reply_to_message

    if not (media.document or media.audio or media.video or media.photo or media.animation or media.voice or media.video_note or media.sticker):
        return await message.reply_text("❌ ᴛʜɪs ᴅᴏᴇsɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ᴀ sᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴇᴅɪᴀ ғɪʟᴇ.")

    download_msg = await message.reply_text("⬇️ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...")
    file_path = await media.download()
    await download_msg.edit("📤 ᴜᴘʟᴏᴀᴅɪɴɢ ᴛᴏ ᴄᴀᴛʙᴏx...")

    success, result = upload_file(file_path)
    os.remove(file_path)

    if success:
        text = f"{to_smallcaps('your file has been uploaded:')}\n👉 [ᴄʟɪᴄᴋ ᴛᴏ ᴄᴏᴏʏ ʟɪɴᴋ]({result})"
        await download_msg.edit(text, disable_web_page_preview=True)
    else:
        await download_msg.edit(result)
