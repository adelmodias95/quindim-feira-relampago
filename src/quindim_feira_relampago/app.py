from flask import Flask, request
from pymongo.errors import ConnectionFailure

from .admin import resetar
from .db import criar_indices, db
from .erros import registrar_tratadores
from .livros import buscar_livros
from .pedidos import buscar_pedido, confirmar, pedido_para_json
from .reservas import ReservaEntrada, buscar, criar, para_json
from .seed import restaurar_catalogo

criar_indices()
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


@app.route("/v1/reservas/<reserva_id>/confirmar", methods=["POST"])
def confirmar_reserva(reserva_id):
    pedido, criado = confirmar(reserva_id)
    return pedido_para_json(pedido), 201 if criado else 200


@app.route("/v1/pedidos/<pedido_id>")
def obter_pedido(pedido_id):
    return pedido_para_json(buscar_pedido(pedido_id))


@app.route("/healthz")
def healthz():
    try:
        db.command("ping")
        return {"status": "ok"}, 200

    except ConnectionFailure:
        return {"status": "error"}, 503
