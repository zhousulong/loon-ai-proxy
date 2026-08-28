import json

with open("data/domains_metadata.json", "r") as f:
    data = json.load(f)

domains = list(data["domains"].keys())

cn_domains = [d for d in domains if d.endswith(".cn")]
print(f"Total .cn domains in current list: {len(cn_domains)}")
print("Sample .cn domains:", cn_domains[:20])
