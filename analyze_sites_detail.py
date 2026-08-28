import json
import re

with open("data/raw_fetched.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# 1. apiranking.com
apiranking = raw_data.get("https://apiranking.com/", "")
print("apiranking.com analysis:")
# Check schema.org ItemList or HTML cards
json_ld_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', apiranking, re.DOTALL)
for j in json_ld_matches:
    try:
        data = json.loads(j)
        if data.get("@type") == "ItemList":
            print(f"  Found ItemList with {len(data.get('itemListElement', []))} items")
            print("  First item:", json.dumps(data.get('itemListElement', [])[0], indent=2, ensure_ascii=False))
    except Exception as e:
        print("  JSON-LD parse error:", e)

# Check all direct links or href in HTML
cards = re.findall(r'href=["\'](https?://[^"\']+|/go/[^"\']+)["\']', apiranking)
print(f"  Total hrefs in apiranking: {len(cards)}")
print("  Sample apiranking hrefs:", cards[:10])

# 2. apisou.com
apisou = raw_data.get("https://www.apisou.com/", "")
print("\napisou.com analysis:")
# apisou might have site links like /site/xxx or direct links or embedded data
apisou_sites = re.findall(r'href=["\'](/site/[^"\']+)["\']', apisou)
print(f"  /site/ links in apisou: {len(apisou_sites)}")
apisou_all_urls = re.findall(r'https?://[a-zA-Z0-9\.\-]+(?::\d+)?(?:/[^\s<>"\'\)]*)?', apisou)
print(f"  all http URLs in apisou: {len(apisou_all_urls)}")
print("  Sample apisou URLs:", list(set(apisou_all_urls))[:15])

# 3. routerhubs.com
routerhubs = raw_data.get("https://routerhubs.com/", "")
print("\nrouterhubs.com analysis:")
json_ld_rh = re.findall(r'<script type="application/ld\+json">(.*?)</script>', routerhubs, re.DOTALL)
for j in json_ld_rh:
    try:
        data = json.loads(j)
        print("  RouterHubs JSON-LD type:", data.get("@type"))
    except:
        pass
# Search for baseUrl or domains in routerhubs HTML
rh_urls = re.findall(r'https?://[a-zA-Z0-9\.\-_]+(?:\.[a-zA-Z]{2,})(?::\d+)?(?:/[^\s<>"\'\\&]*)?', routerhubs)
print(f"  all URLs in routerhubs: {len(set(rh_urls))}")
print("  Sample routerhubs URLs:", list(set(rh_urls))[:15])

# 4. aisitenav.com
aisitenav = raw_data.get("https://aisitenav.com/", "")
print("\naisitenav.com analysis:")
# Favicon URLs often contain domains: https://favicon.im/DOMAIN?larger=true
fav_domains = re.findall(r'favicon\.im/([a-zA-Z0-9\.\-_]+)', aisitenav)
print(f"  Favicon domains in aisitenav: {len(fav_domains)}, unique: {len(set(fav_domains))}")
print("  Sample favicon domains:", list(set(fav_domains))[:15])

# 5. howtok.net
howtok = raw_data.get("https://howtok.net/", "")
print("\nhowtok.net analysis:")
howtok_urls = re.findall(r'https?://[a-zA-Z0-9\.\-_]+(?:\.[a-zA-Z]{2,})(?::\d+)?(?:/[^\s<>"\'\\&]*)?', howtok)
print(f"  all URLs in howtok: {len(set(howtok_urls))}")
print("  Sample howtok URLs:", list(set(howtok_urls))[:15])
