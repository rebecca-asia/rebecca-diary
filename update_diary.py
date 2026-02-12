#!/usr/bin/env python3
"""
update_diary.py — Rebecca's Diary SSG.

Scans memory and Obsidian directories for daily notes,
generates a full timeline HTML, and updates the website.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Optional

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_CONFIG = {
    "memory_dir": Path("/Users/rebeccacyber/.openclaw/workspace/memory"),
    "obsidian_dir": Path("/Users/rebeccacyber/Documents/Obsidian Vault"),
    "template_html": BASE_DIR / "src" / "template.html",
    "index_html": BASE_DIR / "src" / "index.html",
}

CARDS_PLACEHOLDER = "<!-- DIARY_CARDS_PLACEHOLDER -->"
ENTRIES_PLACEHOLDER = "<!-- DIARY_ENTRIES_PLACEHOLDER -->"

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
                <img src="assets/rebecca/レベッカ_顔絵ニュートラル.png" alt="" class="entry-avatar">
                <div class="entry-date">$date</div>
            </div>
            <div class="entry-content">
$sections
            </div>
        </article>""")

CARD_TEMPLATE = Template("""\
            <a href="#diary-$date" class="diary-card">
                <div class="card-date">$emoji $date</div>
                <div class="card-preview">$preview</div>
                <div class="card-sources">$sources</div>
            </a>""")

SECTION_TEMPLATE = Template("""\
        <div class="section-$css_class">
            <h3>$icon $title</h3>
$body
        </div>""")


# ─── Data Structures ────────────────────────────────────────────────────────

@dataclass
class DiarySection:
    title: str
    icon: str
    css_class: str
    body_html: str
    raw_md: str = ""  # Original markdown for preview extraction


@dataclass
class DiaryEntry:
    date: str
    sections: list[DiarySection] = field(default_factory=list)

    @property
    def has_content(self) -> bool:
        return bool(self.sections)

    def to_html(self) -> str:
        rendered = []
        for section in self.sections:
            rendered.append(
                SECTION_TEMPLATE.substitute(
                    css_class=section.css_class,
                    icon=section.icon,
                    title=section.title,
                    body=section.body_html,
                )
            )
        return ENTRY_TEMPLATE.substitute(
            date=self.date,
            sections="\n".join(rendered),
        )

    def to_card_html(self) -> str:
        # Build preview from first meaningful markdown lines
        preview = ""
        for section in self.sections:
            preview = extract_preview(section.raw_md)
            if preview:
                break

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
            preview=preview,
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


def build_entry(date_str: str, memory_dir: Path, obsidian_dir: Path) -> Optional[DiaryEntry]:
    """Build a DiaryEntry for a specific date from both sources."""
    converter = MarkdownConverter()
    entry = DiaryEntry(date=date_str)

    sources = [
        (memory_dir / f"{date_str}.md", "Internal Memory (OpenClaw)", "\U0001f9e0", "memory"),
        (obsidian_dir / f"{date_str}.md", "Daily Report (Obsidian)", "\U0001f4dd", "obsidian"),
    ]

    has_content = False
    for path, title, icon, css_class in sources:
        raw = read_source(path)
        if raw is None:
            continue
        html = converter.convert(raw)
        if html.strip():
            entry.sections.append(
                DiarySection(title=title, icon=icon, css_class=css_class, body_html=html, raw_md=raw)
            )
            has_content = True
            log.debug("Loaded section '%s' from %s", title, path.name)

    return entry if has_content else None


def generate_site(config: dict, dry_run: bool = False) -> bool:
    """Generate the full website by scanning all dates."""
    memory_dir = config["memory_dir"]
    obsidian_dir = config["obsidian_dir"]
    template_path = config["template_html"]
    output_path = config["index_html"]

    if not template_path.is_file():
        log.error("Template not found: %s", template_path)
        return False

    dates = scan_dates(memory_dir, obsidian_dir)
    log.info("Found %d unique dates to process.", len(dates))

    entries_html = []
    cards_html = []
    for date in dates:
        entry = build_entry(date, memory_dir, obsidian_dir)
        if entry:
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
    log.info("Successfully generated site at %s with %d entries.", output_path, len(entries_html))
    return True


# ─── CLI ─────────────────────────────────────────────────────────────────────

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebecca's Diary SSG - Scans and generates full static site.",
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
        "--dry-run",
        action="store_true",
        help="Print generated HTML to stdout instead of writing file.",
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

    success = generate_site(config, dry_run=args.dry_run)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
