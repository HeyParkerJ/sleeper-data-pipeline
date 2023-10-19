from mongo import write
from fetchers import get_transactions, get_upper_and_lower_leg, get_playoff_week_start

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
# Your fromLeg should be 0 if you wanna go all the way back
def fetch_and_write_transactions(LeagueDataFetcher, mongoClient, fromLeg, toLeg):
    for i in range(fromLeg, toLeg, -1):
        transactions = get_transactions(LeagueDataFetcher, i)
        # for each set of transactions, write them
        write_transactions(mongoClient, transactions)
    print('Done fetching and writing transactions')

# I'm unsure if I want to hash on league_id or the year of the season...
# I need the league_id if I want to scale this to other leagues ever...
# Perhaps I can do both or add the season to the data object before inserting...
# Conclusion - let's add season to a transaction and leave it out of this fn
def create_matchup_hash(league_id, leg, matchup_id, roster_id):
    if matchup_id == None:
        matchup_id = 0
    template = "{}-{}-{}-{}".format(league_id, leg, matchup_id, roster_id)
    print(template)
    return template

def fetch_and_push_matchups(league_data, LeagueDataFetcher, mongoClient, season, league_id):
    looping_bounds = get_upper_and_lower_leg(league_data)
    playoff_week_start = get_playoff_week_start(league_data)

    for i in range(looping_bounds[1], looping_bounds[0], -1):
        matchups = LeagueDataFetcher.get_matchups(i)

        # This is *very* inefficient, but let's roll with it until its an issue, then we can improve
        # Note - Edge case not handled: tie
        for matchup in matchups:
            paired_matchup = next(y for y in matchups if y["matchup_id"] == matchup["matchup_id"] and y["roster_id"] != matchup["roster_id"])

            # Handle custom points
            matchup_points = matchup["points"] if matchup["custom_points"] == None else matchup["custom_points"]
            paired_matchup_points = paired_matchup["points"] if paired_matchup["custom_points"] == None else paired_matchup["custom_points"]

            if matchup_points > paired_matchup_points:
                matchup["is_winner"] = True
            elif matchup_points < paired_matchup_points:
                matchup["is_winner"] = False
            else:
                matchup["is_winner"] = None

            if matchup["matchup_id"] == None:
                matchup_id = 0
            else:
                matchup_id = matchup["matchup_id"]

            roster_id = matchup["roster_id"]
            hash = create_matchup_hash(league_id, i, matchup_id, roster_id)

            # TODO - get season from league data before appending
            matchup["opponent_score"] = paired_matchup["points"]
            matchup["opponent_roster_id"] = paired_matchup["roster_id"]
            matchup["season"] = season
            matchup["league_id"] = league_id
            matchup["leg"] = i
            if i >= playoff_week_start:
                matchup["is_playoffs"] = True
            else:
                matchup["is_playoffs"] = False
            
            write(mongoClient, "matchups", {"_id": hash}, matchup)

def write_season(mongoClient, league_data):
    filter_query = {"league_id": league_data['league_id']}
    write(mongoClient, 'league', filter_query, league_data)