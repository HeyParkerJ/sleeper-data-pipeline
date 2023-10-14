from mongo import read
from datetime import datetime

# There are many times where I'll have a roster id and I want a display name instead
def get_display_name_from_roster_id(LeagueDataFetcher, roster_id):
    rosters = LeagueDataFetcher.get_rosters()

    # 2 - rosters.find (or whatever) where roster_id === roster_id
    owner_id = get_owner_id_from_roster_id(roster_id, rosters)

    # 3 - Get display name with this user/owner_id
    users = LeagueDataFetcher.get_users()
    display_name = get_display_name_from_user_id(owner_id, users)
    return display_name

def get_display_name_from_user_id(user_id, users):
    display_name = None
    for user in users:
        if user["user_id"] == user_id:
            display_name = user["display_name"]
    return display_name

# TAKE NOTE - owner_id (from rosters) is the same as user_id (from users)
def get_owner_id_from_roster_id(roster_id, rosters):
    owner_id = None
    for roster in rosters:
        if roster["roster_id"] == roster_id:
            owner_id = roster["owner_id"]
    return owner_id

def transform_transactions_to_human_readable(transactions, LeagueDataFetcher):
    # Note - the impl described below is just for waiver claims
    # It would be an enhancement to make it work for trades

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
        adds = list(transaction.get("adds").keys())[0]

        owner_display_name = get_display_name_from_roster_id(LeagueDataFetcher, transaction.get("roster_ids")[0])

        HR_transaction = {
            "faab": transaction["settings"]["waiver_bid"],
            "player_name": player_ids_and_names.get(list(transaction.get("adds").keys())[0]),
            "owner": owner_display_name,
            "date": transform_timestamp_to_human_readable(transaction.get("status_updated"))
        }
        human_readable_transactions.append(HR_transaction)

    return human_readable_transactions

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

