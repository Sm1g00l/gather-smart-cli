# gather-smart-cli

CLI para interagir com Smart Objects do Gather Town.

```bash
pip install -e .
gather setup
gather-bot add "task: auth" timer
gather-light --color green
gather-inbox add "tarefa X"
```

## Configuração do Webhook (Importante)
O SDK oficial (`@gathertown/webhook-object-sdk`) usa webhooks assinados. A URL fornecida pelo Gather (ex: `https://api.v2.gather.town/api/v2/hooks/spaces/.../objects/...`) pode ser uma URL de configuração/referência, não um endpoint `POST` direto. Se você receber `404 not_found` ao testar diretamente, isso indica que o endpoint ativo pode ser diferente (talvez montado pelo SDK com assinatura `X-Gather-Signature` ou `Authorization`).

**O que fazer:**
- Configure `BOT_MONITOR_URL`, `LIGHTBULB_URL`, `INBOX_URL` no `.env` com a URL exata que o SDK oficial usa no seu ambiente.
- Se o endpoint ativo for confirmado, a CLI funcionará imediatamente (`requests.post` com `X-API-Key`).
- Se ainda não confirmar o endpoint, a CLI está pronta e os mocks dos testes cobrem o comportamento esperado.

**Pendência:** Confirmar com webhook ativo se markdown simples (`**bold**`) é aceito; enquanto isso, usar texto simples + emojis.

## Prompt para Claude Code / Codex
Veja `PROMPT.md`.
