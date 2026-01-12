import time
import unittest

from src.queue_manager import QueueManager


class QueueManagerTest(unittest.TestCase):
    def test_stop_cancels_running_and_queued(self) -> None:
        manager = QueueManager(step_delay=0.01, steps=50)

        first_id = manager.enqueue("ping", {})
        second_id = manager.enqueue("ping", {})

        self._wait_for_running(manager)
        result = manager.stop_all()

        self.assertTrue(result["ok"])
        self.assertIn(second_id, result["cancelled_queue"])
        self.assertEqual(result["current"], first_id)

        self._wait_for_idle(manager)
        status = manager.status()
        self.assertIsNone(status["current"])
        self.assertEqual(status["queued"], [])

    def _wait_for_running(self, manager: QueueManager) -> None:
        deadline = time.time() + 1.0
        while time.time() < deadline:
            if manager.status()["current"] is not None:
                return
            time.sleep(0.01)
        self.fail("timeout waiting for running task")

    def _wait_for_idle(self, manager: QueueManager) -> None:
        deadline = time.time() + 1.0
        while time.time() < deadline:
            status = manager.status()
            if status["current"] is None and not status["queued"]:
                return
            time.sleep(0.01)
        self.fail("timeout waiting for idle queue")


if __name__ == "__main__":
    unittest.main()
