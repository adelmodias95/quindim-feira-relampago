# Notas

## Decisões

- Utilizar uv em vez de Poetry, porque o uv instala a própria versão do Python dentro do projeto, ao invés de usar a instalação global do Python. Escolhi por indicação de um agente de IA. Vou entender as diferenças na prática conforme for desenvolvendo o projeto.

## Diário

### 21/09 — dia 1

- Li a especificação algumas vezes para entender o problema
- Repositório criado
- Nunca desenvolvi API em Python e MongoDB, então será um desafio para mim.
- Instalação do uv via site oficial. Utilizei a opção de instalar via Homebrew.
- Inicialização do projeto com uv e instalação das dependências necessárias.
- Criação do arquivo app.py para a primeira rota API, seguindo a documentação do Flask.
- Instalação do python3 e Flask globalmente. Execução do app.py com python3: `python3 -m flask --app app run`.
- Execução da primeira rota utilizando uv para que ele utilize o ambiente do projeto. `uv run flask --app quindim_feira_relampago.app run --port 8000 --debug`.

#### Fontes de estudo dia 1:

- [Poetry vs UV](https://medium.com/@hitorunajp/poetry-vs-uv-which-python-package-manager-should-you-use-in-2025-4212cb5e0a14)
- [API com Flask](https://youtu.be/LP8besicfH4?si=yL0nJryUk5ybsNot)
- [uv - Getting Started](https://docs.astral.sh/uv/getting-started/installation/)
- [Flask - Quickstart](https://flask.palletsprojects.com/en/stable/quickstart/#)
- [Flask - API With JSON](https://flask.palletsprojects.com/en/stable/quickstart/#apis-with-json)
