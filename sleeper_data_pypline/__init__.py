import json
import argparse
import inspect
from sleeper_wrapper import League
from dotenv import load_dotenv
from etl import write_draft, fetch_and_write_transactions, fetch_and_push_matchups, write_season, write_players
from mongo import connect
from transforms import get_10g1c_leagueid_by_year, get_display_name_from_roster_id
from fetchers import get_leg

load_dotenv()

# TODO - backfill 2019 - my data is missing this for some reason
# TODO - redo the draft insertions, but add season to the payload
# TODO - given a season and a roster id, figure out the display_name
# TODO - Calculate high scores of the week
# TODO - How many (and which) players were both drafted and started by the championship team in the championship week?
def init():
    parser = argparse.ArgumentParser(description="Sleeper pipeline ETL scripts and data utilities")

    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    parser_identify = subparsers.add_parser("identify", help="Identify a league member")
    parser_identify.add_argument("number", type=int, choices=range(1, 11), help="An integer between 1 and 10")

    etl_choices = ['draft', 'league', 'transactions', 'matchups', 'players']

    parser_etl = subparsers.add_parser("etl", help="Grab data for a season, upsert it into mongo")
    parser_etl.add_argument("action", type=str, choices=etl_choices, help="Grab and load draft data")
    parser_etl.add_argument("season", type=int, help="The season (ex: 2022)")

    args = parser.parse_args()

    validActions = [
        "identify",
        "etl"
    ]

    season = args.season

    print(f"Action: {args.command}")
    if args.command not in validActions:
        print('Action is not valid')
        raise
    
    if args.command == "identify":
        league_id = get_10g1c_leagueid_by_year(season)
        LeagueDataFetcher = League(league_id)
        print(get_display_name_from_roster_id(LeagueDataFetcher, args.number))
    if args.command == "etl":
        MongoClient = connect()
        league_id = get_10g1c_leagueid_by_year(season)
        LeagueDataFetcher = League(league_id)
        if args.action == "league":
            write_season(LeagueDataFetcher, MongoClient)
        if args.action == "transactions":
            highLeg = 17
            lowLeg = 0
            fetch_and_write_transactions(LeagueDataFetcher, MongoClient, highLeg, lowLeg)
        if args.action == "draft":
            write_draft(LeagueDataFetcher, MongoClient, league_id)
        if args.action == "matchups":
            fetch_and_push_matchups(LeagueDataFetcher, MongoClient)
        if args.action == "players":
            write_players(MongoClient)
        else:
            print('ETL action: {} is not a valid action'.format(args.action))
            raise

# TODO - Can I check and log out if a transaction was updated vs inserted?
def upsert_missing_transactions(LeagueDataFetcher, mongoClient):
    league_data = LeagueDataFetcher.get_league()
    fromLeg = get_leg(league_data)
    toLeg = fromLeg - 2 # go back 2 weeks
    fetch_and_write_transactions(LeagueDataFetcher, mongoClient, fromLeg, toLeg)
        
init()