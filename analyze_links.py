import json
import re
import urllib.parse
import base64

with open("data/raw_fetched.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

for source, content in raw_data.items():
    print(f"--- Analyzing {source} ---")
    
    # Check for specific patterns like go?to= or jump.html?target= or base64 or direct hrefs
    jump_matches = re.findall(r'(?:href|src|url)=["\']?([^"\' >]+)', content, re.IGNORECASE)
    markdown_links = re.findall(r'\[([^\]]*)\]\((https?://[^\)]+)\)', content)
    raw_http_links = re.findall(r'https?://[a-zA-Z0-9\.\-_]+(?::\d+)?(?:/[^\s<>"\'\)]*)?', content)
    
    all_links = set(raw_http_links + [l[1] for l in markdown_links])
    print(f"Total raw links found: {len(all_links)}")
    
    # Sample a few links
    sample = list(all_links)[:10]
    for s in sample:
        print(f"  {s}")
