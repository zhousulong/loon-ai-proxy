import urllib.request
import urllib.parse
import re
import ssl
import json
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

sources = {
    "github_raw": [
        "https://raw.githubusercontent.com/frank36512/aiapi/main/README.md",
        "https://raw.githubusercontent.com/howardpen9/awesome-ai-api-proxy/main/README.md",
        "https://raw.githubusercontent.com/Claws-ZH/awesome-ai-api/main/README.md",
        "https://raw.githubusercontent.com/mn-api/awesome-ai-proxy/main/README.md",
        # try master branch as fallback if main fails
        "https://raw.githubusercontent.com/frank36512/aiapi/master/README.md",
        "https://raw.githubusercontent.com/howardpen9/awesome-ai-api-proxy/master/README.md",
        "https://raw.githubusercontent.com/Claws-ZH/awesome-ai-api/master/README.md",
        "https://raw.githubusercontent.com/mn-api/awesome-ai-proxy/master/README.md",
    ],
    "nav_sites": [
        "https://www.apisou.com/",
        "https://aisitenav.com/",
        "https://apiranking.com/",
        "https://routerhubs.com/",
        "https://howtok.net/",
    ]
}

def fetch_url(url):
    print(f"Fetching: {url}")
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            content = resp.read()
            try:
                return content.decode('utf-8')
            except:
                return content.decode('gbk', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

raw_data = {}
for url in sources["github_raw"]:
    content = fetch_url(url)
    if content:
        raw_data[url] = content

for url in sources["nav_sites"]:
    content = fetch_url(url)
    if content:
        raw_data[url] = content

os.makedirs("data", exist_ok=True)
with open("data/raw_fetched.json", "w", encoding="utf-8") as f:
    json.dump(raw_data, f, ensure_ascii=False, indent=2)

print(f"Saved {len(raw_data)} fetched contents.")
