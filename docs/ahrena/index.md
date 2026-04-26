# Ahrena — Framework de Capacidades AI-First

> **Produto:** Ahrena · **Responsável:** Guardia · **Status:** Ativo · **Tipo:** Plataforma Interna

## O que é o Ahrena?

**Ahrena** é o Framework de Capacidades AI-First da Guardia. Ele estrutura o conhecimento, os processos e o comportamento de agentes de AI por meio de uma taxonomia unificada, permitindo colaboração consistente, auditável e reproduzível entre humanos e AI em qualquer disciplina de engenharia.

O Ahrena define *como* os times e os agentes de AI da Guardia pensam, decidem e executam — desde uma mensagem de commit até o design completo de uma feature de produto.

## Por que criamos o Ahrena

À medida que a Guardia adotou agentes de AI como participantes de primeira classe nos fluxos de trabalho de engenharia, a necessidade de um modelo operacional estruturado, versionado e agnóstico de plataforma tornou-se crítica. Sem ele:

- Agentes tomavam decisões inconsistentes entre sessões
- O conhecimento ficava no histórico de chat, não em artefatos versionados
- O onboarding de novos engenheiros ou agentes exigia transferência de conhecimento tribal
- Não havia uma única fonte de verdade para processos, convenções e padrões

O Ahrena resolve isso ao tratar as regras de comportamento dos agentes, o conhecimento de referência, as skills executáveis e os comandos como **código** — versionado, revisável e implantável.

## Princípios fundamentais

| Princípio | O que significa |
|---|---|
| **AI como copiloto, não piloto** | Humanos definem a direção; agentes executam e propõem, nunca decidem sozinhos |
| **Processo acima de ferramenta** | Regras e procedimentos são agnósticos de plataforma; ferramentas vêm e vão |
| **Artefatos como código** | Toda convenção, lei e skill é um arquivo versionado em `framework/` |
| **`framework/` como fonte de verdade** | Uma fonte canônica única; todas as configurações de plataforma (Cursor, Claude Code) são geradas a partir dela |

## Arquitetura em resumo

```
framework/
├── en/                  ← Artefatos em inglês (fonte de verdade)
├── pt-BR/               ← Artefatos em português brasileiro
├── es/                  ← Artefatos em espanhol
└── templates/           ← Templates oficiais por Pilar
```

O framework é organizado por **Clade → Subclade → Pilar**. Dentro de cada Pilar, os artefatos são nomeados pelo prefixo do tipo:

| Pilar | Prefixo | Papel |
|---|---|---|
| **Lexis** | `lex-` | Leis invioláveis — sem exceção |
| **Codex** | `codex-` | Manuais de referência — conhecimento e orientação |
| **Katas** | `kata-` | Skills executáveis — procedimentos reproduzíveis |
| **Warriors** | `warrior-` | Agentes especializados — orquestram Katas |
| **Cries** | `cry-` | Comandos de alto nível — ativam Warriors ou Katas |

## Escala

| Dimensão | Quantidade |
|---|---|
| Total de artefatos no framework | ~649 |
| Idiomas | 3 (en, pt-BR, es) |
| Lexis (leis invioláveis) | 39 |
| Codex (manuais de referência) | 55 |
| Katas (skills executáveis) | 53 |
| Warriors (agentes especializados) | 14 |
| Cries (comandos) | 31 |
| Clades | 4 |
| Subclades | 16 |

## Plataformas suportadas

O Ahrena é agnóstico de plataforma. O instalador (`scripts/install.py`) gera configurações específicas para cada IDE a partir de `framework/`:

| Plataforma | Configuração gerada | Notas |
|---|---|---|
| **Claude Code** | `.claude/` (skills, commands, agents, docs) + `CLAUDE.md` | Plataforma principal na Guardia |
| **Cursor** | `.cursor/` (rules, skills, commands, agents) | Integração completa com a IDE |

## Capacidades principais

### Issue-Driven Development

O Warrior `warrior-athena` orquestra um fluxo de desenvolvimento completo em 7 fases — desde a leitura de uma issue no GitHub até a abertura de um PR revisado — com 2 gates obrigatórios (Scope e Quality), rastreabilidade completa entre critérios de aceitação e testes, e criação de ADRs para decisões arquiteturais.

[→ lex-issue-driven](../../framework/en/engineering/workflow/lexis/lex-issue-driven.md)

### Ciclo de Design de Plataforma

Os Warriors `warrior-prometheus`, `warrior-theseus`, `warrior-daedalus` e `warrior-kronos` cobrem o ciclo completo de design de feature: modelagem de domínio (DDD), design de API (OAS) e documentação de eventos (CloudEvents).

### Experiência de Produto AI-First

A Lexis `lex-ai-first-experience` determina que toda interface voltada ao usuário na Guardia utilize o Isac (o agente de AI) como superfície principal de interação — não uma barra lateral de funcionalidades.

[→ lex-ai-first-experience](../../framework/en/design/system/lexis/lex-ai-first-experience.md)

### Multilíngue por padrão

Todo artefato do framework existe em inglês, português brasileiro e espanhol. O `warrior-translator` e o `kata-translate` automatizam a tradução com regras específicas por idioma, aplicadas pelas leis `lex-language-*`.

## Índice de documentação

| Documento | Descrição |
|---|---|
| [Conceitos](concepts.md) | Pilares, Clades, Subclades, taxonomia de endereçamento |
| [Clades & Subclades](clades.md) | Catálogo completo com cobertura de pilares por subclade |
| [Catálogo de Lexis](lexis.md) | Todas as 39 leis invioláveis |
| [Catálogo de Codex](codex.md) | Todos os 55 manuais de referência |
| [Catálogo de Katas](katas.md) | Todas as 53 skills executáveis |
| [Catálogo de Warriors](warriors.md) | Todos os 14 agentes especializados |
| [Catálogo de Cries](cries.md) | Todos os 31 comandos de alto nível |
