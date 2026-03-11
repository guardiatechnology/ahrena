# Codex: Manual do Arquivo .directives

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Configuração canônica do framework Ahrena

## Visão Geral

Este Codex documenta o arquivo `.ahrena/.directives`, que centraliza as configurações canônicas do framework. Descreve o propósito de cada seção, o significado das chaves e quando usar cada path ou opção. É o manual de referência que complementa a `lex-directives` (que estabelece a obrigação de ler e aplicar o arquivo). Consulte a Lex para a lei; consulte este Codex para interpretar e estender o `.directives`.

## Contexto

- **Domínio:** Configuração transversal do Ahrena (paths, idiomas, terminal, naming, tom)
- **Público-alvo:** Agentes de IA, mantenedores do framework e integradores que instalam ou customizam o Ahrena
- **Atualização:** Sempre que uma nova seção for adicionada ao `.directives` ou o significado de uma chave for alterado

## Conteúdo

### Propósito do arquivo

O `.directives` é o ponto único de verdade para:

- Caminhos canônicos do framework (onde estão templates, artefatos, specs)
- Idioma padrão e idiomas obrigatórios para artefatos
- Tipo de terminal para comandos (bash ou PowerShell)
- Convenções de nomenclatura (prefixos, extensões, casing, endereçamento, clades reservados)
- Tom e estilo de escrita para artefatos e comunicação

Nenhum agente deve inferir esses valores sem consultar o arquivo (conforme `lex-directives`).

### Seção `paths`

| Chave | Significado | Uso |
|-------|-------------|-----|
| `paths.root` | Diretório raiz do framework no projeto | `.ahrena/` — ponto de entrada em qualquer projeto que adota o Ahrena |
| `paths.directives` | Caminho do arquivo de diretivas | `.ahrena/.directives` — sempre relativo à raiz do repositório |
| `paths.templates` | Diretório de templates no repositório do framework | `templates/` — contém os samples (lex, codex, kata, warrior, cry) |
| `paths.framework` | Diretório do framework no repo Ahrena | `framework/` — árvore por idioma e clade |
| `paths.project_artifacts` | Onde criar artefatos específicos do projeto antes de ir para o framework | `.ahrena/artifacts/` — mesma estrutura que o framework |
| `paths.oas` | Destino de especificações OpenAPI | Ex.: `docs/oas` — criado pelo instalador ou pelo agente se ausente |
| `paths.events` | Destino de documentação CloudEvents | Ex.: `docs/events` |
| `paths.samples.lexis` | Caminho do template de Lexis | Ex.: `templates/lex-sample.md` |
| `paths.samples.codex` | Caminho do template de Codex | Ex.: `templates/codex-sample.md` |
| `paths.samples.katas` | Caminho do template de Katas | Ex.: `templates/kata-sample.md` |
| `paths.samples.warriors` | Caminho do template de Warriors | Ex.: `templates/warrior-sample.md` |
| `paths.samples.cries` | Caminho do template de Cries | Ex.: `templates/cry-sample.md` |

Ao criar artefatos, use sempre os caminhos de `paths.samples` (ou o equivalente em `.directives`) para localizar o template. Para detalhes sobre quando usar `project_artifacts` vs `framework`, consulte `codex-paths`.

### Seção `language`

| Chave | Significado | Uso |
|-------|-------------|-----|
| `language.default` | Idioma padrão do framework | Ex.: `pt-BR` — artefatos são criados primeiro neste idioma; fonte da verdade |
| `language.i18n` | Lista de idiomas obrigatórios | Ex.: `pt-BR`, `es`, `en` — todo artefato no framework deve existir em todos |
| `language.cursor` | Idioma usado nos artefatos gerados para o Cursor (`.mdc`) | Ex.: `en` — único idioma no `.cursor/`; não há pastas por idioma |

Consulte `lex-framework-language` e `codex-framework-language` para a estrutura de pastas por idioma.

### Seção `terminal`

| Chave | Significado | Uso |
|-------|-------------|-----|
| `terminal` | Tipo de shell para comandos | Valores: `bash` ou `powershell` — agentes devem usar esse tipo ao propor ou executar comandos (ver `lex-terminal-type` e `codex-terminal-type`) |

