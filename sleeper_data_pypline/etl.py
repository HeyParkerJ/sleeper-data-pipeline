from sleeper_wrapper import League, Drafts, Players
from mongo import write
from transforms import get_10g1c_leagueid_by_year
from fetchers import get_transactions, get_leg, get_upper_and_lower_leg, get_playoff_week_start

def write_draft(mongoClient, league_id):
    LeagueDataFetcher = League(league_id)
    drafts = LeagueDataFetcher.get_all_drafts()
    if len(drafts) != 1:
        print('Very unexpected scenario encountedered: This league has >1 draft. LeagueID:', league_id)
            
    draft_id = drafts[0]["draft_id"]

    DraftDataFetcher = Drafts(draft_id)

    all_picks = DraftDataFetcher.get_all_picks()
    draft_details = DraftDataFetcher.get_specific_draft()

    draft_details_filter_query = {draft_id: draft_id}
    write(mongoClient, 'drafts', draft_details_filter_query, draft_details)

    for pick in all_picks:
        draft_picks_filter_query = { "draft_id": draft_id, 
                                        "round": pick["round"], 
                                        "pick_no": pick["pick_no"] }
        write(mongoClient, 'draft_picks', draft_picks_filter_query, pick)
        print('Wrote pick:', pick["round"], pick["pick_no"])

def fetch_and_write_transactions(LeagueDataFetcher, mongoClient, highLeg, lowLeg):
    """
    LowLeg should be 0 if you wanna go all the way back
    """
    def write_transactions(mongoClient, transactions):
        for transaction in transactions:
            trans_id = transaction[ 'transaction_id' ]
            filter_query = { "transaction_id": trans_id }
            write(mongoClient, 'transactions', filter_query, transaction)

    for i in range(highLeg, lowLeg, -1):
        transactions = League.get_transactions(LeagueDataFetcher, i)
        # for each set of transactions, write them
        write_transactions(mongoClient, transactions)
    print('Done fetching and writing transactions')


def fetch_and_push_matchups(LeagueDataFetcher, mongoClient):
    def create_matchup_hash(league_id, leg, matchup_id, roster_id):
        if matchup_id == None:
            matchup_id = 0
        template = "{}-{}-{}-{}".format(league_id, leg, matchup_id, roster_id)
        print(template)
        return template

    league_data = LeagueDataFetcher.get_league()
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
            league_id = league_data["league_id"]
            hash = create_matchup_hash(league_id, i, matchup_id, roster_id)

            # TODO - get season from league data before appending
            matchup["opponent_score"] = paired_matchup["points"]
            matchup["opponent_roster_id"] = paired_matchup["roster_id"]
            matchup["season"] = league_data["season"]
            matchup["league_id"] = league_id
            matchup["leg"] = i
            if i >= playoff_week_start:
                matchup["is_playoffs"] = True
            else:
                matchup["is_playoffs"] = False
            
            write(mongoClient, "matchups", {"_id": hash}, matchup)

def write_players(players, mongoClient):
    players = Players()
    all_players = players.get_all_players()
    players_list = list(players.values())
    for player in players_list:
        filter_query = { "player_id": player["player_id"] }
        write(mongoClient, 'players', filter_query, player)

def write_season(mongoClient, LeagueDataFetcher):
    league_data = LeagueDataFetcher.get_league()
    filter_query = {"league_id": league_data['league_id']}
    write(mongoClient, 'league', filter_query, league_data)