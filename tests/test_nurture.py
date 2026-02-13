"""Tests for domain/nurture.py — nurture parameter calculations."""

import unittest
from datetime import datetime, timezone, timedelta

from domain.nurture import (
    calc_health,
    calc_energy,
    classify_energy,
    calc_mood,
    classify_mood,
    calc_trust,
    calc_intimacy,
    calc_exp,
    calc_level,
    get_next_level_exp,
    get_current_level_exp,
    calc_day,
    update_visits,
    evaluate,
)
from domain.constants import (
    NURTURE_FIRST_DAY,
    EXP_TABLE,
    EXP_EXTRAPOLATION_STEP,
    ENERGY_BASE,
    ENERGY_THRESHOLDS,
    MOOD_THRESHOLDS,
)

JST = timezone(timedelta(hours=9))


class TestCalcHealth(unittest.TestCase):
    """Test health score extraction."""

    def test_none_returns_50(self):
        self.assertEqual(calc_health(None), 50)

    def test_normal_value(self):
        self.assertEqual(calc_health(75), 75)

    def test_clamped_to_0(self):
        self.assertEqual(calc_health(-10), 0)

    def test_clamped_to_100(self):
        self.assertEqual(calc_health(150), 100)

    def test_float_truncated(self):
        self.assertEqual(calc_health(75.9), 75)


class TestCalcEnergy(unittest.TestCase):
    """Test energy calculation from uptime and time period."""

    def test_base_energy_no_inputs(self):
        self.assertEqual(calc_energy(None, None), ENERGY_BASE)

    def test_low_uptime_no_penalty(self):
        # 4 hours = below threshold, no penalty
        self.assertEqual(calc_energy(4 * 3600, "active"), ENERGY_BASE)

    def test_uptime_penalty(self):
        # 20 hours = 12h over threshold => 36 penalty
        result = calc_energy(20 * 3600, "active")
        self.assertLess(result, ENERGY_BASE)
        self.assertEqual(result, ENERGY_BASE - 36)

    def test_uptime_penalty_capped(self):
        # 100 hours = way over, but penalty capped at 40
        result = calc_energy(100 * 3600, "active")
        self.assertEqual(result, ENERGY_BASE - 40)

    def test_deep_night_modifier(self):
        result = calc_energy(0, "deep_night")
        self.assertEqual(result, ENERGY_BASE - 20)

    def test_late_night_modifier(self):
        result = calc_energy(0, "late_night")
        self.assertEqual(result, ENERGY_BASE - 10)

    def test_combined_penalty_and_modifier(self):
        # 16h uptime + deep_night
        uptime = 16 * 3600  # 8h over threshold => 24 penalty
        result = calc_energy(uptime, "deep_night")
        self.assertEqual(result, ENERGY_BASE - 24 - 20)

    def test_energy_never_below_0(self):
        result = calc_energy(200 * 3600, "deep_night")
        self.assertGreaterEqual(result, 0)

    def test_energy_never_above_100(self):
        result = calc_energy(0, "active")
        self.assertLessEqual(result, 100)


class TestClassifyEnergy(unittest.TestCase):
    """Test energy classification with boundary values."""

    def test_energetic(self):
        result = classify_energy(80)
        self.assertEqual(result["state"], "energetic")

    def test_boundary_energetic(self):
        result = classify_energy(70)
        self.assertEqual(result["state"], "energetic")

    def test_normal(self):
        result = classify_energy(50)
        self.assertEqual(result["state"], "normal")

    def test_boundary_normal(self):
        result = classify_energy(40)
        self.assertEqual(result["state"], "normal")

    def test_tired(self):
        result = classify_energy(30)
        self.assertEqual(result["state"], "tired")

    def test_boundary_tired(self):
        result = classify_energy(20)
        self.assertEqual(result["state"], "tired")

    def test_exhausted(self):
        result = classify_energy(10)
        self.assertEqual(result["state"], "exhausted")

    def test_exhausted_zero(self):
        result = classify_energy(0)
        self.assertEqual(result["state"], "exhausted")

    def test_all_states_have_label(self):
        for val in [80, 50, 25, 5]:
            result = classify_energy(val)
            self.assertIn("label", result)
            self.assertIn("state", result)


