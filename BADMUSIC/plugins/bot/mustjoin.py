from pyrogram import Client, filters
from BADMUSIC import app
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, InputMediaPhoto
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from pyrogram.enums import ChatMemberStatus
import io

# List of mandatory channels/groups
MUST_JOIN = ["PBX_CHAT", "PBX_UPDATE"]

@app.on_message(filters.incoming & filters.private, group=-1)
async def must_join_channel(app: Client, msg: Message):
    if not MUST_JOIN:
        return

    missing_channels = []  # To store missing channel names
    buttons = []  # To store button objects

    for channel in MUST_JOIN:
        try:
            await app.get_chat_member(channel, msg.from_user.id)
        except UserNotParticipant:
            try:
                if channel.isalpha():
                    link = f"https://t.me/{channel}"
                else:
                    chat_info = await app.get_chat(channel)
                    link = chat_info.invite_link

                if link:
                    missing_channels.append(channel)
                    buttons.append([InlineKeyboardButton(f"ᴊᴏɪɴ {channel}", url=link)])
            except ChatAdminRequired:
                print(f"๏ ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴀꜱ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ {channel}!")

    if missing_channels:
        try:
            # Try to get user's profile photo
            try:
                photos = await app.get_profile_photos(msg.from_user.id, limit=1)
                if photos.total_count > 0:
                    file = await app.download_media(photos[0].file_id)
                    photo_bytes = open(file, "rb").read()
                else:
                    raise Exception("ɴᴏ ᴘʀᴏꜰɪʟᴇ ᴘɪᴄ")
            except:
                # Fallback image
                import requests
                photo_bytes = requests.get("https://files.catbox.moe/bjnhm5.jpg").content

            # Send the photo as Spoiler
            await msg.reply_photo(
                photo=photo_bytes,
                has_spoiler=True,
                caption=(
                    "๏ ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ, ʏᴏᴜ'ᴠᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇꜱᴇ ᴄʜᴀɴɴᴇʟꜱ/ɢʀᴏᴜᴘꜱ ʏᴇᴛ:\n\n"
                    + "\n".join([f"[ᴊᴏɪɴ {channel}](https://t.me/{channel})" for channel in missing_channels])
                ),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await msg.stop_propagation()
        except ChatWriteForbidden:
            pass
