import os
import re
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

ALLOWED_APPS = {
    "Notes",
    "Safari",
    "Google Chrome",
    "Terminal",
    "Visual Studio Code",
}

URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)
MAX_TEXT_LENGTH = 200
MAX_TITLE_LENGTH = 80
MAX_URL_LENGTH = 2048
MAX_SLEEP_MS = 5000


class SkillError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class SkillResult:
    ok: bool
    message: str
    artifact_path: Optional[str] = None


def redact_params(action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if action == "ping":
        return {}
    if action == "noop":
        return {}
    if action == "notify":
        return {
            "title": _truncate(params.get("title"), MAX_TITLE_LENGTH),
            "message": _truncate(params.get("message"), MAX_TEXT_LENGTH),
        }
    if action == "open_url":
        url = params.get("url")
        return {"url": _truncate(url, 120) if isinstance(url, str) else url}
    if action == "open_app":
        return {"app_name": params.get("app_name")}
    if action == "screenshot":
        return {}
    if action == "sleep":
        return {"ms": params.get("ms")}
    return dict(params)


def ping(params: Dict[str, Any]) -> SkillResult:
    del params
    return SkillResult(ok=True, message="pong")


def noop(params: Dict[str, Any]) -> SkillResult:
    del params
    return SkillResult(ok=True, message="noop")


def open_app(params: Dict[str, Any]) -> SkillResult:
    app_name = params.get("app_name")
    if app_name not in ALLOWED_APPS:
        raise SkillError("app_not_allowed", "app is not in allowlist")

    subprocess.run(["/usr/bin/open", "-a", app_name], check=True)
    return SkillResult(ok=True, message="app_opened")


def open_url(params: Dict[str, Any]) -> SkillResult:
    url = params.get("url")
    if not isinstance(url, str) or not url.strip():
        raise SkillError("url_required", "url is required")
    if len(url) > MAX_URL_LENGTH:
        raise SkillError("url_too_long", "url is too long")
    if not URL_PATTERN.match(url):
        raise SkillError("url_not_allowed", "only http/https allowed")

    subprocess.run(["/usr/bin/open", url], check=True)
    return SkillResult(ok=True, message="url_opened")


def notify(params: Dict[str, Any]) -> SkillResult:
    title = params.get("title")
    message = params.get("message")
    if not isinstance(title, str) or not title.strip():
        raise SkillError("title_required", "title is required")
    if not isinstance(message, str) or not message.strip():
        raise SkillError("message_required", "message is required")
    if len(title) > MAX_TITLE_LENGTH:
        raise SkillError("title_too_long", "title is too long")
    if len(message) > MAX_TEXT_LENGTH:
        raise SkillError("message_too_long", "message is too long")

    script = f'display notification "{_escape(message)}" with title "{_escape(title)}"'
    subprocess.run(["/usr/bin/osascript", "-e", script], check=True)
    return SkillResult(ok=True, message="notified")


def screenshot(params: Dict[str, Any]) -> SkillResult:
    del params
    directory = os.path.join("artifacts", "screenshots")
    os.makedirs(directory, exist_ok=True)
    filename = f"screenshot_{int(time.time() * 1000)}.png"
    path = os.path.join(directory, filename)
    subprocess.run(["/usr/bin/screencapture", "-x", path], check=True)
    return SkillResult(ok=True, message="screenshot_saved", artifact_path=path)


def sleep(params: Dict[str, Any], should_stop) -> SkillResult:
    ms = params.get("ms")
    if not isinstance(ms, int):
        raise SkillError("ms_required", "ms must be an integer")
    if ms < 0 or ms > MAX_SLEEP_MS:
        raise SkillError("ms_out_of_range", "ms out of range")

    remaining = ms / 1000.0
    while remaining > 0:
        if should_stop():
            return SkillResult(ok=False, message="stopped")
        step = min(0.1, remaining)
        time.sleep(step)
        remaining -= step
    return SkillResult(ok=True, message="slept")


def _escape(value: str) -> str:
    return value.replace('"', '\\"')


def _truncate(value: Optional[str], length: int) -> Optional[str]:
    if not isinstance(value, str):
        return value
    if len(value) <= length:
        return value
    return value[: length - 3] + "..."
