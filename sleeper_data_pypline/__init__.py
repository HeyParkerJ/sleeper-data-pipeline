from sleeper_wrapper import League
from dotenv import load_dotenv
from mongo import do
import json

load_dotenv()

league_id = 852771702776672256 # this is for 2022

league = League(league_id)

data = League.get_league(league)

do()

print(data)