class TestCalcMood(unittest.TestCase):
    """Test mood calculation from 4 factors."""

    def test_perfect_conditions(self):
        # health=100, energy=100, streak>=7+visits, active period
        visit_data = {"streak": 7, "today_visits": 1}
        result = calc_mood(100, 100, visit_data, "active")
        # 100*0.4 + 100*0.2 + 20 + 16 = 96
        self.assertEqual(result, 96)

    def test_worst_conditions(self):
        visit_data = {"streak": 0, "today_visits": 0}
        result = calc_mood(0, 0, visit_data, "deep_night")
        # 0*0.4 + 0*0.2 + 10 + 4 = 14
        self.assertEqual(result, 14)

    def test_weights_sum_correctly(self):
        # All factors at neutral-ish
        visit_data = {"streak": 0, "today_visits": 0}
        result = calc_mood(50, 50, visit_data, "afternoon")
        # 50*0.4 + 50*0.2 + 10 + 14 = 54
        self.assertEqual(result, 54)

    def test_visit_streak_mid_boost(self):
        visit_data = {"streak": 3, "today_visits": 0}
        result = calc_mood(50, 50, visit_data, "active")
        # 50*0.4 + 50*0.2 + 14 + 16 = 60
        self.assertEqual(result, 60)

    def test_visit_today_boost(self):
        visit_data = {"streak": 0, "today_visits": 1}
        result = calc_mood(50, 50, visit_data, "active")
        # 50*0.4 + 50*0.2 + 16 + 16 = 62
        self.assertEqual(result, 62)

    def test_none_visit_data(self):
        result = calc_mood(50, 50, None, "active")
        # 50*0.4 + 50*0.2 + 10 + 16 = 56
        self.assertEqual(result, 56)

    def test_none_time_period(self):
        visit_data = {"streak": 0, "today_visits": 0}
        result = calc_mood(50, 50, visit_data, None)
        # 50*0.4 + 50*0.2 + 10 + 10 = 50
        self.assertEqual(result, 50)

    def test_clamped_to_100(self):
        visit_data = {"streak": 10, "today_visits": 5}
        result = calc_mood(100, 100, visit_data, "active")
        self.assertLessEqual(result, 100)


class TestClassifyMood(unittest.TestCase):
    """Test mood classification."""

    def test_great(self):
        result = classify_mood(85)
        self.assertEqual(result["state"], "great")

    def test_boundary_great(self):
        result = classify_mood(80)
        self.assertEqual(result["state"], "great")

    def test_good(self):
        result = classify_mood(70)
        self.assertEqual(result["state"], "good")

    def test_normal(self):
        result = classify_mood(50)
        self.assertEqual(result["state"], "normal")

    def test_down(self):
        result = classify_mood(25)
        self.assertEqual(result["state"], "down")

    def test_bad(self):
        result = classify_mood(10)
        self.assertEqual(result["state"], "bad")

    def test_bad_zero(self):
        result = classify_mood(0)
        self.assertEqual(result["state"], "bad")

    def test_all_have_message(self):
        for val in [90, 70, 50, 25, 5]:
            result = classify_mood(val)
            self.assertIn("message", result)
            self.assertIsNotNone(result["message"])


class TestCalcTrust(unittest.TestCase):
    """Test trust calculation (logarithmic growth)."""

    def test_zero_visits(self):
        result = calc_trust(0, 0)
        self.assertEqual(result, 10)  # base only, log10(1)=0

    def test_ten_visits_no_streak(self):
        result = calc_trust(10, 0)
        # 10 + min(70, 25 * log10(10)) = 10 + 25 = 35
        self.assertEqual(result, 35)

    def test_hundred_visits(self):
        result = calc_trust(100, 0)
        # 10 + min(70, 25 * 2) = 60
        self.assertEqual(result, 60)

    def test_streak_bonus(self):
        result = calc_trust(10, 5)
        base_result = calc_trust(10, 0)
        self.assertEqual(result, base_result + 10)  # 5 * 2 = 10

    def test_streak_bonus_capped(self):
        result = calc_trust(10, 100)
        base_result = calc_trust(10, 0)
        self.assertEqual(result, base_result + 15)  # capped at 15

    def test_trust_capped_at_100(self):
        result = calc_trust(1000000, 100)
        self.assertLessEqual(result, 100)


