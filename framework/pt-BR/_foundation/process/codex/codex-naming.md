# Codex: Convenções de Nomenclatura do Framework

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Nomenclatura e endereçamento de artefatos do Ahrena

## Visão Geral

Este Codex detalha as convenções de nomenclatura definidas na seção `naming` do `.ahrena/.directives`. Complementa a `lex-naming` (que estabelece a obrigação) com exemplos, boas práticas e armadilhas. Use este Codex ao criar ou revisar nomes de arquivos, diretórios e posição de artefatos na taxonomia.

## Contexto

- **Domínio:** Nomenclatura de artefatos e estrutura de diretórios do framework
- **Público-alvo:** Agentes de IA que criam ou movem artefatos; mantenedores do framework
- **Atualização:** Quando as convenções no `.directives` forem alteradas ou novos clades reservados forem definidos

## Conteúdo

### Prefixos por Pilar

O prefixo de cada Pilar é o valor definido em `naming.prefixes` em `.ahrena/.directives` (chaves: `lexis`, `codex`, `katas`, `warriors`, `cries`). Quem define é o usuário ou o projeto; o agente DEVE consultar o arquivo para saber o valor em uso.

| Pilar | Chave em naming.prefixes | Exemplo de arquivo (quando o valor padrão é usado) |
|-------|--------------------------|---------------------------------------------------|
| Lexis | `lexis` | `lex-directives.md`, `lex-pilars.md` |
| Codex | `codex` | `codex-naming.md`, `codex-pilars.md` |
| Katas | `katas` | `kata-create-lexis.md`, `kata-translate.md` |
| Warriors | `warriors` | `warrior-translator.md`, `warrior-daedalus.md` |
| Cries | `cries` | `cry-new-lex.md`, `cry-translate.md` |

Nunca use um prefixo de outro Pilar (ex.: não nomear um Codex como `manual-xyz.md`). O prefixo identifica o tipo do artefato; a identificação é feita pelo valor configurado em `.directives`, não por valor fixo.

### Extensões

| Contexto | Extensão | Exemplo |
|----------|----------|---------|
| Framework (arquivos .md no repo) | `.md` | `lex-pilars.md` |
| Cursor rules | `.mdc` | `lex-pilars.mdc` (gerado a partir do .md) |
| Skills e commands no Cursor | Conforme recurso (ex.: SKILL.md, .md) | Definido pelo instalador |

### Casing

| Elemento | Convenção | Exemplo correto | Exemplo incorreto |
|----------|-----------|-----------------|-------------------|
| Nome de arquivo | kebab-case | `codex-restful-apis.md` | `codex_restful_apis.md`, `codexRestfulApis.md` |
| Nome de diretório | kebab-case | `project_artifacts`, `_foundation` | `ProjectArtifacts`, `_Foundation` |

Nota: clades reservados usam prefixo `_` (ex.: `_foundation`); o restante do nome segue kebab-case.

### Endereçamento (taxonomia)

Padrão: `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}`

| Segmento | Significado | Exemplo |
|----------|-------------|---------|
| `lang` | Código BCP 47 do idioma | `pt-BR`, `es`, `en` |
| `clade` | Disciplina ou domínio de primeiro nível | `_foundation`, `engineering`, `documentation` |
| `subclade` | Área dentro do clade | `authoring`, `platform`, `i18n` |
| `pilar` | Nome do pilar (plural em pastas): lexis, codex, katas, warriors, cries | `lexis`, `codex`, `katas` |
| `prefix-name.ext` | Nome do arquivo com prefixo e extensão | `lex-pilars.md` |

Exemplo completo: `pt-BR/_foundation/authoring/lexis/lex-pilars.md`

### Clades reservados

Definidos em `naming.reserved_clades`. Ex.: `_foundation`.

- Usam prefixo `_` para indicar que são transversais ou especiais.
- Não crie um clade com o mesmo nome sem o prefixo (ex.: não usar `foundation` como clade se `_foundation` for reservado).
- Consulte o `.directives` para a lista atual.

### Tom e estilo (naming.tone_and_writing_style)

A seção `naming.tone_and_writing_style` no `.directives` contém diretrizes de tom e estilo de escrita. Sua aplicação é obrigatória por `lex-tone` e detalhada em `codex-tone`. Não faz parte da nomenclatura de arquivos/diretórios, mas está sob a seção `naming` no arquivo.

### Boas práticas

| Prática | Descrição |
|---------|-----------|
| Nome descritivo após o prefixo | Use `lex-no-secrets` em vez de `lex-1`; o nome deve indicar o conteúdo |
| Consistência entre idiomas | O mesmo artefato em pt-BR, es e en deve ter o mesmo nome de arquivo (ex.: `lex-pilars.md` em todas as pastas de idioma) |
| Evitar siglas obscuras | Prefira `codex-restful-apis` a `codex-ra` se o contexto não for óbvio |
| Subclade específico | Escolha o subclade mais específico que fizer sentido (ex.: `authoring` dentro de `_foundation`) |

### Armadilhas comuns

| Armadilha | Problema | Solução |
|-----------|----------|---------|
| Esquecer o prefixo | Arquivo `directives.md` no diretório lexis | Nomear `lex-directives.md` |
| Casing errado | `Lex-Pilars.md` ou `lex_pilars.md` | Usar kebab-case: `lex-pilars.md` |
| Artefato fora da árvore | Arquivo na raiz de `framework/` ou sem idioma | Posicionar em `{lang}/{clade}/{subclade}/{pilar}/` |
| Pilar como pasta | Nome da pasta deve ser plural (lexis, codex, katas, warriors, cries) | Usar `lexis/`, não `lex/` |

## Glossário

| Termo | Definição |
|-------|-----------|
| Endereçamento | Posição completa do artefato na taxonomia (lang/clade/subclade/pilar/arquivo) |
| Clade reservado | Clade listado em `naming.reserved_clades` com regras especiais (ex.: prefixo `_`) |
| kebab-case | Palavras em minúsculas separadas por hífen (ex.: `lex-no-secrets`) |

## Referências

- `lex-naming` — Lei que obriga o uso das convenções de nomenclatura
- `lex-directives` — Consulta obrigatória ao `.ahrena/.directives`
- `codex-directives` — Manual do arquivo .directives (seção naming)
- `lex-framework-language` — Estrutura de idiomas e primeiro nível de navegação
- `codex-tone` — Aplicação de tone_and_writing_style (sob naming no .directives)
