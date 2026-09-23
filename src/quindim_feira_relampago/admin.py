import os
import secrets

from .db import db
from .erros import ErroDeNegocio
from .seed import restaurar_catalogo

ADMIN_TOKEN = os.environ["ADMIN_TOKEN"]


def resetar(token):
    if token is None or not secrets.compare_digest(
        token.encode(), ADMIN_TOKEN.encode()
    ):
        raise ErroDeNegocio(
            401, "nao_autorizado", "Token de administrador ausente ou inválido."
        )

    db.reservas.delete_many({})
    db.pedidos.delete_many({})
    db.eventos.delete_many({})
    restaurar_catalogo()