class TestCalcIntimacy(unittest.TestCase):
    """Test intimacy calculation (logarithmic growth)."""

    def test_zero_time(self):
        result = calc_intimacy(0, 0)
        # 5 + min(75, 23 * log10(0.1 + 1)) ≈ 5 + 0.99 = 5
        self.assertGreaterEqual(result, 5)

    def test_one_hour(self):
        result = calc_intimacy(60, 0)
        # 5 + min(75, 23 * log10(1 + 1)) ≈ 5 + 6.92 = 11
        self.assertGreater(result, 10)

    def test_ten_hours(self):
        result = calc_intimacy(600, 0)
        # 5 + min(75, 23 * log10(10 + 1)) ≈ 5 + 23.95 = 28
        self.assertGreater(result, 25)

    def test_today_bonus(self):
        result_with = calc_intimacy(60, 60)
        result_without = calc_intimacy(60, 0)
        # 60 / 6 = 10 bonus
        self.assertEqual(result_with, result_without + 10)

    def test_today_bonus_capped(self):
        result_high = calc_intimacy(60, 120)
        result_max = calc_intimacy(60, 60)
        # Both should cap at +10
        self.assertEqual(result_high, result_max)

    def test_intimacy_capped_at_100(self):
        result = calc_intimacy(10000000, 120)
        self.assertLessEqual(result, 100)


class TestCalcExp(unittest.TestCase):
    """Test EXP calculation from multiple sources."""

    def test_zero_everything(self):
        visit_data = {"total_visits": 0, "total_time_minutes": 0, "streak": 0}
        result = calc_exp(visit_data, 50, 0)
        # visit=0, time=0, streak=0, health=0 (50-50=0), skill=0
        self.assertEqual(result, 0)

    def test_visits_only(self):
        visit_data = {"total_visits": 10, "total_time_minutes": 0, "streak": 0}
        result = calc_exp(visit_data, 50, 0)
        # 10 * 10 = 100
        self.assertEqual(result, 100)

    def test_time_only(self):
        visit_data = {"total_visits": 0, "total_time_minutes": 50, "streak": 0}
        result = calc_exp(visit_data, 50, 0)
        # (50 // 5) * 2 = 20
        self.assertEqual(result, 20)

    def test_health_bonus(self):
        visit_data = {"total_visits": 0, "total_time_minutes": 0, "streak": 0}
        result = calc_exp(visit_data, 80, 0)
        # (80 - 50) * 2 = 60
        self.assertEqual(result, 60)

    def test_health_below_threshold_no_bonus(self):
        visit_data = {"total_visits": 0, "total_time_minutes": 0, "streak": 0}
        result = calc_exp(visit_data, 30, 0)
        self.assertEqual(result, 0)

    def test_skill_bonus(self):
        visit_data = {"total_visits": 0, "total_time_minutes": 0, "streak": 0}
        result = calc_exp(visit_data, 50, 5)
        # 5 * 50 = 250
        self.assertEqual(result, 250)

    def test_streak_bonus(self):
        visit_data = {"total_visits": 5, "total_time_minutes": 0, "streak": 3}
        result = calc_exp(visit_data, 50, 0)
        # visit=50, streak=5*3*5=75 => 125
        self.assertEqual(result, 125)

    def test_streak_capped(self):
        visit_data = {"total_visits": 1, "total_time_minutes": 0, "streak": 20}
        result = calc_exp(visit_data, 50, 0)
        # visit=10, streak=1*10*5=50 (capped at 10)
        self.assertEqual(result, 60)

    def test_none_visit_data(self):
        result = calc_exp(None, 80, 5)
        # health=(80-50)*2=60, skill=250
        self.assertEqual(result, 310)


