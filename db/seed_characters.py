import sqlite3

# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect('dnd.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

class_table = '''
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY,
    name TEXT,
    hit_dice TEXT,
    primary_ability TEXT,
    saving_throw_proficiency TEXT,
    armor_proficiency TEXT,
    weapon_proficiency TEXT,
    spellcasting_ability TEXT,
    starting_equipment TEXT,
    class_traits TEXT,
    starting_gold INTEGER
);
'''
classes = [
('Wizard', 'd6', 'Intelligence', 'Intelligence, Wisdom', 'None', 'Daggers, darts, slings, quarterstaffs, light crossbows', 'Intelligence', 'A spellbook, an arcane focus, a scholar''s pack, a spell component pouch', 'Spellcasting, Arcane Recovery, Arcane Tradition', "4d4 x 10"),
('Fighter', 'd10', 'Strength or Dexterity', 'Strength, Constitution', 'All armor, shields', 'Simple weapons, martial weapons', 'None', 'Chain mail, a martial weapon and a shield, a longbow and 20 arrows, a dungeoneer''s pack or an explorer''s pack', 'Fighting Style, Second Wind', "5d4 x 10"),
('Rogue', 'd8', 'Dexterity', 'Dexterity, Intelligence', 'Light armor', 'Simple weapons, hand crossbows, longswords, rapiers, shortswords', 'Dexterity', 'Leather armor, two daggers, thieves'' tools, a burglar''s pack', 'Sneak Attack, Thieves'' Cant, Cunning Action', "4d4 x 10gp"),
('Cleric', 'd8', 'Wisdom', 'Wisdom, Charisma', 'Light armor, medium armor, shields', 'All simple weapons', 'Wisdom', 'A mace or a warhammer, scale mail, a light crossbow and 20 bolts, a priest''s pack or an explorer''s pack', 'Spellcasting, Divine Domain', "5d4 x 10"),
('Barbarian', 'd12', 'Strength', 'Strength, Constitution', 'Light armor, medium armor, shields', 'Simple weapons, martial weapons', 'None', 'An explorer''s pack, four javelins', 'Rage, Unarmored Defense', '2d4 x 10')
]
cursor.execute(class_table)
# Insert the race data into the table
cursor.executemany('INSERT INTO classes (name, hit_dice, primary_ability, saving_throw_proficiency, armor_proficiency, weapon_proficiency, spellcasting_ability, starting_equipment, class_traits, starting_gold) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', classes)

race_table = ''' CREATE TABLE IF NOT EXISTS races (
    name TEXT PRIMARY KEY,
    size TEXT,
    speed INTEGER,
    languages TEXT,
    ability_score_modifiers TEXT,
    vision TEXT,
    traits TEXT
); '''
cursor.execute(race_table)
races = [('Human', 'Medium', 30, 'Common', '{"Strength": 1, "Dexterity": 1, "Constitution": 1, "Intelligence": 1, "Wisdom": 1, "Charisma": 1}', 'Normal', 'Versatile and adaptable.'),
('Elf', 'Medium', 30, 'Common, Elvish', '{"Dexterity": 2}', 'Darkvision 60ft', 'Keen senses and love for nature.'),
('Dwarf', 'Medium', 25, 'Common, Dwarvish', '{"Constitution": 2}', 'Darkvision 60ft', 'Resistant to poison and skilled craftsmen.'),
('Halfling', 'Small', 25, 'Common, Halfling', '{"Dexterity": 2}', 'None', 'Lucky and stealthy by nature.')]
# Insert the race data into the table
cursor.executemany('INSERT INTO races (name, size, speed, languages, ability_score_modifiers, vision, traits) VALUES (?, ?, ?, ?, ?, ?, ?)', races)

# Define the SQL command to create the characters table
create_table_query = '''
CREATE TABLE IF NOT EXISTS characters (
    name TEXT PRIMARY KEY,
    race TEXT,
    class TEXT,
    age INT,
    weight INT,
    description TEXT,
    gold INT, 
    max_health INT,
    health INT,
    level INT,
    proficiency INTEGER,
    armor TEXT,
    FOREIGN KEY (class) REFERENCES classes (name),
    FOREIGN KEY (race) REFERENCES races (name)
);
'''

# Execute the SQL command
cursor.execute(create_table_query)
create_table_query = '''
CREATE TABLE IF NOT EXISTS initial_stats (
    id INTEGER PRIMARY KEY,
    strength INTEGER,
    dexterity INTEGER,
    constitution INTEGER,
    intelligence INTEGER,
    wisdom INTEGER,
    charisma INTEGER,
    character_name TEXT,
    FOREIGN KEY (character_name) REFERENCES characters (name)
);
'''

# Execute the SQL command
cursor.execute(create_table_query)

create_table_query = '''
CREATE TABLE IF NOT EXISTS character_weapon (
    character_name TEXT,
    weapon_name TEXT,
    FOREIGN KEY (character_name) REFERENCES characters(name),
    FOREIGN KEY (weapon_name) REFERENCES weapons(name)
);
'''

# Execute the SQL command
cursor.execute(create_table_query)
item_table = '''CREATE TABLE IF NOT EXISTS items (
    name TEXT PRIMARY KEY,
    item_type TEXT,
    description TEXT,
    weight INTEGER,
    value INTEGER,
    max_uses INTEGER
); '''
cursor.execute(item_table)
items = [('Health Potion', 'Consumable', 'Restores 2d4 + 2 of the user''s health.', 0.5, 50, 1),
    ('Key', 'Key', 'Unlocks a specific door or chest.', 0.1, 10, 1),
    ('Adventure Kit', 'Tool', 'Contains basic supplies for wilderness travel and survival.', 5, 100, None)]
cursor.executemany('INSERT INTO items (name, item_type, description, weight, value, max_uses) VALUES (?, ?, ?, ?, ?, '
                   '?)', items)



create_table_query = '''
CREATE TABLE IF NOT EXISTS character_bag (
    character_name TEXT,
    item_name TEXT,
    FOREIGN KEY (character_name) REFERENCES characters(name),
    FOREIGN KEY (item_name) REFERENCES items(name)
);
'''

# Execute the SQL command
cursor.execute(create_table_query)


conn.commit()
conn.close()

print("Database table of characters created successfully.")