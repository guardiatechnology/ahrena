# Lexis: Labels Canônicos de Status na Issue e PR

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Issues e Pull Requests em repositórios Guardia que participam do fluxo Issue-Driven

## Propósito

Body da Issue (canonical per ADR-002), Issue e PR carregam o mesmo trabalho em momentos distintos do ciclo. Sem um conjunto canônico de labels de status, o agente perde a referência cruzada, dashboards desalinham, e o cálculo agregado de child↔subtasks fica impreciso. Esta Lei codifica os labels `status: <name>` que espelham o enum de `lex-agent-planning`, **separa-o em dois eixos disjuntos** (dev cycle e release cycle), garante consistência intra-artefato, e mantém ortogonalidade com os labels de Discovery (`pending-spec`/`spec-ready`).

## Lei

> **Toda Issue e todo PR que participam do fluxo Issue-Driven DEVEM carregar exatamente um label `status: <name>` do conjunto canônico. O conjunto se divide em dois eixos disjuntos: **Eixo A (dev cycle)** aplicável a Issues/PRs de feature/fix/chore/refactor (`status: todo`, `status: development`, `status: to review`, `status: review`, `status: done`); **Eixo B (release cycle)** aplicável exclusivamente à release Issue dedicada criada por Janus (`status: to release`, `status: release`, `status: done`). O terminal `status: abandoned` é compartilhado pelos dois eixos. Mutex é **intra-artefato**: nenhuma Issue ou PR carrega dois labels `status:*` simultaneamente. Aplicar label do Eixo B em Issue/PR do Eixo A (ou vice-versa) é PROIBIDO. O label `status:*` é ortogonal aos labels de Discovery (`pending-spec`/`spec-ready`) e aos labels de tipo (`feature request ➕`, etc.) — múltiplos eixos coexistem.**

## Abrangência

- **Aplica-se a:** todas as Issues abertas via templates aprovados (`feature-request`, `user-story-for-api`, `user-story-for-frontend`, `tech-task`, `subtask`, **release** — novo template introduzido por ADR-002 / plan-046 Step 3.5), e todos os PRs em repositórios Guardia.
- **Agentes vinculados:**
  - Eixo A — `warrior-eunomia` (`— → todo`), `warrior-athena` (`todo → development`, `development → to review`, `to review → done`), `warrior-argos` (`to review ↔ review`).
  - Eixo B — `warrior-janus` (`— → to release`, `to release → release`, `release → done`).
- **Exceções:**
  - **Epic** não recebe `status:*` — é decomposto em child Issues, cada uma com seu próprio ciclo (Eixo A). O Epic fecha quando todas as crianças (`Tracked by`) atingem `done`.
  - **Issues geradas por Dependabot** ou scanners de segurança seguem fluxo próprio e ficam isentas.

## Rules

### 1. Eixo A — Dev cycle (Issues/PRs de feature/fix/chore/refactor)

| Label | Cor sugerida | Quando aplicar | Owner |
|---|---|---|---|
| `status: todo` | `#cccccc` (cinza claro) | Plano canônico no body da Issue, branch vinculada, worktree pronto | `warrior-eunomia` (fallback: agente da sessão) |
| `status: development` | `#83d2ff` (azul claro) | Implementação em andamento (Athena Phase 4) | `warrior-athena` |
| `status: to review` | `#fff3a3` (amarelo claro) | PR aberto, esperando reviewer pegar | `warrior-athena` (entrada); `warrior-argos` (retorno do `review`) |
| `status: review` | `#fbca04` (amarelo) | Argos ou humano revisando ativamente | `warrior-argos` |
| `status: done` | `#0e8a16` (verde) | PR mergeado; Issue fechada via `Closes #N` | `warrior-athena` (no merge) |
| `status: abandoned` | `#6e6e6e` (cinza escuro) | Plano descartado (terminal alternativo) | criador ou owner atual |

### 2. Eixo B — Release cycle (exclusivamente release Issue dedicada)

| Label | Cor sugerida | Quando aplicar | Owner |
|---|---|---|---|
| `status: to release` | `#ffb178` (laranja claro) | Janus abriu release Issue; populou `Tracks: #N1, #N2, ...` | `warrior-janus` |
| `status: release` | `#e07400` (laranja) | `kata-release-prepare` rodando; humano aprovou bump/changelog | `warrior-janus` |
| `status: done` | `#0e8a16` (verde) | Tag empurrada, `validate-tag.yml` passou, Release publicada | `warrior-janus` |
| `status: abandoned` | `#6e6e6e` (cinza escuro) | Release abortada antes de tag | `warrior-janus` |

A release Issue é criada por Janus como ponto de entrada do release cycle. Não existe "release branch": o ciclo opera sobre a release Issue + tag + GitHub Release. Detalhes em `warrior-janus` e `kata-release-prepare`.

### 3. Mutex intra-artefato

