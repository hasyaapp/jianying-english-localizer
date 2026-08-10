#!/usr/bin/env python3
"""Force-translate remaining NUL-delimited Chinese UI strings in embedded binaries."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

from argostranslate import translate


APP = Path("VideoFusion-macOS-English.app")
CACHE_PATH = Path("tools/embedded_force_translate_cache.json")
HAN_RE = re.compile(r"[\u3400-\u9fff]")

TARGETS = [
    "Contents/Frameworks/libVECreator.dylib",
    "Contents/Frameworks/libAICreator.dylib",
    "Contents/Frameworks/VECrashHandler.app/Contents/MacOS/VECrashHandler",
    "Contents/Frameworks/VEHelper.app/Contents/MacOS/VEHelper",
    "Contents/Frameworks/libvideoeditor.dylib",
]

SKIP_MARKERS = (
    "function ",
    "var ",
    "let ",
    "const ",
    "return ",
    "project[",
    "local ",
    "require(",
    "import ",
    "anchors",
    "Rectangle",
    "Text {",
    "//",
    "/*",
    "*/",
)

UI_KEYWORDS = (
    "失败",
    "错误",
    "会员",
    "剪映",
    "智能",
    "字幕",
    "素材",
    "视频",
    "音频",
    "文本",
    "草稿",
    "云空间",
    "导出",
    "导入",
    "保存",
    "取消",
    "确定",
    "登录",
    "支付",
    "退款",
    "网络",
    "加载",
    "字体",
    "音乐",
    "积分",
    "账号",
    "帐号",
    "模板",
    "轨道",
    "识别",
    "生成",
    "添加",
    "删除",
    "更新",
    "下载",
    "上传",
    "权限",
)

MANUAL = {
    "失败": "Failed",
    "成功": "OK",
    "取消": "Cancel",
    "确定": "OK",
    "添加": "Add",
    "删除": "Delete",
    "登录": "Login",
    "保存": "Save",
    "导出": "Export",
    "导入": "Import",
    "重试": "Retry",
    "剪映": "JY",
    "剪映云": "JY Cloud",
    "剪映专业版": "JY Pro",
    "会员": "Member",
    "字幕": "Subs",
    "文本": "Text",
    "音频": "Audio",
    "视频": "Video",
    "草稿": "Draft",
    "模板": "Tpl",
    "素材": "Media",
    "字体": "Font",
    "积分": "Points",
    "空间": "Space",
    "花字类型": "Text style",
    "按照<a style='color:#00c1cd' href='https://bytedance.feishu.cn/docx/UKObd7djfoZRj4xoreIcgHbnnKf'>「导出异常指南」</a>进行操作": (
        "Follow <a style='color:#00c1cd' href='https://bytedance.feishu.cn/docx/UKObd7djfoZRj4xoreIcgHbnnKf'>Export issue guide</a>"
    ),
    "人声增强失败": "Voice enhance fail",
    "获取用户列表失败": "Get users failed",
    "删除评论失败": "Delete comment fail",
    "删除失败，没权限": "Delete failed, no permission",
    "*当前倍速不支持“关闭变调”": "Current speed does not support pitch lock",
    "附加上下文，作为反馈参考：": "Extra context for feedback:",
    "请绑定手机号后使用": "Bind phone to use",
    "单声道素材无需配置声道": "Mono media needs no channel setup",
    "内存不足提示": "Low memory warning",
    "当前草稿不再提示": "Do not show for this draft",
    "邀请链接已失效": "Invite link expired",
    "文字模板已打散": "Text template split",
    "空间后再导出": "space before export",
    "关于商用音乐": "About commercial music",
    "我接受音乐使用确认书": "I accept the music usage confirmation",
    "开通会员并导出": "Subscribe and export",
    "加载数字人失败，请重试": "Digital human load failed, retry",
    "添加重复帧创建转场": "Add duplicate frames for transition",
    "添加标签让你的素材被更多人发现": "Add tags so more people find your media",
    "调整后跟踪效果丢失，需重新跟踪": "Tracking lost after adjustment; track again",
    "登录后即可导入字体": "Log in to import fonts",
    "登录后，可以查看收藏的字体": "Log in to view favorite fonts",
    "登录后可选择": "Log in to select",
    "同意加入": "Agree to join",
    "添加失败": "Add failed",
    "数字人应用需更新至剪映最新版本": "Update digital human app to latest JY",
    "文本朗读": "Text to speech",
    "渲染失败": "Render failed",
    "同时替换原数字人": "Replace original digital human too",
    "音频下载中...": "Downloading audio...",
    "拆分字幕失败": "Split captions failed",
    "字幕已更新": "Captions updated",
    "字幕及音频已添加在轨道": "Captions and audio added to track",
    "字幕更新中..": "Updating captions...",
    "文本及音频已添加在轨道": "Text and audio added to track",
    "更新失败": "Update failed",
    "请更新到最新版本使用": "Update to latest version",
    "欢迎使用数字人": "Welcome to digital human",
    "字数限制": "Character limit",
    "确认开启": "Confirm enable",
    "请确认积分消耗": "Confirm point usage",
    "本次预估需额外消耗%1积分": "Estimated extra cost: %1 points",
    "会员赠送积分": "Member bonus points",
    "文章为AI生成，不代表任何平台观点": "AI-generated article; not platform views",
    "请确认音乐版权": "Confirm music copyright",
    "改词翻唱已完成，并已为你加入AI音乐库": "Lyric cover complete and added to AI music library",
    "未识别到歌词，不支持改词翻唱": "No lyrics found; lyric cover unavailable",
    "剪映 AI - 改词翻唱": "JY AI - Lyric cover",
    "填入原歌词": "Enter original lyrics",
    "使用改词翻唱后暂不支持发布为模板": "Templates cannot be published after lyric cover",
    "与原曲歌词字数不匹配，请修改": "Lyric count mismatch; edit it",
    "将消耗积分": "Will use points",
    "智能解说粗剪": "Smart narration rough cut",
    "音频不合规，请修改": "Audio not compliant; edit it",
}

SHORTEN = (
    ("Jianying", "JY"),
    ("membership", "member"),
    ("Membership", "Member"),
    ("subscription", "sub"),
    ("Subscription", "Sub"),
    ("automatic", "auto"),
    ("Automatic", "Auto"),
    ("renewal", "renew"),
    ("Renewal", "Renew"),
    ("recognition", "recog"),
    ("Recognition", "Recog"),
    ("subtitle", "sub"),
    ("Subtitle", "Sub"),
    ("caption", "cap"),
    ("Caption", "Cap"),
    ("material", "media"),
    ("Material", "Media"),
    ("account", "acct"),
    ("Account", "Acct"),
    ("project", "proj"),
    ("Project", "Proj"),
    ("template", "tpl"),
    ("Template", "Tpl"),
    ("operation", "op"),
    ("Operation", "Op"),
    ("current", "cur"),
    ("Current", "Cur"),
    ("successful", "ok"),
    ("Successful", "OK"),
    ("download", "dl"),
    ("Download", "DL"),
    ("upload", "up"),
    ("Upload", "Up"),
    ("please ", ""),
    ("Please ", ""),
    ("the ", ""),
    ("The ", ""),
)


def load_deep_module():
    spec = importlib.util.spec_from_file_location("deep_patch_residual_chinese", "tools/deep_patch_residual_chinese.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load deep patch module")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def translator():
    langs = translate.get_installed_languages()
    zh = next((lang for lang in langs if lang.code.startswith("zh")), None)
    en = next((lang for lang in langs if lang.code == "en"), None)
    if zh is None or en is None:
        raise RuntimeError("Argos zh->en model is not installed")
    return zh.get_translation(en)


def likely_ui_segment(s: str) -> bool:
    if not HAN_RE.search(s):
        return False
    if len(HAN_RE.findall(s)) < 2:
        return False
    if not any(ch in s for ch in UI_KEYWORDS):
        return False
    if len(s.encode("utf-8")) > 3000:
        return False
    if any(marker in s for marker in SKIP_MARKERS):
        return False
    return True


def fallback_label(s: str) -> str:
    if len(s.encode("utf-8")) > 300:
        if "隐私政策" in s:
            return "Privacy policy notice"
        if "使用须知" in s:
            return "Usage notice"
        if "商业使用" in s or "版权" in s:
            return "Commercial use notice"
        if "授权书" in s:
            return "Authorization notice"
        if "功能升级" in s:
            return "Feature update notes"
        if "功能介绍" in s:
            return "Feature introduction"
        if "模板" in s:
            return "Template terms"
        return "Notice"
    if "智能" in s:
        return "Smart tool"
    if "失败" in s or "错误" in s:
        return "Failed"
    if "会员" in s:
        return "Member"
    if "字幕" in s:
        return "Captions"
    if "音频" in s:
        return "Audio"
    if "视频" in s:
        return "Video"
    if "素材" in s:
        return "Media"
    if "草稿" in s:
        return "Draft"
    if "导出" in s:
        return "Export"
    if "导入" in s:
        return "Import"
    if "保存" in s:
        return "Save"
    if "支付" in s:
        return "Payment"
    if "退款" in s:
        return "Refund"
    if "网络" in s:
        return "Network"
    if "加载" in s:
        return "Loading"
    if "字体" in s:
        return "Font"
    if "音乐" in s:
        return "Music"
    if "积分" in s:
        return "Points"
    if "账号" in s or "帐号" in s:
        return "Account"
    if "模板" in s:
        return "Template"
    if "轨道" in s:
        return "Track"
    if "识别" in s:
        return "Recognition"
    if "生成" in s:
        return "Generate"
    if "添加" in s:
        return "Add"
    if "删除" in s:
        return "Delete"
    if "更新" in s:
        return "Update"
    if "下载" in s:
        return "Download"
    if "上传" in s:
        return "Upload"
    if "权限" in s:
        return "Permission"
    return "Translated"


def clean_translation(text: str) -> str:
    text = text.replace("CapCut", "Jianying")
    text = text.replace("Jian Ying", "Jianying").replace("Cut Ying", "Jianying")
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(" .", ".").replace(" ,", ",").replace(" :", ":")
    if HAN_RE.search(text):
        text = HAN_RE.sub("", text)
        text = re.sub(r"\s+", " ", text).strip()
    return text or "Translated"


def fit(text: str, max_len: int) -> bytes:
    text = clean_translation(text)
    if len(text.encode("utf-8")) <= max_len:
        return text.encode("utf-8")
    for old, new in SHORTEN:
        text = text.replace(old, new)
        if len(text.encode("utf-8")) <= max_len:
            return text.encode("utf-8")
    words = text.split()
    while len(" ".join(words).encode("utf-8")) > max_len and len(words) > 1:
        words.pop()
    text = " ".join(words) if words else text
    data = text.encode("utf-8")
    if len(data) <= max_len:
        return data
    return data[:max_len].decode("utf-8", "ignore").rstrip().encode("utf-8") or b"EN"


def build_mapping(candidates: set[str]) -> dict[bytes, bytes]:
    deep = load_deep_module()
    po_pairs = {old.decode("utf-8"): new.decode("utf-8") for old, new in deep.encode_po_replacement_cores(APP)}
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    tx = translator()

    mapping: dict[bytes, bytes] = {}
    for s in sorted(candidates, key=lambda value: len(value.encode("utf-8")), reverse=True):
        max_len = len(s.encode("utf-8"))
        if s in MANUAL:
            raw = MANUAL[s]
        elif s in deep.PACKED_TEXT_REPLACEMENTS:
            raw = deep.PACKED_TEXT_REPLACEMENTS[s]
        elif s in po_pairs:
            raw = po_pairs[s]
        elif s in cache:
            raw = cache[s]
        else:
            raw = fallback_label(s)
            cache[s] = raw
        out = fit(raw, max_len)
        if HAN_RE.search(out.decode("utf-8", "ignore")):
            out = fit("Translated", max_len)
        if len(out) <= max_len:
            mapping[s.encode("utf-8")] = out
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    return mapping


def main() -> None:
    candidates: set[str] = set()
    for rel in TARGETS:
        data = (APP / rel).read_bytes()
        for part in data.split(b"\0"):
            try:
                s = part.decode("utf-8")
            except UnicodeDecodeError:
                continue
            if likely_ui_segment(s):
                candidates.add(s)

    mapping = build_mapping(candidates)
    files_changed = 0
    replacements = 0
    for rel in TARGETS:
        path = APP / rel
        parts = path.read_bytes().split(b"\0")
        changed = False
        for i, part in enumerate(parts):
            new_core = mapping.get(part)
            if new_core is None or len(new_core) > len(part):
                continue
            parts[i] = new_core + (b"\0" * (len(part) - len(new_core)))
            replacements += 1
            changed = True
        if changed:
            path.write_bytes(b"\0".join(parts))
            files_changed += 1
    print(f"candidates={len(candidates)} files_changed={files_changed} replacements={replacements}")


if __name__ == "__main__":
    main()
