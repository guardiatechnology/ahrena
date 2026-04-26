# Ahrena — Conceitos

## Os Cinco Pilares

O Ahrena organiza todo o conhecimento e as capacidades em cinco Pilares. Cada Pilar tem um papel distinto, um prefixo canônico e uma posição na hierarquia de autoridade.

```
Lexis  (autoridade)
  └── governa todos
Codex  (conhecimento)
  └── orienta Katas e Warriors
Katas  (execução)
  └── aplicados por Warriors; invocados por Cries
Warriors  (orquestração)
  └── orquestram Katas; invocados por Cries
Cries  (pontos de entrada)
  └── invocam Katas ou Warriors; nunca Lexis ou Codex diretamente
```

### Lexis

> **"Lei inquebrável. Não admite exceção."**

| Propriedade | Valor |
|---|---|
| Prefixo | `lex-` |
| Autoridade | Máxima — governa todos os outros Pilares |
| Pode ser invocado por | Nunca invocado diretamente; consultado por Codex, Katas, Warriors |
| Exceções | Nenhuma. Uma Lexis é absoluta. |

Uma Lexis estabelece uma regra que todo agente, humano ou AI, deve seguir em qualquer contexto. Violar uma Lexis não é um problema técnico — é uma violação de governança. Exemplos: `lex-signed-commits`, `lex-issue-driven`, `lex-brand-colors`.

---

### Codex

> **"Manual de referência. Organiza o conhecimento para orientar decisões."**

| Propriedade | Valor |
|---|---|
| Prefixo | `codex-` |
| Autoridade | Segunda — fonte de verdade para o conhecimento |
| Pode ser invocado por | Consultado por Katas e Warriors; não invocado por Cries |
| Exceções | N/A — Codex orienta, não impõe |

Um Codex é um documento de referência detalhado. Ele explica *como* as coisas funcionam, *por que* são estruturadas de determinada forma e *quando* aplicar diferentes abordagens. Exemplos: `codex-restful-apis`, `codex-python-architecture`, `codex-brand-voice`.

---

### Katas

> **"Skill reproduzível. Aplica Lexis e consulta Codex para executar uma tarefa clara e reproduzível."**

| Propriedade | Valor |
|---|---|
| Prefixo | `kata-` |
| Autoridade | Terceira — executa aplicando Lexis e consultando Codex |
| Pode ser invocado por | Cries (diretamente ou via Warrior); Warriors |
| Exceções | N/A |

Um Kata é uma skill executável — um procedimento que o agente segue passo a passo. Quando invocado, um Kata tem uma entrada definida, uma sequência de passos e uma saída definida. Exemplos: `kata-contributing-issue`, `kata-api-design-oas`, `kata-quality-gate`.

---

### Warriors

> **"Agente especializado. Orquestra um ou mais Katas."**

| Propriedade | Valor |
|---|---|
| Prefixo | `warrior-` |
| Autoridade | Quarta — orquestra Katas; consulta Lexis e Codex |
| Pode ser invocado por | Cries ou usuários |
| Exceções | N/A |

Um Warrior é um agente de AI especializado com expertise de domínio. Ele seleciona, sequencia e combina Katas para alcançar objetivos complexos. Warriors são declarados com um papel, uma persona e um conjunto de ferramentas. Exemplos: `warrior-athena` (workflow), `warrior-apollo` (backend), `warrior-hephaestus` (frontend).

---

### Cries

> **"Comando de alto nível. Ativa um Kata ou Warrior."**

| Propriedade | Valor |
|---|---|
| Prefixo | `cry-` |
| Autoridade | Quinta — pontos de entrada; invocam apenas Katas ou Warriors |
| Pode ser invocado por | Usuários |
| Exceções | Cries NÃO DEVEM invocar Lexis nem acessar Codex diretamente |

Um Cry é um comando voltado ao usuário — os comandos `/` que os usuários digitam para acionar uma capacidade. Um Cry é o ponto de entrada do framework. Exemplos: `/cry-implement-issue`, `/cry-new-lex`, `/cry-api-design`.

---

## Regras de Invocação

```
Usuário
  → invoca → Cry
               → invoca → Kata (um para um)
               → invoca → Warrior (um para vários Katas)
                            → orquestra → Katas
                                          → aplicam → Lexis
                                          → consultam → Codex
```

**Restrição crítica:** Um Cry que precisa de múltiplos Katas DEVE invocar um Warrior que os orquestre. Um Cry não deve invocar Katas diretamente se mais de um for necessário.

---

## Clades e Subclades

O framework organiza os artefatos por **disciplina** usando uma taxonomia de dois níveis:

