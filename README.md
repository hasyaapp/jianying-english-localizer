# Jianying English Localizer

A local macOS toolkit for translating the Chinese Jianying desktop app (`VideoFusion-macOS.app`) into English.

The project patches a **local copy** of Jianying. It does not distribute Jianying, CapCut, modified application bundles, paid assets, or proprietary binaries.

## What it translates

The localization pipeline covers more than the main language catalog:

- `zh-Hans.po` UI strings.
- `Info.plist`, `InfoPlist.strings`, and bundled text resources.
- H5/React smart-text, narration, lyrics, and voice-over interfaces.
- Lynx commerce, subscription, invoice, refund, redeem, and AI-feature templates.
- TTS display names and selected JSON resources.
- Known feature names embedded in macOS binaries.
- NUL-delimited UI-like Chinese strings in selected frameworks and helper binaries.

Whenever possible, official CapCut English resources are used as the highest-quality reference. Remaining Jianying-only strings fall back to project mappings and optional local Chinese-to-English translation.

## Safety model

The original Jianying installation is kept untouched:

1. Copy `/Applications/VideoFusion-macOS.app` to a working app bundle.
2. Patch only the copy.
3. Re-sign the modified copy with an ad-hoc macOS signature.
4. Optionally install it separately as `/Applications/Jianying EN.app`.

Do **not** commit or redistribute `.app` bundles. They are intentionally ignored by `.gitignore`.

## Requirements

- macOS.
- Jianying installed at `/Applications/VideoFusion-macOS.app`.
- Python 3.11+.
- Apple `codesign`.
- Recommended: CapCut installed at `/Applications/CapCut.app` for official English localization references.
- Optional: Argos Translate for forced translation of Jianying-only leftovers.

Install the optional translation dependency:

```bash
python3 -m venv .venv-translate
. .venv-translate/bin/activate
pip install -r requirements-translate.txt
```

Argos also requires a Chinese-to-English model installed in that environment.

## Quick start

From the repository root:

```bash
ditto /Applications/VideoFusion-macOS.app ./VideoFusion-macOS-English.app
python3 tools/localize_videofusion.py
```

If Argos Translate is available, force-translate remaining PO fallbacks:

```bash
.venv-translate/bin/python tools/force_translate_fallbacks.py
```

Patch residual H5, Lynx, and embedded binary strings:

```bash
python3 tools/deep_patch_residual_chinese.py ./VideoFusion-macOS-English.app
.venv-translate/bin/python tools/force_patch_embedded_segments.py
```

Re-sign and verify the patched app:

```bash
codesign --force --deep --sign - ./VideoFusion-macOS-English.app
codesign --verify --deep --strict --verbose=1 ./VideoFusion-macOS-English.app
```

Install it separately:

```bash
ditto ./VideoFusion-macOS-English.app "/Applications/Jianying EN.app"
codesign --verify --deep --strict --verbose=1 "/Applications/Jianying EN.app"
```

For the complete patch order, see [docs/PIPELINE.md](docs/PIPELINE.md).

## Auto update

The repository includes a local macOS LaunchAgent that can rebuild `Jianying EN.app` when the installed Jianying source changes.

Install it from the repository root:

```bash
python3 tools/install_auto_update.py --kickstart
```

Useful commands:

```bash
# Check whether a rebuild would happen
python3 tools/auto_update_jianying_en.py --dry-run

# Force a rebuild now
python3 tools/auto_update_jianying_en.py --force

# Remove the LaunchAgent
python3 tools/install_auto_update.py --uninstall
```

See [docs/AUTO_UPDATE.md](docs/AUTO_UPDATE.md) for logs, state files, scheduling, and uninstall details.

## Repository layout

```text
jianying-english-localizer/
├── README.md
├── requirements-translate.txt
├── docs/
│   ├── AUTO_UPDATE.md
│   ├── PIPELINE.md
│   ├── TROUBLESHOOTING.md
│   └── VALIDATION.md
└── tools/
    ├── auto_update_jianying_en.py
    ├── deep_patch_residual_chinese.py
    ├── force_patch_embedded_segments.py
    ├── force_translate_fallbacks.py
    ├── install_auto_update.py
    └── localize_videofusion.py
```

Local/generated files such as app bundles, `__pycache__`, scan reports, logs, and translation-cache JSON files are intentionally excluded from Git.

## Script roles

- `tools/localize_videofusion.py` — main localization pass; prefers official CapCut English resources, then local mappings.
- `tools/force_translate_fallbacks.py` — fixes untranslated PO entries and bad `none` / `null` fallbacks.
- `tools/deep_patch_residual_chinese.py` — patches H5, Lynx, known feature labels, and embedded strings outside the PO catalog.
- `tools/force_patch_embedded_segments.py` — final byte-safe pass for remaining NUL-delimited UI-like Chinese segments.
- `tools/auto_update_jianying_en.py` — rebuilds and installs the English copy only when the source Jianying app changes, or when forced.
- `tools/install_auto_update.py` — installs or removes the LaunchAgent for periodic/source-change checks.

## Validation

At minimum, check the main PO catalog and code signature:

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

Expected PO results:

```text
po_han_count 0
po_bad_none_null 0
```

A raw byte scan can still find CJK-looking data in comments, fonts, generated code, or packed/model data that is not visible UI. Use targeted UI checks rather than treating every raw match as a translation failure.

See [docs/VALIDATION.md](docs/VALIDATION.md) for the deeper validation workflow and [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) if the app fails to open or visible Chinese remains.

## Local-only files

The following should stay on the local machine and should not be committed:

- `VideoFusion-macOS-English.app`
- `deep-scan-*.json`
- `deep-scan-*.txt`
- `chinese-text-files.txt`
- `tools/*cache*.json`
- `tools/__pycache__/`

The translation-cache JSON files can be regenerated by the forced translation passes and may contain machine-specific/generated state.

## Disclaimer

This is an independent local patching toolkit for users who already have Jianying installed. It is not an official ByteDance, Jianying, or CapCut product and does not grant rights to redistribute proprietary software or assets.
