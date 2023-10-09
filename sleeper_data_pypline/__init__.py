from sleeper_wrapper import League, Players
from dotenv import load_dotenv
from mongo import connect, write, read
from commands import get_all_league_ids_in_mongo
import json

load_dotenv()

def init():
    mongoClient = connect()

    latest_league_id = 983808897297317888 # 2023
    LeagueDataFetcher = League(latest_league_id)

    # league_data = LeagueDataFetcher.get_league()

def query_transactions():
    read("transactions")

def write_players(players, mongoClient):
    players_list = list(players.values())
    for player in players_list:
        filter_query = { "player_id": player["player_id"] }
        write(mongoClient, 'players', filter_query, player)

# Leg is the current "week"
def fetch_and_write_transactions(LeagueDataFetcher, mongoClient, leg):
    for i in range(leg, 0, -1):
        transactions = get_transactions(i, LeagueDataFetcher)
        # for each set of transactions, write them
        write_transactions(mongoClient, transactions)
    print('Done fetching and writing transactions')

# do this next
def get_players():
    players = Players()
    all_players = players.get_all_players()

def get_transactions(week, LeagueDataFetcher):
    return League.get_transactions(LeagueDataFetcher, week)

def write_transactions(mongoClient, transactions):
    for transaction in transactions:
        trans_id = transaction[ 'transaction_id' ]
        filter_query = { "transaction_id": trans_id }
        write(mongoClient, 'transactions', filter_query, transaction)

def get_leg(league_data):
    return league_data['settings']['leg']

def write_season(mongoClient, league_data):
    filter_query = {"league_id": league_data['league_id']}
    write(mongoClient, 'league', filter_query, league_data)

def write_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file)
    
    print('Done writing to file', filename)

init()

# read()

# print(json.dumps(data))

# print(data)
