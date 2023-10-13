import json
import os
import re
from random import randint

import openai
import sqlite3

from src.combat import combat
from src.create_character import load_db_character_dict
from src.dice_roller import get_modifier
from src.location import Location

model_engine = "gpt-3.5-turbo"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to the database
conn = sqlite3.connect('db/dnd.db')
cursor = conn.cursor()


def send_message(messages):
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=messages
    )
    return response.choices[0].message['content']


def extract_situation(message):
    if message:
        try:
            start = message.index("{")
            end = message.rindex("}")
            extracted_situation = eval(message[start:end + 1])
            return extracted_situation
        except ValueError:
            return None


def is_character_in_database(character_name):
    cursor.execute("SELECT * FROM characters WHERE name=?", (character_name,))
    return cursor.fetchone() is not None


def load_supported_monster_types():
    cursor.execute("SELECT name FROM monsters")
    return cursor.fetchall()


character_name = input("Hello, which character is going on an adventure today? ")
if not is_character_in_database(character_name):
    exit()
character_dict = load_db_character_dict(character_name)

adventure_name = input("Enter the name of an adventure file or nothing for a random story: ")
if os.path.exists(adventure_name):
    with open(adventure_name, 'r') as file:
        adventure_description = file.read()
else:
    adventure_description = "Generate a fun 5e based dnd adventure of your choosing"

# Initialize conversation with a system message
conversation = [{'role': 'system', 'content': 'You are a dungeon master for 5e.'},
                {'role': 'system', 'content': "This is the player's character:" + json.dumps(character_dict)},
                {'role': 'system', 'content': "Supported monsters: " + str(load_supported_monster_types())},
                {'role': 'system',
                 'content': "If the adventure is done/finished, Include, 'ADVENTURE DONE' in the message"},
                {'role': 'system',
                 'content': "If the player's health is ever not positive, describe their death and end the adventure"},
                {'role': 'system',
                 'content': "To request dice rolls, send a message in the form of DICE_ROLL_WISDOM, only stats can be requested"},
                {'role': 'system',
                 'content': "All combat will be handled locally."},
                {'role': 'system',
                 'content': "Player init is handled by the local combat system. "
                            "To begin a combat return a message of form: '{monsters: [{monster_name: str, "
                            "char: character, initiative: int}], location: {description:str"
                            ", length: int, width: int, occupied: (int, int, char), player_location: (int, int)}}'."
                            " Monster names must be in the supported monsters lists, char should be a unique character."
                            " Room sizes should always have extra space. Monsters in room need to occupy a location."},
                {'role': 'system', 'content': "Describe the initial scene to the player. The first response should not be combat."
                                              " Adventure description: " + adventure_description}]
description = send_message(conversation)
conversation.append({'role': 'assistant', 'content': description})
print(description)
combat_message = None
rolls = []
while True:
    if not combat_message and not rolls:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        # Add user message to conversation
        conversation.append({'role': 'user', 'content': user_input})

    # Get assistant's reply
    response = send_message(conversation)
    # Add assistant's message to conversation
    conversation.append({'role': 'assistant', 'content': response})
    combat_message = extract_situation(response)
    if combat_message:
        player_initiative = randint(1, 20)
        player_initiative = player_initiative + get_modifier(character_dict['stats']['dexterity'])
        print(f"Rolling initiative ... {player_initiative}")
        location = Location(**combat_message['location'])
        player = combat(location=location, monsters=combat_message["monsters"], player=character_dict, init=10)
        conversation.append({'role': 'system', 'content': "player after combat: " + json.dumps(character_dict)})
        conversation.append({'role': 'system', 'content': "Describe the result of combat based on the player's health"})
    else:
        # Print assistant's reply
        print(f"DM: {response}")
        if "DICE_ROLL" in response:
            # Define the pattern
            pattern = r'DICE_ROLL\w*'
            # Find all matches in the input string
            matches = re.findall(pattern, response)
            rolls = []
            for match in matches:
                words = match.split("_")[-1]
                mod = get_modifier(character_dict["stats"][words.lower()])
                rolls.append(randint(1, 20)+mod)
            print(f"Dice roll results {rolls}")
            conversation.append({'role': 'system', 'content': "Dice rolls: " + str(rolls)})
        else:
            rolls = []

    if "ADVENTURE DONE" in response:
        break
