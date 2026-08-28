import json
import re

with open("data/raw_fetched.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

for name in ["https://www.apisou.com/", "https://apiranking.com/", "https://routerhubs.com/", "https://aisitenav.com/"]:
    if name in raw_data:
        print(f"=== {name} ===")
        content = raw_data[name]
        # check for NEXT_DATA
        if '__NEXT_DATA__' in content:
            print("Found __NEXT_DATA__")
            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', content, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    print("Parsed NEXT_DATA successfully!")
                    with open(f"data/{name.replace('/', '_').replace(':', '')}_nextdata.json", "w") as out:
                        json.dump(data, out, indent=2, ensure_ascii=False)
                except Exception as e:
                    print(f"Error parsing NEXT_DATA: {e}")
        # check for nuxt or other scripts
        script_matches = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
        print(f"Total script tags: {len(script_matches)}")
        for idx, s in enumerate(script_matches):
            if "http" in s or "domain" in s or "url" in s or "site" in s:
                print(f"  Script {idx} length: {len(s)}")
