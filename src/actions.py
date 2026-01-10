# src/actions.py
from typing import Any, Dict, Tuple

# 白名单：允许的 action 列表
ALLOWED_ACTIONS = {
    "ping",
    "print_text",
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
    if action == "ping":
        # ping 不需要参数
        if params:
            return False, "ping_params_must_be_empty"

    if action == "print_text":
        text = params.get("text")
        if not isinstance(text, str) or not text.strip():
            return False, "print_text_requires_text"

    return True, ""