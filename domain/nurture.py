"""
domain/nurture.py - Nurture parameter calculation (pure functions).

Extracted from collectors/collect_nurture.py (Phase 2A).
All thresholds and labels come from domain.constants.
No I/O, no subprocess, no file access.
"""

import math

from domain.constants import (
    NURTURE_FIRST_DAY,
    EXP_TABLE,
    EXP_EXTRAPOLATION_STEP,
    EXP_SOURCES,
    HEALTH_EXP_THRESHOLD,
    STREAK_EXP_CAP,
    ENERGY_BASE,
    ENERGY_UPTIME_THRESHOLD_HOURS,
    ENERGY_UPTIME_PENALTY_PER_HOUR,
    ENERGY_UPTIME_PENALTY_MAX,
    ENERGY_TIME_WEIGHTS,
    ENERGY_THRESHOLDS,
    ENERGY_LABELS,
    MOOD_WEIGHTS,
    MOOD_VISIT_NEUTRAL,
    MOOD_VISIT_TODAY,
    MOOD_VISIT_STREAK_LONG,
    MOOD_VISIT_STREAK_MID,
    MOOD_TIME_FACTORS,
    MOOD_THRESHOLDS,
    MOOD_LABELS,
    TRUST_BASE,
    TRUST_LOG_COEFFICIENT,
    TRUST_MAX_FROM_VISITS,
    TRUST_STREAK_BONUS_PER_DAY,
    TRUST_STREAK_BONUS_MAX,
    INTIMACY_BASE,
    INTIMACY_LOG_COEFFICIENT,
    INTIMACY_MAX_FROM_HOURS,
    INTIMACY_TODAY_DIVISOR,
    INTIMACY_TODAY_BONUS_MAX,
)


def calc_health(overall_score):
    """
    Extract health score for nurture calculation.

    Args:
        overall_score: int or None - health overall score (0-100)

    Returns:
        int - health value (0-100), defaults to 50 if None
    """
    if overall_score is None:
        return 50
    return int(max(0, min(100, overall_score)))


def calc_energy(uptime_seconds, time_period, hour=None):
    """
    Calculate energy based on uptime and time of day.

    Args:
        uptime_seconds: int or None - system uptime in seconds
        time_period: str or None - current time period name
        hour: int or None - unused, kept for API compatibility

    Returns:
        int - energy value (0-100)
    """
    energy = ENERGY_BASE

    # Uptime penalty
    if uptime_seconds is not None:
        uptime_hours = uptime_seconds / 3600
        if uptime_hours > ENERGY_UPTIME_THRESHOLD_HOURS:
            penalty = min(
                (uptime_hours - ENERGY_UPTIME_THRESHOLD_HOURS) * ENERGY_UPTIME_PENALTY_PER_HOUR,
                ENERGY_UPTIME_PENALTY_MAX,
            )
            energy -= penalty

    # Time-of-day modifier
    if time_period is not None:
        mod = ENERGY_TIME_WEIGHTS.get(time_period, 0)
        energy += mod

    return max(0, min(100, int(energy)))


def classify_energy(value):
    """
    Classify energy into state with label and message.

    Args:
        value: int - energy value (0-100)

    Returns:
        dict - {state, label, message}
    """
    for threshold, state in ENERGY_THRESHOLDS:
        if threshold is None or value >= threshold:
            return {"state": state, **ENERGY_LABELS[state]}
    # Fallback
    return {"state": "exhausted", **ENERGY_LABELS["exhausted"]}


def calc_mood(health_val, energy_val, visit_data, time_period):
    """
    Calculate mood from multiple factors.

    Args:
        health_val: int - health score (0-100)
        energy_val: int - energy value (0-100)
        visit_data: dict - visit log with streak, today_visits
        time_period: str or None - current time period name

    Returns:
        int - mood value (0-100)
    """
    # Health factor
    health_factor = health_val * MOOD_WEIGHTS["health"]

    # Energy factor
    energy_factor = energy_val * MOOD_WEIGHTS["energy"]

    # Visit factor
    visit_factor = MOOD_VISIT_NEUTRAL
    streak = visit_data.get("streak", 0) if visit_data else 0
    today_visits = visit_data.get("today_visits", 0) if visit_data else 0
    if today_visits > 0:
        visit_factor = MOOD_VISIT_TODAY
    if streak >= 7:
        visit_factor = MOOD_VISIT_STREAK_LONG
    elif streak >= 3:
        visit_factor = max(visit_factor, MOOD_VISIT_STREAK_MID)

    # Time factor
    time_factor = MOOD_VISIT_NEUTRAL  # neutral default
    if time_period is not None:
        time_factor = MOOD_TIME_FACTORS.get(time_period, MOOD_VISIT_NEUTRAL)

    mood = int(health_factor + energy_factor + visit_factor + time_factor)
    return max(0, min(100, mood))


