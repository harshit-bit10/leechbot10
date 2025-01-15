import json
#Jio Cinema Downloader Bot Created By Aryan Chaudhary
import re
import asyncio
import utils
import yt_dlp
import jiocine
import subprocess
from pyrogram import Client, filters, idle
from urllib import parse
import time
import logging
import ffmpeg
from cdm.devices import devices
from cdm.wvdecrypt import WvDecrypt
from base64 import b64decode, b64encode
from yt_dlp.postprocessor import PostProcessor
from utils import scriptsDir, joinPath, realPath
from asyncio import create_subprocess_exec, create_subprocess_shell, run_coroutine_threadsafe, sleep
from pyrogram.errors import FloodWait
#from button import ButtonMaker
def atos(func, *args, wait=True, **kwargs):
    future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
    return future.result() if wait else future
import os
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Set up logging
logging.basicConfig(level=logging.INFO)  # Set the logging level
logger = logging.getLogger(__name__)  # Create a logger object

# Language Id Name Map
lang_map = {
    "en": "English",
    "hi": "Hindi",
    "gu": "Gujarati",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "mr": "Marathi",
    "ml": "Malayalam",
    "bn": "Bengali",
    "bho": "Bhojpuri",
    "pa": "Punjabi",
    "jp": "Japanese",
    "or": "Oriya"
}





class ButtonMaker:
    def __init__(self):
        self.__button = []
        self.__header_button = []
        self.__first_body_button = []
        self.__last_body_button = []
        self.__footer_button = []

    def ubutton(self, key, link, position=None):
        if not position:
            self.__button.append(InlineKeyboardButton(text=key, url=link))
        elif position == 'header':
            self.__header_button.append(InlineKeyboardButton(text=key, url=link))
        elif position == 'f_body':
            self.__first_body_button.append(InlineKeyboardButton(text=key, url=link))
        elif position == 'l_body':
            self.__last_body_button.append(InlineKeyboardButton(text=key, url=link))
        elif position == 'footer':
            self.__footer_button.append(InlineKeyboardButton(text=key, url=link))

    def ibutton(self, key, data, position=None):
        if not position:
            self.__button.append(InlineKeyboardButton(text=key, callback_data=data))
        elif position == 'header':
            self.__header_button.append(InlineKeyboardButton(text=key, callback_data=data))
        elif position == 'f_body':
            self.__first_body_button.append(InlineKeyboardButton(text=key, callback_data=data))
        elif position == 'l_body':
            self.__last_body_button.append(InlineKeyboardButton(text=key, callback_data=data))
        elif position == 'footer':
            self.__footer_button.append(InlineKeyboardButton(text=key, callback_data=data))

    def build_menu(self, b_cols=1, h_cols=8, fb_cols=2, lb_cols=2, f_cols=8):
        menu = [self.__button[i:i+b_cols]
                for i in range(0, len(self.__button), b_cols)]
        if self.__header_button:
            if len(self.__header_button) > h_cols:
                header_buttons = [self.__header_button[i:i+h_cols]
                                  for i in range(0, len(self.__header_button), h_cols)]
                menu = header_buttons + menu
            else:
                menu.insert(0, self.__header_button)
        if self.__first_body_button:
            if len(self.__first_body_button) > fb_cols:
                [menu.append(self.__first_body_button[i:i+fb_cols])
                 for i in range(0, len(self.__first_body_button), fb_cols)]
            else:
                menu.append(self.__first_body_button)
        if self.__last_body_button:
            if len(self.__last_body_button) > lb_cols:
                [menu.append(self.__last_body_button[i:i+lb_cols])
                 for i in range(0, len(self.__last_body_button), lb_cols)]
            else:
                menu.append(self.__last_body_button)
        if self.__footer_button:
            if len(self.__footer_button) > f_cols:
                [menu.append(self.__footer_button[i:i+f_cols])
                 for i in range(0, len(self.__footer_button), f_cols)]
            else:
                menu.append(self.__footer_button)
        return InlineKeyboardMarkup(menu)

# Generate main config file from definition config before starting
configPath = joinPath(scriptsDir, 'config.json')
if not utils.isExist(configPath):
    utils.copyFile(joinPath(scriptsDir, 'config.def'), configPath)

# Some important variables
default_res = ""
default_strm = ''
config = utils.JSO(configPath, 4)
app = Client(
    "SHARKOTTDLBOT",
    bot_token="7439562089:AAGrjFfGXkwAReLtzhSn1aDMi7j7e_oHTZs",
    api_id="7603458",
    api_hash="910e420f1f74f40305a684a331dade35",
    sleep_threshold=30
)

# List of sudo users (user IDs and group IDs)
sudo_users = [6066102279]   # Add your user IDs here
sudo_groups = [-1002273763090]  # Add your group ID here (negative ID for groups)
dump_chat_id = [-1002316955124]
credits = "SharkToonsIndia"

async def is_user_sudo(client, user_id):
    # Check if the user is in the sudo_users list
    if user_id in sudo_users:
        return True

    # Check if the user is a member of any of the sudo_groups
    for group_id in sudo_groups:
        try:
            chat_member = await client.get_chat_member(group_id, user_id)
            # Allow access if the user is a member of the group
            return True  # If the user is found in the group, grant access
        except Exception as e:
            print(f"Error checking group membership for group {group_id}: {e}")

    return False

@app.on_message(filters.private)  # Only respond to private messages
async def handle_private_message(client, message):
    user_id = message.from_user.id  # Get the user ID of the sender

    # Check if the user is authorized
    if user_id not in sudo_users:
        # Send a message if the user is not authorized
        await message.reply(
            "<code>Hey Dude, seems like master hasn't given you access to use me.\n"
            "Please contact him immediately at</code> <b> @SupremeYoriichi</b>"
        )
        return  # Exit the function if the user is not authorized

    # If the user is authorized, send them a welcome message
    await message.reply("<code>You Have Access, Bot By</code> <b>@SupremeYoriichi</b>")

def sudo_only(func):
    async def wrapper(client, message):
        if not await is_user_sudo(client, message.from_user.id):
            await message.reply_text("You do not have permission to use this command.")
            return
        return await func(client, message)
    return wrapper


# Global variables to store user selections
# At the top of your script
global content_name  # Declare it as global
user_audio_selection = set()  # Use a set for audio selections
user_video_selection = set()  # Initialize as a set for video selections
content_data = None
processing_states = {}
ydl_opts = {}  # Initialize ydl_opts as a global variable
# At the top of your script
output_dir_name = ""
output_dir = ""
temp_dir = ""
audio_formats = []  # Global variable for audio formats
video_formats = []  # Global variable for video formats
global playback_url  # Declare playback_url as global
global processed_abrs  # Add this line
global processed_vbrs  # Add this line
processed_vbrs = []  # Initialize processed_vbrs as an empty list
acodecs = []  # Global variable for processed audio information
vcodecs = []  # Global variable for processed video information
selected_stream_type = None
# Global variable to track link processing state
is_processing_link = False
chat_id = None
global rid_map  # Add this line at the top of your script
rid_map = {}  # Initialize it as an empty dictionary

# Download playback function
async def download_playback(content_id, content_data, callback_query):
    logging.info(f"Starting download playback for Content ID: {content_id}")

    initial_message = await callback_query.message.reply_text('[=>] Fetching Playback Details...')
    is_processing_link = False  # Reset the processing state after the operation is complete

    try:
        # Fetch playback data using the content ID and auth token
        content_playback = jiocine.fetchPlaybackData(content_id, config.get("authToken"))
        logging.info(f"Fetched playback data: {content_playback}")

        # Check if playback data was successfully retrieved
        if not content_playback:
            logging.warning(f"No playback details found for Content ID: {content_id}")
            await initial_message.delete()
            await callback_query.message.reply_text("[X] Playback Details Not Found!")
            is_processing_link = False
            return

        playback_urls = content_playback.get("playbackUrls", [])  # Use .get() to avoid KeyError
        n_playbacks = len(playback_urls)
        logging.info(f"Number of playback URLs found: {n_playbacks}")

        # Ask user to select stream type if multiple playback URLs are available
        if n_playbacks > 1:
            logging.info("Multiple playback URLs found. Asking user for stream type selection.")
            await initial_message.delete()
            await callback_query.message.reply_text(
                "Which Stream Type do you prefer? (HLS or DASH)", 
                reply_markup=create_inline_buttons(["HLS", "DASH"], "stream_type")
            )
        elif n_playbacks == 1:
            logging.info("Single playback URL found. Processing immediately.")
            await initial_message.delete()
            playback_data = playback_urls[0]
            await process_playback_data(playback_data, callback_query)
            return

        # If no playback data is available, inform the user
        if n_playbacks == 0:
            logging.warning("No playback data available.")
            await initial_message.delete()
            await callback_query.message.reply_text("[X] No playback data available. Please try again.")
            return
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        await initial_message.delete()
        await callback_query.message.reply_text("[X] An unexpected error occurred. Please try again later.")


# Handle stream type selection (HLS or DASH)
# Handle stream type selection (HLS or DASH)
@app.on_callback_query(filters.regex(r"^stream_type_(\w+)$"))
async def handle_stream_type_selection(client, callback_query):
    global selected_stream_type  # Use the global variable to track the selected stream type
    await callback_query.answer()
    selected_stream_type = callback_query.data.split("_")[-1]  # Get the selected stream type (HLS or DASH)

    # Fetch playback data based on the selected stream type
    content_playback = jiocine.fetchPlaybackData(content_data['id'], config.get("authToken"))

    if not content_playback:
        await callback_query.message.reply_text("[!] Unable to fetch playback data. Please try again.")
        return

    playback_urls = content_playback.get("playbackUrls", [])
    
    if not playback_urls:
        await callback_query.message.reply_text("[!] No playback URLs found for the selected stream type.")
        return

    # Select the first available playback URL
    playback_data = playback_urls[0]
    global playback_url
    playback_url = playback_data['url']  # Store the URL

    # Inform the user about the selected stream type and playback URL
    stream_type_message = await callback_query.message.reply_text(f'[*] Selected Stream Type: {selected_stream_type}')
    playback_url_message = await callback_query.message.reply_text(f'[*] Playback URL: {playback_url}')

    # Proceed with the download process
    await process_playback_data(playback_data, callback_query)

    # Delete the stream type and playback URL messages after a short delay
    await stream_type_message.delete()
    await playback_url_message.delete()
    # Also delete the inline buttons message
    await callback_query.message.delete()  # This will delete the message containing the inline buttons

async def process_playback_data(playback_data, callback_query):
    global playback_url, rid_map  # Declare rid_map as global
    if not playback_data:
        await callback_query.message.reply_text("[X] Unable to get Playback Url!")
        return

    playback_url = playback_data['url']  # Store the URL

    # Log the required information to the console
    print(f"Playback URL: {playback_url}, Encryption: {playback_data.get('encryption', 'None')}, Stream Type: {playback_data.get('streamtype', 'Unknown')}")

    # Fetch MPD data if the stream type is DASH
    if playback_data["streamtype"] == "dash":
        getting_mpd_message = await callback_query.message.reply_text('[ =>] Getting MPD manifest data...')
        mpd_data = jiocine.getMPDData(playback_data["url"])
        if not mpd_data:
            await getting_mpd_message.delete()  # Delete the getting MPD message
            await callback_query.message.reply_text("[!] Failed to get MPD manifest")
            return

        periods = mpd_data['MPD']['Period']
        if not periods:
            await getting_mpd_message.delete()  # Delete the getting MPD message
            await callback_query.message.reply_text("[!] Failed to parse MPD manifest")
            return

        # Extract rid_map and pssh_kid
        rid_map, pssh_kid = jiocine.parseMPDData(periods)  # Ensure this function returns the correct values

        # Proceed with decryption if PSSH keys are available
        if len(pssh_kid) > 0:
            await fetch_widevine_keys(pssh_kid, content_playback, playback_data)
            await download_vod_ytdlp(playback_data['url'], content_data, callback_query, has_drm=True, rid_map=rid_map)
        else:
            await getting_mpd_message.delete()  # Delete the getting MPD message
            pssh_message = await callback_query.message.reply_text("[!] Can't find PSSH, Content may be Encrypted")
            await download_vod_ytdlp(playback_data['url'], content_data, callback_query)
    elif playback_data["streamtype"] == "hls" and playback_data["encryption"] == "aes128":
        await download_vod_ytdlp(playback_data['url'], content_data, callback_query)
    else:
        await callback_query.message.reply_text("[X] Unsupported Stream Type!")

    await asyncio.sleep(1)  # Wait for 1 seconds (or your desired duration)
    await pssh_message.delete()  # Delete the message

