# Lexis: Desenvolvimento Orientado por Issue

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Fluxo de desenvolvimento de features e bugfixes orientado por issues do GitHub no framework Ahrena

## Propósito

Em projetos que adotam o fluxo Issue-Driven Development (orquestrado por `warrior-athena`), cada feature ou bugfix começa em uma issue do GitHub e atravessa fases obrigatórias de análise, design, implementação e validação. Sem regras firmes, esse fluxo perde integridade: gates são pulados, critérios de aceitação viram opcionais, decisões arquiteturais não ficam registradas, e a documentação produzida se espalha em locais inconsistentes.

Esta Lexis existe para garantir que **toda implementação tenha rastreabilidade desde a issue original até o PR final**, que **gates de qualidade não sejam contornados**, que **decisões arquiteturais relevantes sejam registradas como ADRs** e que **toda documentação produzida pelo fluxo fique estruturada em `docs/`**.

## Lei

> **Toda implementação conduzida por `warrior-athena` DEVE partir de uma issue existente, passar por ambos os Gates (Escopo e Qualidade), respeitar a rastreabilidade bidirecional entre critérios de aceitação e testes, registrar decisões arquiteturais relevantes como ADRs em `docs/adr/`, e produzir toda documentação pública do fluxo em `docs/issues/issue-{n}/`.**

## Regras

### 1. Issue obrigatória como ponto de partida

O agente **DEVE**:

1. Exigir uma referência de issue existente (`owner/repo#número` ou equivalente) antes de iniciar qualquer fase do fluxo.
2. Ler a issue via `kata-mcp-github-read` na Fase 1.
3. Se a issue não existir ou estiver vazia, informar ao usuário e encerrar — não criar a issue automaticamente nem inferir o escopo.

### 2. Gates não podem ser pulados

O agente **NÃO PODE**:

1. Avançar da Fase 3 para a Fase 4 sem aprovação explícita humana no Gate 1 (escopo).
2. Criar o PR na Fase 7 se o Gate 2 (qualidade) não resultou em `go`.
3. Marcar itens do Gate 2 como atendidos sem execução real da verificação (ex.: não pode declarar "testes passam" sem rodar `pytest`).

### 3. Rastreabilidade bidirecional AC ↔ teste

Para que o Gate 2 passe:

1. **Cada critério de aceitação** numerado na Fase 2 **DEVE** ter pelo menos um teste que o cobre.
2. **Cada teste novo** introduzido na Fase 4 **DEVE** estar ligado a pelo menos um AC via convenção `AC-{N}` no nome ou docstring do teste.
3. Testes novos sem AC correspondente são tratados como **scope creep** e bloqueiam o gate.

### 4. ADRs obrigatórios para decisões arquiteturais relevantes

O agente **DEVE** invocar `kata-adr-write` quando a Fase 3 identificar:

1. Nova escolha tecnológica (framework, biblioteca, padrão arquitetural).
2. Deviação de padrão existente no codebase.
3. Trade-off significativo entre alternativas.
4. Decisão que afeta múltiplos componentes ou contratos externos.

O ADR **DEVE** ser salvo em `docs/adr/ADR-{n}-{título-em-kebab}.md` no formato MADR simplificado.

### 5. Documentação em `docs/`

O agente **DEVE** estruturar toda documentação pública do fluxo em `docs/`:

1. `docs/issues/issue-{n}/01-brief.md` — análise da issue (Fase 1)
2. `docs/issues/issue-{n}/02-requirements.md` — ACs numerados (Fase 2)
3. `docs/issues/issue-{n}/03-architecture.md` — design (Fase 3)
4. `docs/issues/issue-{n}/05-security-review.md` — revisão de segurança (Fase 5)
5. `docs/issues/issue-{n}/06-quality-report.md` — relatório do Gate 2 (Fase 6)
6. `docs/adr/ADR-{n}-*.md` — ADRs quando aplicáveis

Estado efêmero de orquestração (checkpoint entre fases) pode ir em `.ahrena/workflow/issue-{n}/checkpoint.md`, **nunca** em `docs/`. O checkpoint **DEVE** usar front-matter YAML versionado (ver Regra 7).

### 7. Schema versionado do checkpoint

O agente **DEVE** manter o checkpoint em `.ahrena/workflow/issue-{n}/checkpoint.md` com **front-matter YAML estruturado** contendo no mínimo:

