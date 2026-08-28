import subprocess
import json
import re

def fetch(url):
    res = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "--max-time", "10", url], capture_output=True, text=True, errors='ignore')
    return res.stdout

# 1. Check apisou sitemap / api
print("Fetching apisou sitemap...")
apisou_sitemap = fetch("https://www.apisou.com/sitemap.xml")
print("apisou sitemap length:", len(apisou_sitemap))
site_slugs = re.findall(r'<loc>https://www\.apisou\.com/site/([^<]+)</loc>', apisou_sitemap)
print(f"Found {len(site_slugs)} site slugs in apisou sitemap")

# 2. Check apiranking sitemap
print("Fetching apiranking sitemap...")
apiranking_sitemap = fetch("https://apiranking.com/sitemap.xml")
print("apiranking sitemap length:", len(apiranking_sitemap))
apiranking_slugs = re.findall(r'<loc>https://apiranking\.com/go/([^<]+)</loc>', apiranking_sitemap)
print(f"Found {len(apiranking_slugs)} slugs in apiranking sitemap")

# Check if apiranking has an api or json
apiranking_js = fetch("https://apiranking.com/static/js/main.js") # or check html for script src
print("apiranking js length:", len(apiranking_js))