def extractyt(url, ci):
    try:
        os.remove(f"info{ci}.json")
    except Exception:
        pass
    
    # Run yt-dlp with a longer timeout
    result = subprocess.run(
        f"yt-dlp --dump-json {url} > info{ci}.json",
        shell=True,
        timeout=60  # Set a timeout of 60 seconds
    )
    
    # Check if the command was successful
    if result.returncode != 0:
        print("[!] yt-dlp command failed. Please check the URL or your network connection.")
        return None  # Return None if the command fails

    # Load the JSON data
    try:
        with open(f'info{ci}.json', 'r') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        print("[!] Failed to decode JSON. The file may be empty or corrupted.")
        return None  # Return None if JSON decoding fails





def round_to_nearest_even(num):
    """Round to the nearest even number."""
    rounded = round(num)
    if rounded % 2 != 0:  # If the rounded number is odd
        rounded += 1 if rounded > num else -1  # Adjust to the nearest even
    return rounded

def process_vbrs(video_formats):
    """Process the video bitrates (vbr) for a list of video formats."""
    processed_vbrs = []
    
    for fmt in video_formats:
        # Try to get the bitrate from different keys
        vbr = fmt.get('bitrate') or fmt.get('tbr') or fmt.get('vbr')  # Check for multiple keys
        if vbr is not None:
            processed_vbrs.append(int(vbr))  # Convert to integer and add to the list
        else:
            processed_vbrs.append(0)  # Append a default value if no bitrate is found

    return processed_vbrs

def process_abrs(audio_formats):
    """Process the average bitrates (abr) for a list of audio formats."""
    processed_abrs = []
    
    for i in range(len(audio_formats)):
        fmt = audio_formats[i]
        abr = fmt.get('abr')

        if abr is not None:
            # Remove decimal part
            abr_int = int(abr)
            is_even = (abr_int % 2 == 0)

            # Check against all other formats
            for j in range(len(audio_formats)):
                if i != j:  # Don't compare with itself
                    next_fmt = audio_formats[j]
                    next_abr = next_fmt.get('abr')

                    if next_abr is not None:
                        next_abr_int = int(next_abr)

                        # Check if the difference is within 2 kbps
                        if abs(abr_int - next_abr_int) <= 2:
                            # If either is even, use the even one
                            if is_even:
                                processed_abrs.append(abr_int)
                                break
                            elif next_abr_int % 2 == 0:
                                processed_abrs.append(next_abr_int)
                                break
                            else:
                                # Calculate the average and round to the nearest even number
                                average_bitrate = (abr_int + next_abr_int) / 2
                                processed_abrs.append(round_to_nearest_even(average_bitrate))
                                break
            else:
                # If no matches found, just add the rounded value
                processed_abrs.append(abr_int)

    return processed_abrs


# Mapping of longer audio codec names to shorter representations

cacodec_mapping = {
    "mp4a.40.29": "AAC.2.0",  # AAC LC
    "mp4a.40.2": "AAC.2.0",   # AAC LC
    "mp4a.40.5": "AAC.5.1",   # AAC HE
    "mp4a.40.21": "AAC.5.1",  # AAC HEv1
    "mp4a.40.22": "AAC.5.1",  # AAC HEv2
    "mp4a.40.28": "AAC.ELD",  # AAC ELD
    "mp4a.366": "AAC",        # AAC
    "aac": "AAC",             # AAC
    "mp3": "MP3",             # MP3
    "opus": "Opus",           # Opus
    "vorbis": "Vorbis",       # Vorbis
    "flac": "FLAC",           # FLAC
    "pcm_s16le": "PCM.16-bit", # PCM 16-bit little-endian
    "pcm_s24le": "PCM.24-bit", # PCM 24-bit little-endian
    "alac": "ALAC",           # ALAC
    "ac3": "AC3",             # AC3
    "eac3": "EAC3",           # EAC3
    "dts": "DTS",             # DTS
    "dts_hd": "DTS-HD",       # DTS-HD
    "aiff": "AIFF",           # AIFF
    "aif": "AIFF",            # AIFF
    "mp2": "MP2",             # MP2
    "mp2a": "MP2",            # MP2 Audio
    "gsm": "GSM",             # GSM
    "g726": "G.726",          # G.726
    "g722": "G.722",          # G.722
    "g711": "G.711",          # G.711
    "m4a": "M4A",             # M4A
    "m4b": "M4B",             # M4B
    "m4p": "M4P",             # M4P
    "aac_plus": "AAC.Plus",   # AAC Plus
    "mpc": "Musepack",        # Musepack
    "wv": "WavPack",          # WavPack
    "tta": "TTA",             # TTA
    "ape": "APE",             # APE
    "dsd": "DSD",             # DSD
    "dff": "DFF",             # DFF
    "dsf": "DSF",             # DSF
    "wma": "WMA",             # WMA
    "wma_pro": "WMA.Pro",     # WMA Pro
    "wma_lossless": "WMA.Lossless", # WMA Lossless
    "aac_he": "HE.AAC",       # HE-AAC
    "aac_he_v2": "HE.AAC.v2", # HE-AAC v2
    "mp3_hd": "MP3.HD",       # MP3 HD
    "mp3_pro": "MP3.Pro",     # MP3 Pro
    "midi": "MIDI",           # MIDI
    "xmf": "XMF",             # XMF
    "spx": "Speex",           # Speex
    "opus_vbr": "Opus.VBR",   # Opus VBR
    "opus_cbr": "Opus.CBR",   # Opus CBR
    "opus_lossless": "Opus.Lossless", # Opus Lossless
    "ac-3": "DD+2.0",  #DD
    "ec-3": "DD+5.1", #DD
    "flac_lossless": "FLAC.Lossless", # FLAC Lossless
    "flac_highres": "FLAC.High.Resolution", # FLAC High Resolution
    "aiff_c": "AIFF.C",       # AIFF-C
    "aifc": "AIFF.C",         # AIFF-C
    "m4a_aac": "M4A.AAC",     # M4A with AAC
    "m4a_alac": "M4A.ALAC",   # M4A with ALAC
    "m4a_mp3": "M4A.MP3",     # M4A with MP3
    "m4a_aac_plus": "M4A.AAC.Plus", # M4A with AAC Plus
}

codec_mapping = {
    "mp4a.40.29": "mp4a",  # AAC LC
    "mp4a.40.2": "mp4a",   # AAC LC
    "mp4a.40.5": "mp4a",   # AAC HE
    "mp4a.40.21": "mp4a",  # AAC HEv1
    "mp4a.40.22": "mp4a",  # AAC HEv2
    "mp4a.40.28": "mp4a",  # AAC ELD
    "mp4a.366": "mp4a",    # AAC
    "aac": "aac",          # AAC
    "mp3": "mp3",          # MP3
    "opus": "opus",        # Opus
    "vorbis": "vorbis",    # Vorbis
    "flac": "flac",        # FLAC
    "pcm_s16le": "pcm",    # PCM 16-bit little-endian
    "pcm_s24le": "pcm",    # PCM 24-bit little-endian
    "alac": "alac",        # ALAC
    "ac3": "ac3",          # AC3
    "eac3": "eac3",        # EAC3
    "dts": "dts",          # DTS
    "dts_hd": "dts",       # DTS-HD
    "aiff": "aiff",        # AIFF
    "aif": "aiff",         # AIFF
    "mp4a.40.28": "mp4a",  # AAC ELD
    "mp4a.40.2": "mp4a",   # AAC LC
    "mp4a.40.5": "mp4a",   # AAC HE
    "mp4a.40.21": "mp4a",  # AAC HEv1
    "mp4a.40.22": "mp4a",  # AAC HEv2
    "mp4a.40.29": "mp4a",  # AAC LC
    "mp4a.40.2": "mp4a",   # AAC LC
    "mp4a.40.5": "mp4a",   # AAC HE
    "mp4a.40.21": "mp4a",  # AAC HEv1
    "mp4a.40.22": "mp4a",  # AAC HEv2
    "mp4a.40.28": "mp4a",  # AAC ELD
    "mp4a.366": "mp4a",    # AAC
    "aac": "aac",          # AAC
    "mp3": "mp3",          # MP3
    "opus": "opus",        # Opus
    "vorbis": "vorbis",    # Vorbis
    "flac": "flac",        # FLAC
    "pcm_s16le": "pcm",    # PCM 16-bit little-endian
    "pcm_s24le": "pcm",    # PCM 24-bit little-endian
    "alac": "alac",        # ALAC
    "ac3": "ac3",          # AC3
    "eac3": "eac3",        # EAC3
    "dts": "dts",          # DTS
    "dts_hd": "dts",       # DTS-HD
    "aiff": "aiff",        # AIFF
    "aif": "aiff",         # AIFF
    "mp4a.40.29": "mp4a",  # AAC LC
    "mp4a.40.2": "mp4a",   # AAC LC
    "mp4a.40.5": "mp4a",   # AAC HE
    "mp4a.40.21": "mp4a",  # AAC HEv1
    "mp4a.40.22": "mp4a",  # AAC HEv2
    "mp4a.40.28": "mp4a",  # AAC ELD
    "mp4a.366": "mp4a",    # AAC
 "aac": "aac",          # AAC
    "mp3": "mp3",          # MP3
    "opus": "opus",        # Opus
    "vorbis": "vorbis",    # Vorbis
    "flac": "flac",        # FLAC
    "pcm_s16le": "pcm",    # PCM 16-bit little-endian
    "pcm_s24le": "pcm",    # PCM 24-bit little-endian
    "alac": "alac",        # ALAC
    "ac3": "ac3",          # AC3
    "eac3": "eac3",        # EAC3
    "dts": "dts",          # DTS
    "dts_hd": "dts",       # DTS-HD
    "aiff": "aiff",        # AIFF
    "aif": "aiff",         # AIFF
    "mp2": "mp2",          # MP2
    "mp2a": "mp2",         # MP2 Audio
    "gsm": "gsm",          # GSM
    "g726": "g726",        # G.726
    "g722": "g722",        # G.722
    "g711": "g711",        # G.711
    "m4a": "m4a",          # M4A
    "m4b": "m4b",          # M4B
    "m4p": "m4p",          # M4P
    "aac_plus": "aac",     # AAC Plus
    "mpc": "mpc",          # Musepack
    "wv": "wv",            # WavPack
    "tta": "tta",          # TTA
    "ape": "ape",          # APE
    "dsd": "dsd",          # DSD
    "dff": "dff",          # DFF
    "dsf": "dsf",          # DSF
    "wma": "wma",          # WMA
    "wma_pro": "wma",      # WMA Pro
    "wma_lossless": "wma", # WMA Lossless
    "aac_he": "aac",       # HE-AAC
    "aac_he_v2": "aac",    # HE-AAC v2
    "mp3_hd": "mp3",       # MP3 HD
    "mp3_pro": "mp3",      # MP3 Pro
    "midi": "midi",        # MIDI
    "xmf": "xmf",          # XMF
    "spx": "spx",          # Speex
    "ac-3": "ac-3",  #DD
    "ec-3": "ec-3",  #DD
    "opus_vbr": "opus",    # Opus VBR
    "opus_cbr": "opus",    # Opus CBR
    "opus_lossless": "opus", # Opus Lossless
    "flac_lossless": "flac", # FLAC Lossless
    "flac_highres": "flac",  # FLAC High Resolution
    "aiff_c": "aiff",      # AIFF-C
    "aifc": "aiff",        # AIFF-C
    "m4a_aac": "m4a",      # M4A with AAC
    "m4a_alac": "m4a",     # M4A with ALAC
    "m4a_mp3": "m4a",      # M4A with MP3
    "m4a_aac_plus": "m4a", # M4A with AAC Plus
}

