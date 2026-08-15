---
name: cry-tags
description: "Gerenciar Tags de Sessão. Atalho do usuário para ler, definir, limpar ou re-inferir as tags da sessão Claude Code atual, conforme lex-session-tags"
---

# Cry: Gerenciar Tags de Sessão

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho do usuário para ler, definir, limpar ou re-inferir as tags da sessão Claude Code atual, conforme `lex-session-tags`

## Uso

```
/cry-tags <subcomando> [args]
```

## Subcomandos

| Subcomando | Efeito |
|---|---|
| `set <kind> [topic1] [topic2]` | Substitui o objeto de tags atual pelos valores fornecidos. `kind` DEVE estar em `session_tracking.tags.kinds`; os topics são opcionais. |
| `show` | Imprime o objeto de tags atual para o usuário sem modificar nada. |
| `clear` | Remove a chave `tags` do heartbeat (reseta para "sem tags"). |
| `--auto-suggest` | Força uma nova inferência via `kata-session-tag-suggest` mesmo se `tags` já estiver presente, e então escreve a sugestão via `kata-session-heartbeat`. |

## O que o Comando Faz

1. Lê `session_tracking.tags.*` de `.ahrena/.directives`.
2. Lê o heartbeat atual em `.ahrena/workflow/sessions/<session_id>.json` (quando presente).
3. Despacha por subcomando:
   - `set`: valida `kind` contra o vocabulário configurado; rejeita com um erro de uma linha listando o vocabulário quando inválido. Invoca `kata-session-heartbeat` com o objeto `tags` mesclado.
   - `show`: imprime o objeto `tags` atual (ou `"(sem tags)"` quando ausente).
   - `clear`: invoca `kata-session-heartbeat` passando `tags=null` para remover o campo.
   - `--auto-suggest`: invoca `kata-session-tag-suggest` com o primeiro prompt do usuário (lido da sessão) + front-matter do plano + nome da branch; encadeia a saída JSON para `kata-session-heartbeat --set-tags`.
4. Emite uma confirmação de uma linha no formato `tagged: [kind] [topic1] [topic2]` (ou `tags cleared` / `(sem tags)`).

## Template de Prompt

```
Invoque a kata relevante para o {subcomando}:

- Para `set`: valide o kind contra session_tracking.tags.kinds, depois chame
  kata-session-heartbeat com tags={kind, topics: [...]}.

- Para `show`: leia .ahrena/workflow/sessions/<session_id>.json e imprima o
  objeto tags ou "(sem tags)" quando ausente.

- Para `clear`: chame kata-session-heartbeat com tags=null.

- Para `--auto-suggest`: chame kata-session-tag-suggest com o primeiro
  prompt do usuário da sessão, depois encadeie a saída JSON para
  kata-session-heartbeat --set-tags.

Após qualquer escrita, emita a confirmação de uma linha:
  tagged: [kind] [topic1] [topic2]
ou:
  tags cleared
```

## Exemplos de Invocação

**Definir tags:**

```
/cry-tags set bug reconciliation api
```

Saída:

```
tagged: [bug] [reconciliation] [api]
```

**Mostrar tags atuais:**

```
/cry-tags show
```

Saída:

```
tagged: [tech-task] [session-tags] [foundation]
```

**Limpar:**

```
/cry-tags clear
```

Saída:

```
tags cleared
```

**Forçar re-inferência via auto-sugestão:**

```
/cry-tags --auto-suggest
```

Saída:

```
tagged: [tech-task] [session-tracking] [framework]
```

**Kind inválido:**

```
/cry-tags set documentation
```

Saída (stderr, sem escrita):

```
ERROR: kind 'documentation' não está em session_tracking.tags.kinds.
Kinds configurados: tech-task, bug, spike, user-story, epic, chore, design, review, exploration, release.
```

## Restrições

- NÃO persiste tags em nenhum lugar além do heartbeat JSON — duplicação no front-matter do plano, no corpo da Issue ou em mensagem de commit é proibida pela regra 4 de `lex-session-tags`.
- NÃO inventa valores de `kind` fora de `session_tracking.tags.kinds`. Adições de projeto passam por revisão de PR em `.ahrena/.directives`.
- NÃO opera quando `session_tracking.enabled: false` ou `session_tracking.tags.enabled: false` — sai silenciosamente com uma nota de uma linha.
- NÃO opera fora do Claude Code (sem `CLAUDE_CODE_SESSION_ID`) — sai silenciosamente conforme cláusula de exceção de `lex-session-tags`.
- A saída respeita o tom da Guardia (`lex-tone`, `lex-brand-voice`) — direto, sem buzzwords.

## Diferença para a Kata

| Aspecto | `cry-tags` | `kata-session-heartbeat` / `kata-session-tag-suggest` |
|---|---|---|
| **Natureza** | Atalho do usuário | Procedimentos completos |
| **Invocação** | `/cry-tags <subcomando>` (1 linha) | Chamada pelo `cry-tags` ou por warriors |
| **Conhece o vocabulário?** | Lê de `.directives`, valida entrada do usuário | A kata também valida, mas não apresenta a mensagem de erro ao humano |
| **Saída** | Confirmação de uma linha para o usuário | JSON estruturado + código de saída |
