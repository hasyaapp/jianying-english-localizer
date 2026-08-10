#!/usr/bin/env python3
"""Install or remove the macOS LaunchAgent for Jianying EN auto-updates."""

from __future__ import annotations

import argparse
import os
import plistlib
import subprocess
import sys
from pathlib import Path


LABEL = "com.hasyaapp.jianying-english-localizer"
PLIST_PATH = Path.home() / f"Library/LaunchAgents/{LABEL}.plist"
LOG_PATH = Path.home() / "Library/Logs/jianying-english-localizer.launchd.log"
SOURCE_APP = Path("/Applications/VideoFusion-macOS.app")


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("$ " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, text=True, check=check)


def gui_domain() -> str:
    return f"gui/{os.getuid()}"


def unload() -> None:
    run(["launchctl", "bootout", gui_domain(), str(PLIST_PATH)], check=False)


def write_plist(repo: Path, interval: int) -> None:
    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "Label": LABEL,
        "ProgramArguments": [
            sys.executable,
            str(repo / "tools/auto_update_jianying_en.py"),
            "--repo",
            str(repo),
        ],
        "RunAtLoad": True,
        "StartInterval": interval,
        "WatchPaths": [
            str(SOURCE_APP),
            str(SOURCE_APP / "Contents/Info.plist"),
            str(SOURCE_APP / "Contents/Resources/po/zh-Hans.po"),
        ],
        "StandardOutPath": str(LOG_PATH),
        "StandardErrorPath": str(LOG_PATH),
        "WorkingDirectory": str(repo),
    }
    with PLIST_PATH.open("wb") as handle:
        plistlib.dump(payload, handle, sort_keys=False)


def install(repo: Path, interval: int, kickstart: bool) -> None:
    write_plist(repo, interval)
    unload()
    run(["launchctl", "bootstrap", gui_domain(), str(PLIST_PATH)])
    if kickstart:
        run(["launchctl", "kickstart", "-k", f"{gui_domain()}/{LABEL}"], check=False)
    print(f"Installed LaunchAgent: {PLIST_PATH}")


def uninstall() -> None:
    unload()
    if PLIST_PATH.exists():
        PLIST_PATH.unlink()
    print(f"Removed LaunchAgent: {PLIST_PATH}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--interval", type=int, default=21_600, help="Check interval in seconds. Default: 6 hours.")
    parser.add_argument("--kickstart", action="store_true", help="Run the job immediately after installing.")
    parser.add_argument("--uninstall", action="store_true", help="Remove the LaunchAgent instead of installing it.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.uninstall:
        uninstall()
    else:
        install(args.repo.resolve(), args.interval, args.kickstart)


if __name__ == "__main__":
    main()
