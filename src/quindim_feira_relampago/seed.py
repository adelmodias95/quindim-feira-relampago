from pymongo import ReplaceOne

from .db import db

CATALOGO = [
    {
        "_id": "QND-001",
        "titulo": "O Jardim de Dentro",
        "preco_centavos": 3990,
        "estoque": 10,
    },
    {
        "_id": "QND-002",
        "titulo": "Bicho-Palavra",
        "preco_centavos": 2990,
        "estoque": 10,
    },
    {
        "_id": "QND-003",
        "titulo": "A Casa que Anda",
        "preco_centavos": 1995,
        "estoque": 10,
    },
    {
        "_id": "QND-004",
        "titulo": "Kit Primeira Leitura",
        "preco_centavos": 8990,
        "estoque": 3,
    },
    {
        "_id": "QND-005",
        "titulo": "A Lua no Bolso — edição numerada",
        "preco_centavos": 12900,
        "estoque": 1,
    },
]


def restaurar_catalogo():
    db.livros.bulk_write(
        [
            ReplaceOne(
                {"_id": livro["_id"]},
                {**livro, "disponivel": livro["estoque"]},
                upsert=True,
            )
            for livro in CATALOGO
        ]
    )
