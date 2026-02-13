"""Tests for domain/skills.py — skill level calculation."""

import unittest

from domain.skills import calculate_level, get_level_label
from domain.constants import SKILL_LEVEL_LABELS


class TestCalculateLevel(unittest.TestCase):
    """Test skill level calculation from components."""

    def test_base_level(self):
        """Plugin with no components = level 1."""
        self.assertEqual(calculate_level(0, False, False, False), 1)

    def test_one_sub_skill(self):
        """1 sub-skill adds 2 levels."""
        self.assertEqual(calculate_level(1, False, False, False), 3)

    def test_three_sub_skills(self):
        """3 sub-skills adds 3 levels."""
        self.assertEqual(calculate_level(3, False, False, False), 4)

    def test_five_sub_skills(self):
        """5+ sub-skills adds 4 levels."""
        self.assertEqual(calculate_level(5, False, False, False), 5)

    def test_ten_sub_skills(self):
        """10 sub-skills still adds 4 (same as 5+)."""
        self.assertEqual(calculate_level(10, False, False, False), 5)

    def test_commands_add_one(self):
        self.assertEqual(calculate_level(0, True, False, False), 2)

    def test_agents_add_one(self):
        self.assertEqual(calculate_level(0, False, True, False), 2)

    def test_hooks_add_one(self):
        self.assertEqual(calculate_level(0, False, False, True), 2)

    def test_all_components(self):
        """All components: 1 + 4 + 1 + 1 + 1 = 8."""
        self.assertEqual(calculate_level(5, True, True, True), 8)

    def test_maximum_level_capped_at_10(self):
        """Level should never exceed 10."""
        # 10 sub_skills=+4, commands=+1, agents=+1, hooks=+1 => 1+4+1+1+1=8
        self.assertEqual(calculate_level(10, True, True, True), 8)
        # Verify min(level, 10) capping
        self.assertLessEqual(calculate_level(100, True, True, True), 10)

    def test_exact_cap(self):
        """1 + 4 + 1 + 1 + 1 + ... still caps."""
        self.assertLessEqual(calculate_level(100, True, True, True), 10)


class TestGetLevelLabel(unittest.TestCase):
    """Test level label lookup."""

    def test_all_levels_1_to_10(self):
        for level in range(1, 11):
            label = get_level_label(level)
            self.assertEqual(label, SKILL_LEVEL_LABELS[level])

    def test_level_0_fallback(self):
        self.assertEqual(get_level_label(0), "覚えたて")

    def test_level_above_10(self):
        self.assertEqual(get_level_label(11), "マスター")

    def test_level_100(self):
        self.assertEqual(get_level_label(100), "マスター")

    def test_level_1_label(self):
        self.assertEqual(get_level_label(1), "覚えたて")

    def test_level_5_label(self):
        self.assertEqual(get_level_label(5), "手に馴染んできた")

    def test_level_10_label(self):
        self.assertEqual(get_level_label(10), "マスター")


if __name__ == "__main__":
    unittest.main()