```yaml
---
schema_version: 1
issue: 42
repo: guardiafinance/ahrena
phase_completed: 3
phase_next: 4
artifacts:
  brief: docs/issues/issue-42/01-brief.md
  requirements: docs/issues/issue-42/02-requirements.md
  architecture: docs/issues/issue-42/03-architecture.md
adrs:
  - ADR-008-use-event-sourcing-for-refund-audit-trail.md
gate_1:
  status: approved | pending | rejected
  approved_at: "2026-04-16T14:30:00Z"
  approver: "@user"
gate_2:
  status: go | no-go | pending
  last_run_at: "..."
delegations:
  - warrior: warrior-daedalus
    kata: kata-api-design-oas
    status: completed | running | failed | timed-out
    started_at: "..."
    completed_at: "..."
    output_refs: ["docs/..."]
    layer: 1                          # opcional; presente apenas em fluxos com stack
# Bloco opcional. Presente apenas quando a Fase 3 propôs decomposição
# em camadas e o humano aprovou no Gate 1. Ausência = fluxo PR único
# (comportamento padrão; preserva schema_version 1).
stack:
  approved: false                     # vira true após Gate 1 aprovar a decomposição
  tool: vanilla                       # eco de .directives.stacked_prs.tool (vanilla | gs)
  decomposition:
    - layer: 1
      slug: schema
      covers_acs: [AC-1, AC-2]
      components: ["db/migrations/*", "models/*"]
      status: pending                 # pending | in-progress | submitted | merged
      pr: null                        # owner/repo#N quando submetido
    - layer: 2
      slug: api
      covers_acs: [AC-3, AC-4]
      components: ["api/routers/*", "use_cases/*"]
      status: pending
      pr: null
updated_at: "2026-04-16T15:00:00Z"
---

# Notas narrativas (opcional, para contexto humano)
```

O conteúdo após `---` pode conter prosa livre para leitura humana, mas o estado operacional **DEVE** estar no front-matter. Campos desconhecidos são preservados; campos obrigatórios removidos invalidam o checkpoint e exigem reconstrução manual.

### 8. Protocolo de delegação (máquina de estados)

Quando `warrior-athena` delega uma fase a um warrior especialista (Apollo, Hephaestus, Daedalus, Kronos, Atlas, Hera, Hestia, Demeter, Iris), o handoff **DEVE** seguir uma máquina de estados registrada no checkpoint:

```
delegated → running → completed | failed | timed-out
```

Regras:

1. **`delegated`**: Athena grava a entrada de delegação no front-matter do `checkpoint.md` (warrior, kata, refs de entrada, `started_at`). Especialista é invocado.
2. **`running`**: especialista confirma atualizando a entrada com `status: running` no primeiro passo. Se o agente não consegue confirmar em até 60 segundos da invocação, a delegação é tratada como `timed-out`.
3. **`completed`**: especialista termina e grava `output_refs: [...]` + `completed_at`; status vira `completed`. Athena retoma a partir do checkpoint.
4. **`failed`**: especialista registra motivo explícito + outputs parciais (se houver). Athena apresenta a falha ao humano e pede direção (retry, escalar, abandonar).
5. **`timed-out`**: inferido por Athena quando não há atualização de status dentro do deadline configurado (default: 30 min para `kata-*-implement`; 10 min para katas curtos). Tratado como `failed` — humano decide.

Athena **NUNCA** re-invoca silenciosamente uma delegação em `running` ou `completed`. Re-invocação após `failed`/`timed-out` **DEVE** criar nova entrada de delegação (preservando a antiga como trilha de auditoria) — nunca mutar o histórico.

O formato da entrada de delegação está definido na Regra 7 (lista `delegations:`); timestamps e status são fonte da verdade para o estado da orquestração.

### 9. Checkpoint permanece enxuto

O arquivo checkpoint é re-lido a cada transição de fase. Para manter consumo de tokens previsível, o checkpoint **DEVE**:

- Conter apenas **estado operacional ativo** (fase atual, última delegação, outcomes dos gates, ponteiros para artefatos).
- **Não duplicar conteúdo** de `docs/issues/issue-{n}/*.md` — esses são a narrativa durável; checkpoint carrega referências (caminhos), não cópias.
- **Não acumular histórico além da última delegação failed/timed-out mantida para auditoria** (histórico mais antigo pertence aos arquivos de narrativa da issue, não ao checkpoint).

Tamanho-alvo: menos de ~2 KB após o fluxo completo. Se o checkpoint exceder 5 KB, o agente **DEVE** podar entradas históricas antes de continuar; conteúdo podado vai para `history.md` irmão (opcional) ou é descartado se já capturado em `docs/issues/issue-{n}/`.

### 6. Scope creep é bloqueio, não aviso

O Gate 2 **DEVE** falhar se:

