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

    missing_channels = []
    buttons = []

    for channel in MUST_JOIN:
        try:
            await app.get_chat_member(channel, msg.from_user.id)
        except UserNotParticipant:
            try:
                # Get chat info (for both id and username)
                chat_info = await app.get_chat(channel)
                link = None
                # Try to get invite link
                if hasattr(chat_info, "username") and chat_info.username:
                    link = f"https://t.me/{chat_info.username}"
                elif hasattr(chat_info, "invite_link") and chat_info.invite_link:
                    link = chat_info.invite_link
                else:
                    # Try to export invite link (need admin rights)
                    try:
                        link = await app.export_chat_invite_link(chat_info.id)
                    except ChatAdminRequired:
                        print(f"๏ ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴀꜱ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ {channel}!")
                        continue  # Skip this channel

                if link:
                    missing_channels.append((chat_info.title or channel, link))
                    buttons.append([InlineKeyboardButton(f"ᴊᴏɪɴ {chat_info.title or channel}", url=link)])
            except ChatAdminRequired:
                print(f"๏ ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴀꜱ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ {channel}!")
                continue

    if missing_channels:
        try:
            # Try to get user's profile photo and download it
            try:
                user = await app.get_users(msg.from_user.id)
                if user.photo:
                    photo_path = await app.download_media(user.photo.big_file_id)
                    photo_input = photo_path
                else:
                    raise Exception("No profile pic")
            except Exception:
                photo_input = "https://files.catbox.moe/bjnhm5.jpg"

            # Prepare the caption with correct links
            caption = (
                "๏ ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴍʏ ᴅᴀᴛᴀʙᴀꜱᴇ, ʏᴏᴜ'ᴠᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇꜱᴇ ᴄʜᴀɴɴᴇʟꜱ/ɢʀᴏᴜᴘꜱ ʏᴇᴛ:\n\n"
                + "\n".join([f"[ᴊᴏɪɴ {title}]({link})" for title, link in missing_channels])
            )

            await msg.reply_photo(
                photo=photo_input,
                has_spoiler=True,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True
            )
            await msg.stop_propagation()
            if "photo_path" in locals() and os.path.exists(photo_path):
                os.remove(photo_path)
        except ChatWriteForbidden:
            pass