class TestCalcLevel(unittest.TestCase):
    """Test level calculation from EXP."""

    def test_level_1(self):
        self.assertEqual(calc_level(0), 1)

    def test_level_2(self):
        self.assertEqual(calc_level(100), 2)

    def test_just_below_level_2(self):
        self.assertEqual(calc_level(99), 1)

    def test_level_20(self):
        self.assertEqual(calc_level(15500), 20)

    def test_extrapolation_level_21(self):
        self.assertEqual(calc_level(15500 + 2500), 21)

    def test_extrapolation_level_22(self):
        self.assertEqual(calc_level(15500 + 5000), 22)

    def test_high_exp(self):
        result = calc_level(100000)
        self.assertGreater(result, 20)


class TestLevelExpFunctions(unittest.TestCase):
    """Test get_next_level_exp and get_current_level_exp."""

    def test_next_level_exp_level_1(self):
        self.assertEqual(get_next_level_exp(1), 100)

    def test_next_level_exp_level_19(self):
        self.assertEqual(get_next_level_exp(19), 15500)

    def test_next_level_exp_beyond_table(self):
        self.assertEqual(get_next_level_exp(20), 15500 + EXP_EXTRAPOLATION_STEP)

    def test_current_level_exp_level_1(self):
        self.assertEqual(get_current_level_exp(1), 0)

    def test_current_level_exp_level_2(self):
        self.assertEqual(get_current_level_exp(2), 100)

    def test_current_level_exp_beyond_table(self):
        expected = EXP_TABLE[-1] + (20 - len(EXP_TABLE)) * EXP_EXTRAPOLATION_STEP
        self.assertEqual(get_current_level_exp(21), expected)


class TestCalcDay(unittest.TestCase):
    """Test day calculation from datetime."""

    def test_first_day(self):
        self.assertEqual(calc_day(NURTURE_FIRST_DAY), 1)

    def test_day_2(self):
        dt = NURTURE_FIRST_DAY + timedelta(days=1)
        self.assertEqual(calc_day(dt), 2)

    def test_day_45(self):
        dt = NURTURE_FIRST_DAY + timedelta(days=44)
        self.assertEqual(calc_day(dt), 45)

    def test_before_first_day_returns_1(self):
        dt = NURTURE_FIRST_DAY - timedelta(days=10)
        self.assertEqual(calc_day(dt), 1)


class TestUpdateVisits(unittest.TestCase):
    """Test visit detection and tracking."""

    def _make_log(self, **overrides):
        log = {
            "total_visits": 0,
            "total_time_minutes": 0,
            "streak": 0,
            "last_visit": None,
            "last_visit_date": None,
            "today_visits": 0,
            "today_time_minutes": 0,
            "previous_status": "offline",
        }
        log.update(overrides)
        return log

    def test_offline_to_online_new_visit(self):
        now = datetime(2026, 2, 13, 12, 0, 0, tzinfo=JST)
        vlog = self._make_log()
        result = update_visits(vlog, "online", now)
        self.assertEqual(result["total_visits"], 1)
        self.assertEqual(result["today_visits"], 1)
        self.assertEqual(result["streak"], 1)

    def test_online_to_online_no_new_visit(self):
        now = datetime(2026, 2, 13, 12, 0, 0, tzinfo=JST)
        vlog = self._make_log(previous_status="online", total_visits=5)
        result = update_visits(vlog, "online", now)
        self.assertEqual(result["total_visits"], 5)  # unchanged

    def test_online_accumulates_time(self):
        now = datetime(2026, 2, 13, 12, 0, 0, tzinfo=JST)
        vlog = self._make_log(previous_status="online", total_time_minutes=100)
        result = update_visits(vlog, "online", now)
        self.assertEqual(result["total_time_minutes"], 105)
        self.assertEqual(result["today_time_minutes"], 5)

    def test_offline_no_time_accumulation(self):
        now = datetime(2026, 2, 13, 12, 0, 0, tzinfo=JST)
        vlog = self._make_log(previous_status="offline")
        result = update_visits(vlog, "offline", now)
        self.assertEqual(result["total_time_minutes"], 0)

    def test_date_change_resets_daily(self):
        now = datetime(2026, 2, 14, 12, 0, 0, tzinfo=JST)
        vlog = self._make_log(
            last_visit_date="2026-02-13",
            today_visits=5,
            today_time_minutes=60,
        )
        result = update_visits(vlog, "offline", now)
        self.assertEqual(result["today_visits"], 0)
        self.assertEqual(result["today_time_minutes"], 0)

    def test_streak_continues_next_day(self):
        now = datetime(2026, 2, 14, 12, 0, 0, tzinfo=JST)
        vlog = self._make_log(
            last_visit_date="2026-02-13",
            streak=3,
            previous_status="offline",
        )
        result = update_visits(vlog, "online", now)
        self.assertEqual(result["streak"], 4)

    def test_streak_breaks_after_gap(self):
        now = datetime(2026, 2, 16, 12, 0, 0, tzinfo=JST)
        vlog = self._make_log(
            last_visit_date="2026-02-13",
            streak=5,
        )
        result = update_visits(vlog, "offline", now)
        self.assertEqual(result["streak"], 0)

    def test_away_to_online_new_visit(self):
        now = datetime(2026, 2, 13, 12, 0, 0, tzinfo=JST)
        vlog = self._make_log(previous_status="away")
        result = update_visits(vlog, "online", now)
        self.assertEqual(result["total_visits"], 1)


