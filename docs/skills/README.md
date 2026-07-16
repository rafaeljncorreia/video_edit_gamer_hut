# Biblioteca de Skills & MCPs

## Fluxo multi-agente: Claude Code + OpenCode

O usuário já roda o **app desktop do OpenCode** (`OpenCode.exe`, não é CLI nem MCP) configurado com Deepseek V4 Flash grátis (OpenRouter/Google AI Studio/Zen). Para gastar menos créditos Claude/Anthropic no processo todo, dividimos o trabalho:

- **Claude Code** — orquestração, decisões de marca/estilo (brandbook, style guide), revisão de qualidade, integração final. Trabalho de julgamento, poucos tokens.
- **OpenCode (Deepseek grátis)** — implementação pesada/iterativa: features do pipeline, debugging repetitivo, boilerplate. Trabalho de muitos tokens, sem necessidade de julgamento de marca.

Como não há CLI do OpenCode acessível via Bash neste ambiente, o handoff é manual: Claude Code escreve a especificação da tarefa, o usuário cola no app OpenCode. Ver [`opencode-workflow.md`](opencode-workflow.md) para o template e o protocolo de segurança contra edições concorrentes.

## Implementado (MVP — automação de anúncio de Mercado Livre)

- **openai-whisper** (PyTorch) — transcrição local com timestamp por palavra. Ver [`src/README.md`](../../src/README.md). Usado no lugar de `faster-whisper` porque a dependência PyAV do faster-whisper é bloqueada por política de Controle de Aplicativo do Windows nesta máquina.
- **FFmpeg** (CLI local, via `subprocess`) — todo o corte, composição (fundo desfocado + centro nítido), mixagem de áudio e queima de legenda `.ass` (karaokê) do pipeline. Não usa um "FFmpeg MCP Server" — chamado diretamente como processo, o que já dá controle total sem overhead de protocolo.
- **`/voiceover-script`** (skill do projeto, [`.claude/skills/voiceover-script/SKILL.md`](../../.claude/skills/voiceover-script/SKILL.md)) — gera o roteiro de narração do anúncio de Mercado Livre a partir de `media/raw/<slug>/`. Codifica a voz da marca (brandbook + social playbook), a estrutura de 4 beats (hook → corpo → procedência → CTA), o alvo de 55–100 palavras e as regras de escrita para TTS/legenda karaokê. Invocar com `/voiceover-script <slug>`; salva o texto aprovado em `media/raw/<slug>/script.txt`. **Limitações**: produz texto, não voz (TTS ElevenLabs é etapa futura); exige confirmação humana do título oficial do jogo e de fatos não inferíveis do footage (plataforma, edição, escassez real); cobre só o formato de anúncio ML.

## Ainda não integrado (aguardando necessidade concreta)

- **Remotion** — motor de vídeo programável (React/TypeScript). Não foi necessário para o formato atual (composição estática por vídeo); útil se precisarmos de animações mais elaboradas de legenda/elementos no futuro.
- **FFmpeg `silencedetect`** — detecção de silêncio para cortes automáticos. Não usado ainda porque o formato de anúncio de Mercado Livre não tem cortes internos (é 1 capa + 1 trailer contínuo); relevante se formatos futuros exigirem remover pausas/gaguejos da narração.
- **CapCut Project Editor MCP** — edita o rascunho `.json` local do projeto CapCut **às cegas** (sem visão da interface) — não é "assistir/controlar o CapCut como um humano". Isso seria `computer-use` (disponível neste ambiente), que tem custo alto em créditos por depender de screenshot+visão a cada ação — o oposto do objetivo de eficiência do projeto. Reavaliado em 2026-07-03: os dois ganhos que motivariam essa integração — legenda automática e biblioteca de música — já são cobertos pelo pipeline (`subtitles.py` gera karaokê via Whisper, `compose.py` mixa música em volume baixo). Sem necessidade concreta hoje.

Cada skill/MCP integrado ganha aqui uma entrada com: o que faz, como foi instalado, como invocar, e limitações conhecidas.

## Auditoria 2026-07-02 (plugins/repos sugeridos pelo usuário)

