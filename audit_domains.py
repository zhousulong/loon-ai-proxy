import json
import re

with open("data/raw_fetched.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Let's inspect all domains and write them to a structured file with details
with open("process_domains.py", "r") as f:
    code = f.read()

# Let's run a full scan and export to CSV/JSON to inspect
