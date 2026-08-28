import json
import re
import urllib.parse
from datetime import datetime

# Load valid IANA TLDs
with open("data/iana_tlds.json", "r") as f:
    VALID_TLDS = set(json.load(f))

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

# Excluded domains: Official AI services, Big Tech, Code Hosting, CDNs, Navigators, Domestic Platforms, etc.
EXCLUDE_DOMAINS = {
    # Placeholders & samples
    "yourdomain.com", "example.com", "example.org", "example.net", "test.com", "localhost", "domain.com",

    # Official Foreign AI Providers
    "openai.com", "chatgpt.com", "oaistatic.com", "oaiusercontent.com", "microsoft.com", "azure.com", "bing.com", "copilot.microsoft.com",
    "anthropic.com", "claude.ai",
    "google.com", "googleapis.com", "google.dev", "ai.google.dev", "aistudio.google.com", "gstatic.com", "googleusercontent.com", "gemini.google.com",
    "x.ai", "grok.com", "meta.ai", "llama.com", "amazon.com", "amazonaws.com", "aws.amazon.com", "apple.com", "icloud.com",
    "cohere.com", "together.ai", "mistral.ai", "perplexity.ai", "groq.com", "cerebras.ai", "novita.ai",
    "fal.ai", "replicate.com", "stability.ai", "midjourney.com", "elevenlabs.io", "runwayml.com", "huggingface.co",
    "ai21.com", "sambanova.ai", "fireworks.ai", "anyscale.com", "lepton.ai", "scale.com",

    # Domestic Big Tech & Official AI / Cloud Platforms (All Chinese platforms)
    "baidu.com", "baidubce.com", "yiyan.baidu.com", "qianfan.com", "wenxin.com",
    "aliyun.com", "alibaba-inc.com", "alibabacloud.com", "tongyi.aliyun.com", "dashscope.com", "modelscope.cn", "modelscope.com", "tongyi.com",
    "tencent.com", "tencentcs.com", "hunyuan.tencent.com", "yuanbao.com", "myqcloud.com",
    "bytedance.com", "volcengine.com", "doubao.com", "coze.cn", "coze.com", "zijieapi.com", "snssdk.com", "oceanengine.com",
    "huawei.com", "huaweicloud.com",
    "deepseek.com", "deepseek.cn",
    "zhipuai.cn", "bigmodel.cn", "chatglm.cn", "zhipu.ai",
    "moonshot.cn", "kimi.ai", "kimi.com",
    "minimaxi.com", "minimax.chat", "hailuoai.com", "hailuo.ai",
    "baichuan-ai.com", "baichuanapi.com", "baichuan-inc.com", "baixiaoying.com",
    "01.ai", "lingyiwanwu.com", "wanzhi.com", "01wanwu.cn",
    "stepfun.com", "stepfun.cn", "yuewen.cn", "stepchat.cn", "maopaoya.com",
    "sensetime.com", "sensenova.cn", "sensechat.cn",
    "xfyun.cn", "iflytek.com", "sparkdesk.cn", "xfyun.com",
    "tiangong.cn", "kunlun-inc.com", "tiangong.ai",
    "360.com", "360.cn", "360.net", "so.com",
    "163.com", "netease.com", "fuxi.163.com", "youdao.com",
    "siliconflow.cn", "siliconflow.com",
    "metaso.cn", "metaso.com",
    "modelbest.cn", "modelbest.com",
    "langboat.com", "mengzi.com",
    "shengshu-ai.com", "pixverse.ai", "vidu.studio", "vidu.cn",
    "infini-ai.com", "infini-ai.cn",
    "10086.cn", "189.cn", "ctyun.cn", "10010.com", "unicom.cn", "ecloud.10086.cn",
    "apifox.cn", "apifox.com", "ucloud.cn", "compshare.cn", "scnet.cn",

    # Public platforms / code hosting / communities
    "github.com", "github.io", "githubusercontent.com", "gitlab.com", "gitee.com", "gitcode.com", "gitlink.org.cn", "coding.net",
    "linux.do", "v2ex.com", "zhihu.com", "bilibili.com", "weibo.com", "qq.com", "weixin.qq.com", "mp.weixin.qq.com",
    "t.me", "telegram.org", "discord.com", "discord.gg", "twitter.com", "x.com", "facebook.com", "youtube.com",
    "medium.com", "juejin.cn", "csdn.net", "sspai.com", "cnblogs.com", "nodeseek.com", "hostloc.com", "v2nodes.com",
    "segmentfault.com", "infoq.cn", "oschina.net", "cnbeta.com.tw", "ithome.com", "smzdm.com",

    # Infra / CDNs / Cloud providers / Analytics / Navigators / Tools
    "cloudflare.com", "cloudflarestream.com", "workers.dev", "pages.dev", "vercel.app", "netlify.app",
    "render.com", "zeabur.app", "railway.app", "deno.dev", "supabase.co", "firebaseapp.com",
    "akamai.com", "fastly.com", "jsdelivr.net", "unpkg.com", "cdnjs.cloudflare.com", "bootcdn.cn",
    "googletagmanager.com", "google-analytics.com", "clarity.ms", "umami.is", "posthog.com", "plausible.io",
    "schema.org", "w3.org", "shields.io", "badgen.net", "favicon.im", "iconify.design", "fontawesome.com",
    "sentry.io", "crisp.chat", "intercom.io", "tawk.to", "51.la", "cnzz.com", "tongji.baidu.com",
    "apisou.com", "aisitenav.com", "apiranking.com", "routerhubs.com", "howtok.net",
    "star-history.com", "awesome.re", "opencompass.org.cn", "arena.ai", "kilo.ai",
    "stripe.com", "alipay.com", "epay.me", "bufpay.com", "auth0.com", "clerk.dev", "clerk.com",
    "paypal.com", "wechat.com", "tenpay.com", "zapier.com",
    "sogou.com", "duckduckgo.com", "wikipedia.org", "notion.site", "notion.so",
    "feishu.cn", "larksuite.com", "yuque.com", "wolai.com", "hubspot.com"
}

