import json

with open("data/domains_metadata.json", "r") as f:
    data = json.load(f)

domains = list(data["domains"].keys())

DOMESTIC_COMPANIES_KNOWN = {
    # Alibaba
    "aliyun.com", "alibaba-inc.com", "alibabacloud.com", "tongyi.aliyun.com", "dashscope.com", "modelscope.cn", "modelscope.com",
    # Baidu
    "baidu.com", "baidubce.com", "yiyan.baidu.com", "qianfan.com",
    # Tencent
    "tencent.com", "tencentcs.com", "hunyuan.tencent.com", "yuanbao.com",
    # ByteDance
    "bytedance.com", "volcengine.com", "doubao.com", "coze.cn", "coze.com", "zijieapi.com", "snssdk.com", "oceanengine.com",
    # Huawei
    "huawei.com", "huaweicloud.com",
    # DeepSeek
    "deepseek.com", "deepseek.cn",
    # Zhipu
    "zhipuai.cn", "bigmodel.cn", "chatglm.cn", "zhipu.ai",
    # Moonshot
    "moonshot.cn", "kimi.ai", "kimi.com",
    # MiniMax
    "minimaxi.com", "minimax.chat", "hailuoai.com", "hailuo.ai",
    # Baichuan
    "baichuan-ai.com", "baichuanapi.com", "baichuan-inc.com", "baixiaoying.com",
    # 01.AI
    "01.ai", "lingyiwanwu.com", "wanzhi.com",
    # StepFun
    "stepfun.com", "yuewen.cn", "stepchat.cn", "maopaoya.com",
    # SenseTime
    "sensetime.com", "sensenova.cn", "sensechat.cn",
    # iFlytek
    "xfyun.cn", "iflytek.com", "sparkdesk.cn", "xfyun.com",
    # Kunlun
    "tiangong.cn", "kunlun-inc.com", "tiangong.ai",
    # 360
    "360.com", "360.cn", "360.net",
    # NetEase
    "163.com", "netease.com", "fuxi.163.com", "youdao.com",
    # SiliconFlow
    "siliconflow.cn", "siliconflow.com",
    # Metaso
    "metaso.cn", "metaso.com",
    # ModelBest
    "modelbest.cn", "modelbest.com",
    # Langboat
    "langboat.com", "mengzi.com",
    # Shengshu / Vidu
    "shengshu-ai.com", "vidu.studio", "vidu.cn",
    # Infini-AI
    "infini-ai.com", "infini-ai.cn",
    # Telecoms
    "10086.cn", "189.cn", "ctyun.cn", "10010.com", "unicom.cn",
    # Apifox / domestic tools
    "apifox.cn", "apifox.com"
}

# Find any matching or domestic .cn domains
domestic_domains = []
for d in domains:
    if d.endswith(".cn") or d in DOMESTIC_COMPANIES_KNOWN:
        domestic_domains.append(d)

print(f"Total domestic domains to remove: {len(domestic_domains)}")
for d in domestic_domains:
    print(f"  {d}")
