import json
import os
import urllib.error
import urllib.request

import pytest

BASE = os.getenv("API_URL", "http://localhost:8000")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "token-de-exemplo")


def requisitar(metodo, caminho, corpo=None, cabecalhos=None):
    """Chamada HTTP simples, só com a biblioteca padrão. Devolve (status, corpo)."""
    dados = json.dumps(corpo).encode() if corpo is not None else None
    pedido = urllib.request.Request(f"{BASE}{caminho}", data=dados, method=metodo)
    pedido.add_header("Content-Type", "application/json")

    for nome, valor in (cabecalhos or {}).items():
        pedido.add_header(nome, valor)

    try:
        with urllib.request.urlopen(pedido, timeout=15) as resposta:
            texto = resposta.read().decode()
            return resposta.status, json.loads(texto) if texto else None
    except urllib.error.HTTPError as erro:
        texto = erro.read().decode()
        return erro.code, json.loads(texto) if texto else None


@pytest.fixture
def api():
    """Zera o ambiente antes do cenário e devolve a função de requisição.

    Pula o teste, em vez de falhar, quando a API não está no ar — assim a suíte
    de unidade continua rodando sem o Docker.
    """
    try:
        status, _ = requisitar(
            "POST", "/v1/admin/reset", cabecalhos={"X-Admin-Token": ADMIN_TOKEN}
        )
    except OSError:
        pytest.skip(f"API não respondeu em {BASE}. Suba com 'docker compose up'.")

    if status != 204:
        pytest.skip(f"O reset devolveu {status}. Confira o ADMIN_TOKEN do .env.")

    return requisitar