1. Arquivos modificados estão fora do escopo declarado na Fase 3.
2. Funções ou classes públicas novas não são justificadas por algum AC.

Quando detectado, o agente **DEVE** apresentar duas opções ao usuário:
- Ampliar os ACs (nova iteração do Gate 1) para cobrir o código adicional.
- Remover o código além do escopo do PR atual e abrir nova issue para ele.

Em fluxos com `stack.approved: true`, o escopo de cada checagem de scope creep é a **camada corrente**, não a stack inteira (ver Regra 11).

### 10. Decomposição em stacked PRs na Fase 3

Durante a Fase 3 (Architecture), `warrior-athena` **DEVE** consultar a Decision Checklist canônica de [`codex-stacked-prs`](../../../_foundation/contributing/codex/codex-stacked-prs.md) (seção 2) contra o escopo declarado e os ACs numerados na Fase 2:

1. **Avaliar sinais altos e anti-sinais** conforme a checklist (≥ 3 sinais altos AND 0 anti-sinais → propor stack; caso contrário, PR único).
2. **Se a checklist aprovar:** registrar uma seção `## Stacked PR Decomposition` em `docs/issues/issue-{n}/03-architecture.md` contendo:
   - Tabela de camadas com colunas `Layer | Slug | ACs cobertos | Componentes tocados | Justificativa de independência de review`
   - Ferramenta selecionada (lookup em `.directives.stacked_prs.tool`; default `vanilla`)
   - Mapeamento explícito AC ↔ camada (cada AC pertence a exatamente uma camada)
3. **Se a checklist reprovar:** registrar `Single PR — checklist not met` na mesma seção, citando os sinais avaliados; seguir o fluxo padrão de PR único.

A decomposição proposta **NÃO PODE** ser aplicada antes da aprovação humana no Gate 1. Athena apresenta a decomposição como parte do design e aguarda revisão.

A escolha da ferramenta (`vanilla` vs. `gs`) é decisão do projeto via `.directives` — Athena apenas lê o valor; nunca modifica a diretiva. Quando `stacked_prs.tool: gs` está configurado mas `git-spice` não está disponível no ambiente, `kata-stacked-pr-create` cai no caminho `vanilla` com warning.

### 11. Gate 2 por camada quando há stack aprovada

Quando o checkpoint contém `stack.approved: true`, `kata-quality-gate` **DEVE** rodar **por camada** antes de cada PR ser submetido, não uma única vez no final:

1. **AC ↔ test traceability** (Regra 3) é avaliada apenas contra o subset de ACs cobertos pela camada (`stack.decomposition[i].covers_acs`), não contra o conjunto completo.
2. **Scope creep** (Regra 6) é avaliado apenas contra os componentes declarados pela camada na Fase 3 (`stack.decomposition[i].components`).
3. Cada `decomposition[i].status` só transita de `in-progress` para `submitted` quando os 7 checks da `kata-quality-gate` passarem para a camada.
4. Validação agregada final (após todas as camadas com status `submitted`) confirma que **toda** AC foi coberta por alguma camada (não há AC órfão) e que **todo** componente tocado foi declarado em alguma camada (não há componente órfão).

Em fluxos sem stack (bloco `stack` ausente), Gate 2 roda uma única vez sobre o escopo completo (comportamento atual preservado).

### 12. Roteamento do PR na Fase 7

A Fase 7 escolhe o kata de criação de PR com base no estado de `stack`:

| Estado do checkpoint | Kata invocado |
|---|---|
| `stack` ausente OU `stack.approved: false` | `kata-contributing-pr` (PR único — comportamento atual) |
| `stack.approved: true` | `kata-stacked-pr-create` |

`kata-stacked-pr-create` lê `.directives.stacked_prs.tool` e segue a variante correspondente (vanilla ou gs). Cada PR criado pela cadeia atualiza a entrada correspondente em `stack.decomposition[i].pr` no checkpoint, com formato `owner/repo#N`.

A regra de referência da issue guarda-chuva (Regra 5 do `codex-stacked-prs`, seção 1.2) é aplicada por `kata-stacked-pr-create`: camadas intermediárias usam `Refs #N`; a última usa `Closes #N` para fechar a issue automaticamente no merge.

## Abrangência

