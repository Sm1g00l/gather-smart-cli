# gather-smart-cli

CLI para atualizar Smart Objects do Gather Town via webhooks assinados (Standard Webhooks v1).

**Versão atual: 0.2.6** — histórico de mudanças no [CHANGELOG.md](CHANGELOG.md).

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
git checkout v0.2.6   # opcional: fixa a versão
pip install -e .
```

### 2. Instale a skill no seu agente de IA
**Claude Code** (a skill precisa ficar numa pasta própria, como `SKILL.md`):
```bash
mkdir -p ~/.claude/skills/gather-smart-cli
cp skills/claude-code/gather-smart-cli.md ~/.claude/skills/gather-smart-cli/SKILL.md
```
> Usa `CLAUDE_CONFIG_DIR` (várias contas)? Troque `~/.claude` pela pasta da conta.

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

Rate limit: 57/60 restantes (policy 60;w=60)
```
O ping devolve o **estado vivo** de cada objeto (`status.state`, `activity.entries`, `switch.on`, `variant.color`, `counter.count`), então `gather-test all` também serve para conferir o efeito de um comando.

---

## 📋 Comandos

### Bot Monitor — tarefas do agente
```bash
gather-bot show                                                   # estado + atividades com id (ao vivo)
gather-bot add "🔄 refatorar auth" --status working --id t-auth    # iniciou
gather-bot add "❓ refatorar auth: qual lib?" --status question --id t-auth  # dúvida (edita a mesma entrada)
gather-bot add "⚠️ refatorar auth: CI fora" --status alert --id t-auth       # bloqueado
gather-bot add "✅ refatorar auth" --status on --id t-auth         # concluiu
gather-bot add --status off                                       # só o estado, sem mensagem
gather-bot remove t-auth                                          # remove uma atividade
gather-bot ping                                                   # testa conexão
gather-bot list                                         # histórico local
gather-bot clear                                        # limpa as mensagens do bot
```
- O **estado** vira o ícone; o **texto** vira uma entrada de atividade no objeto.
- Com `--id`, o `add` **edita** a entrada daquela chave (ou cria, se não existir). Sem `--id`, cria uma entrada nova a cada chamada.
- Estados aceitos pelo Gather: `working`, `on`, `question`, `alert`, `off`. `timer` é aceito como alias de `working` (o Gather rejeita `timer` com `400`).
- `list` mostra o histórico local (`bot_messages.json`, gravado no diretório atual).

### Lightbulb — presença do usuário
```bash
gather-light on --color green   # livre / focado
gather-light on --color red     # em reunião / não perturbe
gather-light on --color orange  # ausente / almoço
gather-light off --color green  # desliga
```
Cores que a lâmpada aceita: `green`, `red`, `orange`. `yellow` vira `orange`: o Gather responde `200` para `yellow`, mas não muda a cor.

### Inbox — fila de pendentes
```bash
gather-inbox show                          # pendências com id + contador (ao vivo)
gather-inbox add "revisar PR #42" --id p-pr-42          # cria ou edita pela chave
gather-inbox add "revisar PR #42 (2 comentários)" --id p-pr-42   # edita, não duplica
gather-inbox add "revisar PR #43"          # sem --id: id aleatório, sempre cria
gather-inbox set --level 3                 # contador do objeto
gather-inbox remove <task_id>              # id aparece no gather-test all / list
gather-inbox clear                         # remove todas as tarefas
gather-inbox list                          # histórico local (tasks.json)
```

**Multi-inbox** (inbox de colegas):
```bash
gather-inbox config add joao --url <url> --key whsec_... --owner "João"
gather-inbox config list
gather-inbox config default joao
gather-inbox config remove joao
gather-inbox add "tarefa para o João" --to joao
```
Os inboxes salvos ficam em `~/.config/gather-cli/inboxes.json` (chmod 600). Sem nenhum salvo, vale `INBOX_URL`/`INBOX_KEY` do `.env`.

---

## ✏️ Ler para editar (limite de 20 atividades)
O Gather guarda **no máximo 20 atividades** por objeto (bot e inbox); da 21ª em diante a mais antiga **some sem aviso**. Ele também não tem evento de edição, e `activity.add` com um id que já existe é **ignorado**.

Por isso o fluxo recomendado (e o das skills) é:
1. `show` para ler o que já está lá;
2. se já existe entrada do mesmo assunto, `add ... --id <id dela>` para editar (a CLI faz `remove` + `add`; a entrada vai para o fim);
3. só crie entrada nova quando o assunto for novo, com uma chave estável (`t-<slug>` no bot, `p-<slug>` na inbox);
4. pendência resolvida: `gather-inbox remove <id>`, não um novo `add`.

---

## ⏱️ Rate limit
O Gather limita a **60 requisições por minuto por space** (e 100/min por IP). Toda resposta traz a cota:

| Header | Exemplo | Quando vem |
|---|---|---|
| `RateLimit-Limit` | `60` | sempre |
| `RateLimit-Remaining` | `57` | sempre |
| `RateLimit-Policy` | `60;w=60` (60 req em janela de 60s) | sempre |
| `Retry-After` | `60` (segundos) | no `429` |

Num `429`, a CLI **segura a execução** por `Retry-After` + 2s e reenvia a mesma mensagem (mesmo `webhook-id`, assinatura nova). Avisa no stderr enquanto espera:
```
Gather 429: aguardando 62s (Retry-After=60s)...
```
O teto de espera por comando é `GATHER_MAX_WAIT` (padrão `150` segundos); passando disso, o `429` é devolvido. Um `503` com `Retry-After` segue a mesma regra.

`gather-bot add` com texto faz 2 requisições (atividade + estado); `gather-light` também faz 2 (cor + liga/desliga).

---

## 🧪 Testes
```bash
pytest                           # unitários (mockados), não tocam no Gather
GATHER_E2E=1 pytest -m e2e -v    # ponta a ponta contra os Smart Objects reais do .env
```
O e2e tira um snapshot dos 3 objetos, exercita todos os comandos e restaura o estado original no fim (e confere).
Faz ~52 requisições. Lê a cota nos headers (`RateLimit-Remaining`): se não sobra o bastante, espera a janela de 60s antes de começar; num `429`, a própria CLI espera o `Retry-After`. Enquanto roda, ele consome quase toda a cota do space por ~1 minuto.

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
| `429 rate_limited` | 60 req/min/space ou 100/min/IP | A CLI espera sozinha `Retry-After` + 2s e reenvia (teto: `GATHER_MAX_WAIT`, padrão 150s) |
| `503` | Transitório | Com `Retry-After`, a CLI espera e reenvia; sem ele, tente de novo depois |

---

## 📦 Requisitos
- Python 3.11+
- Conta Gather Town com Smart Objects configurados