# Validation

This toolkit has two validation goals:

1. Confirm the main translation catalog is clean.
2. Confirm the patched macOS app bundle is still launchable from a signing perspective.

## Main PO Checks

```bash
python3 - <<'PY'
from pathlib import Path
import re

po = Path("VideoFusion-macOS-English.app/Contents/Resources/po/zh-Hans.po").read_text("utf-8")
print("po_han_count", len(re.findall(r"[\u4e00-\u9fff]", po)))
print("po_bad_none_null", len(re.findall(r'msgstr "(?:none|null|None|NULL)"', po)))
PY
```

Expected:

```text
po_han_count 0
po_bad_none_null 0
```

## Target String Check

For a practical UI smoke check, scan for terms that previously appeared in visible panels:

```bash
python3 - <<'PY'
from pathlib import Path

terms = [
    "智能包装", "智能文案", "蒙太奇", "子弹时间", "定格",
    "加载失败", "网络异常", "需输入10字以上", "正在Generate",
]

root = Path("VideoFusion-macOS-English.app/Contents")
remaining = []
for term in terms:
    needle = term.encode("utf-8")
    count = 0
    for path in root.rglob("*"):
        if path.is_file():
            count += path.read_bytes().count(needle)
    if count:
        remaining.append((term, count))

print("target_terms_remaining", remaining)
PY
```

Expected:

```text
target_terms_remaining []
```

## Signature Check

```bash
codesign --verify --deep --strict --verbose=1 ./VideoFusion-macOS-English.app
```

Expected:

```text
./VideoFusion-macOS-English.app: valid on disk
./VideoFusion-macOS-English.app: satisfies its Designated Requirement
```

## Known Non-Issues

A raw byte-level scan can still report Chinese-looking matches from:

- Source comments embedded inside binaries.
- Generated code snippets that are not visible UI.
- Font filenames.
- Model or packed resource bytes that decode accidentally as CJK characters.

Treat raw scans as leads, not proof. Prefer targeted scans against visible UI terms and NUL-delimited string tables.

