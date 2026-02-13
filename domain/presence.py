"""
domain/presence.py - Presence status determination and time context.

Pure functions only — no I/O, no subprocess, no file access.
All thresholds and labels come from domain.constants.
"""

import random

from domain.constants import (
    ONLINE_THRESHOLD_SEC,
    AWAY_THRESHOLD_SEC,
    SLEEPING_THRESHOLD_SEC,
    STATUS_LABELS,
    TIME_PERIODS,
    TIME_MESSAGES,
)


def determine_status(gateway_alive, inactive_seconds, time_period):
    """
    Determine Rebecca's presence status.

    Args:
        gateway_alive: bool - whether OpenClaw Gateway is running
        inactive_seconds: float or None - seconds since last activity
        time_period: str - current time period name (e.g. "deep_night")

    Returns:
        dict {status, label, emoji}
    """
    # Rule 1: online
    if (gateway_alive and inactive_seconds is not None
            and inactive_seconds < ONLINE_THRESHOLD_SEC):
        status = "online"
        return {"status": status, **STATUS_LABELS[status]}

    # Rule 2: away
    if (gateway_alive and inactive_seconds is not None
            and ONLINE_THRESHOLD_SEC <= inactive_seconds < AWAY_THRESHOLD_SEC):
        status = "away"
        return {"status": status, **STATUS_LABELS[status]}

    # Rule 3: sleeping (check BEFORE offline)
    if (time_period == "deep_night" and inactive_seconds is not None
            and inactive_seconds > SLEEPING_THRESHOLD_SEC):
        status = "sleeping"
        return {"status": status, **STATUS_LABELS[status]}

    # Rule 4: offline (default fallback)
    status = "offline"
    return {"status": status, **STATUS_LABELS[status]}


def get_time_context(hour):
    """
    Determine time period and Rebecca's message based on hour (0-23).

    Returns:
        dict {period, message}
    """
    period = None
    for start, end, name in TIME_PERIODS:
        if start <= hour < end:
            period = name
            break

    if period is None:
        period = "night"  # fallback (should not happen with full 24h coverage)

    message = random.choice(TIME_MESSAGES[period])
    return {"period": period, "message": message}


def evaluate(gateway_alive, last_activity_dt, now_dt):
    """
    Full presence evaluation.

    Args:
        gateway_alive: bool
        last_activity_dt: datetime or None (timezone-aware)
        now_dt: datetime (timezone-aware, JST)

    Returns:
        dict {status, label, emoji, time_context}
    """
    # Calculate inactive seconds
    if last_activity_dt is not None:
        inactive_seconds = (now_dt - last_activity_dt).total_seconds()
    else:
        inactive_seconds = None

    time_context = get_time_context(now_dt.hour)
    status = determine_status(gateway_alive, inactive_seconds, time_context["period"])

    return {
        **status,
        "time_context": time_context,
    }
