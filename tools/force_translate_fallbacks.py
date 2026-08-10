#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import argostranslate.translate


APP_PO = Path("VideoFusion-macOS-English.app/Contents/Resources/po/zh-Hans.po")
ORIGINAL_PO = Path("/Applications/VideoFusion-macOS.app/Contents/Resources/po/zh-Hans.po")
CAPCUT_EN_PO = Path("/Applications/CapCut.app/Contents/Resources/po/en.po")
CAPCUT_ZH_PO = Path("/Applications/CapCut.app/Contents/Resources/po/zh-Hans.po")
CACHE = Path("tools/force_translate_cache.json")
HAN_RE = re.compile(r"[\u3400-\u9fff]")
BAD_RE = re.compile(r"^(?:\[?none\]?|\[?null\]?|「none」)$", re.I)

MSGID_OVERRIDES = {
    "ai_avatar_nothing": "No AI avatar",
    "none": "No option",
    "none_audio": "No audio",
    "none_subtitle": "No subtitles",
    "nothing": "No content",
    "pc_audio_effects_none": "No audio effects",
    "pc_auto_beautify_tab_auto_none": "No auto beautify",
    "pc_charts_none": "No charts",
    "pc_hair_none": "No hair effect",
    "pc_lut_none": "No LUT",
    "pc_none": "No option",
    "pc_separate_none": "No separation",
    "pc_social_media_preview_none": "No preview",
    "pc_sticker_none": "No stickers",
    "pc_stroke_none": "No stroke",
    "pc_subtitle_template_texture_method_none": "No texture",
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


def valid_official(value: str | None) -> bool:
    if not value:
        return False
    stripped = value.strip()
    if not stripped or HAN_RE.search(stripped):
        return False
    if BAD_RE.match(stripped):
        return False
    if re.search(r"\b(?:none|null)\b", stripped, re.I):
        return False
    return True


def protect(text: str) -> tuple[str, dict[str, str]]:
    protected: dict[str, str] = {}
    patterns = [
        r"<[^>]+>",
        r"%\d+",
        r"%[sdif]",
        r"\{\w+\}",
        r"\$\{[^}]+\}",
        r"\\n",
    ]
    combined = re.compile("|".join(f"({p})" for p in patterns))

    def repl(match: re.Match[str]) -> str:
        token = f" __PH{len(protected)}__ "
        protected[token.strip()] = match.group(0)
        return token

    return combined.sub(repl, text), protected


def restore(text: str, protected: dict[str, str]) -> str:
    for token, value in protected.items():
        text = text.replace(token, value)
        text = text.replace(token.replace("_", " _"), value)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(" \\n ", "\\n").replace("\\n ", "\\n").replace(" \\n", "\\n")
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([\[(])\s+", r"\1", text)
    text = re.sub(r"\s+([\])])", r"\1", text)
    return text


def cleanup_translation(text: str) -> str:
    replacements = {
        "Cut Screen": "Jianying",
        "Cutout": "Jianying",
        "clip": "clip",
        "AI Rough Cutting": "AI Rough Cut",
        "mobile phone number": "phone number",
        "cell phone number": "phone number",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


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


def main() -> None:
    current_entries = split_entries(APP_PO.read_text(encoding="utf-8"))
    original = read_po(ORIGINAL_PO)
    capcut_en = read_po(CAPCUT_EN_PO)
    capcut_zh = read_po(CAPCUT_ZH_PO)
    official_by_zh = {
        zh: capcut_en[mid]
        for mid, zh in capcut_zh.items()
        if zh and valid_official(capcut_en.get(mid))
    }
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}

    to_translate: dict[str, str] = {}
    candidate_ids: set[str] = set()
    for entry in current_entries:
        msgid = field_value(entry, "msgid")
        cur = field_value(entry, "msgstr")
        zh = original.get(msgid or "")
        if not msgid or not cur or not zh or not HAN_RE.search(zh):
            continue
        if valid_official(capcut_en.get(msgid)) and cur == capcut_en[msgid]:
            continue
        if zh in official_by_zh and cur == official_by_zh[zh]:
            continue
        if BAD_RE.match(cur.strip()) or re.search(r"\b(?:none|null)\b", cur, re.I) or cur == msgid or "_" in cur:
            candidate_ids.add(msgid)
            if zh not in cache:
                to_translate[zh] = msgid

    print(f"candidate entries: {len(candidate_ids)}")
    print(f"unique uncached zh strings: {len(to_translate)}")

    for idx, zh in enumerate(to_translate, 1):
        protected_text, protected = protect(zh)
        translated = argostranslate.translate.translate(protected_text, "zh", "en")
        translated = cleanup_translation(restore(translated, protected))
        if not translated or HAN_RE.search(translated) or BAD_RE.match(translated):
            translated = re.sub(r"[_-]+", " ", to_translate[zh]).strip()
        cache[zh] = translated
        if idx % 100 == 0:
            CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"translated {idx}/{len(to_translate)}")
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    patched: list[str] = []
    changed = 0
    for entry in current_entries:
        msgid = field_value(entry, "msgid")
        cur = field_value(entry, "msgstr")
        zh = original.get(msgid or "")
        forced = MSGID_OVERRIDES.get(msgid or "")
        if forced and cur != forced:
            patched.append(replace_msgstr(entry, forced))
            changed += 1
        elif msgid in candidate_ids and zh in cache and cur != cache[zh]:
            patched.append(replace_msgstr(entry, cache[zh]))
            changed += 1
        else:
            patched.append(entry)

    APP_PO.write_text("\n\n".join(patched) + "\n", encoding="utf-8")
    print(f"patched entries: {changed}")


if __name__ == "__main__":
    main()
