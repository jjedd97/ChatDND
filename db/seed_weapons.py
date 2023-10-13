import sqlite3

# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect('dnd.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Define the SQL command to create the weapons table
create_table_query = '''
CREATE TABLE IF NOT EXISTS weapons (
    "name" TEXT,
    "type" TEXT,
    "damage" TEXT,
    "weight" INTEGER,
    "range" INTEGER,
    "fullrange" INTEGER,
    "price" INTEGER,
    "finesse" INTEGER,
    "hands" INTEGER,
    PRIMARY KEY("name")
);
'''

# Execute the SQL command
cursor.execute(create_table_query)


weapons_data = [
    ('Club', 'Simple Melee', '1d4 bludgeoning', 2, None, None, 1, 0, 1),
    ('Dagger', 'Simple Melee', '1d4 piercing', 1, 20, 60, 2, 1, 1),
    ('Greatclub', 'Simple Melee', '1d8 bludgeoning', 10, None, None, 2, 0, 2),
    ('Handaxe', 'Simple Melee', '1d6 slashing', 2, None, None, 5, 0, 1),
    ('Javelin', 'Simple Melee', '1d6 piercing', 2, 30, 120, 5, 0, 1),
    ('Light Hammer', 'Simple Melee', '1d4 bludgeoning', 2, None, None, 2, 0, 1),
    ('Mace', 'Simple Melee', '1d6 bludgeoning', 4, None, None, 5, 0, 1),
    ('Quarterstaff', 'Simple Melee', '1d6 bludgeoning', 4, None, None, 2, 0, 2),
    ('Sickle', 'Simple Melee', '1d4 slashing', 2, None, None, 1, 0, 1),
    ('Spear', 'Simple Melee', '1d6 piercing', 3, 20, 60, 1, 0, 1),
    ('Crossbow, Light', 'Simple Ranged', '1d8 piercing', 5, 80, 320, 25, 0, 2),
    ('Dart', 'Simple Ranged', '1d4 piercing', 0.25, 20, 60, 0.05, 1, 1),
    ('Shortbow', 'Simple Ranged', '1d6 piercing', 2, 80, 320, 25, 0, 2),
    ('Sling', 'Simple Ranged', '1d4 bludgeoning', None, 30, 120, 0.1, 0, 1),
    ('Battleaxe', 'Martial Melee', '1d8 slashing', 4, None, None, 10, 0, 1),
    ('Flail', 'Martial Melee', '1d8 bludgeoning', 2, None, None, 10, 0, 1),
    ('Glaive', 'Martial Melee', '1d10 slashing', 6, None, None, 20, 0, 2),
    ('Greataxe', 'Martial Melee', '1d12 slashing', 7, None, None, 30, 0, 2),
    ('Greatsword', 'Martial Melee', '2d6 slashing', 6, None, None, 50, 0, 2),
    ('Halberd', 'Martial Melee', '1d10 slashing', 6, None, None, 20, 0, 2),
    ('Lance', 'Martial Melee', '1d12 piercing', 6, None, None, 10, 0, 2),
    ('Longsword', 'Martial Melee', '1d8 slashing', 3, None, None, 15, 0, 1),
    ('Maul', 'Martial Melee', '2d6 bludgeoning', 10, None, None, 10, 0, 2),
    ('Morningstar', 'Martial Melee', '1d8 piercing', 4, None, None, 15, 0, 1),
    ('Pike', 'Martial Melee', '1d10 piercing', 18, None, None, 5, 0, 2),
    ('Rapier', 'Martial Melee', '1d8 piercing', 2, None, None, 25, 1, 1),
    ('Scimitar', 'Martial Melee', '1d6 slashing', 3, None, None, 25, 1, 1),
    ('Shortsword', 'Martial Melee', '1d6 piercing', 2, None, None, 10, 1, 1),
    ('Trident', 'Martial Melee', '1d6 piercing', 4, 20, 60, 5, 0, 1),
    ('War Pick', 'Martial Melee', '1d8 piercing', 2, None, None, 5, 0, 1),
    ('Warhammer', 'Martial Melee', '1d8 bludgeoning', 2, None, None, 15, 0, 1),
    ('Whip', 'Martial Melee', '1d4 slashing', 3, None, None, 2, 1, 1),
    ('Blowgun', 'Martial Ranged', '1 piercing', 1, 25, 100, 10, 0, 2),
    ('Crossbow, Hand', 'Martial Ranged', '1d6 piercing', 3, 30, 120, 75, 0, 2),
    ('Crossbow, Heavy', 'Martial Ranged', '1d10 piercing', 18, 100, 400, 50, 0, 2),
    ('Longbow', 'Martial Ranged', '1d8 piercing', 2, 150, 600, 50, 0, 2),
    ('Net', 'Martial Ranged', '—', 3, 5, 15, 1, 0, 2)
    ]

# Insert the weapons data into the table
cursor.executemany('INSERT INTO weapons ("name", "type", "damage", "weight", "range", "fullrange", "price", "finesse", "hands") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', weapons_data)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database table of weapons created successfully.")
