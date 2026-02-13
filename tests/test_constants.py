"""Tests for domain/constants.py — structural integrity of constant tables."""

import unittest

from domain.constants import (
    CPU_THRESHOLDS, CPU_LABELS,
    MEMORY_THRESHOLDS, MEMORY_LABELS,
    DISK_THRESHOLDS, DISK_LABELS,
    TEMPERATURE_THRESHOLDS, TEMPERATURE_LABELS,
    UPTIME_THRESHOLDS_DAYS, UPTIME_LABELS,
    OVERALL_SCORE_TABLE,
    ALERT_MESSAGES,
    TIME_PERIODS, TIME_MESSAGES,
    STATUS_LABELS,
    EXP_TABLE,
    SKILL_LEVEL_LABELS,
    STALENESS_FRESH_MAX_MIN, STALENESS_STALE_MAX_MIN,
)


class TestThresholdStructure(unittest.TestCase):
    """All threshold lists must be ascending and end with None."""

    def _check_ascending(self, thresholds, name):
        values = [t[0] for t in thresholds if t[0] is not None]
        for i in range(1, len(values)):
            self.assertGreater(values[i], values[i - 1],
                               f"{name}: thresholds not ascending at index {i}")

    def _check_none_last(self, thresholds, name):
        self.assertIsNone(thresholds[-1][0],
                          f"{name}: last threshold must be None (catch-all)")

    def test_cpu_thresholds(self):
        self._check_ascending(CPU_THRESHOLDS, "CPU")
        self._check_none_last(CPU_THRESHOLDS, "CPU")

    def test_memory_thresholds(self):
        self._check_ascending(MEMORY_THRESHOLDS, "Memory")
        self._check_none_last(MEMORY_THRESHOLDS, "Memory")

    def test_disk_thresholds(self):
        self._check_ascending(DISK_THRESHOLDS, "Disk")
        self._check_none_last(DISK_THRESHOLDS, "Disk")

    def test_temperature_thresholds(self):
        self._check_ascending(TEMPERATURE_THRESHOLDS, "Temperature")
        self._check_none_last(TEMPERATURE_THRESHOLDS, "Temperature")

    def test_uptime_thresholds(self):
        self._check_ascending(UPTIME_THRESHOLDS_DAYS, "Uptime")
        self._check_none_last(UPTIME_THRESHOLDS_DAYS, "Uptime")


class TestLabelCoverage(unittest.TestCase):
    """Every state in a threshold table must have a matching label entry."""

    def _check_coverage(self, thresholds, labels, name):
        states = [t[1] for t in thresholds]
        for state in states:
            self.assertIn(state, labels,
                          f"{name}: state '{state}' missing from labels")
            self.assertIn("label", labels[state])
            self.assertIn("message", labels[state])

    def test_cpu_label_coverage(self):
        self._check_coverage(CPU_THRESHOLDS, CPU_LABELS, "CPU")

    def test_memory_label_coverage(self):
        self._check_coverage(MEMORY_THRESHOLDS, MEMORY_LABELS, "Memory")

    def test_disk_label_coverage(self):
        self._check_coverage(DISK_THRESHOLDS, DISK_LABELS, "Disk")

    def test_temperature_label_coverage(self):
        self._check_coverage(TEMPERATURE_THRESHOLDS, TEMPERATURE_LABELS, "Temperature")

    def test_uptime_label_coverage(self):
        self._check_coverage(UPTIME_THRESHOLDS_DAYS, UPTIME_LABELS, "Uptime")


class TestOverallScoreTable(unittest.TestCase):
    """Overall score table must be descending (checked in order, first match wins)."""

    def test_descending_min_scores(self):
        scores = [entry[0] for entry in OVERALL_SCORE_TABLE]
        for i in range(1, len(scores)):
            self.assertLess(scores[i], scores[i - 1],
                            f"OVERALL_SCORE_TABLE: not descending at index {i}")

    def test_all_entries_have_5_fields(self):
        for entry in OVERALL_SCORE_TABLE:
            self.assertEqual(len(entry), 5,
                             f"Entry {entry} should have 5 fields")

    def test_lowest_score_is_0(self):
        self.assertEqual(OVERALL_SCORE_TABLE[-1][0], 0)


class TestTimePeriods(unittest.TestCase):
    """TIME_PERIODS must cover all 24 hours without gaps."""

    def test_full_24h_coverage(self):
        covered = set()
        for start, end, _ in TIME_PERIODS:
            for h in range(start, end):
                covered.add(h)
        self.assertEqual(covered, set(range(24)),
                         "TIME_PERIODS does not cover all 24 hours")

    def test_no_overlaps(self):
        all_hours = []
        for start, end, _ in TIME_PERIODS:
            all_hours.extend(range(start, end))
        self.assertEqual(len(all_hours), len(set(all_hours)),
                         "TIME_PERIODS has overlapping hours")

    def test_all_periods_have_messages(self):
        for _, _, period in TIME_PERIODS:
            self.assertIn(period, TIME_MESSAGES,
                          f"Period '{period}' missing from TIME_MESSAGES")
            self.assertIsInstance(TIME_MESSAGES[period], list)
            self.assertGreater(len(TIME_MESSAGES[period]), 0)


class TestStatusLabels(unittest.TestCase):
    def test_all_statuses_present(self):
        for status in ("online", "away", "sleeping", "offline"):
            self.assertIn(status, STATUS_LABELS)
            self.assertIn("label", STATUS_LABELS[status])
            self.assertIn("emoji", STATUS_LABELS[status])


class TestAlertMessages(unittest.TestCase):
    def test_levels_1_to_3(self):
        for level in (1, 2, 3):
            self.assertIn(level, ALERT_MESSAGES)
            self.assertIsInstance(ALERT_MESSAGES[level], list)
            self.assertGreater(len(ALERT_MESSAGES[level]), 0)

    def test_level_0_not_present(self):
        self.assertNotIn(0, ALERT_MESSAGES)


class TestExpTable(unittest.TestCase):
    def test_ascending(self):
        for i in range(1, len(EXP_TABLE)):
            self.assertGreater(EXP_TABLE[i], EXP_TABLE[i - 1],
                               f"EXP_TABLE not ascending at index {i}")

    def test_starts_at_zero(self):
        self.assertEqual(EXP_TABLE[0], 0)

    def test_length(self):
        self.assertEqual(len(EXP_TABLE), 20)


class TestStaleness(unittest.TestCase):
    def test_fresh_less_than_stale(self):
        self.assertLess(STALENESS_FRESH_MAX_MIN, STALENESS_STALE_MAX_MIN)


class TestSkillLevelLabels(unittest.TestCase):
    def test_levels_1_to_10(self):
        for level in range(1, 11):
            self.assertIn(level, SKILL_LEVEL_LABELS)
            self.assertIsInstance(SKILL_LEVEL_LABELS[level], str)


if __name__ == "__main__":
    unittest.main()
