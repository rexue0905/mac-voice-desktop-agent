import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional
from uuid import uuid4

from skills import redact_params

class QueueManager:
    def __init__(self, executor, *, step_delay: float = 0.05, steps: int = 5) -> None:
        self._queue: Deque[Dict[str, Any]] = deque()
        self._current: Optional[Dict[str, Any]] = None
        self._logs: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._stop_token = 0
        self._step_delay = step_delay
        self._steps = steps
        self._executor = executor
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def enqueue(self, action: str, params: Dict[str, Any]) -> str:
        task_id = str(uuid4())
        task = {
            "id": task_id,
            "request_id": task_id,
            "step_id": f"{task_id}:1",
            "action": action,
            "params": params,
            "params_redacted": redact_params(action, params),
            "status": "queued",
            "result": None,
        }
        with self._lock:
            self._queue.append(task)
            self._log_event("queued", task)
        return task_id

    def stop_all(self) -> Dict[str, Any]:
        with self._lock:
            self._stop_token += 1
            cancelled = []
            while self._queue:
                task = self._queue.popleft()
                task["status"] = "cancelled"
                cancelled.append(task["id"])
                self._log_event("cancelled", task, detail="queue_cleared")

            if self._current is not None:
                self._current["status"] = "cancelled"
                self._log_event("cancelled", self._current, detail="stop_requested")

            return {
                "ok": True,
                "cancelled_queue": cancelled,
                "current": self._current["id"] if self._current else None,
            }

    def status(self) -> Dict[str, Any]:
        with self._lock:
            queue_snapshot = list(self._queue)
            current_snapshot = dict(self._current) if self._current else None
        return {
            "current": current_snapshot,
            "queued": queue_snapshot,
        }

    def logs(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._logs)

    def _run(self) -> None:
        while True:
            task = None
            with self._lock:
                if self._queue:
                    task = self._queue.popleft()
                    self._current = task
                    task["status"] = "running"
                    self._log_event("running", task)
                    stop_token = self._stop_token
                else:
                    self._current = None
                    stop_token = self._stop_token

            if task is None:
                time.sleep(0.1)
                continue

            if self._should_stop(stop_token):
                self._mark_cancelled(task, "stop_requested")
                continue

            result = self._execute_action(task, stop_token)
            status = result.get("status")
            task["result"] = result
            if status == "stopped":
                self._mark_stopped(task, result)
            elif status == "failed":
                self._mark_failed(task, result)
            else:
                self._mark_completed(task, result)

    def _execute_action(self, task: Dict[str, Any], stop_token: int) -> Dict[str, Any]:
        for _ in range(self._steps):
            time.sleep(self._step_delay)
            if self._should_stop(stop_token):
                return {
                    "status": "stopped",
                    "message": "stopped_before_execute",
                    "error_code": "stopped",
                    "duration_ms": 0,
                }

        return self._executor.execute(
            task["action"],
            task["params"],
            lambda: self._should_stop(stop_token),
        )

    def _should_stop(self, stop_token: int) -> bool:
        with self._lock:
            return self._stop_token != stop_token

    def _mark_cancelled(self, task: Dict[str, Any], detail: str) -> None:
        with self._lock:
            task["status"] = "cancelled"
            self._log_event("cancelled", task, detail=detail)

    def _mark_stopped(self, task: Dict[str, Any], result: Dict[str, Any]) -> None:
        with self._lock:
            task["status"] = "stopped"
            self._log_event("stopped", task, detail=result)

    def _mark_failed(self, task: Dict[str, Any], result: Dict[str, Any]) -> None:
        with self._lock:
            task["status"] = "failed"
            self._log_event("failed", task, detail=result)

    def _mark_completed(self, task: Dict[str, Any], result: Dict[str, Any]) -> None:
        with self._lock:
            task["status"] = "completed"
            self._log_event("completed", task, detail=result)

    def _log_event(
        self,
        event: str,
        task: Dict[str, Any],
        detail: Optional[str] = None,
    ) -> None:
        self._logs.append(
            {
                "ts": time.time(),
                "event": event,
                "request_id": task["request_id"],
                "step_id": task["step_id"],
                "task_id": task["id"],
                "action": task["action"],
                "params": task.get("params_redacted"),
                "status": task["status"],
                "detail": detail,
            }
        )
