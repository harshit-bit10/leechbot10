import requests
import xmltodict
import logging

# Initialize Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger("JioCinemaDownloader")

# Session Setup
session = requests.Session()

# Headers for requests
HEADERS = {
    "Origin": "https://www.jiocinema.com",
    "Referer": "https://www.jiocinema.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
}

# Language Map
LANG_MAP = {
    "en": "English", "hi": "Hindi", "gu": "Gujarati", "ta": "Tamil",
    "te": "Telugu", "kn": "Kannada", "mr": "Marathi", "ml": "Malayalam",
    "bn": "Bengali", "bho": "Bhojpuri", "pa": "Punjabi", "or": "Oriya"
}

# Reverse Language Map
REV_LANG_MAP = {v: k for k, v in LANG_MAP.items()}

# Fetch Guest Token
def fetch_guest_token():
    url = "https://auth-jiocinema.voot.com/tokenservice/apis/v4/guest"
    payload = {
        "appName": "RJIL_JioCinema",
        "deviceType": "fireTV",
        "os": "android",
        "deviceId": "1464251119",
        "freshLaunch": False,
        "adId": "1464251119",
        "appVersion": "4.1.3"
    }

    try:
        response = session.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        token = data.get('authToken')
        if token:
            logger.info("Successfully fetched guest token.")
            return token
        else:
            logger.error("Failed to fetch guest token: Token missing in response.")
    except Exception as e:
        logger.error(f"Error fetching guest token: {e}")
    return None

# Fetch Content Details
def get_content_details(content_id):
    url = f"https://content-jiovoot.voot.com/psapi/voot/v1/voot-web/content/query/asset-details?ids=include:{content_id}&responseType=common"
    try:
        response = session.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        result = data.get('result', [])
        if result:
            logger.info(f"Fetched content details for ID: {content_id}")
            return result[0]
        else:
            logger.warning("No content details found.")
    except Exception as e:
        logger.error(f"Error fetching content details: {e}")
    return None

# Fetch Playback Data
def fetch_playback_data(content_id, token):
    url = f"https://apis-jiovoot.voot.com/playbackjv/v3/{content_id}"
    payload = {
        "4k": True,
        "appVersion": "3.4.0",
        "multiAudioRequired": True,
        "hevc": True,
        "dolby": True
    }
    headers = {
        "accesstoken": token,
        "x-platform": "androidstb",
        "x-platform-token": "stb",
        **HEADERS
    }
    try:
        response = session.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        playback_data = data.get('data')
        if playback_data:
            logger.info(f"Playback data fetched for content ID: {content_id}")
            return playback_data
        else:
            logger.warning("Playback data not available.")
    except Exception as e:
        logger.error(f"Error fetching playback data: {e}")
    return None

# Fetch MPD Data
def fetch_mpd_data(mpd_url):
    try:
        response = session.get(mpd_url, headers=HEADERS)
        response.raise_for_status()
        return xmltodict.parse(response.content)
    except Exception as e:
        logger.error(f"Error fetching MPD data: {e}")
    return None

# Parse MPD for PSSH and KID
def parse_mpd_data(mpd_data):
    rid_kid = {}
    pssh_kid = {}

    def process_content_protection(rid, cp):
        if cp[1]["@schemeIdUri"].lower() == "urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed":
            pssh = cp[1].get("cenc:pssh")
            if pssh:
                kid = cp[0].get("@cenc:default_KID", "").replace("-", "")
                rid_kid[rid] = {"kid": kid, "pssh": pssh}
                pssh_kid.setdefault(pssh, set()).add(kid)

    try:
        for adaptation in mpd_data.get('AdaptationSet', []):
            representations = adaptation.get('Representation', [])
            if not isinstance(representations, list):
                representations = [representations]
            for representation in representations:
                cp = representation.get('ContentProtection', [])
                if len(cp) > 1:
                    process_content_protection(representation['@id'], cp)
        return rid_kid, pssh_kid
    except Exception as e:
        logger.error(f"Error parsing MPD data: {e}")
    return {}, {}

