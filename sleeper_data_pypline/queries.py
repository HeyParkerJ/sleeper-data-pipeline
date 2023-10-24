from pymongo import DESCENDING
from mongo import read
from utils import write_to_file


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

def get_scoring_array(MongoClient, season):
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
        print('doing something for...', matchup["leg"], matchup["roster_id"])
        roster_id = matchup["roster_id"]
        if roster_id not in score_arrays:
            score_arrays[roster_id] = []

        score_arrays[roster_id].append(matchup["points"])

    print('score_arrays', score_arrays)
    total = 0
    for index, score in enumerate( score_arrays[6] ):
        total += score
        print('Week', index)
        print('Score:', score)
        print('Total:', total)

    # write_to_file(score_arrays, "demo_score_arrays.json")
    # scoreArrays = {}
    # for matchup in matchups:
    #     scoreArrays[matchup["roster_id"]]