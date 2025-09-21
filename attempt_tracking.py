import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Optional


def _load_json(path: str, default):
    if not os.path.exists(path):
        return default.copy() if isinstance(default, dict) else list(default)
    with open(path, "r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError:
            return default.copy() if isinstance(default, dict) else list(default)


def _save_json(path: str, payload) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


@dataclass
class AttemptOutcome:
    question_id: str
    correct: bool
    timestamp: datetime
    metadata: Optional[Dict[str, str]] = None


class AttemptTracker:
    """Persist question attempt outcomes and manage review scheduling."""

    def __init__(
        self,
        log_path: str = "attempt_log.json",
        queue_path: str = "review_queue.json",
        base_interval_minutes: int = 15,
    ) -> None:
        self.log_path = log_path
        self.queue_path = queue_path
        self.base_interval_minutes = base_interval_minutes
        self._log: Dict[str, Dict[str, List[Dict[str, object]]]] = _load_json(self.log_path, {})
        self._queue: Dict[str, str] = _load_json(self.queue_path, {})

    @staticmethod
    def _ensure_datetime(value: Optional[datetime]) -> datetime:
        if value is None:
            return datetime.now(timezone.utc)
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _persist(self) -> None:
        _save_json(self.log_path, self._log)
        _save_json(self.queue_path, self._queue)

    def _count_incorrect_attempts(self, question_id: str) -> int:
        attempts = self._log.get(question_id, {}).get("attempts", [])
        return sum(1 for attempt in attempts if not attempt.get("correct", False))

    def _interval_for_attempt(self, incorrect_attempts: int) -> timedelta:
        exponent = max(0, incorrect_attempts - 1)
        minutes = self.base_interval_minutes * (2 ** exponent)
        return timedelta(minutes=minutes)

    def _schedule_next_review(self, question_id: str, timestamp: datetime) -> str:
        incorrect_attempts = self._count_incorrect_attempts(question_id)
        interval = self._interval_for_attempt(incorrect_attempts)
        revisit_time = timestamp + interval
        revisit_iso = revisit_time.isoformat()
        self._log.setdefault(question_id, {}).update({"next_review": revisit_iso})
        self._queue[question_id] = revisit_iso
        return revisit_iso

    def record_attempt(
        self,
        question_id: str,
        correct: bool,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        moment = self._ensure_datetime(timestamp)
        attempt_entry = {
            "timestamp": moment.isoformat(),
            "correct": bool(correct),
        }
        if metadata:
            attempt_entry["metadata"] = metadata

        question_log = self._log.setdefault(question_id, {"attempts": [], "next_review": None})
        question_log.setdefault("attempts", []).append(attempt_entry)

        next_review: Optional[str] = None
        if correct:
            question_log["next_review"] = None
            if question_id in self._queue:
                del self._queue[question_id]
        else:
            next_review = self._schedule_next_review(question_id, moment)

        self._persist()
        return next_review

    def get_items_for_export(self, current_time: Optional[datetime] = None) -> List[str]:
        now = self._ensure_datetime(current_time)
        ready: List[str] = []
        for question_id, revisit_iso in self._queue.items():
            try:
                revisit_time = datetime.fromisoformat(revisit_iso)
            except ValueError:
                revisit_time = now
            if revisit_time.tzinfo is None:
                revisit_time = revisit_time.replace(tzinfo=timezone.utc)
            if revisit_time <= now:
                ready.append(question_id)
        ready.sort()
        return ready

    def mark_exported(self, question_ids: Iterable[str]) -> None:
        removed = False
        for question_id in question_ids:
            if question_id in self._queue:
                del self._queue[question_id]
                removed = True
        if removed:
            self._persist()

    def get_attempts(self, question_id: str) -> List[Dict[str, object]]:
        return list(self._log.get(question_id, {}).get("attempts", []))

    def get_next_review(self, question_id: str) -> Optional[str]:
        return self._log.get(question_id, {}).get("next_review")
