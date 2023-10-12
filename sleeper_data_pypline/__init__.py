from pymongo import DESCENDING
from sleeper_wrapper import League, Players
from dotenv import load_dotenv
from datetime import datetime
from mongo import connect, write, read
from commands import get_all_league_ids_in_mongo
import json

load_dotenv()

def init():
    mongoClient = connect()

    # LeagueDataFetcher = League(get_10g1c_leagueid_by_year(2020))
    t = get_highest_bids_of_all_time(10)
    transform_transactions_to_human_readable(t)

def get_highest_bids_of_all_time(limit):
    def readFn(collection):
        documents = []
        cursor = collection.find().sort('settings.waiver_bid', DESCENDING).limit(limit)
        # Note - prob don't need to take docs out of cursor then append to a new list, can refactor
        for document in cursor:
            documents.append(document)

        return documents

    result = read('transactions', readFn)
    return result

def transform_transactions_to_human_readable(transactions):
    # Note - the impl described below is just for waiver claims

    # 1 - Loop over each transaction and pull out all keys in `adds` and add them to a list (maybe make this an obj if collision is a possible issue?)
    player_ids = []
    for transaction in transactions:
        for player_id in transaction.get("adds"):
            player_ids.append(player_id)
    
    # 2 - Once I have that list, grab all the keys and send a query to our Players db for the names of all those players
    player_ids_and_names = get_player_names_from_ids(player_ids)

    # 3 - When I get the return object, iterate over all the transactions (again) and use the player names to
    # create a human readable output
    human_readable_transactions = []
    for transaction in transactions:
        print('faab', transaction.get("settings.waiver_bid"))
        print('player_id', transaction.get("adds"))

        adds = list(transaction.get("adds").keys())[0]
        print('adds key', adds)

        HR_transaction = {
            "faab": transaction["settings"]["waiver_bid"],
            "player_name": player_ids_and_names.get(list(transaction.get("adds").keys())[0]),
            "owner": get_manager_names_from_ids(transaction.get("roster_ids")[0]),
            "date": transform_timestamp_to_human_readable(transaction.get("status_updated"))
        }
        human_readable_transactions.append(HR_transaction)

    print(human_readable_transactions)

def get_manager_names_from_ids(manager_ids):
    # I need to populate the DB with this info before I can implement
    print('implement me!')

# player_ids must be a list
def get_player_names_from_ids(player_ids):
    def readPlayersFn(collection):
        cursor = collection.find({"player_id": {"$in": player_ids}}, {"player_id": 1, "full_name": 1})
        return cursor

    players = read('players', readPlayersFn)

    # Initialize an empty dictionary to store the results
    result_dict = {}

    # Loop through the cursor and populate the dictionary
    for document in players:
        player_id = document.get('player_id')
        full_name = document.get('full_name')
        if player_id is not None and full_name is not None:
            result_dict[player_id] = full_name

    return result_dict


def transform_timestamp_to_human_readable(timestamp_in_ms):
    # Convert to a datetime object
    timestamp_in_s = timestamp_in_ms / 1000
    dt_object = datetime.fromtimestamp(timestamp_in_s)

    # Convert to a human-readable string
    human_readable = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return human_readable


def get_10g1c_leagueid_by_year(year):
    if year == 2020:
        return 603631612793520128
    elif year == 2021:
        return 687728692536893440
    elif year == 2022:
        return 852771702776672256
    elif year == 2023:
        return 983808897297317888
    else:
        print("Not a valid or known season year provided to get_10g1c_leagueid_by_year", year)

# This isn't going to work the way I want it because of Mongo not really having left-joins
# What I CAN do is grab the transactions from the last week, then query for those players
# The high level function could be like "create_dadbot_transaction_payload"
def query_transactions():
    def readFn(collection):
        collection.aggregate([
            {
                "$lookup":
                {
                    "from": "players",                  # the collection to join with
                    "localField": "",          # field from the orders collection
                    "foreignField": "_id",               # field from the products collection
                    "as": "product_details"              # the array field that will hold the "joined" data
                }
            }
        ])
        
    read("transactions", readFn)

def write_players(players, mongoClient):
    players_list = list(players.values())
    for player in players_list:
        filter_query = { "player_id": player["player_id"] }
        write(mongoClient, 'players', filter_query, player)

# Leg is the current "week"
def fetch_and_write_transactions(LeagueDataFetcher, mongoClient, throughLeg):
    for i in range(throughLeg, 0, -1):
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
