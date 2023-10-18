import unittest
from src.location import Location


class TestLocation(unittest.TestCase):

    def setUp(self):
        # Initialize Location instance for testing
        self.location = Location(description="Test Location", length=5, width=5, occupied=[(1, 1, 'G'), (2, 2, 'O')])

    def test_move(self):
        self.location.move('down')
        self.assertEqual(self.location.player_location, (1, 0))
        self.location.move('right')
        # occupied space
        self.assertEqual(self.location.player_location, (1, 0))
        self.location.move('down-right')
        self.assertEqual(self.location.player_location, (2, 1))
        self.location.move('up-left')
        # can't move
        self.location.move('up-left')
        self.assertEqual(self.location.player_location, (1, 0))
        # ?
        self.location.move('blah')
        self.assertEqual(self.location.player_location, (1, 0))

    def test_move_player(self):
        target_coords = (1, 2)
        new_location = self.location.move_player(3, target_coords)
        self.assertEqual(new_location, target_coords)


    def test_cant_move_player(self):
        target_coords = (2, 2)
        new_location = self.location.move_player(3, target_coords)
        self.assertEqual(new_location, (0, 0))


    def test_move_object(self):
        starting_coords = (1, 1)
        target_coords = (3, 3)
        result = self.location.move_object(4, starting_coords, target_coords)
        self.assertTrue(result)
        self.assertEqual(self.location.occupied, [(3, 3, 'G'), (2, 2, 'O')])

        # Add more test cases for move_object method

    def test_get_valid_neighbors(self):
        neighbors = self.location.get_valid_neighbors(1, 1)
        self.assertEqual(neighbors, [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)])

        # Add more test cases for get_valid_neighbors method

    def test_update_object_char(self):
        self.location.update_object_char(1, 1, 'X')
        self.assertEqual(self.location.occupied, [(1, 1, 'X'), (2, 2, 'O')])

