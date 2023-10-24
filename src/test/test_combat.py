from src.combat import give_monsters_unique_char, determine_combat_order, player_can_hit_monster, \
    get_random_in_range_attack
from src.location import Location

class TestCombat:
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
