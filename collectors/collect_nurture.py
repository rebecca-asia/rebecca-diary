#!/usr/bin/env python3
"""
collect_nurture.py - Nurture parameter calculator for Rebecca's Room

Reads health.json, status.json, and visit_log.json to compute Rebecca's
nurture state: mood, energy, trust, intimacy, EXP, and level.
Outputs src/data/nurture.json and updates src/data/visit_log.json.

Usage:
    python3 collectors/collect_nurture.py        # normal run
    python3 collectors/collect_nurture.py -v     # verbose/debug output

Dependencies: Python 3.9+ stdlib only (no pip packages)
Frequency: every 5 minutes (cron)
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# -- Domain layer import --
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from domain.constants import EXP_TABLE as _DOMAIN_EXP_TABLE

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

JST = timezone(timedelta(hours=9))

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "src" / "data"

HEALTH_FILE = DATA_DIR / "health.json"
STATUS_FILE = DATA_DIR / "status.json"
SKILLS_FILE = DATA_DIR / "skills.json"
VISIT_LOG_FILE = DATA_DIR / "visit_log.json"
NURTURE_FILE = DATA_DIR / "nurture.json"

# Rebecca's birthday (project start)
FIRST_DAY = datetime(2026, 1, 1, 0, 0, 0, tzinfo=JST)

# EXP thresholds per level (from domain.constants)
EXP_TABLE = _DOMAIN_EXP_TABLE

VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv


def log(msg):
    if VERBOSE:
        print(f"[nurture] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Data loading (graceful degradation)
# ---------------------------------------------------------------------------

def load_json(path):
    """Load a JSON file. Returns None if missing or invalid."""
    try:
        if not path.exists():
            log(f"File not found: {path}")
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        log(f"Loaded {path}")
        return data
    except (json.JSONDecodeError, OSError) as e:
        log(f"Failed to load {path}: {e}")
        return None


def load_visit_log():
    """Load visit_log.json with defaults."""
    data = load_json(VISIT_LOG_FILE)
    if data is None:
        log("Initializing new visit log")
        return {
            "total_visits": 0,
            "total_time_minutes": 0,
            "streak": 0,
            "last_visit": None,
            "last_visit_date": None,
            "today_visits": 0,
            "today_time_minutes": 0,
            "previous_status": "offline",
        }
    return data


# ---------------------------------------------------------------------------
# Visit detection
# ---------------------------------------------------------------------------

def update_visits(visit_log, current_status):
    """
    Detect visits based on status transitions.
    - offline -> online = new visit (visit_count++)
    - Date change resets today counters and checks streak
    """
    now = datetime.now(JST)
    today_str = now.strftime("%Y-%m-%d")
    prev_status = visit_log.get("previous_status", "offline")
    last_visit_date = visit_log.get("last_visit_date")

    # Reset daily counters on date change
    if last_visit_date != today_str and last_visit_date is not None:
        log(f"New day: {last_visit_date} -> {today_str}")
        # Check streak: if last_visit_date was yesterday, continue streak
        try:
            last_date = datetime.strptime(last_visit_date, "%Y-%m-%d").date()
            today_date = now.date()
            delta_days = (today_date - last_date).days
            if delta_days == 1:
                # Streak continues (will increment if visit happens)
                log(f"Streak continues from yesterday (current: {visit_log['streak']})")
            elif delta_days > 1:
                # Streak broken
                log(f"Streak broken ({delta_days} days gap)")
                visit_log["streak"] = 0
        except (ValueError, KeyError):
            pass
        visit_log["today_visits"] = 0
        visit_log["today_time_minutes"] = 0

    # Detect new visit: previous offline -> current online
    if prev_status != "online" and current_status == "online":
        visit_log["total_visits"] += 1
        visit_log["today_visits"] = visit_log.get("today_visits", 0) + 1
        visit_log["last_visit"] = now.isoformat(timespec="seconds")

        # Update streak on first visit of the day
        if visit_log.get("last_visit_date") != today_str:
            visit_log["streak"] = visit_log.get("streak", 0) + 1

        visit_log["last_visit_date"] = today_str
        log(f"New visit detected! total={visit_log['total_visits']}, "
            f"today={visit_log['today_visits']}, streak={visit_log['streak']}")

    # Accumulate time if online (5 min per check cycle)
    if current_status == "online":
        visit_log["total_time_minutes"] = visit_log.get("total_time_minutes", 0) + 5
        visit_log["today_time_minutes"] = visit_log.get("today_time_minutes", 0) + 5
        log(f"Online time accumulated: +5min (total={visit_log['total_time_minutes']})")

    visit_log["previous_status"] = current_status
    return visit_log


# ---------------------------------------------------------------------------
# Parameter calculations
# ---------------------------------------------------------------------------

def calc_health(health_data):
    """Extract health score from health.json's overall.score."""
    if health_data is None:
        return 50  # neutral fallback
    try:
        score = health_data["overall"]["score"]
        log(f"Health: {score}")
        return int(score)
    except (KeyError, TypeError):
        log("Health data missing overall.score, using fallback")
        return 50


