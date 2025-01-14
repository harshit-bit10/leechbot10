import os
import json

# Some functions
joinPath = os.path.join
isDir = os.path.isdir
isExist = os.path.exists
scriptsDir = os.path.dirname(__file__)
realPath = os.path.realpath


# Simple Implementation class to manage JSON Config Objects
class JSO:
    __jso = {}
    __path = ""
    __ind = None

    def __init__(self, path, indent=None):
        self.__path = path
        self.__ind = indent
        self.load()

    def store(self):
        try:
            fo = open(self.__path, "w")
            fo.write(json.dumps(self.__jso, indent=self.__ind))
            fo.close()
        except Exception as e:
            print(e)
            exit(0)

    def load(self):
        try:
            fo = open(self.__path, "r")
            self.__jso = json.load(fo)
            fo.close()
        except Exception as e:
            print(e)
            exit(0)

    def get(self, attr):
        return self.__jso[attr]

    def set(self, attr, val):
        self.__jso[attr] = val
        self.store()


def readFile(fname):
    f = open(fname, "r")
    data = f.read()
    f.close()
    return data


def outFile(fname, data):
    fo = open(fname, "w")
    fo.write(data)
    fo.close()


def copyFile(old, new):
    f = open(old, "r")
    outFile(new, f.read())
    f.close()


def clearFolder(dirs):
    filesToRemove = [joinPath(dirs, f) for f in os.listdir(dirs)]
    for f in filesToRemove:
        os.remove(f)


def createDir(path, override=False):
    if override or not isExist(path):
        os.mkdir(path)
        return True
    return False


import os
import re
import json
import requests
import pytz
import ffmpeg, time, math
from urllib.parse import urlparse

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from datetime import datetime, timedelta



colored_text_config = False

MESSAGE = "\n[+] {}\n[+] {} : {}"

def print_message(first, second, third):
    print(MESSAGE.format(colored_text(first, "green"), colored_text(
        second, "blue"), colored_text(third, "cyan")))


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]


async def progress_for_pyrogram(
    current,
    total,
    ud_type,
    message,
    start
):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "\n[{0}{1}] \n**Process**: `{2}%`\n".format(
            ''.join(["█" for i in range(math.floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))

        tmp = progress + "`{0} of {1}`\n**Speed:** `{2}/s`\n**ETA:** `{3}`\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text="{}\n {}".format(
                    ud_type,
                    tmp
                )
            )
        except:
            pass

def colored_text(text, color):
    colors = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m",
    }
    if colored_text_config is True:
        return f"{colors[color]}{text}{colors['reset']}"
    else:
        return text
    
def get_duration(filepath):
    metadata = extractMetadata(createParser(filepath))
    if metadata.has("duration"):
        return metadata.get('duration').seconds
    else:
        return 0


def get_thumbnail(in_filename, path, ttl):
    out_filename = os.path.join(path, str(time.time()) + ".jpg")
    open(out_filename, 'a').close()
    try:
        (
            ffmpeg
            .input(in_filename, ss=ttl)
            .output(out_filename, vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return out_filename
    except ffmpeg.Error as e:
        return None






def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result


def timestamp_to_datetime(timestamp, timezone = "Asia/Kolkata"):
    dt_object = datetime.fromtimestamp(timestamp / 1000, tz=pytz.utc)
    dt_object = dt_object.astimezone(pytz.timezone(timezone))  
    return dt_object.strftime("%d/%m/%Y+%H:%M:%S")






