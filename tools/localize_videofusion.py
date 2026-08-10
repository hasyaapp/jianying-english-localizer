#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import plistlib
import re
from pathlib import Path


ROOT = Path("VideoFusion-macOS-English.app")
CAPCUT = Path("/Applications/CapCut.app")
HAN_RE = re.compile(r"[\u3400-\u9fff]")


COMMON = {
    "剪映专业版": "Jianying Pro",
    "剪映": "Jianying",
    "剪映云": "Jianying Cloud",
    "请允许“剪映专业版”访问您的摄像头，从而为您提供录制功能": "Allow Jianying Pro to access your camera for recording.",
    "请允许“剪映专业版”访问您的麦克风，从而为您提供录音功能": "Allow Jianying Pro to access your microphone for recording.",
    "确定": "OK",
    "取消": "Cancel",
    "关闭": "Close",
    "保存": "Save",
    "导出": "Export",
    "导入": "Import",
    "删除": "Delete",
    "编辑": "Edit",
    "添加": "Add",
    "更多": "More",
    "设置": "Settings",
    "登录": "Log in",
    "退出登录": "Log out",
    "重试": "Retry",
    "完成": "Done",
    "下一步": "Next",
    "上一步": "Back",
    "知道了": "Got it",
    "我了解了": "Got it",
    "开启": "On",
    "会员": "Membership",
    "草稿": "Draft",
    "云空间": "Cloud space",
    "字幕": "Captions",
    "文本": "Text",
    "文字": "Text",
    "音频": "Audio",
    "视频": "Video",
    "贴纸": "Stickers",
    "特效": "Effects",
    "滤镜": "Filters",
    "调节": "Adjust",
    "模板": "Template",
    "素材": "Media",
    "收藏": "Favorites",
    "搜索": "Search",
    "下载": "Download",
    "上传": "Upload",
    "发布": "Publish",
    "分享": "Share",
}