- **Aplica-se a:** qualquer invocação de `/cry-implement-issue` e qualquer atividade conduzida por `warrior-athena`.
- **Agentes vinculados:** `warrior-athena` (orquestrador) e todos os warriors/katas delegados durante o fluxo.
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Gate pulado:** PR criado sem o Gate 2 equivale a código não revisado em produção; bloqueia merge e exige reabertura do fluxo a partir da Fase 5.
2. **Rastreabilidade quebrada:** AC sem teste ou teste sem AC invalida o PR; requer correção antes de reabrir o Gate 2.
3. **ADR ausente:** decisão arquitetural sem ADR deixa a organização sem histórico de racional; ADR deve ser escrito retroativamente antes do merge.
4. **Documentação fora de `docs/`:** quebra o padrão de auditoria; arquivos devem ser movidos para a estrutura correta antes do merge.
5. **Scope creep não declarado:** código além do escopo é revertido ou justificado em nova iteração do Gate 1.

## Exemplos

### Correto

```
# Fluxo conduzido a partir de uma issue existente:
/cry-implement-issue 42 guardiafinance/ahrena

# Athena lê a issue #42, produz:
# docs/issues/issue-42/01-brief.md
# docs/issues/issue-42/02-requirements.md   (AC-1, AC-2, AC-3)
# docs/issues/issue-42/03-architecture.md
# docs/adr/ADR-007-use-fastapi-routers.md   (decisão relevante)

# Aguarda Gate 1 → humano aprova
# Apollo implementa: cada teste referencia AC-N
# Gate 2 executa 6 checks, todos ✅
# docs/issues/issue-42/06-quality-report.md registra o resultado
# PR criado com body referenciando os artefatos acima
```

```
# Fluxo com stacked PR aprovado no Gate 1:
/cry-implement-issue 64 guardiatechnology/ahrena

# Athena lê a issue #64 (5 ACs, ~900 linhas previstas, schema+API+UI):
#   Decision Checklist: 4 sinais altos, 0 anti-sinais → propõe stack
# docs/issues/issue-64/03-architecture.md inclui:
#   ## Stacked PR Decomposition
#     Layer 1 (schema):  AC-1, AC-2  — db/migrations/*, models/*
#     Layer 2 (api):     AC-3, AC-4  — routers/*, use_cases/*
#     Layer 3 (ui):      AC-5       — frontend/components/*
# Gate 1 aprovado → checkpoint grava stack.approved: true
# Apollo implementa Layer 1; Gate 2 roda contra AC-1, AC-2 e components da camada 1 → ✅ submitted
# Apollo implementa Layer 2; Gate 2 roda contra AC-3, AC-4 → ✅ submitted
# Hephaestus implementa Layer 3; Gate 2 roda contra AC-5 → ✅ submitted
# kata-stacked-pr-create cria 3 PRs encadeados; última camada usa Closes #64
```

### Incorreto

```
# ❌ Athena inicia o fluxo sem issue:
/cry-implement-issue "adicionar refund"

# ❌ Humano pede "pular Gate 1, já está ok":
# (Gate 1 é obrigatório — Athena deve recusar)

# ❌ Teste novo sem ligação a AC:
# def test_random_helper(): ...   (sem docstring AC-N)

# ❌ ADR salvo em local incorreto:
# .ahrena/workflow/issue-42/adr.md
# (o caminho correto é docs/adr/ADR-{n}-*.md)

# ❌ Modificação de arquivo fora do escopo declarado:
# (Gate 2 bloqueia; usuário decide entre ampliar AC ou abrir nova issue)

# ❌ Athena propõe decomposição em stack mas inicia Fase 4 sem aprovação no Gate 1:
# (Decomposição precisa de aprovação humana explícita; checkpoint deve registrar stack.approved: true)

# ❌ Camada 2 começa antes da camada 1 estar pronta para review (status submitted):
# (Camadas têm dependência sequencial; Athena delega camada N+1 só após N transitar para submitted)
```

## Validação Automatizada

- **Ferramenta:** `kata-quality-gate` (Gate 2) executa a verificação de rastreabilidade, scope creep e best practices antes do PR; `scripts/validate.py` verifica a presença obrigatória de artefatos em `docs/issues/issue-{n}/` quando o fluxo é concluído. Quando o checkpoint contém `stack.approved: true`, `kata-quality-gate` roda por camada e a validação agregada confirma cobertura de ACs e componentes.
- **Momento:** Gate 1 (antes da Fase 4), Gate 2 (antes de cada camada submetida em fluxos com stack; antes da Fase 7 em fluxo PR único).
- **Métrica:** 100% das issues passam por ambos os gates; 100% dos ACs têm pelo menos um teste; 0 testes sem AC correspondente; 100% das decisões arquiteturais relevantes têm ADR em `docs/adr/`; 0 fluxos com `stack.approved: true` que avancem da Fase 3 para a Fase 4 sem aprovação humana no Gate 1.
