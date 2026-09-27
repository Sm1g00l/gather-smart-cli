---
name: gather-smart-cli
version: 0.2.0
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
| Iniciou tarefa/coding | `gather-bot add "task: <nome>" --status working` |
| Concluiu tarefa | `gather-bot add "task: <nome>" --status on` |
| Travou/dependência externa | `gather-bot add "task: <nome>" --status alert` |
| Precisa input do usuário | `gather-bot add "task: <nome>" --status question` |
| Usuário em call/reunião | `gather-light on --color red` |
| Usuário livre/foco | `gather-light on --color green` |
| Usuário ausente/almoço | `gather-light on --color orange` |
| Nova pendência (seu inbox) | `gather-inbox add "descrição"` |
| Nova pendência (inbox do colega) | `gather-inbox add "descrição" --to colega` |
| Fez pendência do inbox | `gather-inbox set --level <novo_total>` |

### Multi-inbox (v0.2.0)
```bash
# Configurar inbox de colega (1x)
gather-inbox config add joao --url <url> --key whsec_... --owner "João"

# Listar inboxes salvos
gather-inbox config list

# Enviar para inbox do colega
gather-inbox add "tarefa para João" --to joao

# Definir default
gather-inbox config default meu
```

---

## ERROS — TRATE COMO BLOQUEADORES

| Código | Ação IMEDIATA |
|--------|---------------|
| `400` / `415` | Corrija payload; não reenvie igual |
| `404 not_found` | `gather-bot ping` → confira `.env`; veja capabilities no `pong` |
| `404 capability_not_declared` | Rode `ping` → veja capabilities reais |
| `410 token_revoked` | Novo `whsec_...` no painel → `.env` |
| `429 rate_limited` | A CLI já espera `Retry-After` + 2s e reenvia (teto `GATHER_MAX_WAIT`, padrão 150s); não faça burst |
| `503` | Retry com backoff + `Retry-After` |

---

## FORMATAÇÃO
- **Markdown NÃO funciona** no Bot Monitor → texto simples + emojis: ✅ 🔴 ⚠️ ❓ 🟢
- Nunca commite secrets (`whsec_...`). `.env` só local.

---

## COMANDOS RÁPIDOS
```
gather-bot ping
gather-bot add "msg" --status working|on|alert|question|working|off
gather-bot list
gather-bot clear

gather-light on --color green|red|orange
gather-light off --color green|red|orange

gather-inbox add "tarefa" [--to nome]
gather-inbox config add <nome> --url <url> --key whsec_... [--owner <nome>]
gather-inbox config list
gather-inbox config remove <nome>
gather-inbox config default <nome>
gather-inbox set --level N
gather-inbox list
gather-inbox remove <task_id>
gather-inbox clear

gather-test all
gather-setup
```

---

**Repo:** https://github.com/sm1g00l/gather-smart-cli