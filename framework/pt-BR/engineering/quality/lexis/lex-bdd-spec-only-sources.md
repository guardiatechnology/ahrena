# Lexis: Cenários BDD Derivados Exclusivamente das Fontes de Especificação

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Engenharia — Qualidade. Validação comportamental de features entregues pelo fluxo Issue-Driven Development.

## Propósito

A validação BDD só captura "construímos a coisa errada" quando os cenários são independentes da implementação. Um cenário derivado do código só consegue descrever o que foi construído — nunca o que foi pedido. Esta Lexis garante que os cenários funcionem como contrato comportamental black-box: se a especificação não permite escrevê-los, o requisito está incompleto e precisa voltar à origem antes da validação continuar.

Esta Lexis existe para que **a validação BDD seja capaz de detectar divergência entre o que foi pedido e o que foi entregue**, e para impedir que o agente "complete" especificações ambíguas olhando para o código produzido.

## Lei

> **Cenários Gherkin produzidos para validação comportamental DEVEM ser derivados exclusivamente da Issue do GitHub (título, corpo, critérios de aceitação, comentários) e das páginas do Notion vinculadas. Ler, abrir, fazer grep ou consultar de qualquer forma o código de implementação (arquivos sob `src/`, `app/`, `lib/`, `tests/`, etc.) para descobrir, refinar ou completar cenários é PROIBIDO. Se as fontes de especificação não permitem escrever os cenários, o agente DEVE parar e pedir que a Issue seja complementada — nunca recorrer ao código como atalho.**

## Regras

### 1. Fontes permitidas

O agente que produz os cenários **PODE** consultar:

- A Issue do GitHub vinculada (título, corpo, comentários, labels).
- Páginas do Notion referenciadas pela Issue ou pelos artefatos do fluxo Issue-Driven.
- Os artefatos do próprio fluxo: `docs/issues/issue-{n}/01-brief.md`, `02-requirements.md`, `03-architecture.md`.
- ADRs em `docs/adr/` quando explicitamente referenciados pela arquitetura.

### 2. Fontes proibidas

O agente que produz os cenários **NÃO PODE**:

- Abrir arquivos sob `src/`, `app/`, `lib/`, `pkg/`, `internal/`, `tests/`, `spec/`, `__tests__/`, `cypress/`, `e2e/`, ou diretórios equivalentes da stack.
- Executar `grep`/`rg`/`find` sobre o código de implementação.
- Pedir explicação do código a outro agente para inferir comportamento.
- Inspecionar PRs, diffs ou commits da feature em validação.

### 3. Declaração de fontes no artefato

O arquivo `docs/issues/issue-{n}/07-bdd-scenarios.md` **DEVE** declarar, em frontmatter YAML, o conjunto de fontes consultadas:

```yaml
---
issue: 42
repo: guardiafinance/ahrena
sources:
  github_issue: "guardiafinance/ahrena#42"
  notion_pages:
    - "https://www.notion.so/page-id-1"
    - "https://www.notion.so/page-id-2"
  flow_artifacts:
    - docs/issues/issue-42/01-brief.md
    - docs/issues/issue-42/02-requirements.md
generated_at: "2026-04-29T10:00:00Z"
---
```

Caminhos sob `src/`, `app/`, `tests/`, etc. neste bloco invalidam o artefato.

### 4. Especificação insuficiente

Se as fontes permitidas **não** permitem escrever cenários completos para algum critério de aceitação:

1. O agente **DEVE** parar a produção do artefato.
2. **DEVE** abrir comentário na Issue ou bloco de bloqueio em `07-bdd-scenarios.md` listando as ambiguidades.
3. **NÃO PODE** consultar o código para resolver a ambiguidade.
4. A Issue **DEVE** ser complementada (pelo PM, pela engenharia, pelo design) e o fluxo retomado.

### 5. Verificação independente

A validação dos cenários contra a implementação (executada por `kata-bdd-validate-implementation`) **PODE** ler o código — esta é a etapa de mapear cenário ↔ teste existente. A produção dos cenários (`kata-bdd-scenarios-design`) **NÃO PODE**.

A separação entre "desenhar cenários" (cego para o código) e "validar implementação" (com acesso ao código) é a coluna vertebral desta Lexis.

## Abrangência

- **Aplica-se a:** toda feature ou bugfix que completou o fluxo Issue-Driven e entrou na Fase 8 (Validação BDD).
- **Agentes vinculados:** `warrior-themis` (executor da Fase 8), `warrior-athena` (orquestrador que delega), e qualquer Kata invocado dentro da Fase 8.
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Bloqueio do PR:** o Gate 3 (Comportamental) do `kata-quality-gate` falha quando o frontmatter de `07-bdd-scenarios.md` referencia caminhos de implementação ou quando o agente registrar leitura de código durante a Fase 8 de design.
2. **Cenário descartado:** cenários produzidos com violação detectada são descartados; o artefato é regenerado a partir das fontes permitidas.
3. **Issue incompleta torna-se evento de processo:** ambiguidades repetidas geram revisão da Fase 2 (`kata-requirements-brief`) — o problema está no requisito, não no validador.

## Exemplos

### Correto

```
Agente warrior-themis recebe ordem de validar issue #42.
1. Lê: docs/issues/issue-42/01-brief.md, 02-requirements.md.
2. Lê: GitHub Issue #42 (corpo + comentários).
3. Lê: páginas Notion referenciadas pela Issue.
4. Produz docs/issues/issue-42/07-bdd-scenarios.md com:
   - frontmatter declarando essas 4 fontes;
   - cenários cobrindo cada AC numerado.
5. Não abre nenhum arquivo sob src/.
```

### Incorreto

```
Agente warrior-themis recebe ordem de validar issue #42.
1. Lê os artefatos da Fase 1-3.
2. "Para entender o fluxo de reembolso", abre src/refund_service.py.
3. Escreve cenários baseados no comportamento observado no código.

→ Violação. Os cenários agora descrevem o que foi construído, não o que
foi pedido — perdem a capacidade de detectar "construímos a coisa errada".
```

## Validação Automatizada

- **Ferramenta:** lint do frontmatter de `07-bdd-scenarios.md` rejeitando caminhos sob `src/`, `app/`, `lib/`, `tests/`; checklist do `kata-bdd-scenarios-design` exigindo declaração explícita das fontes; revisão pelo `kata-quality-gate` Check 8 (BDD coverage).
- **Momento:** Fase 8 do fluxo Issue-Driven (pré-PR), antes do `kata-pr-prepare`.
- **Métrica:** 0 arquivos `07-bdd-scenarios.md` referenciando caminhos de implementação; 100% dos cenários rastreáveis a uma fonte de especificação declarada.

## Referências

- `lex-bdd-gherkin-format` — formato Gherkin obrigatório dos cenários
- `lex-bdd-no-framework-coupling` — implementação dos testes sem framework BDD
- `lex-issue-driven` — fluxo Issue-Driven que precede a validação BDD
- `kata-bdd-scenarios-design` — procedimento de produção dos cenários
- `kata-bdd-validate-implementation` — procedimento de validação contra implementação
- `warrior-themis` — agente especializado em validação BDD
