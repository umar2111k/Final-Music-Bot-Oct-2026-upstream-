import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters
from distutils.util import strtobool

load_dotenv()

# Get this value from my.telegram.org/apps
API_ID = int(getenv("API_ID", "21404766"))
API_HASH = getenv("API_HASH", "3363e6cbefba6db06baa6710c192d71e")

# Get your token from @BotFather on Telegram.
BOT_TOKEN = getenv("BOT_TOKEN", "7485171019:AAHln_a5FzRMsN_GHP3_3l6PEVC6Gwv8EPo")

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://RonakMusicbot:AQcCEy7e@cluster0.tfkbjew.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 9000))

# Chat id of a group for logging bot's activities
LOGGER_ID = int(getenv("LOGGER_ID", "-1002495188807"))

# Get this value from @MissRose_bot on Telegram by /id
OWNER_ID = int(getenv("OWNER_ID", "6170050819"))

# Cookies # https://batbin.me
#COOKIES = getenv("COOKIES", 
COOKIES = """
# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.
.youtube.com	TRUE	/	TRUE	1738343187	GPS	1
.youtube.com	TRUE	/	TRUE	1767031721	__Secure-ROLLOUT_TOKEN	CPzWqPX_kOerqgEQ_YfAp7KgiwMY86LmteKejgM%3D
.youtube.com	TRUE	/	TRUE	1767031721	VISITOR_INFO1_LIVE	4b8Xk0ePyOc
.youtube.com	TRUE	/	TRUE	1767031721	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgLg%3D%3D
.youtube.com	TRUE	/	TRUE	1786039735	PREF	f6=40000000&f7=100&tz=Asia.Kolkata
.youtube.com	TRUE	/	FALSE	1786039721	SID	g.a000ygj6Wb5zoitukHcjukGER52KBI7lzEPSbn51ixH5rPRy4GL_olxWUZHWtEbbb3QJs-TKMAACgYKAQ8SARESFQHGX2Mi1Ed25FXqUZQimaDPTnuHfBoVAUF8yKrFz7e5fZklHfp3W2QFKMxK0076
.youtube.com	TRUE	/	TRUE	1778752481	__Secure-1PSIDTS	sidts-CjEBjplskHCBQdblI_je2-Lupz-hhWb92_fjq_uqxeb-GQzJoYeqisEcQFSU788o3ndXEAA
.youtube.com	TRUE	/	TRUE	1778752481	__Secure-3PSIDTS	sidts-CjEBjplskHCBQdblI_je2-Lupz-hhWb92_fjq_uqxeb-GQzJoYeqisEcQFSU788o3ndXEAA
.youtube.com	TRUE	/	TRUE	1786039721	__Secure-1PSID	g.a000ygj6Wb5zoitukHcjukGER52KBI7lzEPSbn51ixH5rPRy4GL_tyfIRn53ezCue7CDa9lsQwACgYKARsSARESFQHGX2MigBLByJlPtYjwlqXKKVhmdxoVAUF8yKpO8XZGn5LJhu2PHptCjPJ-0076
.youtube.com	TRUE	/	TRUE	1786039721	__Secure-3PSID	g.a000ygj6Wb5zoitukHcjukGER52KBI7lzEPSbn51ixH5rPRy4GL_Q4ndqXAZ4nsRGz-bJSxQtwACgYKAYkSARESFQHGX2MiJ8ubh5kr5Btr4ej1ecV3jxoVAUF8yKrhXEjXmPaJdxuxHBi_niPS0076
.youtube.com	TRUE	/	FALSE	1786039721	HSID	AYqrqib9VVSMNjMXf
.youtube.com	TRUE	/	TRUE	1786039721	SSID	AxX_HqOcaHlEB6dN6
.youtube.com	TRUE	/	FALSE	1786039721	APISID	cLQ16w8PDbdczbQa/A6pdpNJuzEceIn52L
.youtube.com	TRUE	/	TRUE	1786039721	SAPISID	GCXaO25UzaKgjIQ1/AqOvUCcx9EAEGeka7
.youtube.com	TRUE	/	TRUE	1786039721	__Secure-1PAPISID	GCXaO25UzaKgjIQ1/AqOvUCcx9EAEGeka7
.youtube.com	TRUE	/	TRUE	1786039721	__Secure-3PAPISID	GCXaO25UzaKgjIQ1/AqOvUCcx9EAEGeka7
.youtube.com	TRUE	/	FALSE	1783015735	SIDCC	AKEyXzX30KUNh1ip0qdiJGc9wAGFtLuQ22m03mBJQj7dq_12Qn2ylbVsZ2HKUPYG-npWOlZhqw
.youtube.com	TRUE	/	TRUE	1783015735	__Secure-1PSIDCC	AKEyXzXnxzPNcFBhB0Q0XyMMEXudkclQXYPiA1E5l9igLOVk6KEVSlhUp3btNY1DQmxqkZqMFA
.youtube.com	TRUE	/	TRUE	1783015735	__Secure-3PSIDCC	AKEyXzUqIIrIqUrks74_HjDucA50HuKFBVEeTbIpIrlTmruqmbkMqnvE5MK6CEKg15CaNxZ8sg
.youtube.com	TRUE	/	TRUE	1781776481	LOGIN_INFO	AFmmF2swRQIhAJUAC6rkobPuJ2SacvSIIA9YdTg5QhMBV5e12_Y2AGwBAiAl-xGE73m0JI6XJc5n2G45EWBerLLReHkjOuQzrEdFYw:QUQ3MjNmekZnaEd1ZWVNbndXc1R2Q2RYUlUzMU0yQ2RHbjdDOU1MOWpWWDQtM3BCNzB6dllBUGtDS3h5OXY2d3lYVnRTaXc2WDlkdVBIaGgzVDh4WFRZTWFuVUdvbDBQLW9EalVqNkZJVUVEM2IwdEpqYlpvMmRpc21ETW9WZDhua2dIS0V1eDBlaWJVZnlOX0dJQ2IxdS1NR0Ytb05FSS13
.youtube.com	TRUE	/	FALSE	1738341476	ST-1v5m675	csn=RGuhJgZFXHqq0mvJ&itct=CHQQoTAYACITCNm6yMyyoIsDFatynQkd0GcE-Q%3D%3D
.youtube.com	TRUE	/	FALSE	1738341488	ST-fkjj2x	csn=bIyeS6RFtNznS_eJ&itct=CCEQh_YEGAIiEwiG35TRsqCLAxVcfJ0JHdEnNyRaGFVDRXhzN1ZZMHoxNjJ1SFZaSDhtR0l1d5oBBQgAEPI4
.youtube.com	TRUE	/	FALSE	1738341491	ST-y5u8dv	csn=bIyeS6RFtNznS_eJ&itct=CCcQh_YEGAAiEwiG35TRsqCLAxVcfJ0JHdEnNyRaGFVDRXhzN1ZZMHoxNjJ1SFZaSDhtR0l1d5oBBQgAEPI4
.youtube.com	TRUE	/	FALSE	1738341492	ST-15ody3h	csn=bIyeS6RFtNznS_eJ&itct=CCQQh_YEGAEiEwiG35TRsqCLAxVcfJ0JHdEnNyRaGFVDRXhzN1ZZMHoxNjJ1SFZaSDhtR0l1d5oBBQgAEPI4
.youtube.com	TRUE	/	FALSE	1739825052	ST-143rzh2	csn=70ULf5XOyG7NvNhm&itct=CBgQ08wBGAEiEwiBnL2tycuLAxXk3jgGHSFEOxcyBmctaGlnaA%3D%3D
.youtube.com	TRUE	/	FALSE	1739825055	ST-1lb2hub	csn=70ULf5XOyG7NvNhm&itct=CBEQmJUGGAIiEwiBnL2tycuLAxXk3jgGHSFEOxc%3D
.youtube.com	TRUE	/	FALSE	1739825075	ST-13pmvng	csn=ZTUYjoAo6YzOfjtI&itct=CEcQ_FoiEwi9v_yqycuLAxUVSl4EHU5DHiMyCmctaGlnaC1yZWNaD0ZFd2hhdF90b193YXRjaJoBBhCOHhieAQ%3D%3D
.youtube.com	TRUE	/	FALSE	1739825080	ST-10j0w0a	csn=QJK_SKtcdJJdAh9d&itct=CEEQnaQHGAEiEwiBnL2tycuLAxXk3jgGHSFEOxdaCUZFbGlicmFyeZoBBwi4ARDv8AU%3D
.youtube.com	TRUE	/	FALSE	1739825081	ST-94llcf	csn=QJK_SKtcdJJdAh9d&itct=CDwQrKoBGAMiEwiBnL2tycuLAxXk3jgGHSFEOxcyCmctaGlnaC1jcHdaCUZFbGlicmFyeZoBBwi4ARDv8AU%3D
.youtube.com	TRUE	/	FALSE	1739825085	ST-1mga6p0	csn=QJK_SKtcdJJdAh9d&itct=CC4QrKoBGAkiEwiBnL2tycuLAxXk3jgGHSFEOxcyCmctaGlnaC1jcHdaCUZFbGlicmFyeZoBBwi4ARDv8AU%3D
.youtube.com	TRUE	/	FALSE	1745490614	ST-ic9um4	csn=2oqaJpu6p8P8NNeA&itct=CJoBEPxaIhMI3q3KmLvwjAMVZF71Bx0VfBd7MgpnLWhpZ2gtcmVjWg9GRXdoYXRfdG9fd2F0Y2iaAQYQjh4YngE%3D
.youtube.com	TRUE	/	FALSE	1747216501	ST-32nzby	csn=jGqMVXaFyHto3v-0&itct=CDkQ_FoiEwjL47TO2KKNAxUwQioJHQV4NJoyCmctaGlnaC1yZWNaD0ZFd2hhdF90b193YXRjaJoBBhCOHhieAQ%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	4SCGsP_C1r4
.youtube.com	TRUE	/	FALSE	1751479742	ST-1t6yh3d	csn=PcEdNXSPQrM0Y3d2&itct=CE8Q_FoiEwiWvum14p6OAxXWXvUHHTz9NX0yCmctaGlnaC1yZWNaD0ZFd2hhdF90b193YXRjaJoBBhCOHhieAQ%3D%3D
.youtube.com	TRUE	/	FALSE	1751479819	ST-o33lu0	csn=YCr-QY2AezrDOM8_&itct=CIkBEPxaGAAiEwjNvf-74p6OAxVasqwCHbRGN0kyB3JlbGF0ZWRIurP0wv_82uuHAZoBBQgBEPgd 
""")


