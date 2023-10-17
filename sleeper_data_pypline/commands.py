from pymongo import DESCENDING
from mongo import read

# Probably won't need this... we just learned about upserting in mongo and will probably use that
def get_all_league_ids_in_mongo():
    def myfn(collection):
        cursor = collection.find({}, {'league_id': 1, '_id': 0})

        data_list = list(cursor)

        result = [doc['league_id'] for doc in data_list]

        return result


    return read('league', myfn) 

# TODO - this is more of a query than a organism level command
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
