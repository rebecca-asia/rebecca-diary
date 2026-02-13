"""Tests for domain/health.py — classification, scoring, and alerts."""

import unittest

from domain.health import (
    _classify,
    classify_cpu,
    classify_memory,
    classify_disk,
    classify_temperature,
    classify_uptime,
    calculate_overall_score,
    determine_alert_level,
    get_alert_message,
    evaluate,
)
from domain.constants import CPU_THRESHOLDS, ALERT_MESSAGES


class TestClassifyGeneric(unittest.TestCase):
    """Test the generic _classify helper."""

    def test_below_first_threshold(self):
        self.assertEqual(_classify(10, CPU_THRESHOLDS), "idle")

    def test_at_exact_boundary(self):
        # value == threshold means it does NOT match that bracket (strict <)
        self.assertEqual(_classify(20, CPU_THRESHOLDS), "clear")

    def test_just_below_boundary(self):
        self.assertEqual(_classify(19.99, CPU_THRESHOLDS), "idle")

    def test_catch_all(self):
        self.assertEqual(_classify(100, CPU_THRESHOLDS), "critical")


class TestClassifyCPU(unittest.TestCase):
    """Test CPU classification with boundary values."""

    def test_idle(self):
        result = classify_cpu(0)
        self.assertEqual(result["state"], "idle")
        self.assertIn("label", result)

    def test_boundary_idle_to_clear(self):
        self.assertEqual(classify_cpu(19.99)["state"], "idle")
        self.assertEqual(classify_cpu(20.0)["state"], "clear")

    def test_boundary_clear_to_busy(self):
        self.assertEqual(classify_cpu(49.99)["state"], "clear")
        self.assertEqual(classify_cpu(50.0)["state"], "busy")

    def test_boundary_busy_to_heavy(self):
        self.assertEqual(classify_cpu(69.99)["state"], "busy")
        self.assertEqual(classify_cpu(70.0)["state"], "heavy")

    def test_boundary_heavy_to_critical(self):
        self.assertEqual(classify_cpu(84.99)["state"], "heavy")
        self.assertEqual(classify_cpu(85.0)["state"], "critical")

    def test_critical_extreme(self):
        self.assertEqual(classify_cpu(100)["state"], "critical")

    def test_all_states_have_label_and_message(self):
        for pct in [0, 30, 60, 75, 90]:
            result = classify_cpu(pct)
            self.assertIn("state", result)
            self.assertIn("label", result)
            self.assertIn("message", result)


class TestClassifyMemory(unittest.TestCase):
    def test_spacious(self):
        self.assertEqual(classify_memory(30)["state"], "spacious")

    def test_comfortable(self):
        self.assertEqual(classify_memory(55)["state"], "comfortable")

    def test_normal(self):
        self.assertEqual(classify_memory(70)["state"], "normal")

    def test_tight(self):
        self.assertEqual(classify_memory(90)["state"], "tight")

    def test_critical(self):
        self.assertEqual(classify_memory(95)["state"], "critical")


class TestClassifyDisk(unittest.TestCase):
    def test_spacious(self):
        self.assertEqual(classify_disk(40)["state"], "spacious")

    def test_normal(self):
        self.assertEqual(classify_disk(70)["state"], "normal")

    def test_tight(self):
        self.assertEqual(classify_disk(90)["state"], "tight")

    def test_critical(self):
        self.assertEqual(classify_disk(95)["state"], "critical")


class TestClassifyTemperature(unittest.TestCase):
    def test_none_returns_none(self):
        self.assertIsNone(classify_temperature(None))

    def test_cool(self):
        self.assertEqual(classify_temperature(30)["state"], "cool")

    def test_comfortable(self):
        self.assertEqual(classify_temperature(50)["state"], "comfortable")

    def test_warm(self):
        self.assertEqual(classify_temperature(60)["state"], "warm")

    def test_hot(self):
        self.assertEqual(classify_temperature(75)["state"], "hot")

    def test_critical(self):
        self.assertEqual(classify_temperature(85)["state"], "critical")


class TestClassifyUptime(unittest.TestCase):
    def test_fresh(self):
        # Less than 1 day
        self.assertEqual(classify_uptime(3600)["state"], "fresh")

    def test_normal(self):
        # 2 days
        self.assertEqual(classify_uptime(2 * 86400)["state"], "normal")

    def test_tired(self):
        # 5 days
        self.assertEqual(classify_uptime(5 * 86400)["state"], "tired")

    def test_exhausted(self):
        # 10 days
        self.assertEqual(classify_uptime(10 * 86400)["state"], "exhausted")

    def test_boundary_fresh_to_normal(self):
        # Just under 1 day
        self.assertEqual(classify_uptime(86399)["state"], "fresh")
        # Exactly 1 day
        self.assertEqual(classify_uptime(86400)["state"], "normal")