def calc_energy(health_data, status_data):
    """
    Calculate energy based on uptime and time of day.
    - Longer uptime = lower energy
    - Deep night = natural energy decrease
    """
    energy = 80  # base

    # Uptime penalty
    if health_data:
        try:
            uptime_seconds = health_data["uptime"]["seconds"]
            uptime_hours = uptime_seconds / 3600
            # Penalty: -3 per hour after 8h, capped at -40
            if uptime_hours > 8:
                penalty = min((uptime_hours - 8) * 3, 40)
                energy -= penalty
                log(f"Energy uptime penalty: -{penalty:.1f} (uptime={uptime_hours:.1f}h)")
        except (KeyError, TypeError):
            pass

    # Time-of-day modifier
    if status_data:
        try:
            period = status_data["time_context"]["period"]
            period_modifiers = {
                "deep_night": -20,
                "late_night": -10,
                "morning": -5,
                "active": 0,
                "afternoon": 0,
                "evening": -5,
                "night": -10,
            }
            mod = period_modifiers.get(period, 0)
            energy += mod
            log(f"Energy time modifier: {mod:+d} (period={period})")
        except (KeyError, TypeError):
            pass

    energy = max(0, min(100, int(energy)))
    log(f"Energy: {energy}")
    return energy


def classify_energy(value):
    """Classify energy into state."""
    if value >= 70:
        return "energetic"
    elif value >= 40:
        return "normal"
    elif value >= 20:
        return "tired"
    else:
        return "exhausted"


def calc_mood(health_val, energy_val, visit_log, status_data):
    """
    Calculate mood from multiple factors.
    - Health contributes 40%
    - Energy contributes 20%
    - Recent visits contribute 20%
    - Time context contributes 20%
    """
    # Health factor (0-100 -> 0-40)
    health_factor = health_val * 0.4

    # Energy factor (0-100 -> 0-20)
    energy_factor = energy_val * 0.2

    # Visit factor: recent visits boost mood
    visit_factor = 10  # neutral
    streak = visit_log.get("streak", 0)
    today_visits = visit_log.get("today_visits", 0)
    if today_visits > 0:
        visit_factor = 16  # visited today = good mood
    if streak >= 7:
        visit_factor = 20  # long streak = great mood
    elif streak >= 3:
        visit_factor = max(visit_factor, 14)

    # Time factor
    time_factor = 10  # neutral
    if status_data:
        try:
            period = status_data["time_context"]["period"]
            time_factors = {
                "deep_night": 4,
                "late_night": 6,
                "morning": 8,
                "active": 16,
                "afternoon": 14,
                "evening": 12,
                "night": 10,
            }
            time_factor = time_factors.get(period, 10)
        except (KeyError, TypeError):
            pass

    mood = int(health_factor + energy_factor + visit_factor + time_factor)
    mood = max(0, min(100, mood))
    log(f"Mood: {mood} (health={health_factor:.0f}, energy={energy_factor:.0f}, "
        f"visit={visit_factor}, time={time_factor})")
    return mood