H5_COMMON = {
    "请求发生异常，建议重启软件后重试。": "Request failed. Restart the app and try again.",
    "输入字符最多不超过5000字": "Input must not exceed 5000 characters",
    "输入字符最多不超过": "Input must not exceed ",
    "你希望怎么优化这段文案": "How would you like to improve this copy?",
    "描述修改": "Describe changes",
    "润色": "Polish",
    "扩写": "Expand",
    "缩写": "Shorten",
    "生成结果": "Generated result",
    "复制": "Copy",
    "重新生成": "Regenerate",
    "喜欢": "Like",
    "不喜欢": "Dislike",
    "插入": "Insert",
    "替换": "Replace",
    "深度思考中": "Deep thinking...",
    "思考结果": "Thinking result",
    "已停止生成": "Generation stopped",
    "停止生成": "Stop generating",
    "输入文案后，可以通过润色、扩写、缩写或改写描述，提升文案质量": "After entering copy, use Polish, Expand, Shorten, or describe a rewrite to improve it.",
    "请输入标题": "Enter title",
    "上一个版本": "Previous version",
    "下一个版本": "Next version",
    "清空": "Clear",
    "智能分割字幕": "Smart subtitle splitting",
    "配音选择": "Voice selection",
    "添加到轨道": "Add to track",
    "改写上述文案内容": "Rewrite the copy above",
    "解说角度": "Narration angle",
    "画外旁白": "Voice-over narration",
    "出镜解说": "On-camera narration",
    "写作风格": "Writing style",
    "平铺直叙": "Straight narration",
    "轻松口语化": "Casual spoken style",
    "辛辣吐槽": "Sharp commentary",
    "短剧爽文": "Short-drama punchy style",
    "第一人称独白": "First-person monologue",
    "口播时长": "Voice-over duration",
    "无限制": "No limit",
    "1分钟以下": "Under 1 minute",
    "1~3分钟": "1-3 minutes",
    "3分钟以上": "Over 3 minutes",
    "（选填）也可补充更多要求": "(Optional) Add more requirements",
    "如果对解说不满意，可点击此处重新生成。新生成的文案将拼接到原文案后面": "If you are not satisfied with the narration, click here to regenerate it. The new copy will be appended to the original.",
    "如果对解说不满意，可点击此处重新生成。新生成的文案将替换原文案": "If you are not satisfied with the narration, click here to regenerate it. The new copy will replace the original.",
    "试试用Ai生成解说": "Try generating narration with AI",
    "音频轨道": "Audio track",
    "本地导入": "Local import",
    "语速": "Speed",
    "正在理解素材...": "Analyzing media...",
    "输入解说要求，如“剪成1分钟的剧情解说，突出爽点”": "Enter narration requirements, such as \"cut into a 1-minute story commentary and highlight the key moments\"",
    "也可直接输入解说词或上传「解说音频」": "You can also enter narration text directly or upload \"narration audio\"",
    "输入可用于剪辑参考的口播稿、脚本或具体剪辑要求，如“筛选关键信息，时长控制在1分钟内”": "Enter a voice-over draft, script, or editing requirements for reference, such as \"select key information and keep it within 1 minute\"",
    "输入文稿": "Enter script",
    "点击查看教程": "View tutorial",
    "「智能解说粗剪」使用指南": "\"Smart Narration Rough Cut\" guide",
    "素材静音，添加解说": "Mute media and add narration",
    "配音解说": "Voice narration",
    "保留素材原声": "Keep original media audio",
    "原声剪辑": "Original audio edit",
    "网络错误，请重试": "Network error. Try again.",
    "生成失败，请重试": "Generation failed. Try again.",
    "生成解说稿": "Generate narration script",
    "解说录音": "Narration recording",
    "已上传音频，无需输入文案": "Audio uploaded. No copy input needed.",
    "已上传音频，无需使用Ai朗读": "Audio uploaded. AI reading is not needed.",
    "解说小美": "Narration Xiaomei",
    "修改语速": "Change speed",
    "帮写中...": "Writing...",
    "AI 写解说": "AI writes narration",
    "正在生成解说，请稍候": "Generating narration. Please wait.",
    "字数已超上限": "Character limit exceeded",
    "开始粗剪": "Start rough cut",
    "今天": "Today",
    "本周": "This week",
    "更早": "Earlier",
    "换一批": "Refresh",
    "对话列表": "Conversation list",
    "新建对话": "New conversation",
    "主题生文": "Generate by topic",
    "帮我提取这个Video中的文案": "Extract the copy from this video",
    "帮我提取这个Audio中的文案": "Extract the copy from this audio",
    "帮我提取这个链接中的文案": "Extract the copy from this link",
    "帮我提取这个Video中的摘要": "Extract a summary from this video",
    "今天想写点什么呢？": "What would you like to write today?",
    "今天想写点什么": "What would you like to write today?",
    "我能帮你查询知识、快速生文、优化及总结文案，有任何需求都可以告诉我": "I can look up information, generate copy quickly, refine text, and summarize copy. Tell me what you need.",
    "如小米手环，卖点大屏，轻薄。": "Example: Xiaomi Band, large screen selling point, lightweight.",
    "如爱情，话题保持新鲜感，经营技巧。": "Example: love, keeping things fresh, relationship tips.",
    "如梦想，话题力量，与现实的差距。": "Example: dreams, motivation, and the gap with reality.",
    "如番茄炒蛋，不同口味做法。": "Example: tomato scrambled eggs, different flavors and methods.",
    "如长沙米粉，必去的店，不同吃法。": "Example: Changsha rice noodles, must-visit shops, different ways to eat.",
    "如好用的厨房清洁用品，挑选方法，评测特点。": "Example: useful kitchen cleaning products, how to choose, review highlights.",
    "如新疆，文化，风景。": "Example: Xinjiang, culture, scenery.",
    "写作助理": "Writing assistant",
    "思考中": "Thinking",
    "引用": "Quote",
    "需要引用Text框的内容吗？": "Do you need to quote the text box content?",
    "此内容可能存在安全风险，请重新提问。": "This content may have safety risks. Please ask again.",
    "根据 ${length} 篇内容总结如下：": "Summary based on ${length} items:",
    "如果对解说不满意，可点击此处Regenerate。新生成的文案将覆盖原文案": "If you are not satisfied with the narration, click here to regenerate it. The new copy will replace the original.",
    "Add到Text框": "Add to text box",
    "字`": " characters`",
    "篇内容": " items",
    "上午": "AM",
    "下午": "PM",
    "中午": "Noon",
    "凌晨": "Early morning",
    "早上": "Morning",
    "晚上": "Evening",
    "全屏": "Full screen",
    "几秒": "A few seconds",
    "刚刚": "Just now",
    "前往": "Go to",
    "失败": "Failed",
    "展开": "Expand",
    "开始": "Start",
    "折叠": "Collapse",
    "放大": "Zoom in",
    "歌词": "Lyrics",
    "此刻": "Now",
    "缩小": "Zoom out",
    "返回": "Back",
    "重置": "Reset",
    "链接": "Link",
    "页码": "Page number",
    "预览": "Preview",
    "%s内": "within %s",
    "%s前": "%s ago",
    "1 天": "1 day",
    "1 年": "1 year",
    "上一页": "Previous page",
    "下一页": "Next page",
    "加载中": "Loading",
    "条/页": "items/page",
    "%d 天": "%d days",
    "%d 年": "%d years",
    "1 个月": "1 month",
    "1 分钟": "1 minute",
    "1 小时": "1 hour",
    "其他原因": "Other reason",
    "历史对话": "Conversation history",
    "原始尺寸": "Original size",
    "反馈建议": "Feedback",
    "向右旋转": "Rotate right",
    "向左旋转": "Rotate left",
    "开始时间": "Start time",
    "思考过程": "Thinking process",
    "提交反馈": "Submit feedback",
    "点击升序": "Click for ascending order",
    "点击降序": "Click for descending order",
    "结束时间": "End time",
    "选择日期": "Select date",
    "选择时间": "Select time",
    "%d 个月": "%d months",
    "%d 分钟": "%d minutes",
    "%d 小时": "%d hours",
    "内容不安全": "Unsafe content",
    "反馈已提交": "Feedback submitted",
    "已Copy": "Copied",
    "结果不正确": "Incorrect result",
    "结果质量差": "Low quality result",
    "请选择时间": "Select time",
    "${a}天前": "${a} days ago",
    "${l}天前": "${l} days ago",
    "加载历史对话": "Loading conversation history",
    "共 {0} 条": "{0} items total",
    "已展示全部数据": "All data displayed",
    "第 {0} 页": "Page {0}",
    "请选择一个主题": "Select a topic",
    "Cancel排序": "Cancel sorting",
    "向前 {0} 页": "Back {0} pages",
    "向后 {0} 页": "Forward {0} pages",
    "点击Upload": "Click to upload",
    "YYYY年M月D日": "MMM D, YYYY",
    "如写一首毕业季的歌": "Example: write a graduation season song",
    "期望是 `true`": "Expected `true`",
    "请输入正确的链接格式": "Enter a valid link format",
    "服务器繁忙，请稍后再试": "Server is busy. Try again later.",
    "期望是 `false`": "Expected `false`",
    "正在计算预计Done时间": "Calculating estimated completion time",
    "#{field} 是必填项": "#{field} is required",
    "日_一_二_三_四_五_六": "Sun_Mon_Tue_Wed_Thu_Fri_Sat",
    "释放文件并开始Upload": "Release the file to start upload",
    "Upload音Video文件": "Upload audio or video file",
    "如欧洲，必去路线，住宿选择。": "Example: Europe, must-visit routes, accommodation choices.",
    "我可以帮你生成各种主题的歌曲": "I can help you generate songs on many themes.",
    "YYYY年M月D日 HH:mm": "MMM D, YYYY HH:mm",
    "YYYY年M月D日Ah点mm分": "MMM D, YYYY h:mm A",
    "`#{field}` 不是对象": "`#{field}` is not an object",
    "`#{value}` 不是正数": "`#{value}` is not positive",
    "`#{value}` 不是负数": "`#{value}` is not negative",
    "`#{field}` 不是空数组": "`#{field}` is not an empty array",
    "`#{value}` 必须全大写": "`#{value}` must be uppercase",
    "`#{value}` 必须全小写": "`#{value}` must be lowercase",
    "字符数必须是 #{length}": "Character count must be #{length}",
    "点击或拖拽文件到此处Upload": "Click or drag files here to upload",
    "`#{field}` 不等于期望值": "`#{field}` does not equal the expected value",
    "你可以继续提问，或跟我说On新对话": "You can keep asking, or start a new conversation with me.",
    "你可以继续提问，或跟你来说On新对话": "You can keep asking, or start a new conversation.",
    "#{field} 不是合法的对象类型": "#{field} is not a valid object type",
    "#{field} 不是合法的布尔类型": "#{field} is not a valid boolean type",
    "#{field} 不是合法的数字类型": "#{field} is not a valid number type",
    "#{field} 不是合法的数组类型": "#{field} is not a valid array type",
    "#{field} 不是合法的邮箱地址": "#{field} is not a valid email address",
    "Delete后，聊天记录将不可恢复。": "After deletion, chat history cannot be restored.",
    "Network error请检查网络": "Network error. Check your connection.",
    "`#{field}` 不包含必须字段": "`#{field}` does not contain required fields",
    "【${e.title}文案】${i}": "[${e.title} copy] ${i}",
    "如周末快乐日常，充实时光，温馨瞬间。": "Example: happy weekend daily life, fulfilling time, warm moments.",
    "请粘贴抖音、头条或西瓜Video链接": "Paste a Douyin, Toutiao, or Xigua video link",
    "YYYY年M月D日dddd HH:mm": "dddd, MMM D, YYYY HH:mm",
    "YYYY年M月D日ddddAh点mm分": "dddd, MMM D, YYYY h:mm A",
    "字符数最多为 #{maxLength}": "Character count must be at most #{maxLength}",
    "字符数最少为 #{minLength}": "Character count must be at least #{minLength}",
    "#{field} 不是合法的 IP 地址": "#{field} is not a valid IP address",
    "#{field} 不是合法的Text类型": "#{field} is not a valid text type",
    "周日_周一_周二_周三_周四_周五_周六": "Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday",
    "#{field} 不是合法的 url 地址": "#{field} is not a valid URL",
    "昨天 ${a.format(\"HH:mm\")}": "Yesterday ${a.format(\"HH:mm\")}",
    "昨天 ${o.format(\"HH:mm\")}": "Yesterday ${o.format(\"HH:mm\")}",
    "昨天 ${r.format(\"HH:mm\")}": "Yesterday ${r.format(\"HH:mm\")}",
    "补充Describe your problem": "Describe your problem",
    "#{field} 不包含 #{includes}": "#{field} does not include #{includes}",
    "#{field} 不等于 #{deepEqual}": "#{field} does not equal #{deepEqual}",
    "`#{value}` 不等于 `#{equal}`": "`#{value}` does not equal `#{equal}`",
    "`#{value}` 大于最大值 `#{max}`": "`#{value}` is greater than max `#{max}`",
    "`#{value}` 小于最小值 `#{min}`": "`#{value}` is less than min `#{min}`",
    "`#{field}` 个数不等于 #{length}": "`#{field}` count does not equal #{length}",
    "`#{value}` 不符合模式 #{pattern}": "`#{value}` does not match pattern #{pattern}",
    "星期日_星期一_星期二_星期三_星期四_星期五_星期六": "Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday",
    "Copywriting import n要求，如主题，风格": "Copywriting import requirements, such as theme and style",
    "`#{field}` 个数最多为 #{maxLength}": "`#{field}` count must be at most #{maxLength}",
    "`#{field}` 个数最少为 #{minLength}": "`#{field}` count must be at least #{minLength}",
    "`#{value}` 不在 `#{min} ~ #{max}` 范围内": "`#{value}` is outside the `#{min} ~ #{max}` range",
    "一月_二月_三月_四月_五月_六月_七月_八月_九月_十月_十一月_十二月": "January_February_March_April_May_June_July_August_September_October_November_December",
    "1月_2月_3月_4月_5月_6月_7月_8月_9月_10月_11月_12月": "Jan_Feb_Mar_Apr_May_Jun_Jul_Aug_Sep_Oct_Nov_Dec",
    "我可以帮助你查询知识、生成内容、优化和总结文案、Search抖音Video等，有任何需求都可以随时告诉我": "I can help you look up information, generate content, refine and summarize copy, search Douyin videos, and more. Tell me what you need.",
    "权益对比": "Benefits comparison",
    "订阅服务": "Subscription service",
    "定制数字人": "Custom digital human",
    "发票管理": "Invoice management",
    "联合会员": "Joint membership",
}

