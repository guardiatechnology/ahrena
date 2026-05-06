---
plan_id: "004"
title: "create-discovery-warriors"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#48"
created_at: "2026-05-05T00:00:00Z"
updated_at: "2026-05-06T01:10:00Z"
---

# Plan: Create Product Discovery warriors (Pítia + Phanes)

## Objective

Introduce Product Discovery into Ahrena via two new warriors — **Pítia** (estuda fontes e produz insights) e **Phanes** (promove insights aprovados a Ideas) — junto com a clade nova `product/discovery/`, os procedimentos (Katas), os atalhos (Cries), e o manual de artefatos (Codex), em pt-BR, es e en.

## Scope summary

| Pilar | Artefato | Função |
|---|---|---|
| Warrior | `warrior-pitia` | Discovery: lê APIs/docs/processos, sintetiza, produz insights |
| Warrior | `warrior-phanes` | Ideation: lê insights `approved` e gera Ideas |
| Kata | `kata-discovery-synthesis` | Procedimento da Pítia (leitura → síntese → N insights) |
| Kata | `kata-ideation-from-insight` | Procedimento de Phanes (insight aprovado → Idea) |
| Cry | `cry-discovery` | Atalho que invoca Pítia |
| Cry | `cry-ideation` | Atalho que invoca Phanes |
| Codex | `codex-discovery-artifacts` | Schema dos arquivos `insights/*.md` e `ideas/*.md` + máquina de estados |
| Lexis | `lex-discovery-flow` | Lei do ciclo Discovery → Idea com HARD-GATE per `lex-hard-gate-pattern` |
| Clade nova | `product/discovery/` | Endereçamento canônico em `framework/{lang}/product/discovery/` |

Total de arquivos: **6 warriors + 6 katas + 6 cries + 3 codex + 3 lex + estrutura de diretórios em 3 idiomas + 1 atualização em `framework/platforms.yaml` (registro do lex e do codex)**.

## Decisões (resolvidas)

1. ✅ **`lex-discovery-flow` entra na v1** com HARD-GATE.
2. ✅ **Outputs reais em** `docs/discovery/{topic}/insights/{NNN}-{slug}.md` e `docs/discovery/{topic}/ideas/{NNN}-{slug}.md`.
3. ✅ **Idioma dos outputs** segue `language.default` do `.directives` → **pt-BR**.

## HARD-GATEs do `lex-discovery-flow`

Per `lex-hard-gate-pattern` (subject + ação proibida + preconditions + scope + counter-pretexts + exceções), a lex carrega **dois blocos**:

**HARD-GATE 1 — Promoção de Insight a Idea (subject: warrior-phanes)**

```
warrior-phanes MUST NOT promover um insight a Idea sem que TODAS as
preconditions sejam atendidas:

  (a) insight.status == approved (decisão humana registrada)
  (b) Idea referencia ≥1 insight em linked_insights[]
  (c) Idea preenche os 5 campos obrigatórios:
      problem, hypothesis, target_user, success_metric, effort_estimate
  (d) {topic} da Idea coincide com o {topic} do insight de origem
  (e) Phanes atualiza o insight de origem para status: promoted +
      preenche idea_ref: apontando para a Idea criada

Esta regra aplica-se a TODA criação de Idea no Ahrena, regardless of:
  - "é só experimento"
  - "stakeholder validou verbalmente"
  - "o insight é óbvio"
  - urgência declarada

Exceção única: nenhuma.
```

**HARD-GATE 2 — Mudança de status de Insight (subject: warrior-pitia)**

```
warrior-pitia MUST NOT alterar status de um insight para qualquer
valor diferente de "proposed" sem direção humana explícita registrada
(comentário em PR, mensagem na sessão, ou instrução literal).

Mandatory preconditions para qualquer transição != "proposed":
  (a) Existe instrução humana explícita identificando o insight por path
  (b) A transição-alvo é válida na máquina de estados de codex-discovery-artifacts
  (c) Para under_review → refining: humano forneceu feedback acionável

Esta regra aplica-se a TODOS os insights produzidos por Pítia,
regardless of:
  - "o feedback é trivial"
  - "o status é óbvio"
  - "Pítia já viu o caso antes"

Exceção única: criação inicial (status: proposed) é da própria Pítia
e não exige direção humana.
```

## Steps

### Phase A — Issue e worktree (após aprovação do plano)

