from pydantic_core.core_schema import chain_schema
import requests
from bs4 import BeautifulSoup
import pandas as pd


# Define the class to store the frame data
class FrameData:

    def __init__(self, skill, startup, active, recovery, hit, block, cancel,
                 damage, combo, drive_gain, drive_lose_guard,
                 drive_lose_punish, sa_gain, attribute, note):
        self.skill = skill
        self.startup = startup
        self.active = active
        self.recovery = recovery
        self.hit = hit
        self.block = block
        self.cancel = cancel
        self.damage = damage
        self.combo = combo
        self.drive_gain = drive_gain
        self.drive_lose_guard = drive_lose_guard
        self.drive_lose_punish = drive_lose_punish
        self.sa_gain = sa_gain
        self.attribute = attribute
        self.note = note

    def __str__(self):
        return (f"Skill: {self.skill}\n"
                f"Startup Frames: {self.startup}\n"
                f"Active Frames: {self.active}\n"
                f"Recovery Frames: {self.recovery}\n"
                f"Hit Frames: {self.hit}\n"
                f"Block Frames: {self.block}\n"
                f"Cancel Type: {self.cancel}\n"
                f"Damage: {self.damage}\n"
                f"Combo: {self.combo}\n"
                f"Drive Gauge Gain (Hit): {self.drive_gain}\n"
                f"Drive Gauge Lose (Guard): {self.drive_lose_guard}\n"
                f"Drive Gauge Lose (Punish): {self.drive_lose_punish}\n"
                f"SA Gauge Gain: {self.sa_gain}\n"
                f"Attribute: {self.attribute}\n"
                f"Note: {self.note}")


# Function to scrape and process the data
def scrape_frame_data(url):
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Make a request with the custom headers
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all tr elements where class does not contain 'heading'
    tr_elements = soup.find_all('tr',
                                class_=lambda x: x != 'frame_heading__hh7Ah')

    frame_data_list = []

    # Loop through each tr element and extract the relevant data
    for tr in tr_elements:
        td_elements = tr.find_all('td')

        if len(td_elements
               ) == 15:  # Make sure the expected number of columns are present
            name = td_elements[0].text.strip().replace('\n', '')
            if name[-1].isupper():
                # Remove the last character
                name = name[:-1]
            skill = name
            startup = td_elements[1].text.strip()
            active = td_elements[2].text.strip()
            recovery = td_elements[3].text.strip()
            hit = td_elements[4].text.strip()
            block = td_elements[5].text.strip()
            cancel = td_elements[6].text.strip()
            damage = td_elements[7].text.strip()
            combo = td_elements[8].text.strip()
            drive_gain = td_elements[9].text.strip()
            drive_lose_guard = td_elements[10].text.strip()
            drive_lose_punish = td_elements[11].text.strip()
            sa_gain = td_elements[12].text.strip()
            attribute = td_elements[13].text.strip()
            note = td_elements[14].text.strip()

            # Create an instance of FrameData class and append to the list
            frame_data = FrameData(skill, startup, active, recovery, hit,
                                   block, cancel, damage, combo, drive_gain,
                                   drive_lose_guard, drive_lose_punish,
                                   sa_gain, attribute, note)
            frame_data_list.append(frame_data)

    return frame_data_list


def get_character_name(character):
    character = character.lower().replace(" ", "")
    if 'bison' in character:
        character = "vega_mbison"
    elif 'honda' in character:
        character = "ehonda"
    elif 'gief' in character:
        character = "zangief"
    elif 'akuma' in character:
        character = "gouki_akuma"
    return character


def get_frame_data(character):
    character = get_character_name(character)
    url = f'https://www.streetfighter.com/6/en-us/character/{character}/frame'
    frame_data_list = scrape_frame_data(url)
    return frame_data_list


def get_plus_on_block(character):
    character = get_character_name(character)
    data = get_frame_data(character)
    plus_on_block = sorted([
        frame for frame in data
        if frame.block.strip().isdigit() and int(frame.block) > 0
    ],
                           key=lambda frame: frame.skill)

    response = ""
    for move in plus_on_block:
        response += f"{move.skill} +{move.block} on block\n"

    if response == "":
        response = "No moves with plus on block frames found."
    return response


def get_punish(character):
    character = get_character_name(character)
    data = get_frame_data(character)

    punish_on_block = sorted([
        frame for frame in data
        if frame.block.lstrip('-').isdigit() and int(frame.block) < -3
    ],
                             key=lambda frame: frame.skill)

    response = ""
    for move in punish_on_block:
        response += f"{move.skill} {move.block} on block\n"

    if response == "":
        response = "No moves with negative block frames found."
    return response


def get_super(character):
    character = get_character_name(character)
    data = get_frame_data(character)
    super_cancels = sorted(
        [frame for frame in data if frame.cancel in ["SA1", "SA2", "SA3"]],
        key=lambda frame:
        (["SA1", "SA2", "SA3"].index(frame.cancel), frame.skill))

    response = ""
    for move in super_cancels:
        response += f"{move.skill} can cancel into {move.cancel}\n"

    return response
