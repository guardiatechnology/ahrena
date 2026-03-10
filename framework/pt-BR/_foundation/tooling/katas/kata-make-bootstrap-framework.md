# Kata: Bootstrap do framework (Make bootstrap)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Primeira instalação do framework Ahrena via target `bootstrap` do Makefile

## Objetivo

Realizar a **primeira instalação** do framework Ahrena: baixar o instalador do GitHub e executá-lo com as variáveis desejadas (ex.: PLATFORM, TARGET, VERSION, REPO). Equivalente ao target `bootstrap` do Makefile — ou ao comando equivalente em PowerShell quando `make` não estiver disponível.

## Quando Usar

- Quando o usuário invoca `/cry-make bootstrap` (com ou sem variáveis)
- Quando o projeto ainda não tem `.ahrena/` e é a primeira vez que se instala o framework

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Variáveis | Não | Ex.: `PLATFORM=cursor`, `TARGET=.`, `VERSION=main`, `REPO=...`. Consultar `codex-make` |

## Workflow

```
Progresso:
- [ ] 1. Consultar codex-make (equivalência sem Make para bootstrap)
- [ ] 2. Determinar terminal
- [ ] 3. Executar bootstrap (make ou equivalente)
- [ ] 4. Reportar resultado
```

### Passo 1: Consultar codex-make

1. Ler `codex-make` (target `bootstrap` e seção **Equivalência sem Make** para bootstrap)
2. Identificar o comando: `make bootstrap [variáveis]` ou o one-liner PowerShell (baixar install.py, executar, remover)

### Passo 2: Determinar terminal

1. Ler `.ahrena/.directives` (seção `terminal`) conforme `lex-terminal-type`; se ausente, inferir do SO (em bootstrap pode não existir ainda `.ahrena/`; inferir do SO)

### Passo 3: Executar bootstrap

1. Se `make` disponível: executar `make bootstrap [variáveis]` no diretório do projeto
2. Se `make` não disponível: executar o comando da seção "Equivalência sem Make" do `codex-make` para bootstrap (baixar install.py do GitHub, executar com variáveis, remover o script)
3. Capturar saída e código de saída

### Passo 4: Reportar resultado

1. Apresentar a saída ao usuário; em caso de falha, indicar erro e sugerir correção

## Saídas

| Saída | Formato |
|-------|---------|
| Sucesso | Saída do comando de bootstrap |
| Falha | Mensagem de erro e sugestão de correção |

## Referências

- `codex-make` — Target bootstrap e equivalência sem Make
- `lex-terminal-type` — Tipo de terminal
- `cry-make` — Comando que pode invocar este Kata (target `bootstrap`)
