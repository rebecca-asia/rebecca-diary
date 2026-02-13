"""Tests for domain/presence.py — status determination and time context."""

import unittest
from datetime import datetime, timezone, timedelta

from domain.presence import determine_status, get_time_context, evaluate
from domain.constants import (
    ONLINE_THRESHOLD_SEC,
    AWAY_THRESHOLD_SEC,
    SLEEPING_THRESHOLD_SEC,
    TIME_PERIODS,
    TIME_MESSAGES,
)

JST = timezone(timedelta(hours=9))


class TestDetermineStatus(unittest.TestCase):
    """Test presence status determination."""

    def test_online(self):
        result = determine_status(True, 60, "active")
        self.assertEqual(result["status"], "online")

    def test_away(self):
        result = determine_status(True, ONLINE_THRESHOLD_SEC + 1, "active")
        self.assertEqual(result["status"], "away")

    def test_away_boundary(self):
        # Exactly at ONLINE_THRESHOLD_SEC -> away (>= check)
        result = determine_status(True, ONLINE_THRESHOLD_SEC, "active")
        self.assertEqual(result["status"], "away")

    def test_sleeping_deep_night(self):
        result = determine_status(False, SLEEPING_THRESHOLD_SEC + 1, "deep_night")
        self.assertEqual(result["status"], "sleeping")

    def test_sleeping_requires_deep_night(self):
        # Not deep_night -> should be offline, not sleeping
        result = determine_status(False, SLEEPING_THRESHOLD_SEC + 1, "morning")
        self.assertEqual(result["status"], "offline")

    def test_offline_gateway_dead(self):
        result = determine_status(False, 60, "active")
        self.assertEqual(result["status"], "offline")

    def test_offline_no_activity(self):
        result = determine_status(True, None, "active")
        self.assertEqual(result["status"], "offline")

    def test_offline_long_inactive(self):
        result = determine_status(True, AWAY_THRESHOLD_SEC + 1, "active")
        self.assertEqual(result["status"], "offline")

    def test_all_statuses_have_label_and_emoji(self):
        cases = [
            (True, 60, "active"),           # online
            (True, 2000, "active"),          # away
            (False, 4000, "deep_night"),     # sleeping
            (False, 60, "active"),           # offline
        ]
        for gw, inactive, period in cases:
            result = determine_status(gw, inactive, period)
            self.assertIn("status", result)
            self.assertIn("label", result)
            self.assertIn("emoji", result)


class TestGetTimeContext(unittest.TestCase):
    """Test time period determination for all 24 hours."""

    def test_all_24_hours_covered(self):
        for hour in range(24):
            result = get_time_context(hour)
            self.assertIn("period", result)
            self.assertIn("message", result)
            self.assertIn(result["period"], TIME_MESSAGES)

    def test_late_night(self):
        for hour in [0, 1]:
            result = get_time_context(hour)
            self.assertEqual(result["period"], "late_night")

    def test_deep_night(self):
        for hour in [2, 3, 4, 5]:
            result = get_time_context(hour)
            self.assertEqual(result["period"], "deep_night")

    def test_morning(self):
        for hour in [6, 7, 8]:
            result = get_time_context(hour)
            self.assertEqual(result["period"], "morning")

    def test_active(self):
        for hour in [9, 10, 11]:
            result = get_time_context(hour)
            self.assertEqual(result["period"], "active")

    def test_afternoon(self):
        for hour in [12, 13, 14, 15, 16, 17]:
            result = get_time_context(hour)
            self.assertEqual(result["period"], "afternoon")

    def test_evening(self):
        for hour in [18, 19, 20]:
            result = get_time_context(hour)
            self.assertEqual(result["period"], "evening")

    def test_night(self):
        for hour in [21, 22, 23]:
            result = get_time_context(hour)
            self.assertEqual(result["period"], "night")

    def test_message_from_correct_pool(self):
        result = get_time_context(3)  # deep_night
        self.assertEqual(result["period"], "deep_night")
        self.assertIn(result["message"], TIME_MESSAGES["deep_night"])


class TestEvaluate(unittest.TestCase):
    """Test the full evaluate() integration function."""

    def test_online_evaluation(self):
        now = datetime(2026, 2, 13, 14, 30, 0, tzinfo=JST)
        last_activity = datetime(2026, 2, 13, 14, 25, 0, tzinfo=JST)
        result = evaluate(True, last_activity, now)
        self.assertEqual(result["status"], "online")
        self.assertIn("time_context", result)
        self.assertEqual(result["time_context"]["period"], "afternoon")

    def test_offline_no_activity(self):
        now = datetime(2026, 2, 13, 10, 0, 0, tzinfo=JST)
        result = evaluate(False, None, now)
        self.assertEqual(result["status"], "offline")

    def test_sleeping_deep_night(self):
        now = datetime(2026, 2, 13, 3, 0, 0, tzinfo=JST)
        # Last activity 2 hours ago
        last_activity = datetime(2026, 2, 13, 1, 0, 0, tzinfo=JST)
        result = evaluate(False, last_activity, now)
        self.assertEqual(result["status"], "sleeping")


if __name__ == "__main__":
    unittest.main()
