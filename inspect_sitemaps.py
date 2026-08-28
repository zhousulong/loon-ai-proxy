import re
import subprocess
import json
import concurrent.futures

# Let's inspect apiranking sitemap
res = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "https://apiranking.com/sitemap.xml"], capture_output=True, text=True, errors='ignore').stdout
urls = re.findall(r'<loc>([^<]+)</loc>', res)
print(f"apiranking sitemap has {len(urls)} urls. Sample:")
for u in urls[:15]:
    print(" ", u)

# Also let's inspect routerhubs scripts and html for all table data
res_rh = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "https://routerhubs.com/"], capture_output=True, text=True, errors='ignore').stdout
print("routerhubs page length:", len(res_rh))
# Find domain params or website urls
rh_domains = set(re.findall(r'domain=([a-zA-Z0-9\.\-_]+)', res_rh))
print("routerhubs domain params:", len(rh_domains), list(rh_domains)[:10])

# apisou sitemap
apisou_sitemap = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "https://www.apisou.com/sitemap.xml"], capture_output=True, text=True, errors='ignore').stdout
apisou_urls = re.findall(r'<loc>([^<]+)</loc>', apisou_sitemap)
print(f"apisou sitemap has {len(apisou_urls)} urls.")
