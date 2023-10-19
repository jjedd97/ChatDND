import json
import random
import re
import sqlite3
from time import sleep
from ordered_set import OrderedSet
from src.dice_roller import roll_dice, get_modifier

# Connect to the database
conn = sqlite3.connect('db/dnd.db')
cursor = conn.cursor()


def add_ability_modifier(stats: dict, race_name):
    cursor.execute("SELECT ability_score_modifiers FROM races WHERE name = ?", (race_name,))
    raw_data = cursor.fetchone()[0]
    modifiers = json.loads(raw_data)
    for key, value in modifiers.items():
        stats[key.lower()] = stats[key.lower()] + value


def get_starting_health(con: int, class_name):
    cursor.execute("SELECT hit_dice FROM classes WHERE name = ?", (class_name,))
    raw_data = cursor.fetchone()[0]
    return int(re.findall(r'\d+', raw_data)[0]) + get_modifier(con)


def offer_armor(class_name):
    # TODO
    return "light"


def load_db_character_dict(name):
    cursor.execute("SELECT * FROM characters WHERE name = ?", (name,))
    character_data = cursor.fetchone()
    character_dict = {
        "name": character_data[0],
        "race": character_data[1],
        "class": character_data[2],
        "age": character_data[3],
        "weight": character_data[4],
        "description": character_data[5],
        "gold": character_data[6],
        "max_health": character_data[7],
        "health": character_data[8],
        "level": character_data[9],
        "proficiency": character_data[10],
        "speed": 30,  # TODO
        "armor": character_data[11]
    }
    cursor.execute("SELECT * FROM initial_stats WHERE character_name = ?", (name,))
    stats_data = cursor.fetchone()
    stats = {
        "strength": stats_data[1],
        "dexterity": stats_data[2],
        "constitution": stats_data[3],
        "intelligence": stats_data[4],
        "wisdom": stats_data[5],
        "charisma": stats_data[6]
    }
    add_ability_modifier(stats, race_name=character_dict["race"])
    character_dict["stats"] = stats
    bag = {}
    cursor.execute(
        "SELECT items.* FROM character_bag INNER JOIN items ON character_bag.item_name = items.name WHERE character_bag.character_name = ?",
        (name,))
    items_in_bag = cursor.fetchall()
    for item in items_in_bag:
        bag[item[0]] = {"Item Type": item[1], "Description": item[2], "Weight": item[3], "Value": item[4],
                        "Max Uses": item[5]}
    character_dict["bag"] = bag
    weapons = {}
    cursor.execute(
        "SELECT weapons.* FROM character_weapon INNER JOIN weapons ON character_weapon.weapon_name = weapons.name WHERE "
        "character_weapon.character_name = ?",
        (name,))
    owned_weapons = cursor.fetchall()
    for weapon in owned_weapons:
        weapons[weapon[0]] = {"Type": weapon[1], "Damage": weapon[2], "Weight": weapon[3], "range": weapon[4],
                              "fullrange": weapon[5], "price": weapon[6], "finesse": weapon[7], "hands": weapon[8]}
    character_dict["weapons"] = weapons
    return character_dict


# Function to fetch available races and classes from the database
def get_available_races_classes():
    cursor.execute("SELECT name FROM races")
    available_races = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT name FROM classes")
    available_classes = [row[0] for row in cursor.fetchall()]

    return available_races, available_classes


def get_starting_gold(class_name):
    cursor.execute("SELECT starting_gold FROM classes WHERE name = ?", (class_name,))
    gold_str = [row[0] for row in cursor.fetchall()][0]
    gold_amount = roll_dice(gold_str)
    print(f"Starting gold: {gold_amount}")
    return gold_amount


def get_weapons_by_type(weapon_type):
    cursor.execute("SELECT * FROM weapons WHERE type LIKE ?", (f'%{weapon_type}%',))
    weapons = cursor.fetchall()
    return weapons


def select_weapons(weapons_list, num_selections):
    selected_weapons = []
    if num_selections > 1:
        print("Available Weapons:")
        for i, weapon in enumerate(weapons_list, 1):
            print(
                f"{i}. Name: {weapon[0]}, Type: {weapon[1]}, Damage: {weapon[2]}, Weight: {weapon[3]}, Price: {weapon[6]}")

        for _ in range(num_selections):
            selection = int(input(f"Select weapon {len(selected_weapons) + 1} (Enter the corresponding number): "))

            if 1 <= selection <= len(weapons_list):
                selected_weapons.append(weapons_list[selection - 1])
            else:
                print("Invalid selection. Please choose a valid number.")

    return selected_weapons


