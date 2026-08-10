# Troubleshooting

## macOS says the app is damaged

Re-sign the copied bundle:

```bash
codesign --force --deep --sign - ./VideoFusion-macOS-English.app
codesign --verify --deep --strict --verbose=1 ./VideoFusion-macOS-English.app
```

If the app was copied into `/Applications`, verify that copy too:

```bash
codesign --verify --deep --strict --verbose=1 "/Applications/Jianying EN.app"
```

## The app opens but some text is still Chinese

First check whether the string is in the main PO catalog:

```bash
rg "the Chinese text here" ./VideoFusion-macOS-English.app/Contents/Resources/po
```

If not, scan the app copy:

```bash
rg --text "the Chinese text here" ./VideoFusion-macOS-English.app/Contents
```

Common locations:

- `Contents/Resources/image_h5_*`
- `Contents/Resources/lynx_config`
- `Contents/Frameworks/*.dylib`
- `Contents/Frameworks/*Helper*.app`

Patch text files normally. Patch binaries only with equal-length or shorter replacements and preserve file size.

## CapCut is not installed

The main script prefers official CapCut English resources. Without CapCut, you lose the most accurate translation source.

Recommended setup:

```text
/Applications/CapCut.app
/Applications/VideoFusion-macOS.app
```

## Argos Translate is not installed

The main pass still works. The forced fallback passes require Argos only when automatic translation is needed for leftovers.

Install:

```bash
python3 -m venv .venv-translate
. .venv-translate/bin/activate
pip install -r requirements-translate.txt
```

Then install a Chinese-to-English Argos model in that environment.

