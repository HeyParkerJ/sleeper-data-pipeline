from sleeper_wrapper import League, Players

def get_players():
    players = Players()
    all_players = players.get_all_players()

def get_transactions(LeagueDataFetcher, week):
    return League.get_transactions(LeagueDataFetcher, week)

def get_leg(league_data):
    return league_data['settings']['leg']
