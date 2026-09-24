# Feira Relâmpago — Clube Quindim

API de reserva de estoque e pedidos para a Feira Relâmpago - Clube Quindim.

## Como rodar
```bash
git clone https://github.com/adelmodias95/quindim-feira-relampago.git && cd quindim-feira-relampago
cp .env.example .env
docker compose up --build
```
Depois de rodar o comando, acesse: `http://localhost:8000/healthz`

## Como testar
| Método | Caminho | O que faz
| --- | --- | --- |
| GET | /healthz | 200 se o banco responde, 503 se não
| GET | /v1/livros | catálogo com estoque e disponível
| POST | /v1/reservas | cria a reserva e desconta o disponível
| GET | /v1/reservas/{id} | consulta a reserva; expira se já venceu
| POST | /v1/admin/reset | limpa reservas e pedidos e restaura o catálogo

### Rotas em desenvolvimento
| Método | Caminho
| --- | --- |
| POST | /v1/reservas/{id}/confirmar
| GET | /v1/pedidos/{id}
| POST | /v1/webhooks/pagamento

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

# Voltar ao estado inicial
curl -X POST http://localhost:8000/v1/admin/reset \
  -H "X-Admin-Token: COLE_O_ADMIN_TOKEN_AQUI"
```

### Observações
1) O token da rota `/v1/admin/reset` é o ADMIN_TOKEN declarado no .env
2) O produto QND-005 tem estoque 1 e o QND-004 tem 3, são dois produtos fáceis para testar o limite de estoque.
3) Para testar o `RESERVA_TTL_SEGUNDOS` sem precisar esperar 15 minutos, pode baixar o valor de 900 para 10 no `.env` e subir o ambiente novamente com `docker compose up`.
