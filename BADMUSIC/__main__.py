import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from BADMUSIC import LOGGER, app, userbot
from BADMUSIC.core.call import Bad
from BADMUSIC.misc import sudo
from BADMUSIC.plugins import ALL_MODULES
from BADMUSIC.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS

# Color codes for terminal output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
PURPLE = '\033[0;35m'
CYAN = '\033[0;36m'
PINK = '\033[1;35m'
NC = '\033[0m'

BANNER = f"""
{RED}  ____   ____ _______    _____ _______       _____ _______ ______ _____   {NC}
{GREEN} |  _ \\ / __ \\__   __|  / ____|__   __|/\\   |  __ \\__   __|  ____|  __ \\  {NC}
{YELLOW} | |_) | |  | | | |    | (___    | |  /  \\  | |__) | | |  | |__  | |  | | {NC}
{BLUE} |  _ <| |  | | | |     \\___ \\   | | / /\\ \\ |  _  /  | |  |  __| | |  | | {NC}
{PURPLE}| |_) | |__| | | |     ____) |  | |/ ____ \\| | \\ \\  | |  | |____| |__| | {NC}
{CYAN} |____/ \\____/  |_|    |_____/   |_/_/    \\_\\_|  \\_\\ |_|  |______|_____/  {NC}
"""

async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("✦ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴄʟɪᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇꜱ ɴᴏᴛ ᴅᴇꜰɪɴᴇᴅ, ᴇxɪᴛɪɴɢ...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("BADMUSIC.plugins" + all_module)
    LOGGER("BADMUSIC.plugins").info("✦ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ ᴍᴏᴅᴜʟᴇꜱ...💞")
    await userbot.start()
    await Bad.start()
    try:
        await Bad.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("BADMUSIC").error(
            "✦ ᴘʟᴇᴀꜱᴇ ᴛᴜʀɴ ᴏɴ ᴛʜᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ᴏꜰ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ\\ᴄʜᴀɴɴᴇʟ.\n\n✦ ꜱᴛᴏᴘᴘɪɴɢ ʙᴀᴅᴍᴜꜱɪᴄ ʙᴏᴛ..."
        )
        exit()
    except:
        pass

    await Bad.decorators()
    print(BANNER)

    LOGGER("BADMUSIC").info(
        ""
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("BADMUSIC").info("❖ ꜱᴛᴏᴘᴘɪɴɢ ʙᴀᴅ ᴍᴜꜱɪᴄ ʙᴏᴛ...💌")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