class TestOverallScore(unittest.TestCase):
    def test_idle_mac_scores_great(self):
        # Idle Mac: CPU ~15%, Mem ~60%, Disk ~50%, no temp, 1h uptime
        result = calculate_overall_score(15, 60, 50, None, 3600)
        self.assertGreaterEqual(result["score"], 80)
        self.assertEqual(result["state"], "great")

    def test_critical_mac_scores_low(self):
        # All maxed out
        result = calculate_overall_score(100, 100, 100, 100, 30 * 86400)
        self.assertLess(result["score"], 20)

    def test_score_clamped_to_0_100(self):
        result = calculate_overall_score(0, 0, 0, None, 0)
        self.assertLessEqual(result["score"], 100)
        self.assertGreaterEqual(result["score"], 0)

        result = calculate_overall_score(100, 100, 100, 100, 100 * 86400)
        self.assertGreaterEqual(result["score"], 0)

    def test_all_states_reachable(self):
        # great
        r = calculate_overall_score(10, 50, 40, None, 0)
        self.assertEqual(r["state"], "great")

        # good
        r = calculate_overall_score(30, 70, 50, None, 1 * 86400)
        self.assertEqual(r["state"], "good")

        # poor — penalty: cpu(40-20)*1=20, mem(75-60)*1.5=22.5, disk(0), temp(0), uptime=2 => ~55.5 => score~44
        r = calculate_overall_score(40, 75, 50, None, 1 * 86400)
        self.assertEqual(r["state"], "poor")

        # bad — penalty: cpu(70-20)*1=50, mem(90-60)*1.5=45, disk(0), temp(0), uptime=4 => ~91 => score~9
        r = calculate_overall_score(70, 90, 50, None, 2 * 86400)
        self.assertIn(r["state"], ("bad", "critical"))

    def test_result_has_required_fields(self):
        result = calculate_overall_score(50, 70, 60, 55, 86400)
        for key in ("score", "state", "emoji", "label", "message"):
            self.assertIn(key, result)


class TestAlertLevel(unittest.TestCase):
    def test_level_0_all_normal(self):
        self.assertEqual(determine_alert_level(["idle", "spacious", "normal"], 90), 0)

    def test_level_1_heavy(self):
        self.assertEqual(determine_alert_level(["heavy", "normal", "normal"], 70), 1)

    def test_level_1_tight(self):
        self.assertEqual(determine_alert_level(["idle", "tight", "normal"], 60), 1)

    def test_level_2_one_critical(self):
        self.assertEqual(determine_alert_level(["critical", "normal", "normal"], 50), 2)

    def test_level_3_two_critical(self):
        self.assertEqual(determine_alert_level(["critical", "critical", "normal"], 40), 3)

    def test_level_3_low_score(self):
        self.assertEqual(determine_alert_level(["normal", "normal"], 15), 3)

    def test_empty_states_level_0(self):
        self.assertEqual(determine_alert_level([], 80), 0)


class TestAlertMessage(unittest.TestCase):
    def test_level_0_returns_none(self):
        self.assertIsNone(get_alert_message(0))

    def test_level_1_returns_string(self):
        msg = get_alert_message(1)
        self.assertIsInstance(msg, str)
        self.assertIn(msg, ALERT_MESSAGES[1])

    def test_level_2_returns_string(self):
        msg = get_alert_message(2)
        self.assertIn(msg, ALERT_MESSAGES[2])

    def test_level_3_returns_string(self):
        msg = get_alert_message(3)
        self.assertIn(msg, ALERT_MESSAGES[3])


class TestEvaluate(unittest.TestCase):
    def test_basic_evaluation(self):
        raw = {
            "cpu_usage": 15,
            "mem_usage": 60,
            "disk_usage": 50,
            "temperature": None,
            "uptime_seconds": 3600,
        }
        result = evaluate(raw)
        self.assertIn("cpu", result)
        self.assertIn("memory", result)
        self.assertIn("disk", result)
        self.assertIn("temperature", result)
        self.assertIn("uptime", result)
        self.assertIn("overall", result)
        self.assertIn("alert_level", result)
        self.assertIn("alert_message", result)
        self.assertIsNone(result["temperature"])

    def test_with_temperature(self):
        raw = {
            "cpu_usage": 30,
            "mem_usage": 70,
            "disk_usage": 60,
            "temperature": 55,
            "uptime_seconds": 86400,
        }
        result = evaluate(raw)
        self.assertIsNotNone(result["temperature"])
        self.assertIn("state", result["temperature"])

    def test_defaults_for_missing_keys(self):
        result = evaluate({})
        self.assertEqual(result["cpu"]["state"], "idle")
        self.assertEqual(result["alert_level"], 0)


if __name__ == "__main__":
    unittest.main()
