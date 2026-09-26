Repo: https://github.com/sm1g00l/gather-smart-cli

Passos para qualquer agente (Claude Code, Codex, etc.):
1. Clone ou atualize: `git clone <repo>` ou `git pull`
2. Instale a CLI: `cd gather-smart-cli && pip install -e .`
3. Instale a skill no agente: `cp skills/claude-code/* ~/.claude/skills/` (ou equivalente no Codex)
4. Sempre que uma tarefa de trabalho progredir: atualize os smart objects no Gather conforme o progresso real — `gather-bot add "task: <nome>" <status>` (timer/início, smiley/conclusão, warning/bloqueio), `gather-light --color green/red/yellow` (ocupação/reunião/bloqueio), `gather-inbox add/set` (fila de tarefas pendentes). Não atualize o repo (`git pull`) a cada ação. Se harness = `plan`/`ask`: peça aprovação; se `auto`/`default`: atualize diretamente.
5. Use: `gather setup`, `gather-bot add "mensagem" smiley`, `gather-light --color green`, `gather-inbox add "tarefa X"

Nota sobre harness:
- `auto` / `default`: atualize os objetos diretamente (sem perguntar).
- `plan` / `ask`: peça aprovação antes de alterar estados.

Nota sobre formatação (pendência):
- Markdown simples (`**bold**`, `*italic*`) ainda não verificado no webhook do Bot Monitor. Use texto simples + emojis até confirmar.
