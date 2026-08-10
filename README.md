# Jianying English Localizer

Local English patching toolkit for the macOS Jianying desktop app, packaged as `VideoFusion-macOS.app`.

This repository contains scripts and documentation only. It does not distribute Jianying, CapCut, modified app bundles, paid assets, or proprietary binaries.

## What This Does

The toolkit builds a local English copy of Jianying by translating UI resources from several layers:

- Main `zh-Hans.po` translation catalog.
- `Info.plist`, `InfoPlist.strings`, and bundled text resources.
- H5/React smart text and voice-over panels.
- Lynx commerce, subscription, invoice, refund, redeem, and feature popup templates.
- Embedded NUL-delimited UI string tables inside selected macOS binaries.
- Length-safe binary labels for feature names such as `Montage`, `Bullet Time`, `Hero Moment`, `J-Cut`, and `Freeze`.

The preferred translation source is official CapCut English resources when available. Missing strings fall back to local mappings and forced English replacements.

## Safety Model

The workflow is designed to keep the original app untouched:

1. Copy `/Applications/VideoFusion-macOS.app` into a working directory.
2. Patch only the copied bundle.
3. Re-sign the copied bundle locally with an ad-hoc signature.
4. Optionally install the result as `/Applications/Jianying EN.app`.

Do not commit or redistribute `.app` bundles. They are intentionally ignored by `.gitignore`.

## Requirements

- macOS.
- Installed Jianying app at `/Applications/VideoFusion-macOS.app`.
- Installed CapCut global app at `/Applications/CapCut.app` for official English PO references.
- Python 3.11+.
- Optional but recommended: `argostranslate` for forced fallback translations.
- Apple `codesign`, included with macOS command line tools.

Install the optional Python dependency:

```bash
python3 -m venv .venv-translate
. .venv-translate/bin/activate
pip install -r requirements-translate.txt
```

Argos also needs a local Chinese-to-English model. The exact model install flow depends on your environment; see Argos Translate documentation for package installation.

## Quick Start

From a clean working directory:

```bash
ditto /Applications/VideoFusion-macOS.app ./VideoFusion-macOS-English.app
python3 tools/localize_videofusion.py
```

If you have Argos Translate installed and want to force translate catalog leftovers:

```bash
.venv-translate/bin/python tools/force_translate_fallbacks.py
```

Patch residual H5, Lynx, and selected embedded binary strings:

```bash
python3 tools/deep_patch_residual_chinese.py ./VideoFusion-macOS-English.app
.venv-translate/bin/python tools/force_patch_embedded_segments.py
```

Re-sign and verify:

```bash
codesign --force --deep --sign - ./VideoFusion-macOS-English.app
codesign --verify --deep --strict --verbose=1 ./VideoFusion-macOS-English.app
```

Install as a separate app:

```bash
ditto ./VideoFusion-macOS-English.app "/Applications/Jianying EN.app"
codesign --verify --deep --strict --verbose=1 "/Applications/Jianying EN.app"
```

## Scripts

- `tools/localize_videofusion.py`  
  Main localization pass. Uses official CapCut English PO resources first, then project mappings.

- `tools/force_translate_fallbacks.py`  
  Fills missing PO translations and fixes bad `none` / `null` fallback values.

- `tools/deep_patch_residual_chinese.py`  
  Patches H5 leftovers, Lynx templates, feature labels, and known embedded binary strings with byte-safe replacements.

- `tools/force_patch_embedded_segments.py`  
  Final deep pass for remaining NUL-delimited UI-like Chinese segments in selected binaries.

## Validation Checklist

Before using or publishing a build, verify:

```bash
python3 - <<'PY'
from pathlib import Path
import re
po = Path("VideoFusion-macOS-English.app/Contents/Resources/po/zh-Hans.po").read_text("utf-8")
print("po_han_count", len(re.findall(r"[\u4e00-\u9fff]", po)))
print("po_bad_none_null", len(re.findall(r'msgstr "(?:none|null|None|NULL)"', po)))
PY

codesign --verify --deep --strict --verbose=1 ./VideoFusion-macOS-English.app
```

The expected PO checks are:

- `po_han_count 0`
- `po_bad_none_null 0`

See [docs/VALIDATION.md](docs/VALIDATION.md) for deeper scan notes.

## Notes

This is a local patching toolkit for users who already have the app installed. It is not an official product, not affiliated with ByteDance, CapCut, or Jianying, and does not grant rights to redistribute any proprietary software.

