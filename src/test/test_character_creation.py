import unittest
from io import StringIO
from unittest.mock import patch

from src.create_character import roll_stats, point_buy


class TestCharacterCreation(unittest.TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['1 2 3 4 5 6'])
    @patch('random.randint', return_value=6)
    def test_valid_input(self, mock_rand, mock_input, mock_out):
        assigned_stats = roll_stats()
        self.assertEqual(assigned_stats, [18, 18, 18, 18, 18, 18])

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['6 2 3 4 5 1'])
    @patch('random.randint',
           side_effect=[1, 1, 1, 1, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6])
    def test_swap_input(self, mock_rand, mock_input, mock_out):
        assigned_stats = roll_stats()
        self.assertEqual(assigned_stats, [18, 18, 18, 18, 18, 3])

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['1 2 3 4 5'])  # Invalid input (not enough selections)
    @patch('random.randint', return_value=6)
    def test_invalid_input_too_few_selections(self, mock_rand, mock_input, mock_stdout):
        expected_output = "Invalid selection. Please enter six valid numbers (1-6).\n"
        assigned_stats = roll_stats()
        assert expected_output in mock_stdout.getvalue()
        self.assertIsNone(assigned_stats)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['1 2 3 4 5 7'])  # Invalid input (out of range selection)
    def test_invalid_input_out_of_range(self, mock_input, mock_stdout):
        expected_output = "Invalid selection. Please enter six valid numbers (1-6).\n"
        assigned_stats = roll_stats()
        assert expected_output in mock_stdout.getvalue()
        self.assertIsNone(assigned_stats)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['a b c d e f'])  # Invalid input (non-numeric)
    def test_invalid_input_non_numeric(self, mock_input, mock_stdout):
        expected_output = "Invalid input. Please enter six valid numbers (1-6).\n"
        assigned_stats = roll_stats()
        assert expected_output in mock_stdout.getvalue()
        self.assertIsNone(assigned_stats)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['1 2 1 3 4 5'])  # Invalid input (non-numeric)
    def test_double_up(self, mock_input, mock_stdout):
        expected_output = "Invalid"
        assigned_stats = roll_stats()
        assert expected_output in mock_stdout.getvalue()
        self.assertIsNone(assigned_stats)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['7 1', '5 2', '5 3', '5 4', '3 5'])
    def test_valid_input(self, mock_input, mock_stdout):
        assigned_stats = point_buy()
        self.assertEqual(assigned_stats, [15, 13, 13, 13, 11, 8])

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['7 1', '5 2', '5 3', '5 4', '8 5', '3 6'])
    def test_invalid_buy_input(self, mock_input, mock_stdout):
        assigned_stats = point_buy()
        self.assertEqual(assigned_stats, [15, 13, 13, 13, 8, 11])

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['-1 1', '6 2', '6 3', '6 4', '5 5', "1 1"])
    def test_neg_buy_input(self, mock_input, mock_stdout):
        assigned_stats = point_buy()
        self.assertEqual(assigned_stats, [9, 14, 14, 14, 13, 8])

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['7 1', '-7 1', '7 1', '5 2', '5 3', '5 4', '8 5', '3 6'])
    def test_neg_buy_back(self, mock_input, mock_stdout):
        assigned_stats = point_buy()
        self.assertEqual(assigned_stats, [15, 13, 13, 13, 8, 11])