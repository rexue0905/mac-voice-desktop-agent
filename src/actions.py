# src/actions.py
from typing import Any, Dict, Tuple

# 白名单：允许的 action 列表
ALLOWED_ACTIONS = {
    "ping",
    "noop",
    "stop",
    "open_app",
    "open_url",
    "notify",
    "screenshot",
    "sleep",
}

def validate_command(payload: Dict[str, Any]) -> Tuple[bool, str]:
    """
    校验请求体格式：
    - 必须是 dict
    - 必须包含 action(str) 与 params(dict)
    - action 必须在白名单
    - params 按 action 做最小校验
    返回: (ok, error_message)
    """
    if not isinstance(payload, dict):
        return False, "body_must_be_object"

    action = payload.get("action")
    params = payload.get("params")

    if not isinstance(action, str) or not action.strip():
        return False, "action_required"

    if action not in ALLOWED_ACTIONS:
        return False, "action_not_allowed"

    if not isinstance(params, dict):
        return False, "params_must_be_object"

    # action별 파라미터 최소 검증
    if action == "open_app":
        app_name = params.get("app_name")
        if not isinstance(app_name, str) or not app_name.strip():
            return False, "open_app_requires_app_name"

    if action == "open_url":
        url = params.get("url")
        if not isinstance(url, str) or not url.strip():
            return False, "open_url_requires_url"

    if action == "notify":
        title = params.get("title")
        message = params.get("message")
        if not isinstance(title, str) or not title.strip():
            return False, "notify_requires_title"
        if not isinstance(message, str) or not message.strip():
            return False, "notify_requires_message"

    if action == "screenshot":
        if params:
            return False, "screenshot_params_must_be_empty"

    if action == "sleep":
        ms = params.get("ms")
        if not isinstance(ms, int):
            return False, "sleep_requires_ms"

    return True, ""
