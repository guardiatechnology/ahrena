---
name: cry-checkpoint
description: "Salvar Checkpoint de Sessão. Atalho do usuário para gravar .checkpoint sob demanda, conforme lex-checkpoint"
---

# Cry: Salvar Checkpoint de Sessão

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho do usuário para gravar `.checkpoint` sob demanda, conforme `lex-checkpoint`

## Uso

```
/cry-checkpoint
```

Sem argumentos por padrão. O agente coleta contexto da sessão e grava.

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `--focus "<frase>"` | Não | Sobrescreve o Session focus inferido pelo agente | `--focus "Revisando plan-026"` |
| `--add-thread "<linha>"` | Não | Acrescenta uma Open thread ao checkpoint atual | `--add-thread "Avaliar X"` |
| `--note "<texto>"` | Não | Acrescenta texto às Notes | `--note "Link: https://..."` |
| `--dry-run` | Não | Mostra o conteúdo que seria gravado sem persistir | — |

Sem flags, o agente infere todos os campos do contexto da sessão.

## O que o Comando Faz

1. Invoca `kata-checkpoint-save`
2. O kata coleta Session focus, Active plans, Open threads e Notes do contexto da sessão
3. Valida que conteúdo não duplica plano
4. Grava `.checkpoint` na raiz do workspace com schema canônico
5. Apresenta confirmação ao usuário

## Prompt Template

```
Invocar kata-checkpoint-save com:

- Workspace root: {{pwd}}
- Session focus: {{--focus se fornecido, senão inferir do contexto da sessão}}
- Active plans: {{inferir dos planos com status: in-progress no provider cache (.claude/plans/ para Claude Code; .cursor/plans/ para Cursor)}}
- Open threads: {{coletar do contexto + adicionar --add-thread se fornecido}}
- Notes: {{coletar do contexto + acrescentar --note se fornecido}}
- Dry-run: {{--dry-run flag}}

Após gravação, apresentar confirmação ao usuário no formato:

✅ Checkpoint salvo em `.checkpoint`:
   - Session focus: {primeira frase, max 100 chars}
   - Active plans: {N}
   - Open threads: {N}
   - Notes: {presente | vazio}
```

## Restrições

- NÃO modifica planos (`plan-*.md` no provider cache `.claude/plans/` ou `.cursor/plans/`) — `cry-checkpoint` cobre apenas `.checkpoint`
- NÃO grava conteúdo que duplica plano — kata-checkpoint-save valida e bloqueia
- Output respeita o tom Guardia (`lex-tone`, `lex-brand-voice`) — direto, sem buzzwords
- Não comita `.checkpoint` — segue gitignore per `lex-checkpoint` rule 4
- `--dry-run` mostra mas não grava
