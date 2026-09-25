from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

from .db import db
from .erros import ErroDeNegocio
from .reservas import buscar, iso_z
from .precos import calcular_valores


def confirmar(reserva_id: str):
    reserva = buscar(reserva_id)
    if reserva["status"] == "expirada":
        raise ErroDeNegocio(
            410, "reserva_expirada", "A reserva já expirou e não pode ser confirmada."
        )

    valores = calcular_valores(reserva["itens"])

    pedido = {
        "reserva_id": reserva["_id"],
        "cliente_id": reserva["cliente_id"],
        "status": "aguardando_pagamento",
        "linhas": valores["linhas"],
        "subtotal_centavos": valores["subtotal_centavos"],
        "desconto_centavos": valores["desconto_centavos"],
        "total_centavos": valores["total_centavos"],
        "criado_em": datetime.now(timezone.utc).replace(microsecond=0),
        "pago_em": None,
    }

    try:
        resultado = db.pedidos.insert_one(pedido)
    except DuplicateKeyError:
        return db.pedidos.find_one({"reserva_id": reserva["_id"]}), False

    pedido["_id"] = resultado.inserted_id
    db.reservas.update_one(
        {"_id": reserva["_id"], "status": "ativa"},
        {"$set": {"status": "confirmada"}},
    )
    return pedido, True


def buscar_pedido(pedido_id):
    try:
        identificador = ObjectId(pedido_id)
    except InvalidId:
        raise ErroDeNegocio(404, "nao_encontrado", "Pedido não encontrado.") from None

    pedido = db.pedidos.find_one({"_id": identificador})
    if pedido is None:
        raise ErroDeNegocio(404, "nao_encontrado", "Pedido não encontrado.")

    return pedido


def pedido_para_json(pedido):
    return {
        "id": str(pedido["_id"]),
        "reserva_id": str(pedido["reserva_id"]),
        "cliente_id": pedido["cliente_id"],
        "status": pedido["status"],
        "linhas": pedido["linhas"],
        "subtotal_centavos": pedido["subtotal_centavos"],
        "desconto_centavos": pedido["desconto_centavos"],
        "total_centavos": pedido["total_centavos"],
        "criado_em": iso_z(pedido["criado_em"]),
        "pago_em": iso_z(pedido["pago_em"]) if pedido["pago_em"] else None,
    }
