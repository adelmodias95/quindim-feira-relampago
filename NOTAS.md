# Notas

## Decisões

- 21/09: Utilizar uv em vez de Poetry, porque o uv instala a própria versão do Python dentro do projeto, ao invés de usar a instalação global do Python. Escolhi por indicação de um agente de IA. Vou entender as diferenças na prática conforme for desenvolvendo o projeto.
- 22/09: Utilizar a versão 8.2 da imagem do Mongo. A spec pede mongo:8 mas hoje, ela é resolvida para a série 8.3.x, que introduziu uma verificação que recusa iniciar em kernel Linux 6.19 ou mais novo. A VM que o Docker Desktop roda no meu Mac tem um kernel nessa faixa. O Agente de IA me ajudou a entender e resolver esse problema após eu tentar iniciar o container do mongo db no docker. Print do erro: [https://i.imgur.com/KXJ7yKp.png](https://i.imgur.com/KXJ7yKp.png) [Fonte 1](https://github.com/Sorcha-Platform/Sorcha/issues/1652) / [Fonte 2](https://github.com/bluewave-labs/Checkmate/issues/3842) / [Fonte 3](https://community.graylog.org/t/mongodb-cannot-start-linux-kernel-versions-6-19-and-newer-has-a-known-incompatibility/37373/4)
- 22/09: Aguardar 5 segundos para que a conexão ao Mongo via pymongo seja declarada como erro. Por padrão o pymongo e o gunicorn aguardam 30 segundos, mas o gunicorn vencia a corrida e matava o worker, dessa forma exibia a tela de erro padrão do Flask com a mensagem "Internal Server Error". Agora a API retorna uma resposta JSON no caso de sucesso ou erro.
- 23/09: O seed restaura o catálogo com `ReplaceOne` e `upsert=True` em vez de apagar tudo e inserir. Como a função roda na importação do módulo, os 4 workers do gunicorn a executam quase ao mesmo tempo. Um seed do tipo "apaga e insere" abriria uma janela com o catálogo vazio e faria o segundo worker tomar `DuplicateKeyError`. Sendo idempotente, rodar uma ou quatro vezes deixa o banco no mesmo estado, e a concorrência deixa de importar. A mesma função é reaproveitada pelo `POST /v1/admin/reset`.
- 23/09: Decidi mapear qualquer 4xx não previsto para `requisicao_invalida` e qualquer 5xx para `erro_interno`.
- 23/09: Recuso com 400 `requisicao_invalida` qualquer reserva que repita o mesmo SKU em mais de uma linha. Encontrei esse problema na revisão. Uma req com `[{QND-001, 2}, {QND-001, 2}]` passava, porque cada linha respeitava o máximo de 3, e gerava dois descontos independentes, violando a RN-03. Preferi recusar em vez de somar as linhas repetidas.


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



### 22/09 - dia 2

- Estudo sobre Gunicorn e WSGI. Criei um projeto a parte para iniciar uma aplicação básica com uv gerenciando dependências e ambiente, Gunicorn responsável pelo servidor e Flask para as rotas.
- Criei o Dockerfile e o .dockerignore, construí a imagem com `docker build` e subi um container a partir dela com `docker run`. Agora tenho a rota /healthz como resultado em [http://localhost:8000/healthz](http://localhost:8000/healthz), sendo servida pelo gunicorn dentro do container do Docker, não mais pelo servidor de desenvolvimento do Flask. No momento de criar o Dockerfile, o agente de IA preencheu as flags depois que eu travei, e eu descobri depois que estavam no guia Docker do uv e no --help do gunicorn.
- .env.example: conexão com o banco, TTL da reserva, token do admin, segredo do webhook. Mantive a URL do MongoDB sem usuário e senha para subir a imagem sem autenticação, também mantive  o host como `mongo` e não `localhost` porque dentro da rede do Compose, um serviço chama o outro pelo nome do serviço.
- docker-compose.yml: sobe dois serviços, o banco de dados e a api, mas existe uma condição para a API subir, e é que o banco esteja aceitando conexões. Isso é definido em `condition: service_healthy`. Essa condição funcionou na primeira subida onde o mongo db não iniciou por incompatibilidade com o kernel do meu Docker.
- Criação da conexão Python>Mongo com pymongo. O arquivo db.py possui a conexão com o banco de dados e utiliza as variáveis de ambiente declaradas no .env.
- app.py agora importa a conexão com o banco de dados e faz uma verificação de saúde utilizando o comando `ping` do Mongo. Se a conexão falhar e o banco estiver indisponível, por enquanto, retorna apenas `{"status": "error"}` com código 503.
- Ruff: Utilizei o Ruff pela primeira vez com o comando `uv run ruff check .`, ele me retornou alguns avisos e eu corrigi todos até receber a mensagem `All checks passed!`.



#### Fontes de estudo dia 2:

- [Servidor WSGI e Gunicorn](https://www.youtube.com/watch?v=lQgiEylR49c)
- [Documentação Gunicorn](https://gunicorn.org/quickstart/)
- [Docker Compose Services](https://docs.docker.com/reference/compose-file/services/)
- [Using uv in Docker](https://docs.astral.sh/uv/guides/integration/docker/#using-uv-in-docker)
- [PyMongo](https://pymongo.readthedocs.io/en/stable/api/pymongo/index.html)
- [pymongo.errors.ConnectionFailure](https://pymongo.readthedocs.io/en/stable/api/pymongo/errors.html#pymongo.errors.ConnectionFailure)
- [Database Commands](https://www.mongodb.com/pt-br/docs/manual/reference/command/ping/)
- [The Ruff Linter](https://docs.astral.sh/ruff/linter/)



### 23/09 — dia 3

- O `seed.py` foi escrito pelo agente de IA e eu revisei linha a linha antes de rodar. O `_id` de cada livro é o próprio SKU, e o `disponivel` nasce igual ao `estoque`. O seed usa `bulk_write` com `ReplaceOne` e `upsert=True`, em vez de apagar tudo e inserir. Com 4 workers do gunicorn importando o mesmo módulo, a função roda quatro vezes quase ao mesmo tempo.
- O arquivo `livros.py` e a rota `GET /v1/livros` eu escrevi, e o agente de IA revisou. O módulo busca no banco e monta o JSON que é retornado na rota `{"livros": [...]}`.
- O `erros.py` foi escrito pelo agente de IA e eu revisei. Ele centraliza o tratamento de erro: as rotas passam a levantar exceção, e um lugar só monta a mensagem `{"erro": {"codigo", "mensagem", "detalhes"}}`. São três tratadores registrados no `app` — um para o `ErroDeNegocio`, exceção minha que carrega status, código, mensagem e detalhes, um para `HTTPException`, que pega os erros do próprio Flask, e um para `Exception`, rede de segurança que devolve 500 em JSON e manda o traceback para o log em vez da resposta.
- Entendi que `@app.errorhandler` e `@app.route` funcionam do mesmo jeito, rodam uma vez na importação e só registram a função dentro do objeto `app`. Quem executa é o Flask a cada requisição.
- O `admin.py` com a rota `POST /v1/admin/reset` foi escrito pelo agente de IA, e eu revisei linha a linha e testei. Ele confere o cabeçalho `X-Admin-Token` contra a variável de ambiente, apaga reservas, pedidos e eventos, e reaproveita o `restaurar_catalogo()` do seed.
- Escrevi o `reservas.py`, comecei escrevendo os modelos de entrada com Pydantic, `ItemEntrada` com o limite de 1 a 3 unidades e `ReservaEntrada` exigindo pelo menos um item.
- Precisei acrescentar `tz_aware=True` no `MongoClient`. Sem isso o pymongo devolve as datas sem fuso ao ler do banco, o `isoformat()` não produz o `+00:00` que eu troco por `Z`, e comparar data com fuso e data sem fuso levanta `TypeError` em Python — o que quebraria a expiração.
- Escrevi o `GET /v1/reservas/{id}`
- Fechei o dia corrigindo o problema que apareceu na revisão, o mesmo SKU repetido em duas linhas do pedido passava pela validação e gerava dois descontos, burlando o limite de 3 por reserva. Resolvi com um `field_validator` do Pydantic sobre a lista de itens, que levanta `ValueError` quando há SKU repetido.

#### Fontes de estudo dia 3:

- [Mongo.bulkWrite()](https://www.mongodb.com/pt-br/docs/manual/reference/method/mongo.bulkwrite/#mongodb-method-Mongo.bulkWrite)
- [Serialize and deserialize MongoDB documents in Python using PyMongo](https://oneuptime.com/blog/post/2026-03-31-mongodb-serialize-deserialize-documents-python/view)
- [Append to JSON file using Python](https://www.geeksforgeeks.org/python/append-to-json-file-using-python/)
- [Handling Application Errors](https://flask.palletsprojects.com/en/stable/errorhandling/)
- [Werkzeug HTTP Exceptions](https://werkzeug.palletsprojects.com/en/stable/exceptions/)
- [Pydantic Field](https://pydantic.dev/docs/validation/dev/concepts/fields/)
- [Pydantic Error Handling](https://pydantic.dev/docs/validation/latest/errors/errors/#_top)
- [Pydantic Validators](https://pydantic.dev/docs/validation/latest/concepts/validators/)

### 24/09 — dia 4

- Decidi com o agente de IA que a expiração das reservas acontece durante a requisição, e não em um serviço em segundo plano. Escrevi a função `_expirar_reserva` no `reservas.py`. Ela faz um `update_one` com filtro de três condições e um `$set` mudando o status para `"expirada"`.
- Escrevi a função `expirar_vencidas` no `reservas.py`, que monta o filtro das reservas vencidas.

#### Fontes de estudo dia 4:

- [Comparison Query Operators](https://www.mongodb.com/docs/manual/reference/operator/query-comparison/)
- [$set](https://www.mongodb.com/docs/manual/reference/operator/update/set/)
- [pymongo — Collection.update_one](https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.update_one)
