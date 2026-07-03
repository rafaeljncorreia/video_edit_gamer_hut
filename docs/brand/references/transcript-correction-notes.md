# Notas de Correção de Transcrição — Vídeos de Referência

> Primeira passada de sugestão de correção baseada nos nomes de arquivo em `media/reference/`.
> **Nunca aprovar sem revisão** — estas são suposições a validar com o usuário e/ou com a escuta do áudio real.

## Erros óbvios nos nomes de arquivo (prováveis erros de legenda também)

### 1. `Mighty Morfing Ritas Rewind.mp4`
- **Como está**: "Morfing" e "Ritas"
- **Provável correção**: *Mighty Morphin' Power Rangers: Rita's Rewind*
- **Contexto**: jogo lançado em 2024/2025, publicado por Digital Eclipse
- **Risco**: nome do arquivo pode ter sido encurtado propositalmente

### 2. `Monster unter Iceborn.mp4`
- **Como está**: "Monster unter Iceborn"
- **Provável correção**: *Monster Hunter: Iceborne*
- **Contexto**: expansão de Monster Hunter World, lançamento mundial. "unter" é alemão e não faz sentido em português — provável corrupção do nome do arquivo
- **Risco**: ALTO — precisa confirmar com o usuário qual é o jogo real

### 3. `Everybodys's Golf.mp4`
- **Como está**: "Everybodys's"
- **Provável correção**: *Everybody's Golf*
- **Contexto**: franquia da Sony. Um apóstrofo extra

### 4. `Noob The Factionless.mp4`
- **Como está**: "The Factionless"
- **Provável correção**: *Noob: The Factionless*
- **Contexto**: jogo francês baseado no universo Noob. Falta dois-pontos no título

### 5. `Pokemon Legends of Arceus.mp4`
- **Como está**: "Legends of Arceus"
- **Provável correção**: *Pokémon Legends: Arceus*
- **Contexto**: título oficial não tem "of". Também falta acento em Pokémon
- **Observação**: Whisper provavelmente vai transcrever "Pokémon" sem acento — é uma correção esperada

### 6. `Top Spin 2k25.mp4`
- **Como está**: "2k25"
- **Provável correção**: *TopSpin 2K25*
- **Contexto**: nomenclatura oficial: "TopSpin 2K25" (com "K" maiúsculo e espaço)

### 7. `Lunar remastered.mp4`
- **Como está**: tudo minúsculo
- **Provável correção**: *Lunar Remastered* (com "R" maiúsculo)
- **Contexto**: collection *Lunar Remastered Collection*

### 8. `Alex Kid Miracle World DX.mp4`
- **Como está**: "Kid"
- **Provável correção**: *Alex Kidd in Miracle World DX*
- **Contexto**: nome oficial usa "Kidd" (com dois "d") e "in" entre Alex e Kidd

## Nomes que parecem corretos (mas validar com áudio)

| Arquivo | Título esperado | Confiança |
|---|---|---|
| Arcadegeddon.mp4 | *Arcadegeddon* | Alta |
| Atari Flashback Classics.mp4 | *Atari Flashback Classics* | Alta |
| Disney Aladdin The Lion King.mp4 | *Disney Aladdin & The Lion King* (ou similar) | Média — confirmar se é "and" ou "&" |
| Doinksoft Collection.mp4 | *Doinksoft Collection* | Alta |
| Ezio Collection.mp4 | *Ezio Collection* (ou *Assassin's Creed: The Ezio Collection*) | Alta |
| Monster Jam Showdown.mp4 | *Monster Jam Showdown* | Alta |
| Mortal Kombat 1.mp4 | *Mortal Kombat 1* | Alta |
| Nintendo Switch Sports.mp4 | *Nintendo Switch Sports* | Alta |
| Overcooked 1 + 2.mp4 | *Overcooked 1 + 2* (coleção) | Alta |
| Overpass 2.mp4 | *Overpass 2* | Alta |
| Streets of Rage 4.mp4 | *Streets of Rage 4* | Alta |
| Tchia.mp4 | *Tchia* | Alta |
| Theatrhythm Final Fantasy.mp4 | *Theatrhythm Final Fantasy* | Média — pode ser *Theatrhythm Final Bar Line*? Confirmar |

## Padrões gerais de erro esperados do Whisper

Com base na experiência documentada no style-guide-video.md e no comportamento típico do Whisper:

1. **Nomes de jogos em inglês** → Whisper pode aportuguesar ("Arcadegeddon" → "arcade gedon")
2. **Números no título** → "2K25" pode virar "dois k vinte e cinco"
3. **& (e comercial)** → pode ser transcrito como "and" ou "e" dependendo da narração
4. **Siglário** → "DX" pode virar "de xis"
5. **Termos técnicos** → "steelbook", "lacrado", "publisher" podem ser transcritos de forma estranha

## Processo recomendado

1. Antes de cada `render`, revisar `transcript_words.json`:
   - Corrigir `"word"` para o texto correto
   - **NUNCA** alterar `start`/`end`
2. Verificar nomes de jogos primeiro (são os que o Whisper mais erra)
3. Confirmar com usuário os casos de alta incerteza (#2 "Monster unter Iceborn" principalmente)
