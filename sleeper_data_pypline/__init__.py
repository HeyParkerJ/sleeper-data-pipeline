import json
from sleeper_wrapper import League
from dotenv import load_dotenv
from mongo import connect, read, write
from commands import get_all_league_ids_in_mongo, get_highest_bids_of_all_time
from transforms import get_10g1c_leagueid_by_year, transform_transactions_to_human_readable
from fetchers import get_transactions, get_leg
from writes import fetch_and_write_transactions

load_dotenv()

# TODO - Input all matchups into Mongodb
# TODO - Calculate high scores of the week
def init():
    season = 2023
    league_id = get_10g1c_leagueid_by_year(season)
    mongoClient = connect()
    LeagueDataFetcher = League(league_id)

    leg = 1
    matchups = LeagueDataFetcher.get_matchups(leg)

    for matchup in matchups:
        matchup_id = matchup["matchup_id"]
        roster_id = matchup["roster_id"]
        hash = create_matchup_hash(league_id, leg, matchup_id, roster_id)

        # TODO - get season from league data before appending
        matchup["season"] = season
        matchup["leg"] = leg
        write(mongoClient, "matchups", {"_id": hash}, matchup)

    # leg = 1
    # result = LeagueDataFetcher.get_matchups(leg)
    # print(json.dumps(result))
     
# I'm unsure if I want to hash on league_id or the year of the season...
# I need the league_id if I want to scale this to other leagues ever...
# Perhaps I can do both or add the season to the data object before inserting...
# Conclusion - let's add season to a transaction and leave it out of this fn
def create_matchup_hash(league_id, leg, matchup_id, roster_id):
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