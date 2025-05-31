from BADMUSIC import app
from BADMUSIC.utils.database import get_assistant
from pyrogram import filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup
from os import environ

EVAA = [
    [InlineKeyboardButton(text="• ᴧᴅᴅ мᴇ ʙᴧʙʏ •", url="https://t.me/PBX_CHAT")]
]

chat_id_env = environ.get("CHAT_ID")
CHAT_ID = [int(x) for x in chat_id_env.split(",")] if chat_id_env else []

TEXT = environ.get("APPROVED_WELCOME_TEXT", "❖ ʜᴇʟʟᴏ ʙᴀʙʏ ➥ {mention}\n\n❖ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ➥ {title}\n\n")
APPROVED = environ.get("APPROVED_WELCOME", "on").lower()

# Handle new join requests
@app.on_chat_join_request((filters.group | filters.channel) & filters.chat(CHAT_ID) if CHAT_ID else (filters.group | filters.channel))
async def autoapprove(client, message: ChatJoinRequest):
    chat = message.chat
    user = message.from_user
    print(f"๏ {user.first_name} ᴊᴏɪɴᴇᴅ 🤝")
    await client.approve_chat_join_request(chat.id, user.id)
    if APPROVED == "on":
        await client.send_message(
            chat_id=chat.id,
            text=TEXT.format(mention=user.mention, title=chat.title),
            reply_markup=InlineKeyboardMarkup(EVAA),
        )
