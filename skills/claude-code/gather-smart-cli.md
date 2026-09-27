---
name: gather-smart-cli
version: 0.1.0
description: CLI para atualizar Smart Objects do Gather Town via webhooks assinados.
---

## FONTE DA VERDADE: O ENDPOINT VIVO

**Antes de QUALQUER update**, rode `gather-bot ping`. Se não retornar 200, **pare e corrija** — não envie comandos cegos.

---

## FLUXO OBRIGATÓRIO DO AGENTE

### 1. Setup (uma vez por máquina)
```bash
gather-setup
# Preenche: BOT_MONITOR_URL/KEY, LIGHTBULB_URL/KEY, INBOX_URL/KEY
# Keys: painel Gather → Smart Object → ⋮ → Regenerate token (whsec_... aparece 1x)
gather-test all  # deve dar 3/3 OK
```

### 2. Antes de QUALQUER update real
```bash
gather-bot ping  # ou gather-test all
# Se NÃO 200 → PARE. Corrija .env/secret/URL. Não prossiga.
```

### 3. Após CADA ação de trabalho real — ATUALIZE IMEDIATAMENTE (após ping 200)

| Sua ação | Comando OBRIGATÓRIO |
|----------|---------------------|
| Iniciou tarefa/coding | `gather-bot add "task: <nome>" --status timer` |
| Concluiu tarefa | `gather-bot add "task: <nome>" --status on` |
| Travou/dependência externa | `gather-bot add "task: <nome>" --status alert` |
| Precisa input do usuário | `gather-bot add "task: <nome>" --status question` |
| Usuário em call/reunião | `gather-light on --color red` |
| Usuário livre/foco | `gather-light on --color green` |
| Usuário ausente/almoço | `gather-light on --color yellow` |
| Nova pendência | `gather-inbox add "descrição"` |
| Fez pendência do inbox | `gather-inbox set --level <novo_total>` |

**Harness:** `plan`/`ask` = peça aprovação **antes** da ação; `auto`/`default` = execute ação + update (após ping OK).

---

## ERROS — TRATE COMO BLOQUEADORES

| Código | Ação IMEDIATA |
|--------|---------------|
| `400` / `415` | Corrija payload; não reenvie igual |
| `404 not_found` | `gather-bot ping` → confira `.env`; veja capabilities no `pong` |
| `404 capability_not_declared` | Rode `ping` → veja capabilities reais |
| `410 token_revoked` | Novo `whsec_...` no painel → `.env` |
| `429 rate_limited` | Aguarde `RateLimit-Reset` segs; não faça burst |
| `503` | Retry com backoff + `Retry-After` |

---

## FORMATAÇÃO
- **Markdown NÃO funciona** no Bot Monitor → texto simples + emojis: ✅ 🔴 ⚠️ ❓ 🟢
- Nunca commite secrets (`whsec_...`). `.env` só local.

---

## PRÉ-REQUISITOS
- Python 3.11+ no PATH (`python3` / `py`)
- `git` no PATH
- Windows: instale Python marcando "Add to PATH"

---

## COMANDOS RÁPIDOS
```
gather-bot ping
gather-bot add "msg" --status timer|on|alert|question|working|off
gather-bot list

gather-light on --color green|red|yellow
gather-light off --color green|red|yellow

gather-inbox add "tarefa"
gather-inbox set --level N
gather-inbox list

gather-test all
gather-setup
```

---

**Repo:** https://github.com/sm1g00l/gather-smart-cli