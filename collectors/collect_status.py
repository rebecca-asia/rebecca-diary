#!/usr/bin/env python3
"""
collect_status.py - Rebecca's Room Status Collector

Determines Rebecca's presence status (online/away/sleeping/offline)
based on OpenClaw Gateway process, recent file activity, and time of day.

Output: src/data/status.json (atomic write via .tmp + os.rename)
Frequency: every 1 minute (cron / launchd)
Dependencies: Python 3.9+ stdlib only (no pip packages)

Usage:
    python3 collectors/collect_status.py          # normal run
    python3 collectors/collect_status.py -v       # verbose/debug output
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Tuple

# -- Domain layer import --
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from domain import presence as domain_presence
from domain.constants import HEARTBEAT_THRESHOLD_SEC
from domain.schema import inject_version, inject_staleness, write_json_atomic

# -- Constants ----------------------------------------------------------------

JST = timezone(timedelta(hours=9))

# Project paths (relative to project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "src" / "data"
OUTPUT_FILE = OUTPUT_DIR / "status.json"

# OpenClaw paths
OPENCLAW_WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = OPENCLAW_WORKSPACE / "memory"
HEARTBEAT_FILE = OPENCLAW_WORKSPACE / "HEARTBEAT.md"

# Verbose flag (set via -v CLI arg)
VERBOSE = False

# -- Utility ------------------------------------------------------------------

def log(msg: str) -> None:
    """Print debug message if verbose mode is enabled."""
    if VERBOSE:
        print(f"[status] {msg}", file=sys.stderr)


def now_jst() -> datetime:
    """Return current time in JST."""
    return datetime.now(JST)


def format_iso(dt: datetime) -> str:
    """Format datetime as ISO 8601 with timezone (e.g. 2026-02-13T14:30:00+09:00)."""
    return dt.isoformat(timespec="seconds")


# -- Core functions -----------------------------------------------------------

def check_gateway() -> bool:
    """
    Check if OpenClaw Gateway is alive.

    Primary: pgrep -x openclaw-gateway (exact match, NOT -f which catches Chrome helpers)
    Fallback: HEARTBEAT.md exists and mtime < 5 minutes ago
    """
    # Primary: pgrep -x for exact process name match
    try:
        result = subprocess.run(
            ["/usr/bin/pgrep", "-x", "openclaw-gateway"],
            capture_output=True,
            timeout=5,
        )
        if result.returncode == 0:
            pids = result.stdout.decode().strip()
            log(f"Gateway found via pgrep (PIDs: {pids})")
            return True
        log("Gateway not found via pgrep")
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        log(f"pgrep failed: {e}")

    # Fallback: check HEARTBEAT.md mtime
    try:
        if HEARTBEAT_FILE.exists():
            mtime = HEARTBEAT_FILE.stat().st_mtime
            age = time.time() - mtime
            if age < HEARTBEAT_THRESHOLD_SEC:
                log(f"Gateway alive via HEARTBEAT.md (age: {age:.0f}s)")
                return True
            else:
                log(f"HEARTBEAT.md too old (age: {age:.0f}s, threshold: {HEARTBEAT_THRESHOLD_SEC}s)")
        else:
            log(f"HEARTBEAT.md not found at {HEARTBEAT_FILE}")
    except OSError as e:
        log(f"HEARTBEAT.md check failed: {e}")

    return False


def get_last_activity() -> Tuple[Optional[datetime], Optional[Path]]:
    """
    Scan ~/.openclaw/workspace/memory/*.md for the most recently modified file.

    Returns:
        (mtime as datetime in JST, path to the file) or (None, None) if unavailable
    """
    try:
        if not MEMORY_DIR.is_dir():
            log(f"Memory directory not found: {MEMORY_DIR}")
            return None, None

        md_files = list(MEMORY_DIR.glob("*.md"))
        if not md_files:
            log("No .md files in memory directory")
            return None, None

        # Find the most recently modified file
        latest_file = max(md_files, key=lambda f: f.stat().st_mtime)
        mtime = latest_file.stat().st_mtime
        dt = datetime.fromtimestamp(mtime, tz=JST)
        log(f"Last activity: {latest_file.name} at {format_iso(dt)}")
        return dt, latest_file

    except OSError as e:
        log(f"Error scanning memory directory: {e}")
        return None, None


def get_activity_type(last_activity_path: Optional[Path]) -> str:
    """
    Guess activity type from the most recently modified file path.

    Never raises exceptions.
    """
    if last_activity_path is None:
        return "unknown"

    try:
        path_str = str(last_activity_path)

        # Check known directories
        if "memory" in path_str and path_str.endswith(".md"):
            return "memory_write"
        if "diary" in path_str:
            return "diary_update"
        if "Obsidian" in path_str:
            return "obsidian_note"

        return "unknown"
    except Exception:
        return "unknown"


# -- Main ---------------------------------------------------------------------

def main() -> None:
    global VERBOSE

    if "-v" in sys.argv or "--verbose" in sys.argv:
        VERBOSE = True

    log("Starting status collection...")

    # Step 1: Gateway check
    gateway_alive = check_gateway()

    # Step 2: Last activity
    last_activity, last_activity_path = get_last_activity()

    # Step 3: Delegate to domain layer
    now = now_jst()
    presence_result = domain_presence.evaluate(gateway_alive, last_activity, now)

    # Step 4: Activity type
    activity_type = get_activity_type(last_activity_path)

    # Step 5: Build output
    output = {
        "timestamp": format_iso(now),
        "status": presence_result["status"],
        "label": presence_result["label"],
        "emoji": presence_result["emoji"],
        "last_activity": format_iso(last_activity) if last_activity else None,
        "activity_type": activity_type,
        "gateway_alive": gateway_alive,
        "time_context": presence_result["time_context"],
    }

    # -- Schema version and staleness --
    inject_version(output)
    inject_staleness(output, now)

    log(f"Output: {json.dumps(output, ensure_ascii=False)}")

    # Step 6: Atomic write
    write_json_atomic(output, OUTPUT_FILE)

    if VERBOSE:
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
