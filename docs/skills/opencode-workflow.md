# Fluxo de colaboração: Claude Code + OpenCode

> Definido em 2026-07-03, a pedido do usuário — objetivo é gastar menos créditos Claude/Anthropic no processo de edição, delegando trabalho pesado/repetitivo para o OpenCode.

## O que é

O usuário roda o **app desktop do OpenCode** (`OpenCode.exe`, instalado em `%LOCALAPPDATA%\Programs\@opencode-aidesktop\`), configurado com **Deepseek V4 Flash grátis** via OpenRouter/Google AI Studio/Zen.

Importante: isso **não é um MCP nem uma CLI acessível via Bash** neste ambiente — é um app Electron separado que o usuário abre e opera manualmente. Não há binário `opencode` no PATH (confirmado via `where opencode` / `Get-Command opencode`), então Claude Code não consegue chamá-lo por subprocesso. A integração é um protocolo de handoff manual, não uma automação direta.

## Divisão de trabalho

| | Claude Code | OpenCode (Deepseek grátis) |
|---|---|---|
| Papel | Orquestração, julgamento de marca, revisão final | Execução pesada/iterativa |
| Exemplos | Ajustar `style-guide-video.md`, decidir estrutura do pipeline, revisar output de vídeo contra o brandbook, registrar regras em `editing_rules_log.json` | Implementar uma função nova em `compose.py`, debugar um erro repetitivo do ffmpeg testando várias variações, escrever boilerplate/testes |
| Custo | Créditos Anthropic (pagos) | Grátis |

Regra prática: se a tarefa exige entender a marca Gamer Hut ou tomar uma decisão de produto, fica com Claude Code. Se é "malhar código até funcionar" sem julgamento de marca envolvido, delega pro OpenCode.

## Template de handoff

Quando uma tarefa for delegada, Claude Code escreve uma especificação com estes campos (o usuário cola no app OpenCode):

```
## Objetivo
[o que precisa ser feito, em 1-2 frases]

## Contexto
- CLAUDE.md: [regras relevantes]
- Arquivos envolvidos: [caminhos]
- Regras técnicas relevantes: [entradas de memory/editing_rules_log.json que se aplicam]

## Critério de aceite
[como saber que terminou — ex: comando que deve rodar sem erro, output esperado]

## Não fazer
[armadilhas conhecidas — ex: não combinar trim+concat+overlay num único filter_complex do ffmpeg, ver compose.py]
```

## Segurança contra edições concorrentes

Como o OpenCode pode estar rodando ao mesmo tempo que uma sessão do Claude Code, antes de começar a editar arquivos:

1. Rodar `git status --short` e `git diff --stat` para checar mudanças não commitadas que não vieram desta sessão.
2. Evitar editar os mesmos arquivos que o OpenCode estiver mexendo na mesma janela de tempo — perguntar ao usuário se há uma tarefa OpenCode em andamento antes de tocar em arquivos que ele citou.
3. Preferir tarefas em arquivos/módulos diferentes por vez, para não gerar conflito de merge.
