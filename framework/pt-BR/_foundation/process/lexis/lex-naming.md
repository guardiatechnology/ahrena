# Lexis: Convenções de Nomenclatura Obrigatórias

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Nomenclatura e endereçamento de artefatos do framework Ahrena

## Propósito

O Ahrena define convenções de nomenclatura no arquivo `.ahrena/.directives` (seção `naming`): prefixos por Pilar, extensões por contexto, casing para arquivos e diretórios, padrão de endereçamento e clades reservados. Sem uma Lei que obrigue o uso dessas convenções, artefatos podem ser criados com prefixos errados, casing inconsistente ou fora da taxonomia, quebrando a navegabilidade e a governança do framework.

Esta Lexis consolida a obrigação de seguir **naming.prefixes**, **naming.extensions**, **naming.casing**, **naming.addressing** e **naming.reserved_clades** definidos em `.ahrena/.directives`. A consulta ao arquivo é estabelecida pela `lex-directives`; esta Lexis explicita que todo artefato **DEVE** conformar às convenções de nomenclatura.

## Lei

> **Todo artefato do framework Ahrena DEVE seguir as convenções de nomenclatura definidas na seção `naming` de `.ahrena/.directives`: prefixo obrigatório do Pilar (`naming.prefixes`), extensão conforme o contexto (`naming.extensions`), casing para arquivos e diretórios (`naming.casing`), padrão de endereçamento (`naming.addressing`) e respeito aos clades reservados (`naming.reserved_clades`).**

## Regras

### 1. Prefixos

Todo artefato DEVE usar o prefixo do seu Pilar conforme `naming.prefixes` em `.ahrena/.directives`. Os prefixos são definidos pelo usuário ou pelo projeto; as chaves são `lexis`, `codex`, `katas`, `warriors`, `cries`. O agente identifica o tipo do artefato (Lexis, Codex, Kata, etc.) observando qual prefixo configurado o nome do arquivo usa — não assume valores fixos.

Exemplo: se `naming.prefixes.lexis` for `lex-`, arquivo de Lei deve ser nomeado `lex-{nome}.md`; se o projeto definir outro valor (ex.: `lei-`), esse valor é o obrigatório. Nunca usar prefixo de outro Pilar nem omitir o prefixo.

### 2. Extensões

- No framework (árvore `framework/`): usar `naming.extensions.framework` (em geral `.md`).
- No Cursor (rules): usar `naming.extensions.cursor` (em geral `.mdc`).

### 3. Casing

- Arquivos: seguir `naming.casing.files` (em geral kebab-case). Exemplo: `lex-no-secrets.md`.
- Diretórios: seguir `naming.casing.directories` (em geral kebab-case). Exemplo: `engineering/backend/`.

### 4. Endereçamento

Todo artefato no framework DEVE ser posicionado conforme `naming.addressing`. O padrão canônico é:

`{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}`

O idioma é o primeiro nível de navegação (`lex-framework-language`). Nenhum artefato pode ficar fora dessa estrutura (ex.: na raiz de `framework/` sem idioma/clade/subclade/pilar).

### 5. Clades reservados

Os valores em `naming.reserved_clades` (ex.: `_foundation`) são clades especiais. O agente DEVE reconhecê-los e respeitar suas regras (ex.: prefixo `_` para clades transversais). Não criar clades com nomes que conflitem com os reservados.

### 6. Fonte da verdade

As chaves e valores exatos (prefixos, extensões, casing) são definidos em `.ahrena/.directives`. Na ausência do arquivo, o agente DEVE alertar o usuário. Não inferir convenções sem consultar o arquivo (`lex-directives`).

## Abrangência

- **Aplica-se a:** todo artefato criado ou mantido no framework Ahrena e no espaço de projeto (`.ahrena/artifacts/`) quando a estrutura espelha a do framework.
- **Agentes vinculados:** todos os Warriors e agentes genéricos que criam ou nomeiam artefatos.
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Artefato não conformante:** artefato com nome ou posição fora das convenções não deve ser aceito; deve ser renomeado ou movido.
2. **Navegação quebrada:** artefatos fora do endereçamento canônico quebram a taxonomia e a geração correta do `.cursor/`.
3. **Remediação:** o agente deve consultar `.directives` e `codex-naming`, corrigir o nome e o caminho do artefato.

## Exemplos

### Correto

- `framework/pt-BR/_foundation/authoring/lexis/lex-pilars.md` — idioma, clade, subclade, pilar, prefixo e kebab-case.
- `framework/pt-BR/engineering/platform/codex/codex-restful-apis.md` — convenções respeitadas.

### Incorreto

- `framework/lexis/lex-pilars.md` — falta idioma e clade/subclade.
- `framework/pt-BR/_foundation/authoring/lexis/pilars.md` — falta o prefixo do Pilar Lexis (consultar `naming.prefixes.lexis` em `.directives`).
- `framework/pt-BR/_foundation/Authoring/lexis/lex-pilars.md` — diretório não está em kebab-case.

## Validação Automatizada

- **Ferramenta:** verificação pelo agente ao criar ou revisar artefato; possível extensão com script de validação.
- **Momento:** na criação (kata-create-*), na revisão de PR e no push para o framework.
- **Métrica:** 0 artefatos com prefixo incorreto, casing incorreto ou fora do endereçamento canônico.

## Referências

- `lex-directives` — Consulta obrigatória ao `.ahrena/.directives`
- `codex-naming` — Manual de convenções de nomenclatura e exemplos
- `codex-directives` — Significado da seção naming no .directives
- `lex-framework-language` — Idioma como primeiro nível e estrutura de pastas