- [ ] A1. Abrir issue no GitHub via `kata-contributing-issue` (template `feature-request`, type `Feature`, labels `feature request ➕`)
- [ ] A2. Atualizar `issue:` no front-matter deste plano com `guardiatechnology/ahrena#N`
- [ ] A3. Criar worktree via `kata-git-worktree`: branch `feat/{N}-create-discovery-warriors`, dir `.worktrees/{N}-create-discovery-warriors/`

### Phase B — Fundação (taxonomia + governança)

- [ ] B1. Criar estrutura de diretórios `framework/{pt-BR,es,en}/product/discovery/{lexis,codex,warriors,katas,cries}/`
- [ ] B2. Redigir `codex-discovery-artifacts.md` em pt-BR cobrindo:
  - Esqueleto YAML de `insights/{NNN}-{slug}.md` (front-matter: id, topic, status, source_refs[], tags[], created_at, updated_at, merged_into, idea_ref, rejected_reason, awaiting_evidence_reason)
  - Esqueleto YAML de `ideas/{NNN}-{slug}.md` (front-matter: id, topic, problem, hypothesis, target_user, success_metric, effort_estimate, linked_insights[], created_at, updated_at)
  - Máquina de estados (mermaid) com 9 status e tabela de transições com responsável (humano vs. warrior-pitia)
  - Convenção de numeração `{NNN}` por `topic` (zero-padded, sequencial dentro do topic)
- [ ] B3. Redigir `lex-discovery-flow.md` em pt-BR (template `lex-sample.md`):
  - Cobertura, agentes vinculados (warrior-pitia, warrior-phanes), ausência de exceção
  - Os DOIS blocos HARD-GATE definidos acima (Promoção a Idea + Mudança de status)
  - Validação automatizada: lint do front-matter + verificação de transições no PR
- [ ] B4. Traduzir `codex-discovery-artifacts` e `lex-discovery-flow` para es e en via `kata-translate` (HARD-GATEs traduzidos integralmente per `lex-hard-gate-pattern` regra 6)
- [ ] B5. Registrar entradas em `framework/platforms.yaml`:
  - `product/discovery/lexis/lex-discovery-flow` sob `cursor.rules` (description + alwaysApply: false; carregado pelos warriors de Discovery)
  - `product/discovery/codex/codex-discovery-artifacts` sob `cursor.rules` (description + alwaysApply: false)
  - Mesmas entradas sob `claude-code.rules` se a estrutura existir no platforms.yaml

### Phase C — Procedimentos (Katas)

- [ ] C1. Redigir `kata-discovery-synthesis.md` em pt-BR (template `kata-sample.md`):
  - Inputs: `topic`, `source_refs[]` (URLs de OpenAPI/Notion/Figma/transcrições), `language`
  - Workflow: ler fontes via MCP (notion/figma/github) → sintetizar → produzir N insights com `status: proposed`
  - Outputs: arquivos em `docs/discovery/{topic}/insights/`
- [ ] C2. Traduzir `kata-discovery-synthesis` para es e en
- [ ] C3. Redigir `kata-ideation-from-insight.md` em pt-BR:
  - Inputs: `insight_path` (precisa estar `status: approved`)
  - Workflow: validar status → ler insight → mapear problem/hypothesis/target_user/success_metric/effort_estimate → produzir Idea
  - Side effect: atualizar insight para `status: promoted` + preencher `idea_ref:`
  - Outputs: arquivo em `docs/discovery/{topic}/ideas/`
- [ ] C4. Traduzir `kata-ideation-from-insight` para es e en

### Phase D — Especialistas (Warriors)

- [ ] D1. Redigir `warrior-pitia.md` em pt-BR (template `warrior-sample.md`):
  - Identidade: Pítia, "Oráculo de Discovery", domínio "Product Discovery — síntese de insights a partir de fontes heterogêneas"
  - Faz: estuda fontes; mapeia ubiquitous language candidato; produz insights estruturados; itera após feedback (`refining`); marca `awaiting_evidence` quando trava
  - Não faz: aprova/rejeita (humano); transforma insight em Idea (Phanes); modela bounded context (Theseus)
  - Consulta: `lex-directives`, `lex-mcp`, `lex-discovery-flow`, `codex-discovery-artifacts`, `codex-mcp-{notion,figma,github}`
  - Executa: `kata-discovery-synthesis`, `kata-mcp-notion-read`, `kata-mcp-figma-extract`, `kata-mcp-github-read`
