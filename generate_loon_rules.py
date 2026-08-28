import json
import re
import urllib.parse
import os
from datetime import datetime

# Comprehensive Blacklist
OFFICIAL_AI_AND_BIGTECH = {
    # OpenAI & Microsoft
    "openai.com", "chatgpt.com", "oaistatic.com", "oaiusercontent.com", "microsoft.com", "azure.com", "bing.com", "copilot.microsoft.com",
    # Anthropic
    "anthropic.com", "claude.ai",
    # Google
    "google.com", "googleapis.com", "google.dev", "ai.google.dev", "aistudio.google.com", "gstatic.com", "googleusercontent.com", "gemini.google.com",
    # xAI
    "x.ai", "grok.com",
    # Meta / AWS / Apple
    "meta.ai", "llama.com", "amazon.com", "amazonaws.com", "aws.amazon.com", "apple.com", "icloud.com",
    # Domestic Big Tech & Official AI
    "deepseek.com", "zhipuai.cn", "bigmodel.cn", "chatglm.cn", "baichuan-ai.com", "baichuanapi.com",
    "moonshot.cn", "kimi.ai", "minimaxi.com", "minimax.chat", "stepfun.com", "01.ai", "lingyiwanwu.com",
    "sensenova.cn", "xfyun.cn", "iflytek.com", "baidu.com", "baidubce.com", "yiyan.baidu.com",
    "aliyun.com", "alibaba-inc.com", "alibabacloud.com", "tongyi.aliyun.com", "tencent.com", "tencentcs.com",
    "hunyuan.tencent.com", "163.com", "netease.com", "fuxi.163.com", "360.com", "360.cn", "10086.cn",
    "kunlun-inc.com", "tiangong.cn", "doubao.com", "volcengine.com", "bytedance.com", "sensetime.com",
    # Well-known Official Providers
    "cohere.com", "together.ai", "mistral.ai", "perplexity.ai", "groq.com", "cerebras.ai", "novita.ai",
    "fal.ai", "replicate.com", "stability.ai", "midjourney.com", "elevenlabs.io", "runwayml.com", "huggingface.co"
}

PUBLIC_INFRA_AND_COMMUNITIES = {
    # Git & Code Hosting
    "github.com", "github.io", "githubusercontent.com", "gitlab.com", "gitee.com", "gitcode.com", "gitlink.org.cn", "coding.net",
    # Tech communities & forums
    "linux.do", "v2ex.com", "zhihu.com", "bilibili.com", "weibo.com", "qq.com", "weixin.qq.com", "mp.weixin.qq.com",
    "t.me", "telegram.org", "discord.com", "discord.gg", "twitter.com", "x.com", "facebook.com", "youtube.com",
    "medium.com", "juejin.cn", "csdn.net", "sspai.com", "cnblogs.com", "nodeseek.com", "hostloc.com", "v2nodes.com",
    "segmentfault.com", "infoq.cn", "oschina.net", "cnbeta.com.tw", "ithome.com", "smzdm.com",
    # Cloud / Hosting / PaaS
    "cloudflare.com", "cloudflarestream.com", "workers.dev", "pages.dev", "vercel.app", "netlify.app",
    "render.com", "zeabur.app", "railway.app", "deno.dev", "supabase.co", "firebaseapp.com",
    "akamai.com", "fastly.com", "jsdelivr.net", "unpkg.com", "cdnjs.cloudflare.com", "bootcdn.cn",
    # Analytics & Metrics & Shields
    "googletagmanager.com", "google-analytics.com", "clarity.ms", "umami.is", "posthog.com", "plausible.io",
    "schema.org", "w3.org", "shields.io", "badgen.net", "favicon.im", "iconify.design", "fontawesome.com",
    "sentry.io", "crisp.chat", "intercom.io", "tawk.to", "51.la", "cnzz.com", "tongji.baidu.com",
    # Navigators & Hubs
    "apisou.com", "aisitenav.com", "apiranking.com", "routerhubs.com", "howtok.net",
    "star-history.com", "awesome.re", "opencompass.org.cn", "arena.ai", "kilo.ai",
    # Payments / Auth
    "stripe.com", "alipay.com", "epay.me", "bufpay.com", "auth0.com", "clerk.dev", "clerk.com",
    "paypal.com", "wechat.com", "tenpay.com",
    # General / Search Engines / Docs
    "baidu.com", "bing.com", "sogou.com", "so.com", "duckduckgo.com", "wikipedia.org", "notion.site", "notion.so",
    "feishu.cn", "larksuite.com", "yuque.com", "wolai.com"
}

