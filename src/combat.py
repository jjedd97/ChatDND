import math
from random import choice, randint
from re import sub
from time import sleep
from typing import Union

from src.dice_roller import roll_dice, get_modifier, roll_disadvantage, roll_d20
from src.location import Location, Direction
import sqlite3

# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect('db/dnd.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()


def find_and_remove_monster_cord(monster_char, occupied_spaces):
    for i in range(len(occupied_spaces)):
        if occupied_spaces[i][2] == monster_char:
            return occupied_spaces.pop(i)


def give_monsters_unique_char(monsters, location):
    occupied_spaces = location.occupied.copy()
    # Need a better solution here - won't scale
    taken_chars = ['p']
    int_val = 0
    for monster in monsters:
        if monster['char'] in taken_chars:
            while True:
                if str(int_val) in taken_chars:
                    int_val = int_val + 1
                else:
                    taken_chars.append(str(int_val))
                    monster["location"] = find_and_remove_monster_cord(monster["char"], occupied_spaces)
                    monster["char"] = str(int_val)
                    location.update_object_char(monster["location"][0], monster["location"][1], str(int_val))
                    monster["location"] = (monster["location"][0], monster["location"][1], monster["char"])
                    break
        else:
            taken_chars.append(monster['char'])
            monster["location"] = find_and_remove_monster_cord(monster["char"], occupied_spaces)


def determine_combat_order(monsters, init):
    sorted_data = sorted(monsters, key=lambda x: x['initiative'], reverse=True)
    found = False
    for i in range(len(sorted_data)):
        if sorted_data[i]["initiative"] < init:
            sorted_data.insert(i, {"char": "P", "monster_name": "player"})
            found = True
            break
    if not found:
        sorted_data.append({"char": "P", "monster_name": "player"})
    sorted_names = [item['monster_name'] for item in sorted_data]
    print(f"Combat order: {sorted_names}")
    map_names = [item['char'] for item in sorted_data]
    print(f"Map names: {map_names}")
    return map_names


def remove_trailing_numbers(input_string):
    return sub(r'\s\d+$', '', input_string)


def load_monsters_attacks(monsters):
    for monster in monsters:
        monster['monster_name'] = remove_trailing_numbers(monster['monster_name'])
        monster['attacks'] = {}
        cursor.execute("SELECT * FROM attacks WHERE monster_name = ?", (monster["monster_name"],))
        attacks = cursor.fetchall()
        for attack in attacks:
            monster['attacks'][attack[2]] = {'hit': attack[3], "damage_type": attack[4], "roll": attack[5],
                                             "max_targets": attack[6], "range": attack[7], "fullrange": attack[8]}
        # Get additonal monster_data
        cursor.execute("SELECT * FROM monsters WHERE name = ?", (monster["monster_name"],))
        details = cursor.fetchone()
        monster['hit_points'] = details[3]
        monster['armor_class'] = details[4]
        monster["resistances"] = details[6]
        monster["weakness"] = details[7]
        monster["speed"] = details[8]


def get_random_non_ranged_attack(monster):
    non_ranged_attacks = []
    for attack in monster["attacks"]:
        value = monster["attacks"][attack]
        if value["range"] is None:
            value["name"] = attack
            non_ranged_attacks.append(value)
    return choice(non_ranged_attacks)


def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def get_random_in_range_attack(monster, location):
    ranged_attacks = []
    dis_ranged_attacks = []
    type = "long"
    for attack in monster["attacks"]:
        value = monster["attacks"][attack]
        if value["range"] is not None:
            # TODO distance could be blocked
            distance = calculate_distance(monster["location"][0], monster["location"][1],
                                          location.player_location[0], location.player_location[1]) * 5
            if distance <= value["range"]:
                value["name"] = attack
                ranged_attacks.append(value)
            elif distance <= value["fullrange"]:
                value["name"] = attack
                dis_ranged_attacks.append(value)
    if not ranged_attacks:
        ranged_attacks = dis_ranged_attacks
        type = "long_disadvantage"
    if ranged_attacks:
        return choice(ranged_attacks), type
    else:
        return None, None