def classify_mood(value):
    """Classify mood into state and message."""
    if value >= 80:
        return {"state": "great", "message": "今日は調子いい！"}
    elif value >= 60:
        return {"state": "good", "message": "まぁまぁかな"}
    elif value >= 40:
        return {"state": "normal", "message": "ふつう"}
    elif value >= 20:
        return {"state": "down", "message": "ちょっとだるい......"}
    else:
        return {"state": "bad", "message": "......"}


def calc_trust(visit_log):
    """
    Calculate trust from cumulative visit data.
    Trust grows slowly with visits, decays very slowly.
    """
    total_visits = visit_log.get("total_visits", 0)
    streak = visit_log.get("streak", 0)

    # Base trust from total visits (logarithmic growth)
    # 0 visits = 10, 10 visits = 30, 50 visits = 55, 100 visits = 68, 200+ visits = 80+
    import math
    base = 10 + min(70, 25 * math.log10(max(total_visits, 1)))

    # Streak bonus (up to +15)
    streak_bonus = min(streak * 2, 15)

    trust = int(min(100, base + streak_bonus))
    log(f"Trust: {trust} (base={base:.1f}, streak_bonus={streak_bonus})")
    return trust


def calc_intimacy(visit_log):
    """
    Calculate intimacy from time spent together.
    Grows with cumulative time, more slowly than trust.
    """
    import math
    total_minutes = visit_log.get("total_time_minutes", 0)
    total_hours = total_minutes / 60

    # Logarithmic growth based on hours together
    # 0h = 5, 1h = 10, 10h = 28, 42h = 43, 100h = 55, 500h = 72
    intimacy = 5 + min(75, 23 * math.log10(max(total_hours, 0.1) + 1))

    # Today's extended visit bonus (up to +10)
    today_minutes = visit_log.get("today_time_minutes", 0)
    today_bonus = min(today_minutes / 6, 10)  # 60min = +10
    intimacy += today_bonus

    intimacy = int(min(100, intimacy))
    log(f"Intimacy: {intimacy} (hours={total_hours:.1f}, today_bonus={today_bonus:.1f})")
    return intimacy


