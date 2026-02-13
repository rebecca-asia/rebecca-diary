"""
domain/schema.py - Schema versioning, staleness, validation, and atomic write.

Shared utilities for JSON output across all collectors.
"""

import json
import os
from datetime import datetime

from domain import __version__ as SCHEMA_VERSION
from domain.constants import STALENESS_FRESH_MAX_MIN, STALENESS_STALE_MAX_MIN


def inject_version(data):
    """Add schema_version to data dict. Returns the same dict (mutated)."""
    data["schema_version"] = SCHEMA_VERSION
    return data


def calculate_staleness(timestamp_iso, now):
    """
    Calculate staleness from an ISO timestamp string.

    Args:
        timestamp_iso: str - ISO 8601 timestamp
        now: datetime - current time (timezone-aware)

    Returns:
        str - "fresh", "stale", or "dead"
    """
    try:
        then = datetime.fromisoformat(timestamp_iso)
        diff_min = (now - then).total_seconds() / 60.0
    except (ValueError, TypeError):
        return "dead"

    if diff_min <= STALENESS_FRESH_MAX_MIN:
        return "fresh"
    elif diff_min <= STALENESS_STALE_MAX_MIN:
        return "stale"
    else:
        return "dead"


def inject_staleness(data, now):
    """Add staleness field based on data's timestamp. Returns the same dict (mutated)."""
    timestamp = data.get("timestamp", "")
    data["staleness"] = calculate_staleness(timestamp, now)
    return data


def validate_health(data):
    """Validate required fields in health JSON. Returns list of missing field names."""
    required = ["timestamp", "cpu", "memory", "disk", "uptime", "overall", "alert_level"]
    return [f for f in required if f not in data]


def validate_status(data):
    """Validate required fields in status JSON. Returns list of missing field names."""
    required = ["timestamp", "status", "label", "emoji", "time_context"]
    return [f for f in required if f not in data]


def write_json_atomic(data, output_path):
    """
    Write JSON data atomically: write to .tmp, then os.rename().

    Args:
        data: dict to serialize
        output_path: str or Path - final output path
    """
    output_path = str(output_path)
    output_dir = os.path.dirname(output_path)
    tmp_path = output_path + ".tmp"

    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.rename(tmp_path, output_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
