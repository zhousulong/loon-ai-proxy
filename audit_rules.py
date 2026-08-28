import json

with open("data/domains_metadata.json", "r") as f:
    data = json.load(f)

domains = list(data["domains"].keys())

suspicious = []
for d in domains:
    # Check if domain has suspicious characters or patterns
    if not any(d.endswith(tld) for tld in [".com", ".cn", ".net", ".org", ".ai", ".io", ".cc", ".top", ".xyz", ".tech", ".vip", ".fun", ".site", ".cloud", ".pro", ".work", ".space", ".ink", ".shop", ".me", ".co", ".link", ".chat", ".pub", ".dev", ".best", ".app", ".hk", ".tw", ".one", ".in", ".icu", ".live", ".today", ".online", ".run", ".plus", ".cx", ".la", ".so", ".sh", ".asia", ".pw", ".is", ".fm", ".vc", ".su", ".gg"]):
        suspicious.append(d)

print(f"Suspicious TLDs ({len(suspicious)}):", suspicious)

# Check single character or very short or weird
weird = [d for d in domains if len(d.split(".")[0]) <= 1 or "-" in d.split(".")[-1]]
print("Weird domains:", weird)

# Print first 50 domains
print("\nFirst 50 domains:")
for d in domains[:50]:
    print(f"  {d}")
