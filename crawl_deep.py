import subprocess
import json
import re
import urllib.parse
import os
import concurrent.futures

os.makedirs("data/pages", exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

def curl_fetch(url, timeout=10):
    try:
        res = subprocess.run(["curl", "-sL", "-A", HEADERS['User-Agent'], "--max-time", str(timeout), url], capture_output=True, text=True, errors='ignore')
        return res.stdout
    except Exception as e:
        return ""

# 1. Fetch all apisou site pages
print("Fetching apisou site pages...")
apisou_sitemap = curl_fetch("https://www.apisou.com/sitemap.xml")
apisou_slugs = re.findall(r'<loc>(https://www\.apisou\.com/site/[^<]+)</loc>', apisou_sitemap)
print(f"Found {len(apisou_slugs)} apisou pages.")

apisou_pages = {}
def fetch_apisou(u):
    content = curl_fetch(u)
    return u, content

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(fetch_apisou, apisou_slugs)
    for u, c in results:
        if c:
            apisou_pages[u] = c

print(f"Fetched {len(apisou_pages)} apisou detail pages.")

# 2. Fetch apiranking ranking pages
print("Fetching apiranking subpages...")
apiranking_urls = [
    "https://apiranking.com/",
    "https://apiranking.com/rankings/claude-api",
    "https://apiranking.com/rankings/gpt-api",
    "https://apiranking.com/rankings/gemini-api",
    "https://apiranking.com/rankings/grok-api",
    "https://apiranking.com/verify-yourself"
]
apiranking_pages = {}
for u in apiranking_urls:
    c = curl_fetch(u)
    if c:
        apiranking_pages[u] = c

# Check apiranking /go/ targets by following redirects for a sample or checking JSON-LD
apiranking_go_links = set(re.findall(r'href=["\'](/go/[^"\']+)["\']', "\n".join(apiranking_pages.values())))
print(f"Found {len(apiranking_go_links)} /go/ links in apiranking.")

def resolve_go(path):
    # Use curl -I -sL -w "%{url_effective}" to get final url
    url = f"https://apiranking.com{path}"
    try:
        res = subprocess.run(["curl", "-sL", "-o", "/dev/null", "-w", "%{url_effective}", "--max-time", "6", url], capture_output=True, text=True, errors='ignore')
        return path, res.stdout.strip()
    except:
        return path, ""

go_targets = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
    results = executor.map(resolve_go, apiranking_go_links)
    for p, dest in results:
        if dest and dest != f"https://apiranking.com{p}":
            go_targets[p] = dest

print(f"Resolved {len(go_targets)} redirect links from apiranking.")

# Save everything
with open("data/apisou_pages.json", "w", encoding="utf-8") as f:
    json.dump(apisou_pages, f, ensure_ascii=False)

with open("data/apiranking_pages.json", "w", encoding="utf-8") as f:
    json.dump(apiranking_pages, f, ensure_ascii=False)

with open("data/apiranking_redirects.json", "w", encoding="utf-8") as f:
    json.dump(go_targets, f, ensure_ascii=False, indent=2)

print("Crawling complete.")
