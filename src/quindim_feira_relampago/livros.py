from .db import db
from .reservas import expirar_vencidas


def buscar_livros():
    expirar_vencidas()

    livros_db = db.livros.find()
    catalogo = []

    for livro in livros_db:
        catalogo.append(
            {
                "sku": livro["_id"],
                "titulo": livro["titulo"],
                "preco_centavos": livro["preco_centavos"],
                "estoque": livro["estoque"],
                "disponivel": livro["disponivel"],
            }
        )

    return catalogo
