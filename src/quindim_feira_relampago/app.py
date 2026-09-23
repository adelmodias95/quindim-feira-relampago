from flask import Flask, request
from pymongo.errors import ConnectionFailure

from .admin import resetar
from .db import db
from .erros import registrar_tratadores
from .livros import buscar_livros
from .reservas import ReservaEntrada, buscar, criar, para_json
from .seed import restaurar_catalogo

restaurar_catalogo()

app = Flask(__name__)

registrar_tratadores(app)


@app.route("/v1/admin/reset", methods=["POST"])
def resetar_ambiente():
    resetar(request.headers.get("X-Admin-Token"))
    return "", 204


@app.route("/v1/livros")
def listar_livros():
    livros = buscar_livros()
    return {"livros": livros}


@app.route("/v1/reservas", methods=["POST"])
def criar_reserva():
    entrada = ReservaEntrada(**request.get_json())
    reserva = criar(entrada)
    return para_json(reserva), 201


@app.route("/v1/reservas/<reserva_id>")
def obter_reserva(reserva_id):
    return para_json(buscar(reserva_id))


@app.route("/healthz")
def healthz():
    try:
        db.command("ping")
        return {"status": "ok"}, 200

    except ConnectionFailure:
        return {"status": "error"}, 503
