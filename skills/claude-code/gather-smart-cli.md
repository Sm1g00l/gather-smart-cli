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

## Pendência
- Markdown simples no webhook do Bot Monitor ainda não verificado; usar texto simples + emojis.