Em qualquer instante, **uma mesma Issue (ou PR)** carrega exatamente um label `status:*`. Aplicar dois labels `status:*` simultaneamente à mesma Issue/PR (ex.: `status: to review` + `status: review`) é PROIBIDO.

Mutex **não** é cross-artifact: a release Issue (Eixo B) coexiste com N feature Issues em `done` (Eixo A) sem conflito — são artefatos distintos.

Cada transição é executada por:

```bash
gh issue edit {N} --remove-label "status: <previous>" --add-label "status: <next>"
gh pr edit {N}    --remove-label "status: <previous>" --add-label "status: <next>"
```

Preferir MCP `update_issue` / `update_pull_request` quando o servidor GitHub MCP estiver listado em `mcp.servers` e ativo (per `lex-mcp` regra 1).

### 4. Cross-cycle labeling proibido

Labels do Eixo B (`status: to release`, `status: release`) **não podem** ser aplicadas em Issues/PRs de feature/fix/chore/refactor. Labels do Eixo A (`status: todo`, `status: development`, `status: to review`, `status: review`) **não podem** ser aplicadas em release Issue.

Detecção: o tipo da Issue (`gh issue view {N} --json type`) determina o eixo permitido. Release Issue carrega Issue Type `Task` (ou `Feature` quando criada como release feature por convenção do template) + label `release ↗️`. Cross-cycle labeling é violação do HARD-GATE.

### 5. Sincronização Issue ↔ PR

Quando um PR é aberto para uma Issue em `status: development`, o agente que executa a transição (per `lex-agent-planning` Tabela A) DEVE atualizar simultaneamente:

1. Label `status: <name>` na Issue.
2. Label `status: <name>` no PR.
3. Disparar `kata-flush-plan-to-issue` para garantir que o body da Issue reflete o estado pós-transição.

Falha em qualquer um dos três produz drift detectável no Gate 2 (per `kata-quality-gate`).

### 6. Ortogonalidade com labels de Discovery

Os labels de Discovery (`pending-spec`, `spec-ready`, definidos por plan-038) operam em um eixo separado:

- `pending-spec`/`spec-ready` controlam **entrada** no fluxo Athena para US-child (User Story child de Epic). Convivem com `status:*` na mesma Issue.
- US-child criada por Calliope nasce com `pending-spec` e **sem** `status:*`. Recebe `status: todo` somente quando ganha `spec-ready` (transição feita pelo PM correspondente após produzir a spec).
- Bug e Tech-task pulam o gate de spec e recebem `status: todo` direto na criação por Eunomia.

### 7. Epic não recebe `status:*`

Epic é decomposto por Calliope (plan-038) e nunca passa por Athena diretamente. O Epic não tem ciclo `todo → development → ...` próprio; seu estado é derivado de `Tracked by` (children com `status:*`). Aplicar `status:*` a um Epic é PROIBIDO.

### 8. Criação inicial das labels no repositório

