import os

from pymongo import MongoClient

CONNECTION_STRING = os.environ["MONGO_URL"]
DB_NAME = os.environ["MONGO_DB"]

client = MongoClient(CONNECTION_STRING, serverSelectionTimeoutMS=5000, tz_aware=True)
db = client[DB_NAME]


def criar_indices():
    db.pedidos.create_index({"reserva_id": 1}, unique=True)
