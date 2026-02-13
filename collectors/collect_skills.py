#!/usr/bin/env python3
"""
collect_skills.py - Claude Plugin/Skill collector for Rebecca's Room

Scans ~/.claude/plugins/marketplaces/claude-plugins-official/ to discover
installed plugins, skills, LSP languages, and external integrations.
Outputs structured data to src/data/skills.json.

Usage:
    python3 collectors/collect_skills.py        # normal run
    python3 collectors/collect_skills.py -v     # verbose/debug output

Dependencies: Python 3.9+ stdlib only (no pip packages)
Frequency: every 1 hour (cron)
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# -- Domain layer import --
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from domain.constants import SKILL_LEVEL_LABELS as _DOMAIN_SKILL_LEVEL_LABELS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

JST = timezone(timedelta(hours=9))

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "src" / "data"
OUTPUT_FILE = OUTPUT_DIR / "skills.json"

PLUGINS_BASE = Path.home() / ".claude" / "plugins" / "marketplaces" / "claude-plugins-official"
PLUGINS_DIR = PLUGINS_BASE / "plugins"
EXTERNAL_DIR = PLUGINS_BASE / "external_plugins"

VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv

# Plugins to skip (not real skills)
SKIP_PLUGINS = {"example-plugin"}

# Category mapping: plugin_id -> category
CATEGORY_MAP = {
    "plugin-dev": "development",
    "agent-sdk-dev": "development",
    "feature-dev": "development",
    "frontend-design": "design",
    "playground": "design",
    "hookify": "automation",
    "claude-code-setup": "automation",
    "code-review": "quality",
    "code-simplifier": "quality",
    "pr-review-toolkit": "quality",
    "claude-md-management": "quality",
    "security-guidance": "quality",
    "commit-commands": "git",
    "explanatory-output-style": "communication",
    "learning-output-style": "communication",
    "ralph-loop": "workflow",
}

# LSP plugin_id -> display name
LSP_NAMES = {
    "typescript-lsp": "TypeScript",
    "pyright-lsp": "Python",
    "rust-analyzer-lsp": "Rust",
    "gopls-lsp": "Go",
    "jdtls-lsp": "Java",
    "csharp-lsp": "C#",
    "kotlin-lsp": "Kotlin",
    "swift-lsp": "Swift",
    "lua-lsp": "Lua",
    "php-lsp": "PHP",
    "clangd-lsp": "C/C++",
}

# Skill level labels (from domain.constants)
LEVEL_LABELS = _DOMAIN_SKILL_LEVEL_LABELS


def log(msg):
    if VERBOSE:
        print(f"[skills] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# YAML frontmatter parser (minimal, stdlib only)
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """Parse YAML frontmatter from a Markdown file. Returns dict or empty dict."""
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    yaml_block = text[3:end].strip()
    result = {}
    for line in yaml_block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^(\w[\w-]*)\s*:\s*(.+)$", line)
        if match:
            key = match.group(1)
            val = match.group(2).strip().strip('"').strip("'")
            result[key] = val
    return result


# ---------------------------------------------------------------------------
# Plugin scanning
# ---------------------------------------------------------------------------

def read_plugin_json(plugin_dir):
    """Read .claude-plugin/plugin.json from a plugin directory."""
    pj = plugin_dir / ".claude-plugin" / "plugin.json"
    if not pj.exists():
        return None
    try:
        with open(pj, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        log(f"Failed to read {pj}: {e}")
        return None


def scan_skills(plugin_dir):
    """Scan skills/*/SKILL.md in a plugin directory. Returns list of sub-skill names."""
    skills_dir = plugin_dir / "skills"
    if not skills_dir.is_dir():
        return []
    sub_skills = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            try:
                text = skill_md.read_text(encoding="utf-8")
                fm = parse_frontmatter(text)
                name = fm.get("name", skill_dir.name)
                sub_skills.append(name)
                log(f"  Skill: {name} (from {skill_md})")
            except OSError as e:
                log(f"  Failed to read {skill_md}: {e}")
                sub_skills.append(skill_dir.name)
        else:
            sub_skills.append(skill_dir.name)
    return sub_skills


def scan_components(plugin_dir):
    """Count commands, agents, hooks in a plugin directory."""
    counts = {}
    for component in ("commands", "agents"):
        comp_dir = plugin_dir / component
        if comp_dir.is_dir():
            md_files = list(comp_dir.glob("*.md"))
            if md_files:
                counts[component] = len(md_files)
    hooks_json = plugin_dir / "hooks" / "hooks.json"
    if hooks_json.exists():
        counts["hooks"] = 1
    return counts


def calculate_level(sub_skill_count, has_commands, has_agents, has_hooks):
    """
    Calculate skill level. Phase 1: based on installed components.
    Future: usage frequency scoring.
    """
    # Base level: installed = 1
    level = 1

    # Sub-skills contribute heavily
    if sub_skill_count >= 5:
        level += 4
    elif sub_skill_count >= 3:
        level += 3
    elif sub_skill_count >= 1:
        level += 2

    # Commands add capability
    if has_commands:
        level += 1

    # Agents add sophistication
    if has_agents:
        level += 1

    # Hooks add automation depth
    if has_hooks:
        level += 1

    return min(level, 10)


def get_level_label(level):
    """Get Rebecca's label for a skill level."""
    if level in LEVEL_LABELS:
        return LEVEL_LABELS[level]
    if level > 10:
        return "マスター"
    return "覚えたて"


def scan_plugins():
    """Scan all plugins and return categorized results."""
    skills = []
    languages = []
    integrations = []

    # -- Official plugins --
    if PLUGINS_DIR.is_dir():
        for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
            if not plugin_dir.is_dir():
                continue
            plugin_id = plugin_dir.name
            if plugin_id in SKIP_PLUGINS:
                log(f"Skipping {plugin_id}")
                continue

            # LSP plugins
            if plugin_id.endswith("-lsp"):
                display_name = LSP_NAMES.get(plugin_id, plugin_id.replace("-lsp", "").title())
                languages.append({
                    "name": display_name,
                    "plugin_id": plugin_id,
                    "active": True,
                })
                log(f"LSP: {display_name} ({plugin_id})")
                continue

            # Standard plugins with metadata
            pj = read_plugin_json(plugin_dir)

            sub_skills = scan_skills(plugin_dir)
            components = scan_components(plugin_dir)

            # Skip plugins with no plugin.json AND no content
            if pj is None and not sub_skills and not components:
                log(f"No plugin.json and no content for {plugin_id}, skipping")
                continue

            category = CATEGORY_MAP.get(plugin_id, "other")

            # Derive display name from plugin.json or plugin_id
            display_name = plugin_id
            if pj:
                display_name = pj.get("name", plugin_id)
            # Clean up name: kebab-case -> Title Case
            if display_name == plugin_id:
                display_name = plugin_id.replace("-", " ").title()

            level = calculate_level(
                len(sub_skills),
                "commands" in components,
                "agents" in components,
                "hooks" in components,
            )

            skill_entry = {
                "name": display_name,
                "plugin_id": plugin_id,
                "category": category,
                "level": level,
                "sub_skills": sub_skills,
                "sub_skill_count": len(sub_skills),
                "label": get_level_label(level),
            }
            skills.append(skill_entry)
            log(f"Plugin: {display_name} (Lv.{level}, {len(sub_skills)} skills, cat={category})")
    else:
        log(f"Plugins directory not found: {PLUGINS_DIR}")

    # -- External plugins --
    if EXTERNAL_DIR.is_dir():
        for plugin_dir in sorted(EXTERNAL_DIR.iterdir()):
            if not plugin_dir.is_dir():
                continue
            plugin_id = plugin_dir.name
            pj = read_plugin_json(plugin_dir)
            display_name = plugin_id.title()
            if pj:
                display_name = pj.get("name", display_name)
                if display_name == plugin_id:
                    display_name = plugin_id.replace("-", " ").title()

            integrations.append({
                "name": display_name,
                "plugin_id": plugin_id,
                "type": "external",
            })
            log(f"External: {display_name} ({plugin_id})")
    else:
        log(f"External plugins directory not found: {EXTERNAL_DIR}")

    # Sort skills by level descending
    skills.sort(key=lambda s: s["level"], reverse=True)

    return skills, languages, integrations


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def build_output(skills, languages, integrations):
    """Build the final JSON output."""
    now = datetime.now(JST)

    total_plugins = len(skills) + len(languages) + len(integrations)
    with_skills = sum(1 for s in skills if s["sub_skill_count"] > 0)

    return {
        "timestamp": now.isoformat(timespec="seconds"),
        "summary": {
            "total_plugins": total_plugins,
            "with_skills": with_skills,
            "lsp_count": len(languages),
            "external_count": len(integrations),
        },
        "skills": skills,
        "languages": languages,
        "integrations": integrations,
    }


def write_json_atomic(data, output_path):
    """Atomic write: .tmp -> rename."""
    os.makedirs(output_path.parent, exist_ok=True)
    tmp_path = output_path.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.rename(tmp_path, output_path)
        log(f"Wrote {output_path}")
    except OSError as e:
        log(f"Failed to write {output_path}: {e}")
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log("Starting skill collection...")

    skills, languages, integrations = scan_plugins()
    data = build_output(skills, languages, integrations)
    write_json_atomic(data, OUTPUT_FILE)

    if VERBOSE:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        s = data["summary"]
        print(f"OK: plugins={s['total_plugins']}, "
              f"skills={s['with_skills']}, "
              f"lsp={s['lsp_count']}, "
              f"external={s['external_count']}, "
              f"timestamp={data['timestamp']}")


if __name__ == "__main__":
    main()
