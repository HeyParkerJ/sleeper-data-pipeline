from pymongo.mongo_client import MongoClient
import os

def connect():
    """
    Returns a mongo client
    """
    password = os.getenv("MONGO_PASSWORD")
    uri = f"mongodb+srv://parker:{password}@sleeper.lnapcdq.mongodb.net/?retryWrites=true&w=majority"

    client = MongoClient(uri)
    # Send a ping to confirm a successful connection
    print("Pinging our deployment")
    try:
        client.admin.command('ping')
        print("We are a go!")
    except Exception as e:
        print(e)

    return client

def ping(client):
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

def read (client, collection_name, fn):
    db = client["sleeper"]
    collection = db[collection_name]

    try:
        return fn(collection)
    except Exception as e:
        print(e)


def write (client, collectionName, filter_query, data):
    db = client["sleeper"]
    collection = db[collectionName]

    try:
        collection.update_one(filter_query, {"$set": data}, upsert=True)
        print('Wrote transaction_id', filter_query)
    except Exception as e:
        print('Exception on', filter_query)
        print(e)
