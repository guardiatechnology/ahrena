# Lexis: Labels Canônicos de Status na Issue e PR

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Issues e Pull Requests em repositórios Guardia que participam do fluxo Issue-Driven

## Propósito

Plano, Issue do GitHub e PR carregam o mesmo trabalho em momentos distintos do ciclo. Sem um conjunto canônico de labels de status, o agente perde a referência cruzada entre os três artefatos, dashboards desalinham, e o cálculo agregado de child↔subtasks fica impreciso. Esta Lei codifica os 7 labels `status: <name>` que espelham o enum unificado de `lex-agent-planning`, garante consistência entre plano/Issue/PR, e separa esses labels do gating de Discovery (`pending-spec`/`spec-ready`).

## Lei

> **Toda Issue e todo PR que participam do fluxo Issue-Driven DEVEM carregar exatamente um label `status: <name>` do conjunto canônico (`status: todo`, `status: development`, `status: to review`, `status: review`, `status: to release`, `status: release`, `status: done`), espelhando o `status:` do plano correspondente. Nenhum agente DEVE aplicar dois labels `status: *` simultaneamente à mesma Issue ou PR. O label `status:*` é ortogonal aos labels de Discovery (`pending-spec`/`spec-ready`) e aos labels de tipo (`feature request ➕`, `user story 🎯`, etc.) — múltiplos eixos coexistem na mesma Issue.**

## Abrangência

- **Aplica-se a:** todas as Issues abertas via templates aprovados (`feature-request`, `user-story-for-api`, `user-story-for-frontend`, `simple-task`, `subtask`) e todos os PRs em repositórios Guardia.
- **Agentes vinculados:** `warrior-eunomia` (aplica `status: todo` na criação), `warrior-athena` (move `todo → development`, `development → to review`, `to review → to release`), `warrior-argos` (move `to review ↔ review`), `warrior-janus` (move `to release → release → done`), e qualquer agente que crie ou modifique Issues/PRs.
- **Exceções:**
  - **Epic** não recebe `status:*` — é decomposto em child Issues, cada uma com seu próprio ciclo. O Epic fecha quando todas as crianças (`Tracked by`) atingem `done`.
  - **Issues geradas por Dependabot** ou scanners de segurança seguem fluxo próprio e ficam isentas.

## Rules

### 1. Conjunto canônico de 7 labels

| Label | Cor sugerida | Quando aplicar | Owner |
|---|---|---|---|
| `status: todo` | `#cccccc` (cinza claro) | Plano criado, Issue aberta, branch vinculada, worktree pronto | `warrior-eunomia` (fallback: agente da sessão) |
| `status: development` | `#83d2ff` (azul claro) | Implementação em andamento (Athena Phase 4) | `warrior-athena` |
| `status: to review` | `#fff3a3` (amarelo claro) | PR aberto, esperando reviewer pegar | `warrior-athena` (entrada); `warrior-argos` (retorno do `review`) |
| `status: review` | `#fbca04` (amarelo) | Argos ou humano revisando ativamente | `warrior-argos` |
| `status: to release` | `#ffb178` (laranja claro) | Review aprovado, esperando release iniciar | `warrior-athena` |
| `status: release` | `#e07400` (laranja) | Release em execução (tag/build/deploy) | `warrior-janus` |
| `status: done` | `#0e8a16` (verde) | Release concluído, PR mergeado, ciclo encerrado | `warrior-janus` |

A descrição da label no GitHub DEVE conter a semântica resumida do estado para auditoria visual rápida.

### 2. Mutex entre labels `status:*`

Em qualquer instante, a Issue ou PR DEVE ter **exatamente um** label `status:*`. Cada transição é executada por:

```bash
gh issue edit {N} --remove-label "status: <previous>" --add-label "status: <next>"
gh pr edit {N}    --remove-label "status: <previous>" --add-label "status: <next>"
```

Aplicar dois labels `status:*` simultaneamente (ex.: `status: to review` + `status: review`) é PROIBIDO.

### 3. Sincronização com o plano

O label `status:*` na Issue DEVE espelhar o `status:` do front-matter do plano correspondente em todo instante. O agente que executa a transição (per `lex-agent-planning` "Owners de cada transição") DEVE atualizar simultaneamente:

1. `status:` no front-matter do plano.
2. Label `status: <name>` na Issue.
3. Label `status: <name>` no PR (a partir de `to review`).

Falha em qualquer um dos três produz drift detectável no Gate 2 (per `kata-quality-gate`).

### 4. Ortogonalidade com labels de Discovery

Os labels de Discovery (`pending-spec`, `spec-ready`, definidos por plan-038) operam em um eixo separado:

- `pending-spec`/`spec-ready` controlam **entrada** no fluxo Athena para US-child (User Story child de Epic). Convivem com `status:*` na mesma Issue.
- US-child criada por Calliope nasce com `pending-spec` e **sem** `status:*`. Recebe `status: todo` somente quando ganha `spec-ready` (transição feita pelo PM correspondente após produzir a spec).
- Bug e Tech-task pulam o gate de spec e recebem `status: todo` direto na criação por Eunomia.