def give_starting_weapon(character_name, class_name):
    # TODO spells
    martial_choices = 0
    simple_choices = 0
    weapon_names = []
    print("Giving starting weapons")
    if class_name == "Fighter":
        user_input = input("Would you like a shield? (yes/no): ").lower()
        if user_input == 'yes':
            # TODO give shield
            martial_choices = martial_choices + 1
        else:
            martial_choices = martial_choices + 2
        while True:
            user_input = input("Do you want handaxes or a light crossbow? (handaxe/crossbow): ").lower()
            if "handaxe" in user_input:
                weapon_names.append("Handaxe")
                break
            if 'crossbow' in user_input:
                weapon_names.append("Crossbow, Light")
                break
    if class_name == "Wizard":
        while True:
            user_input = input("Do you want daggers or a quarterstaff? (dagger/quarterstaff): ").lower()
            if "dagger" in user_input:
                weapon_names.append("Dagger")
                break
            if 'quarterstaff' in user_input:
                weapon_names.append("Quarterstaff")
                break
    if class_name == "Rogue":
        weapon_names.append("Dagger")
        while True:
            user_input = input("Do you want a rapier or a shortsword? (rapier/shortsword): ").lower()
            if "rapier" in user_input:
                weapon_names.append("Rapier")
                break
            if 'shortsword' in user_input:
                weapon_names.append("Shortsword")
                break
        if "shortsword" in weapon_names:
            weapon_names.append("Shortbow")
        else:
            while True:
                user_input = input("Do you want a shortbow or a shortsword? (shortbow/shortsword): ").lower()
                if "shortbow" in user_input:
                    weapon_names.append("Shortbow")
                    break
                if 'shortsword' in user_input:
                    weapon_names.append("Shortsword")
                    break
    if class_name == "Cleric":
        # TODO martial proficiency check
        weapon_names.append("mace")
        simple_choices = simple_choices + 1
    if class_name == "Barbarian":
        simple_choices = simple_choices + 1
        martial_choices = martial_choices + 1
    all_martial_weapon = get_weapons_by_type("martial")
    selected_martial_weapons = select_weapons(all_martial_weapon, martial_choices)
    for weapon in selected_martial_weapons:
        weapon_names.append(weapon[0])
    all_simple_weapon = get_weapons_by_type("simple")
    selected_simple_weapons = select_weapons(all_simple_weapon, simple_choices)
    for weapon in selected_simple_weapons:
        weapon_names.append(weapon[0])
    for i in range(len(weapon_names)):
        weapon_names[i] = (character_name, weapon_names[i])
    cursor.executemany(
        'INSERT INTO character_weapon (character_name, weapon_name) VALUES (?, ?)',
        weapon_names)


def give_starting_items(character_name):
    print("Giving starting items")
    starting_items = [(character_name, "Adventure Kit")]
    cursor.executemany(
        'INSERT INTO character_bag (character_name, item_name) VALUES (?, ?)',
        starting_items)


def check_if_name_exists(name):
    # Check if the name exists in the characters table
    cursor.execute("SELECT name FROM characters WHERE name=?", (name,))
    result = cursor.fetchone()
    return bool(result)


# Function to create a character
def create_character():
    available_races, available_classes = get_available_races_classes()
    while True:
        name = input("Enter a name: ")
        if not check_if_name_exists(name):
            break
        else:
            print("This name already exists. Please choose a different name.")
    print("Available Races:", available_races)
    race = input("Enter character race: ")

    if race not in available_races:
        print("Invalid race. Please select from available races.")
        return None

    print("Available Classes:", available_classes)
    class_name = input("Enter character class: ")

    if class_name not in available_classes:
        print("Invalid class. Please select from available classes.")
        return None

    description = input("Enter character description: ")
    try:
        age = int(input("Enter character age (int): "))
    except:
        age = None

    try:
        weight = int(input("Enter character weight (int): "))
    except:
        weight = None

    # Choose method for generating stats
    print("\nChoose a method for generating stats:")
    print("1. Roll Stats")
    print("2. Point Buy")
    method = input("Enter your choice (1 or 2): ")

    if method == '1':
        stats = roll_stats()
    elif method == '2':
        stats = point_buy()
    else:
        print("Invalid choice. Please select either 1 or 2.")
        return None
    modified_states = {"strength": stats[0],
                       "dexterity": stats[1],
                       "constitution": stats[2],
                       "intelligence": stats[3],
                       "wisdom": stats[4],
                       "charisma": stats[5]}
    add_ability_modifier(modified_states, race_name=race)

    starting_health = get_starting_health(modified_states['constitution'], class_name)

    return {
        "name": name,
        "description": description,
        "starting_gold": get_starting_gold(class_name),
        "race": race,
        "class": class_name,
        "stats": stats,
        "age": age,
        "weight": weight,
        "level": 1,  # TODO
        "health": starting_health,
        "proficiency": 2,
        "armor": offer_armor(class_name)
    }


