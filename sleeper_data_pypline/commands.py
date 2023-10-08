import requests
from mongo import write, read
from sleeper_wrapper import League

# Probably won't need this... we just learned about upserting in mongo and will probably use that
def get_all_league_ids_in_mongo():
    def myfn(collection):
        cursor = collection.find({}, {'league_id': 1, '_id': 0})

        data_list = list(cursor)

        result = [doc['league_id'] for doc in data_list]

        return result


    return read('league', myfn)
