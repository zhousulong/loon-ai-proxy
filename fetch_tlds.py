import urllib.request
import ssl
import json
import re

# Fetch IANA official TLD list for exact TLD validation
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

tld_url = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
try:
    req = urllib.request.Request(tld_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        tlds = {line.decode('utf-8').strip().lower() for line in resp.readlines() if not line.startswith(b'#')}
    print(f"Fetched {len(tlds)} valid IANA TLDs")
except Exception as e:
    print(f"Failed to fetch IANA TLDs: {e}")
    # Fallback to broad common TLD list
    tlds = {"com", "net", "org", "cn", "ai", "io", "cc", "top", "xyz", "tech", "vip", "fun", "site", "cloud", "pro", "work", "space", "ink", "shop", "me", "co", "link", "chat", "pub", "dev", "best", "app", "hk", "tw", "one", "in", "icu", "live", "today", "online", "run", "plus", "cx", "la", "so", "sh", "asia", "pw", "is", "fm", "vc", "su", "gg", "uk", "jp", "de", "us", "kr", "fr", "ca", "ru", "info", "biz", "mobi", "name", "art", "club", "store", "buzz", "moe", "ltd", "life", "xin", "win", "tv", "pics", "studio", "cool", "fan", "ren", "host", "love", "market", "sbs", "lol", "codes", "lat", "world", "cfd", "my", "mx", "mom", "ge", "gs", "vg"}

with open("data/iana_tlds.json", "w") as f:
    json.dump(list(tlds), f)