class TestEvaluate(unittest.TestCase):
    """Test the full evaluate integration function."""

    def test_basic_evaluation(self):
        now = datetime(2026, 2, 13, 12, 0, 0, tzinfo=JST)
        health_data = {"overall": {"score": 80}, "uptime": {"seconds": 3600}}
        status_data = {"status": "online", "time_context": {"period": "active"}}
        visit_log = {
            "total_visits": 10, "total_time_minutes": 100, "streak": 3,
            "last_visit": None, "last_visit_date": "2026-02-13",
            "today_visits": 2, "today_time_minutes": 30, "previous_status": "online",
        }

        nurture, updated_vlog = evaluate(health_data, status_data, None, visit_log, now)

        self.assertIn("timestamp", nurture)
        self.assertIn("mood", nurture)
        self.assertIn("energy", nurture)
        self.assertIn("trust", nurture)
        self.assertIn("intimacy", nurture)
        self.assertIn("exp", nurture)
        self.assertIn("level", nurture)
        self.assertIn("day", nurture)
        self.assertIn("health", nurture)

        self.assertIn("state", nurture["mood"])
        self.assertIn("value", nurture["mood"])
        self.assertIn("state", nurture["energy"])
        self.assertIn("value", nurture["energy"])

    def test_all_none_inputs(self):
        """Should not crash with all None inputs."""
        now = datetime(2026, 2, 13, 12, 0, 0, tzinfo=JST)
        visit_log = {
            "total_visits": 0, "total_time_minutes": 0, "streak": 0,
            "last_visit": None, "last_visit_date": None,
            "today_visits": 0, "today_time_minutes": 0, "previous_status": "offline",
        }

        nurture, updated_vlog = evaluate(None, None, None, visit_log, now)

        self.assertIsInstance(nurture, dict)
        self.assertGreaterEqual(nurture["level"], 1)
        self.assertEqual(nurture["health"], 50)  # fallback

    def test_visit_detection_through_evaluate(self):
        """offline->online should increment visit count."""
        now = datetime(2026, 2, 13, 12, 0, 0, tzinfo=JST)
        status_data = {"status": "online", "time_context": {"period": "active"}}
        visit_log = {
            "total_visits": 0, "total_time_minutes": 0, "streak": 0,
            "last_visit": None, "last_visit_date": None,
            "today_visits": 0, "today_time_minutes": 0, "previous_status": "offline",
        }

        _, updated_vlog = evaluate(None, status_data, None, visit_log, now)
        self.assertEqual(updated_vlog["total_visits"], 1)


if __name__ == "__main__":
    unittest.main()
