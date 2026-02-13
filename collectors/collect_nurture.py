#!/usr/bin/env python3
"""
collect_nurture.py - Nurture parameter calculator for Rebecca's Room

Reads health.json, status.json, and visit_log.json to compute Rebecca's
nurture state: mood, energy, trust, intimacy, EXP, and level.
Outputs src/data/nurture.json and updates src/data/visit_log.json.

Calculation logic delegated to domain/nurture.py (Phase 2A).
This collector handles I/O only.

Usage:
    python3 collectors/collect_nurture.py        # normal run
    python3 collectors/collect_nurture.py -v     # verbose/debug output

Dependencies: Python 3.9+ stdlib only (no pip packages)
Frequency: every 5 minutes (cron)
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# -- Domain layer import --
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from domain import nurture as domain_nurture
from domain.schema import write_json_atomic, inject_version, inject_staleness

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
# Main
# ---------------------------------------------------------------------------

def main():
    log("Starting nurture collection...")

    # Load input data (graceful degradation)
    health_data = load_json(HEALTH_FILE)
    status_data = load_json(STATUS_FILE)
    skills_data = load_json(SKILLS_FILE)
    visit_log = load_visit_log()

    now = datetime.now(JST)

    # Calculate nurture parameters via domain layer
    nurture, updated_visit_log = domain_nurture.evaluate(
        health_data, status_data, skills_data, visit_log, now
    )

    # Inject schema version and staleness
    inject_version(nurture)
    inject_staleness(nurture, now)

    # Write outputs
    write_json_atomic(nurture, str(NURTURE_FILE))
    write_json_atomic(updated_visit_log, str(VISIT_LOG_FILE))

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