VOICE_NAMES = {
    "水果舞曲": "Fruit Dance",
    "康康舞曲": "Can-Can Dance",
    "康定情歌": "Kangding Love Song",
    "心灵鸡汤": "Inspirational",
    "娱乐扒妹": "Entertainment Host",
    "甜美解说": "Sweet Narrator",
    "春日甜妹": "Spring Sweet Girl",
    "歌唱女王": "Singing Queen",
    "摇滚男生": "Rock Male",
    "情歌王": "Love Song King",
    "歌唱达人": "Singing Expert",
    "激扬男声": "Energetic Male",
    "甜美女孩": "Sweet Girl",
    "春节甜妹": "Spring Festival Sweet Girl",
    "清新歌手": "Fresh Singer",
    "广西表哥": "Guangxi Cousin",
    "粤语男声": "Cantonese Male",
    "天津小哥": "Tianjin Guy",
    "河南大叔": "Henan Uncle",
    "西安掌柜": "Xi'an Shopkeeper",
    "东北老铁": "Northeast Buddy",
    "重庆小伙": "Chongqing Guy",
    "台湾女生": "Taiwanese Female",
    "动漫小新": "Anime Xiaoxin",
    "动漫海绵": "Anime Sponge",
    "亲切女声": "Friendly Female",
    "知性女声": "Intellectual Female",
    "新闻女声": "News Female",
    "温柔淑女": "Gentle Lady",
    "小萝莉": "Little Girl",
    "小姐姐": "Young Lady",
    "知识讲解": "Knowledge Explainer",
    "新闻男声": "News Male",
    "阳光男生": "Sunny Male",
    "雅痞大叔": "Stylish Uncle",
    "说唱小哥": "Rap Guy",
    "萌娃": "Cute Child",
}


