# Feira Relâmpago — Clube Quindim

API de reserva de estoque e pedidos para a Feira Relâmpago - Clube Quindim, com uma tela em Nuxt.

## Como rodar
```bash
git clone https://github.com/adelmodias95/quindim-feira-relampago.git && cd quindim-feira-relampago
cp .env.example .env
docker compose up --build
```
Sobem três containers: o MongoDB, a API em `http://localhost:8000` e o frontend em `http://localhost:3000`. O catálogo é semeado na subida, então dá para usar a tela direto.

Para conferir que a API está falando com o banco: `http://localhost:8000/healthz`

## Como testar

### Testes automatizados
```bash
uv run pytest
```

São dois grupos. Os de unidade cobrem o desconto progressivo e o rateio, sem banco, e incluem uma verificação de que a soma dos descontos das linhas bate exatamente com o desconto total nas 1023 combinações possíveis do catálogo. O de concorrência dispara 20 reservas simultâneas contra o MongoDB de verdade e confere que o disponível nunca fica negativo.

O grupo de concorrência precisa do ambiente no ar. Se a API não responder, ele é pulado em vez de falhar, e só os testes de unidade rodam.

### A API à mão

| Método | Caminho | O que faz |
| --- | --- | --- |
| GET | /healthz | 200 se o banco responde, 503 se não |
| GET | /v1/livros | catálogo com estoque e disponível |
| POST | /v1/reservas | cria a reserva e desconta o disponível |
| GET | /v1/reservas/{id} | consulta a reserva; expira se já venceu |
| POST | /v1/reservas/{id}/confirmar | gera o pedido com desconto e rateio |
| GET | /v1/pedidos/{id} | consulta o pedido |
| POST | /v1/webhooks/pagamento | recebe os eventos de pagamento, assinados |
| POST | /v1/admin/reset | limpa reservas, pedidos e eventos e restaura o catálogo |

### Exemplo de ponta a ponta
```bash
# Ver o catálogo
curl http://localhost:8000/v1/livros

# Reservar
curl -X POST http://localhost:8000/v1/reservas \
  -H "Content-Type: application/json" \
  -d '{"cliente_id": "c-001", "itens": [{"sku": "QND-001", "quantidade": 2}]}'

# Consultar a reserva
curl http://localhost:8000/v1/reservas/COLE_O_ID_AQUI

# Confirmar e gerar o pedido
curl -X POST http://localhost:8000/v1/reservas/COLE_O_ID_AQUI/confirmar

# Voltar ao estado inicial
curl -X POST http://localhost:8000/v1/admin/reset \
  -H "X-Admin-Token: COLE_O_ADMIN_TOKEN_AQUI"
```

### Observações
1) O token da rota `/v1/admin/reset` é o ADMIN_TOKEN declarado no .env
2) O produto QND-005 tem estoque 1 e o QND-004 tem 3, são dois produtos fáceis para testar o limite de estoque.
3) Para testar o `RESERVA_TTL_SEGUNDOS` sem precisar esperar 15 minutos, pode baixar o valor de 900 para 10 no `.env` e subir o ambiente novamente com `docker compose up`.
4) O status do pedido só muda por eventos do webhook, que são assinados com HMAC-SHA256 usando o `WEBHOOK_SEGREDO`. A tela não confirma pagamento: quem faz isso é o provedor externo.

## Estrutura

```
src/quindim_feira_relampago/
  app.py         as rotas e os códigos de status
  db.py          conexão com o Mongo e os índices únicos
  seed.py        o catálogo fixo, restaurado de forma idempotente
  livros.py      leitura do catálogo
  reservas.py    reserva, desconto atômico, compensação e expiração
  precos.py      desconto progressivo e rateio por linha
  pedidos.py     confirmação da reserva e consulta do pedido
  webhooks.py    assinatura, idempotência e efeitos do pagamento
  erros.py       o envelope de erro, num lugar só
tests/           unidade (sem banco) e concorrência (com banco)
frontend/        Nuxt 4: uma tela, com rotas de servidor para falar com a API
```

A regra de negócio mora em `reservas.py`, `precos.py`, `pedidos.py` e `webhooks.py`. Os outros arquivos são infraestrutura: conexão, catálogo, erros e rotas.

As decisões de projeto e o diário de desenvolvimento estão no [NOTAS.md](NOTAS.md).
