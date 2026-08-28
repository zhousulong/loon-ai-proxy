# 第三方 AI API / 中转站 Loon 分流规则集

本规则集汇总了全网各大第三方 AI API 中转平台、转售网关与代理站的域名，专门用于在 **Loon**、**Surge**、**Shadowrocket**、**Clash** 等代理工具中进行独立分流配置（例如：将第三方中转站请求分流至「直连 DIRECT」或「特定低延迟中转节点」，避免与官方 OpenAI / Anthropic 分流规则产生冲突）。

---

## 规则集文件列表

| 文件名 | 规则数量 | 适用场景 | 远程订阅链接 (Raw) |
| :--- | :--- | :--- | :--- |
| **[`AIProxy.list`](./AIProxy.list)** | **883 条** | 全量版（收录最全，已剔除国内平台及 `.cn` 域名） | `https://raw.githubusercontent.com/zhousulong/loon-ai-proxy/main/AIProxy.list` |
| **[`AIProxy_Lite.list`](./AIProxy_Lite.list)** | **458 条** | 精选版（高频/多源收录，已剔除国内平台及 `.cn` 域名） | `https://raw.githubusercontent.com/zhousulong/loon-ai-proxy/main/AIProxy_Lite.list` |

---

## 过滤与清洗标准

1. **已剔除全部国内平台与国内域名**：
   - **国家顶级域名**：全部以 `.cn`（包括 `.com.cn`、`.net.cn`、`.org.cn` 等）结尾的域名均已剔除；
   - **国内大模型及云厂商**：百度千帆/文心、阿里通义/DashScope/魔搭、腾讯混元、字节火山引擎/豆包/扣子、华为盘古、DeepSeek、智谱 GLM、月之暗面 Kimi、MiniMax、百川智能、零一万物、阶跃星辰、商汤日日新、讯飞星火、天工 AI、360智脑、网易伏羲、硅基流动 (SiliconFlow)、秘塔科技 (Metaso)、面壁智能 (ModelBest)、澜舟科技、无问芯穹、中国移动/电信/联通等。
2. **已剔除官方大模型直连接口**：
   - OpenAI、Anthropic Claude、Google Gemini、xAI Grok、Perplexity、Mistral、Cohere、Together AI、Groq 等（请使用官方专属规则分流）。
3. **已剔除公共基础设施与社交平台**：
   - GitHub、GitLab、Vercel、Cloudflare、Linux.do、V2EX、知乎、Bilibili、微信、支付宝、各大统计分析平台与支付网关。

---

## Loon 配置与使用指南

### 方式一：远程规则集引入（推荐）

在 Loon 配置文件的 `[Remote Rule]` 节点下添加：

```ini
[Remote Rule]
# 第三方 AI 中转站分流（全量版，策略组指向 AI-Proxy 或 DIRECT）
https://raw.githubusercontent.com/zhousulong/loon-ai-proxy/main/AIProxy.list, policy=AI-Proxy, tag=AI-Proxy, enabled=true
```

### 方式二：直接在 Loon 配置文件中添加策略组与规则

#### 1. 新增策略组 `[Proxy Group]`
```ini
[Proxy Group]
# 第三方中转站策略组：根据自身网络情况选择直连 (DIRECT) 或指定节点
AI-Proxy = select, DIRECT, PROXY, 香港节点, 日本节点, 新加坡节点, node-select=false
```

#### 2. 配置规则分流顺序 `[Rule]`
> **注意**：建议将 `AIProxy.list` 放置在官方 `OpenAI` / `Anthropic` 规则之后，以保证官方 API 请求走官方专属代理，而第三方中转域名走 `AI-Proxy` 策略。

```ini
[Rule]
# 1. 官方 AI 服务规则（走官方专属代理）
# RULE-SET,https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/OpenAI/OpenAI.list,OpenAI
# RULE-SET,https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Claude/Claude.list,Claude

# 2. 第三方 AI 中转站规则（走直连或特定中转节点）
RULE-SET,https://raw.githubusercontent.com/zhousulong/loon-ai-proxy/main/AIProxy.list,AI-Proxy

# 3. 最终兜底规则
FINAL,DIRECT
```

---

## 规则更新维护

项目内置了自动化提取与更新脚本：
- `python3 fetch_sources.py`：抓取各数据源
- `python3 crawl_deep.py`：解析深层详情与跳转链
- `python3 build_rules.py`：清洗、验证 TLD 并重新生成分流列表
