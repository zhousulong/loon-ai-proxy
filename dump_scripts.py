import json
import re

with open("data/raw_fetched.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Let's inspect apisou.com
apisou = raw_data.get("https://www.apisou.com/", "")
print("=== APISOU SCRIPT SNIPPET ===")
scripts = re.findall(r'<script[^>]*>(.*?)</script>', apisou, re.DOTALL)
for s in scripts[:5]:
    if len(s) > 100:
        print(s[:300])
        print("---")

# Let's inspect apiranking.com
apiranking = raw_data.get("https://apiranking.com/", "")
print("=== APIRANKING SCRIPT SNIPPET ===")
scripts2 = re.findall(r'<script[^>]*>(.*?)</script>', apiranking, re.DOTALL)
for s in scripts2[:5]:
    if len(s) > 100:
        print(s[:400])
        print("---")

# Let's inspect routerhubs.com
routerhubs = raw_data.get("https://routerhubs.com/", "")
print("=== ROUTERHUBS SNIPPET ===")
print(routerhubs[1000:2500])
