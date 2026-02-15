#!/usr/bin/env python3
"""
update_diary.py — Rebecca's Diary SSG.

Scans memory and Obsidian directories for daily notes,
generates a full timeline HTML, and updates the website.

Phase 3: SQLite-backed diary database for persistent storage.
Default: process today only → save to DB → read all from DB → diary.html
--rebuild: process all dates → save to DB → read all from DB → diary.html
--migrate-cache: migrate file-based caches to DB
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sqlite3
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from string import Template
from typing import Optional

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure project root is on sys.path so `domain` package can be imported
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

DEFAULT_CONFIG = {
    "memory_dir": Path("/Users/rebeccacyber/.openclaw/workspace/memory"),
    "obsidian_dir": Path("/Users/rebeccacyber/Documents/Obsidian Vault"),
    "template_html": BASE_DIR / "src" / "template.html",
    "index_html": BASE_DIR / "src" / "diary.html",
}

CARDS_PLACEHOLDER = "<!-- DIARY_CARDS_PLACEHOLDER -->"
ENTRIES_PLACEHOLDER = "<!-- DIARY_ENTRIES_PLACEHOLDER -->"

TRANSLATION_CACHE_DIR = BASE_DIR / ".translation-cache"
RECAP_CACHE_DIR = BASE_DIR / ".recap-cache"
DB_PATH = BASE_DIR / "diary.db"
OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"
TRANSLATION_MODEL = "anthropic/claude-sonnet-4-5"


def _gateway_url_and_token() -> tuple[str, str]:
    """Read Gateway URL and auth token from OpenClaw config."""
    config = json.loads(OPENCLAW_CONFIG.read_text(encoding="utf-8"))
    gw = config.get("gateway", {})
    port = gw.get("port", 18789)
    token = gw.get("auth", {}).get("token", "")
    return f"http://127.0.0.1:{port}/v1/chat/completions", token

# ─── Integration Logic ───────────────────────────────────────────────────────

def merge_markdown_sources(memory_md: Optional[str], obsidian_md: Optional[str]) -> str:
    """Combine memory and obsidian markdown into a single integrated markdown."""
    parts = []

    if memory_md:
        parts.append("## 🧠 Internal Memory (OpenClaw)")
        parts.append(memory_md.strip())

    if obsidian_md:
        if parts:
            parts.append("\n---\n")
        parts.append("## 📝 Daily Report (Obsidian)")
        parts.append(obsidian_md.strip())

    return "\n\n".join(parts)

# ─── Logging ─────────────────────────────────────────────────────────────────

log = logging.getLogger("update_diary")


def setup_logging(*, verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    log.setLevel(level)
    log.addHandler(handler)


# ─── HTML Templates ─────────────────────────────────────────────────────────

ENTRY_TEMPLATE = Template("""\
        <article class="diary-entry" id="diary-$date">
            <a href="#top" class="back-link">&larr; Back to list</a>
            <div class="entry-header">
                <img src="assets/rebecca/transparent/レベッカ_顔絵ニュートラル.png" alt="" class="entry-avatar">
                <div class="entry-date">$date</div>
            </div>
            <div class="entry-content">
$sections
            </div>
        </article>""")

CARD_TEMPLATE = Template("""\
            <a href="#diary-$date" class="diary-card">
                <div class="card-date">$emoji $date</div>
                <div class="card-preview lang-content" data-lang="ja">$preview_ja</div>
                <div class="card-preview lang-content" data-lang="en">$preview_en</div>
                <div class="card-sources">$sources</div>
            </a>""")

SECTION_TEMPLATE = Template("""\
        <div class="section-$css_class">
            <h3>$icon $title</h3>
            <div class="lang-content" data-lang="ja">
$body_ja
            </div>
            <div class="lang-content" data-lang="en">
