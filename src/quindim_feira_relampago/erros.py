from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

CODIGOS_HTTP = {
    400: "requisicao_invalida",
    401: "nao_autorizado",
    404: "nao_encontrado",
    409: "estoque_insuficiente",
    410: "reserva_expirada",
}


class ErroDeNegocio(Exception):
    def __init__(self, status, codigo, mensagem, detalhes=None):
        super().__init__(mensagem)
        self.status = status
        self.codigo = codigo
        self.mensagem = mensagem
        self.detalhes = detalhes or {}


def _resposta(status, codigo, mensagem, detalhes=None):
    corpo = {
        "erro": {
            "codigo": codigo,
            "mensagem": mensagem,
            "detalhes": detalhes or {},
        }
    }
    return corpo, status


def registrar_tratadores(app):
    @app.errorhandler(ErroDeNegocio)
    def _de_negocio(erro):
        return _resposta(erro.status, erro.codigo, erro.mensagem, erro.detalhes)

    @app.errorhandler(HTTPException)
    def _http(erro):
        codigo = CODIGOS_HTTP.get(erro.code)
        if codigo is None:
            codigo = "requisicao_invalida" if erro.code < 500 else "erro_interno"
        return _resposta(erro.code, codigo, erro.description)

    @app.errorhandler(Exception)
    def _inesperado(erro):
        app.logger.exception("erro nao tratado")
        return _resposta(500, "erro_interno", "Erro interno.")

    @app.errorhandler(ValidationError)
    def _validacao(erro):
        return _resposta(
            400,
            "requisicao_invalida",
            "Corpo ou parâmetros fora do contrato.",
            {"campos": erro.errors(include_url=False, include_context=False)},
        )
