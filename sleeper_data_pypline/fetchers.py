from sleeper_wrapper import League, Players

def get_players():
    players = Players()
    all_players = players.get_all_players()

def get_transactions(LeagueDataFetcher, week):
    return League.get_transactions(LeagueDataFetcher, week)

def get_leg(league_data):
    return league_data['settings']['leg']

# This function intends to return data on which legs we should iterate through to backfill data for
# a given season. For example, in a completed 17 week season, it should return
# an array of [lower, upper] - ex: [1, 17]
def get_upper_and_lower_leg(league_data):
    upper = 0
    # Note - this conditional is superflous at the moment - it appears the downstream data is the same either way
    if league_data["status"] == "in_season":
        upper = league_data["settings"]["leg"] # This will be the current leg
    if league_data["status"] == "complete":
        upper = league_data["settings"]["leg"] # This will be the last leg

    return [0, upper]

def get_playoff_week_start(league_data):
    return league_data["settings"]["playoff_week_start"]