# Set it true if you want your bot to be private only [You'll need to allow CHAT_ID via /authorize command then only your bot will play music in that chat.]
PRIVATE_BOT_MODE = strtobool(getenv("PRIVATE_BOT_MODE", "True"))

## Fill these variables if you're deploying on heroku.
# Your heroku app name
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", "ronak-musicc")
# Get it from http://dashboard.heroku.com/account
HEROKU_API_KEY = getenv("HEROKU_API_KEY", "HRKU-AAlONfi-HBe995oIayzXbJEPyzox4kQaWoHR9y9xOegQ_____wopzvHPi8WE")

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/Pbx-Official/BADMUSIC",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "Bad")
GIT_TOKEN = getenv(
    "GIT_TOKEN", None
)  # Fill this variable if your upstream repository is private

API_URL = getenv("API_URL", 'https://api.thequickearn.xyz') 
API_KEY = getenv("API_KEY", '30DxNexGenBots938b57') 

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/Spark_Developer")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/Spark_Developer")

# Set this to True if you want the assistant to automatically leave chats after an interval
AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", False))


# Get this credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "19d2fe49f79143fa90e75be9c95255db")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "9e3e42756a8040a89424e7bf3343fa19")


# Maximum limit for fetching playlist's track from youtube, spotify, apple links.
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))


# Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))
# Checkout https://www.gbmb.org/mb-to-bytes for converting mb to bytes


# Get your pyrogram v2 session from @StringFatherBot on Telegram
STRING1 = getenv("STRING_SESSION", None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)


BANNED_USERS = filters.user()
TEMP_DB_FOLDER = "Tempdb"
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}
LOG = 2



START_IMG_URL = getenv(
    "START_IMG_URL", "https://files.catbox.moe/f3bqbs.jpg"
)
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://files.catbox.moe/g35in5.jpg"
)
PLAYLIST_IMG_URL = "https://telegra.ph/file/7795e58425337d0455e95.jpg"
STATS_IMG_URL = "https://files.catbox.moe/7wvzw1.jpg"
TELEGRAM_AUDIO_URL = "https://telegra.ph/file/d2081243af7c1d7578b7b.jpg"
TELEGRAM_VIDEO_URL = "https://telegra.ph/file/d2081243af7c1d7578b7b.jpg"
STREAM_IMG_URL = "https://telegra.ph/file/982b01ba53c3d69b0d0ce.jpg"
SOUNCLOUD_IMG_URL = "https://telegra.ph/file/982b01ba53c3d69b0d0ce.jpg"
YOUTUBE_IMG_URL = "https://telegra.ph/file/d2081243af7c1d7578b7b.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://telegra.ph/file/61024698bfc926e95d57a.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://telegra.ph/file/61024698bfc926e95d57a.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://telegra.ph/file/61024698bfc926e95d57a.jpg"

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))


if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
)
