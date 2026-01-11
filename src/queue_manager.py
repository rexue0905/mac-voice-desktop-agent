import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional
from uuid import uuid4


class QueueManager:
    def __init__(self, *, step_delay: float = 0.05, steps: int = 5) -> None:
        self._queue: Deque[Dict[str, Any]] = deque()
        self._current: Optional[Dict[str, Any]] = None
        self._logs: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._stop_token = 0
        self._step_delay = step_delay
        self._steps = steps
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def enqueue(self, action: str, params: Dict[str, Any]) -> str:
        task_id = str(uuid4())
        task = {
            "id": task_id,
            "action": action,
            "params": params,
            "status": "queued",
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

            cancelled = self._execute_action(task, stop_token)
            if cancelled:
                self._mark_cancelled(task, "stop_requested")
            else:
                self._mark_completed(task)

    def _execute_action(self, task: Dict[str, Any], stop_token: int) -> bool:
        # 模块 4：仅模拟执行时间，实际执行器在后续模块实现
        for _ in range(self._steps):
            time.sleep(self._step_delay)
            if self._should_stop(stop_token):
                return True
        return False

    def _should_stop(self, stop_token: int) -> bool:
        with self._lock:
            return self._stop_token != stop_token

    def _mark_cancelled(self, task: Dict[str, Any], detail: str) -> None:
        with self._lock:
            task["status"] = "cancelled"
            self._log_event("cancelled", task, detail=detail)

    def _mark_completed(self, task: Dict[str, Any]) -> None:
        with self._lock:
            task["status"] = "completed"
            self._log_event("completed", task)

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
                "task_id": task["id"],
                "action": task["action"],
                "status": task["status"],
                "detail": detail,
            }
        )
