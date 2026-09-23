import os

from pymongo import MongoClient

CONNECTION_STRING = os.environ["MONGO_URL"]
DB_NAME = os.environ["MONGO_DB"]

client = MongoClient(CONNECTION_STRING, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]