$body_en
            </div>
        </div>""")


# ─── Data Structures ────────────────────────────────────────────────────────

@dataclass
class DiarySection:
    title: str
    icon: str
    css_class: str
    body_html: str
    raw_md: str = ""  # Original markdown for preview extraction
    body_html_ja: str = ""  # Japanese translation HTML
    raw_md_ja: str = ""  # Japanese translation markdown


@dataclass
class DiaryEntry:
    date: str
    sections: list[DiarySection] = field(default_factory=list)
    recap_ja: str = ""
    recap_en: str = ""

    @property
    def has_content(self) -> bool:
        return bool(self.sections)

    def to_html(self) -> str:
        rendered = []

        # Add Recap section if available
        if self.recap_ja or self.recap_en:
            rendered.append(f"""
        <div class="section-recap">
            <div class="lang-content" data-lang="ja">
                <p class="recap-text">「{self.recap_ja}」</p>
            </div>
            <div class="lang-content" data-lang="en">
                <p class="recap-text">"{self.recap_en}"</p>
            </div>
        </div>""")

        for section in self.sections:
            rendered.append(
                SECTION_TEMPLATE.substitute(
                    css_class=section.css_class,
                    icon=section.icon,
                    title=section.title,
                    body_ja=section.body_html_ja or "<p><em>翻訳はまだないよ</em></p>",
                    body_en=section.body_html,
                )
            )
        return ENTRY_TEMPLATE.substitute(
            date=self.date,
            sections="\n".join(rendered),
        )

    def to_card_html(self) -> str:
        # Build preview: EN = original, JA = translated
        preview_en = ""
        preview_ja = ""
        for section in self.sections:
            if not preview_en:
                preview_en = extract_preview(section.raw_md)
            if not preview_ja and section.raw_md_ja:
                preview_ja = extract_preview(section.raw_md_ja)

        if not preview_ja:
            preview_ja = preview_en

        # Build source icons
        source_icons = []
        for section in self.sections:
            if section.css_class == "memory":
                source_icons.append("\U0001f9e0")
            elif section.css_class == "obsidian":
                source_icons.append("\U0001f4dd")
        sources = " ".join(source_icons)

        return CARD_TEMPLATE.substitute(
            date=self.date,
            emoji="\U0001f4c5",
            preview_ja=preview_ja,
            preview_en=preview_en,
            sources=sources,
        )


def extract_preview(md_text: str, max_length: int = 120) -> str:
    """Extract the first meaningful line of text from markdown for card preview."""
    for line in md_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        # Skip headings
        if stripped.startswith("#"):
            continue
        # Skip horizontal rules
        if re.match(r"^[-*_]{3,}$", stripped):
            continue
        # Clean list prefix
        cleaned = re.sub(r"^[-*]\s+", "", stripped)
        cleaned = re.sub(r"^\d+\.\s+", "", cleaned)
        # Strip markdown formatting
        cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"\*(.+?)\*", r"\1", cleaned)
        cleaned = re.sub(r"`(.+?)`", r"\1", cleaned)
        cleaned = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", cleaned)
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
        return cleaned
    return ""


# ─── Markdown → HTML Converter ──────────────────────────────────────────────

class MarkdownConverter:
    """Converts a subset of Markdown to HTML suitable for diary entries.

    Handles: headings (##–####), unordered lists, ordered lists,
    bold/italic inline formatting, inline code, links, and tables.
    """

    def convert(self, text: str) -> str:
        lines = text.split("\n")
        output: list[str] = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Skip top-level heading (title)
            if line.startswith("# ") and not line.startswith("## "):
                i += 1
                continue

            # Blank lines
            if not line.strip():
                i += 1
                continue

            # Headings ##..####
            heading_match = re.match(r"^(#{2,4})\s+(.+)$", line)
            if heading_match:
                level = len(heading_match.group(1))
                tag = f"h{min(level + 1, 6)}"  # ## → h3, ### → h4, #### → h5
                content = self._inline(heading_match.group(2))
                output.append(f"<{tag}>{content}</{tag}>")
                i += 1
                continue

            # Unordered list block
            if line.startswith("- "):
                items, i = self._collect_list(lines, i, prefix="- ")
                output.append("<ul>")
                for item in items:
                    output.append(f"  <li>{self._inline(item)}</li>")
                output.append("</ul>")
                continue

            # Ordered list block
            ol_match = re.match(r"^\d+\.\s+(.+)$", line)
            if ol_match:
                items, i = self._collect_ordered_list(lines, i)
                output.append("<ol>")
                for item in items:
                    output.append(f"  <li>{self._inline(item)}</li>")
                output.append("</ol>")
                continue

            # Table block
            if line.startswith("|"):
                table_html, i = self._convert_table(lines, i)
                output.append(table_html)
                continue

            # Regular paragraph
            output.append(f"<p>{self._inline(line)}</p>")
            i += 1

        return "\n".join(output)

    # ── List collectors ──

    @staticmethod
    def _collect_list(
        lines: list[str], start: int, *, prefix: str
    ) -> tuple[list[str], int]:
        items: list[str] = []
        i = start
        while i < len(lines):
            line = lines[i]
            if line.startswith(prefix):
                items.append(line[len(prefix):])
            elif line.startswith("  ") and items:
                # Continuation line (indented under previous item)
                items[-1] += " " + line.strip()
            else:
                break
            i += 1
        return items, i

    @staticmethod
    def _collect_ordered_list(
        lines: list[str], start: int
    ) -> tuple[list[str], int]:
        items: list[str] = []
        i = start
        while i < len(lines):
            line = lines[i]
            m = re.match(r"^\d+\.\s+(.+)$", line)
            if m:
                items.append(m.group(1))
            elif line.startswith("  ") and items:
                items[-1] += " " + line.strip()
            else:
                break
            i += 1
        return items, i

    # ── Table converter ──

    def _convert_table(self, lines: list[str], start: int) -> tuple[str, int]:
        rows: list[list[str]] = []
        i = start
        while i < len(lines) and lines[i].startswith("|"):
            line = lines[i]
            # Skip separator rows (|---|---|)
            if re.match(r"^\|[\s\-:|]+\|$", line):
                i += 1
                continue
            cells = [c.strip() for c in line.split("|") if c.strip()]
            rows.append(cells)
            i += 1

        if not rows:
            return ("", i)

        parts = ['<table class="diary-table">']

        # First row as header
        parts.append("  <thead><tr>")
        for cell in rows[0]:
            parts.append(f"    <th>{self._inline(cell)}</th>")
        parts.append("  </tr></thead>")

        # Remaining rows as body
        if len(rows) > 1:
            parts.append("  <tbody>")
            for row in rows[1:]:
                parts.append("  <tr>")
                for cell in row:
                    parts.append(f"    <td>{self._inline(cell)}</td>")
                parts.append("  </tr>")
            parts.append("  </tbody>")

        parts.append("</table>")
        return ("\n".join(parts), i)

    # ── Inline formatting ──

    @staticmethod
    def _inline(text: str) -> str:
        # Bold: **text**
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        # Italic: *text* (but not inside bold markers)
        text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
        # Inline code: `text`
        text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
        # Links: [text](url)
        text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
        return text


# ─── Translation ─────────────────────────────────────────────────────────────

def _cache_path(date_str: str, source: str) -> Path:
    """Return the cache file path for a given date and source."""
    return TRANSLATION_CACHE_DIR / f"{date_str}_{source}.json"


def _load_cached_translation(
    date_str: str, source: str, md_hash: str,
    db_conn: Optional[sqlite3.Connection] = None,
) -> Optional[str]:
    """Load a cached translation if the source hash matches.

    Checks DB first (if available), then falls back to file cache.
    """
    # DB cache (primary)
    if db_conn is not None:
        from domain.diary import get_translation_cache
        cached = get_translation_cache(db_conn, date_str, source, md_hash)
        if cached is not None:
            log.debug("DB cache hit for %s_%s", date_str, source)
            return cached

    # File cache (fallback)
    path = _cache_path(date_str, source)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("hash") == md_hash:
            log.debug("File cache hit for %s_%s", date_str, source)
            translation = data.get("translation")
            # Backfill to DB if available
            if db_conn is not None and translation:
                from domain.diary import set_translation_cache
                set_translation_cache(db_conn, date_str, source, md_hash, translation)
                log.debug("Backfilled DB cache for %s_%s", date_str, source)
            return translation
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def _save_cached_translation(
    date_str: str, source: str, md_hash: str, translation: str,
    db_conn: Optional[sqlite3.Connection] = None,
) -> None:
    """Save a translation to cache (DB and/or file)."""
    # Save to DB (primary)
    if db_conn is not None:
        from domain.diary import set_translation_cache
        set_translation_cache(db_conn, date_str, source, md_hash, translation)
        log.debug("Saved translation to DB for %s_%s", date_str, source)

    # Also save to file (for backward compat during transition)
    TRANSLATION_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(date_str, source)
    data = {"hash": md_hash, "translation": translation}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    log.debug("Saved translation to file for %s_%s", date_str, source)


def translate_markdown(md_text: str) -> Optional[str]:
    """Translate markdown text to Japanese via OpenClaw Gateway."""
    payload = json.dumps({
        "model": TRANSLATION_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a translation machine. Your ONLY job is to translate English text to Japanese.\n"
                    "STRICT RULES:\n"
                    "1. Translate every sentence word-for-word. Do NOT summarize, shorten, or skip any content.\n"
                    "2. Do NOT add comments, opinions, reactions, or explanations. You are NOT a reviewer.\n"
                    "3. Do NOT change the meaning, tone, or structure of the original text.\n"
                    "4. Preserve ALL Markdown formatting EXACTLY (headings, lists, tables, bold, italic, code, links).\n"
                    "5. Keep proper nouns, technical terms, file paths, and code snippets in English.\n"
                    "6. Output ONLY the translated Markdown. No extra text.\n"
                    "\n"
                    "Example:\n"
                    "Input: '## Task\\n- Completed feature A\\n- Working on bug fix'\n"
                    "Output: '## タスク\\n- 機能Aを完了\\n- バグ修正に取り組み中'\n"
                    "\n"
                    "Now translate the following document:"
                ),
            },
            {"role": "user", "content": md_text},
        ],
        "temperature": 0.3,
    }).encode("utf-8")

    url, token = _gateway_url_and_token()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError, OSError) as e:
        log.warning("Translation failed: %s", e)
        return None


def get_translation(
    date_str: str, source: str, md_text: str,
    db_conn: Optional[sqlite3.Connection] = None,
) -> Optional[str]:
    """Get Japanese translation of markdown, using cache when possible."""
    md_hash = hashlib.sha256(md_text.encode("utf-8")).hexdigest()

    # Check cache (DB first, then file)
    cached = _load_cached_translation(date_str, source, md_hash, db_conn=db_conn)
    if cached is not None:
        return cached

    # Translate
    log.info("Translating %s_%s ...", date_str, source)
    translated = translate_markdown(md_text)
    if translated:
        _save_cached_translation(date_str, source, md_hash, translated, db_conn=db_conn)
    return translated


def get_recap(
    date_str: str, content: str,
    db_conn: Optional[sqlite3.Connection] = None,
) -> tuple[str, str]:
    """Generate or load a cached recap for the day."""
    md_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    # Check DB cache first
    if db_conn is not None:
        from domain.diary import get_recap_cache
        cached = get_recap_cache(db_conn, date_str, md_hash)
        if cached is not None:
            log.debug("DB recap cache hit for %s", date_str)
            return cached

    # Check file cache (fallback)
    RECAP_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = RECAP_CACHE_DIR / f"{date_str}.json"

    if cache_path.is_file():
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            if data.get("hash") == md_hash:
                ja, en = data.get("ja", ""), data.get("en", "")
                # Backfill to DB
                if db_conn is not None and ja and en:
                    from domain.diary import set_recap_cache
                    set_recap_cache(db_conn, date_str, md_hash, ja, en)
                return ja, en
        except Exception:
            pass

    log.info("Generating Rebecca Recap for %s ...", date_str)

    payload = json.dumps({
        "model": TRANSLATION_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Rebecca from Cyberpunk: Edgerunners. "
                    "Write a very short (max 2 sentences) commentary on the following day's activity. "
                    "Be sassy, sharp-tongued, but loyal to Takeru. Use oversized emotions. "
                    "Output format: JSON with keys 'ja' and 'en'. "
                    "Example: {'ja': '今日は散々だったけど、次はぶちかましてやろうぜ！', 'en': 'Rough day, but let's blast them next time!'}"
                ),
            },
            {"role": "user", "content": content},
        ],
        "temperature": 0.8,
        "response_format": {"type": "json_object"}
    }).encode("utf-8")

    url, token = _gateway_url_and_token()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            res_content = result["choices"][0]["message"]["content"]
            res_json = json.loads(res_content)
            ja, en = res_json.get("ja", ""), res_json.get("en", "")
            if ja and en:
                # Save to file (backward compat)
                cache_path.write_text(json.dumps({"hash": md_hash, "ja": ja, "en": en}, ensure_ascii=False), encoding="utf-8")
                # Save to DB
                if db_conn is not None:
                    from domain.diary import set_recap_cache
                    set_recap_cache(db_conn, date_str, md_hash, ja, en)
                return ja, en
    except Exception as e:
        log.warning("Recap generation failed: %s", e)

    return "", ""


# ─── Core Logic ──────────────────────────────────────────────────────────────

def scan_dates(memory_dir: Path, obsidian_dir: Path) -> list[str]:
    """Find all unique YYYY-MM-DD dates from filenames in both directories."""
    dates = set()
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")

    for d in [memory_dir, obsidian_dir]:
        if not d.is_dir():
            log.warning("Directory not found: %s", d)
            continue
        for f in d.glob("*.md"):
            m = pattern.match(f.name)
            if m:
                dates.add(m.group(1))

    return sorted(list(dates), reverse=True)


def read_source(path: Path) -> Optional[str]:
    """Read a markdown file, returning None if it doesn't exist."""
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def build_entry(
    date_str: str,
    memory_dir: Path,
    obsidian_dir: Path,
    *,
    skip_translation: bool = False,
    db_conn: Optional[sqlite3.Connection] = None,
) -> Optional[DiaryEntry]:
    """Build a DiaryEntry for a specific date by integrating memory and obsidian."""
    converter = MarkdownConverter()
    entry = DiaryEntry(date=date_str)

    memory_md = read_source(memory_dir / f"{date_str}.md")
    obsidian_md = read_source(obsidian_dir / f"{date_str}.md")

    if not memory_md and not obsidian_md:
        return None

    # Integrate the two sources
    integrated_md = merge_markdown_sources(memory_md, obsidian_md)
    html_en = converter.convert(integrated_md)

    if not html_en.strip():
        return None

    # Translation (EN→JA)
    html_ja = ""
    raw_md_ja = ""
    if not skip_translation:
        # Use 'integrated' as the cache source key
        translated_md = get_translation(date_str, "integrated", integrated_md, db_conn=db_conn)
        if translated_md:
            raw_md_ja = translated_md
            html_ja = converter.convert(translated_md)

    # We use a single section for the integrated view
    entry.sections.append(
        DiarySection(
            title="Rebecca's Integrated Log",
            icon="\U0001f5d2",
            css_class="integrated",
            body_html=html_en,
            raw_md=integrated_md,
            body_html_ja=html_ja,
            raw_md_ja=raw_md_ja,
        )
    )

    # Generate recap
    if not skip_translation:
        recap_ja, recap_en = get_recap(date_str, integrated_md, db_conn=db_conn)
        entry.recap_ja = recap_ja
        entry.recap_en = recap_en

    log.debug("Integrated entry for %s", date_str)

    # Save to DB if connection available
    if db_conn is not None:
        _save_entry_to_db(
            db_conn,
            date_str=date_str,
            memory_md=memory_md,
            obsidian_md=obsidian_md,
            integrated_md=integrated_md,
            html_en=html_en,
            html_ja=html_ja,
            raw_md_ja=raw_md_ja,
            recap_en=entry.recap_en,
            recap_ja=entry.recap_ja,
            preview_en=extract_preview(integrated_md),
            preview_ja=extract_preview(raw_md_ja) if raw_md_ja else "",
        )

    return entry


def _save_entry_to_db(
    db_conn: sqlite3.Connection,
    *,
    date_str: str,
    memory_md: Optional[str],
    obsidian_md: Optional[str],
    integrated_md: str,
    html_en: str,
    html_ja: str,
    raw_md_ja: str,
    recap_en: str,
    recap_ja: str,
    preview_en: str,
    preview_ja: str,
) -> None:
    """Save a built entry to the database."""
    from domain.diary import upsert_entry
    integrated_hash = hashlib.sha256(integrated_md.encode("utf-8")).hexdigest()
    upsert_entry(
        db_conn,
        date=date_str,
        memory_md=memory_md,
        obsidian_md=obsidian_md,
        integrated_md=integrated_md,
        integrated_hash=integrated_hash,
        html_en=html_en,
        html_ja=html_ja or None,
        raw_md_ja=raw_md_ja or None,
        recap_en=recap_en,
        recap_ja=recap_ja,
        preview_en=preview_en,
        preview_ja=preview_ja,
    )
    log.debug("Saved entry %s to DB", date_str)


def _entry_from_db_row(row: dict) -> DiaryEntry:
    """Reconstruct a DiaryEntry from a database row."""
    entry = DiaryEntry(date=row["date"])
    entry.recap_ja = row.get("recap_ja") or ""
    entry.recap_en = row.get("recap_en") or ""
    entry.sections.append(
        DiarySection(
            title="Rebecca's Integrated Log",
            icon="\U0001f5d2",
            css_class="integrated",
            body_html=row["html_en"],
            raw_md=row["integrated_md"],
            body_html_ja=row.get("html_ja") or "",
            raw_md_ja=row.get("raw_md_ja") or "",
        )
    )
    return entry


# ─── Site Generation ─────────────────────────────────────────────────────────


def _render_html(
    template_path: Path,
    output_path: Path,
    entries: list[DiaryEntry],
    dry_run: bool = False,
) -> bool:
    """Render diary entries into the HTML template."""
    if not template_path.is_file():
        log.error("Template not found: %s", template_path)
        return False

    entries_html = []
    cards_html = []
    for entry in entries:
        if entry.has_content:
            entries_html.append(entry.to_html())
            cards_html.append(entry.to_card_html())

    if not entries_html:
        log.warning("No diary entries found to generate.")

    template_content = template_path.read_text(encoding="utf-8")

    if CARDS_PLACEHOLDER not in template_content:
        log.error("Placeholder '%s' not found in template.", CARDS_PLACEHOLDER)
        return False
    if ENTRIES_PLACEHOLDER not in template_content:
        log.error("Placeholder '%s' not found in template.", ENTRIES_PLACEHOLDER)
        return False

    final_html = template_content.replace(CARDS_PLACEHOLDER, "\n\n".join(cards_html))
    final_html = final_html.replace(ENTRIES_PLACEHOLDER, "\n\n".join(entries_html))

    if dry_run:
        print(final_html)
        return True

    output_path.write_text(final_html, encoding="utf-8")
    log.info("Generated site at %s with %d entries.", output_path, len(entries_html))
    return True


def generate_site(config: dict, dry_run: bool = False, skip_translation: bool = False) -> bool:
    """Generate the full website by scanning all dates (legacy mode, no DB)."""
    memory_dir = config["memory_dir"]
    obsidian_dir = config["obsidian_dir"]
    template_path = config["template_html"]
    output_path = config["index_html"]

    if not template_path.is_file():
        log.error("Template not found: %s", template_path)
        return False

    dates = scan_dates(memory_dir, obsidian_dir)
    log.info("Found %d unique dates to process.", len(dates))

    entries = []
    for d in dates:
        entry = build_entry(d, memory_dir, obsidian_dir, skip_translation=skip_translation)
        if entry:
            entries.append(entry)

    return _render_html(template_path, output_path, entries, dry_run=dry_run)


def generate_site_with_db(
    config: dict,
    db_conn: sqlite3.Connection,
    *,
    rebuild: bool = False,
    dry_run: bool = False,
    skip_translation: bool = False,
) -> bool:
    """Generate the website using the diary database.

    Default: process today only → save to DB → read all from DB → render HTML
    --rebuild: process all dates → save to DB → read all from DB → render HTML
    """
    from domain.diary import get_all_entries, count_entries

    memory_dir = config["memory_dir"]
    obsidian_dir = config["obsidian_dir"]
    template_path = config["template_html"]
    output_path = config["index_html"]

    if not template_path.is_file():
        log.error("Template not found: %s", template_path)
        return False

    # Step 1: Determine which dates to process
    if rebuild:
        dates_to_process = scan_dates(memory_dir, obsidian_dir)
        log.info("Rebuild mode: processing %d dates.", len(dates_to_process))
    else:
        today_str = date.today().isoformat()
        dates_to_process = [today_str]
        log.info("Default mode: processing today (%s) only.", today_str)

    # Step 2: Build and save entries for target dates
    processed = 0
    for d in dates_to_process:
        entry = build_entry(
            d, memory_dir, obsidian_dir,
            skip_translation=skip_translation,
            db_conn=db_conn,
        )
        if entry:
            processed += 1

    log.info("Processed %d entries (saved to DB).", processed)

    # Step 3: Read ALL entries from DB and generate HTML
    db_rows = get_all_entries(db_conn, order="DESC")
    log.info("Reading %d entries from DB for HTML generation.", len(db_rows))

    entries = [_entry_from_db_row(row) for row in db_rows]

    return _render_html(template_path, output_path, entries, dry_run=dry_run)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebecca's Diary SSG - SQLite-backed diary generator.",
    )
    parser.add_argument(
        "--memory-dir",
        type=Path,
        default=DEFAULT_CONFIG["memory_dir"],
        help="Path to OpenClaw memory directory.",
    )
    parser.add_argument(
        "--obsidian-dir",
        type=Path,
        default=DEFAULT_CONFIG["obsidian_dir"],
        help="Path to Obsidian vault directory.",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_CONFIG["template_html"],
        help="Path to HTML template.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_CONFIG["index_html"],
        help="Path to output HTML file.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help="Path to diary SQLite database.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild: process all dates from source files into DB.",
    )
    parser.add_argument(
        "--migrate-cache",
        action="store_true",
        help="Migrate file-based translation/recap caches to DB.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated HTML to stdout instead of writing file.",
    )
    parser.add_argument(
        "--skip-translation",
        action="store_true",
        help="Skip AI translation (dev/test mode).",
    )
    parser.add_argument(
        "--no-db",
        action="store_true",
        help="Legacy mode: skip DB, process all dates like pre-Phase 3.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    setup_logging(verbose=args.verbose)

    config = {
        "memory_dir": args.memory_dir,
        "obsidian_dir": args.obsidian_dir,
        "template_html": args.template,
        "index_html": args.output,
    }

    # Legacy mode (no DB)
    if args.no_db:
        log.info("Running in legacy mode (no DB).")
        success = generate_site(config, dry_run=args.dry_run, skip_translation=args.skip_translation)
        return 0 if success else 1

    # Phase 3: DB mode
    from domain.diary import init_db, migrate_file_caches

    db_conn = init_db(args.db)
    log.info("Database initialized at %s", args.db)

    try:
        # Migrate caches if requested
        if args.migrate_cache:
            log.info("Migrating file-based caches to DB...")
            stats = migrate_file_caches(db_conn, TRANSLATION_CACHE_DIR, RECAP_CACHE_DIR)
            log.info(
                "Migration complete: %d translations, %d recaps, %d skipped.",
                stats["translations"], stats["recaps"], stats["skipped"],
            )

        # Generate site
        success = generate_site_with_db(
            config,
            db_conn,
            rebuild=args.rebuild,
            dry_run=args.dry_run,
            skip_translation=args.skip_translation,
        )
    finally:
        db_conn.close()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
