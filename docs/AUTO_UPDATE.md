# Auto Update

The repository includes a local macOS auto-updater for `/Applications/Jianying EN.app`.

It watches the original Jianying app:

```text
/Applications/VideoFusion-macOS.app
```

When the source app changes, it rebuilds the local English copy using the scripts in this repository and installs:

```text
/Applications/Jianying EN.app
```

The original app is not modified.

## Install The LaunchAgent

From the repository root:

```bash
python3 tools/install_auto_update.py
```

By default, the LaunchAgent:

- Runs once when loaded.
- Checks every 6 hours.
- Watches the source app, `Info.plist`, and `zh-Hans.po`.
- Logs to `~/Library/Logs/jianying-english-localizer.launchd.log`.

To install and run immediately:

```bash
python3 tools/install_auto_update.py --kickstart
```

## Manual Check

Run a dry check:

```bash
python3 tools/auto_update_jianying_en.py --dry-run
```

Force a rebuild:

```bash
python3 tools/auto_update_jianying_en.py --force
```

The state file is stored at:

```text
~/Library/Application Support/JianyingEnglishLocalizer/state.json
```

## Uninstall The LaunchAgent

```bash
python3 tools/install_auto_update.py --uninstall
```

This removes only the scheduled updater. It does not delete `/Applications/Jianying EN.app`.

## Notes

The updater does not push app bundles or generated cache files to GitHub. It only keeps the local installed English app in sync with the locally installed Jianying source app.

GitHub Actions cannot build this automatically because the proprietary Jianying and CapCut app bundles are not available on hosted runners and should not be committed to the repository.