Se ausente, o agente infere pelo sistema operacional ou pergunta ao usuário.

### Seção `naming`

| Chave | Significado | Uso |
|-------|-------------|-----|
| `naming.prefixes.lexis` | Prefixo de arquivos Lexis | `lex-` |
| `naming.prefixes.codex` | Prefixo de arquivos Codex | `codex-` |
| `naming.prefixes.katas` | Prefixo de arquivos Katas | `kata-` |
| `naming.prefixes.warriors` | Prefixo de arquivos Warriors | `warrior-` |
| `naming.prefixes.cries` | Prefixo de arquivos Cries | `cry-` |
| `naming.extensions.framework` | Extensão no framework | `.md` |
| `naming.extensions.cursor` | Extensão no Cursor (rules) | `.mdc` |
| `naming.casing.files` | Convenção para nomes de arquivo | Ex.: `kebab-case` |
| `naming.casing.directories` | Convenção para nomes de diretório | Ex.: `kebab-case` |
| `naming.addressing` | Padrão de endereçamento de artefatos | `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}` |
| `naming.reserved_clades` | Clades com regras especiais (prefixo `_`) | Ex.: `_foundation` |
| `naming.tone_and_writing_style` | Lista de diretrizes de tom e estilo | Aplicadas ao produzir artefatos e comunicação (ver `lex-tone` e `codex-tone`) |

Consulte `codex-naming` para detalhes e exemplos; consulte `lex-naming` para a lei que obriga o uso dessas convenções.

### Cabeçalho de artefatos (bloco de citação)

Na primeira linha de todo artefato do framework (Lexis, Codex, Katas, Warriors, Cries), o bloco de citação contém **Prefixo**, **Tipo** e **Escopo**. O campo **Prefixo** **DEVE** indicar o **valor efetivo do prefixo** (ex.: `lex-`, `codex-`, `kata-`, `warrior-`, `cry-`), e **NÃO** apenas uma referência à diretiva.

| Forma | Correto | Incorreto |
|-------|---------|-----------|
| **Prefixo** | `**Prefixo:** \`lex-\` \| **Tipo:** ...` | `**Prefixo:** conforme naming.prefixes.lexis em .directives \| ...` |
| Motivo | O artefato é autodescritivo; o leitor vê imediatamente o prefixo do Pilar | A referência à diretiva exige consulta ao `.directives` para saber o valor; em documentação impressa ou fora do contexto do repo, o prefixo fica ambíguo |

O valor do prefixo deve ser o mesmo definido em `naming.prefixes.{pilar}` no `.directives` (no repositório Ahrena, tipicamente `lex-`, `codex-`, `kata-`, `warrior-`, `cry-`). Ao criar ou revisar artefatos, use o valor real do prefixo no cabeçalho.

### Extensibilidade

Novas seções podem ser adicionadas ao `.directives` (ex.: `security`, `notifications`). O agente deve interpretar seções desconhecidas de forma razoável. O arquivo **NÃO DEVE** ser modificado pelo agente sem solicitação explícita do usuário (`lex-directives`).

### Relação com lex-directives

- **lex-directives:** estabelece que todo agente DEVE ler e aplicar o `.directives` antes de produzir artefatos ou comunicação. Define aplicação por seção (paths, language, naming.*).
- **codex-directives:** explica o que cada seção e chave significam e quando usá-las. Use a Lex para a obrigação; use este Codex para interpretação e referência rápida.

## Glossário

| Termo | Definição |
|-------|-----------|
| Diretiva | Par de chave-valor (ou estrutura aninhada) no arquivo `.directives` que governa um aspecto do comportamento do framework |
| Caminho canônico | Path definido em `paths` que todos os agentes devem usar ao referenciar ou criar artefatos |
| Fonte da verdade | O idioma definido em `language.default`; versões em outros idiomas devem ser equivalentes a ele |

## Referências

- `lex-directives` — Lei de consulta obrigatória ao `.directives`
- `codex-paths` — Manual dos caminhos canônicos (paths.*)
- `codex-naming` — Manual de convenções de nomenclatura
- `codex-tone` — Aplicação de tone_and_writing_style
- `.ahrena/.directives` — Arquivo canônico (localização em `paths.directives`)
