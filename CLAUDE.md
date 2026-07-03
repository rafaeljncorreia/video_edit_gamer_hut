# video_edit_gamer_hut

Editor de vídeos verticais (9:16) orientado por IA para a marca **Gamer Hut**. Roda hoje como pipeline orquestrado pelo Claude Code; caminho futuro é virar app independente/pago com API key própria da Anthropic (via Cowork).

## Início de toda sessão

Antes de qualquer tarefa de edição, seguir [`memory/session_init.md`](memory/session_init.md) — ler brandbook, style guide e log de regras aprendidas.

## Roadmap

- **Fase 0 (em andamento)** — entender a marca Gamer Hut e o estilo de edição de referência. Ver [`docs/brand/`](docs/brand/).
- **Fase 1 (em andamento, orientada por necessidade concreta)** — integrar skills/tools conforme surge a necessidade real (não especulativamente). Ver [`docs/skills/`](docs/skills/) para o que já está implementado vs. ainda pendente, e [`docs/skills/opencode-workflow.md`](docs/skills/opencode-workflow.md) para o fluxo de colaboração com OpenCode.
- **Fase 2 (iniciada)** — aprendizado contínuo: log de regras (`memory/editing_rules_log.json`) alimentado por feedback do usuário e por descobertas técnicas, consultado a cada sessão.

## MVP (Objetivo 0)

Foco atual: **automação de anúncios de Mercado Livre** — formato fixo capa (3s) → trailer (fundo desfocado + centro nítido) → narração + legenda karaokê + música baixa. Ver [`src/README.md`](src/README.md) para uso do pipeline e [`docs/brand/style-guide-video.md`](docs/brand/style-guide-video.md) para a especificação do formato. Voz é gravada pelo usuário e fornecida como arquivo de áudio (narração por IA é requisito futuro, não deste MVP).

## Regras do projeto

- A pasta `media/` (footage bruto, áudio, referências, output) nunca deve ser commitada — está no `.gitignore`. Vídeos são fornecidos localmente pelo usuário a cada sessão, em `media/raw/<slug>/`.
- Toda regra de edição aprendida via feedback do usuário — ou descoberta técnica relevante (ex: limitações de ambiente) — deve ser registrada em `memory/editing_rules_log.json`, não apenas lembrada em conversa.
- Pipeline de automação em `src/pipeline/` (Python + ffmpeg + openai-whisper). Ver [`src/README.md`](src/README.md).
