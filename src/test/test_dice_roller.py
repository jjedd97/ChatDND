import unittest
from io import StringIO
from unittest.mock import patch

import pytest

from src.dice_roller import roll_dice, get_modifier, roll_save


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

    @patch('sys.stdout', new_callable=StringIO)
    def test_successful_roll(self, mock_stdout):
        stats = {'strength': 16, 'dexterity': 14, 'constitution': 12, 'intelligence': 10, 'wisdom': 8, 'charisma': 6}
        roll = "1 strength"
        result = roll_save(roll, stats)

        self.assertTrue(result)

    @patch('sys.stdout', new_callable=StringIO)
    def test_successful_roll_long_str(self, mock_stdout):
        stats = {'strength': 16, 'dexterity': 14, 'constitution': 12, 'intelligence': 10, 'wisdom': 8, 'charisma': 6}
        roll = "Hello 1 Strength World"
        result = roll_save(roll, stats)

        self.assertTrue(result)

    @patch('sys.stdout', new_callable=StringIO)
    def test_failed_roll(self, mock_stdout):
        stats = {'strength': 1, 'dexterity': 14, 'constitution': 12, 'intelligence': 10, 'wisdom': 8, 'charisma': 6}
        roll = "30 strength"
        result = roll_save(roll, stats)

        self.assertFalse(result)

    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_stat(self, mock_stdout):
        stats = {'strength': 16, 'dexterity': 14, 'constitution': 12, 'intelligence': 10, 'wisdom': 8, 'charisma': 6}
        roll = "12 agility"  # 'agility' is not a valid stat
        with pytest.raises(KeyError):
            roll_save(roll, stats)

    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_roll_format(self, mock_stdout):
        stats = {'strength': 16, 'dexterity': 14, 'constitution': 12, 'intelligence': 10, 'wisdom': 8, 'charisma': 6}
        with pytest.raises(IndexError):
            roll = "12"  # Missing stat name
            roll_save(roll, stats)
