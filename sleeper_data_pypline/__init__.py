from pymongo import DESCENDING
from sleeper_wrapper import League
from dotenv import load_dotenv
from mongo import connect, read
from commands import get_all_league_ids_in_mongo
from transforms import get_10g1c_leagueid_by_year

load_dotenv()

# TODO - Dex bid 52 on Ford this year and it's not coming up in my queries
def init():
    mongoClient = connect()

    season = 2023
    LeagueDataFetcher = League(get_10g1c_leagueid_by_year(season))
     
def upsert_missing_transactions():
    # This fn will essentially grab the last 2 legs of
    # transactions and upsert them. We can eventually 
    # get this to run daily or so
    print('implement me!')

init()