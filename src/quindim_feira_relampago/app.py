from flask import Flask
from pymongo.errors import ConnectionFailure

from .db import db
from .erros import registrar_tratadores
from .livros import buscar_livros
from .seed import restaurar_catalogo

restaurar_catalogo()

app = Flask(__name__)

registrar_tratadores(app)


@app.route("/v1/livros")
def listar_livros():
    livros = buscar_livros()
    return {"livros": livros}


@app.route("/healthz")
def healthz():
    try:
        db.command("ping")
        return {"status": "ok"}, 200

    except ConnectionFailure:
        return {"status": "error"}, 503
