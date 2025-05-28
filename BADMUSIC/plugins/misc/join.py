from pytgcalls.types.events import GroupCallParticipantJoined, GroupCallParticipantLeft
from BADMUSIC import LOGGER, app, userbot
from BADMUSIC.core.call import Bad
from config import BANNED_USERS

@Bad.on_event(GroupCallParticipantJoined)
async def on_participant_joined(client, update: GroupCallParticipantJoined):
    user_id = update.user_id
    chat_id = update.chat_id
    # Log in console
    LOGGER("BADMUSIC").info(f"✅ User {user_id} joined VC in {chat_id}")
    # Send message in the same group
    try:
        await app.send_message(
            chat_id,
            f"✅ User [{user_id}](tg://user?id={user_id}) joined the voice chat."
        )
    except Exception as e:
        LOGGER("BADMUSIC").error(f"Failed to send join message: {e}")

@Bad.on_participant_left()
async def on_participant_left(client, update: GroupCallParticipantLeft):
    user_id = update.user_id
    chat_id = update.chat_id
    LOGGER("BADMUSIC").info(f"❌ User {user_id} left VC in {chat_id}")
    try:
        await app.send_message(
            chat_id,
            f"❌ User [{user_id}](tg://user?id={user_id}) left the voice chat."
        )
    except Exception as e:
        LOGGER("BADMUSIC").error(f"Failed to send leave message: {e}")
