def calcular_valores(itens):
    subtotal_centavos = 0
    unidades = 0

    for item in itens:
        subtotal_centavos += item["preco_centavos"] * item["quantidade"]
        unidades += item["quantidade"]

    if unidades <= 2:
        percentual = 0
    elif unidades <= 4:
        percentual = 10
    else:
        percentual = 15

    desconto_centavos = (percentual * subtotal_centavos + 50) // 100

    linhas = []
    soma_das_cotas = 0

    for item in itens:
        valor_centavos = item["preco_centavos"] * item["quantidade"]
        proporcao = valor_centavos * desconto_centavos
        cota = proporcao // subtotal_centavos
        soma_das_cotas += cota

        linhas.append(
            {
                "sku": item["sku"],
                "quantidade": item["quantidade"],
                "preco_centavos": item["preco_centavos"],
                "valor_centavos": valor_centavos,
                "desconto_centavos": cota,
                "resto": proporcao % subtotal_centavos,
            }
        )

    sobra = desconto_centavos - soma_das_cotas
    por_maior_resto = sorted(linhas, key=lambda linha: linha["resto"], reverse=True)

    for linha in por_maior_resto[:sobra]:
        linha["desconto_centavos"] += 1

    for linha in linhas:
        linha["liquido_centavos"] = linha["valor_centavos"] - linha["desconto_centavos"]
        del linha["resto"]

    return {
        "linhas": linhas,
        "subtotal_centavos": subtotal_centavos,
        "desconto_centavos": desconto_centavos,
        "total_centavos": subtotal_centavos - desconto_centavos,
    }
