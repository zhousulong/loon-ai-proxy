import json
import re
import urllib.parse
import os

# Blacklist of generic / official / social / infra / documentation domains
EXCLUDE_DOMAINS = {
    # Official AI Providers
    "openai.com", "chatgpt.com", "anthropic.com", "claude.ai", "google.com", "googleapis.com", 
    "google.dev", "ai.google.dev", "aistudio.google.com", "gstatic.com", "x.ai", "grok.com",
    "deepseek.com", "zhipuai.cn", "bigmodel.cn", "baichuan-ai.com", "baichuanapi.com", 
    "moonshot.cn", "kimi.ai", "minimaxi.com", "minimax.chat", "stepfun.com", "01.ai", 
    "lingyiwanwu.com", "sensenova.cn", "xfyun.cn", "baidu.com", "baidubce.com", "aliyun.com", 
    "alibaba-inc.com", "tencent.com", "tencentcs.com", "cohere.com", "together.ai", "mistral.ai",
    "perplexity.ai", "groq.com", "cerebras.ai", "novita.ai", "fal.ai", "replicate.com",
    "stability.ai", "midjourney.com", "elevenlabs.io", "runwayml.com", "huggingface.co",
    "aws.amazon.com", "amazon.com", "azure.com", "microsoft.com",

    # Public platforms / code hosting / communities
    "github.com", "github.io", "githubusercontent.com", "gitlab.com", "gitee.com", "gitcode.com",
    "linux.do", "v2ex.com", "zhihu.com", "bilibili.com", "weibo.com", "qq.com", "weixin.qq.com",
    "t.me", "telegram.org", "discord.com", "discord.gg", "twitter.com", "x.com", "facebook.com",
    "youtube.com", "medium.com", "juejin.cn", "csdn.net", "sspai.com", "cnblogs.com", "nodeseek.com",

    # Infra / CDNs / Cloud providers / Analytics
    "cloudflare.com", "cloudflarestream.com", "workers.dev", "pages.dev", "vercel.app", "netlify.app",
    "render.com", "zeabur.app", "railway.app", "deno.dev", "supabase.co", "firebaseapp.com",
    "akamai.com", "fastly.com", "jsdelivr.net", "unpkg.com", "cdnjs.cloudflare.com",
    "googletagmanager.com", "google-analytics.com", "clarity.ms", "umami.is", "posthog.com",
    "schema.org", "w3.org", "shields.io", "badgen.net", "favicon.im", "apple.com", "play.google.com",
    "qiniu.com", "qiniup.com", "ucloud.cn", "compshare.cn",

    # Navigation / Aggregation sites themselves
    "apisou.com", "aisitenav.com", "apiranking.com", "routerhubs.com", "howtok.net",
    "star-history.com", "awesome.re", "opencompass.org.cn", "arena.ai", "kilo.ai",

    # Payment / Auth / Common Services
    "stripe.com", "alipay.com", "epay.me", "bufpay.com", "auth0.com", "clerk.dev", "clerk.com",
    "sentry.io", "crisp.chat", "intercom.io", "tawk.to"
}

# Multi-part TLDs commonly used
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
    # Check IP address
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', hostname):
        return None
    if ":" in hostname: # ipv6 or with port
        hostname = hostname.split(":")[0]
    
    parts = hostname.split(".")
    if len(parts) < 2:
        return None
    
    # Check 2-part suffix like .com.cn, .us.com
    if len(parts) >= 3:
        two_part = f"{parts[-2]}.{parts[-1]}"
        if two_part in MULTI_TLDS:
            return ".".join(parts[-3:])
    
    return ".".join(parts[-2:])

def clean_url_to_domains(url):
    if not url:
        return []
    url = url.strip().strip('"').strip("'").strip('\\').strip('|').strip('`')
    # If not starting with scheme, add https://
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
        
        # Check query parameters for embedded target domains (e.g. ?url=https%3A%2F%2F...)
        query_domains = []
        if parsed.query:
            params = urllib.parse.parse_qs(parsed.query)
            for k, vs in params.items():
                for v in vs:
                    if "http" in v or "." in v:
                        query_domains.extend(clean_url_to_domains(v))
                        
        root = extract_root_domain(hostname)
        return [(hostname, root)] + query_domains
    except Exception as e:
        return []

# Collect all URLs
all_extracted_domains = set() # (hostname, root_domain, source_desc)

# 1. GitHub & Initial raw
with open("data/raw_fetched.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

for src, content in raw_data.items():
    urls = re.findall(r'https?://[a-zA-Z0-9\.\-_]+(?::\d+)?(?:/[^\s<>"\'\)\`\\\|]*)?', content)
    # Also find markdown link patterns
    md_urls = re.findall(r'\[([^\]]*)\]\((https?://[^\)]+)\)', content)
    for title, u in md_urls:
        urls.append(u)
    for u in urls:
        for host, root in clean_url_to_domains(u):
            if root and root not in EXCLUDE_DOMAINS:
                all_extracted_domains.add((host, root, src))

# 2. apisou pages
with open("data/apisou_pages.json", "r", encoding="utf-8") as f:
    apisou_pages = json.load(f)

for src, content in apisou_pages.items():
    # Look for official website link in apisou detail page
    urls = re.findall(r'https?://[a-zA-Z0-9\.\-_]+(?::\d+)?(?:/[^\s<>"\'\)\`\\\|]*)?', content)
    for u in urls:
        for host, root in clean_url_to_domains(u):
            if root and root not in EXCLUDE_DOMAINS:
                all_extracted_domains.add((host, root, f"apisou: {src}"))

# 3. apiranking pages & redirects
with open("data/apiranking_pages.json", "r", encoding="utf-8") as f:
    apiranking_pages = json.load(f)

for src, content in apiranking_pages.items():
    urls = re.findall(r'https?://[a-zA-Z0-9\.\-_]+(?::\d+)?(?:/[^\s<>"\'\)\`\\\|]*)?', content)
    for u in urls:
        for host, root in clean_url_to_domains(u):
            if root and root not in EXCLUDE_DOMAINS:
                all_extracted_domains.add((host, root, f"apiranking: {src}"))

with open("data/apiranking_redirects.json", "r", encoding="utf-8") as f:
    redirects = json.load(f)

for path, dest in redirects.items():
    for host, root in clean_url_to_domains(dest):
        if root and root not in EXCLUDE_DOMAINS:
            all_extracted_domains.add((host, root, f"apiranking_redirect: {path}"))

print(f"Total raw (host, root) pairs extracted: {len(all_extracted_domains)}")

# Aggregate by root domain
root_map = {}
for host, root, src in all_extracted_domains:
    if root not in root_map:
        root_map[root] = {"hosts": set(), "sources": set()}
    root_map[root]["hosts"].add(host)
    root_map[root]["sources"].add(src)

print(f"Total unique root domains: {len(root_map)}")
print("Sample root domains (first 30):")
for r in sorted(list(root_map.keys()))[:30]:
    print(f"  {r} (subdomains: {list(root_map[r]['hosts'])[:3]})")