def get_acodecs(audio_formats):
    """Extract and shorten audio codecs from the provided audio formats."""
    return [codec_mapping.get (fmt.get('acodec', 'Unknown'), fmt.get('acodec', 'Unknown')) for fmt in audio_formats]

# Mapping of longer video codec names to shorter representations
cvcodec_mapping = {
    "avc1.42E01E": "H.264",              # H.264 Baseline Profile
    "avc1.42E01F": "H.264",              # H.264 Baseline Profile 10-bit
    "avc1.4D401E": "H.264",              # H.264 Main Profile
    "avc1.4D401F": "H.264",              # H.264 Main Profile 10-bit
    "avc1.64001E": "H.264",              # H.264 High Profile
    "avc1.64001F": "H.264",              # H.264 High Profile 10-bit
    "avc1.640020": "H.264",              # H.264 High 4:2:2 Profile
    "avc1.640021": "H.264",              # H.264 High 4:4:4 Profile
    "avc1.4D4020": "H.264",              # H.264 Main 10 Profile
    "avc1.4D4032": "H.264",              # H.264 High 10 Intra Profile
    "avc1.4D4040": "H.264",              # H.264 High 4:2:2 10 Profile
    "avc1.640028": "H.264",              # H.264 High 4:4:4 10 Profile
    "avc1.640029": "H.264",              # H.264 High 4:4:4 16-bit
    "avc1.64002A": "H.264",              # H.264 High 4:2:0 10 Profile
    "avc1.64002B": "H.264",              # H.264 High 4:2:2 10 Profile
    "avc1.64002C": "H.264",              # H.264 High 4:4:4 10 Profile
    "avc1.64002D": "H.264",              # H.264 High 4:2:0 12 Profile
    "avc1.64002E": "H.264",              # H.264 High 4:2:2 12 Profile
    "avc1.64002F": "H.264",              # H.264 High 4:4:4 12 Profile
    "avc1.640030": "H.264",              # H.264 High 4:2:0 16 Profile
    "avc1.640031": "H.264",              # H.264 High 4:2:2 16 Profile
    "avc1.640032": "H.264",              # H.264 High 4:4:4 16 Profile
    "avc1.640033": "H.264",              # H.264 High 4:2:0 12 10 Profile
    "avc1.640034": "H.264",              # H.264 High 4:2:2 12 10 Profile
    "avc1.640035": "H.264",              # H.264 High 4:4:4 12 10 Profile
    "avc1.640036": "H.264",              # H.264 High 4:2:0 16 10 Profile
    "avc1.640037": "H.264",              # H.264 High 4:2:2 16 10 Profile
    "avc1.640038": "H.264",              # H.264 High 4:4:4 16 10 Profile
    "avc1.640039": "H.264",              # H.264 High 4:2:0 16 12 Profile
    "avc1.64003A": "H.264",              # H.264 High 4:2:2 16 12 Profile
    "avc1.64003B": "H.264",              # H.264 High 4:4:4 16 12 Profile
    "avc1.64003C": "H .264",              # H.264 High 4:2:0 16 14 Profile
    "avc1.64003D": "H.264",              # H.264 High 4:2:2 16 14 Profile
    "avc1.64003E": "H.264",              # H.264 High 4:4:4 16 14 Profile
    "avc1.4D4015": "H.264",              # H.264 Main Profile 4:2:0
    "avc1.4D4016": "H.264",              # H.264 Main Profile 4:2:2
    "avc1.4D4017": "H.264",              # H.264 Main Profile 4:4:4
    "avc1.4D4018": "H.264",              # H.264 Main Profile 4:2:0 10-bit
    "avc1.4D4019": "H.264",              # H.264 Main Profile 4:2:2 10-bit
    "avc1.4D401A": "H.264",              # H.264 Main Profile 4:4:4 10-bit
    "avc1.4D401B": "H.264",              # H.264 Main Profile 4:2:0 12-bit
    "avc1.4D401C": "H.264",              # H.264 Main Profile 4:2:2 12-bit
    "avc1.4D401D": "H.264",              # H.264 Main Profile 4:4:4 12-bit
    "hevc.1": "H.265",                   # H.265 Main Profile
    "hevc.2": "H.265",                   # H.265 Main 10 Profile
    "hevc.3": "H.265",                   # H.265 Main Still Picture Profile
    "hevc.4": "H.265",                   # H.265 Range Extensions Profile
    "hevc.5": "H.265",                   # 4:2:0 H.265 4:2:0 Profile
    "hevc.6": "H.265",                   # 4:2:2 H.265 4:2:2 Profile
    "hevc.7": "H.265",                   # 4:4:4 H.265 4:4:4 Profile
    "hevc.8": "H.265",                   # 4:2:0 10 H.265 4:2:0 10 Profile
    "hevc.9": "H.265",                   # 4:2:2 10 H.265 4:2:2 10 Profile
    "hevc.10": "H.265",                  # 4:4:4 10 H.265 4:4:4 10 Profile
    "hevc.11": "H.265",                  # 4:2:0 12 H.265 4:2:0 12 Profile
    "hevc.12": "H.265",                  # 4:2:2 12 H.265 4:2:2 12 Profile
    "hevc.13": "H.265",                  # 4:4:4 12 H.265 4:4:4 12 Profile
    "hevc.14": "H.265",                  # Main 12 H.265 Main 12 Profile
    "hevc.15": "H.265",                  # Main 10 Intra H.265 Main 10 Intra Profile
    "hevc.16": "H.265",                  # Main 12 Intra H.265 Main 12 Intra Profile
    "vp8": "VP8",                        # VP8
    "vp9": "VP9",                        # VP9
    "vp10": "VP10",                      # VP10
    "mpeg4": "MPEG-4",                  # MPEG-4
    "mp4v": "MPEG-4",                    # MPEG-4
    "mpeg2": "MPEG-2",                  # MPEG-2
    "mpeg1": "MPEG-1",                  # MPEG-1
    "wmv1": "WMV",                       # WMV
    "wmv2": "WMV",                       # WMV
    "wmv3": "WMV",                       # WM "wmv": "WMV",                       # WMV
    "vc1": "VC-1",                       # VC-1
    "dv": "DV",                          # DV
    "dvc": "DV",                         # DV
    "dvcpro": "DVCPRO",                  # DVCPRO
    "dvcprohd": "DVCPRO HD",             # DVCPRO HD
    "prores": "ProRes",                  # ProRes
    "prores_4444": "ProRes",             # 4444 ProRes 4444
    "prores_422": "ProRes",              # 422 ProRes 422
    "prores_422hq": "ProRes",            # 422 HQ ProRes 422 HQ
    "prores_422lt": "ProRes",            # 422 LT ProRes 422 LT
    "prores_422proxy": "ProRes",         # 422 Proxy ProRes 422 Proxy
    "jpeg": "JPEG",                      # JPEG
    "png": "PNG",                        # PNG
    "gif": "GIF",                        # GIF
    "h263": "H.263",                     # H.263
    "h261": "H.261",                     # H.261
    "rawvideo": "RAW",                   # RAW
    "yuv420p": "YUV",                    # YUV 420
    "yuv422p": "YUV",                    # YUV 422
    "yuv444p": "YUV",                    # YUV 444
    "yuvj420p": "YUVJ",                  # YUVJ 420
    "yuvj422p": "YUVJ",                  # YUVJ 422
    "yuvj444p": "YUVJ",                  # YUVJ 444
    "huffYUV": "HuffYUV",                # HuffYUV
    "ffv1": "FFV1",                      # FFV1
    "vp6": "VP6",                        # VP6
    "vp7": "VP7",                        # VP7
    "vp8_alpha": "VP8 Alpha",            # VP8 Alpha
    "vp9_alpha": "VP9 Alpha",            # VP9 Alpha
    "av1": "AV1",                        # AV1
    "av2": "AV2",                        # AV2
    "av3": "AV3",                        # AV3
    "av4": "AV4",                        # AV4
    "av5": "AV5",                        # AV5
    "av6": "AV6",                        # AV6
    "av7": "AV7",                        # AV7
    "av8": "AV8",                        # AV8
    "av9": "AV9",                        # AV9
    "av10": "AV10",                      # AV10
    "av11": "AV11",                      # AV11
    "av12": "AV12",                      # AV12
    "av13": "AV13",                      # AV13
    "av14": "AV14",                      # AV14
    "av15": "AV15",                      # AV15
    "av16": "AV16",                      # AV16
    "av17": "AV17",                      # AV17
    "av18": "AV18",                      # AV18
    "av19": "AV19",                      # AV19
    "av20": "AV20",                      # AV20
    "av21": "AV21",                      # AV21
    "av22": "AV22",                      # AV22
    "av23": "AV23",                      # AV23
    "av24": "AV24",                      # AV24
    "av25": "AV25",                      # AV25
    "av26": "AV26",                      # AV26
    "av27": "AV27",                      # AV27
    "av28": "AV28",                      # AV28
    "av29": "AV29",                      # AV29
    "av30": "AV30",                      # AV30
    "av31": "AV31",                      # AV31
    "av32": "AV32",                      # AV32
    "av33": "AV33",                      # AV33
    "av34": "AV34",                      # AV34
    "av35": "AV35",                      # AV35
    "av36": "AV36",                      # AV36
    "av37": "AV37",                      # AV37
    "av38": "AV38",                      # AV38
    "av39": "AV39",                      # AV39
    "av40": "AV40",                      # AV40
    "av41": "AV41",                      # AV41
    "av42": "AV42",                      # AV42
    "av43": "AV43",                      # AV43
    "av44": "AV44",                      # AV44
    "av45": "AV45",                      # AV45
    "av46": "AV46",                      # AV46
    "av47": "AV47",                      # AV47
    "av48": "AV48",                      # AV48
    "av49": "AV49",                      # AV49
    "av50": "AV50",                      # AV50
    "av51": "AV51",                      # AV51
    "av52": "AV52",                      # AV52
    "av53": "AV53",                      # AV53
    "av54": "AV54",                      # AV54
    "av55": "AV55",                      # AV55
    "av56": "AV56",                      # AV56
    "av57": "AV57",                      # AV57
    "av58": "AV58",                      # AV58
    "av59": "AV59",                      # AV59
    "av60": "AV60",                      # AV60
    "av61": "AV61",                      # AV61
    "av62": "AV62",                      # AV62
    "av63": "AV63",                      # AV63
    "av64": "AV64",                      # AV64
    "av65": "AV65",                      # AV65
    "av66": "AV66",                      # AV66
    "av67": "AV67",                      # AV67
    "av68": "AV68",                      # AV68
    "av69": "AV69",                      # AV69
    "av70": "AV70",                      # AV70
    "av71": "AV71",                      # AV71
    "av72": "AV72",                      # AV72
    "av73": "AV73",                      # AV73
    "av74": "AV74",                      # AV74
    "av75": "AV75",                      # AV75
    "av76": "AV76",                      # AV76
    "av77": "AV77",                      # AV77
    "av78": "AV78",                      # AV78
    "av79": "AV79",                      # AV79
    "av80": "AV80",                      # AV80
    "av81": "AV81",                      # AV81
    "av82": "AV82",                      # AV82
    "av83": "AV83",                      # AV83
    "av84": "AV84",                      # AV84
    "av85": "AV85",                      # AV85
    "av86": "AV86",                      # AV86
    "av87": "AV87",                      # AV87
    "av88": "AV88",                      # AV88
    "av89": "AV89",                      # AV89
    "av90": "AV90",                      # AV90
    "av91": "AV91",                      # AV91
    "av92": "AV92",                      # AV92
    "av93": "AV93",                      # AV93
    "av94": "AV94",                      # AV94
    "av95": "AV95",                      # AV95
    "av96": "AV96",                      # AV96
    "av97": "AV97",                      # AV97
    "av98": "AV98",                      # AV98
    "av99": "AV99",                      # AV99
    "av100": "AV100"                     # AV100
}


