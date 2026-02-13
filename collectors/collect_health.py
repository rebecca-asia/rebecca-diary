#!/usr/bin/env python3
"""
collect_health.py - Mac system health collector for Rebecca's Room

Collects CPU, memory, disk, temperature, and uptime metrics from macOS,
delegates classification/scoring to domain layer, and writes the result
to src/data/health.json.

Usage:
    python3 collectors/collect_health.py        # normal run
    python3 collectors/collect_health.py -v     # verbose/debug output

Dependencies: Python 3.9+ stdlib only (no pip packages)
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# -- Domain layer import --
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from domain import health as domain_health
from domain.schema import inject_version, inject_staleness, write_json_atomic

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "src", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "health.json")

JST = timezone(timedelta(hours=9))

VERBOSE = "-v" in sys.argv


def log(msg):
    """Print debug message when verbose mode is enabled."""
    if VERBOSE:
        print(f"[DEBUG] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Metric Collection Functions (I/O — unchanged)
# ---------------------------------------------------------------------------

def get_cpu_usage():
    # type: () -> float
    """
    Get total CPU usage percentage using /usr/bin/top.
    Parses the "CPU usage" line: "CPU usage: XX.XX% user, YY.YY% sys, ZZ.ZZ% idle"
    Returns user + sys as total percentage.
    """
    result = subprocess.run(
        ["/usr/bin/top", "-l", "1", "-n", "0"],
        capture_output=True, text=True, timeout=30
    )
    output = result.stdout
    for line in output.splitlines():
        if "CPU usage" in line:
            log(f"CPU line: {line.strip()}")
            # Parse: "CPU usage: 12.50% user, 8.33% sys, 79.16% idle"
            match = re.search(
                r"(\d+\.\d+)%\s+user.*?(\d+\.\d+)%\s+sys",
                line
            )
            if match:
                user = float(match.group(1))
                sys_pct = float(match.group(2))
                total = round(user + sys_pct, 1)
                log(f"CPU: user={user}%, sys={sys_pct}%, total={total}%")
                return total
    raise ValueError("Could not parse CPU usage from top output")


def get_memory():
    # type: () -> dict
    """
    Get memory usage using /usr/bin/vm_stat and /usr/sbin/sysctl.
    - vm_stat: page statistics (page size from header, 16384 on Apple Silicon)
    - sysctl hw.memsize: total physical memory in bytes
    - used = (active + wired + compressor) * page_size
    - inactive pages are file cache, NOT counted as "used"
    """
    # Get total memory
    result = subprocess.run(
        ["/usr/sbin/sysctl", "-n", "hw.memsize"],
        capture_output=True, text=True, timeout=10
    )
    total_bytes = int(result.stdout.strip())
    total_gb = total_bytes / (1024 ** 3)
    log(f"Total memory: {total_bytes} bytes ({total_gb:.1f} GB)")

    # Get vm_stat
    result = subprocess.run(
        ["/usr/bin/vm_stat"],
        capture_output=True, text=True, timeout=10
    )
    vm_output = result.stdout
    log(f"vm_stat output:\n{vm_output}")

    # Parse page size from header line:
    # "Mach Virtual Memory Statistics: (page size of 16384 bytes)"
    page_size_match = re.search(r"page size of (\d+) bytes", vm_output)
    if page_size_match:
        page_size = int(page_size_match.group(1))
    else:
        # Fallback: Apple Silicon default
        page_size = 16384
    log(f"Page size: {page_size}")

    # Parse page counts - values end with a period
    def parse_pages(key):
        pattern = rf"^{re.escape(key)}:\s+(\d+)"
        match = re.search(pattern, vm_output, re.MULTILINE)
        if match:
            return int(match.group(1))
        return 0

    active = parse_pages("Pages active")
    wired = parse_pages("Pages wired down")
    # "Pages occupied by compressor" is the key on macOS
    compressor = parse_pages("Pages occupied by compressor")

    log(f"Pages - active: {active}, wired: {wired}, compressor: {compressor}")

    used_bytes = (active + wired + compressor) * page_size
    used_gb = used_bytes / (1024 ** 3)
    usage_percent = (used_bytes / total_bytes) * 100 if total_bytes > 0 else 0.0

    return {
        "used_gb": round(used_gb, 1),
        "total_gb": round(total_gb, 1),
        "usage_percent": round(usage_percent, 1),
    }


def get_disk():
    # type: () -> dict
    """
    Get disk usage using shutil.disk_usage('/').
    Returns used_gb and total_gb as integers.
    """
    usage = shutil.disk_usage("/")
    total_gb = int(usage.total / (1024 ** 3))
    used_gb = int(usage.used / (1024 ** 3))
    usage_percent = (usage.used / usage.total) * 100 if usage.total > 0 else 0.0

    log(f"Disk: used={used_gb}GB, total={total_gb}GB, usage={usage_percent:.1f}%")

    return {
        "used_gb": used_gb,
        "total_gb": total_gb,
        "usage_percent": round(usage_percent, 1),
    }


def get_temperature():
    # type: () -> float | None
    """
    Get CPU temperature using osx-cpu-temp if available.
    Returns None if the tool is not installed or fails.
    Never raises exceptions.
    """
    try:
        osx_cpu_temp = shutil.which("osx-cpu-temp")
        if osx_cpu_temp is None:
            log("osx-cpu-temp not found, skipping temperature")
            return None

        result = subprocess.run(
            [osx_cpu_temp],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout.strip()
        log(f"osx-cpu-temp output: {output}")

        # Parse output like "62.0°C" or "62.0 C"
        match = re.search(r"(\d+\.?\d*)", output)
        if match:
            temp = float(match.group(1))
            log(f"Temperature: {temp}C")
            return temp

        log("Could not parse temperature output")
        return None
    except Exception as e:
        log(f"Temperature collection failed: {e}")
        return None


def get_uptime():
    # type: () -> dict
    """
    Get system uptime using /usr/sbin/sysctl -n kern.boottime.
    Parses the epoch timestamp and computes delta from now.
    Returns {"seconds": int, "display": str} like "3d 14h 2m".
    """
    result = subprocess.run(
        ["/usr/sbin/sysctl", "-n", "kern.boottime"],
        capture_output=True, text=True, timeout=10
    )
    output = result.stdout.strip()
    log(f"kern.boottime: {output}")

    # Parse: "{ sec = 1707800000, usec = 0 } ..." or similar
    match = re.search(r"sec\s*=\s*(\d+)", output)
    if not match:
        raise ValueError(f"Could not parse kern.boottime: {output}")

    boot_epoch = int(match.group(1))
    now_epoch = int(time.time())
    delta_seconds = now_epoch - boot_epoch

    if delta_seconds < 0:
        delta_seconds = 0

    # Format display string
    days = delta_seconds // 86400
    hours = (delta_seconds % 86400) // 3600
    minutes = (delta_seconds % 3600) // 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if days > 0 or hours > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    display = " ".join(parts)

    log(f"Uptime: {delta_seconds}s ({display})")

    return {
        "seconds": delta_seconds,
        "display": display,
    }


# ---------------------------------------------------------------------------
# Main Logic
# ---------------------------------------------------------------------------

def collect_all():
    # type: () -> dict
    """
    Collect all raw metrics, delegate classification to domain layer.
    Individual metric failures set that metric to null instead of crashing.
    """
    now = datetime.now(JST)
    timestamp = now.isoformat()
    log(f"Collection started at {timestamp}")

    # -- Collect raw metrics --
    cpu_usage = 0.0
    try:
        cpu_usage = get_cpu_usage()
    except Exception as e:
        log(f"CPU collection failed: {e}")

    mem_raw = None
    mem_usage = 0.0
    try:
        mem_raw = get_memory()
        mem_usage = mem_raw["usage_percent"]
    except Exception as e:
        log(f"Memory collection failed: {e}")

    disk_raw = None
    disk_usage = 0.0
    try:
        disk_raw = get_disk()
        disk_usage = disk_raw["usage_percent"]
    except Exception as e:
        log(f"Disk collection failed: {e}")

    temp_celsius = None
    try:
        temp_celsius = get_temperature()
    except Exception as e:
        log(f"Temperature collection failed: {e}")

    uptime_raw = None
    uptime_seconds = 0
    try:
        uptime_raw = get_uptime()
        uptime_seconds = uptime_raw["seconds"]
    except Exception as e:
        log(f"Uptime collection failed: {e}")

    # -- Delegate to domain layer --
    raw_metrics = {
        "cpu_usage": cpu_usage,
        "mem_usage": mem_usage,
        "disk_usage": disk_usage,
        "temperature": temp_celsius,
        "uptime_seconds": uptime_seconds,
    }
    domain_result = domain_health.evaluate(raw_metrics)

    # -- Merge raw data with domain classifications --
    # CPU always has a default (0.0), so always build cpu_data
    cpu_data = {"usage_percent": cpu_usage, **domain_result["cpu"]}

    memory_data = None
    if mem_raw is not None:
        memory_data = {**mem_raw, **domain_result["memory"]}

    disk_data = None
    if disk_raw is not None:
        disk_data = {**disk_raw, **domain_result["disk"]}

    temperature_data = None
    if temp_celsius is not None and domain_result["temperature"] is not None:
        temperature_data = {"celsius": temp_celsius, **domain_result["temperature"]}

    uptime_data = None
    if uptime_raw is not None:
        uptime_data = {**uptime_raw, **domain_result["uptime"]}

    # -- Assemble output --
    output = {
        "timestamp": timestamp,
        "cpu": cpu_data,
        "memory": memory_data,
        "disk": disk_data,
        "temperature": temperature_data,
        "uptime": uptime_data,
        "overall": domain_result["overall"],
        "alert_level": domain_result["alert_level"],
        "alert_message": domain_result["alert_message"],
    }

    # -- Schema version and staleness --
    inject_version(output)
    inject_staleness(output, now)

    return output


def main():
    try:
        data = collect_all()
        write_json_atomic(data, OUTPUT_FILE)

        if VERBOSE:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"OK: score={data['overall']['score']}, "
                  f"alert={data['alert_level']}, "
                  f"timestamp={data['timestamp']}")
    except Exception as e:
        print(f"FATAL: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