def attack_player(attack, attack_type, player):
    if attack_type == "long_disadvantage":
        hit = roll_disadvantage() + attack["hit"]
    else:
        hit = roll_d20() + attack["hit"]
    if hit >= player["ac"]:
        print(f"Attacked with {attack['name']}")
        damage = roll_dice(attack['roll'])
        print(f"Attacked for {damage}")
        player["health"] = player["health"] - damage
    else:
        print("Player dodged the attack!")


def give_player_ac(player):
    base = 10
    modifier = get_modifier(player["stats"]["dexterity"])
    player["ac"] = base + modifier


def player_can_hit_monster(weapon, monster, location) -> Union[str, None]:
    player_location = location.player_location
    monster_cords = (monster["location"][0], monster["location"][1])
    monster_neighbors = location.get_valid_neighbors(*monster_cords)
    if player_location in monster_neighbors and weapon["range"] is None:
        return "short"
    if (weapon["range"] and player_location not in monster_neighbors
            and calculate_distance(monster["location"][0],
                                   monster["location"][1],
                                   location.player_location[0],
                                   location.player_location[
                                       1]) * 5 <= weapon[
                "range"]):
        return "long"
    if (weapon["range"] and player_location not in monster_neighbors
            and calculate_distance(monster["location"][0],
                                   monster["location"][1],
                                   location.player_location[0],
                                   location.player_location[
                                       1]) * 5 <= weapon[
                "fullrange"]):
        return "long_disadvantage"
    return None


