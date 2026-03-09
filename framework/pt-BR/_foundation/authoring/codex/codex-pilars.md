# Codex: Sistema de Pilares do Ahrena

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Criação e evolução de artefatos do framework

## Visão Geral

Este Codex é a referência central sobre o sistema de Pilares do Ahrena. Descreve a natureza de cada Pilar, como se relacionam entre si, e como o framework utiliza seus próprios artefatos para evoluir — o conceito de autossuficiência.

## Contexto

- **Domínio:** Taxonomia e arquitetura do framework Ahrena
- **Público-alvo:** Agentes de IA e mantenedores do framework
- **Atualização:** Sempre que um novo Pilar for criado ou as relações entre Pilares mudarem

## Conteúdo

### Os Cinco Pilares

O Ahrena organiza todo conhecimento em cinco Pilares, cada um com um papel distinto:

| Pilar | Prefixo | Natureza | Pergunta que responde |
|-------|---------|----------|----------------------|
| **Lexis** | `lex-` | Lei inquebável | "O que é proibido ou obrigatório?" |
| **Codex** | `codex-` | Manual de referência | "O que preciso saber sobre este domínio?" |
| **Katas** | `kata-` | Procedimento repetível | "Como executo esta tarefa passo a passo?" |
| **Warriors** | `warrior-` | Agente especializado | "Quem é responsável por este domínio?" |
| **Cries** | `cry-` | Comando recorrente | "Como invoco esta ação rapidamente?" |

### Hierarquia de Autoridade

Os Pilares possuem uma hierarquia implícita de autoridade:

1. **Lexis** — autoridade máxima. Nenhum outro artefato pode contradizer uma Lexis. São absolutas.
2. **Codex** — fonte de verdade para conhecimento de domínio. Orienta decisões.
3. **Katas** — procedimentos que obedecem Lexis e consultam Codex.
4. **Warriors** — agentes que seguem Lexis, consultam Codex e executam Katas.
5. **Cries** — atalhos que disparam Katas ou invocam Warriors.

### Relações entre Pilares

```
Lexis ─────────── governa ──────────► todos os outros
Codex ─────────── informa ──────────► Katas, Warriors
Katas ─────────── executado por ────► Warriors, agentes genéricos
Warriors ─────── invocado por ──────► Cries, usuários
Cries ──────────── dispara ─────────► Katas (via Warriors ou diretamente)
```

Cada Pilar pode referenciar artefatos de outros Pilares:

| Pilar | Referencia | É referenciado por |
|-------|------------|--------------------|
| Lexis | — | Codex, Katas, Warriors |
| Codex | Lexis | Katas, Warriors |
| Katas | Lexis, Codex | Warriors, Cries |
| Warriors | Lexis, Codex, Katas | Cries |
| Cries | Katas, Warriors | — |

### Kit de Criação

Para que o framework seja autossuficiente, cada Pilar possui um **Kit de Criação** composto por:

| Peça | Pilar | Função |
|------|-------|--------|
| Codex do Pilar | Codex | Conhecimento sobre o que é e como escrever bem |
| Kata de criação | Kata | Procedimento passo a passo para criar um novo artefato |
| Cry de invocação | Cry | Atalho rápido para disparar a criação |

A cadeia de execução é:

```
/cry-new-{pilar} → kata-create-{pilar} → codex-{pilar} + template + lexis
```

### Como Decidir qual Pilar Usar

| Situação | Pilar | Justificativa |
|----------|-------|---------------|
| Preciso estabelecer uma regra absoluta que ninguém pode violar | **Lexis** | Leis não admitem exceções |
| Preciso documentar conhecimento de domínio para consulta | **Codex** | Base de conhecimento estruturada |
| Preciso padronizar como uma tarefa recorrente é executada | **Kata** | Procedimento com inputs, passos e outputs |
| Preciso de um agente dedicado com identidade e escopo | **Warrior** | Especialista com persona e responsabilidades |
| Preciso de um atalho rápido para uma ação do dia a dia | **Cry** | Invocação rápida de 1-2 passos |

Perguntas de refinamento:

- **É uma restrição absoluta?** → Lexis
- **É conhecimento para consulta?** → Codex
- **É um procedimento multi-passo?** → Kata
- **Precisa de persona e escopo contínuo?** → Warrior
- **É uma invocação simples e rápida?** → Cry

