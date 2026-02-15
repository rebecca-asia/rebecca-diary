"""
domain/diary.py — Diary database repository layer.

SQLite-backed persistence for diary entries, translation cache,
and recap cache. Replaces file-based caching with a single DB.

Uses Python 3 standard library only (sqlite3).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ─── Schema ──────────────────────────────────────────────────────────────────

SCHEMA_VERSION = "3.0"

_CREATE_TABLES_SQL = """\
CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS diary_entries (
    date            TEXT PRIMARY KEY,
    memory_md       TEXT,
    obsidian_md     TEXT,
    integrated_md   TEXT NOT NULL,
    integrated_hash TEXT NOT NULL,
    html_en         TEXT NOT NULL,
    html_ja         TEXT,
    raw_md_ja       TEXT,
    recap_en        TEXT DEFAULT '',
    recap_ja        TEXT DEFAULT '',
    preview_en      TEXT DEFAULT '',
    preview_ja      TEXT DEFAULT '',
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS translation_cache (
    date        TEXT NOT NULL,
    source      TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    translation TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    PRIMARY KEY (date, source)
);

CREATE TABLE IF NOT EXISTS recap_cache (
    date         TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,
    recap_ja     TEXT NOT NULL,
    recap_en     TEXT NOT NULL,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entry_tags (
    date TEXT NOT NULL REFERENCES diary_entries(date),
    tag  TEXT NOT NULL,
    PRIMARY KEY (date, tag)
);

CREATE TABLE IF NOT EXISTS entry_metadata (
    date  TEXT NOT NULL REFERENCES diary_entries(date),
    key   TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (date, key)
);
"""

# ─── DB Initialization ───────────────────────────────────────────────────────


def _now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def init_db(db_path: str | Path) -> sqlite3.Connection:
    """Initialize the diary database, creating tables if needed.

    Enables WAL mode for better concurrent read performance.
    Sets schema_version in schema_meta if not present.

    Returns an open connection.
    """
    db_path = str(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(_CREATE_TABLES_SQL)

    # Set schema version if not present
    row = conn.execute(
        "SELECT value FROM schema_meta WHERE key = 'schema_version'"
    ).fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO schema_meta (key, value) VALUES (?, ?)",
            ("schema_version", SCHEMA_VERSION),
        )
        conn.commit()

    return conn


# ─── Schema Version ──────────────────────────────────────────────────────────


def get_schema_version(conn: sqlite3.Connection) -> str:
    """Get the schema version from the database."""
    row = conn.execute(
        "SELECT value FROM schema_meta WHERE key = 'schema_version'"
    ).fetchone()
    return row["value"] if row else ""


def set_schema_version(conn: sqlite3.Connection, version: str) -> None:
    """Set the schema version in the database."""
    conn.execute(
        "INSERT OR REPLACE INTO schema_meta (key, value) VALUES (?, ?)",
        ("schema_version", version),
    )
    conn.commit()


# ─── Entry CRUD ──────────────────────────────────────────────────────────────


def upsert_entry(
    conn: sqlite3.Connection,
    *,
    date: str,
    memory_md: Optional[str] = None,
    obsidian_md: Optional[str] = None,
    integrated_md: str,
    integrated_hash: str,
    html_en: str,
    html_ja: Optional[str] = None,
    raw_md_ja: Optional[str] = None,
    recap_en: str = "",
    recap_ja: str = "",
    preview_en: str = "",
    preview_ja: str = "",
) -> None:
    """Insert or update a diary entry."""
    now = _now_iso()

    # Check if entry exists to preserve created_at
    existing = conn.execute(
        "SELECT created_at FROM diary_entries WHERE date = ?", (date,)
    ).fetchone()
    created_at = existing["created_at"] if existing else now

    conn.execute(
        """\
        INSERT OR REPLACE INTO diary_entries
            (date, memory_md, obsidian_md, integrated_md, integrated_hash,
             html_en, html_ja, raw_md_ja,
             recap_en, recap_ja, preview_en, preview_ja,
             created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            date,
            memory_md,
            obsidian_md,
            integrated_md,
            integrated_hash,
            html_en,
            html_ja,
            raw_md_ja,
            recap_en,
            recap_ja,
            preview_en,
            preview_ja,
            created_at,
            now,
        ),
    )
    conn.commit()


def get_entry(conn: sqlite3.Connection, date: str) -> Optional[dict]:
    """Get a diary entry by date. Returns dict or None."""
    row = conn.execute(
        "SELECT * FROM diary_entries WHERE date = ?", (date,)
    ).fetchone()
    return dict(row) if row else None


def get_all_entries(conn: sqlite3.Connection, *, order: str = "DESC") -> list[dict]:
    """Get all diary entries, ordered by date.

    Args:
        order: "DESC" (newest first, default) or "ASC" (oldest first).
    """
    if order.upper() not in ("ASC", "DESC"):
        raise ValueError(f"order must be 'ASC' or 'DESC', got '{order}'")
    rows = conn.execute(
        f"SELECT * FROM diary_entries ORDER BY date {order.upper()}"
    ).fetchall()
    return [dict(r) for r in rows]


def delete_entry(conn: sqlite3.Connection, date: str) -> bool:
    """Delete a diary entry by date. Returns True if a row was deleted."""
    # Also clean up related tags and metadata
    conn.execute("DELETE FROM entry_tags WHERE date = ?", (date,))
    conn.execute("DELETE FROM entry_metadata WHERE date = ?", (date,))
    cursor = conn.execute("DELETE FROM diary_entries WHERE date = ?", (date,))
    conn.commit()
    return cursor.rowcount > 0


def count_entries(conn: sqlite3.Connection) -> int:
    """Return the total number of diary entries."""
    row = conn.execute("SELECT COUNT(*) as cnt FROM diary_entries").fetchone()
    return row["cnt"]


# ─── Translation Cache ───────────────────────────────────────────────────────


def get_translation_cache(
    conn: sqlite3.Connection, date: str, source: str, source_hash: str
) -> Optional[str]:
    """Get a cached translation if the source hash matches.

    Returns the translation text or None if not found / hash mismatch.
    """
    row = conn.execute(
        "SELECT source_hash, translation FROM translation_cache WHERE date = ? AND source = ?",
        (date, source),
    ).fetchone()
    if row is None:
        return None
    if row["source_hash"] != source_hash:
        return None
    return row["translation"]


def set_translation_cache(
    conn: sqlite3.Connection,
    date: str,
    source: str,
    source_hash: str,
    translation: str,
) -> None:
    """Save a translation to the cache."""
    conn.execute(
        """\
        INSERT OR REPLACE INTO translation_cache
            (date, source, source_hash, translation, created_at)
        VALUES (?, ?, ?, ?, ?)""",
        (date, source, source_hash, translation, _now_iso()),
    )
    conn.commit()


# ─── Recap Cache ─────────────────────────────────────────────────────────────


def get_recap_cache(
    conn: sqlite3.Connection, date: str, content_hash: str
) -> Optional[tuple[str, str]]:
    """Get a cached recap if the content hash matches.

    Returns (recap_ja, recap_en) or None if not found / hash mismatch.
    """
    row = conn.execute(
        "SELECT content_hash, recap_ja, recap_en FROM recap_cache WHERE date = ?",
        (date,),
    ).fetchone()
    if row is None:
        return None
    if row["content_hash"] != content_hash:
        return None
    return (row["recap_ja"], row["recap_en"])


def set_recap_cache(
    conn: sqlite3.Connection,
    date: str,
    content_hash: str,
    recap_ja: str,
    recap_en: str,
) -> None:
    """Save a recap to the cache."""
    conn.execute(
        """\
        INSERT OR REPLACE INTO recap_cache
            (date, content_hash, recap_ja, recap_en, created_at)
        VALUES (?, ?, ?, ?, ?)""",
        (date, content_hash, recap_ja, recap_en, _now_iso()),
    )
    conn.commit()


# ─── Tags & Metadata ────────────────────────────────────────────────────────


def set_tags(conn: sqlite3.Connection, date: str, tags: list[str]) -> None:
    """Set tags for a diary entry (replaces existing tags)."""
    conn.execute("DELETE FROM entry_tags WHERE date = ?", (date,))
    for tag in tags:
        conn.execute(
            "INSERT INTO entry_tags (date, tag) VALUES (?, ?)", (date, tag)
        )
    conn.commit()


def get_tags(conn: sqlite3.Connection, date: str) -> list[str]:
    """Get all tags for a diary entry."""
    rows = conn.execute(
        "SELECT tag FROM entry_tags WHERE date = ? ORDER BY tag", (date,)
    ).fetchall()
    return [r["tag"] for r in rows]


def set_metadata(conn: sqlite3.Connection, date: str, key: str, value: str) -> None:
    """Set a metadata key-value pair for a diary entry."""
    conn.execute(
        "INSERT OR REPLACE INTO entry_metadata (date, key, value) VALUES (?, ?, ?)",
        (date, key, value),
    )
    conn.commit()


def get_metadata(conn: sqlite3.Connection, date: str) -> dict[str, str]:
    """Get all metadata for a diary entry."""
    rows = conn.execute(
        "SELECT key, value FROM entry_metadata WHERE date = ? ORDER BY key",
        (date,),
    ).fetchall()
    return {r["key"]: r["value"] for r in rows}


# ─── Cache Migration ────────────────────────────────────────────────────────


def migrate_file_caches(
    conn: sqlite3.Connection,
    translation_cache_dir: Path,
    recap_cache_dir: Path,
) -> dict[str, int]:
    """Migrate file-based translation and recap caches to the database.

    Returns a dict with counts: {"translations": N, "recaps": M, "skipped": K}
    """
    import re

    stats = {"translations": 0, "recaps": 0, "skipped": 0}

    # Migrate translation cache
    if translation_cache_dir.is_dir():
        pattern = re.compile(r"^(\d{4}-\d{2}-\d{2})_(.+)\.json$")
        for f in sorted(translation_cache_dir.glob("*.json")):
            m = pattern.match(f.name)
            if not m:
                stats["skipped"] += 1
                continue
            date_str, source = m.group(1), m.group(2)
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                source_hash = data.get("hash", "")
                translation = data.get("translation", "")
                if source_hash and translation:
                    # Only insert if not already in DB
                    existing = conn.execute(
                        "SELECT source_hash FROM translation_cache WHERE date = ? AND source = ?",
                        (date_str, source),
                    ).fetchone()
                    if existing is None:
                        conn.execute(
                            "INSERT INTO translation_cache (date, source, source_hash, translation, created_at) VALUES (?, ?, ?, ?, ?)",
                            (date_str, source, source_hash, translation, _now_iso()),
                        )
                        stats["translations"] += 1
                    else:
                        stats["skipped"] += 1
                else:
                    stats["skipped"] += 1
            except (json.JSONDecodeError, OSError):
                stats["skipped"] += 1

    # Migrate recap cache
    if recap_cache_dir.is_dir():
        for f in sorted(recap_cache_dir.glob("*.json")):
            date_str = f.stem  # e.g., "2026-02-10"
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                content_hash = data.get("hash", "")
                recap_ja = data.get("ja", "")
                recap_en = data.get("en", "")
                if content_hash and recap_ja and recap_en:
                    existing = conn.execute(
                        "SELECT content_hash FROM recap_cache WHERE date = ?",
                        (date_str,),
                    ).fetchone()
                    if existing is None:
                        conn.execute(
                            "INSERT INTO recap_cache (date, content_hash, recap_ja, recap_en, created_at) VALUES (?, ?, ?, ?, ?)",
                            (date_str, content_hash, recap_ja, recap_en, _now_iso()),
                        )
                        stats["recaps"] += 1
                    else:
                        stats["skipped"] += 1
                else:
                    stats["skipped"] += 1
            except (json.JSONDecodeError, OSError):
                stats["skipped"] += 1

    conn.commit()
    return stats