- [ ] D2. Traduzir `warrior-pitia` para es e en
- [ ] D3. Redigir `warrior-phanes.md` em pt-BR:
  - Identidade: Phanes, "Manifestador de Ideas", domínio "Product Discovery — promoção de insight aprovado a Idea"
  - Faz: lê insights `approved`, sintetiza problem/hypothesis/metric, gera Idea, marca insight como `promoted`
  - Não faz: produz insight (Pítia); prioriza backlog (Prometheus); escreve PRD (Prometheus)
  - Consulta: `lex-directives`, `lex-discovery-flow`, `codex-discovery-artifacts`
  - Executa: `kata-ideation-from-insight`
- [ ] D4. Traduzir `warrior-phanes` para es e en

### Phase E — Atalhos (Cries)

- [ ] E1. Redigir `cry-discovery.md` em pt-BR (template `cry-sample.md`): invoca `warrior-pitia` com `topic` e `source_refs[]`
- [ ] E2. Traduzir `cry-discovery` para es e en
- [ ] E3. Redigir `cry-ideation.md` em pt-BR: invoca `warrior-phanes` com `insight_path`
- [ ] E4. Traduzir `cry-ideation` para es e en

### Phase F — Sync e PR

- [ ] F1. Rodar sync (`make sync-cursor` + targets equivalentes para `.claude/`) para materializar artefatos em `.cursor/{rules,skills,agents,commands}/` e `.claude/{agents,skills,commands,rules}/`
- [ ] F2. Self-review via `kata-artifact-self-review` em cada artefato novo
- [ ] F3. Verificar HARD-GATE de `lex-pr-quality`: labels mirror, size, assignee, reviewers
- [ ] F4. Abrir PR via `kata-pr-prepare` referenciando issue da fase A com `Closes #N`

## Dependencies

- Aprovação do usuário neste plano (gate antes de A1)
- GitHub issue aberta (gate antes de A3)
- Clade `product/` não existe → criar como nova clade não-reservada (não conflita com `naming.reserved_clades`)
- MCPs ativos: `github`, `notion`, `figma` precisam estar listados em `mcp.servers` do `.directives` para Pítia operar (verificar; se não estiverem, abrir issue separada para configuração)

## Risks

- **R1 — Schema imaturo:** front-matter de insight/idea pode precisar revisão após primeiro uso real. Mitigação: marcar codex como `draft` na primeira versão e revisar após primeira jornada Discovery → Idea completa.
- **R2 — Sobreposição com Prometheus:** Phanes gera Idea; Prometheus depois transforma Idea em PRD. A fronteira pode ficar tênue. Mitigação: explicitar em "Não Faz" do Phanes "não produz PRD nem priorização", e em "Faz" do Prometheus declarar que ele consome Ideas como input.
- **R3 — Clade nova `product/`:** introduz nível taxonômico que hoje não existe. Mitigação: registrar em ADR a decisão de criar a clade e que outros artefatos de produto (PRDs futuros, capability specs) também moram lá.
- **R4 — Lex prematura:** com `lex-discovery-flow` já na v1, HARD-GATEs podem precisar revisão após primeiro uso real (ex.: precondition (b) "linked_insights[] não vazio" pode ser muito rígida se uma Idea legitimamente nasce de pesquisa não documentada como insight). Mitigação: marcar a lex como `Type: Unbreakable Law` mas reservar 1ª revisão obrigatória após o primeiro ciclo Discovery → Idea completo, registrada em ADR.
- **R5 — Tradução triplica trabalho:** ~21 arquivos para traduzir (6 warriors + 6 katas + 6 cries + 3 codex + 3 lex em es/en a partir de pt-BR, descontados os pt-BR originais). Mitigação: usar `kata-translate` em lote por pilar; verificar HARD-GATE blocks com tag literal preservada per `lex-hard-gate-pattern` regra 6.

## Out of scope (v1)

- ADR formal sobre criação da clade `product/` (recomendado, mas pode ser PR separada)
- Configuração de MCPs no `.directives` (pré-requisito; issue separada se necessário)
- Implementação real de templates de insight/idea já populados (será feita no primeiro uso)
- Lint automatizado do front-matter de insights/ideas (citado na "Validação Automatizada" da lex como aspiração; implementação real fica para iteração posterior)
