import json
import argparse
import inspect
from sleeper_wrapper import League, Drafts
from dotenv import load_dotenv
from mongo import connect, read, write
from commands import get_all_league_ids_in_mongo, get_highest_bids_of_all_time
from transforms import get_10g1c_leagueid_by_year, transform_transactions_to_human_readable, get_display_name_from_roster_id
from fetchers import get_transactions, get_leg
from writes import fetch_and_write_transactions, write_season
from utils import write_to_file

load_dotenv()

# TODO - backfill 2019 and previous - my data is missing this for some reason
# TODO - given a season and a roster id, figure out the display_name
# TODO - Calculate high scores of the week
# TODO - Add draft data
# TODO - How many (and which) players were both drafted and started by the championship team in the championship week?
def init():
    # league_data = LeagueDataFetcher.get_league()

    season = 2022

    parser = argparse.ArgumentParser(description="Sleeper pipeline ETL scripts and data utilities")

    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    parser_identify = subparsers.add_parser("identify", help="Identify a league member")
    parser_identify.add_argument("number", type=int, choices=range(1, 11), help="An integer between 1 and 10")

    parser_etl = subparsers.add_parser("etl", help="Perform some ETL")
    parser_etl.add_argument("action", type=str, choices=['draft', 'league'], help="Grab and load draft data")
    parser_etl.add_argument("season", type=int, help="The season (ex: 2022)")

    args = parser.parse_args()

    validActions = [
        "identify",
        "etl"
    ]

    print(f"Action: {args.command}")
    if args.command not in validActions:
        print('Action is not valid')
        raise

    if args.command == "identify":
        league_id = get_10g1c_leagueid_by_year(season)
        LeagueDataFetcher = League(league_id)
        print(get_display_name_from_roster_id(LeagueDataFetcher, args.number))
    if args.command == "etl":
        mongoClient = connect()
        if args.action == "league":
            league_id = get_10g1c_leagueid_by_year(args.season)
            LeagueDataFetcher = League(league_id)
            league_data = LeagueDataFetcher.get_league()
            write_season(mongoClient, league_data)
        if args.action == "draft":
            league_id = get_10g1c_leagueid_by_year(args.season)
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

# TODO - Can I check and log out if a transaction was updated vs inserted?
def upsert_missing_transactions(LeagueDataFetcher, mongoClient):
    league_data = LeagueDataFetcher.get_league()
    fromLeg = get_leg(league_data)
    toLeg = fromLeg - 2 # go back 2 weeks
    fetch_and_write_transactions(LeagueDataFetcher, mongoClient, fromLeg, toLeg)
        
init()