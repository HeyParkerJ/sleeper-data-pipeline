from pymongo.mongo_client import MongoClient
import json
import os

# Returns a mongo_client
def connect():
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


def ping ():
    password = os.getenv("MONGO_PASSWORD")
    uri = f"mongodb+srv://parker:{password}@sleeper.lnapcdq.mongodb.net/?retryWrites=true&w=majority"
    # Create a new client and connect to the server
    client = MongoClient(uri)
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

def read (collection_name, fn):
    password = os.getenv("MONGO_PASSWORD")
    uri = f"mongodb+srv://parker:{password}@sleeper.lnapcdq.mongodb.net/?retryWrites=true&w=majority"
    # Create a new client and connect to the server
    client = MongoClient(uri)
    db = client["sleeper"]
    collection = db[collection_name]

    try:
        return fn(collection)
    except Exception as e:
        print(e)


def write (client, collectionName, filter_query, data):
    db = client["sleeper"]
    collection = db[collectionName]

    # We can now do a collection.insert_one
    try:
        # Implement here
        collection.update_one(filter_query, {"$set": data}, upsert=True)
        print('Wrote transaction_id', filter_query)
    except Exception as e:
        print('Exception on', filter_query)
        print(e)
