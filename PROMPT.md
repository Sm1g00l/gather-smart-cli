# gather-smart-cli — Prompt para Agentes (Claude Code, Codex, etc.)

## Objetivo
CLI (`gather-bot`, `gather-light`, `gather-inbox`, `gather-test`, `gather-setup`) para atualizar Smart Objects do Gather Town.

---

## FONTE DA VERDADE: O ENDPOINT VIVO

**Antes de QUALQUER update**, rode `gather-bot ping`. Se não retornar 200, **pare e corrija** — não envie comandos cegos.

---

## PRÉ-REQUISITOS POR SO

| Sistema | Verifique |
|---------|-----------|
| Linux/macOS | `python3 --version` (>=3.11), `git` |
| Windows | `py --version` (>=3.11), `git` |

> Python: [python.org/downloads](https://python.org/downloads) → "Add to PATH" no Windows.

---

## INSTALAÇÃO DA CLI + SKILL

```bash
# 1. Clone e instale
cd /path/to/gather-smart-cli
pip install -e .

# 2. Instale skill no agente
# Claude Code:
cp skills/claude-code/gather-smart-cli.md ~/.claude/skills/
# Codex:
cp skills/codex/gather-smart-cli.md ~/.codex/skills/

# 3. Configure credenciais (1x)
gather-setup
# Preenche: BOT_MONITOR_URL/KEY, LIGHTBULB_URL/KEY, INBOX_URL/KEY
# Keys: painel Gather → Smart Object → ⋮ → Regenerate token (whsec_... aparece 1x)

# 4. Verifique
gather-test all  # 3/3 OK
```

---

## FLUXO OBRIGATÓRIO DO AGENTE

### REGRA 1 — Ping antes de tudo
```bash
gather-bot ping  # ou gather-test all
# Se NÃO 200 → PARE. Corrija .env/secret/URL. Não prossiga.
```

### REGRA 2 — Atualize após CADA ação real (após ping 200)

| Sua ação | Comando OBRIGATÓRIO |
|----------|---------------------|
| Iniciou tarefa/coding | `gather-bot add "task: <nome>" --status working` |
| Concluiu tarefa | `gather-bot add "task: <nome>" --status on` |
| Travou/dependência | `gather-bot add "task: <nome>" --status alert` |
| Precisa input | `gather-bot add "task: <nome>" --status question` |
| Usuário em call | `gather-light on --color red` |
| Usuário livre/foco | `gather-light on --color green` |
| Usuário ausente | `gather-light on --color orange` |
| Nova pendência | `gather-inbox add "descrição"` |
| Fez pendência inbox | `gather-inbox set --level <novo_total>` |

**Harness:** `plan`/`ask` = aprove **antes** da ação; `auto`/`default` = execute ação + update (após ping OK).

---

## ERROS — BLOQUEADORES

| Código | Ação IMEDIATA |
|--------|---------------|
| `400`/`415` | Corrija payload; não reenvie igual |
| `404 not_found` | `gather-bot ping` → confira `.env`; veja capabilities no `pong` |
| `404 capability_not_declared` | Rode `ping` → veja capabilities reais |
| `410 token_revoked` | Novo `whsec_...` no painel → `.env` |
| `429` | A CLI já espera `Retry-After` + 2s e reenvia (teto `GATHER_MAX_WAIT`, padrão 150s); não faça burst |
| `503` | Retry com backoff + `Retry-After` |

---

## FORMATAÇÃO
- **Markdown NÃO funciona** → texto simples + emojis: ✅ 🔴 ⚠️ ❓ 🟢

---

## COMANDOS
```
gather-bot ping
gather-bot add "msg" --status working|on|alert|question|working|off
gather-bot list
gather-bot clear

gather-light on --color green|red|orange
gather-light off --color green|red|orange

gather-inbox add "tarefa"
gather-inbox set --level N
gather-inbox list

gather-test all
gather-setup
```

---

**Repo:** https://github.com/sm1g00l/gather-smart-cli