# gather-smart-cli

CLI para atualizar Smart Objects do Gather Town via webhooks assinados (Standard Webhooks v1).

---

## 🚀 Instalação (2 min)

### Pré-requisitos
| Sistema | Comando |
|---------|---------|
| **Linux/macOS** | `python3 -m pip install --user pipx && pipx ensurepath` |
| **Windows** | `py -m pip install --user pipx && pipx ensurepath` |
| **Todos** | Python 3.11+ instalado e no PATH |

> Se não tem Python: [python.org/downloads](https://python.org/downloads) → marque "Add to PATH" no Windows.

### 1. Clone e instale
```bash
git clone https://github.com/sm1g00l/gather-smart-cli
cd gather-smart-cli
pip install -e .
```

### 2. Instale a skill no seu agente de IA
**Claude Code:**
```bash
cp skills/claude-code/gather-smart-cli.md ~/.claude/skills/
```

**Codex:**
```bash
cp skills/codex/gather-smart-cli.md ~/.codex/skills/
```

> A skill ensina o agente **quando e como** usar cada comando. Depois disso, você só fala naturalmente: *"muda o light pra vermelho"* ou *"adiciona tarefa no bot"*.

### 3. Configure as credenciais
```bash
gather-setup
```
Vai perguntar interativamente:
- **Bot Monitor URL** + **Key** (`whsec_...`)
- **Lightbulb URL** + **Key** (`whsec_...`)
- **Inbox URL** + **Key** (`whsec_...`)

> Pegue as keys no painel do Gather: Smart Object → ⋮ → **Regenerate token** (copie o `whsec_...` que aparece uma vez só).

### 4. Teste
```bash
gather-test all
```
Deve sair:
```
[OK] Bot Monitor: 200 | preset=status, capabilities=...
[OK] Lightbulb: 200 | preset=switch, capabilities=...
[OK] Inbox: 200 | preset=inbox, capabilities=...
```

---

## 📋 Comandos

### Bot Monitor — tarefas do agente
```bash
gather-bot add "task: refatorar auth" --status working   # iniciou
gather-bot add "task: refatorar auth" --status on      # concluiu
gather-bot add "task: refatorar auth" --status alert   # bloqueado
gather-bot add "task: refatorar auth" --status question # dúvida
gather-bot ping                                        # testa conexão
gather-bot list                                        # histórico local
gather-bot clear                                       # limpa as mensagens do bot
```

### Lightbulb — presença do usuário
```bash
gather-light on --color green   # livre / focado
gather-light on --color red     # em reunião / não perturbe
gather-light on --color yellow  # ausente / almoço
gather-light off --color green  # desliga
```

### Inbox — fila de pendentes
```bash
gather-inbox add "revisar PR #42"
gather-inbox set --level 3
gather-inbox list
```

---

## ⚠️ Formatação
**Markdown NÃO funciona** no Bot Monitor (testado: `**bold**`, `*italic*`, `` `code` `` saem literais).  
Use **texto simples + emojis**: ✅ 🔴 ⚠️ ❓ 🟢

---

## 🔧 Troubleshooting

| Erro | Causa | Solução |
|------|-------|---------|
| `400` / `415` | Body/Content-Type inválido | Não edite payload manualmente |
| `404 not_found` | Secret errado, URL errada, timestamp >5min | Rode `gather-bot ping`, confira `.env` |
| `410 token_revoked` | Token regenerado no painel | Copie novo `whsec_...` pro `.env` |
| `429 rate_limited` | 60 req/min/space ou 100/min/IP | Espere `RateLimit-Reset` segs |
| `503` | Transitório | Retry com backoff |

---

## 📦 Requisitos
- Python 3.11+
- Conta Gather Town com Smart Objects configurados