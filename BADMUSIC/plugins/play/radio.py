from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import BANNED_USERS
from strings import get_string
from BADMUSIC import app
from BADMUSIC.utils.database import get_assistant, get_lang
from BADMUSIC.utils.decorators.radio import RadioWrapper
from BADMUSIC.utils.logger import play_logs
from BADMUSIC.utils.stream.stream import stream

# Radio Station List
RADIO_STATION = {
    "ᴀɪʀ ʙɪʟᴀsᴘᴜʀ": "http://air.pc.cdn.bitgravity.com/air/live/pbaudio110/playlist.m3u8",
    "ᴀɪʀ ʀᴀɪᴘᴜʀ": "http://air.pc.cdn.bitgravity.com/air/live/pbaudio118/playlist.m3u8",
    "ᴄᴀᴘɪᴛᴀʟ ꜰᴍ": "http://media-ice.musicradio.com/CapitalMP3?.mp3&listening-from-radio-garden=1616312105154",
    "ᴇɴɢʟɪsʜ": "https://hls-01-regions.emgsound.ru/11_msk/playlist.m3u8",
    "ᴅᴅ sᴘᴏʀᴛs": "http://103.199.161.254/Content/ddsports/Live/Channel(DDSPORTS)/index.m3u8",
    "ʀᴀᴅɪᴏ ᴛᴏᴅᴀʏ": "http://stream.zenolive.com/8wv4d8g4344tv",
    "sᴀɴsᴋᴀʀ ᴛᴠ": "https://d26idhjf0y1p2g.cloudfront.net/out/v1/cd66dd25b9774cb29943bab54bbf3e2f/index.m3u8",
    "sᴀᴅʜɴᴀ ᴛᴠ": "https://6n3yow8pl9ok-hls-live.5centscdn.com/sadhanalivetv/live.stream/playlist.m3u8",
    "ᴘᴛᴄ ᴍᴜsɪᴄ": "https://streaming.ptcplay.com/ptcMusicINOne/smil:Live.smil/playlist.m3u8",
    "𝟿xᴍ ᴍᴜsɪᴄ": "https://d2q8p4pe5spbak.cloudfront.net/bpk-tv/9XM/9XM.isml/index.m3u8",
    "ɴᴇᴡs ʙɪʜᴀʀ ᴊʜᴀʀᴋʜᴀɴᴅ": "https://ythls.armelin.one/channel/UC531MlZA5LUbeGwEN_zcppw.m3u8",
    "ɴʀᴊ ʜɪᴛs": "http://cdn.nrjaudio.fm/audio1/fr/30001/mp3_128.mp3",
    "ɪʙɪᴢᴀ ʜɪᴛs ʀᴀᴅɪᴏ": "http://streamingp.shoutcast.com/IbizaGlobalRadio",
}

# Function to create triangular buttons dynamically
def create_triangular_buttons():
    buttons = []
    stations = list(RADIO_STATION.keys())
    row_count = 2  # Number of buttons per row

    # Iterate through the stations and create buttons
    while stations:
        button_row = []
        for _ in range(min(row_count, len(stations))):
            station_name = stations.pop(0)
            button_row.append(
                InlineKeyboardButton(
                    station_name, callback_data=f"radio_station_{station_name}"
                )
            )
        buttons.append(button_row)

    return buttons


@app.on_message(
    filters.command(["radio", "radioplayforce", "cradio", "rdo"])
    & filters.group
    & ~BANNED_USERS
)
@RadioWrapper
async def radio(
    client, message: Message, _, chat_id, video, channel, playmode, url, fplay
):
    msg = await message.reply_text("ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ...")

    try:
        userbot = await get_assistant(message.chat.id)
        get = await app.get_chat_member(message.chat.id, userbot.id)

        if get.status == ChatMemberStatus.BANNED:
            return await msg.edit_text(
                text=f"» {userbot.mention} ᴀssɪsᴛᴀɴᴛ ɪs ʙᴀɴɴᴇᴅ ɪɴ {message.chat.title}.\nᴘʟᴇᴀsᴇ ᴜɴʙᴀɴ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ."
            )
    except UserNotParticipant:
        pass

    # Create triangular buttons for available radio stations
    buttons = create_triangular_buttons()

    # Create a textual list of all channels
    channels_list = "\n".join(
        [f"{i + 1}. {name}" for i, name in enumerate(RADIO_STATION.keys())]
    )

    # Send message with buttons and list of channels
    await message.reply_text(
        f"ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴘʟᴀʏ ᴀ ʀᴀᴅɪᴏ ᴄʜᴀɴɴᴇʟ:\n\n"
        f"ᴄʜᴀɴɴᴇʟ ʟɪsᴛ:\n{channels_list}\n\n"
        f"sᴇʟᴇᴄᴛ ᴀ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴘʟᴀʏ ᴛʜᴇ ʀᴇsᴘᴇᴄᴛɪᴠᴇ ʀᴀᴅɪᴏ sᴛᴀᴛɪᴏɴ.",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@app.on_callback_query(filters.regex(r"radio_station_(.*)"))
async def play_radio(client, callback_query):
    station_name = callback_query.data.split("_")[-1]
    RADIO_URL = RADIO_STATION.get(station_name)

    if RADIO_URL:
        await callback_query.message.edit_text(
            "ᴏᴋ ʙᴀʙʏ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ sᴛᴀʀᴛɪɴɢ ʏᴏᴜʀ ʀᴀᴅɪᴏ ɪɴ ᴠᴄ ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴠᴄ ᴀɴᴅ ᴇɴᴊᴏʏ😁"
        )
        language = await get_lang(callback_query.message.chat.id)
        _ = get_string(language)
        chat_id = callback_query.message.chat.id

        try:
            await stream(
                _,
                callback_query.message,
                callback_query.from_user.id,
                RADIO_URL,
                chat_id,
                callback_query.from_user.mention,
                callback_query.message.chat.id,
                video=None,
                streamtype="index",
            )
        except Exception as e:
            ex_type = type(e).__name__
            err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
            await callback_query.message.edit_text(err)
        await play_logs(callback_query.message, streamtype="Radio")
    else:
        await callback_query.message.edit_text("ɪnᴠᴀʟɪᴅ sᴛᴀᴛɪᴏɴ sᴇʟᴇᴄᴛᴇᴅ!")