def classify_mood(value):
    """
    Classify mood into state with message.

    Args:
        value: int - mood value (0-100)

    Returns:
        dict - {state, label, message}
    """
    for threshold, state in MOOD_THRESHOLDS:
        if threshold is None or value >= threshold:
            return {"state": state, **MOOD_LABELS[state]}
    # Fallback
    return {"state": "bad", **MOOD_LABELS["bad"]}


def calc_trust(total_visits, streak, max_streak=None):
    """
    Calculate trust from cumulative visit data (logarithmic growth).

    Args:
        total_visits: int - total visit count
        streak: int - current visit streak (days)
        max_streak: int or None - unused, kept for API compatibility

    Returns:
        int - trust value (0-100)
    """
    base = TRUST_BASE + min(
        TRUST_MAX_FROM_VISITS,
        TRUST_LOG_COEFFICIENT * math.log10(max(total_visits, 1)),
    )
    streak_bonus = min(streak * TRUST_STREAK_BONUS_PER_DAY, TRUST_STREAK_BONUS_MAX)
    return int(min(100, base + streak_bonus))


def calc_intimacy(total_minutes, today_minutes):
    """
    Calculate intimacy from time spent together (logarithmic growth).

    Args:
        total_minutes: int - cumulative time in minutes
        today_minutes: int - today's session time in minutes

    Returns:
        int - intimacy value (0-100)
    """
    total_hours = total_minutes / 60
    intimacy = INTIMACY_BASE + min(
        INTIMACY_MAX_FROM_HOURS,
        INTIMACY_LOG_COEFFICIENT * math.log10(max(total_hours, 0.1) + 1),
    )
    today_bonus = min(today_minutes / INTIMACY_TODAY_DIVISOR, INTIMACY_TODAY_BONUS_MAX)
    intimacy += today_bonus
    return int(min(100, intimacy))


