# Gamer Hut — Guia de Estilo de Vídeo (Fase 0)

> Confirmado a partir de 21 vídeos de referência (anúncios de Mercado Livre) em `media/reference/`, mais a descrição do usuário. Formato analisado: vertical 1080x1920, 30fps.

## Formato: Anúncio de Mercado Livre (foco atual do MVP)

Estrutura fixa, em 3 blocos:

1. **Capa (0–3s)** — vídeo (não imagem estática) da caixa/capa física do jogo sendo mostrada em mãos. Sem legenda nesse trecho. Sem narração ainda.
2. **Trailer composto** — a partir do momento em que a capa termina:
   - **Fundo**: o trailer horizontal do jogo, escalado para preencher a tela toda (9:16) e **desfocado** (blur).
   - **Centro**: o mesmo clipe do trailer, **nítido**, ocupando uma faixa horizontal central de ~1/3 da altura vertical — a "tela inteira" do trailer cabe nessa faixa (letterboxed, sem crop, mantendo aspect ratio original do trailer).
3. **Narração + legenda** — a narração (voz do usuário) começa **exatamente** quando a capa termina (não durante a capa). Legenda sincronizada com a narração, estilo karaokê: texto branco em negrito com contorno/sombra preta, com a **palavra sendo falada no momento destacada em laranja** (Orange Sunset `#F26641`), as demais em branco. Fonte com peso forte (compatível com Russo One / bold sans), posicionada no terço inferior da tela.

## Áudio

- **Vídeo original (capa e trailer) não tem som próprio no anúncio final** — todo áudio de câmera/trailer é removido.
- **Narração**: única fonte de voz, começa junto com o trailer composto (pós-capa), volume principal.
- **Música de fundo**: presente sob a narração inteira, em volume bem baixo (não pode competir com a voz).
- Todo o restante do vídeo (cortes, blocos visuais) permanece mudo exceto narração + música.

## Legendas — pontos de atenção conhecidos

- Geradas automaticamente (hoje via IA de legenda do CapCut) a partir da narração.
- **Precisam de revisão manual**: nomes de jogos e termos específicos frequentemente saem errados/confusos na transcrição automática — este é um ponto explícito de correção humana antes de finalizar, e deve virar um passo do pipeline (gerar transcrição → revisar/corrigir → só então renderizar legenda final).

## Ritmo de corte
Dentro do bloco de trailer, não há recortes adicionais visíveis nas amostras analisadas — é o próprio trailer rodando (fundo desfocado + centro nítido) enquanto a narração conduz o ritmo. Não confundir com b-roll de múltiplos clipes — por vídeo de anúncio há tipicamente 1 trailer + 1 capa.

## Transições
Corte seco entre capa e bloco de trailer (sem transição elaborada observada nas amostras).

## Hooks de abertura
A capa física do jogo em mãos já funciona como hook visual (reconhecimento imediato do produto) antes de qualquer texto.

## Estrutura por pilar editorial
Este formato de anúncio de Mercado Livre é a aplicação prática do pilar **Drop & Pré-venda** (ver [gamer-hut-brandbook.md](gamer-hut-brandbook.md)) — foco em apresentação direta do produto físico + trailer do jogo, sem storytelling longo de Lore & Curiosidade.

---
*Este documento deve ser lido no início de toda sessão de edição (ver [`memory/session_init.md`](../../memory/session_init.md)).*
