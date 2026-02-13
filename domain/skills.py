"""
domain/skills.py - Skill level calculation (pure functions).

Extracted from collectors/collect_skills.py (Phase 2A).
All labels come from domain.constants.
No I/O, no subprocess, no file access.
"""

from domain.constants import SKILL_LEVEL_LABELS


def calculate_level(sub_skill_count, has_commands, has_agents, has_hooks):
    """
    Calculate skill level based on installed components.

    Args:
        sub_skill_count: int - number of sub-skills
        has_commands: bool - whether plugin has commands
        has_agents: bool - whether plugin has agents
        has_hooks: bool - whether plugin has hooks

    Returns:
        int - skill level (1-10)
    """
    level = 1

    if sub_skill_count >= 5:
        level += 4
    elif sub_skill_count >= 3:
        level += 3
    elif sub_skill_count >= 1:
        level += 2

    if has_commands:
        level += 1
    if has_agents:
        level += 1
    if has_hooks:
        level += 1

    return min(level, 10)


def get_level_label(level):
    """
    Get Rebecca's label for a skill level.

    Args:
        level: int - skill level

    Returns:
        str - Japanese label for the level
    """
    if level in SKILL_LEVEL_LABELS:
        return SKILL_LEVEL_LABELS[level]
    if level > 10:
        return "マスター"
    return "覚えたて"
