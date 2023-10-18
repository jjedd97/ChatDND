import unittest

from src.dice_roller import roll_dice, get_modifier


class TestDiceRolling(unittest.TestCase):

    def test_roll_dice(self):
        assert 1 <= roll_dice('2d4 + 2 + 1') <= 11

    def test_get_modifier(self):
        self.assertEqual(get_modifier(10), 0)
        self.assertEqual(get_modifier(16), 3)
        self.assertEqual(get_modifier(30), 10)

    def test_invalid_score_for_get_modifier(self):
        with self.assertRaises(ValueError):
            get_modifier(31)
        with self.assertRaises(ValueError):
            get_modifier(-1)
