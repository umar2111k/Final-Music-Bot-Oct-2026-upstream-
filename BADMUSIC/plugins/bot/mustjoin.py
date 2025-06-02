from pyrogram import Client, filters
from BADMUSIC import app
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from pyrogram.enums import ChatMemberStatus

import requests
import os

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
            # Try to get user's profile photo and download it
            try:
                user = await app.get_users(msg.from_user.id)
                if user.photo:
                    # Download the user's big profile photo to a temporary file
                    photo_path = await app.download_media(user.photo.big_file_id)
                    photo_input = photo_path
                else:
                    raise Exception("No profile pic")
            except Exception:
                # Fallback image
                photo_input = "https://files.catbox.moe/bjnhm5.jpg"

            # Send the photo as Spoiler (Pyrogram v2+ has 'has_spoiler' param)
            await msg.reply_photo(
                photo=photo_input,
                has_spoiler=True,
                caption=(
                    "๏ ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴍʏ ᴅᴀᴛᴀʙᴀꜱᴇ, ʏᴏᴜ'ᴠᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇꜱᴇ ᴄʜᴀɴɴᴇʟꜱ/ɢʀᴏᴜᴘꜱ ʏᴇᴛ:\n\n"
                    + "\n".join([f"[ᴊᴏɪɴ {channel}](https://t.me/{channel})" for channel in missing_channels])
                ),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await msg.stop_propagation()
            # Optionally clean up the downloaded photo file
            if "photo_path" in locals() and os.path.exists(photo_path):
                os.remove(photo_path)
        except ChatWriteForbidden:
            pass
