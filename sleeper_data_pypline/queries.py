from pymongo import DESCENDING
from mongo import read


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
