from pyrogram import Client, filters
import httpx
from BADMUSIC import app



API_URL = "http://3.0.146.239:8000/chatbot"
API_KEY = "chatai.Badmunda.workers"

@app.on_message(filters.private & filters.text)
async def chatbot_reply(client, message):
    user_text = message.text
    params = {
        "api_key": API_KEY,
        "message": user_text
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL, params=params)
            data = response.json()

        reply_text = data.get("response", "Sorry, no reply from API.")
        await message.reply_text(reply_text)

    except Exception as e:
        await message.reply_text(f"⚠️ Error: {e}")

