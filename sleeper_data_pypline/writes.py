from mongo import write
from fetchers import get_transactions

def write_transactions(mongoClient, transactions):
    for transaction in transactions:
        trans_id = transaction[ 'transaction_id' ]
        filter_query = { "transaction_id": trans_id }
        write(mongoClient, 'transactions', filter_query, transaction)

def write_players(players, mongoClient):
    players_list = list(players.values())
    for player in players_list:
        filter_query = { "player_id": player["player_id"] }
        write(mongoClient, 'players', filter_query, player)

# Leg is the current "week"
def fetch_and_write_transactions(LeagueDataFetcher, mongoClient, fromLeg, toLeg):
    for i in range(fromLeg, toLeg, -1):
        transactions = get_transactions(LeagueDataFetcher, i)
        # for each set of transactions, write them
        write_transactions(mongoClient, transactions)
    print('Done fetching and writing transactions')

def write_season(mongoClient, league_data):
    filter_query = {"league_id": league_data['league_id']}
    write(mongoClient, 'league', filter_query, league_data)