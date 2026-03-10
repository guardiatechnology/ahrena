# Kata: Sincronizar .cursor/ (Make sync-cursor)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Regenerar `.cursor/` a partir de `.ahrena/framework/` e `.ahrena/artifacts/` via target `sync-cursor`

## Objetivo

Regenerar o diretório `.cursor/` (rules, skills, commands, agents) a partir de `.ahrena/framework/` e `.ahrena/artifacts/`, **sem baixar** nada do remoto. Equivalente ao target `sync-cursor` do Makefile — ou ao comando equivalente em PowerShell/Python quando `make` não estiver disponível.

## Quando Usar

- Quando o usuário invoca `/cry-make sync-cursor` (com ou sem variáveis, ex.: TARGET)
- Quando foi alterado o conteúdo de `.ahrena/framework/` ou `.ahrena/artifacts/` e é necessário refletir em `.cursor/`
- Após criar ou editar artefatos no projeto que precisam aparecer no Cursor

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Variáveis | Não | Ex.: `TARGET=.`. Consultar `codex-make` |

## Workflow

```
Progresso:
- [ ] 1. Consultar codex-make (equivalência sem Make para sync-cursor)
- [ ] 2. Verificar .ahrena/update.py e .ahrena/.directives
- [ ] 3. Determinar terminal
- [ ] 4. Executar sync-cursor (make ou equivalente)
- [ ] 5. Reportar resultado
```

### Passo 1: Consultar codex-make

1. Ler `codex-make` (target `sync-cursor` e seção **Equivalência sem Make**)
2. Identificar o comando: `make sync-cursor [variáveis]` ou `python .ahrena/update.py --target . --sync-cursor`

### Passo 2: Verificar .ahrena/update.py e .ahrena/.directives

1. Verificar que o projeto tem `.ahrena/update.py` e `.ahrena/.directives` (instalação prévia do Ahrena)
2. Se não existir, informar que é necessário instalar antes (`/cry-make install` ou bootstrap)

### Passo 3: Determinar terminal

1. Ler `.ahrena/.directives` (seção `terminal`) conforme `lex-terminal-type`; se ausente, inferir do SO

### Passo 4: Executar sync-cursor

1. Se `make` disponível: executar `make sync-cursor [variáveis]` no diretório do projeto
2. Se `make` não disponível: executar `python .ahrena/update.py --target <TARGET> --sync-cursor` conforme codex-make
3. Capturar saída e código de saída

### Passo 5: Reportar resultado

1. Apresentar a saída ao usuário; em caso de falha, indicar erro e sugerir correção

## Saídas

| Saída | Formato |
|-------|---------|
| Sucesso | Saída do comando sync-cursor |
| Falha | Mensagem de erro e sugestão de correção |

## Referências

- `codex-make` — Target sync-cursor e equivalência sem Make
- `lex-terminal-type` — Tipo de terminal
- `cry-make` — Comando que pode invocar este Kata (target `sync-cursor`)