def po_unescape(s: str) -> str:
    return ast.literal_eval(s)


def po_escape(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def split_entries(text: str) -> list[str]:
    entries: list[str] = []
    cur: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            if cur:
                entries.append("\n".join(cur))
                cur = []
            continue
        cur.append(line)
    if cur:
        entries.append("\n".join(cur))
    return entries


def field_value(entry: str, field: str) -> str | None:
    lines = entry.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(field + " "):
            out.append(po_unescape(line[len(field) + 1 :]))
            i += 1
            while i < len(lines) and lines[i].startswith('"'):
                out.append(po_unescape(lines[i]))
                i += 1
            return "".join(out)
        i += 1
    return None


def read_po(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for entry in split_entries(path.read_text(encoding="utf-8")):
        msgid = field_value(entry, "msgid")
        msgstr = field_value(entry, "msgstr")
        if msgid is not None and msgstr is not None:
            mapping[msgid] = msgstr
    return mapping


def humanize_key(key: str) -> str:
    if not key:
        return ""
    if key in {"/", "_", "-", "|"}:
        return key
    s = key
    s = re.sub(r"^(PC|CC|CapCut|Jianying|lv|ve|pc|pad|mobile|web)[_-]+", "", s)
    s = re.sub(r"[_-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace(" ai ", " AI ").replace(" vip ", " VIP ").replace(" url ", " URL ")
    if not s:
        return key
    return s[:1].upper() + s[1:]


def replace_msgstr(entry: str, new_value: str) -> str:
    lines = entry.splitlines()
    out: list[str] = []
    i = 0
    replaced = False
    while i < len(lines):
        line = lines[i]
        if not replaced and line.startswith("msgstr "):
            out.append("msgstr " + po_escape(new_value))
            i += 1
            while i < len(lines) and lines[i].startswith('"'):
                i += 1
            replaced = True
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def patch_po(app_po: Path, capcut_en: Path, capcut_zh: Path) -> dict[str, str]:
    en_by_id = read_po(capcut_en)
    zh_by_id = read_po(capcut_zh)
    en_by_zh = {
        zh: en_by_id[msgid]
        for msgid, zh in zh_by_id.items()
        if zh and msgid in en_by_id and en_by_id[msgid] and not HAN_RE.search(en_by_id[msgid])
    }

    text = app_po.read_text(encoding="utf-8")
    entries = split_entries(text)
    patched: list[str] = []
    zh_to_en = dict(COMMON)
    exact = by_zh = fallback = untouched = 0

    for entry in entries:
        msgid = field_value(entry, "msgid")
        old = field_value(entry, "msgstr")
        if msgid is None or old is None or msgid == "":
            patched.append(entry)
            continue
        if not HAN_RE.search(old):
            patched.append(entry)
            untouched += 1
            continue

        if msgid in en_by_id and en_by_id[msgid] and not HAN_RE.search(en_by_id[msgid]):
            new = en_by_id[msgid]
            exact += 1
        elif old in en_by_zh:
            new = en_by_zh[old]
            by_zh += 1
        elif old in COMMON:
            new = COMMON[old]
            by_zh += 1
        else:
            new = humanize_key(msgid)
            fallback += 1

        zh_to_en[old] = new
        patched.append(replace_msgstr(entry, new))

    app_po.write_text("\n\n".join(patched) + "\n", encoding="utf-8")
    print(f"PO patched: exact={exact} by_zh={by_zh} fallback={fallback} untouched={untouched}")
    return zh_to_en


def patch_plists_and_strings(root: Path) -> None:
    info = root / "Contents/Info.plist"
    with info.open("rb") as f:
        data = plistlib.load(f)
    data["NSCameraUsageDescription"] = COMMON["请允许“剪映专业版”访问您的摄像头，从而为您提供录制功能"]
    data["NSMicrophoneUsageDescription"] = COMMON["请允许“剪映专业版”访问您的麦克风，从而为您提供录音功能"]
    data["CFBundleDisplayName"] = "Jianying Pro"
    with info.open("wb") as f:
        plistlib.dump(data, f)

    for path in root.glob("Contents/**/InfoPlist.strings"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-16")
        text = re.sub(r'"CFBundleName"\s*=\s*".*?";', '"CFBundleName" = "Jianying Pro";', text)
        text = re.sub(r'"CFBundleDisplayName"\s*=\s*".*?";', '"CFBundleDisplayName" = "Jianying Pro";', text)
        path.write_text(text, encoding="utf-8")


def patch_text_files(root: Path, zh_to_en: dict[str, str]) -> None:
    def han_count(value: str) -> int:
        return len(HAN_RE.findall(value))

    replacements = {
        k: v
        for k, v in zh_to_en.items()
        if k
        and HAN_RE.search(k)
        and han_count(k) >= 3
        and len(k) >= 4
        and v
        and not HAN_RE.search(v)
    }
    replacements.update(COMMON)
    replacements.update(H5_COMMON)
    ordered = sorted(replacements.items(), key=lambda kv: len(kv[0]), reverse=True)
    exts = {".js", ".json", ".html", ".css", ".strings", ".plist", ".config"}
    changed = 0
    for path in root.glob("Contents/**/*"):
        if not path.is_file() or path.suffix not in exts:
            continue
        if path.name == "Info.plist":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not HAN_RE.search(text):
            continue
        new = text
        for zh, en in ordered:
            new = new.replace(zh, en)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"Text files patched: {changed}")


def patch_sparkle(root: Path) -> None:
    sparkle = root / "Contents/Frameworks/Sparkle.framework/Versions/B/Resources"
    en = sparkle / "en.lproj"
    base = sparkle / "Base.lproj"
    for loc in ["zh_CN.lproj", "zh_TW.lproj", "zh_HK.lproj", "ja.lproj"]:
        target = sparkle / loc
        if not target.exists():
            continue
        for src in en.glob("*.strings"):
            dst = target / src.name
            if dst.exists():
                dst.write_bytes(src.read_bytes())
        sparkle_src = base / "Sparkle.strings"
        sparkle_dst = target / "Sparkle.strings"
        if sparkle_src.exists() and sparkle_dst.exists():
            sparkle_dst.write_bytes(sparkle_src.read_bytes())
    print("Sparkle Chinese localizations replaced with English strings")


def patch_datepicker_locale(root: Path) -> None:
    replacements = {
        'formatYear:"YYYY 年"': 'formatYear:"YYYY"',
        'formatMonth:"YYYY 年 MM 月"': 'formatMonth:"MMMM YYYY"',
        'locale:"zh-CN"': 'locale:"en-US"',
        'dayjsLocale:"zh-cn"': 'dayjsLocale:"en"',
        'today:"今天"': 'today:"Today"',
        'month:"月"': 'month:"month"',
        'year:"年"': 'year:"year"',
        'week:"周"': 'week:"week"',
        'day:"日"': 'day:"day"',
        'January:"一月"': 'January:"January"',
        'February:"二月"': 'February:"February"',
        'March:"三月"': 'March:"March"',
        'April:"四月"': 'April:"April"',
        'May:"五月"': 'May:"May"',
        'June:"六月"': 'June:"June"',
        'July:"七月"': 'July:"July"',
        'August:"八月"': 'August:"August"',
        'September:"九月"': 'September:"September"',
        'October:"十月"': 'October:"October"',
        'November:"十一月"': 'November:"November"',
        'December:"十二月"': 'December:"December"',
        'self:"周"': 'self:"Week"',
        'monday:"周一"': 'monday:"Monday"',
        'tuesday:"周二"': 'tuesday:"Tuesday"',
        'wednesday:"周三"': 'wednesday:"Wednesday"',
        'thursday:"周四"': 'thursday:"Thursday"',
        'friday:"周五"': 'friday:"Friday"',
        'saturday:"周六"': 'saturday:"Saturday"',
        'sunday:"周日"': 'sunday:"Sunday"',
        'monday:"一"': 'monday:"Mon"',
        'tuesday:"二"': 'tuesday:"Tue"',
        'wednesday:"三"': 'wednesday:"Wed"',
        'thursday:"四"': 'thursday:"Thu"',
        'friday:"五"': 'friday:"Fri"',
        'saturday:"六"': 'saturday:"Sat"',
        'sunday:"日"': 'sunday:"Sun"',
        'date:"请选择日期"': 'date:"Select date"',
        'week:"请选择周"': 'week:"Select week"',
        'month:"请选择月份"': 'month:"Select month"',
        'year:"请选择年份"': 'year:"Select year"',
        'quarter:"请选择季度"': 'quarter:"Select quarter"',
        '"开始日期"': '"Start date"',
        '"结束日期"': '"End date"',
        '"开始周"': '"Start week"',
        '"结束周"': '"End week"',
        '"开始月份"': '"Start month"',
        '"结束月份"': '"End month"',
        '"开始年份"': '"Start year"',
        '"结束年份"': '"End year"',
        '"开始季度"': '"Start quarter"',
        '"结束季度"': '"End quarter"',
    }
    changed = 0
    for path in root.glob("Contents/Resources/image_h5_*/static/js/*.js"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "请选择日期" not in text and "YYYY 年" not in text:
            continue
        new = text
        for old, repl in replacements.items():
            new = new.replace(old, repl)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"Date picker locale patched: {changed}")


def patch_exact_js_literals(root: Path) -> None:
    exact = {"周": "Week", "日": "Day", "页": "Page"}
    changed = 0
    pattern = re.compile(r'(["\'])(周|日|页)\1')
    for path in root.glob("Contents/Resources/image_h5_*/static/js/*.js"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = pattern.sub(lambda m: f"{m.group(1)}{exact[m.group(2)]}{m.group(1)}", text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"Exact JS literals patched: {changed}")


def fallback_voice_name(item: dict[str, str]) -> str:
    for key in ("tone_en_name", "tone_speaker", "tone_cn_name"):
        value = item.get(key, "")
        if value and not HAN_RE.search(value):
            tail = value.split("_")[-1]
            tail = re.sub(r"\d+", " ", tail)
            tail = re.sub(r"([a-z])([A-Z])", r"\1 \2", tail)
            return tail.replace("-", " ").replace("_", " ").strip().title() or "Voice"
    return "Voice"


def patch_tts(root: Path) -> None:
    path = root / "Contents/Resources/tts/tone_infos.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data.get("tone_infos", []):
        source = item.get("tone_cn_name", "")
        name = VOICE_NAMES.get(source) or fallback_voice_name(item)
        item["tone_cn_name"] = name
        item["tone_en_name"] = name
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print("TTS voice names patched")


def main() -> None:
    app_po = ROOT / "Contents/Resources/po/zh-Hans.po"
    zh_to_en = patch_po(
        app_po,
        CAPCUT / "Contents/Resources/po/en.po",
        CAPCUT / "Contents/Resources/po/zh-Hans.po",
    )
    patch_plists_and_strings(ROOT)
    patch_text_files(ROOT, zh_to_en)
    patch_tts(ROOT)
    patch_datepicker_locale(ROOT)
    patch_exact_js_literals(ROOT)
    patch_sparkle(ROOT)


if __name__ == "__main__":
    main()
