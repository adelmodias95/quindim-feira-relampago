from concurrent.futures import ThreadPoolExecutor

SIMULTANEAS = 20


def reservar_uma_unidade(api, sku):
    return api(
        "POST",
        "/v1/reservas",
        {"cliente_id": "teste-rn04", "itens": [{"sku": sku, "quantidade": 1}]},
    )


def disponivel_de(api, sku):
    _, catalogo = api("GET", "/v1/livros")
    return next(
        livro["disponivel"] for livro in catalogo["livros"] if livro["sku"] == sku
    )


def test_a_ultima_unidade_vai_para_uma_requisicao_so(api):
    # QND-005 tem estoque 1 no seed: 20 clientes disputam a mesma unidade.
    with ThreadPoolExecutor(max_workers=SIMULTANEAS) as executor:
        respostas = list(
            executor.map(
                lambda _: reservar_uma_unidade(api, "QND-005"), range(SIMULTANEAS)
            )
        )

    status = [codigo for codigo, _ in respostas]

    assert status.count(201) == 1, f"mais de uma reserva foi criada: {status}"
    assert status.count(409) == SIMULTANEAS - 1
    assert disponivel_de(api, "QND-005") == 0


def test_estoque_de_tres_aceita_exatamente_tres(api):
    # QND-004 tem estoque 3. O disponível nunca pode ficar negativo (RN-04).
    with ThreadPoolExecutor(max_workers=SIMULTANEAS) as executor:
        respostas = list(
            executor.map(
                lambda _: reservar_uma_unidade(api, "QND-004"), range(SIMULTANEAS)
            )
        )

    status = [codigo for codigo, _ in respostas]

    assert status.count(201) == 3, f"número de reservas diferente do estoque: {status}"
    assert status.count(409) == SIMULTANEAS - 3
    assert disponivel_de(api, "QND-004") == 0