```
Clade (disciplina)
  └── Subclade (área dentro da disciplina)
        └── Diretório do Pilar (lexis/ codex/ katas/ warriors/ cries/)
              └── artefatos
```

### Clade `_foundation`

O clade `_foundation` é **transversal** — suas regras se aplicam a todos os outros clades. É prefixado com `_` para aparecer primeiro na ordenação alfabética e sinalizar sua natureza transversal.

| Subclade | Foco |
|---|---|
| `authoring` | Criação e gestão de artefatos do framework (Lexis, Codex, Katas, Warriors, Cries) |
| `contributing` | Processo de contribuição de código — commits, branches, issues, PRs, versionamento |
| `i18n` | Estrutura de idiomas do framework e navegação |
| `process` | Gestão de sessões de agentes — directives, checkpoint, convenções de nomenclatura |
| `quality` | Regras de qualidade transversais — observabilidade, templates, tom |
| `tooling` | Ferramentas de plataforma — Makefile, servidores MCP, tipo de terminal |

### Clade `design`

| Subclade | Foco |
|---|---|
| `brand` | Identidade visual da Guardia — cores, logo, tipografia, voz |
| `system` | Sistema de design de produto — experiência AI-First, biblioteca de componentes |

### Clade `documentation`

| Subclade | Foco |
|---|---|
| `i18n` | Regras de tradução de documentação e padrões específicos por idioma |

### Clade `engineering`

| Subclade | Foco |
|---|---|
| `backend` | Serviços Python — arquitetura, FastAPI, SQLAlchemy, testes, tooling |
| `data` | Modelagem de dados, design de schema, migrations, políticas de retenção |
| `devops` | Infraestrutura AWS — Well-Architected, IaC, segurança, custo |
| `frontend` | Interfaces web — React/TypeScript, acessibilidade, testes, segurança |
| `mobile` | iOS e Android — React Native/Flutter, offline-first, paridade de plataforma |
| `platform` | Padrões da plataforma Guardia — REST APIs, entidades, eventos, auth, tratamento de erros |
| `quality` | Estratégia de testes — pirâmide, isolamento, cobertura |
| `sre` | Site Reliability — SLO, alertas, resposta a incidentes |
| `workflow` | Fluxo de desenvolvimento — Issue-Driven Development, Gates, ADRs |

---

## Taxonomia de Endereçamento

Todo artefato do framework reside em um caminho canônico:

```
framework/{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.md
```

| Segmento | Exemplos |
|---|---|
| `{lang}` | `en`, `pt-BR`, `es` |
| `{clade}` | `_foundation`, `design`, `documentation`, `engineering` |
| `{subclade}` | `authoring`, `contributing`, `backend`, `platform`, ... |
| `{pilar}` | `lexis`, `codex`, `katas`, `warriors`, `cries` |
| `{prefix}-{name}` | `lex-issue-driven`, `codex-restful-apis`, `kata-quality-gate` |

**Exemplo:** A lei que governa o fluxo Issue-Driven reside em:
```
framework/en/engineering/workflow/lexis/lex-issue-driven.md
framework/pt-BR/engineering/workflow/lexis/lex-issue-driven.md
framework/es/engineering/workflow/lexis/lex-issue-driven.md
```

O idioma é sempre o primeiro nível de navegação. Todo artefato deve existir nos três idiomas.

---

## `.ahrena/.directives`

O arquivo `.ahrena/.directives` é o arquivo de configuração do projeto. Ele define:

| Seção | Controla |
|---|---|
| `paths` | Caminhos canônicos para artefatos do framework, templates e configurações geradas |
| `language.default` | Idioma padrão para criação de artefatos (`pt-BR` na Guardia) |
| `language.i18n` | Versões de idioma obrigatórias (`["pt-BR", "es", "en"]`) |
| `naming.prefixes` | Prefixos dos Pilares (`lex-`, `codex-`, `kata-`, `warrior-`, `cry-`) |
| `naming.casing` | Convenção de nomenclatura de arquivos e diretórios (kebab-case) |
| `naming.addressing` | Padrão de endereçamento canônico |
| `naming.reserved_clades` | Nomes de clades especiais (`_foundation`) |
| `naming.tone_and_writing_style` | Regras de tom e estilo para artefatos e comunicação |
| `terminal` | Tipo de shell para comandos (`bash` ou `powershell`) |
| `mcp.servers` | Servidores MCP autorizados (`github`, `notion`, `figma`) |

Todo agente DEVE ler `.ahrena/.directives` antes de produzir qualquer artefato — aplicado por `lex-directives`.
