import argparse
from sleeper_wrapper import League
from dotenv import load_dotenv
from etl import write_draft_and_picks, fetch_and_write_transactions, fetch_and_push_matchups, write_season, write_players
from mongo import connect
from transforms import get_10g1c_leagueid_by_year, get_display_name_from_roster_id
from fetchers import get_leg, get_upper_and_lower_leg
from queries import get_scoring_array

load_dotenv()

# TODO - add season and leagueid to transactions
# TODO - backfill 2019 - my data is missing this for some reason
# TODO - backfill week 1 transactions and matchups
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
    parser_etl.add_argument("season", type=str, help="The season (ex: 2022)")
    parser_etl.add_argument("--h", type=int, help="High leg (when action will span multiple legs)")
    parser_etl.add_argument("--l", type=int, help="Low leg (when action will span multiple legs)")

    query_choices = ['time_to_1k']
    parser_query = subparsers.add_parser("query", help="make a query, answer a question")
    parser_query.add_argument("action", type=str, choices=query_choices, help="which query do you want to execute?")
    parser_query.add_argument("season", type=str, help="The season (ex: 2022)")

    args = parser.parse_args()

    validActions = [
        "identify",
        "etl",
        "query"
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
    elif args.command == "etl":
        MongoClient = connect()
        league_id = get_10g1c_leagueid_by_year(season)
        LeagueDataFetcher = League(league_id)
        if args.action == "league":
            write_season(LeagueDataFetcher, MongoClient)
        elif args.action == "transactions":
            # This is inefficient to fetch the league here and then do it again later when we pass LeagueDataFetcher
            # Is there a way to pass league_data if it's already been fetched or LeagueDataFetcher if not?
            legs = get_upper_and_lower_leg(LeagueDataFetcher.get_league())
            highLeg = args.h or legs[1]
            lowLeg = args.l or legs[0]
            fetch_and_write_transactions(LeagueDataFetcher, MongoClient, highLeg, lowLeg)
        elif args.action == "draft":
            write_draft_and_picks(LeagueDataFetcher, MongoClient, league_id)
        elif args.action == "matchups":
            fetch_and_push_matchups(LeagueDataFetcher, MongoClient)
        elif args.action == "players":
            write_players(MongoClient)
        else:
            print('ETL action: {} is not a valid action'.format(args.action))
            raise
    elif args.command == "query":
        if args.action == "time_to_1k":
           MongoClient = connect()
           get_scoring_array(MongoClient, args.season) 

# TODO - Can I check and log out if a transaction was updated vs inserted?
def upsert_missing_transactions(LeagueDataFetcher, mongoClient):
    league_data = LeagueDataFetcher.get_league()
    fromLeg = get_leg(league_data)
    toLeg = fromLeg - 2 # go back 2 weeks
    fetch_and_write_transactions(LeagueDataFetcher, mongoClient, fromLeg, toLeg)
        
init()