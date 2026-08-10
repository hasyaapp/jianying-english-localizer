#!/usr/bin/env python3
"""Rebuild and install Jianying EN when the source Jianying app changes."""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_SOURCE_APP = Path("/Applications/VideoFusion-macOS.app")
DEFAULT_INSTALL_APP = Path("/Applications/Jianying EN.app")
DEFAULT_WORK_APP_NAME = "VideoFusion-macOS-English.app"
DEFAULT_STATE = Path.home() / "Library/Application Support/JianyingEnglishLocalizer/state.json"
DEFAULT_LOG = Path.home() / "Library/Logs/jianying-english-localizer.log"

SOURCE_SENTINELS = [
    "Contents/Info.plist",
    "Contents/Resources/po/zh-Hans.po",
    "Contents/Resources/lynx_config",
    "Contents/Frameworks/libVECreator.dylib",
    "Contents/Frameworks/libAICreator.dylib",
    "Contents/Frameworks/liblyra_cli_client.dylib",
    "Contents/Frameworks/VideoFusionData.framework/VideoFusionData",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Logger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def __call__(self, message: str) -> None:
        line = f"[{now()}] {message}"
        print(line, flush=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def run(cmd: list[str], *, cwd: Path, log: Logger, env: dict[str, str] | None = None) -> None:
    log("$ " + " ".join(cmd))
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )
    if proc.stdout:
        for line in proc.stdout.splitlines():
            log("  " + line)
    if proc.returncode:
        raise RuntimeError(f"Command failed with exit code {proc.returncode}: {' '.join(cmd)}")


def read_plist(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        return plistlib.load(handle)


def file_digest(path: Path, max_bytes: int = 2_000_000) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        digest.update(handle.read(max_bytes))
    return digest.hexdigest()


def path_signature(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"exists": False}
    stat = path.stat()
    payload: dict[str, object] = {
        "exists": True,
        "kind": "dir" if path.is_dir() else "file",
        "mtime_ns": stat.st_mtime_ns,
        "size": stat.st_size,
    }
    if path.is_file() and stat.st_size <= 8_000_000:
        payload["sha256_prefix"] = file_digest(path)
    return payload


def source_signature(source_app: Path) -> dict[str, object]:
    info_path = source_app / "Contents/Info.plist"
    info = read_plist(info_path) if info_path.exists() else {}
    return {
        "source_app": str(source_app),
        "bundle_identifier": info.get("CFBundleIdentifier"),
        "short_version": info.get("CFBundleShortVersionString"),
        "bundle_version": info.get("CFBundleVersion"),
        "sentinels": {rel: path_signature(source_app / rel) for rel in SOURCE_SENTINELS},
    }


def load_state(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def argos_python(repo: Path) -> Path | None:
    candidate = repo / ".venv-translate/bin/python"
    if not candidate.exists():
        return None
    proc = subprocess.run(
        [str(candidate), "-c", "import argostranslate.translate"],
        cwd=str(repo),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return candidate if proc.returncode == 0 else None


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def rebuild(args: argparse.Namespace, log: Logger, signature: dict[str, object]) -> None:
    repo = args.repo.resolve()
    source_app = args.source_app.resolve()
    work_app = (repo / args.work_app_name).resolve()
    install_app = args.install_app.resolve()

    if not source_app.exists():
        raise FileNotFoundError(f"Source app not found: {source_app}")
    if not Path("/Applications/CapCut.app").exists():
        log("Warning: /Applications/CapCut.app not found; official English reference may be unavailable.")

    log(f"Rebuilding English app from {source_app}")
    remove_path(work_app)
    run(["ditto", str(source_app), str(work_app)], cwd=repo, log=log)

    run([sys.executable, "tools/localize_videofusion.py"], cwd=repo, log=log)

    venv_python = argos_python(repo)
    if venv_python:
        run([str(venv_python), "tools/force_translate_fallbacks.py"], cwd=repo, log=log)
    else:
        log("Skipping Argos PO fallback pass; .venv-translate with argostranslate is not available.")

    run([sys.executable, "tools/deep_patch_residual_chinese.py", str(work_app)], cwd=repo, log=log)

    if venv_python:
        run([str(venv_python), "tools/force_patch_embedded_segments.py"], cwd=repo, log=log)
    else:
        log("Skipping embedded force pass; .venv-translate with argostranslate is not available.")

    run(["codesign", "--force", "--deep", "--sign", "-", str(work_app)], cwd=repo, log=log)
    run(["codesign", "--verify", "--deep", "--strict", "--verbose=1", str(work_app)], cwd=repo, log=log)

    if not args.skip_install:
        log(f"Installing patched app to {install_app}")
        remove_path(install_app)
        run(["ditto", str(work_app), str(install_app)], cwd=repo, log=log)
        run(["codesign", "--verify", "--deep", "--strict", "--verbose=1", str(install_app)], cwd=repo, log=log)

    save_state(
        args.state_file,
        {
            "last_success_at": now(),
            "source_signature": signature,
            "work_app": str(work_app),
            "install_app": str(install_app),
            "skip_install": args.skip_install,
        },
    )
    log("Auto-update completed successfully.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-app", type=Path, default=DEFAULT_SOURCE_APP)
    parser.add_argument("--install-app", type=Path, default=DEFAULT_INSTALL_APP)
    parser.add_argument("--work-app-name", default=DEFAULT_WORK_APP_NAME)
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--log-file", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--force", action="store_true", help="Rebuild even if the source signature is unchanged.")
    parser.add_argument("--dry-run", action="store_true", help="Only report whether a rebuild would happen.")
    parser.add_argument("--skip-install", action="store_true", help="Build the working app but do not install into /Applications.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    log = Logger(args.log_file)
    signature = source_signature(args.source_app)
    state = load_state(args.state_file)
    previous = state.get("source_signature")
    install_missing = not args.install_app.exists() and not args.skip_install
    changed = args.force or install_missing or previous != signature

    if args.dry_run:
        log(f"dry_run changed={changed} force={args.force} install_missing={install_missing}")
        return

    if not changed:
        log("Source app unchanged; no rebuild needed.")
        return

    rebuild(args, log, signature)


if __name__ == "__main__":
    main()
