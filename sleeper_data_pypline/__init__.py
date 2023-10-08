from sleeper_wrapper import League
from dotenv import load_dotenv
from mongo import connect, write
from commands import get_all_league_ids_in_mongo
import json

load_dotenv()

def init():
    # mongoClient = connect()

    latest_league_id = 983808897297317888 # 2023
    LeagueDataFetcher = League(latest_league_id)

    league_data = LeagueDataFetcher.get_league()

    # write_season(league_data) 
    leg = get_leg(league_data)
    print(leg)

    # Need to currently add the 2023 season to Mongodb


def write_transaction(week, LeagueDataFetcher, mongoClient):
    transactions = League.get_transactions(LeagueDataFetcher, 1)

    for transaction in transactions:
        trans_id = transaction[ 'transaction_id' ]
        filter_query = { "transaction_id": trans_id }
        write(mongoClient, 'transactions', filter_query, transaction)

def get_leg(league_data):
    return league_data['settings']['leg']

def write_season(league_data):
    print(json.dumps(league_data))

init()

# read()

# print(json.dumps(data))

# print(data)
