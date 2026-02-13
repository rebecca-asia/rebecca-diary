"""
domain/health.py - Health classification, scoring, and alert logic.

Pure functions only — no I/O, no subprocess, no file access.
All thresholds and labels come from domain.constants.
"""

import random

from domain.constants import (
    CPU_THRESHOLDS, CPU_LABELS,
    MEMORY_THRESHOLDS, MEMORY_LABELS,
    DISK_THRESHOLDS, DISK_LABELS,
    TEMPERATURE_THRESHOLDS, TEMPERATURE_LABELS,
    UPTIME_THRESHOLDS_DAYS, UPTIME_LABELS,
    OVERALL_SCORE_TABLE,
    PENALTY_CPU_OFFSET, PENALTY_CPU_WEIGHT,
    PENALTY_MEMORY_OFFSET, PENALTY_MEMORY_WEIGHT,
    PENALTY_DISK_OFFSET, PENALTY_DISK_WEIGHT,
    PENALTY_TEMP_OFFSET, PENALTY_TEMP_WEIGHT,
    PENALTY_UPTIME_PER_DAY, PENALTY_UPTIME_MAX,
    ALERT_CRITICAL_STATES, ALERT_HEAVY_STATES,
    ALERT_MESSAGES,
)


def _classify(value, thresholds):
    """Generic threshold classifier. Returns the state string for the given value."""
    for upper_bound, state in thresholds:
        if upper_bound is None or value < upper_bound:
            return state
    # Should not reach here if thresholds are well-formed (last entry is None)
    return thresholds[-1][1]


def classify_cpu(usage_percent):
    """Classify CPU usage into emotional state. Returns dict {state, label, message}."""
    state = _classify(usage_percent, CPU_THRESHOLDS)
    return {"state": state, **CPU_LABELS[state]}


def classify_memory(usage_percent):
    """Classify memory usage into emotional state. Returns dict {state, label, message}."""
    state = _classify(usage_percent, MEMORY_THRESHOLDS)
    return {"state": state, **MEMORY_LABELS[state]}


def classify_disk(usage_percent):
    """Classify disk usage into emotional state. Returns dict {state, label, message}."""
    state = _classify(usage_percent, DISK_THRESHOLDS)
    return {"state": state, **DISK_LABELS[state]}


def classify_temperature(celsius):
    """Classify temperature. Returns dict {state, label, message} or None if celsius is None."""
    if celsius is None:
        return None
    state = _classify(celsius, TEMPERATURE_THRESHOLDS)
    return {"state": state, **TEMPERATURE_LABELS[state]}


def classify_uptime(seconds):
    """Classify uptime into emotional state. Returns dict {state, label, message}."""
    days = seconds / 86400.0
    state = _classify(days, UPTIME_THRESHOLDS_DAYS)
    return {"state": state, **UPTIME_LABELS[state]}


def calculate_overall_score(cpu_pct, mem_pct, disk_pct, temp_c, uptime_sec):
    """
    Calculate overall health score (0-100) using penalty-based system.

    Returns dict {score, state, emoji, label, message}.
    """
    cpu_penalty = max(0, cpu_pct - PENALTY_CPU_OFFSET) * PENALTY_CPU_WEIGHT
    memory_penalty = max(0, mem_pct - PENALTY_MEMORY_OFFSET) * PENALTY_MEMORY_WEIGHT
    disk_penalty = max(0, disk_pct - PENALTY_DISK_OFFSET) * PENALTY_DISK_WEIGHT
    temp_penalty = max(0, temp_c - PENALTY_TEMP_OFFSET) * PENALTY_TEMP_WEIGHT if temp_c is not None else 0
    uptime_days = uptime_sec / 86400.0
    uptime_penalty = min(uptime_days * PENALTY_UPTIME_PER_DAY, PENALTY_UPTIME_MAX)

    total_penalty = cpu_penalty + memory_penalty + disk_penalty + temp_penalty + uptime_penalty
    score = max(0, min(100, round(100 - total_penalty)))

    for min_score, state, emoji, label, message in OVERALL_SCORE_TABLE:
        if score >= min_score:
            return {
                "score": score,
                "state": state,
                "emoji": emoji,
                "label": label,
                "message": message,
            }

    # Fallback (should not reach here)
    last = OVERALL_SCORE_TABLE[-1]
    return {"score": score, "state": last[1], "emoji": last[2], "label": last[3], "message": last[4]}


def determine_alert_level(states, overall_score):
    """
    Determine alert level 0-3 based on metric states and overall score.

    Args:
        states: list of state strings from all active metrics
        overall_score: int 0-100

    Returns:
        int 0-3
    """
    critical_count = sum(1 for s in states if s in ALERT_CRITICAL_STATES)
    heavy_count = sum(1 for s in states if s in ALERT_HEAVY_STATES)

    if critical_count >= 2 or overall_score < 20:
        return 3
    if critical_count >= 1:
        return 2
    if heavy_count >= 1:
        return 1
    return 0


def get_alert_message(level):
    """Get a random alert message for the given level. Returns str or None."""
    if level == 0 or level not in ALERT_MESSAGES:
        return None
    return random.choice(ALERT_MESSAGES[level])


def evaluate(raw_metrics):
    """
    Full health evaluation from raw metric values.

    Args:
        raw_metrics: dict with keys:
            - cpu_usage: float (percent)
            - mem_usage: float (percent)
            - disk_usage: float (percent)
            - temperature: float or None (celsius)
            - uptime_seconds: int

    Returns:
        dict with keys: cpu, memory, disk, temperature, uptime, overall, alert_level, alert_message
        (classification dicts for each metric, plus overall score and alert info)
    """
    cpu_pct = raw_metrics.get("cpu_usage", 0)
    mem_pct = raw_metrics.get("mem_usage", 0)
    disk_pct = raw_metrics.get("disk_usage", 0)
    temp_c = raw_metrics.get("temperature", None)
    uptime_sec = raw_metrics.get("uptime_seconds", 0)

    cpu = classify_cpu(cpu_pct)
    memory = classify_memory(mem_pct)
    disk = classify_disk(disk_pct)
    temperature = classify_temperature(temp_c)
    uptime = classify_uptime(uptime_sec)

    overall = calculate_overall_score(cpu_pct, mem_pct, disk_pct, temp_c, uptime_sec)

    # Collect states for alert determination
    all_states = [cpu["state"], memory["state"], disk["state"]]
    if temperature is not None:
        all_states.append(temperature["state"])
    all_states.append(uptime["state"])

    alert_level = determine_alert_level(all_states, overall["score"])
    alert_message = get_alert_message(alert_level)

    return {
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "temperature": temperature,
        "uptime": uptime,
        "overall": overall,
        "alert_level": alert_level,
        "alert_message": alert_message,
    }
