from pymongo import DESCENDING
from mongo import read
from utils import write_to_file
from transforms import get_display_name_from_roster_id


def get_highest_bids_of_all_time(amount_of_bids):
    def readFn(collection):
        documents = []
        query = {"status": "complete"}
        cursor = collection.find(query).sort('settings.waiver_bid', DESCENDING).limit(amount_of_bids)
        # Note - prob don't need to take docs out of cursor then append to a new list, can refactor
        for document in cursor:
            documents.append(document)

        return documents

    result = read('transactions', readFn)
    return result

def get_scoring_array_and_calculate_week_of_1k_points(LeagueDataFetcher, MongoClient, season):
    """
    For each season (ex: query for season: 2023, 2022, etc)
    Start at leg 1 and count up
    For each match in the leg
    assign to a dict like this:
    {
        roster_id: [125, 130, 156, etc]
    }
    """
    def readFn(collection):
        documents = []
        query = {"season": season}
        cursor = collection.find(query).sort('leg')
        for document in cursor:
            documents.append(document)
        return documents

    matchups = read(MongoClient, "matchups", readFn)

    score_arrays = {}
    for matchup in matchups:
        roster_id = matchup["roster_id"]
        if roster_id not in score_arrays:
            score_arrays[roster_id] = {"scores": [], "total": 0}

        score_arrays[roster_id]["scores"].append(matchup["points"])
        score_arrays[roster_id]["total"] += matchup["points"]

        if score_arrays[roster_id]["total"] > 1000 and "week_to_hit_1k" not in score_arrays[roster_id]:
            score_arrays[roster_id]["week_to_hit_1k"] = matchup["leg"]


    rosters = LeagueDataFetcher.get_rosters()
    users = LeagueDataFetcher.get_users()

    result = {}
    for key in score_arrays:
        name = get_display_name_from_roster_id(rosters, users, key)    
        result[name] = score_arrays[key]

    return result