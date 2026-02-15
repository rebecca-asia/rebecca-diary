"""Tests for domain/diary.py — diary database repository layer."""

import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from domain.diary import (
    SCHEMA_VERSION,
    init_db,
    get_schema_version,
    set_schema_version,
    upsert_entry,
    get_entry,
    get_all_entries,
    delete_entry,
    count_entries,
    get_translation_cache,
    set_translation_cache,
    get_recap_cache,
    set_recap_cache,
    set_tags,
    get_tags,
    set_metadata,
    get_metadata,
    migrate_file_caches,
)


class DiaryDBTestCase(unittest.TestCase):
    """Base test case that provides a temp DB for each test."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db_path = self.tmp.name
        self.conn = init_db(self.db_path)

    def tearDown(self):
        self.conn.close()
        os.unlink(self.db_path)


# ─── DB Initialization ───────────────────────────────────────────────────────


class TestInitDB(DiaryDBTestCase):
    """Test database initialization."""

    def test_tables_exist(self):
        """All expected tables are created."""
        tables = {
            row[0]
            for row in self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        expected = {
            "schema_meta",
            "diary_entries",
            "translation_cache",
            "recap_cache",
            "entry_tags",
            "entry_metadata",
        }
        self.assertTrue(expected.issubset(tables), f"Missing tables: {expected - tables}")

    def test_wal_mode(self):
        """WAL journal mode is enabled."""
        row = self.conn.execute("PRAGMA journal_mode").fetchone()
        self.assertEqual(row[0], "wal")

    def test_foreign_keys_enabled(self):
        """Foreign keys are enabled."""
        row = self.conn.execute("PRAGMA foreign_keys").fetchone()
        self.assertEqual(row[0], 1)

    def test_schema_version_set(self):
        """Schema version is set on first init."""
        self.assertEqual(get_schema_version(self.conn), SCHEMA_VERSION)

    def test_idempotent_init(self):
        """Calling init_db twice does not error or reset schema version."""
        set_schema_version(self.conn, "99.0")
        self.conn.close()
        conn2 = init_db(self.db_path)
        self.assertEqual(get_schema_version(conn2), "99.0")
        conn2.close()

    def test_row_factory(self):
        """Connection uses Row factory for dict-like access."""
        self.assertIs(self.conn.row_factory, sqlite3.Row)


# ─── Schema Version ──────────────────────────────────────────────────────────


class TestSchemaVersion(DiaryDBTestCase):
    """Test schema version management."""

    def test_get_default_version(self):
        self.assertEqual(get_schema_version(self.conn), SCHEMA_VERSION)

    def test_set_and_get_version(self):
        set_schema_version(self.conn, "4.0")
        self.assertEqual(get_schema_version(self.conn), "4.0")

    def test_overwrite_version(self):
        set_schema_version(self.conn, "4.0")
        set_schema_version(self.conn, "5.0")
        self.assertEqual(get_schema_version(self.conn), "5.0")


# ─── Entry CRUD ──────────────────────────────────────────────────────────────


class TestUpsertEntry(DiaryDBTestCase):
    """Test diary entry insertion and update."""

    def _make_entry(self, **overrides):
        defaults = {
            "date": "2026-02-16",
            "memory_md": "# Memory\nToday was good.",
            "obsidian_md": "# Obsidian\nReport.",
            "integrated_md": "## Combined\nAll content.",
            "integrated_hash": "abc123",
            "html_en": "<h3>Combined</h3><p>All content.</p>",
            "html_ja": "<h3>結合</h3><p>全コンテンツ。</p>",
            "raw_md_ja": "## 結合\n全コンテンツ。",
            "recap_en": "Good day!",
            "recap_ja": "いい日だった！",
            "preview_en": "Today was good.",
            "preview_ja": "今日はよかった。",
        }
        defaults.update(overrides)
        return defaults

    def test_insert_new_entry(self):
        upsert_entry(self.conn, **self._make_entry())
        entry = get_entry(self.conn, "2026-02-16")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["date"], "2026-02-16")
        self.assertEqual(entry["memory_md"], "# Memory\nToday was good.")
        self.assertEqual(entry["html_en"], "<h3>Combined</h3><p>All content.</p>")

    def test_update_preserves_created_at(self):
        upsert_entry(self.conn, **self._make_entry())
        entry1 = get_entry(self.conn, "2026-02-16")
        created_at_1 = entry1["created_at"]

        upsert_entry(self.conn, **self._make_entry(html_en="<p>Updated</p>"))
        entry2 = get_entry(self.conn, "2026-02-16")
        self.assertEqual(entry2["created_at"], created_at_1)
        self.assertEqual(entry2["html_en"], "<p>Updated</p>")
        self.assertNotEqual(entry2["updated_at"], entry2["created_at"])

    def test_nullable_fields(self):
        upsert_entry(
            self.conn,
            date="2026-02-15",
            integrated_md="content",
            integrated_hash="hash",
            html_en="<p>content</p>",
        )
        entry = get_entry(self.conn, "2026-02-15")
        self.assertIsNone(entry["memory_md"])
        self.assertIsNone(entry["obsidian_md"])
        self.assertIsNone(entry["html_ja"])
        self.assertEqual(entry["recap_en"], "")

    def test_unicode_content(self):
        upsert_entry(
            self.conn,
            date="2026-02-14",
            integrated_md="日本語テスト 🔥 émojis",
            integrated_hash="uni123",
            html_en="<p>日本語テスト 🔥 émojis</p>",
        )
        entry = get_entry(self.conn, "2026-02-14")
        self.assertIn("🔥", entry["integrated_md"])
        self.assertIn("日本語", entry["integrated_md"])


class TestGetEntry(DiaryDBTestCase):
    """Test entry retrieval."""

    def test_get_nonexistent(self):
        self.assertIsNone(get_entry(self.conn, "9999-99-99"))

    def test_get_returns_dict(self):
        upsert_entry(
            self.conn,
            date="2026-02-16",
            integrated_md="test",
            integrated_hash="h",
            html_en="<p>test</p>",
        )
        entry = get_entry(self.conn, "2026-02-16")
        self.assertIsInstance(entry, dict)
        self.assertIn("date", entry)
        self.assertIn("created_at", entry)
        self.assertIn("updated_at", entry)


class TestGetAllEntries(DiaryDBTestCase):
    """Test getting all entries."""

    def test_empty_db(self):
        self.assertEqual(get_all_entries(self.conn), [])

    def test_order_desc(self):
        for d in ["2026-02-10", "2026-02-12", "2026-02-11"]:
            upsert_entry(
                self.conn,
                date=d,
                integrated_md=f"content {d}",
                integrated_hash=f"h{d}",
                html_en=f"<p>{d}</p>",
            )
        entries = get_all_entries(self.conn, order="DESC")
        dates = [e["date"] for e in entries]
        self.assertEqual(dates, ["2026-02-12", "2026-02-11", "2026-02-10"])

    def test_order_asc(self):
        for d in ["2026-02-12", "2026-02-10", "2026-02-11"]:
            upsert_entry(
                self.conn,
                date=d,
                integrated_md=f"content {d}",
                integrated_hash=f"h{d}",
                html_en=f"<p>{d}</p>",
            )
        entries = get_all_entries(self.conn, order="ASC")
        dates = [e["date"] for e in entries]
        self.assertEqual(dates, ["2026-02-10", "2026-02-11", "2026-02-12"])

    def test_invalid_order(self):
        with self.assertRaises(ValueError):
            get_all_entries(self.conn, order="RANDOM")


class TestDeleteEntry(DiaryDBTestCase):
    """Test entry deletion."""

    def test_delete_existing(self):
        upsert_entry(
            self.conn,
            date="2026-02-16",
            integrated_md="test",
            integrated_hash="h",
            html_en="<p>test</p>",
        )
        self.assertTrue(delete_entry(self.conn, "2026-02-16"))
        self.assertIsNone(get_entry(self.conn, "2026-02-16"))

    def test_delete_nonexistent(self):
        self.assertFalse(delete_entry(self.conn, "9999-99-99"))

    def test_delete_cleans_tags_and_metadata(self):
        upsert_entry(
            self.conn,
            date="2026-02-16",
            integrated_md="test",
            integrated_hash="h",
            html_en="<p>test</p>",
        )
        set_tags(self.conn, "2026-02-16", ["work", "code"])
        set_metadata(self.conn, "2026-02-16", "mood", "good")
        delete_entry(self.conn, "2026-02-16")
        self.assertEqual(get_tags(self.conn, "2026-02-16"), [])
        self.assertEqual(get_metadata(self.conn, "2026-02-16"), {})


class TestCountEntries(DiaryDBTestCase):
    """Test entry counting."""

    def test_empty(self):
        self.assertEqual(count_entries(self.conn), 0)

    def test_with_entries(self):
        for d in ["2026-02-10", "2026-02-11", "2026-02-12"]:
            upsert_entry(
                self.conn,
                date=d,
                integrated_md="c",
                integrated_hash="h",
                html_en="<p>c</p>",
            )
        self.assertEqual(count_entries(self.conn), 3)


# ─── Translation Cache ───────────────────────────────────────────────────────


class TestTranslationCache(DiaryDBTestCase):
    """Test translation cache operations."""

    def test_set_and_get(self):
        set_translation_cache(self.conn, "2026-02-16", "integrated", "hash1", "翻訳テキスト")
        result = get_translation_cache(self.conn, "2026-02-16", "integrated", "hash1")
        self.assertEqual(result, "翻訳テキスト")

    def test_hash_mismatch(self):
        set_translation_cache(self.conn, "2026-02-16", "integrated", "hash1", "翻訳テキスト")
        result = get_translation_cache(self.conn, "2026-02-16", "integrated", "wrong_hash")
        self.assertIsNone(result)

    def test_not_found(self):
        result = get_translation_cache(self.conn, "2026-02-16", "integrated", "hash1")
        self.assertIsNone(result)

    def test_overwrite(self):
        set_translation_cache(self.conn, "2026-02-16", "integrated", "hash1", "v1")
        set_translation_cache(self.conn, "2026-02-16", "integrated", "hash2", "v2")
        self.assertIsNone(get_translation_cache(self.conn, "2026-02-16", "integrated", "hash1"))
        self.assertEqual(get_translation_cache(self.conn, "2026-02-16", "integrated", "hash2"), "v2")

    def test_multiple_sources(self):
        set_translation_cache(self.conn, "2026-02-16", "memory", "h1", "memory翻訳")
        set_translation_cache(self.conn, "2026-02-16", "obsidian", "h2", "obsidian翻訳")
        self.assertEqual(
            get_translation_cache(self.conn, "2026-02-16", "memory", "h1"), "memory翻訳"
        )
        self.assertEqual(
            get_translation_cache(self.conn, "2026-02-16", "obsidian", "h2"), "obsidian翻訳"
        )

    def test_multiple_dates(self):
        set_translation_cache(self.conn, "2026-02-15", "integrated", "h1", "昨日")
        set_translation_cache(self.conn, "2026-02-16", "integrated", "h2", "今日")
        self.assertEqual(
            get_translation_cache(self.conn, "2026-02-15", "integrated", "h1"), "昨日"
        )
        self.assertEqual(
            get_translation_cache(self.conn, "2026-02-16", "integrated", "h2"), "今日"
        )


# ─── Recap Cache ─────────────────────────────────────────────────────────────


class TestRecapCache(DiaryDBTestCase):
    """Test recap cache operations."""

    def test_set_and_get(self):
        set_recap_cache(self.conn, "2026-02-16", "hash1", "日本語recap", "English recap")
        result = get_recap_cache(self.conn, "2026-02-16", "hash1")
        self.assertEqual(result, ("日本語recap", "English recap"))

    def test_hash_mismatch(self):
        set_recap_cache(self.conn, "2026-02-16", "hash1", "ja", "en")
        result = get_recap_cache(self.conn, "2026-02-16", "wrong")
        self.assertIsNone(result)

    def test_not_found(self):
        result = get_recap_cache(self.conn, "2026-02-16", "hash1")
        self.assertIsNone(result)

    def test_overwrite(self):
        set_recap_cache(self.conn, "2026-02-16", "hash1", "old_ja", "old_en")
        set_recap_cache(self.conn, "2026-02-16", "hash2", "new_ja", "new_en")
        self.assertIsNone(get_recap_cache(self.conn, "2026-02-16", "hash1"))
        self.assertEqual(get_recap_cache(self.conn, "2026-02-16", "hash2"), ("new_ja", "new_en"))


# ─── Tags & Metadata ────────────────────────────────────────────────────────


class TestTags(DiaryDBTestCase):
    """Test tag operations."""

    def setUp(self):
        super().setUp()
        upsert_entry(
            self.conn,
            date="2026-02-16",
            integrated_md="test",
            integrated_hash="h",
            html_en="<p>test</p>",
        )

    def test_set_and_get_tags(self):
        set_tags(self.conn, "2026-02-16", ["work", "code", "debug"])
        tags = get_tags(self.conn, "2026-02-16")
        self.assertEqual(tags, ["code", "debug", "work"])  # sorted

    def test_empty_tags(self):
        self.assertEqual(get_tags(self.conn, "2026-02-16"), [])

    def test_replace_tags(self):
        set_tags(self.conn, "2026-02-16", ["old1", "old2"])
        set_tags(self.conn, "2026-02-16", ["new1"])
        self.assertEqual(get_tags(self.conn, "2026-02-16"), ["new1"])

    def test_tags_for_nonexistent_entry(self):
        self.assertEqual(get_tags(self.conn, "9999-99-99"), [])


class TestMetadata(DiaryDBTestCase):
    """Test metadata operations."""

    def setUp(self):
        super().setUp()
        upsert_entry(
            self.conn,
            date="2026-02-16",
            integrated_md="test",
            integrated_hash="h",
            html_en="<p>test</p>",
        )

    def test_set_and_get(self):
        set_metadata(self.conn, "2026-02-16", "mood", "good")
        set_metadata(self.conn, "2026-02-16", "energy", "high")
        meta = get_metadata(self.conn, "2026-02-16")
        self.assertEqual(meta, {"energy": "high", "mood": "good"})

    def test_overwrite_value(self):
        set_metadata(self.conn, "2026-02-16", "mood", "good")
        set_metadata(self.conn, "2026-02-16", "mood", "bad")
        self.assertEqual(get_metadata(self.conn, "2026-02-16")["mood"], "bad")

    def test_empty_metadata(self):
        self.assertEqual(get_metadata(self.conn, "2026-02-16"), {})


# ─── Cache Migration ────────────────────────────────────────────────────────


class TestMigrateFileCaches(DiaryDBTestCase):
    """Test file-based cache migration to DB."""

    def setUp(self):
        super().setUp()
        self.tmpdir = tempfile.mkdtemp()
        self.trans_dir = Path(self.tmpdir) / "translation-cache"
        self.recap_dir = Path(self.tmpdir) / "recap-cache"
        self.trans_dir.mkdir()
        self.recap_dir.mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir)
        super().tearDown()

    def _write_translation(self, filename, hash_val, translation):
        data = {"hash": hash_val, "translation": translation}
        (self.trans_dir / filename).write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )

    def _write_recap(self, filename, hash_val, ja, en):
        data = {"hash": hash_val, "ja": ja, "en": en}
        (self.recap_dir / filename).write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )

    def test_migrate_translations(self):
        self._write_translation("2026-02-10_integrated.json", "h1", "翻訳1")
        self._write_translation("2026-02-11_memory.json", "h2", "翻訳2")
        stats = migrate_file_caches(self.conn, self.trans_dir, self.recap_dir)
        self.assertEqual(stats["translations"], 2)
        self.assertEqual(
            get_translation_cache(self.conn, "2026-02-10", "integrated", "h1"), "翻訳1"
        )
        self.assertEqual(
            get_translation_cache(self.conn, "2026-02-11", "memory", "h2"), "翻訳2"
        )

    def test_migrate_recaps(self):
        self._write_recap("2026-02-10.json", "h1", "JA recap", "EN recap")
        stats = migrate_file_caches(self.conn, self.trans_dir, self.recap_dir)
        self.assertEqual(stats["recaps"], 1)
        self.assertEqual(
            get_recap_cache(self.conn, "2026-02-10", "h1"), ("JA recap", "EN recap")
        )

    def test_skip_existing_translation(self):
        set_translation_cache(self.conn, "2026-02-10", "integrated", "h1", "DB version")
        self._write_translation("2026-02-10_integrated.json", "h1", "File version")
        stats = migrate_file_caches(self.conn, self.trans_dir, self.recap_dir)
        self.assertEqual(stats["skipped"], 1)
        self.assertEqual(stats["translations"], 0)
        # DB version preserved
        self.assertEqual(
            get_translation_cache(self.conn, "2026-02-10", "integrated", "h1"), "DB version"
        )

    def test_skip_existing_recap(self):
        set_recap_cache(self.conn, "2026-02-10", "h1", "DB ja", "DB en")
        self._write_recap("2026-02-10.json", "h1", "File ja", "File en")
        stats = migrate_file_caches(self.conn, self.trans_dir, self.recap_dir)
        self.assertEqual(stats["skipped"], 1)
        self.assertEqual(stats["recaps"], 0)

    def test_skip_malformed_json(self):
        (self.trans_dir / "2026-02-10_integrated.json").write_text(
            "not json", encoding="utf-8"
        )
        stats = migrate_file_caches(self.conn, self.trans_dir, self.recap_dir)
        self.assertEqual(stats["skipped"], 1)

    def test_skip_non_matching_filename(self):
        (self.trans_dir / "random_file.json").write_text(
            '{"hash":"h","translation":"t"}', encoding="utf-8"
        )
        stats = migrate_file_caches(self.conn, self.trans_dir, self.recap_dir)
        self.assertEqual(stats["skipped"], 1)

    def test_empty_dirs(self):
        stats = migrate_file_caches(self.conn, self.trans_dir, self.recap_dir)
        self.assertEqual(stats, {"translations": 0, "recaps": 0, "skipped": 0})

    def test_nonexistent_dirs(self):
        missing = Path(self.tmpdir) / "nope"
        stats = migrate_file_caches(self.conn, missing, missing)
        self.assertEqual(stats, {"translations": 0, "recaps": 0, "skipped": 0})

    def test_skip_incomplete_translation(self):
        """Translation with missing hash or translation field is skipped."""
        data = {"hash": "", "translation": "text"}
        (self.trans_dir / "2026-02-10_integrated.json").write_text(
            json.dumps(data), encoding="utf-8"
        )
        stats = migrate_file_caches(self.conn, self.trans_dir, self.recap_dir)
        self.assertEqual(stats["skipped"], 1)

    def test_skip_incomplete_recap(self):
        """Recap with missing fields is skipped."""
        data = {"hash": "h", "ja": "", "en": "text"}
        (self.recap_dir / "2026-02-10.json").write_text(
            json.dumps(data), encoding="utf-8"
        )
        stats = migrate_file_caches(self.conn, self.trans_dir, self.recap_dir)
        self.assertEqual(stats["skipped"], 1)

    def test_mixed_migration(self):
        """Mix of translations and recaps."""
        self._write_translation("2026-02-10_integrated.json", "h1", "翻訳1")
        self._write_translation("2026-02-11_obsidian.json", "h2", "翻訳2")
        self._write_recap("2026-02-10.json", "rh1", "JA1", "EN1")
        self._write_recap("2026-02-12.json", "rh2", "JA2", "EN2")
        stats = migrate_file_caches(self.conn, self.trans_dir, self.recap_dir)
        self.assertEqual(stats["translations"], 2)
        self.assertEqual(stats["recaps"], 2)
        self.assertEqual(stats["skipped"], 0)


# ─── Edge Cases ──────────────────────────────────────────────────────────────


class TestEdgeCases(DiaryDBTestCase):
    """Test edge cases and robustness."""

    def test_large_content(self):
        """Very large markdown content is handled."""
        large_md = "# Big\n" + ("Lorem ipsum. " * 10000)
        upsert_entry(
            self.conn,
            date="2026-02-16",
            integrated_md=large_md,
            integrated_hash="big",
            html_en=f"<p>{large_md}</p>",
        )
        entry = get_entry(self.conn, "2026-02-16")
        self.assertEqual(len(entry["integrated_md"]), len(large_md))

    def test_special_characters_in_content(self):
        """SQL-sensitive characters don't break queries."""
        tricky = "O'Brien said \"hello\" and 100% of -- comments; DROP TABLE"
        upsert_entry(
            self.conn,
            date="2026-02-16",
            integrated_md=tricky,
            integrated_hash="tricky",
            html_en=f"<p>{tricky}</p>",
        )
        entry = get_entry(self.conn, "2026-02-16")
        self.assertEqual(entry["integrated_md"], tricky)

    def test_empty_string_fields(self):
        """Empty strings are stored correctly (not converted to NULL)."""
        upsert_entry(
            self.conn,
            date="2026-02-16",
            integrated_md="content",
            integrated_hash="h",
            html_en="<p>c</p>",
            recap_en="",
            recap_ja="",
            preview_en="",
            preview_ja="",
        )
        entry = get_entry(self.conn, "2026-02-16")
        self.assertEqual(entry["recap_en"], "")
        self.assertEqual(entry["recap_ja"], "")

    def test_timestamps_are_iso(self):
        """Timestamps are valid ISO 8601 format."""
        upsert_entry(
            self.conn,
            date="2026-02-16",
            integrated_md="test",
            integrated_hash="h",
            html_en="<p>t</p>",
        )
        entry = get_entry(self.conn, "2026-02-16")
        # Should be parseable
        from datetime import datetime
        datetime.fromisoformat(entry["created_at"])
        datetime.fromisoformat(entry["updated_at"])


if __name__ == "__main__":
    unittest.main()