def calc_exp(visit_data, health_val, skill_count):
    """
    Calculate total EXP.

    Args:
        visit_data: dict - visit log with total_visits, total_time_minutes, streak
        health_val: int - health score (0-100)
        skill_count: int - number of installed skills

    Returns:
        int - total EXP
    """
    total_visits = visit_data.get("total_visits", 0) if visit_data else 0
    total_minutes = visit_data.get("total_time_minutes", 0) if visit_data else 0
    streak = visit_data.get("streak", 0) if visit_data else 0

    visit_exp = total_visits * EXP_SOURCES["visit"]
    time_exp = (total_minutes // 5) * EXP_SOURCES["time_per_5min"]
    streak_exp = total_visits * min(streak, STREAK_EXP_CAP) * EXP_SOURCES["streak_bonus"]
    health_exp = max(0, health_val - HEALTH_EXP_THRESHOLD) * EXP_SOURCES["health_bonus"]
    skill_exp = skill_count * EXP_SOURCES["skill_bonus"]

    return visit_exp + time_exp + streak_exp + health_exp + skill_exp


def calc_level(total_exp):
    """
    Determine level from total EXP using the threshold table.

    Args:
        total_exp: int - total EXP

    Returns:
        int - current level (1+)
    """
    level = 1
    for i, threshold in enumerate(EXP_TABLE):
        if total_exp >= threshold:
            level = i + 1
        else:
            break
    # Extrapolate beyond table
    if total_exp >= EXP_TABLE[-1]:
        extra = total_exp - EXP_TABLE[-1]
        extra_levels = extra // EXP_EXTRAPOLATION_STEP
        level = len(EXP_TABLE) + int(extra_levels)
    return level


def get_next_level_exp(level):
    """
    Get EXP needed for next level.

    Args:
        level: int - current level

    Returns:
        int - total EXP required for next level
    """
    if level < len(EXP_TABLE):
        return EXP_TABLE[level]
    return EXP_TABLE[-1] + (level - len(EXP_TABLE) + 1) * EXP_EXTRAPOLATION_STEP


def get_current_level_exp(level):
    """
    Get EXP at which current level starts.

    Args:
        level: int - current level

    Returns:
        int - total EXP at start of this level
    """
    if level <= 1:
        return 0
    if level - 1 < len(EXP_TABLE):
        return EXP_TABLE[level - 1]
    return EXP_TABLE[-1] + (level - 1 - len(EXP_TABLE)) * EXP_EXTRAPOLATION_STEP


def calc_day(now_dt):
    """
    Calculate days since Rebecca's first day.

    Args:
        now_dt: datetime (timezone-aware)

    Returns:
        int - day number (1+)
    """
    delta = now_dt - NURTURE_FIRST_DAY
    return max(1, delta.days + 1)


def update_visits(visit_log, current_status, now_dt):
    """
    Detect visits based on status transitions. Mutates and returns visit_log.

    Args:
        visit_log: dict - visit log data (mutated in place)
        current_status: str - current presence status
        now_dt: datetime (timezone-aware, JST)

    Returns:
        dict - updated visit_log
    """
    from datetime import datetime

    today_str = now_dt.strftime("%Y-%m-%d")
    prev_status = visit_log.get("previous_status", "offline")
    last_visit_date = visit_log.get("last_visit_date")

    # Reset daily counters on date change
    if last_visit_date != today_str and last_visit_date is not None:
        try:
            last_date = datetime.strptime(last_visit_date, "%Y-%m-%d").date()
            today_date = now_dt.date()
            delta_days = (today_date - last_date).days
            if delta_days > 1:
                visit_log["streak"] = 0
        except (ValueError, KeyError):
            pass
        visit_log["today_visits"] = 0
        visit_log["today_time_minutes"] = 0

    # Detect new visit: previous offline -> current online
    if prev_status != "online" and current_status == "online":
        visit_log["total_visits"] = visit_log.get("total_visits", 0) + 1
        visit_log["today_visits"] = visit_log.get("today_visits", 0) + 1
        visit_log["last_visit"] = now_dt.isoformat(timespec="seconds")

        # Update streak on first visit of the day
        if visit_log.get("last_visit_date") != today_str:
            visit_log["streak"] = visit_log.get("streak", 0) + 1

        visit_log["last_visit_date"] = today_str

    # Accumulate time if online (5 min per check cycle)
    if current_status == "online":
        visit_log["total_time_minutes"] = visit_log.get("total_time_minutes", 0) + 5
        visit_log["today_time_minutes"] = visit_log.get("today_time_minutes", 0) + 5

    visit_log["previous_status"] = current_status
    return visit_log


def evaluate(health_data, status_data, skills_data, visit_log, now_dt):
    """
    Full nurture evaluation. Produces nurture dict and updated visit log.

    Args:
        health_data: dict or None - health.json data
        status_data: dict or None - status.json data
        skills_data: dict or None - skills.json data
        visit_log: dict - visit log (mutated)
        now_dt: datetime (timezone-aware, JST)

    Returns:
        tuple - (nurture_dict, updated_visit_log)
    """
    # Get current status for visit detection
    current_status = "offline"
    if status_data:
        current_status = status_data.get("status", "offline")

    # Update visit log
    visit_log = update_visits(visit_log, current_status, now_dt)

    # Extract inputs
    overall_score = None
    if health_data:
        try:
            overall_score = health_data["overall"]["score"]
        except (KeyError, TypeError):
            pass

    uptime_seconds = None
    if health_data:
        try:
            uptime_seconds = health_data["uptime"]["seconds"]
        except (KeyError, TypeError):
            pass

    time_period = None
    if status_data:
        try:
            time_period = status_data["time_context"]["period"]
        except (KeyError, TypeError):
            pass

    skill_count = 0
    if skills_data:
        try:
            skill_count = len(skills_data.get("skills", []))
        except (TypeError, AttributeError):
            pass

    # Calculate parameters
    health_val = calc_health(overall_score)
    energy_val = calc_energy(uptime_seconds, time_period)
    mood_val = calc_mood(health_val, energy_val, visit_log, time_period)
    trust_val = calc_trust(
        visit_log.get("total_visits", 0),
        visit_log.get("streak", 0),
    )
    intimacy_val = calc_intimacy(
        visit_log.get("total_time_minutes", 0),
        visit_log.get("today_time_minutes", 0),
    )
    total_exp = calc_exp(visit_log, health_val, skill_count)
    level = calc_level(total_exp)
    day = calc_day(now_dt)

    mood_class = classify_mood(mood_val)
    energy_class = classify_energy(energy_val)

    # EXP progress within current level
    current_level_exp = get_current_level_exp(level)
    next_level_exp = get_next_level_exp(level)
    exp_in_level = total_exp - current_level_exp

    nurture = {
        "timestamp": now_dt.isoformat(timespec="seconds"),
        "health": health_val,
        "mood": {
            "value": mood_val,
            "state": mood_class["state"],
            "message": mood_class["message"],
        },
        "energy": {
            "value": energy_val,
            "state": energy_class["state"],
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
