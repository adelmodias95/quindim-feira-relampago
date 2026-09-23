from .db import db


def buscar_livros():
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
