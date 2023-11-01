import math
from unittest.mock import MagicMock, patch

from src.combat import give_monsters_unique_char, determine_combat_order, player_can_hit_monster, \
    get_random_in_range_attack, find_and_remove_monster_cord, remove_trailing_numbers, calculate_distance, attack_player
from src.location import Location


class TestCombat:
    @patch('src.combat.roll_disadvantage', return_value=6)
    @patch('src.combat.roll_dice', return_value=8)
    @patch('src.combat.roll_d20', return_value=12)
    def test_attack_player(self, d20, dice_mock, dis_mock):
        # Test Case 1: Successful attack
        attack = {
            "name": "Bite",
            "hit": 5,
            "roll": "2d6",
            "damage_type": "piercing"
        }
        player = {
            "ac": 12,
            "resistances": [],
            "immunities": [],
            "health": 20
        }
        attack_player(attack, "normal", player)
        assert player["health"] == 12  # New health after attack

        # Test Case 2: Missed attack
        attack = {
            "name": "Bite",
            "hit": 5,
            "roll": "2d6",
            "damage_type": "piercing"
        }
        player = {
            "ac": 30,  # High AC makes the attack miss
            "resistances": [],
            "immunities": [],
            "health": 20
        }
        attack_player(attack, "normal", player)
        assert player["health"] == 20  # Health remains unchanged

        # Test Case 3: Player resists attack
        attack = {
            "name": "Bite",
            "hit": 5,
            "roll": "2d6",
            "damage_type": "piercing"
        }
        player = {
            "ac": 1,
            "resistances": ["piercing"],  # Player resists piercing damage
            "immunities": [],
            "health": 20
        }
        attack_player(attack, "normal", player)
        assert player["health"] == 16  # New health after attack (damage halved)

        # Test Case 4: Player is immune to attack
        attack = {
            "name": "Bite",
            "hit": 5,
            "roll": "2d6",
            "damage_type": "piercing"
        }
        player = {
            "ac": 1,
            "resistances": [],
            "immunities": ["piercing"],  # Player is immune to piercing damage
            "health": 20
        }
        attack_player(attack, "normal", player)
        assert player["health"] == 20  # Health remains unchanged

        # Test Case 5: Long disadvantage attack
        attack = {
            "name": "Bite",
            "hit": 5,
            "roll": "2d6",
            "damage_type": "piercing"
        }
        player = {
            "ac": 12,
            "resistances": [],
            "immunities": [],
            "health": 20
        }
        attack_player(attack, "long_disadvantage", player)
        dis_mock.assert_called()

    def test_calculate_distance(self):
        # Test Case 1: Points at the origin
        result = calculate_distance(0, 0, 0, 0)
        assert result == 0.0

        # Test Case 2: Points on the same axis
        result = calculate_distance(1, 0, 4, 0)
        assert result == 3.0

        # Test Case 3: Points with positive coordinates
        result = calculate_distance(3, 4, 6, 8)
        assert math.isclose(result, 5.0)

        # Test Case 4: Points with zero coordinates
        result = calculate_distance(0, 0, 5, 0)
        assert result == 5.0

        # Test Case 5: Points with zero coordinates (reversed)
        result = calculate_distance(5, 0, 0, 0)
        assert result == 5.0

    def test_remove_trailing_numbers(self):
        # Test Case 1: Input string ends with a single digit
        input_string = "Goblin 1"
        result = remove_trailing_numbers(input_string)
        assert result == "Goblin"

        # Test Case 2: Input string ends with multiple digits
        input_string = "Giant Spider 10"
        result = remove_trailing_numbers(input_string)
        assert result == "Giant Spider"

        # Test Case 3: Input string without trailing digits, no change expected
        input_string = "Dragon"
        result = remove_trailing_numbers(input_string)
        assert result == "Dragon"

        # Test Case 4: Input string with trailing numbers mixed with letters
        input_string = "Phoenix 25 Fire"
        result = remove_trailing_numbers(input_string)
        assert result == "Phoenix 25 Fire"

    def test_find_and_remove_monster_cord(self):
        # Test Case 1: Monster with 'G' character is found and removed
        monster_char = 'G'
        occupied_spaces = [(1, 2, 'G'), (2, 1, 'O'), (3, 3, 'M')]

        result = find_and_remove_monster_cord(monster_char, occupied_spaces)

        assert result == (1, 2, 'G')
        assert occupied_spaces == [(2, 1, 'O'), (3, 3, 'M')]

        # Test Case 2: Monster with 'O' character is found and removed
        monster_char = 'O'
        occupied_spaces = [(1, 2, 'G'), (2, 1, 'O'), (3, 3, 'M')]

        result = find_and_remove_monster_cord(monster_char, occupied_spaces)

        assert result == (2, 1, 'O')
        assert occupied_spaces == [(1, 2, 'G'), (3, 3, 'M')]

        # Test Case 3: Monster with character not in the list, no removal
        monster_char = 'X'
        occupied_spaces = [(1, 2, 'G'), (2, 1, 'O'), (3, 3, 'M')]

        result = find_and_remove_monster_cord(monster_char, occupied_spaces)

        assert result is None
        assert occupied_spaces == [(1, 2, 'G'), (2, 1, 'O'), (3, 3, 'M')]

    def test_give_monsters_unique_char(self):
        # Test Case 1: One monster with a unique char
        monsters = [{'char': 'G', 'initiative': 12, 'location': (1, 3, 'G'), 'monster_name': 'Goblin'}]
        location = Location(description='Test Location', length=5, width=5, occupied=[(1, 3, 'G')])

        give_monsters_unique_char(monsters, location)

        assert monsters == [{'char': 'G', 'initiative': 12, 'location': (1, 3, 'G'), 'monster_name': 'Goblin'}]

        # Test Case 2: Two monsters with the same char, should be assigned unique chars
        monsters = [{'char': 'G', 'initiative': 12, 'location': (1, 3, 'G'), 'monster_name': 'Goblin'},
                    {'char': 'G', 'initiative': 6, 'location': (2, 2, 'G'), 'monster_name': 'Goblin'}]
        location = Location(description='Test Location', length=5, width=5, occupied=[(1, 3, 'G'), (2, 2, 'G')])

        give_monsters_unique_char(monsters, location)

        assert monsters == [{'char': 'G', 'initiative': 12, 'location': (1, 3, 'G'), 'monster_name': 'Goblin'},
                            {'char': '0', 'initiative': 6, 'location': (2, 2, '0'), 'monster_name': 'Goblin'}]

    def test_determine_combat_order(self):
        # Test Case 1: Two monsters with different initiatives, player has higher initiative
        monsters = [{'char': 'G', 'initiative': 12, 'monster_name': 'Goblin'},
                    {'char': 'O', 'initiative': 8, 'monster_name': 'Orc'}]
        initiative = 15

        result = determine_combat_order(monsters, initiative)

        assert result == ['P', 'G', 'O']

        # Test Case 2: Two monsters with different initiatives, player has lower initiative
        monsters = [{'char': 'G', 'initiative': 12, 'monster_name': 'Goblin'},
                    {'char': 'O', 'initiative': 8, 'monster_name': 'Orc'}]
        initiative = 5

        result = determine_combat_order(monsters, initiative)

        assert result == ['G', 'O', 'P']

        # Test Case 3: Player has highest initiative
        monsters = [{'char': 'G', 'initiative': 8, 'monster_name': 'Goblin'},
                    {'char': 'O', 'initiative': 6, 'monster_name': 'Orc'}]
        initiative = 15

        result = determine_combat_order(monsters, initiative)

        assert result == ['P', 'G', 'O']

        # Test Case 4: Player has lowest initiative
        monsters = [{'char': 'G', 'initiative': 8, 'monster_name': 'Goblin'},
                    {'char': 'O', 'initiative': 6, 'monster_name': 'Orc'}]
        initiative = 3

        result = determine_combat_order(monsters, initiative)

        assert result == ['G', 'O', 'P']

        # Test Case 5: Only one monster
        monsters = [{'char': 'G', 'initiative': 8, 'monster_name': 'Goblin'}]
        initiative = 5

        result = determine_combat_order(monsters, initiative)

        assert result == ['G', 'P']

    def test_player_can_hit_monster(self):
        # Test Case 1: Player is in short range with a melee weapon
        weapon = {"range": None}
        monster = {"location": (1, 2, 'G')}
        location = Location("Test Location", 5, 5, [(1, 2, 'G')], (2, 1))

        result = player_can_hit_monster(weapon, monster, location)

        assert result == "short"

        # Test Case 2: Player is in short range with a ranged weapon
        weapon = {"range": 30}
        monster = {"location": (2, 2, 'M')}
        location = Location("Test Location", 5, 5, [(2, 2, 'M')], (2, 1))

        result = player_can_hit_monster(weapon, monster, location)

        assert result == None

        # Test Case 3: Player is in long range with a ranged weapon
        weapon = {"range": 30, "fullrange": 60}
        monster = {"location": (4, 4, 'M')}
        location = Location("Test Location", 5, 5, [(1, 2, 'G'), (2, 1, 'O'), (3, 3, 'M')], (2, 1))

        result = player_can_hit_monster(weapon, monster, location)

        assert result == "long"

        # Test Case 4: Player is in long range with a ranged weapon, but beyond full range
        weapon = {"range": 30, "fullrange": 60}
        monster = {"location": (6, 6, 'M')}
        location = Location("Test Location", 10, 10, [(7, 7, 'M')], (1, 1))

        result = player_can_hit_monster(weapon, monster, location)

        assert result == "long_disadvantage"

        # Test Case 5: Player is not in range
        weapon = {"range": 30, "fullrange": 40}
        monster = {"location": (10, 10, 'M')}
        location = Location("Test Location", 5, 5, [(10, 10, 'M')], (0, 0))

        result = player_can_hit_monster(weapon, monster, location)

        assert result is None

    def test_get_random_in_range_attack(self):
        # Test Case 1: Player is within range for a ranged attack
        monster = {
            "attacks": {
                "Fireball": {"range": 50, "fullrange": 100, "damage": "3d6"}
            },
            "location": (3, 3, 'M')
        }
        location = Location("Test Location", 5, 5, [(3, 3, 'M')], (2, 1))

        result, attack_type = get_random_in_range_attack(monster, location)

        assert result == {"range": 50, "fullrange": 100, "damage": "3d6", "name": "Fireball"}
        assert attack_type == "long"

        # Test Case 2: Player is within disadvantage range for ranged attack
        monster = {
            "attacks": {
                "Arrow Shower": {"range": 5, "fullrange": 100, "damage": "3d6"}
            },
            "location": (3, 3, 'M')
        }
        location = Location("Test Location", 5, 5, [(3, 3, 'M')], (1, 1))

        result, attack_type = get_random_in_range_attack(monster, location)

        assert result == {"range": 5, "fullrange": 100, "damage": "3d6", "name": "Arrow Shower"}
        assert attack_type == "long_disadvantage"

        # Test Case 3: Player is out of range for any ranged attacks
        monster = {
            "attacks": {
                "Fireball": {"range": 5, "fullrange": 10, "damage": "3d6"}
            },
            "location": (3, 3, 'M')
        }
        location = Location("Test Location", 5, 5, [(3, 3, 'M')], (1, 4))

        result, attack_type = get_random_in_range_attack(monster, location)

        assert result is None
        assert attack_type == None

        # Test Case 4: Player is within range for a ranged attack, but not disadvantage range
        monster = {
            "attacks": {
                "Fireball": {"range": 50, "fullrange": 100, "damage": "3d6"}
            },
            "location": (3, 3, 'M')
        }
        location = Location("Test Location", 5, 5, [(1, 2, 'G'), (2, 1, 'O'), (3, 3, 'M')], (2, 2))

        result, attack_type = get_random_in_range_attack(monster, location)

        assert result == {"range": 50, "fullrange": 100, "damage": "3d6", "name": "Fireball"}
        assert attack_type == "long"
