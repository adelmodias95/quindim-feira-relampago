from flask import Flask
from pymongo.errors import ConnectionFailure

from .db import db

app = Flask(__name__)


@app.route("/healthz")
def healthz():
    try:
        db.command("ping")
        return {"status": "ok"}, 200

    except ConnectionFailure:
        return {"status": "error"}, 503
