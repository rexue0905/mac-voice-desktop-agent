import time
from typing import Any, Callable, Dict, Optional

from skills import (
    SkillError,
    SkillResult,
    notify,
    noop,
    open_app,
    open_url,
    ping,
    redact_params,
    screenshot,
    sleep,
)


class Executor:
    def execute(
        self,
        action: str,
        params: Dict[str, Any],
        should_stop: Callable[[], bool],
    ) -> Dict[str, Any]:
        if should_stop():
            return self._stopped_result("stopped_before_execute")

        started_at = time.time()
        result: Optional[SkillResult] = None
        error_code: Optional[str] = None

        try:
            if action == "open_app":
                result = open_app(params)
            elif action == "ping":
                result = ping(params)
            elif action == "noop":
                result = noop(params)
            elif action == "open_url":
                result = open_url(params)
            elif action == "notify":
                result = notify(params)
            elif action == "screenshot":
                result = screenshot(params)
            elif action == "sleep":
                result = sleep(params, should_stop)
            else:
                return self._failed_result("action_not_supported", "action not supported")
        except SkillError as exc:
            error_code = exc.code
            result = SkillResult(ok=False, message=exc.message)
        except Exception:
            error_code = "execution_failed"
            result = SkillResult(ok=False, message="execution failed")

        duration_ms = int((time.time() - started_at) * 1000)

        if result is None:
            return self._failed_result("execution_failed", "execution failed")

        if result.message == "stopped" or should_stop():
            return self._stopped_result("stopped_during_execute", duration_ms)

        return {
            "status": "ok" if result.ok else "failed",
            "message": result.message,
            "artifact_path": result.artifact_path,
            "error_code": error_code,
            "duration_ms": duration_ms,
            "params_redacted": redact_params(action, params),
        }

    def _stopped_result(self, message: str, duration_ms: int = 0) -> Dict[str, Any]:
        return {
            "status": "stopped",
            "message": message,
            "artifact_path": None,
            "error_code": "stopped",
            "duration_ms": duration_ms,
        }

    def _failed_result(self, code: str, message: str) -> Dict[str, Any]:
        return {
            "status": "failed",
            "message": message,
            "artifact_path": None,
            "error_code": code,
            "duration_ms": 0,
        }