def is_domestic(domain):
    # Rule 1: Any .cn TLD (com.cn, net.cn, org.cn, edu.cn, *.cn)
    if domain.endswith(".cn"):
        return True
    # Rule 2: Explicitly listed domestic companies
    if domain in EXCLUDE_DOMAINS:
        return True
    return False

def is_valid_domain(d):
    if not d or len(d) > 255 or " " in d or "/" in d or "\\" in d or ":" in d or "@" in d:
        return False
    parts = d.split(".")
    if len(parts) < 2:
        return False
    # Check TLD
    tld = parts[-1].lower()
    if tld not in VALID_TLDS:
        return False
    # Check valid label chars
    for p in parts:
        if not p or len(p) > 63:
            return False
        if not re.match(r'^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$', p):
            return False
    return True

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
    
    # Check multi-part TLD
    if len(parts) >= 3:
        two_part = f"{parts[-2]}.{parts[-1]}"
        if two_part in MULTI_TLDS:
            candidate = ".".join(parts[-3:])
            if is_valid_domain(candidate):
                return candidate
    
    candidate = ".".join(parts[-2:])
    if is_valid_domain(candidate):
        return candidate
    return None

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

records = []

# 1. GitHub & Initial raw
with open("data/raw_fetched.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

for src, content in raw_data.items():
    urls = re.findall(r'https?://[a-zA-Z0-9\.\-_]+(?::\d+)?(?:/[^\s<>"\'\)\`\\\|]*)?', content)
    md_urls = re.findall(r'\[([^\]]*)\]\((https?://[^\)]+)\)', content)
    for title, u in md_urls:
        urls.append(u)
    for u in urls:
        for host, root in clean_url_to_domains(u):
            if root and not is_domestic(root) and root not in EXCLUDE_DOMAINS and is_valid_domain(root):
                records.append((host, root, src))

# 2. apisou pages
with open("data/apisou_pages.json", "r", encoding="utf-8") as f:
    apisou_pages = json.load(f)

for src, content in apisou_pages.items():
    urls = re.findall(r'https?://[a-zA-Z0-9\.\-_]+(?::\d+)?(?:/[^\s<>"\'\)\`\\\|]*)?', content)
    for u in urls:
        for host, root in clean_url_to_domains(u):
            if root and not is_domestic(root) and root not in EXCLUDE_DOMAINS and is_valid_domain(root):
                records.append((host, root, f"apisou detail"))

# 3. apiranking pages & redirects
with open("data/apiranking_pages.json", "r", encoding="utf-8") as f:
    apiranking_pages = json.load(f)

for src, content in apiranking_pages.items():
    urls = re.findall(r'https?://[a-zA-Z0-9\.\-_]+(?::\d+)?(?:/[^\s<>"\'\)\`\\\|]*)?', content)
    for u in urls:
        for host, root in clean_url_to_domains(u):
            if root and not is_domestic(root) and root not in EXCLUDE_DOMAINS and is_valid_domain(root):
                records.append((host, root, f"apiranking"))

with open("data/apiranking_redirects.json", "r", encoding="utf-8") as f:
    redirects = json.load(f)

for path, dest in redirects.items():
    for host, root in clean_url_to_domains(dest):
        if root and not is_domestic(root) and root not in EXCLUDE_DOMAINS and is_valid_domain(root):
            records.append((host, root, f"apiranking target"))

# Group by root domain
domain_data = {}
for host, root, src in records:
    if root not in domain_data:
        domain_data[root] = {
            "hosts": set(),
            "sources": set(),
            "count": 0
        }
    domain_data[root]["hosts"].add(host)
    domain_data[root]["sources"].add(src)
    domain_data[root]["count"] += 1

sorted_domains = sorted(domain_data.keys())
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Write AIProxy.list
rule_lines = [
    "# ==================================================================",
    "# 规则名称: 第三方 AI API 中转与代理分流规则 (AIProxy.list - 纯海外/免翻分流版)",
    f"# 更新时间: {now_str}",
    f"# 包含域名: {len(sorted_domains)} 个独立中转服务商根域名",
    "# 过滤说明: 已剔除全部国内大厂、国内AI平台及全部 .cn 域名",
    "# 适用客户端: Loon / Surge / Shadowrocket / Clash 等",
    "# 数据来源聚合:",
    "#   - GitHub: frank36512/aiapi",
    "#   - GitHub: howardpen9/awesome-ai-api-proxy",
    "#   - GitHub: Claws-ZH/awesome-ai-api",
    "#   - GitHub: mn-api/awesome-ai-proxy",
    "#   - 导航站: https://www.apisou.com/",
    "#   - 导航站: https://aisitenav.com/",
    "#   - 导航站: https://apiranking.com/",
    "#   - 导航站: https://routerhubs.com/",
    "#   - 导航站: https://howtok.net/",
    "# ==================================================================",
    ""
]

for d in sorted_domains:
    rule_lines.append(f"DOMAIN-SUFFIX,{d}")

with open("AIProxy.list", "w", encoding="utf-8") as f:
    f.write("\n".join(rule_lines) + "\n")

# Write AIProxy_Lite.list (High confidence / multiple citations)
lite_domains = sorted([d for d in sorted_domains if len(domain_data[d]["sources"]) >= 2 or domain_data[d]["count"] >= 3])
lite_lines = [
    "# ==================================================================",
    "# 规则名称: 精选高频第三方 AI API 中转分流规则 (AIProxy_Lite.list - 纯海外/免翻分流版)",
    f"# 更新时间: {now_str}",
    f"# 包含域名: {len(lite_domains)} 个高频/多源收录中转站根域名",
    "# 过滤说明: 已剔除全部国内大厂、国内AI平台及全部 .cn 域名",
    "# 适用客户端: Loon / Surge / Shadowrocket / Clash 等",
    "# ==================================================================",
    ""
]
for d in lite_domains:
    lite_lines.append(f"DOMAIN-SUFFIX,{d}")

with open("AIProxy_Lite.list", "w", encoding="utf-8") as f:
    f.write("\n".join(lite_lines) + "\n")

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

print(f"Final Count after removing domestic platforms -> AIProxy.list: {len(sorted_domains)}, AIProxy_Lite.list: {len(lite_domains)}")