vcodec_mapping = {
    "avc1.42E01E": "avc1",              # H.264 Baseline Profile
    "avc1.42E01F": "avc1",              # H.264 Baseline Profile 10-bit
    "avc1.4D401E": "avc1",              # H.264 Main Profile
    "avc1.4D401F": "avc1",              # H.264 Main Profile 10-bit
    "avc1.64001E": "avc1",              # H.264 High Profile
    "avc1.64001F": "avc1",              # H.264 High Profile 10-bit
    "avc1.640020": "avc1",              # H.264 High 4:2:2 Profile
    "avc1.640021": "avc1",              # H.264 High 4:4:4 Profile
    "avc1.4D4020": "avc1",              # H.264 Main 10 Profile
    "avc1.4D4032": "avc1",              # H.264 High 10 Intra Profile
    "avc1.4D4040": "avc1",              # H.264 High 4:2:2 10 Profile
    "avc1.640028": "avc1",              # H.264 High 4:4:4 10 Profile
    "avc1.640029": "avc1",              # H.264 High 4:4:4 16-bit
    "avc1.64002A": "avc1",              # H.264 High 4:2:0 10 Profile
    "avc1.64002B": "avc1",              # H.264 High 4:2:2 10 Profile
    "avc1.64002C": "avc1",              # H.264 High 4:4:4 10 Profile
    "avc1.64002D": "avc1",              # H.264 High 4:2:0 12 Profile
    "avc1.64002E": "avc1",              # H.264 High 4:2:2 12 Profile
    "avc1.64002F": "avc1",              # H.264 High 4:4:4 12 Profile
    "avc1.640030": "avc1",              # H.264 High 4:2:0 16 Profile
    "avc1.640031": "avc1",              # H.264 High 4:2:2 16 Profile
    "avc1.640032": "avc1",              # H.264 High 4:4:4 16 Profile
    "avc1.640033": "avc1",              # H.264 High 4:2:0 12 10 Profile
    "avc1.640034": "avc1",              # H.264 High 4:2:2 12 10 Profile
    "avc1.640035": "avc1",              # H.264 High 4:4:4 12 10 Profile
    "avc1.640036": "avc1",              # H.264 High 4:2:0 16 10 Profile
    "avc1.640037": "avc1",              # H.264 High 4:2:2 16 10 Profile
    "avc1.640038": "avc1",              # H.264 High 4:4:4 16 10 Profile
    "avc1.640039": "avc1",              # H.264 High 4:2:0 16 12 Profile
    "avc1.64003A": "avc1",              # H.264 High 4:2:2 16 12 Profile
    "avc1.64003B": "avc1",              # H.264 High 4:4:4 16 12 Profile
    "avc1.64003C": "avc1",              # H.264 High 4:2:0 16 14 Profile
    "avc1.64003D": "avc1",              # H.264 High 4:2:2 16 14 Profile
    "avc1.64003E": "avc1",              # H.264 High 4:4:4 16 14 Profile
    "avc1.4D4015": "avc1",              # H.264 Main Profile 4:2:0
    "avc1.4D4016": "avc1",              # H.264 Main Profile 4:2:2
    "avc1.4D4017": "avc1",              # H.264 Main Profile 4:4:4
    "avc1.4D4018": "avc1",              # H.264 Main Profile 4:2:0 10-bit
    "avc1.4D4019": "avc1",              # H.264 Main Profile 4:2:2 10-bit
    "avc1.4D401A": "avc1",              # H.264 Main Profile 4:4:4 10-bit
    "avc1.4D401B": "avc1",              # H.264 Main Profile 4:2:0 12-bit
    "avc1.4D401C": "avc1",              # H.264 Main Profile 4:2:2 12-bit
    "avc1.4D401D": "avc1",              # H.264 Main Profile 4:4:4 12-bit
    "hevc.1": "HEVC Main",                 # HEVC Main Profile
    "hevc.2": "HEVC Main 10",              # HEVC Main 10 Profile
    "hevc.3": "HEVC Main Still Picture",    # HEVC Main Still Picture Profile
    "hevc.4": "HEVC Range Extensions",      # HEVC Range Extensions Profile
    "hevc.5": "HEVC",  # 4:2:0 HEVC 4:2:0 Profile
    "hevc.6": "HEVC",   #4:2:2 HEVC 4:2:2 Profile
    "hevc.7": "HEVC",   #4:4:4 HEVC 4:4:4 Profile
    "hevc.8": "HEVC",   #4:2:0 10 HEVC 4:2:0 10 Profile
    "hevc.9": "HEVC",   #4:2:2 10 HEVC 4:2:2 10 Profile
    "hevc.10": "HEVC",   #4:4:4 10 HEVC 4:4:4 10 Profile
    "hevc.11": "HEVC",   #4:2:0 12 HEVC 4:2:0 12 Profile
    "hevc.12": "HEVC",   #4:2:2 12 HEVC 4:2:2 12 Profile
    "hevc.13": "HEVC",   #4:4:4 12 HEVC 4:4:4 12 Profile
    "hevc.14": "HEVC",   #Main 12 HEVC Main 12 Profile
    "hevc.15": "HEVC",   #Main 10 Intra HEVC Main 10 Intra Profile
    "hevc.16": "HEVC",   #Main 12 Intra HEVC Main 12 Intra Profile
    "vp8": "VP8",            # VP8
    "vp9": "VP9",            # VP9
    "vp10": "VP10",          # VP10
    "mpeg4": "MPEG-4",      # MPEG-4
    "mp4v": "MPEG-4",        # MPEG-4
    "mpeg2": "MPEG-2",      # MPEG-2
    "mpeg1": "MPEG-1",      # MPEG-1
    "wmv1": "WMV",           # WMV
    "wmv2": "WMV",           # WMV
    "wmv3": "WMV",           # WMV
    "vc1": "VC-1",           # VC-1
    "dv": "DV",              # DV
    "dvc": "DV",             # DV
    "dvcpro": "DVCPRO",      # DVCPRO
    "dvcprohd": "DVCPRO HD", # DVCPRO HD
    "prores": "ProRes",      # ProRes
    "prores_4444": "ProRes ", # 4444 ProRes 4444
    "prores_422": "ProRes ", # 422 ProRes 422
    "prores_422hq": "ProRes ", # 422 HQ ProRes 422 HQ
    "prores_422lt": "ProRes ", # 422 LT ProRes 422 LT
    "prores_422proxy": "ProRes",  # 422 Proxy ProRes 422 Proxy
    "jpeg": "JPEG",          # JPEG
    "png": "PNG",            # PNG
    "gif": "GIF",            # GIF
    "h263": "H.263",         # H.263
    "h261": "H.261",         # H.261
    "rawvideo": "RAW",       # RAW
    "yuv420p": "YUV",    # YUV 420
    "yuv422p": "YUV",    # YUV 422
    "yuv444p": "YUV ",    # YUV 444
    "yuvj420p": "YUVJ",  # YUVJ 420
    "yuvj422p": "YUVJ",  # YUVJ 422
    "yuvj444p": "YUVJ",  # YUVJ 444
    "huffYUV": "HuffYUV",    # HuffYUV
    "ffv1": "FFV1",          # FFV1
    "vp6": "VP6",            # VP6
    "vp7": "VP7",            # VP7
    "vp8_alpha": "VP8 Alpha", # VP8 Alpha
    "vp9_alpha": "VP9 Alpha", # VP9 Alpha
    "av1": "AV1",            # AV1
    "av2": "AV2",            # AV2
    "av3": "AV3",            # AV3
    "av4": "AV4",            # AV4
    "av5": "AV5",            # AV5
    "av6": "AV6",            # AV6
    "av7": "AV7",            # AV7
    "av8": "AV8",            # AV8
    "av9": "AV9",            # AV9
    "av10": "AV10",          # AV10
    "av11": "AV11",          # AV11
    "av12": "AV12",          # AV12
    "av13": "AV13",          # AV13
    "av14": "AV14",          # AV14
    "av15": "AV15",          # AV15
    "av16": "AV16",          # AV16
    "av17": "AV17",          # AV17
    "av18": "AV18",          # AV18
    "av19": "AV19",          # AV19
    "av20": "AV20",          # AV20
    "av21": "AV21",          # AV21
    "av22": "AV22",          # AV22
    "av23": "AV23",          # AV23
    "av24": "AV24",          # AV24
    "av25": "AV25",          # AV25
    "av26": "AV26",          # AV26
    "av27": "AV27",          # AV27
    "av28": "AV28",          # AV28
    "av29": "AV29",          # AV29
    "av30": "AV30",          # AV30
    "av31": "AV31",          # AV31
    "av32": "AV32",          # AV32
    "av33": "AV33",          # AV33
    "av34": "AV34",          # AV34
    "av35": "AV35",          # AV35
    "av36": "AV36",          # AV36
    "av37": "AV37",          # AV37
    "av38": "AV38",          # AV38
    "av39": "AV39",          # AV39
    "av40": "AV40",          # AV40
    "av41": "AV41",          # AV41
    "av42": "AV42",          # AV42
    "av43": "AV43",          # AV43
    "av44": "AV44",          # AV44
    "av45": "AV45",          # AV45
    "av46": "AV46",          # AV46
    "av47": "AV47",          # AV47
    "av48": "AV48",          # AV48
    "av49": "AV49",          # AV49
    "av50": "AV50",          # AV50
    "av51": "AV51",          # AV51
    "av52": "AV52",          # AV52
    "av53": "AV53",          # AV53
    "av54": "AV54",          # AV54
    "av55": "AV55",          # AV55
    "av56": "AV56",          # AV56
    "av57": "AV57",          # AV57
    "av58": "AV58",          # AV58
    "av59": "AV59",          # AV59
    "av60": "AV60",          # AV60
    "av61": "AV61",          # AV61
    "av62": "AV62",          # AV62
    "av63": "AV63",          # AV63
    "av64": "AV64",          # AV64
    "av65": "AV65",          # AV65
    "av66": "AV66",          # AV66
    "av67": "AV67",          # AV67
    "av68": "AV68",          # AV68
    "av69": "AV69",          # AV69
    "av70": "AV70",          # AV70
    "av71": "AV71",          # AV71
    "av72": "AV72",          # AV72
    "av73": "AV73",          # AV73
    "av73": "AV73",          # AV73
    "av74": "AV74",          # AV74
    "av75": "AV75",          # AV75
    "av76": "AV76",          # AV76
    "av77": "AV77",          # AV77
    "av78": "AV78",          # AV78
    "av79": "AV79",          # AV79
    "av80": "AV80",          # AV80
    "av81": "AV81",          # AV81
    "av82": "AV82",          # AV82
    "av83": "AV83",          # AV83
    "av84": "AV84",          # AV84
    "av85": "AV85",          # AV85
    "av86": "AV86",          # AV86
    "av87": "AV87",          # AV87
    "av88": "AV88",          # AV88
    "av89": "AV89",          # AV89
    "av90": "AV90",          # AV90
    "av91": "AV91",          # AV91
    "av92": "AV92",          # AV92
    "av93": "AV93",          # AV93
    "av94": "AV94",          # AV94
    "av95": "AV95",          # AV95
    "av96": "AV96",          # AV96
    "av97": "AV97",          # AV97
    "av98": "AV98",          # AV98
    "av99": "AV99",          # AV99
    "av100": "AV100"         # AV100
}