def get_user_action(actions):
    print("Available Actions:")
    for i, action in enumerate(actions):
        print(f"{i + 1}. {action}")

    try:
        choice = int(input("Enter the number of the action you want to perform: "))
        if 1 <= choice <= len(actions):
            chosen_action = actions[choice - 1]
            return chosen_action
        else:
            print("Invalid choice. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def select_monster_character(monsters):
    print("Available Monsters:")
    for i, monster in enumerate(monsters):
        print(f"{i + 1}. Character: {monster['char']}, Name: {monster['monster_name']}")

    try:
        choice = int(input("Enter the number of the monster you want to select: "))
        if 1 <= choice <= len(monsters):
            selected_char = monsters[choice - 1][0]['char']
            return selected_char, monsters[1]
        else:
            print("Invalid choice. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def switch_weapons(player, current_weapon):
    print(f"Available weapons: {player['weapons']}")
    while True:
        choice = input("Weapon name: ")
        if choice in player["weapons"]:
            return player["weapons"][choice]


def attack_monster(monster, attack_type, weapon, player):
    if attack_type == "long_disadvantage":
        hit = roll_disadvantage() + player["proficiency"] + get_modifier(player["stats"]["strength"])
    else:
        hit = roll_d20() + player["proficiency"] + get_modifier(player["stats"]["strength"])
    if hit >= monster["armor_class"]:
        attack_data = weapon["Damage"].split()
        dice = attack_data[0]
        damage_type = attack_data[1]
        # TODO finnesse
        damage = roll_dice(dice) + player["proficiency"] + get_modifier(player["stats"]["strength"])
        monster["hit_points"] = monster["hit_points"] - damage
        message = f"You hit the monster for {damage}."
        if monster["hit_points"] < 1:
            message = message + f" {monster['char']} falls"
        print(message)
    else:
        print("Attack missed")


def move_player(player, location):
    moves = player["speed"] / 5
    while moves > 0:
        move_input = input(
            f"Enter a direction {Direction.list()}  or coordinates (x y) to move(quit to stop): ").lower()
        if move_input in Direction.list():
            location.move(move_input)
            moves = moves - 1
        elif move_input == "quit":
            break
        else:
            try:
                x, y = map(int, move_input.split())
                result_cords = location.move_player(moves, (x, y))
                if result_cords == (x, y):
                    break
            except ValueError:
                print("Invalid input. Please try again.")


def displayer_stats(player, current_weapon):
    print(f"{player['name']} has {player['health']}/{player['max_health']} health, \n weapon stats: {current_weapon}")


def combat(location: Location, monsters: list, init: int, player: dict) -> dict:
    """Handles the combat part of this dnd game"""
    give_monsters_unique_char(monsters, location)
    load_monsters_attacks(monsters)
    order = determine_combat_order(monsters, init)
    give_player_ac(player)
    combat_done = False
    turn = 1
    actions = ["move", "switch_weapon", "attack", "display_stats", "end_turn"]
    current_weapon = None
    while not combat_done:
        already_attacked = False
        print(f"{turn=}")
        location.print_grid()
        for creature in order:
            if creature == "P":
                if player["health"] <= 0:
                    combat_done = True
                    return player
                if len(order) == 1:
                    return player
                else:
                    if current_weapon is None:
                        current_weapon = switch_weapons(player, None)
                    while len(actions) > 2:
                        hittable_monsters = []
                        for monster in monsters:
                            result = player_can_hit_monster(current_weapon, monster, location)
                            if result:
                                hittable_monsters.append((monster, result))
                        if not hittable_monsters and "attack" in actions:
                            actions.remove("attack")
                        if hittable_monsters and not already_attacked and "attack" not in actions:
                            actions.append("attack")
                        chosen_action = get_user_action(actions)
                        if chosen_action is not None:
                            print(f"You have chosen to {chosen_action}.")
                        if chosen_action == "end_turn":
                            break
                        if chosen_action == "switch_weapon":
                            current_weapon = switch_weapons(player, current_weapon)
                            actions.remove("switch_weapon")
                        if chosen_action == "attack":
                            # TODO multiple targets
                            if len(hittable_monsters) > 1:
                                char, attack_type = select_monster_character(hittable_monsters)
                            else:
                                char, attack_type = hittable_monsters[0][0]["char"], hittable_monsters[0][1]
                            attacking = [x for x in hittable_monsters if x[0]["char"] == char][0]
                            attack_monster(attacking[0], attacking[1], current_weapon, player)
                            actions.remove("attack")
                            already_attacked = True
                        if chosen_action == "move":
                            actions.remove("move")
                            move_player(player, location)
                        if chosen_action == "display_stats":
                            displayer_stats(player, current_weapon)

            else:
                current_monster = [x for x in monsters if x["char"] == creature][0]
                if current_monster["hit_points"] > 0:
                    player_location = location.player_location
                    player_neighbors = location.get_valid_neighbors(*player_location)
                    monster_cords = (current_monster["location"][0], current_monster["location"][1])
                    close_attack = False
                    if monster_cords not in player_neighbors:
                        attack, attack_type = get_random_in_range_attack(current_monster, location)
                        if not attack:
                            for neighbor in player_neighbors:
                                if location.move_object(creature["speed"] / 5,
                                                        (creature["location"][0], current_monster["location"][1]),
                                                        neighbor):
                                    print(f"{creature} has approached you")
                                    current_monster["location"][0] = neighbor[0]
                                    current_monster["location"][1] = neighbor[1]
                                    close_attack = True
                    else:
                        close_attack = True

                    if close_attack:
                        attack = get_random_non_ranged_attack(current_monster)
                        attack_type = "close"

                    if attack:
                        print(f"{creature} is attacking")
                        sleep(1)
                        attack_player(attack, attack_type, player)
        # TODO remove the dead monsters
        alive_monsters = [monster for monster in monsters if "hit_points" not in monster or monster["hit_points"] > 0]
        dead_monsters = [monster for monster in monsters if monster not in alive_monsters]
        for monster in dead_monsters:
            if monster['char'] != 'P':
                order.remove(monster["char"])
                location.occupied.remove(monster['location'])
        monsters = alive_monsters
        turn = turn + 1
