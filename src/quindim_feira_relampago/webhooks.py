import hashlib
import hmac
import os
from datetime import datetime
from typing import Literal

from bson.errors import InvalidId
from bson.objectid import ObjectId
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError

from .db import db
from .erros import ErroDeNegocio
from .reservas import devolver

SECRET = os.environ["WEBHOOK_SEGREDO"]


class Evento(BaseModel):
    evento_id: str
    pedido_id: str
    tipo: Literal["pago", "recusado"]
    ocorrido_em: datetime


def _assinatura_valida(corpo, assinatura):
    if assinatura is None:
        return False

    esperada = hmac.new(SECRET.encode(), corpo, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperada, assinatura)


def processar_webhook(corpo_cru, assinatura):
    if not _assinatura_valida(corpo_cru, assinatura):
        raise ErroDeNegocio(401, "nao_autorizado", "Assinatura ausente ou inválida.")

    evento = Evento.model_validate_json(corpo_cru)

    try:
        db.eventos.insert_one(evento.model_dump())
    except DuplicateKeyError:
        return

    try:
        pedido_id = ObjectId(evento.pedido_id)
    except InvalidId:
        return

    if evento.tipo == "pago":
        db.pedidos.update_one(
            {"_id": pedido_id, "status": "aguardando_pagamento"},
            {"$set": {"status": "pago", "pago_em": evento.ocorrido_em}},
        )
        return

    pedido = db.pedidos.find_one({"_id": pedido_id})
    if pedido is None:
        return
    resultado = db.pedidos.update_one(
        {"_id": pedido_id, "status": "aguardando_pagamento"},
        {"$set": {"status": "cancelado"}},
    )
    if resultado.modified_count == 1:
        for linha in pedido["linhas"]:
            devolver(linha["sku"], linha["quantidade"])
    return