# Function to extract video codecs
def get_vcodecs(video_formats):
    """Extract video codecs from the provided video formats."""
    return [vcodec_mapping.get(fmt.get('vcodec', 'Unknown'), 'Unknown') for fmt in video_formats]

# Function to create inline buttons
def create_inline_buttons(options, callback_prefix):
    buttons = [InlineKeyboardButton(text=option, callback_data=f"{callback_prefix}_{idx}") for idx, option in enumerate(options)]
    return InlineKeyboardMarkup([buttons])

# Function to create selection buttons with selection feedback
def create_selection_buttons(options, callback_prefix, selected_indices):
    buttons = []
    for idx, option in enumerate(options):
        button_text = f"✅ {option}" if idx in selected_indices else option
        buttons.append(InlineKeyboardButton(text=button_text, callback_data=f"{callback_prefix}_{idx}"))
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(rows)

def ensure_output_directory():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

# Progress hook for download status
def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Downloading: {d['filename']} | {d['_percent_str']} | {d['_eta_str']} remaining")
    elif d['status'] == 'finished':
        print(f"Done downloading: {d['filename']} | Total size: {d['total_bytes_str']}")

# Fetch Widevine keys using PSSH
async def fetch_widevine_keys(pssh_kid_map, content_playback, playback_data, callback_query):
    # (Include the entire function code here)
    got_cert = False
    cert_data = None
    pssh_cache = config.get("psshCacheStore")

    # Get Keys for all KIDs of PSSH
    for pssh in pssh_kid_map.keys():
        print(f'[*] PSSH: {pssh}')

        # Need to fetch even if one key missing
        fetch_keys = False
        if pssh in pssh_cache:
            for kid in pssh_cache[pssh].keys():
                if kid not in pssh_kid_map[pssh]:
                    fetch_keys = True
                    break
        else:
            fetch_keys = True

        if fetch_keys:
            # Fetch License Certificate of not Present
            if not got_cert:
                print(f'[=>] Get Widevine Server License')
                cert_req = b64decode("CAQ=")
                cert_data = jiocine.getWidevineLicense(playback_data["licenseurl"], cert_req,
                                                       config.get("authToken"), content_playback["playbackId"])
                cert_data = b64encode(cert_data).decode()
                got_cert = True

            print(f'[=>] Perform Widevine Handshake for Keys')

            wv_decrypt = WvDecrypt(devices.device_samsung_sm_g935f, cert_data)

            challenge = wv_decrypt.get_challenge(pssh)

            wv_license = jiocine.getWidevineLicense(playback_data["licenseurl"], challenge,
                                                    config.get("authToken"), content_playback["playbackId"])

            wv_decrypt.update_license(wv_license)

            # Add keys to the map
            pssh_cache[pssh] = wv_decrypt.get_keys()

            # Flush to new Cache
            config.set("psshCacheStore", pssh_cache)


def extract_season_id(content_url):
    # Define a regex pattern to match the season ID from the URL
    pattern = r'https?://www\.jiocinema\.com/tv-shows/[^/]+/season/(\d+)'
    
    match = re.search(pattern, content_url)
    if match:
        return match.group(1)  # Return the captured season ID
    else:
        return None  # Return None if no match is found

# Use mp4decrypt to decrypt vod(video on demand) using kid:key
def decrypt_vod_mp4d(kid, key, input_path, output_path):
    # (Include the entire function code here)
    # Create mp4decrypt command
    mp4decPath = realPath(joinPath(scriptsDir, config.get('mp4decPath')))
    command = [mp4decPath, '--key', f"{kid}:{key}", input_path, output_path]
    process = subprocess.Popen(command, stderr=subprocess.PIPE, universal_newlines=True)
    for line in process.stderr:
        print(line)
    process.communicate()

def sanitize_filename(filename):
    # Replace problematic characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*#:]', '_', filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')

def sanitize_folder_name(folder_name):
    # Replace problematic characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*#:]', '_', folder_name)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')

def extract_content_name(url):
    # Define a regex pattern to match the content name for various types
    pattern = r'https?://www\.jiocinema\.com/(?:tv-shows|movies|promos|series|episodes|shows)/([^/]+)/(?:\d+/([^/]+)/)?\d+'
    
    match = re.search(pattern, url)
    if match:
        # Return the captured group which is the main content name, replacing hyphens with spaces
        return match.group(1).replace('-', ' ')  # Replace hyphens with spaces
    else:
        return None  # Return None if no match is found

# Start command
@app.on_message(filters.command("start") & (filters.private | filters.group))
@sudo_only
async def start_command(client, message):
    await message.reply_text("Welcome to Jio Cinema Downloader Bot! Please enter the content URL:")

# Dictionary to store content details for multiple links
content_data_dict = {}

# Initialize content_data to avoid UnboundLocalError
content_data = None  # Initialize content_data at the start

@app.on_message(filters.command("jcdl") & (filters.private | filters.group))
@sudo_only
async def jcdl_command(client, message):
    command_parts = message.text.split(maxsplit=1)  # Split the command and the URL
    if len(command_parts) < 2:
        await message.reply_text("Please provide a content URL after the command.")
        return

    content_url = command_parts[1].strip()  # Get the URL part

    # Check if the user wants to download the whole season
    if content_url.endswith("-all"):
        content_url = content_url[:-4].strip()  # Remove the '-all' flag
        await download_whole_season(client, message, content_url)
    else:
        await handle_url(client, message, content_url)

# Handle incoming messages (for URL)
async def handle_url(client, message, content_url):
    global content_data, content_data_dict, is_processing_link, content_name

    chat_id = message.chat.id  # Get the chat ID

    if is_processing_link or processing_states.get(chat_id, False):
        await message.reply_text("Only one link can be processed at a time. Please wait until the current process is finished.")
        return

    # Set the processing state to True
    is_processing_link = False
    processing_states[chat_id] = False

    print(f"Received URL: {content_url} from {message.from_user.id}")  # Debugging line

    # Validate URL
    urlRegex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if re.match(urlRegex, content_url) is None:
        await message.reply_text("Please provide a valid URL!")
        is_processing_link = False  # Reset the processing state
        processing_states[chat_id] = False
        return

    # Extract content ID from URL
    content_url_parts = content_url.split('/')
    try:
        content_id = content_url_parts[-1]
        int(content_id)  # Validate content ID
    except ValueError:
        await message.reply_text("Please provide a valid URL!")
        is_processing_link = False  # Reset the processing state
        processing_states[chat_id] = False
        return

    # Continue with your existing logic to fetch content details, etc.
    # Ensure content_data is initialized before using it
    if content_data is None:
        content_data = {}  # Initialize content_data if it's None

    content_data_dict[content_id] = content_data

    # Extract content name from the URL if needed
    content_name = extract_content_name(content_url)  # Use the function to extract content name

    # Capitalize the first letter of each word in content_name
    if content_name:
        content_name = content_name.title()  # Capitalize first letter of each word

    # Fetch content details
    fct_message = await message.reply_text("Fetching content details...")
    content_data = jiocine.getContentDetails(content_id)
    if not content_data:
        await message.reply_text("Content details not found!")
        is_processing_link = False  # Reset the processing state
        return
    await fct_message.delete()
    # Store the fetched content_data in the dictionary
    content_data_dict[content_id] = content_data  # Store the fetched data

    if content_data['isPremium'] and not config.get("hasPremium"):
        print("[!] Need Premium Account for this Content")
        await message.reply_text("[!] Need Premium Account for this Content")
        is_processing_link = False  # Reset the processing state
        # After the download is complete or if an error occurs
        processing_states[chat_id] = False  # Reset the processing state
        return

    # Define flags for content types after fetching content details
    is_movie = content_data['mediaType'] == "MOVIE"
    is_tv_show = content_data['mediaType'] == "TV_SHOW"
    is_series = content_data['mediaType'] == "SERIES"
    is_episode = content_data['mediaType'] == "EPISODE"

    # Construct the details message based on content type
    if is_movie:
        details_message = (
            f"[*] Content Id: {content_data['id']}\n"
            f"[*] {content_data['mediaType'].title()} Name: {content_name.title()}\n"
            f"[*] Type: {content_data['mediaType'].title()}\n"
            f"[*] Default Language: {content_data['defaultLanguage'].title()}\n"
            f"[*] Release Year: {content_data['releaseYear']}\n"
        )
    else:
        details_message = (
            f"[*] Content Id: {content_data['id']}\n"
            f"[*] {content_data['mediaType'].title()} Title: {content_name.title()}\n"
            f"[*] {content_data['mediaType'].title()} Name: {content_data['shortTitle'].title()}\n"
            f"[*] Type: {content_data['mediaType'].title()}\n"
            f"[*] Default Language: {content_data['defaultLanguage'].title()}\n"
            f"[*] Release Year: {content_data['releaseYear']}\n"
        )

    await message.reply_text(details_message, reply_markup=create_inline_buttons(["Yes", "No"], f"confirm_content_{content_id}"))

    # Reset the processing state after handling the link
    is_processing_link = False  # Reset the processing state after the operation is complete

def create_inline_buttons(buttons, callback_prefix):
    inline_buttons = []
    for button in buttons:
        # Create a unique callback data for each button
        callback_data = f"{callback_prefix}_{button.lower()}"  # Use lower case for consistency
        inline_buttons.append(
            [InlineKeyboardButton(button, callback_data=callback_data)]
        )
    return InlineKeyboardMarkup(inline_buttons)

# Handle content confirmation
@app.on_callback_query(filters.regex(r"^confirm_content_(\d+)_(yes|no)$"))
async def handle_content_confirmation(client, callback_query):
    await callback_query.answer()  # Acknowledge the callback query

    content_id, response = callback_query.data.split("_")[-2:]  # Extract content_id and response

    # Check if the content_id exists in the content_data_dict
    if content_id in content_data_dict:
        content_data = content_data_dict[content_id]  # Retrieve the content data using content_id
        print(f"Retrieved content_data: {content_data}")  # Debugging statement

        if response == "yes":  # User confirmed
            if 'id' in content_data:  # Check if 'id' exists in content_data
                pwd_message = await callback_query.message.reply_text("Proceeding with the download...")
                await download_playback(content_data['id'], content_data, callback_query)  # Pass callback_query here
                await pwd_message.delete()
                # Delete the confirmation message
                await callback_query.message.delete()  # Delete the confirmation message
            else:
                await callback_query.message.reply_text("Content ID not found in content data.")
        else:  # User declined
            await callback_query.message.reply_text("Download canceled. You can start again by sending /start.")
            await callback_query.message.delete()  # Delete the confirmation message
    else:
        await callback_query.message.reply_text("Content not found. Please try again.")



