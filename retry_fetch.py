import json
import re
import subprocess
import os

# Let's retry failed ones using curl
failed_urls = [
    "https://apiranking.com/",
    "https://raw.githubusercontent.com/Claws-ZH/awesome-ai-api/master/README.md",
    "https://raw.githubusercontent.com/mn-api/awesome-ai-proxy/master/README.md",
]

def fetch_with_curl(url):
    try:
        res = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36", "--max-time", "15", url], capture_output=True, text=True, errors='ignore')
        return res.stdout
    except Exception as e:
        print(f"Curl error {url}: {e}")
        return ""

with open("data/raw_fetched.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

for url in failed_urls:
    if url not in raw_data or len(raw_data[url]) < 100:
        print(f"Retrying with curl: {url}")
        content = fetch_with_curl(url)
        if content:
            raw_data[url] = content
            print(f"Successfully fetched {url}, len={len(content)}")

with open("data/raw_fetched.json", "w", encoding="utf-8") as f:
    json.dump(raw_data, f, ensure_ascii=False, indent=2)

for k, v in raw_data.items():
    print(f"{k}: length {len(v)}")
