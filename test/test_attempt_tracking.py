from datetime import datetime, timedelta, timezone

from attempt_tracking import AttemptTracker


def test_incorrect_attempt_schedules_revisit(tmp_path):
    log_path = tmp_path / "attempts.json"
    queue_path = tmp_path / "queue.json"
    tracker = AttemptTracker(str(log_path), str(queue_path), base_interval_minutes=10)

    now = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    next_review = tracker.record_attempt("q1", correct=False, timestamp=now)

    assert next_review is not None
    expected_time = now + timedelta(minutes=10)
    assert tracker.get_next_review("q1") == expected_time.isoformat()

    ready = tracker.get_items_for_export(expected_time)
    assert ready == ["q1"]

    tracker.mark_exported(["q1"])
    assert tracker.get_items_for_export(expected_time) == []


def test_repeated_incorrect_attempts_expand_interval(tmp_path):
    log_path = tmp_path / "attempts.json"
    queue_path = tmp_path / "queue.json"
    tracker = AttemptTracker(str(log_path), str(queue_path), base_interval_minutes=5)

    start = datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc)
    tracker.record_attempt("q42", correct=False, timestamp=start)

    first_revisit = datetime.fromisoformat(tracker.get_next_review("q42"))
    assert first_revisit == start + timedelta(minutes=5)

    second_attempt_time = first_revisit
    tracker.record_attempt("q42", correct=False, timestamp=second_attempt_time)

    second_revisit = datetime.fromisoformat(tracker.get_next_review("q42"))
    assert second_revisit == second_attempt_time + timedelta(minutes=10)

    ready_before_time = tracker.get_items_for_export(second_revisit - timedelta(minutes=1))
    assert ready_before_time == []

    ready_after_time = tracker.get_items_for_export(second_revisit)
    assert ready_after_time == ["q42"]
