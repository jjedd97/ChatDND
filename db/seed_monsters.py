import sqlite3

# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect('dnd.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()
monster_table = '''
CREATE TABLE IF NOT EXISTS monsters (
    name TEXT PRIMARY KEY,
    type TEXT,
    alignment TEXT,
    hit_points INTEGER,
    armor_class INTEGER,
    challenge_rating REAL,
    resistances TEXT,
    weaknesses TEXT,
    speed INTEGER
);'''
monsters = [
    ('Goblin', 'Humanoid', 'Neutral Evil', 7, 15, 0.25, None, None, 30),
    ('Orc', 'Humanoid', 'Chaotic Evil', 15, 13, 0.5, None, None, 30),
    ('Giant Spider', 'Beast', 'Unaligned', 26, 14, 1, None, None, 30),
    ('Skeleton', 'Undead', 'Lawful Evil', 13, 13, 0.25, "poison", "bludgeoning", 30),
    ('Zombie', 'Undead', 'Neutral Evil', 22, 8, 0.5, "poison", None, 20)
]
cursor.execute(monster_table)
# Insert the race data into the table
cursor.executemany('INSERT INTO monsters (name, type, alignment, hit_points, armor_class, challenge_rating, resistances, weaknesses, speed) '
                   'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', monsters)

attack_table = '''
CREATE TABLE IF NOT EXISTS attacks (
    id INTEGER PRIMARY KEY,
    monster_name TEXT,
    name TEXT,
    hit INTEGER,
    damage_type TEXT,
    damage_roll TEXT,
    save_roll TEXT,
    save_damage TEXT,
    save_type TEXT,
    max_targets INTEGER, 
    range INTEGER,
    fullrange INTEGER,
    charges INTEGER,
    status TEXT,
    FOREIGN KEY(monster_name) REFERENCES monsters(name)
);'''
cursor.execute(attack_table)
attacks = [
("Goblin", 'Scimitar', 4, 'slashing', '1d6 + 2', None, None, None, 1, None, None, None, None),
    ("Goblin", 'Shortbow', 4, 'piercing', '1d6 + 2', None, None, None, 1, 80, 320, None, None),
("Orc", 'Greataxe', 5, 'slashing', '1d12 + 3', 1, None, None, None, None, None, None, None),
("Orc", 'Javelin', 5, 'piercing', '1d6 + 3', None, None, None, 1, 30, 120, None, None),
("Giant Spider", 'Bite', 5, 'piercing', '1d8 + 3', "DC 11 Constitution half", "2d8", "poison", 1, 80, 320, None, None),
("Giant Spider", 'Web', 5, None, None, None, None, None, 1, 30, 60, 5, "{'restrained':'DC 12 Strength'}"),
("Skeleton", 'Shortsword', 5, 'piercing', '1d6 + 2', None, None, None, 1, None, None, None, None),
("Skeleton", 'Shortbow', 5, 'piercing', '1d6 + 2', None, None, None, 1, 80, 320, None, None),
("Zombie", 'Slam', 3, 'bludgeoning', '1d6 + 1', None, None, None, 1, None, None, None, None),
]

cursor.executemany('INSERT INTO attacks '
                   '(monster_name, name, hit, damage_type, damage_roll,  save_roll, save_damage, save_type, max_targets,'
                   ' range, fullrange, charges, status) '
                   'VALUES (?,?,?,?,?,?,?,?, ?, ?, ?, ?, ?)',
                   attacks)


conn.commit()
conn.close()

print("Database table of monsters created successfully.")