async def download_vod_ytdlp(url, content, callback_query, has_drm=False, rid_map=None):
    global default_res, audio_formats, video_formats, output_dir_name, output_dir, temp_dir, ydl_headers, processed_abrs # Declare as global at the beginning of the function

    is_processing_link = False  # Reset the processing state after the operation is complete

    # Ensure default_res is an integer
    if isinstance(default_res, str):
        try:
            default_res = int(default_res)
        except ValueError:
            default_res = -1  # Default to -1 if conversion fails

    # Conversion Map for Type to Sub Folder
    sub_dir = jiocine.contentTypeDir[content["mediaType"]]
    output_dir_name = sanitize_folder_name(f"{content['fullTitle']} ({content['releaseYear']})")

    is_series_episode = content["mediaType"] == "EPISODE"
    if is_series_episode:
        output_dir_name = sanitize_folder_name(f'{content["seasonName"]} ({content["releaseYear"]})')

    # Output dir path
    output_dir = config.get('downloadPath').format(sub_dir, output_dir_name)
    output_dir = realPath(joinPath(scriptsDir, output_dir))
    temp_dir = realPath(joinPath(scriptsDir, config.get('tempPath')))

    # Separate out baseUrl and Query
    parsed_url = parse.urlparse(url)
    base_url = url.replace(parsed_url.query, '')[:-1]
    query_head = parsed_url.query.replace("=", ":", 1).split(":")

    # Add more Headers
    ydl_headers = {
        query_head[0]: query_head[1]
    }
    ydl_headers.update(jiocine.headers)

    ydl_opts = {
        'no_warnings': True,
        'nocheckcertificate': True,
        'format': 'bv+ba/b',
        'paths': {
            'home': output_dir,
            'temp': temp_dir
        },
        'outtmpl': {
            'default': f'{output_dir_name}.%(ext)s',
        },
        'http_headers': ydl_headers
    }

    if has_drm:
        ydl_opts['allow_unplayable_formats'] = True



    try:
        content_info = yt_dlp.YoutubeDL(ydl_opts).extract_info(base_url, download=False)
        print("Available formats:")
        for fmt in content_info.get("formats", []):
            print(f"{fmt['format_id']} - {fmt.get('height', 'Unknown')}p")
    except yt_dlp.utils.DownloadError as e:
        await callback_query.message.reply_text(f"[!] Error Fetching Content Info: {e}")
        return
    
    # Extract available formats
    available_formats = content_info.get("formats", [])
    audio_formats = [fmt for fmt in available_formats if fmt.get("acodec") != "none"]
    video_formats = [fmt for fmt in available_formats if fmt.get("vcodec") != "none"]

    # Process the video bitrates
    processed_vbrs.clear()  # Clear previous values if necessary
    processed_vbrs.extend(process_vbrs(video_formats))  # Populate processed_vbrs

    # Process the average bitrates for the audio formats
    processed_abrs = process_abrs(audio_formats)  # Add this line

    # Get audio codecs
    audio_codecs = get_acodecs(audio_formats)  # Call the renamed function

# Print original audio codecs
    print("Original Audio Codecs:")
    for fmt in audio_formats:
        print(fmt['acodec'])

    # Get video codecs
    video_codecs = get_vcodecs(video_formats)

    # Print original video codecs
    print("\nVideo Codecs:")
    for fmt in video_formats:
        print(fmt['vcodec'])

# Create buttons for audio selection with multi-select
    audio_buttons = create_selection_buttons(
        [
            f"{lang_map.get(fmt['language'], fmt['language'])} ({codec_mapping.get(fmt.get('acodec', 'Unknown'), 'Unknown')} - {processed_abrs[i]} kbps)"
            for i, fmt in enumerate(audio_formats)
        ],
        "select_audio",
        user_audio_selection
    )

    await callback_query.message.reply_text("Please select audio tracks:", reply_markup=audio_buttons)

# Handle continue selection for audio
@app.on_callback_query(filters.regex(r"^continue_selection$"))
async def handle_continue_selection(client, callback_query):
    await callback_query.answer()
    
    if user_audio_selection:
        await callback_query.message.reply_text("Audio selection complete. Now select a video track:")
        
        # Create buttons for video selection with single-select
        # Create buttons for video selection with single-select
        video_buttons = create_selection_buttons(
            [
                f"{fmt.get('height', 'Unknown')}p ({vcodec_mapping.get(fmt.get('vcodec', 'Unknown'), 'Unknown')} - {processed_vbrs[i] if i < len(processed_vbrs) else 'N/A'} kbps)"
                for i, fmt in enumerate(video_formats)
            ],
            "select_video",
            user_video_selection
        )

        # Send the video selection buttons to the user
        await callback_query.message.reply_text("Please select a video track:", reply_markup=video_buttons)
    else:
        await callback_query.message.reply_text("Please select at least one audio track before continuing.")

async def wait_for_audio_selection(callback_query, audio_formats, video_buttons):
    global user_audio_selection
    user_audio_selection = set()  # Reset selection

    while True:
        await asyncio.sleep(1)  # Wait for user to make selections
        if "continue_selection" in user_audio_selection:  # Check if continue button is pressed
            break

    await callback_query.message.reply_text("Audio selection complete. Now select a video track:", reply_markup=video_buttons)

    # Wait for user to select video format
    await wait_for_video_selection(callback_query, video_formats)

@app.on_callback_query(filters.regex(r"^confirm_video_selection$"))
async def confirm_video_selection(client, callback_query,):
    
    global content_name, chat_id  # Access the global variable
    await callback_query.answer()

    # Ensure user has made selections
    if not user_video_selection:
        await callback_query.message.reply_text("Please select a video format before confirming.")
        return

    # Get selected audio formats
    selected_audio_indices = list(user_audio_selection)  # Convert to list to access indices
    audio_formats_selected = [audio_formats[i] for i in selected_audio_indices]  # Get the selected audio formats

    # Get selected video format
    selected_video_index = next(iter(user_video_selection))
    video_format = video_formats[selected_video_index]

    # Print selected formats and URL
    print(f"Selected Audio Formats: {[fmt['format_id'] for fmt in audio_formats_selected]}")
    print(f"Selected Video Format: {video_format['format_id']}")
    print(f"Starting download for URL: {playback_url}")  # Use the stored playback_url

    # Construct the caption based on the specified nomenclature
    resolution = video_format.get('height', 'Unknown')  # Get the resolution
    vid_codec = vcodec_mapping.get(video_format.get('vcodec', 'Unknown'), 'Unknown')  # Get the video codec
    cvid_codec = cvcodec_mapping.get(video_format.get('vcodec', 'Unknown'), 'Unknown')  # Get the video codec
    extension = "mp4"

    # Ensure content_title and release_year are defined
    content_title = content_data['shortTitle']  # Get the title from content data
    release_year = content_data['releaseYear']  # Get the release year
    selected_vbr = int(video_format.get('bitrate', video_format.get('vbr', 0)))  # Get the bitrate or vbr, default to 0

    # Create a dictionary to group audio formats by bitrate and codec
    audio_info_dict = {}
    for fmt in audio_formats_selected:
        lang = lang_map.get(fmt['language'], fmt['language'])
        bitrate = int(fmt.get('abr', 0))  # Convert to int to remove decimal
        codec = cacodec_mapping.get(fmt.get('acodec', 'Unknown'), 'Unknown')
        key = (bitrate, codec)

        if key not in audio_info_dict:
            audio_info_dict[key] = []
        audio_info_dict[key].append(lang)

    # Construct the selected audio information string
    selected_audio_info = '-'.join(
        f"{'-'.join(langs)}-{bitrate}kbps-{codec}"
        for (bitrate, codec), langs in audio_info_dict.items()
    )

    if content_data['mediaType'] == "MOVIE":
        precaption = f"<code>{content_title}.{release_year}.{selected_audio_info}.{resolution}p.{selected_vbr}.kbps.JC.WEB-DL.{cvid_codec}.{credits}.{extension}</code>"
    else:
        precaption = f"<code>{content_name}.{release_year}.{content_title}.{selected_audio_info}.{resolution}p.{selected_vbr}kbps.JC.WEB-DL.{cvid_codec}.{credits}.{extension}</code>"

    print(f"PreCaption constructed: {precaption}")  # Debugging statement

    # Send the initial download message and store the message object
    download_message = await callback_query.message.reply_text(f"[+] Downloading ...... \nFilename: {precaption}")

    user_audio_selection.clear()  # Reset audio track selection
    user_video_selection.clear()  # Reset video track selection

    # After confirming the selection and before starting the download
    is_processing_link = False  # Set to True when starting the download
    processing_states[callback_query.message.chat.id] = False  # Set for the current chat

    # Proceed with downloading the selected formats, including the download_message and precaption
    await download_selected_formats(playback_url, audio_formats_selected, video_format, callback_query, download_message, precaption)