def calc_exp(visit_log, health_val, skills_data):
    """
    Calculate total EXP.
    Sources:
    - Visits: 10 EXP per visit
    - Time: 2 EXP per 5 minutes online
    - Health maintenance: 1 EXP per health point above 50 per cycle
    - Skills: 50 EXP per skill plugin
    - Streak bonus: streak * 5 per visit
    """
    total_visits = visit_log.get("total_visits", 0)
    total_minutes = visit_log.get("total_time_minutes", 0)
    streak = visit_log.get("streak", 0)

    visit_exp = total_visits * 10
    time_exp = (total_minutes // 5) * 2
    streak_exp = total_visits * min(streak, 10) * 5  # retroactive estimation

    # Health bonus: above 50 is positive, capped
    health_exp = max(0, health_val - 50) * 2

    # Skills bonus
    skill_count = 0
    if skills_data:
        try:
            skill_count = len(skills_data.get("skills", []))
        except (TypeError, AttributeError):
            pass
    skill_exp = skill_count * 50

    total_exp = visit_exp + time_exp + streak_exp + health_exp + skill_exp

    log(f"EXP: {total_exp} (visit={visit_exp}, time={time_exp}, "
        f"streak={streak_exp}, health={health_exp}, skill={skill_exp})")
    return total_exp


def calc_level(total_exp):
    """Determine level from total EXP using the threshold table."""
    level = 1
    for i, threshold in enumerate(EXP_TABLE):
        if total_exp >= threshold:
            level = i + 1
        else:
            break
    # If EXP exceeds the table, extrapolate
    if total_exp >= EXP_TABLE[-1]:
        extra = total_exp - EXP_TABLE[-1]
        extra_levels = extra // 2500  # 2500 EXP per level beyond table
        level = len(EXP_TABLE) + int(extra_levels)

    log(f"Level: {level} (total_exp={total_exp})")
    return level


def get_next_level_exp(level):
    """Get EXP needed for next level."""
    if level < len(EXP_TABLE):
        return EXP_TABLE[level]
    # Extrapolate beyond table
    return EXP_TABLE[-1] + (level - len(EXP_TABLE) + 1) * 2500


def get_current_level_exp(level):
    """Get EXP at which current level starts."""
    if level <= 1:
        return 0
    if level - 1 < len(EXP_TABLE):
        return EXP_TABLE[level - 1]
    return EXP_TABLE[-1] + (level - 1 - len(EXP_TABLE)) * 2500


def calc_day():
    """Calculate days since Rebecca's first day."""
    now = datetime.now(JST)
    delta = now - FIRST_DAY
    return max(1, delta.days + 1)


# ---------------------------------------------------------------------------
# Build output
# ---------------------------------------------------------------------------

def build_nurture(health_data, status_data, skills_data, visit_log):
    """Compute all nurture parameters and build output dict."""
    now = datetime.now(JST)

    # Get current status for visit detection
    current_status = "offline"
    if status_data:
        current_status = status_data.get("status", "offline")

    # Update visit log
    visit_log = update_visits(visit_log, current_status)

    # Calculate parameters
    health_val = calc_health(health_data)
    energy_val = calc_energy(health_data, status_data)
    mood_val = calc_mood(health_val, energy_val, visit_log, status_data)
    trust_val = calc_trust(visit_log)
    intimacy_val = calc_intimacy(visit_log)
    total_exp = calc_exp(visit_log, health_val, skills_data)
    level = calc_level(total_exp)
    day = calc_day()

    mood_class = classify_mood(mood_val)
    energy_state = classify_energy(energy_val)

    # EXP progress within current level
    current_level_exp = get_current_level_exp(level)
    next_level_exp = get_next_level_exp(level)
    exp_in_level = total_exp - current_level_exp

    nurture = {
        "timestamp": now.isoformat(timespec="seconds"),
        "health": health_val,
        "mood": {
            "value": mood_val,
            "state": mood_class["state"],
            "message": mood_class["message"],
        },
        "energy": {
            "value": energy_val,
            "state": energy_state,
        },
        "trust": trust_val,
        "intimacy": intimacy_val,
        "exp": {
            "current": exp_in_level,
            "next_level": next_level_exp - current_level_exp,
            "total": total_exp,
        },
        "level": level,
        "day": day,
    }

    return nurture, visit_log


# ---------------------------------------------------------------------------
# Atomic write
# ---------------------------------------------------------------------------

def write_json_atomic(data, output_path):
    """Atomic write: .tmp -> rename."""
    os.makedirs(output_path.parent, exist_ok=True)
    tmp_path = output_path.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.rename(tmp_path, output_path)
        log(f"Wrote {output_path}")
    except OSError as e:
        log(f"Failed to write {output_path}: {e}")
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log("Starting nurture collection...")

    # Load input data (graceful degradation)
    health_data = load_json(HEALTH_FILE)
    status_data = load_json(STATUS_FILE)
    skills_data = load_json(SKILLS_FILE)
    visit_log = load_visit_log()

    # Calculate nurture parameters
    nurture, updated_visit_log = build_nurture(
        health_data, status_data, skills_data, visit_log
    )

    # Write outputs
    write_json_atomic(nurture, NURTURE_FILE)
    write_json_atomic(updated_visit_log, VISIT_LOG_FILE)

    if VERBOSE:
        print("=== nurture.json ===")
        print(json.dumps(nurture, ensure_ascii=False, indent=2))
        print("\n=== visit_log.json ===")
        print(json.dumps(updated_visit_log, ensure_ascii=False, indent=2))
    else:
        print(f"OK: lv={nurture['level']}, "
              f"mood={nurture['mood']['value']}, "
              f"energy={nurture['energy']['value']}, "
              f"trust={nurture['trust']}, "
              f"exp={nurture['exp']['total']}, "
              f"day={nurture['day']}, "
              f"timestamp={nurture['timestamp']}")


if __name__ == "__main__":
    main()
