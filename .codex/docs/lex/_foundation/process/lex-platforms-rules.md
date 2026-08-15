# Lexis: Regra obrigatória em platforms.yaml para Lexis e Codex

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Criação de Lexis e Codex no framework Ahrena

## Lei

> **Todo Lexis e todo Codex criado no framework DEVE ter uma entrada correspondente em `cursor.rules` em `framework/platforms.yaml`. A entrada DEVE incluir ao menos a chave `description`.**

## Regras

### 1. Entrada obrigatória

Para cada artefato Lexis ou Codex (arquivo `lex-*.md` ou `codex-*.md` no framework), deve existir em `cursor.rules` uma chave igual ao **rule key** do artefato (caminho relativo ao framework sem idioma e sem `.md`). Ex.: `_foundation/process/lexis/lex-directives`, `documentation/i18n/codex-language-ptbr`.

### 2. Chave `description` obrigatória

Cada entrada em `cursor.rules` **DEVE** conter a chave **`description`** com um texto que oriente a plataforma (ex.: Cursor) a aplicar a rule de forma inteligente. As chaves `alwaysApply` e `globs` são opcionais (default: alwaysApply false; sem globs).

### 3. Momento da criação

Ao criar um novo Lexis ou Codex (via kata-create-lexis, kata-create-codex ou fluxo equivalente), o agente **DEVE** adicionar imediatamente a entrada em `framework/platforms.yaml` em `cursor.rules`, com ao menos `description`. O sync (`python .ahrena/update.py --sync-cursor`) falhará se algum lex/codex não estiver listado.

### 4. Override no projeto

O projeto pode definir ou sobrescrever entradas em `.ahrena/platforms.yaml`. A obrigação aplica-se à existência da entrada (no default ou no override); a fonte pode ser o framework ou o projeto.
