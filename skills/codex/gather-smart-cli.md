---
name: gather-smart-cli
version: 0.1.0
description: CLI para interagir com Smart Objects do Gather Town via webhooks.
---

## Quando usar
- Quando precisar atualizar status de tarefas no escritório virtual Gather.
- Usar com Claude Code ou Codex para automatizar `gather-bot`, `gather-light`, `gather-inbox`.

## Comandos principais
- `gather-bot add "msg" timer` → Bot Monitor
- `gather-light --color green` → Lightbulb
- `gather-inbox add "tarefa"` → Inbox

## Setup
```bash
gather setup
```

## Atualizar estados
Sempre que uma tarefa progredir, execute o comando correspondente para refletir no Gather.
Não atualize o repo (`git pull`) a cada ação — atualizações são estados dos objetos.
Se harness = `plan`/`ask`: peça aprovação; se `auto`/`default`: atualize diretamente.

## Regras do SDK oficial (de message.txt / docs/reference.md)
- **Secret (`whsec_…`):** nunca commit, nunca log; ler de env (`GATHER_WEBHOOK_SECRET`); validar que começa com `whsec_`.
- **Assinatura:** `Standard Webhooks v1` (HMAC-SHA256 sobre `${id}.${timestamp}.${body}`). Não assinar manualmente — usar a biblioteca oficial; mas se fizer manual, assinar os bytes exatos do payload uma só vez.
- **Status codes:** `200` = aceito. Não retry `4xx` (`400`/`404`/`410`/`415`) — corrigir. Retry só `5xx`/`503`, com backoff.
- **Rate limits:** respeitar `RateLimit-Limit` / `RateLimit-Remaining` / `RateLimit-Reset`; limite `60 req/min` por espaço, `100/min` por IP.
- **Timestamp:** enviar fresco (`±5` min); nunca replay body antigo.
- **WebHook ID (`id`):** único por evento; reutilizar no retry (idempotente); `10` últimos ids deduplicados.
- **Body:** `{ "type": "<capability>.<method>", "timestamp": "ISO-8601", "data": { ... } }` (`timestamp` obrigatório exceto `webhook.ping`).
- **404 `not_found`:** falha uniforme — assinatura ruim, URL errada, timestamp expirado, body reformado, ou objeto não aceita o `type`. Sempre rodar `webhook.ping` antes.
- **Eventos (status):** `status.set` (`state`: `off`/`on`/`question`/`alert`/`working`); `status.reset`; `switch.set_state` (`on`: bool); `inbox.activity.add` (`id` ≤128, `text` ≤500); `inbox.counter.set`/`counter.increment`; `variant.set` (`color`).

## Pendência
- Markdown simples no webhook do Bot Monitor ainda não verificado; usar texto simples + emojis.