def roll_stats():
    rolls = []
    for i in range(6):
        print(f"Rolling stat ... {i + 1}")
        sleep(1)
        sub_rolls = []
        for j in range(4):
            rolled = random.randint(1, 6)
            print(f"Rolled a {rolled}")
            sub_rolls.append(rolled)
        sub_rolls.remove(min(sub_rolls))
        total = sum(sub_rolls)
        print("Dropping lowest roll")
        print(f"Total: {total}")
        rolls.append(sum(sub_rolls))
    print(f"Rolled stats: {rolls}")
    assigned_stats = [0, 0, 0, 0, 0, 0]
    print(f"Stat order: STR DEX CON INT WIS CHA")
    print("\nAssign the rolls to your stats (e.g., '1 2 3 4 5 6' to assign rolls in order): ")
    user_input = input().split()

    try:
        selections = OrderedSet(map(int, user_input))
        if len(selections) == 6 and all(1 <= s <= 6 for s in selections):
            for i, stat in enumerate(selections):
                assigned_stats[stat - 1] = rolls[i]
        else:
            print("Invalid selection. Please enter six valid numbers (1-6).")
            return None
    except ValueError:
        print("Invalid input. Please enter six valid numbers (1-6).")
        return None

    return assigned_stats


def point_buy():
    points = 27
    stats = [8, 8, 8, 8, 8, 8]

    while points > 0:
        print(f"\nRemaining Points: {points}")
        print(f"Stat order: STR DEX CON INT WIS CHA")
        print("Current Stats:", stats)
        print("Assign points to stats (e.g., '1 2 ' to add 1 point to stat 2): ")
        user_input = input().split()

        try:
            selections = list(map(int, user_input))
            if len(selections) == 2 and 1 <= selections[1] <= 6:
                if points >= selections[0] and stats[selections[1] - 1] < 15 and stats[selections[1] - 1] + selections[0] >= 8 :
                    extra = 0
                    # points above 13 cost 2 to add to
                    if stats[selections[1] - 1] + selections[0] >= 14:
                        if stats[selections[1] - 1] + selections[0] == 15 and stats[selections[1] - 1] < 14:
                            extra = 2
                        else:
                            extra = 1
                    # subtraction
                    if selections[0] < 0 and stats[selections[1] - 1] + selections[0] >= 14:
                        if stats[selections[1] - 1] == 15 and selections[0] < -1:
                            extra = -2
                        else:
                            extra = -1
                    if points >= selections[0] + extra:
                        stats[selections[1] - 1] += selections[0]
                        points -= selections[0] + extra
                    else:
                        print("Selections above 13 cost an extra point")
                else:
                    if selections[0] < 0:
                        print(f"You can't subtract points to stat {selections[1]}.")
                    else:
                        print(f"You can't add points to stat {selections[1]}.")
            else:
                print("Invalid selection. Please enter three valid numbers (1-6).")
        except ValueError:
            print("Invalid input. Please enter three valid numbers (1-6).")

    return stats


# Function to save the character to the database
def save_character(character):
    cursor.execute(
        "INSERT INTO characters (name, description, race, class, age, weight, gold, level, health, max_health, proficiency, armor)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (character["name"], character["description"], character["race"], character["class"],
         character["age"], character["weight"], character["starting_gold"], character["level"], character["health"],
         character['health'], character["proficiency"], character['armor']))

    cursor.execute(
        "INSERT INTO initial_stats (strength, dexterity, constitution, intelligence, wisdom, charisma, character_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (*character["stats"], character["name"]))
    give_starting_items(character_name=character["name"])
    give_starting_weapon(character_name=character["name"], class_name=character["class"])
    conn.commit()
    print(f"\nCharacter '{character['name']}' saved successfully!")


if __name__ == '__main__':
    # Example usage
    character = create_character()
    if character:
        save_character(character)

    # Close the connection
    conn.close()
