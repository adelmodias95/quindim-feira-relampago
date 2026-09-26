from itertools import combinations, product

from quindim_feira_relampago.precos import calcular_valores

CATALOGO = {
    "QND-001": 3990,
    "QND-002": 2990,
    "QND-003": 1995,
    "QND-004": 8990,
    "QND-005": 12900,
}

CAMPOS_DA_LINHA = {
    "sku",
    "quantidade",
    "preco_centavos",
    "valor_centavos",
    "desconto_centavos",
    "liquido_centavos",
}


def itens(*pares):
    return [
        {"sku": sku, "preco_centavos": CATALOGO[sku], "quantidade": q}
        for sku, q in pares
    ]


def test_exemplo_da_especificacao():
    # RN-08: uma unidade de cada, 3 unidades no total, 10% sobre 8975.
    resultado = calcular_valores(itens(("QND-001", 1), ("QND-002", 1), ("QND-003", 1)))

    assert resultado["subtotal_centavos"] == 8975
    assert resultado["desconto_centavos"] == 898
    assert resultado["total_centavos"] == 8077
    assert [linha["desconto_centavos"] for linha in resultado["linhas"]] == [
        399,
        299,
        200,
    ]
    assert [linha["liquido_centavos"] for linha in resultado["linhas"]] == [
        3591,
        2691,
        1795,
    ]


def test_ate_duas_unidades_nao_ha_desconto():
    resultado = calcular_valores(itens(("QND-001", 2)))

    assert resultado["desconto_centavos"] == 0
    assert resultado["total_centavos"] == resultado["subtotal_centavos"]


def test_meio_centavo_sobe():
    # 3 x 1995 = 5985; 10% dá 598,5 centavos. O arredondamento comercial sobe para 599.
    # O round() do Python, que é bancário, devolveria 598.
    assert calcular_valores(itens(("QND-003", 3)))["desconto_centavos"] == 599


def test_a_faixa_conta_unidades_e_nao_linhas():
    # Duas linhas, 5 unidades no total: entra na faixa de 15%.
    resultado = calcular_valores(itens(("QND-001", 3), ("QND-002", 2)))

    assert resultado["subtotal_centavos"] == 17950
    assert resultado["desconto_centavos"] == 2693


def test_empate_no_resto_vai_para_a_primeira_linha():
    resultado = calcular_valores(
        [
            {"sku": "PRIMEIRA", "preco_centavos": 333, "quantidade": 2},
            {"sku": "SEGUNDA", "preco_centavos": 333, "quantidade": 2},
        ]
    )

    assert [linha["desconto_centavos"] for linha in resultado["linhas"]] == [67, 66]
    assert resultado["desconto_centavos"] == 133


def test_a_lista_recebida_nao_e_alterada():
    entrada = itens(("QND-001", 1), ("QND-003", 2))
    copia = [dict(item) for item in entrada]

    calcular_valores(entrada)

    assert entrada == copia


def test_cada_linha_tem_exatamente_os_campos_do_contrato():
    resultado = calcular_valores(itens(("QND-001", 2), ("QND-002", 1)))

    for linha in resultado["linhas"]:
        assert set(linha) == CAMPOS_DA_LINHA


def combinacoes_do_catalogo():
    for tamanho in range(1, len(CATALOGO) + 1):
        for skus in combinations(CATALOGO, tamanho):
            for quantidades in product((1, 2, 3), repeat=tamanho):
                yield list(zip(skus, quantidades))


def test_a_soma_das_linhas_bate_em_todas_as_combinacoes():
    # A RN-08 exige que a soma dos descontos das linhas seja exatamente o desconto
    # total. Um exemplo não prova isso: aqui vão as 1023 combinações do catálogo.
    total = 0

    for combinacao in combinacoes_do_catalogo():
        resultado = calcular_valores(itens(*combinacao))
        soma_descontos = sum(
            linha["desconto_centavos"] for linha in resultado["linhas"]
        )
        soma_liquidos = sum(linha["liquido_centavos"] for linha in resultado["linhas"])

        assert soma_descontos == resultado["desconto_centavos"], combinacao
        assert soma_liquidos == resultado["total_centavos"], combinacao
        total += 1

    assert total == 1023


def test_nenhum_valor_e_float():
    # RN-01: dinheiro é sempre inteiro em centavos.
    resultado = calcular_valores(itens(("QND-003", 3), ("QND-004", 1)))

    for chave in ("subtotal_centavos", "desconto_centavos", "total_centavos"):
        assert type(resultado[chave]) is int

    for linha in resultado["linhas"]:
        for chave in CAMPOS_DA_LINHA - {"sku"}:
            assert type(linha[chave]) is int
