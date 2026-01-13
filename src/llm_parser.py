import json
import os
import urllib.request
from typing import Any, Dict, Optional


ALLOWED_ACTIONS = {"stop", "sleep", "ping", "noop"}

SYSTEM_PROMPT = """あなたは自然言語をアクションJSONに変換するエンジンです。
必ず次のいずれかのJSONのみを返してください。
成功時:
{"action":"stop","params":{}}
{"action":"sleep","params":{"ms":1000}}
{"action":"ping","params":{}}
{"action":"noop","params":{}}
失敗時:
{"error":"unsupported_or_ambiguous_request"}

追加の説明やMarkdownは禁止です。
曖昧な依頼は必ず error を返してください。"""


class LLMParseError(Exception):
    pass


def parse_natural_language(text: str) -> Dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise LLMParseError("OPENAI_API_KEY is not set")

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    }

    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read().decode("utf-8")
        data = json.loads(raw)

    content = _extract_content(data)
    return _validate_output(content)


def _extract_content(data: Dict[str, Any]) -> str:
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise LLMParseError("invalid_response")


def _validate_output(content: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return {"error": "unsupported_or_ambiguous_request"}

    if not isinstance(parsed, dict):
        return {"error": "unsupported_or_ambiguous_request"}

    if "error" in parsed:
        if parsed["error"] == "unsupported_or_ambiguous_request":
            return {"error": "unsupported_or_ambiguous_request"}
        return {"error": "unsupported_or_ambiguous_request"}

    action = parsed.get("action")
    params = parsed.get("params")
    if action not in ALLOWED_ACTIONS:
        return {"error": "unsupported_or_ambiguous_request"}
    if not isinstance(params, dict):
        return {"error": "unsupported_or_ambiguous_request"}

    if action == "sleep":
        ms = params.get("ms")
        if not isinstance(ms, int):
            return {"error": "unsupported_or_ambiguous_request"}

    if action in {"stop", "ping", "noop"} and params:
        return {"error": "unsupported_or_ambiguous_request"}

    return {"action": action, "params": params}