async def download_selected_formats(playback_url, audio_formats_selected, video_format, callback_query, download_message, precaption):
    # Your existing code...
    global output_dir_name, output_dir
    user_audio_selection.clear()  # Reset audio track selection
    user_video_selection.clear()  # Reset video track selection

    is_processing_link = False  # Reset the processing state after the operation is complete

    # Create a unique filename based on content details
    content_title = content_data['shortTitle']  # Get the title from content data
    release_year = content_data['releaseYear']  # Get the release year
    episode_number = content_data.get('episodeNumber', None)  # Get episode number if available
    specific_video_name = f"{content_title}{f'_{episode_number}' if episode_number else ''}_{video_format['format_id']}"  # Create a specific name
    sanitized_video_name = sanitize_filename(specific_video_name)  # Sanitize the name
    content_name = content_data.get('fullTitle', content_title)  # Extract content name

    # Create a unique output directory
    output_dir = os.path.join(config.get('downloadPath'), sanitized_video_name)
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

    # Prepare the path for the muxed file
    muxed_file_path = os.path.join(output_dir, f"{sanitized_video_name.replace(' ', '_')}.muxed.mp4")
    thumbnail_path = os.path.join(output_dir, f"{sanitized_video_name.replace(' ', '_')}.jpg")  # Path for thumbnail

    # Set up the download options for the selected video format
    output_name = f"{sanitized_video_name}.%(ext)s"
    
    # Set up the download options for video using aria2c
    video_ydl_opts = {
        'format': video_format['format_id'],
        'outtmpl': os.path.join(output_dir, output_name),
        'http_headers': ydl_headers,
        'external_downloader': 'aria2c',  # Use aria2c as the external downloader
        'geo_bypass': True,  # Enable geo-bypass
        'external_downloader_args': [
            'aria2c:--retry-wait=1',
            '--max-file-not-found=10',
            '--max-tries=3',
            '-j', '500',
            '-x', '2'
        ],

        'add_header': ['range:bytes=0-'],  # Add header to requests
        'file_access_retries': 10,  # Retry accessing file 10 times
        'fragment_retries': 20,  # Retry individual fragments 20 times
        'concurrent_fragments': 5,  # Number of fragments downloaded concurrently
        'allow_unplayable_formats': True,  # Allow unplayable formats to be downloaded
    }


    # Retry logic for video download
    retry_attempts = 3  # Number of retry attempts
    for attempt in range(retry_attempts):
        try:
            await asyncio.to_thread(yt_dlp.YoutubeDL(video_ydl_opts).download, [playback_url])
            break  # Exit the retry loop if download is successful
        except yt_dlp.utils.DownloadError as e:
            print(f"[!] Video download failed on attempt {attempt + 1}: {e}")
            if attempt < retry_attempts - 1:
                await asyncio.sleep(2)  # Wait before retrying
            else:
                await callback_query.message.reply_text("[!] Video download failed after multiple attempts.")

    # Prepare paths for muxing
    video_file_path = os.path.join(output_dir, output_name.replace('%(ext)s', 'mp4'))  # Adjust based on your output format
    audio_file_paths = []

    # Download each selected audio format
    for audio_format in audio_formats_selected:
        # Define the audio file name using the same unique naming convention
        audio_file_name = f"{sanitize_filename(audio_format['format_id'])}.m4a"
        audio_file_path = os.path.join(output_dir, audio_file_name)  # Create the full path for the audio file

        audio_ydl_opts = {
            'format': audio_format['format_id'],
            'outtmpl': audio_file_path,  # Ensure audio is saved in the specified directory
            'http_headers': ydl_headers,
            'external_downloader': 'aria2c',  # Use aria2c as the external downloader
            'geo_bypass': True,  # Enable geo-bypass
            'external_downloader_args': [
                'aria2c:--retry-wait=1',
                '--max-file-not-found=10',
                '--max-tries=3',
                '-j', '500',
                '-x', '2'
            ],
            'add_header': ['range:bytes=0-'],  # Add header to requests
            'file_access_retries': 10,  # Retry accessing file 10 times
            'fragment_retries': 20,  # Retry individual fragments 20 times
            'concurrent_fragments': 5,  # Number of fragments downloaded concurrently
            'allow_unplayable_formats': True,  # Allow unplayable formats to be downloaded
        }


        print(f"Downloading audio format: {audio_format['format_id']}")  # Debugging output 
        # Retry logic for audio download
        retry_attempts = 3  # Number of retry attempts
        for attempt in range(retry_attempts):
            try:
                await asyncio.to_thread(yt_dlp.YoutubeDL(audio_ydl_opts).download, [playback_url])
                audio_file_paths.append(audio_file_path)
                print(f"Downloaded audio file: {audio_file_path}")
                break  # Exit the retry loop if download is successful
            except yt_dlp.utils.DownloadError as e:
                print(f"[!] Error downloading audio format {audio_format['format_id']} on attempt {attempt + 1}: {e}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(2)  # Wait before retrying
                else:
                    await callback_query.message.reply_text("[!] Audio download failed after multiple attempts.")
                    if "403" in str(e):
                        print("[*] URL expired, fetching a new URL...")
                        playback_data = await refresh_playback_url(callback_query)  # Function to refresh the URL
                        if playback_data:
                            playback_url = playback_data['url']  # Update the playback URL with the new one
                        else:
                            await callback_query.message.reply_text("[!] Failed to refresh playback URL.")
                            return  # Exit if unable to refresh URL
                    else:
                        await callback_query.message.reply_text("[!] An error occurred while downloading audio.")
                        return  # Exit on other errors

    # Log the decryption process
    # Assuming rid_map is a dictionary where keys are rid and values are pssh_kid
    keys = {rid: pssh_kid for rid, pssh_kid in rid_map.items()} if rid_map else "None"

    # Print the decryption information
    print(f"[+] Decrypting ........................... {precaption} Using Keys: {keys}")
    dcp_message = await callback_query.message.reply_text(f"[+] Decrypting .......\n {precaption} \n\nUsing Keys: {keys}")
    await dcp_message.delete()

    # Edit the download message to indicate that muxing is starting
    muxing_message = await download_message.edit_text(f"[+] Muxing ...... \nFilename: {precaption}")

    # Now mux the video and all audio files together
    await merge_vod_ffmpeg(video_file_path, audio_file_paths, muxed_file_path, download_message, precaption, credits)

    # Check if the muxed file was created successfully
    if not os.path.exists(muxed_file_path):
        await callback_query.message.reply_text("[!] Muxed file was not created successfully.")
        return

    # Extract duration and thumbnail after muxing
    duration = await get_video_duration(muxed_file_path)  # Ensure this is awaited

    # Calculate half of the duration
    half_duration = duration // 2

    # Extract thumbnail at half of the duration
    await extract_thumbnail_at_timestamp(muxed_file_path, thumbnail_path, half_duration)

    # If the muxed file was created successfully, upload it
    if os.path.exists(muxed_file_path):
        uploader = tgUploader(app, callback_query.message, callback_query.message.id, muxing_message)  # Pass muxing_message
        # Example of calling the upload_file method
        await uploader.upload_file(muxed_file_path, precaption, duration, thumbnail_path)  # Ensure this matches the method signature
    else:
        await callback_query.message.reply_text("[!] Muxed file was not created successfully.")

    # Format the duration into a readable format (HH:MM:SS)
    formatted_duration = time.strftime('%H:%M:%S', time.gmtime(duration))
    
    # After muxing is complete
    duration = await get_video_duration(muxed_file_path)

    try:
        # Additional code can be placed here if needed
        pass
    except Exception as e:
        print(f"[!] Failed to upload file: {muxed_file_path}. Error: {e}")

async def refresh_playback_url(callback_query):

    # Log the attempt to refresh the playback URL
    await callback_query.message.reply_text("[*] Refreshing playback URL...")

    # Fetch new playback data using the content ID and auth token
    content_playback = jiocine.fetchPlaybackData(content_data['id'], config.get("authToken"))

    # Check if playback data was successfully retrieved
    if not content_playback:
        await callback_query.message.reply_text("[!] Unable to refresh playback URL. Please try again later.")
        return None

    playback_urls = content_playback.get("playbackUrls", [])
    
    # Check if there are playback URLs available
    if not playback_urls:
        await callback_query.message.reply_text("[!] No playback URLs found in the response.")
        return None

    # Select the first available playback URL (you can implement more logic here if needed)
    new_playback_url = playback_urls[0].get("url")
    
    if not new_playback_url:
        await callback_query.message.reply_text("[!] New playback URL is not available.")
        return None

    # Update the global playback_url variable
    playback_url = new_playback_url
    await callback_query.message.reply_text("[*] Playback URL refreshed successfully.")
    
    return {"url": playback_url}  # Return the new playback URL in a dictionary format



# Handle audio selection
@app.on_callback_query(filters.regex(r"^select_audio_(\d+)$"))
async def handle_audio_selection(client, callback_query):
    global user_audio_selection
    await callback_query.answer()
    selected_audio_index = int(callback_query.data.split("_")[-1])
    
    # Update user selection
    if selected_audio_index in user_audio_selection:
        user_audio_selection.remove(selected_audio_index)  # Deselect if already selected
    else:
        user_audio_selection.add(selected_audio_index)  # Select if not selected

    # Create buttons for audio selection with multi-select
    audio_buttons = create_selection_buttons(
        [
            f"{lang_map.get(fmt['language'], fmt['language'])} ({codec_mapping.get(fmt.get('acodec', 'Unknown'), 'Unknown')} - {processed_abrs[i]} kbps)"
            for i, fmt in enumerate(audio_formats)
        ],
        "select_audio",
        user_audio_selection
    )

    # Add a continue button
    audio_buttons.inline_keyboard.append([InlineKeyboardButton("Continue to Video Selection", callback_data="continue_video_selection")])

    # Update the message with audio buttons
    await callback_query.message.edit_reply_markup(reply_markup=audio_buttons)

# Handle continue to video selection
@app.on_callback_query(filters.regex(r"^continue_video_selection$"))
async def continue_video_selection(client, callback_query):
    await callback_query.answer()

    # Create buttons for video selection with single-select
    video_buttons = create_selection_buttons(
        [
            f"{fmt.get('height', 'Unknown')}p ({vcodec_mapping.get(fmt.get('vcodec', 'Unknown'), 'Unknown')} - {processed_vbrs[i] if i < len(processed_vbrs) else 'N/A'} kbps)"
            for i, fmt in enumerate(video_formats)
        ],
        "select_video",
        user_video_selection
    )

    # Add a continue button for video selection
    video_buttons.inline_keyboard.append([InlineKeyboardButton("Continue", callback_data="confirm_video_selection")])

    # Update the same message with video buttons
    video_selection_message = await callback_query.message.edit_reply_markup(reply_markup=video_buttons)

# Handle video selection
@app.on_callback_query(filters.regex(r"^select_video_(\d+)$"))
async def handle_video_selection(client, callback_query):
    global user_video_selection
    await callback_query.answer()
    
    selected_video_index = int(callback_query.data.split("_")[-1])
    
    # Update user selection
    if selected_video_index in user_video_selection:
        user_video_selection.remove(selected_video_index)  # Deselect if already selected
    else:
        user_video_selection.clear()  # Clear previous selections
        user_video_selection.add(selected_video_index)  # Select if not selected

    # Create buttons for video selection with single-select
    video_buttons = create_selection_buttons(
        [
            f"{fmt.get('height', 'Unknown')}p ({vcodec_mapping.get(fmt.get('vcodec', 'Unknown'), 'Unknown')} - {processed_vbrs[i] if i < len(processed_vbrs) else 'N/A'} kbps)"
            for i, fmt in enumerate(video_formats)
        ],
        "select_video",
        user_video_selection
    )

    # Add a continue button for video selection
    video_buttons.inline_keyboard.append([InlineKeyboardButton("Continue", callback_data="confirm_video_selection")])

    # Update the same message with video buttons
    video_selection_message = await callback_query.message.edit_reply_markup(reply_markup=video_buttons)

# Confirm video selection
@app.on_callback_query(filters.regex(r"^confirm_video_selection$"))
async def confirm_video_selection(client, callback_query):
    await callback_query.answer()  # Acknowledge the callback query

    # Ensure user has made selections
    if not user_video_selection:
        await callback_query.message.reply_text("Please select a video format before confirming.")
        return

    # Get selected audio formats
    selected_audio_indices = list(user_audio_selection)  # Convert to list to access indices
    audio_formats_selected = [audio_formats[i] for i in selected_audio_indices]  # Get the selected audio formats

    # Get selected video format
    selected_video_index = next(iter(user_video_selection))
    video_format = video_formats[selected_video_index]

    # Proceed with downloading the selected formats
    await download_selected_formats(playback_url, audio_formats_selected, video_format, callback_query, download_message, precaption)

async def download_whole_season(client, message, content_url):
    global content_data, user_audio_selection, user_video_selection

    # Fetch season details
    season_id = extract_season_id(content_url)  # Implement this function to extract the season ID from the URL
    season_data = jiocine.getContentDetails(season_id)
    if not season_data:
        await message.reply_text("[X] Season Details Not Found!")
        return

    episodes = jiocine.getSeriesEpisodes(season_id)
    if not episodes:
        await message.reply_text("[X] Season Episodes Not Found!")
        return

    # Ask for audio and video selection once
    if not user_audio_selection or not user_video_selection:  # Check if selections are already made
        await ask_for_audio_video_selection(client, message, episodes)

    # Download each episode one by one
    for episode in episodes:
        episode_id = episode['id']
        episode_data = jiocine.getContentDetails(episode_id)
        if not episode_data:
            await message.reply_text(f"[X] Episode Details Not Found for Episode ID: {episode_id}")
            continue

        # Proceed with downloading the episode using stored selections
        await download_playback(episode_id, episode_data, message)

async def ask_for_audio_video_selection(client, message, episodes):
    global user_audio_selection, user_video_selection

    # Logic to ask for audio selection
    audio_buttons = create_selection_buttons(
        [
            f"{lang_map.get(fmt['language'], fmt['language'])} ({codec_mapping.get(fmt.get('acodec', 'Unknown'), 'Unknown')} - {processed_abrs[i]} kbps)"
            for i, fmt in enumerate(audio_formats)
        ],
        "select_audio",
        user_audio_selection
    )

    await message.reply_text("Please select audio tracks:", reply_markup=audio_buttons)

    # Logic to ask for video selection
    video_buttons = create_selection_buttons(
        [
            f"{fmt.get('height', 'Unknown')}p ({vcodec_mapping.get(fmt.get('vcodec', 'Unknown'), 'Unknown')} - {processed_vbrs[i] if i < len(processed_vbrs) else 'N/A'} kbps)"
            for i, fmt in enumerate(video_formats)
        ],
        "select_video",
        user_video_selection
    )

    await message.reply_text("Please select video tracks:", reply_markup=video_buttons)



async def get_video_duration(video_path):
    """Get the duration of the video file using ffprobe."""
    try:
        # Use ffprobe to get the duration
        result = await asyncio.to_thread(subprocess.run, 
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        duration = float(result.stdout.strip())
        return duration  # Return duration in seconds
    except subprocess.CalledProcessError as e:
        print(f"[!] Error getting video duration: {e}")
        return 0  # Return 0 if there's an error

async def extract_thumbnail_at_timestamp(video_path, thumbnail_path, timestamp):
    """Extract a thumbnail from the video at a specific timestamp."""
    try:
        await asyncio.to_thread(subprocess.run,
            ['ffmpeg', '-y', '-i', video_path, '-ss', str(timestamp), '-vframes', '1', thumbnail_path],
            check=True
        )
        print(f"Thumbnail extracted successfully: {thumbnail_path}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error extracting thumbnail: {e}")

def sanitize_filename(name):
    # Replace problematic characters with safe ones
    return name.replace(':', '_').replace('#', '_').replace('/', '_').replace('\\', '_')

def download_content(output_dir_name, content, content_info, base_url, audio_file_paths, has_drm):
    # Update output name
    sanitized_output_dir_name = sanitize_filename(output_dir_name)  # Sanitize the directory name
    output_name = sanitized_output_dir_name.replace(" ", "_")  # Replace spaces with underscores

    is_processing_link = False  # Reset the processing state after the operation is complete

    if is_series_episode:
        output_name = f'E{content["episode"]}-{sanitize_filename(content["fullTitle"])}'  # Sanitize the title
        print(f'[=>] Downloading S{content["season"]}E{content["episode"]} {content["fullTitle"]}')
    else:
        print(f"[=>] Downloading {sanitized_output_dir_name}")

    output_name += f'.{content_info["height"]}p'
    output_name += f'.{content["defaultLanguage"]}'
    output_name += '.WEB-DL'

    # Audio Codec
    if 'acodec' in content_info:
        acodec = content_info['acodec']
        if acodec and acodec in jiocine.AUDIO_CODECS:
            acodec = jiocine.AUDIO_CODECS[acodec]
            if 'AAC' in acodec:
                output_name += '.AAC'
            elif 'AC3' in acodec:
                output_name += '.DD'
            elif 'EAC3' in acodec:
                output_name += '.DD+'

    # Video Codec
    dyr = content_info['dynamic_range']
    if dyr and dyr == 'HDR':
        output_name += '.x265.10bit.HDR'
    else:
        vcodec = content_info['vcodec']
        if vcodec and 'hvc' in vcodec:
            output_name += '.x265'
        else:
            output_name += '.x264'

    output_name += '.%(ext)s'

    ydl_opts = {
        'outtmpl': output_name,
        # Add other options as needed
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Custom Decryptor for DRM Vids
            if has_drm:
                class DRMDecryptPP(PostProcessor):
                    def run(self, info):
                        # If hls stream
                        if 'requested_formats' not in info:
                            return [], info

                        # If decrypted file already there
                        if 'filepath' not in info['requested_formats'][0]:
                            return [], info

                        del_paths = []
                        dec_paths = []
                        self.to_screen('Doing Post Processing')
                        pssh_cache = config.get("psshCacheStore")

                        # Try finding key for
                        for fmts in info['requested_formats']:
                            fmt_id = fmts['format_id']
                            filepath = fmts['filepath']

                            fmt_code = f"f{fmt_id}"
                            outPath = fmts['filepath'].replace(fmt_code, fmt_code + "dec")  # Corrected line

                            if fmt_id in rid_map:
                                _data = rid_map[fmt_id]
                                pssh = _data['pssh']
                                kid = _data['kid']

                                if pssh in pssh_cache:
                                    _data = pssh_cache[pssh]
                                    self.to_screen(f'{kid}:{_data[kid]}')
                                    self.to_screen('Decrypting Content')
                                    decrypt_vod_mp4d(kid, _data[kid], filepath, outPath)
                                    del_paths.append(filepath)
                                    dec_paths.append(outPath)

                        # Merge both decrypted parts
                        self.to_screen('Merging Audio and Video')
                        merge_vod_ffmpeg(del_paths, dec_paths)

                        return [], info

                ydl.add_post_processor(DRMDecryptPP())
            ydl.download([base_url])

        # Check if video file exists
        video_file_path = os.path.join(sanitized_output_dir_name, output_name)
        if not os.path.exists(video_file_path):
            print(f"Video file does not exist: {video_file_path}")
            return

        # Check if audio files exist
        for audio_path in audio_file_paths:
            if not os.path.exists(audio_path):
                print(f"Audio file does not exist: {audio_path}")
                return

    except yt_dlp.utils.DownloadError as e:
        print(f"Download error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

import os
import asyncio
import subprocess

async def merge_vod_ffmpeg(video_path, audio_paths, output_path, download_message, precaption, credits):
    """
    Merge video and audio streams using FFmpeg with metadata embedding.
    
    Parameters:
    - video_path: Path to the video file.
    - audio_paths: List of paths to the audio files.
    - output_path: Path to the output file.
    - download_message: Telegram message object for sending updates.
    - precaption: Pre-caption for messages (if needed).
    - credits: Metadata to embed, such as "encoded by {credits}".
    """
    # Check if video file exists
    if not os.path.exists(video_path):
        print(f"Video file does not exist: {video_path}")
        await download_message.reply_text("[!] Video file does not exist.")
        return

    # Check if audio files exist
    for audio_path in audio_paths:
        if not os.path.exists(audio_path):
            print(f"Audio file does not exist: {audio_path}")
            await download_message.reply_text(f"[!] Audio file does not exist: {audio_path}")
            return

    # Function to get bitrate for audio files
    def get_bitrate(file_path):
        command = [
            'ffprobe', '-v', 'error', '-select_streams', 'a:0',
            '-show_entries', 'stream=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', file_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0 and result.stdout.strip().isdigit():
            return int(result.stdout.strip()) // 1000  # Convert to kbps
        return None

    # Get audio bitrates
    audio_metadata = []
    for audio_path in audio_paths:
        bitrate = get_bitrate(audio_path)
        if bitrate:
            audio_metadata.append(f"title={credits} - {bitrate} kbps")
        else:
            audio_metadata.append(f"title={credits} - Unknown kbps")
            print(f"Could not determine bitrate for: {audio_path}")
            await download_message.reply_text(f"[!] Could not determine bitrate for: {audio_path}")

    # Construct the FFmpeg command
    command = ['ffmpeg', '-hide_banner', '-y', '-i', video_path]

    # Add each audio file to the command
    for audio_path in audio_paths:
        command.extend(['-i', audio_path])

    # Set the video codec to copy
    command.extend(['-c:v', 'copy'])

    # Map the video stream and all audio streams to the output
    command.append('-map')
    command.append('0:v')  # Map the video stream from the first input (video file)

    # Map each audio stream and embed its metadata
    for i, metadata in enumerate(audio_metadata):
        command.append('-map')
        command.append(f'{i + 1}:a')  # Map each audio stream
        command.extend(['-metadata:s:a:' + str(i), metadata])  # Metadata for each audio stream

    # Embed global metadata
    command.extend([
        '-metadata', f"encoded_by={credits}",
        '-metadata', f"genre={credits}",
        '-metadata', f"album={credits}",
        '-metadata', f"comment={credits}",
        '-metadata', f"artist={credits}",
        '-metadata', f"publisher={credits}",
        '-metadata:s:v', f"title={credits}"  # Video stream metadata
    ])

    # Specify the output file
    command.append(output_path)

    # Execute the command in a separate thread
    try:
        await asyncio.to_thread(subprocess.run, command, check=True)  # Run the FFmpeg command asynchronously
        print(f"Muxing completed successfully: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during muxing: {e}")
        await download_message.reply_text("[!] Error during muxing.")



class tgUploader:
    def __init__(self, app, message, message_id, muxing_message):
        self.app = app
        self.message = message
        self.message_id = message_id
        self.muxing_message = muxing_message

    async def upload_file(self, file_path, precaption, duration: float, thumbnail_path):
        await self.muxing_message.delete()  # Delete the muxing message
        up_dn_msg_message = None  # Initialize the message variable
        uploaded_size = 0  # Initialize uploaded_size in the outer function
        last_update_time = time.time()  # Track the last update time

        try:
            file_size = os.path.getsize(file_path)
            start_time = time.time()

            # Ensure duration is a float
            if not isinstance(duration, (int, float)):
                print(f"[!] Duration is not a float: {duration}")
                return

            async def progress(current, total):
                nonlocal uploaded_size, last_update_time
                uploaded_size = current
                elapsed_time = time.time() - start_time
                speed = (uploaded_size / (1024 * 1024)) / elapsed_time if elapsed_time > 0 else 0  # Speed in MB/s
                eta = (total - uploaded_size) / (speed * 1024 * 1024) if speed > 0 else 0  # ETA in seconds

                # Calculate percentage
                percent = (uploaded_size / total) * 100

                # Determine size format (MB or GB)
                if file_size > 1000 * 1024 * 1024:  # Greater than 1000 MB
                    uploaded_size_display = uploaded_size / (1024 * 1024 * 1024)  # Convert to GB
                    file_size_display = file_size / (1024 * 1024 * 1024)  # Convert to GB
                    size_unit = "GB"
                else:
                    uploaded_size_display = uploaded_size / (1024 * 1024)  # Convert to MB
                    file_size_display = file_size / (1024 * 1024)  # Convert to MB
                    size_unit = "MB"

                # Calculate blocks for progress bar
                blocks = int(percent // 5)  # Each block represents 5%
                progress_bar = '⬢' * blocks + '⬡' * (20 - blocks)  # 20 blocks total

                # Print simple console output
                print(f"Upload Progress: {percent:.2f}% | Uploaded: {uploaded_size}/{total} bytes")

                # Update the message in the chat only if 5 seconds have passed
                current_time = time.time()
                if current_time - last_update_time >= 5:  # Check if 5 seconds have passed
                    # Create a detailed message for the chat
                    chat_message = (
                        f"<code>[ + ] ......</code> <b>Uploading The File :-</b>\n"
                        f"<b>File - Name :-</b> <code>{precaption}</code>\n"   
                        f"<b>[{progress_bar}]</b>\n"  # Progress bar
                        f"<b>Percentage :-</b> <code>{percent:.2f}%</code>\n"  # Percentage display
                        f"<b>Uploaded :-</b> <code>{uploaded_size_display:.2f} {size_unit} / {file_size_display:.2f} {size_unit}</code>\n"  # Uploaded size
                        f"<b>ETA :-</b> <code>{eta:.2f} seconds</code>\n"  # ETA 
                        f"<b>Speed :-</b> <code>{speed:.2f} MB/s </code>"  # Speed
                    )
                    try:
                        up_dn_msg_message = await self.app.edit_message_text(chat_id=self.message.chat.id, message_id=self.message_id, text=chat_message)
                        last_update_time = current_time  # Update the last update time
                    except FloodWait as e:
                        print(f"FloodWait: Sleeping for {e.x} seconds")
                        await asyncio.sleep(e.x)  # Wait for the specified time
                        up_dn_msg_message = await self.app.edit_message_text(chat_id=self.message.chat.id, message_id=self.message_id, text=chat_message)  # Retry sending the message

            # Upload the video with the thumbnail and capture the message
            video_message = await self.app.send_video(
                chat_id=self.message.chat.id,
                video=file_path,
                progress=progress,
                caption=precaption,
                width=1280,
                height=720,
                duration=duration , 
                thumb=thumbnail_path
            )
            print(f"[+] Successfully uploaded: {file_path}")

            if hasattr(video_message, 'id'):
                print(f"[DEBUG] Video message ID: {video_message.id}")  # Debugging line
                await self.app.copy_message(
                        chat_id=dump_chat_id[0],  # Access the first element of the list
                    from_chat_id=self.message.chat.id,
                    message_id=video_message.id   # The ID of the message to copy
                )
                logger.info(f"Video forwarded successfully for {chat_id} to dump chat {dump_chat_id}.")
            else:
               print("[!] Video message ID is not available.")

            # Cleanup: Delete the uploaded file and thumbnail
            os.remove(file_path)
            os.remove(thumbnail_path)
            print(f"[+] Deleted local files: {file_path} and {thumbnail_path}")

        except Exception as e:
            print(f"[!] Failed to upload file: {file_path}. Error: {e}")

        # Delete the progress message if it was created
        if up_dn_msg_message:
            await up_dn_msg_message.delete()

# Main execution
if __name__ == '__main__':
    print('[=>] Jio Cinema Downloader Bot Starting')

    if not config.get("authToken") and not config.get("useAccount"):
        print("[=>] Guest Token is Missing, Requesting One")
        guestToken = jiocine.fetchGuestToken()
        if not guestToken:
            print("[!] Guest Token Not Received")
            exit(0)

        print("[=>] Got Guest Token :)")
        config.set("authToken", guestToken)

    print(f'[=>] Welcome {config.get("accountName")}, Jio Cinema Free User')

    app.start()
    print("Bot started")
    idle()
    app.stop()
