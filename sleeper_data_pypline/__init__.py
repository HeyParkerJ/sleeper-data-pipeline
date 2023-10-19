import json
from sleeper_wrapper import League
from dotenv import load_dotenv
from mongo import connect, read, write
from commands import get_all_league_ids_in_mongo, get_highest_bids_of_all_time
from transforms import get_10g1c_leagueid_by_year, transform_transactions_to_human_readable
from fetchers import get_transactions, get_leg, get_upper_and_lower_leg, get_playoff_week_start
from writes import fetch_and_write_transactions
from utils import write_to_file

load_dotenv()

# TODO - Calculate high scores of the week
def init():
    season = 2022
    league_id = get_10g1c_leagueid_by_year(season)
    mongoClient = connect()
    LeagueDataFetcher = League(league_id)
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

# TODO - Can I check and log out if a transaction was updated vs inserted?
def upsert_missing_transactions(LeagueDataFetcher, mongoClient):
    league_data = LeagueDataFetcher.get_league()
    fromLeg = get_leg(league_data)
    toLeg = fromLeg - 2 # go back 2 weeks
    fetch_and_write_transactions(LeagueDataFetcher, mongoClient, fromLeg, toLeg)
        
init()