ALL_EXCLUDED = OFFICIAL_AI_AND_BIGTECH | PUBLIC_INFRA_AND_COMMUNITIES

MULTI_TLDS = {
    "com.cn", "net.cn", "org.cn", "gov.cn", "edu.cn",
    "co.uk", "org.uk", "me.uk", "ac.uk",
    "co.jp", "ne.jp", "ac.jp", "go.jp",
    "com.hk", "net.hk", "org.hk", "idv.hk", "edu.hk", "gov.hk",
    "com.tw", "org.tw", "idv.tw",
    "us.com", "us.org", "cn.com",
    "com.au", "net.au", "org.au",
    "co.nz", "net.nz", "org.nz"
}

def extract_root_domain(hostname):
    hostname = hostname.lower().strip().rstrip(".")
    if not hostname or "." not in hostname:
        return None
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', hostname):
        return None
    if ":" in hostname:
        hostname = hostname.split(":")[0]
    
    parts = hostname.split(".")
    if len(parts) < 2:
        return None
    
    if len(parts) >= 3:
        two_part = f"{parts[-2]}.{parts[-1]}"
        if two_part in MULTI_TLDS:
            return ".".join(parts[-3:])
    
    return ".".join(parts[-2:])

def clean_url_to_domains(url):
    if not url:
        return []
    url = url.strip().strip('"').strip("'").strip('\\').strip('|').strip('`')
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.netloc
        if ":" in hostname:
            hostname = hostname.split(":")[0]
        hostname = hostname.lower().strip()
        if not hostname:
            return []
        
        query_domains = []
        if parsed.query:
            params = urllib.parse.parse_qs(parsed.query)
            for k, vs in params.items():
                for v in vs:
                    if "http" in v or "." in v:
                        query_domains.extend(clean_url_to_domains(v))
                        
        root = extract_root_domain(hostname)
        return [(hostname, root)] + query_domains
    except Exception:
        return []

# Load all crawled data
extracted_records = [] # (hostname, root_domain, source_tag)

# 1. Raw GitHub & initial nav
with open("data/raw_fetched.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

for src, content in raw_data.items():
    urls = re.findall(r'https?://[a-zA-Z0-9\.\-_]+(?::\d+)?(?:/[^\s<>"\'\)\`\\\|]*)?', content)
    md_urls = re.findall(r'\[([^\]]*)\]\((https?://[^\)]+)\)', content)
    for title, u in md_urls:
        urls.append(u)
    for u in urls:
        for host, root in clean_url_to_domains(u):
            if root and root not in ALL_EXCLUDED:
                extracted_records.append((host, root, src))

# 2. apisou pages
with open("data/apisou_pages.json", "r", encoding="utf-8") as f:
    apisou_pages = json.load(f)

for src, content in apisou_pages.items():
    urls = re.findall(r'https?://[a-zA-Z0-9\.\-_]+(?::\d+)?(?:/[^\s<>"\'\)\`\\\|]*)?', content)
    for u in urls:
        for host, root in clean_url_to_domains(u):
            if root and root not in ALL_EXCLUDED:
                extracted_records.append((host, root, f"apisou detail"))

# 3. apiranking pages & redirects
with open("data/apiranking_pages.json", "r", encoding="utf-8") as f:
    apiranking_pages = json.load(f)

for src, content in apiranking_pages.items():
    urls = re.findall(r'https?://[a-zA-Z0-9\.\-_]+(?::\d+)?(?:/[^\s<>"\'\)\`\\\|]*)?', content)
    for u in urls:
        for host, root in clean_url_to_domains(u):
            if root and root not in ALL_EXCLUDED:
                extracted_records.append((host, root, f"apiranking"))

with open("data/apiranking_redirects.json", "r", encoding="utf-8") as f:
    redirects = json.load(f)

for path, dest in redirects.items():
    for host, root in clean_url_to_domains(dest):
        if root and root not in ALL_EXCLUDED:
            extracted_records.append((host, root, f"apiranking target"))

# Group by root domain
domain_data = {}
for host, root, src in extracted_records:
    # Filter out invalid domain patterns (e.g. ends with png, svg, txt, etc.)
    if any(root.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".svg", ".ico", ".css", ".js", ".json", ".md", ".webp"]):
        continue
    if root not in domain_data:
        domain_data[root] = {
            "hosts": set(),
            "sources": set(),
            "count": 0
        }
    domain_data[root]["hosts"].add(host)
    domain_data[root]["sources"].add(src)
    domain_data[root]["count"] += 1

