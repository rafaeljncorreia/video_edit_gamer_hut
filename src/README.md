# Pipeline — Anúncio de Mercado Livre (Gamer Hut)

Automação do formato descrito em [`docs/brand/style-guide-video.md`](../docs/brand/style-guide-video.md): capa (3s) → trailer (fundo desfocado + centro nítido) → narração + legenda karaokê + música baixa.

## Setup (uma vez)

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

Requer `ffmpeg` e `ffprobe` no PATH.

> A instalação usa `openai-whisper` (não `faster-whisper`) porque a dependência `PyAV` do faster-whisper é bloqueada nesta máquina por uma política de Controle de Aplicativo do Windows (DLL não assinada). `openai-whisper` usa PyTorch + chamadas de `ffmpeg` via subprocess, sem esse problema.

## Convenção de pasta por vídeo

Crie `media/raw/<slug>/` (ex: `media/raw/mortal-kombat-1/`) com:

| Arquivo | Obrigatório | Descrição |
|---|---|---|
| `cover.mp4` | sim | vídeo da capa do jogo, **mínimo 3s** |
| `trailer.mp4` | sim | trailer horizontal do jogo (qualquer duração — repete em loop se for mais curto que a narração) |
| `narration.wav` / `.mp3` | sim | narração gravada pelo usuário |
| `music.mp3` | não | música de fundo (repete em loop se for curta; toca bem baixo sob a narração) |

## Uso

```
# 1) transcreve a narração com timestamp por palavra
python src/build_ad.py transcribe media/raw/<slug>

# 2) REVISE media/raw/<slug>/transcript_words.json — corrija nomes de jogos e
#    palavras que a transcrição possa ter errado. NÃO altere start/end.

# 3) gera a legenda karaokê final e renderiza o vídeo
python src/build_ad.py render media/raw/<slug>
```

Saída: `media/output/<slug>.mp4` (1080x1920, 30fps).

## Detalhes de implementação

- `pipeline/transcribe.py` — Whisper local (`openai-whisper`, modelo `small` por padrão, `--model` para trocar) com `word_timestamps=True`.
- `pipeline/subtitles.py` — agrupa palavras em blocos de legenda e gera um `.ass` com uma linha `Dialogue` por palavra, alternando a cor da palavra ativa (laranja `#F26641`) — efeito karaokê estilo CapCut.
- `pipeline/compose.py` — monta o vídeo final em **múltiplos passes** de ffmpeg (capa, trailer composto, concat, mixagem de áudio, queima de legenda), cada um com uma única saída simples. Isso é proposital: um único `filter_complex` grande combinando trim + concat + overlay(boxblur) nesta build do ffmpeg (`N-125093-gd2d371d10d`) produzia frames corrompidos (conteúdo da capa vazava para dentro da faixa nítida do trailer) — reproduzido isoladamente e contornado com arquivos intermediários. Se atualizar o ffmpeg, vale re-testar se um grafo único passa a funcionar.

## Limitações conhecidas / pendências

- A fonte da marca (**Russo One**) não está instalada no sistema — o ffmpeg cai para uma fonte padrão (Arial Bold no Windows) ao queimar a legenda. Para usar a fonte correta, baixe `Russo One` (Google Fonts) e instale no Windows, ou passe `fontsdir` para o filtro `ass` em `compose.py`.
- Antes de gerar a `narration.wav`/`.mp3` real, teste com o comando `transcribe` para conferir a qualidade da transcrição em português.
