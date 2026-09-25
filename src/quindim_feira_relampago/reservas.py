import os
from datetime import datetime, timedelta, timezone

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, Field, field_validator

from .db import db
from .erros import ErroDeNegocio

RESERVA_TTL_SEGUNDOS = int(os.environ["RESERVA_TTL_SEGUNDOS"])


class ItemEntrada(BaseModel):
    sku: str
    quantidade: int = Field(ge=1, le=3)


class ReservaEntrada(BaseModel):
    cliente_id: str = Field(min_length=1)
    itens: list[ItemEntrada] = Field(min_length=1)

    @field_validator("itens")
    @classmethod
    def _sem_sku_repetido(cls, itens):
        skus = [item.sku for item in itens]
        if len(skus) != len(set(skus)):
            raise ValueError("cada SKU pode aparecer apenas uma vez na reserva")
        return itens


def _descontar(sku, quantidade):
    resultado = db.livros.update_one(
        {"_id": sku, "disponivel": {"$gte": quantidade}},
        {"$inc": {"disponivel": -quantidade}},
    )
    return resultado.modified_count == 1


def _devolver(sku, quantidade):
    db.livros.update_one({"_id": sku}, {"$inc": {"disponivel": quantidade}})


def _expirar_reserva(reserva):
    resultado = db.reservas.update_one(
        {
            "_id": reserva["_id"],
            "status": "ativa",
            "expira_em": {"$lte": datetime.now(timezone.utc)},
        },
        {"$set": {"status": "expirada"}},
    )

    if resultado.modified_count == 1:
        for item in reserva["itens"]:
            _devolver(item["sku"], item["quantidade"])
        return True
    return False


def expirar_vencidas(skus=None):
    filtro = {
        "status": "ativa",
        "expira_em": {"$lte": datetime.now(timezone.utc)},
    }
    if skus:
        filtro["itens.sku"] = {"$in": skus}

    for reserva in db.reservas.find(filtro):
        _expirar_reserva(reserva)


def iso_z(momento):
    return momento.isoformat().replace("+00:00", "Z")


def criar(entrada):
    descontados = []
    faltantes = []

    skus = [item.sku for item in entrada.itens]
    expirar_vencidas(skus)

    for item in entrada.itens:
        if _descontar(item.sku, item.quantidade):
            descontados.append(item)
        else:
            faltantes.append(item.sku)

    if faltantes:
        for item in descontados:
            _devolver(item.sku, item.quantidade)
        raise ErroDeNegocio(
            409,
            "estoque_insuficiente",
            "Não há unidades suficientes para um ou mais SKUs.",
            {"skus": faltantes},
        )

    precos = {
        livro["_id"]: livro["preco_centavos"]
        for livro in db.livros.find({"_id": {"$in": skus}})
    }

    criado_em = datetime.now(timezone.utc).replace(microsecond=0)
    reserva = {
        "cliente_id": entrada.cliente_id,
        "status": "ativa",
        "itens": [
            {
                "sku": item.sku,
                "quantidade": item.quantidade,
                "preco_centavos": precos[item.sku],
            }
            for item in entrada.itens
        ],
        "criado_em": criado_em,
        "expira_em": criado_em + timedelta(seconds=RESERVA_TTL_SEGUNDOS),
    }

    resultado = db.reservas.insert_one(reserva)
    reserva["_id"] = resultado.inserted_id
    return reserva


def buscar(reserva_id):
    try:
        identificador = ObjectId(reserva_id)
    except InvalidId:
        raise ErroDeNegocio(404, "nao_encontrado", "Reserva não encontrada.") from None

    reserva = db.reservas.find_one({"_id": identificador})
    if reserva is None:
        raise ErroDeNegocio(404, "nao_encontrado", "Reserva não encontrada.")

    expirado = _expirar_reserva(reserva)

    if expirado:
        reserva = db.reservas.find_one({"_id": identificador})

    return reserva


def para_json(reserva):
    return {
        "id": str(reserva["_id"]),
        "cliente_id": reserva["cliente_id"],
        "status": reserva["status"],
        "itens": [
            {
                "sku": item["sku"],
                "quantidade": item["quantidade"],
                "preco_centavos": item["preco_centavos"],
            }
            for item in reserva["itens"]
        ],
        "criado_em": iso_z(reserva["criado_em"]),
        "expira_em": iso_z(reserva["expira_em"]),
    }
