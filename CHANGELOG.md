# Changelog

Mudanças relevantes do gather-smart-cli, da mais recente para a mais antiga.
Versões seguem as tags `vX.Y.Z` do repositório.

## [0.2.6] - 2026-09-27
Fluxo "ler para editar": o Gather guarda no máximo 20 atividades por objeto, não tem evento de edição e ignora `activity.add` com id repetido.

- `gather-bot show` e `gather-inbox show [--to]`: leem o estado vivo (atividades com id, estado/contador, uso do limite de 20).
- `--id <chave>` em `gather-bot add` e `gather-inbox add`: edita a entrada da chave em vez de criar outra.
- `gather-bot remove <id>`.
- Skills e PROMPT: fluxo "ler para editar" (uma tarefa = uma entrada).

## [0.2.5] - 2026-09-27
Tudo validado contra os Smart Objects reais (ver `tests/test_e2e.py`).
- **Bot Monitor:** o texto do `add` agora chega ao Gather (como atividade); antes só ia pro arquivo local.
- **Bot Monitor:** `timer` (antigo padrão) era rejeitado com `400`; padrão agora é `working`, `timer` virou alias.
- **Bot Monitor:** novo `gather-bot clear`.
- **Lightbulb:** `--color` era ignorado; agora envia `variant.set`. Nova cor `orange`; `yellow` (que o Gather ignora) virou alias de `orange`.
- **Inbox:** id da tarefa era `task_<tamanho do texto>` e colidia; agora é único.
- **Rate limit:** a CLI respeita `Retry-After` no `429` e reenvia (teto `GATHER_MAX_WAIT`); `gather-test all` mostra a cota restante.
- **Testes:** suíte e2e opcional (`GATHER_E2E=1 pytest -m e2e`) com snapshot e restauração do estado.

## [0.2.0] - 2026-09-26
- Multi-inbox (`gather-inbox config ...`, `--to`), `gather-inbox remove` e `clear`.

[0.2.6]: https://github.com/sm1g00l/gather-smart-cli/releases/tag/v0.2.6
[0.2.5]: https://github.com/sm1g00l/gather-smart-cli/releases/tag/v0.2.5
[0.2.0]: https://github.com/sm1g00l/gather-smart-cli/commit/7fa5d43