### Padrões e Convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| Nomenclatura de arquivo | `{prefixo}-{nome}.md` | `lex-no-secrets.md` |
| Casing | kebab-case | `codex-framework-language.md` |
| Endereçamento | `{lang}/{clade}/{subclade}/{pilar}/{arquivo}` | `pt-BR/engineering/quality/lexis/lex-code-review.md` |
| Criação dual | framework (`.md`) + IDE (formato da plataforma) | `.md` + `.mdc` (Cursor) |

### Restrições Técnicas

- Todo artefato **DEVE** seguir o template oficial do seu Pilar (`templates/{pilar}-sample.md`)
- Todo artefato **DEVE** existir nos idiomas definidos em `language.i18n`
- O idioma padrão (`language.default`) é a fonte da verdade
- Nomes de arquivo usam o prefixo do Pilar e kebab-case
- Termos canônicos (Lexis, Codex, Katas, Warriors, Cries, Clade, Subclade, Pilar) nunca são traduzidos

### Artefatos no projeto (.ahrena)

Artefatos podem ser criados primeiro no **espaço do projeto** (`.ahrena/artifacts/`), específicos para aquele repositório. Isso permite iterar e validar antes de incorporar ao framework canônico.

| Aspecto | Projeto (`.ahrena/artifacts/`) | Framework (`framework/`) |
|---------|-------------------------------|--------------------------|
| **Uso** | Específico do projeto; validação local | Parte do repositório Ahrena; compartilhado |
| **Estrutura** | Mesma do framework: `{lang}/{clade}/{subclade}/{pilar}/{prefixo}-{nome}.md` | `framework/{lang}/{clade}/{subclade}/{pilar}/` |
| **Idiomas** | Pode existir só no idioma padrão; ao fazer Push, os demais são gerados se faltarem | **DEVE** existir em todos os idiomas de `language.i18n` |
| **Quando criar aqui** | Regras ou procedimentos ainda em validação; artefatos que podem nunca ir para o framework | Artefatos estáveis e aprovados para o framework |

**Fluxo recomendado:**

1. **Criar no projeto:** use os Katas de criação (`kata-create-lexis`, `kata-create-codex`, etc.) com destino **projeto** — o artefato é salvo em `.ahrena/artifacts/{lang}/{clade}/{subclade}/{pilar}/`.
2. **Sincronizar com o .cursor:** para que a IDE (Cursor) passe a usar o artefato, execute `python .ahrena/update.py --sync-cursor` ou `make sync-cursor`. O update regera `.cursor/` a partir de `.ahrena/framework/` e `.ahrena/artifacts/`.
3. **Validar:** use e ajuste o artefato no contexto do projeto.
4. **Push para o framework:** quando estiver pronto para incorporar ao framework, execute `kata-push-to-framework` (ou o Cry `cry-push-to-framework`). O procedimento copia os artefatos de `.ahrena/artifacts/` para `framework/`, garante traduções nos idiomas obrigatórios e opcionalmente remove ou mantém a cópia no projeto.

O path canônico do espaço de projeto é definido em `paths.project_artifacts` em `.ahrena/.directives` (valor padrão: `.ahrena/artifacts/`).

## Glossário

| Termo | Definição |
|-------|-----------|
| Pilar | Uma das cinco categorias de artefato do Ahrena |
| Clade | Primeiro nível de organização temática (ex: engineering, documentation) |
| Subclade | Segundo nível de organização dentro de um Clade (ex: quality, i18n) |
| Kit de Criação | Conjunto Codex + Kata + Cry que permite criar novos artefatos de um Pilar |
| Criação dual | Padrão de criar o artefato canônico (`.md`) e a versão derivada para a IDE |
| Endereçamento | Caminho completo de um artefato na taxonomia do framework |
| Artefatos de projeto | Artefatos criados em `.ahrena/artifacts/`, específicos do repositório, antes de serem incorporados ao framework |
| Push para o framework | Procedimento (kata-push-to-framework) que incorpora artefatos de `.ahrena/artifacts/` ao `framework/`, com i18n completo |

## Referências

- `.ahrena/.directives` — Diretivas canônicas do framework
- `lex-template-usage` — Lei de uso obrigatório de templates
- `lex-framework-language` — Lei de estrutura de idiomas
- `codex-lexis`, `codex-codex`, `codex-katas`, `codex-warriors`, `codex-cries` — Codex individuais de cada Pilar
