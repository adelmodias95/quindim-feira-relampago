# Notas

## Decisões

- 21/09: Utilizar uv em vez de Poetry, porque o uv instala a própria versão do Python dentro do projeto, ao invés de usar a instalação global do Python. Escolhi por indicação de um agente de IA. Vou entender as diferenças na prática conforme for desenvolvendo o projeto.
- 22/09: Utilizar a versão 8.2 da imagem do Mongo. A spec pede mongo:8 mas hoje, ela é resolvida para a série 8.3.x, que introduziu uma verificação que recusa iniciar em kernel Linux 6.19 ou mais novo. A VM que o Docker Desktop roda no meu Mac tem um kernel nessa faixa. O Agente de IA me ajudou a entender e resolver esse problema após eu tentar iniciar o container do mongo db no docker. Print do erro: [https://i.imgur.com/KXJ7yKp.png](https://i.imgur.com/KXJ7yKp.png) [Fonte 1](https://github.com/Sorcha-Platform/Sorcha/issues/1652) / [Fonte 2](https://github.com/bluewave-labs/Checkmate/issues/3842) / [Fonte 3](https://community.graylog.org/t/mongodb-cannot-start-linux-kernel-versions-6-19-and-newer-has-a-known-incompatibility/37373/4)
- 22/09: Aguardar 5 segundos para que a conexão ao Mongo via pymongo seja declarada como erro. Por padrão o pymongo e o gunicorn aguardam 30 segundos, mas o gunicorn vencia a corrida e matava o worker, dessa forma exibia a tela de erro padrão do Flask com a mensagem "Internal Server Error". Agora a API retorna uma resposta JSON no caso de sucesso ou erro.



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

#### Fontes de estudo dia 3:

[Mongo.bulkWrite()](https://www.mongodb.com/pt-br/docs/manual/reference/method/mongo.bulkwrite/#mongodb-method-Mongo.bulkWrite)
[Serialize and deserialize MongoDB documents in Python using PyMongo](https://oneuptime.com/blog/post/2026-03-31-mongodb-serialize-deserialize-documents-python/view)
[Append to JSON file using Python](https://www.geeksforgeeks.org/python/append-to-json-file-using-python/)
[Handling Application Errors](https://flask.palletsprojects.com/en/stable/errorhandling/)
[Werkzeug - HTTP Exceptions](https://werkzeug.palletsprojects.com/en/stable/exceptions/)