**Recomendado — instalar quando for útil:**
- **[bradautomates/claude-video](https://github.com/bradautomates/claude-video)** (skill `/watch`) — **2.9k stars**, 11 commits, mais ativo. Dá ao Claude a capacidade de "assistir" vídeos via yt-dlp + ffmpeg + Whisper (Groq/OpenAI). Extrator de frames com 3 modos de detalhe (`efficient`/`balanced`/`token-burner`), dedup de frames duplicados, suporte a URLs e caminhos locais. Instalável via `/plugin marketplace add bradautomates/claude-video`. Versão atual: v0.2.0 (2026-07-01). Útil para analisar vídeos de referência e revisar outputs.
  - **Prós**: ativo, bem documentado, multi-plataforma, Whisper fallback.
  - **Contras**: requer yt-dlp + ffmpeg já instalados (ambos já temos); usa API externa (Groq/OpenAI) para transcrição se não houver legendas nativas — no nosso caso já temos Whisper local, então usaríamos mais as partes de frame extraction. Testar se o frame extraction funciona bem com vídeos verticais 9:16.

- **[bsisduck/video-analyzer-skill](https://github.com/bsisduck/video-analyzer-skill)** — **9 stars**, alternativa mais simples. Foco em frame extraction + scene detection + transcrição via Whisper CLI local (sem API externa). Usa grids de frames (3x5 portrait, 4x4 landscape) + subagentes paralelos para análise. Vantagem: não depende de API de terceiros para transcrição, compatível com nosso setup atual (já temos openai-whisper).
  - **Contras**: menos estrelas/atualizações, sem suporte a URLs (só arquivos locais), documentação mais enxuta.

**Avaliado — aguardando:**
- **[TwelveLabs Claude Code Plugin](https://github.com/twelvelabs-io/twelve-labs-claude-code-plugin)** — plugin de busca semântica em vídeo (indexação + search + análise via API TwelveLabs). Útil para catalogar/acessar cenas específicas em bibliotecas grandes de vídeo. Instalável via `/plugin marketplace add twelvelabs-io/twelve-labs-claude-code-plugin`. **Aguardando**: requer chave de API TwelveLabs (não temos) e faz sentido quando tivermos um acervo grande o suficiente para justificar busca semântica.
- **[browser-use/video-use](https://github.com/browser-use/video-use)** — skill para Claude Code (symlink em `~/.claude/skills/`, não é MCP) que edita footage bruta de forma genérica: remove filler ("umm"/pausas), color grading, fades de áudio, legendas, overlays animados via HyperFrames/Remotion/Manim/PIL, autoavaliação de cortes, memória em `project.md`. Depende de **API key paga da ElevenLabs** para transcrição/diarização. **Aguardando**: não se encaixa no MVP atual (formato fixo e scriptado, não uma edição "decidida" pelo agente) e trocaria nossa transcrição local grátis (Whisper) por uma dependência de nuvem paga. Reavaliar se expandirmos para os pilares "Review do Squad" ou "Lore & Curiosidade" do brandbook (conteúdo talking-head/montagem sem formato fixo).
- **[heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)** — framework HTML→vídeo determinístico (`npx hyperframes render`), skills-based (não MCP), para overlays animados, legendas cinéticas e vídeos de lançamento de produto. **Aguardando**: nosso style guide pede composição estática, sem overlays animados nem transições elaboradas. Reavaliar se quisermos enriquecer o pilar "Drop & Pré-venda" (35% do conteúdo) com elementos animados além do karaokê ASS atual.

**Avaliado e descartado (não instalar por enquanto):**
- **claude-mem** (thedotmack) — memória persistente entre sessões via SQLite/vector search local. Redundante com o sistema de memória próprio deste projeto (`memory/editing_rules_log.json` + `session_init.md`, versionado no repo). Instalar os dois juntos criaria duas fontes de verdade conflitantes.
- **context-mode** (mksglu) — otimização de context window (sandboxing de output verboso, ex: logs do ffmpeg). Potencialmente útil no futuro se o volume de output do pipeline virar problema real de contexto, mas é uma dependência grande (11 MCP tools, hooks em todo o ciclo de vida) para um problema que ainda não apareceu. Reavaliar se sessões começarem a esgotar contexto por causa de logs de ffmpeg/whisper.
- **superpowers** (obra) — framework de metodologia de dev (TDD estrito, debugging em 4 fases, brainstorming). Faz sentido para software de produto complexo; overhead desnecessário para scripts de pipeline de vídeo. Reavaliar se o projeto crescer para um app completo (Fase futura "app independente e pago").
- **get-shit-done-cc** — sistema de meta-prompting/spec-driven dev. Descontinuado (não mais mantido pelo autor) — evitar depender de ferramenta sem manutenção.
- **frontend-design@claude-plugins-official** — skill para design de UI/frontend web. Sem uso hoje (não há frontend neste projeto); reavaliar se/quando construirmos a interface do "app independente".
- **skill-creator@claude-plugins-official** — já disponível nativamente neste ambiente (skill `anthropic-skills:skill-creator`), não precisa instalar via marketplace separado.
- Planilha "Nate Herk - Video Database" (Google Sheets) — catálogo de vídeos tutoriais sobre automação com IA em geral (Claude Code, n8n, agentes de voz). Não tem conteúdo específico de edição de vídeo; nada para reter daqui.