Cada repositório que adota o fluxo DEVE criar as labels via `gh label create` (script idempotente em `scripts/bootstrap_status_labels.sh`). Todas as labels já existem desde plan-043 (PR #93); plan-046 não introduz labels novas — apenas reorganiza a semântica em dois eixos.

## HARD-GATE

Per [`lex-hard-gate-pattern`](../quality/lex-hard-gate-pattern.md), o bloco textual desta Lex é canonicamente expresso como:

```
<HARD-GATE>
warrior-eunomia, warrior-athena, warrior-argos, warrior-janus e qualquer
outro agente MUST NOT aplicar label `status:*` em Issue ou PR sem
satisfazer TODOS os critérios:

  (a) Label pertence ao conjunto canônico do eixo correto:
      - Eixo A (feature/fix/chore Issues/PRs): todo | development |
        to review | review | done | abandoned
      - Eixo B (release Issue exclusivamente): to release | release |
        done | abandoned
  (b) Issue/PR não está em estado terminal (done|abandoned) ao receber
      o novo label
  (c) Nenhum outro label `status:*` permanece na Issue/PR após a
      transição (mutex intra-artefato aplicado)
  (d) Label do eixo correto para o tipo da Issue/PR:
      - Issues/PRs de feature/fix/chore/refactor → Eixo A apenas
      - Release Issue (label `release ↗️`) → Eixo B apenas
  (e) Body da Issue atualizado pelo último kata-flush-plan-to-issue
      (Eixo A) ou Tracks populado com PRs mergeados desde o último
      tag (Eixo B, transição `— → to release`)
  (f) Issue não é Epic (Epic não recebe status:*)

Esta regra aplica-se a TODA Issue e TODO PR no fluxo Issue-Driven,
independente de:
  - tamanho percebido ("é só um chore")
  - urgência ("incêndio em produção")
  - quem pediu ("o CEO solicitou")
  - confiança da equipe ("já testamos muito")

Exceção declarada: Epic e Issues geradas por Dependabot/scanners
seguem fluxo próprio. Todo outro tipo de Issue/PR no fluxo
Issue-Driven respeita o mutex e a separação de eixos.
</HARD-GATE>
```

## Exemplos

### Correto — Eixo A (feature Issue + PR)

```bash
# Eunomia cria Issue #96 com body canônico
gh issue edit 96 --add-label "status: todo"

# Athena entra em Phase 4
gh issue edit 96 --remove-label "status: todo" --add-label "status: development"

# Athena abre PR #97; aplica label simultaneamente
gh pr create ... && gh pr edit 97 --add-label "status: to review"
gh issue edit 96 --remove-label "status: development" --add-label "status: to review"

# Argos inicia revisão
gh pr edit 97 --remove-label "status: to review" --add-label "status: review"
gh issue edit 96 --remove-label "status: to review" --add-label "status: review"

# Argos termina sem aprovar; humano cobrado em 3×15min
gh pr edit 97 --remove-label "status: review" --add-label "status: to review"
gh issue edit 96 --remove-label "status: review" --add-label "status: to review"

# Humano aprova; merge fecha Issue
gh pr edit 97 --remove-label "status: to review" --add-label "status: done"
gh issue edit 96 --remove-label "status: to review" --add-label "status: done"
```

### Correto — Eixo B (release Issue)

```bash
# Janus abre release Issue #100; popula Tracks com PRs mergeados
# desde a última tag
gh issue create --title "release: 0.4.0" \
  --body "Tracks: #93, #96, #98, #99" \
  --label "release ↗️,status: to release"

# Janus inicia kata-release-prepare
gh issue edit 100 --remove-label "status: to release" --add-label "status: release"

# Janus conclui: tag empurrada, validate-tag.yml passa, Release criada
gh issue edit 100 --remove-label "status: release" --add-label "status: done"
```

### Incorreto

```bash
# ❌ Dois labels status:* simultâneos (viola mutex intra-artefato)
gh issue edit 96 --add-label "status: to review" --add-label "status: review"

# ❌ Cross-cycle labeling: status: to release em Issue de feature
gh issue edit 96 --add-label "status: to release"
# Issue #96 é feature (Eixo A); status: to release pertence ao Eixo B

# ❌ Cross-cycle labeling reverso: status: development em release Issue
gh issue edit 100 --add-label "status: development"
# Issue #100 é release Issue (Eixo B); status: development pertence ao Eixo A

# ❌ Aplicar status:* em Epic
gh issue edit 88 --add-label "status: development"
# Issue #88 tem Issue Type Epic — proibido per Rule 7
```

## Validação Automatizada

- **Ferramenta:**
  - Script `scripts/bootstrap_status_labels.sh` cria as labels idempotentemente em qualquer repositório.
  - PR review (humano ou Argos) verifica:
    - Alinhamento entre label da Issue e label do PR (mesmo eixo, mesmo estado).
    - Body da Issue reflete o último flush (`kata-flush-plan-to-issue` foi executado na transição).
    - Eixo correto aplicado ao tipo da Issue (feature ⇒ Eixo A; release Issue ⇒ Eixo B).
  - GitHub Action de verificação periódica (futuro) detecta:
    - Issues/PRs com 0 ou ≥2 labels `status:*`
    - Cross-cycle labeling (Eixo A label em release Issue, ou Eixo B label em feature Issue)
    - Issues com Issue Type Epic carregando `status:*`
- **Momento:** ao abrir/atualizar Issue, ao abrir/atualizar PR, em cada transição de owner, no Gate 2 (`kata-quality-gate`).
- **Métrica:** 0 Issues/PRs com label `status:*` cross-cycle; 0 Epics com `status:*`; 100% das transições registradas pelo owner declarado; 100% das release Issues com `Tracks:` populado.

## Referências

- ADR-002 — split em dois eixos (absorção de plan-045)
- `lex-agent-planning` — enum unificado de `status:` e tabelas de owners (Tabela A / Tabela B)
- `lex-issue-quality` — requisitos base de Issues (template, label de tipo, Issue Type, assignee, Why/What/How)
- `lex-issue-first` — toda mudança parte de uma Issue
- `lex-pr-quality` — requisitos do PR (label de tamanho, CODEOWNERS, etc.) — complementar
- `lex-mcp` — preferência MCP + fallback CLI para `update_issue` / `update_pull_request`
- `lex-hard-gate-pattern` — sintaxe do bloco `<HARD-GATE>`
- `codex-agent-planning` — manual operacional com fluxo visual e loop 3×15min
- `codex-labels` — convenção geral de labels no GitHub
- `kata-flush-plan-to-issue` — disparado em cada transição
- `kata-release-prepare`, `kata-release-publish` — operações de Janus no Eixo B
- `warrior-eunomia`, `warrior-athena`, `warrior-argos`, `warrior-janus` — owners das transições
