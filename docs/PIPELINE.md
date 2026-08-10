# Localization Pipeline

This document explains the patch order and why each layer exists.

## 1. Copy The App

Always work on a copy:

```bash
ditto /Applications/VideoFusion-macOS.app ./VideoFusion-macOS-English.app
```

The source app remains untouched. The copied bundle is the only mutation target.

## 2. Main PO Pass

Run:

```bash
python3 tools/localize_videofusion.py
```

This pass reads:

- Jianying copy: `VideoFusion-macOS-English.app/Contents/Resources/po/zh-Hans.po`
- CapCut English: `/Applications/CapCut.app/Contents/Resources/po/en.po`
- CapCut Chinese: `/Applications/CapCut.app/Contents/Resources/po/zh-Hans.po`

Priority:

1. Exact `msgid` match from official CapCut English.
2. Chinese string match via CapCut Chinese-to-English mapping.
3. Local common UI dictionary.
4. Humanized fallback for untranslated keys.

It also patches plist strings, H5 text files, date picker labels, and TTS display names.

## 3. Forced PO Fallbacks

Run with Argos installed:

```bash
.venv-translate/bin/python tools/force_translate_fallbacks.py
```

This pass uses the original Jianying PO as the Chinese source and the patched PO as the destination. It fixes entries that still contain Chinese or invalid fallback values such as `none` and `null`.

## 4. Residual H5, Lynx, And Binary Labels

Run:

```bash
python3 tools/deep_patch_residual_chinese.py ./VideoFusion-macOS-English.app
```

This pass covers strings outside the main PO catalog:

- H5 smart text editor strings.
- H5 voice-over rough cut strings.
- H5 diagnostic strings that can leak to UI or console.
- Lynx commerce and subscription template strings.
- Feature names embedded directly in binary resources.
- Known short UI terms in embedded string tables.

Binary replacements are length-safe. If the replacement is shorter than the source string, padding is used so file offsets remain stable.

## 5. Embedded Segment Force Pass

Run with Argos environment available:

```bash
.venv-translate/bin/python tools/force_patch_embedded_segments.py
```

This final pass scans selected binaries for NUL-delimited UI-like Chinese strings and replaces them with byte-safe English labels.

It intentionally skips obvious source-code/comment blocks to reduce the chance of affecting runtime logic.

## 6. Re-Sign

Any binary modification invalidates the original signature. Re-sign the copied app:

```bash
codesign --force --deep --sign - ./VideoFusion-macOS-English.app
codesign --verify --deep --strict --verbose=1 ./VideoFusion-macOS-English.app
```

## 7. Install Separately

Install the patched app with a separate name:

```bash
ditto ./VideoFusion-macOS-English.app "/Applications/Jianying EN.app"
```

Keeping `/Applications/VideoFusion-macOS.app` intact gives you a clean rollback path.

