---
name: gather-smart-cli
version: 0.2.6
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

### 3. LER PARA EDITAR — não sair adicionando

O Bot Monitor é um **quadro de estado das tarefas**, não um log: **uma tarefa = uma entrada**, editada a cada transição pelo mesmo `--id`.
- O Gather guarda no máximo **20 atividades** por objeto (bot e inbox); da 21ª em diante a mais antiga some sem aviso.
- Não há evento de edição e `activity.add` com id repetido é ignorado; `--id` faz `remove` + `add`.
- Antes de começar uma tarefa: `gather-bot show` (estado + entradas com id). Já existe entrada do mesmo assunto → reutilize o id dela. Várias → mantenha uma, remova as outras (`gather-bot remove <id>`). Nenhuma → id novo e estável `t-<slug>`.
- O texto é o estado atual da tarefa (reescreva, não acrescente). Subtarefas não ganham entrada.
- Com 15+ entradas, remova ✅ antigas até ~10.

### 4. Nas TRANSIÇÕES da tarefa (após ping 200), sempre com o mesmo `--id`

| Sua ação | Comando OBRIGATÓRIO |
|----------|---------------------|
| Iniciou/retomou tarefa | `gather-bot add "🔄 <tarefa>" --status working --id t-<slug>` |
| Precisa input do usuário | `gather-bot add "❓ <tarefa>: <o que precisa>" --status question --id t-<slug>` |
| Travou/dependência externa | `gather-bot add "⚠️ <tarefa>: <motivo>" --status alert --id t-<slug>` |
| Concluiu tarefa | `gather-bot add "✅ <tarefa>: <resultado>" --status on --id t-<slug>` |
| Usuário em call/reunião | `gather-light on --color red` |
| Usuário livre/foco | `gather-light on --color green` |
| Usuário ausente/almoço | `gather-light on --color orange` |
| Nova pendência (ler antes: `gather-inbox show`) | `gather-inbox add "descrição" --id p-<slug>` |
| Pendência mudou | `gather-inbox add "novo texto" --id <id existente>` |
| Nova pendência (inbox do colega) | `gather-inbox add "descrição" --id p-<slug> --to colega` |
| Resolveu pendência | `gather-inbox remove <id>` e `gather-inbox set --level <pendências restantes>` |

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
gather-bot show                      # estado + entradas com id (LER antes de editar)
gather-bot add "msg" --status working|on|alert|question|off --id t-<slug>
gather-bot remove <id>
gather-bot list
gather-bot clear

gather-light on --color green|red|orange
gather-light off --color green|red|orange

gather-inbox show [--to nome]        # pendências com id + contador
gather-inbox add "tarefa" --id p-<slug> [--to nome]
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