### 5. Epic não recebe `status:*`

Epic é decomposto por Calliope (plan-038) e nunca passa por Athena diretamente. O Epic não tem ciclo `todo → development → ...` próprio; seu estado é derivado de `Tracked by` (children com `status:*`). Aplicar `status:*` a um Epic é PROIBIDO.

### 6. Criação inicial das labels no repositório

Cada repositório que adota o fluxo DEVE criar as 7 labels via `gh label create` (script idempotente em `scripts/bootstrap_status_labels.sh` ou kata dedicado). A criação manual via UI do GitHub também é aceitável, desde que respeite nomes, cores e descrições canônicas.

## HARD-GATE

Per [`lex-hard-gate-pattern`](../quality/lex-hard-gate-pattern.md), o bloco textual desta Lex é canonicamente expresso como:

```
<HARD-GATE>
warrior-eunomia, warrior-athena, warrior-argos, warrior-janus e qualquer
outro agente MUST NOT aplicar label `status:*` em Issue ou PR sem
satisfazer TODOS os critérios:

  (a) Label pertence ao conjunto canônico de 7
      (status: todo | development | to review | review | to release
       | release | done)
  (b) Issue/PR não está em estado terminal (done|abandoned) ao receber
      o novo label
  (c) Nenhum outro label `status:*` permanece na Issue/PR após a
      transição (mutex aplicado)
  (d) Plano correspondente teve `status:` atualizado no mesmo passo
  (e) Issue não é Epic (Epic não recebe status:*)

Esta regra aplica-se a TODA Issue e TODO PR no fluxo Issue-Driven,
independente de:
  - tamanho percebido ("é só um chore")
  - urgência ("incêndio em produção")
  - quem pediu ("o CEO solicitou")
  - confiança da equipe ("já testamos muito")

Exceção declarada: Epic e Issues geradas por Dependabot/scanners
seguem fluxo próprio. Todo outro tipo de Issue/PR no fluxo
Issue-Driven respeita o mutex.
</HARD-GATE>
```

## Exemplos

### Correto

```bash
# Eunomia cria Issue #90 e plano-043 em "todo"
gh issue edit 90 --add-label "status: todo"
# (plano-043 front-matter: status: todo)

# Athena entra em Phase 4
gh issue edit 90 --remove-label "status: todo" --add-label "status: development"
# (plano-043 front-matter: status: development)

# Athena abre PR #91 — aplica label simultaneamente
gh pr create ... && gh pr edit 91 --add-label "status: to review"
gh issue edit 90 --remove-label "status: development" --add-label "status: to review"
# (plano-043 front-matter: status: to review)

# Argos inicia revisão
gh pr edit 91 --remove-label "status: to review" --add-label "status: review"
gh issue edit 90 --remove-label "status: to review" --add-label "status: review"
# (plano-043 front-matter: status: review)
```

### Incorreto

```bash
# ❌ Dois labels status:* simultâneos
gh issue edit 90 --add-label "status: to review" --add-label "status: review"

# ❌ Label aplicado sem atualizar plano (drift)
gh issue edit 90 --add-label "status: development"
# (plano-043 ficou em status: todo)

# ❌ Aplicar status:* em Epic
gh issue edit 100 --add-label "status: development"
# Issue #100 tem Issue Type Epic
```

## Validação Automatizada

- **Ferramenta:**
  - Script `scripts/bootstrap_status_labels.sh` cria as 7 labels idempotentemente em qualquer repositório.
  - PR review (humano ou Argos) verifica alinhamento entre `status:` do plano, label da Issue, e label do PR.
  - GitHub Action de verificação periódica (futuro) detecta:
    - Issues/PRs com 0 ou ≥2 labels `status:*`
    - Issues com Issue Type Epic carregando `status:*`
    - Drift entre `status:` do plano e label da Issue
- **Momento:** ao abrir/atualizar Issue, ao abrir/atualizar PR, em cada transição de owner, no Gate 2 (`kata-quality-gate`).
- **Métrica:** 0 Issues/PRs com label `status:*` divergente do plano correspondente; 0 Epics com `status:*`; 100% das transições registradas pelo owner declarado.

## Referências

- `lex-agent-planning` — enum unificado de `status:` e tabela de owners
- `lex-issue-quality` — requisitos base de Issues (template, label de tipo, Issue Type, assignee, Why/What/How)
- `lex-issue-first` — toda mudança parte de uma Issue
- `lex-pr-quality` — requisitos do PR (label de tamanho, CODEOWNERS, etc.) — complementar
- `lex-hard-gate-pattern` — sintaxe do bloco `<HARD-GATE>`
- `codex-agent-planning` — manual operacional com fluxo visual e loop 3×15min
- `codex-labels` — convenção geral de labels no GitHub
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners das transições