print(f"Cleaned unique root domains: {len(domain_data)}")

# Sort alphabetically
sorted_domains = sorted(domain_data.keys())

# Build the Loon Rule-Set Content
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

loon_rules = []
loon_rules.append("# ==================================================================")
loon_rules.append("# Title: Third-Party AI API Proxy & Gateway Rule-Set for Loon")
loon_rules.append(f"# Updated: {now_str}")
loon_rules.append(f"# Total Rules: {len(sorted_domains)} Root Domains")
loon_rules.append("# Description: 第三方 AI API 中转站 / 代理站 / 路由网关分流规则集")
loon_rules.append("# Sources:")
loon_rules.append("#   - https://github.com/frank36512/aiapi")
loon_rules.append("#   - https://github.com/howardpen9/awesome-ai-api-proxy")
loon_rules.append("#   - https://github.com/Claws-ZH/awesome-ai-api")
loon_rules.append("#   - https://github.com/mn-api/awesome-ai-proxy")
loon_rules.append("#   - https://www.apisou.com/")
loon_rules.append("#   - https://aisitenav.com/")
loon_rules.append("#   - https://apiranking.com/")
loon_rules.append("#   - https://routerhubs.com/")
loon_rules.append("#   - https://howtok.net/")
loon_rules.append("# ==================================================================")
loon_rules.append("")

for root in sorted_domains:
    loon_rules.append(f"DOMAIN-SUFFIX,{root}")

output_rule_file = "AIProxy.list"
with open(output_rule_file, "w", encoding="utf-8") as f:
    f.write("\n".join(loon_rules) + "\n")

print(f"Generated {output_rule_file} with {len(sorted_domains)} rules.")

# Also generate a Lite version for top / verified proxies (multi-source verified)
lite_domains = [d for d in sorted_domains if len(domain_data[d]["sources"]) >= 2 or domain_data[d]["count"] >= 3]
loon_rules_lite = []
loon_rules_lite.append("# ==================================================================")
loon_rules_lite.append("# Title: Third-Party AI API Proxy & Gateway Rule-Set (Lite / High-Frequency)")
loon_rules_lite.append(f"# Updated: {now_str}")
loon_rules_lite.append(f"# Total Rules: {len(lite_domains)} Root Domains")
loon_rules_lite.append("# Description: 高频/多源收录的精选中转站分流规则集")
loon_rules_lite.append("# ==================================================================")
loon_rules_lite.append("")
for root in sorted(lite_domains):
    loon_rules_lite.append(f"DOMAIN-SUFFIX,{root}")

output_rule_lite = "AIProxy_Lite.list"
with open(output_rule_lite, "w", encoding="utf-8") as f:
    f.write("\n".join(loon_rules_lite) + "\n")

print(f"Generated {output_rule_lite} with {len(lite_domains)} rules.")

# Save full metadata for reference
meta_export = {
    "total_root_domains": len(sorted_domains),
    "generated_at": now_str,
    "domains": {
        d: {
            "subdomains": sorted(list(domain_data[d]["hosts"])),
            "sources": sorted(list(domain_data[d]["sources"])),
            "occurrences": domain_data[d]["count"]
        }
        for d in sorted_domains
    }
}
with open("data/domains_metadata.json", "w", encoding="utf-8") as f:
    json.dump(meta_export, f, ensure_ascii=False, indent=2)
