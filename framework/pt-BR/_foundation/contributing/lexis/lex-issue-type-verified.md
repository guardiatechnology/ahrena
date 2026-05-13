# Lexis: Verificação Programática do Issue Type

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Toda Issue criada em repositórios Guardia que participa do fluxo Issue-Driven

## Propósito

`lex-issue-quality` exige que toda Issue tenha um Issue Type definido (`Feature`, `Task`, `Bug`, `Epic`). O campo nativo de Issue Type do GitHub é populado automaticamente quando a Issue é criada via template (`.github/ISSUE_TEMPLATE/*.yml` declara `type:`), mas **NÃO** é populado quando a Issue é criada via `gh issue create` sem template. Sem verificação programática pós-criação, Issues criadas via CLI ficam sem type — o que desalinha o HARD-GATE de `lex-agent-planning` e quebra a tabela de owners por tipo. Esta Lei codifica a verificação obrigatória.

## Lei

> **Todo agente que cria uma Issue (humano ou IA, via UI/CLI/MCP) DEVE verificar programaticamente, imediatamente após a criação, que o campo nativo `type` da Issue está populado com um valor compatível com o template usado (`Feature` para `feature-request` / `user-story-for-api` / `user-story-for-frontend`; `Task` para `tech-task` / `subtask`; `Epic` para `epic`; `Bug` quando aplicável). Se vazio, o agente DEVE aplicar o type via `gh api -X PATCH repos/{owner}/{repo}/issues/{N} -f type={Feature|Task|Bug|Epic}` antes de qualquer transição subsequente da Issue. Aplicar label `status: todo` (per `lex-issue-status` Eixo A) em uma Issue sem `type` populado é PROIBIDO.**

## Abrangência

- **Aplica-se a:** todas as Issues criadas em repositórios Guardia, independente do mecanismo (UI do GitHub, `gh issue create`, MCP `create_issue`, script automatizado).
- **Agentes vinculados:** `warrior-eunomia` (modo top-level e subtask), `warrior-athena` (quando delega criação de child Issue), `warrior-calliope` (decomposição de Epic), e qualquer agente que invoque `kata-plan-task`, `kata-create-subtasks` ou `kata-contributing-issue`.
- **Exceções:** Issues geradas por Dependabot ou scanners de segurança seguem fluxo próprio e ficam isentas.

## Regras

### 1. Verificação pós-criação obrigatória

Imediatamente após criar a Issue, o agente **DEVE**:

```bash
gh api repos/{owner}/{repo}/issues/{N} --jq '.type.name // empty'
```

- Se retorna um valor (`Feature`, `Task`, `Bug`, `Epic`) → segue com a verificação de compatibilidade (Regra 2).
- Se retorna vazio → aplicar manualmente (Regra 3).

### 2. Compatibilidade template ↔ type

| Template | Issue Type aceito |
|---|---|
| `feature-request` | `Feature` |
| `epic` | `Epic` |
| `user-story-for-api` | `Feature` |
| `user-story-for-frontend` | `Feature` |
| `tech-task` | `Task` |
| `subtask` | `Task` |

Se o type retornado for incompatível com o template, **abortar e alertar o usuário** — não tentar reescrever silenciosamente (pode mascarar erro de criação).

### 3. Aplicação manual quando ausente

Se a verificação retorna vazio:

```bash
gh api -X PATCH repos/{owner}/{repo}/issues/{N} -f type={Feature|Task|Bug|Epic}
```

Em seguida re-verificar (Regra 1) para confirmar persistência.

### 4. Pré-condição para transições

Aplicar label `status: todo` (entrada no Eixo A do `lex-issue-status`) **SEMPRE** acontece **APÓS** type estar populado e verificado. HARD-GATE de `lex-agent-planning` precondition (b) exige isso explicitamente.

## HARD-GATE

Per [`lex-hard-gate-pattern`](../quality/lex-hard-gate-pattern.md):

```
<HARD-GATE>
warrior-eunomia, warrior-athena, warrior-calliope e qualquer agente que
cria Issue MUST NOT aplicar label `status: todo` (entrada no Eixo A do
lex-issue-status) sem satisfazer TODOS os critérios:

  (a) `gh api repos/{owner}/{repo}/issues/{N} --jq '.type.name'` retorna
      valor não-vazio
  (b) Valor retornado é um de: Feature | Task | Bug | Epic
  (c) Valor é compatível com o template usado per Regra 2 desta Lex

Esta regra aplica-se a TODA Issue no fluxo Issue-Driven, independente de:
  - tamanho percebido ("é só um chore")
  - urgência ("incêndio em produção")
  - quem pediu ("o CEO solicitou")
  - confiança da equipe ("já testamos muito")

Exceção declarada: Issues geradas por Dependabot ou scanners de segurança
seguem fluxo próprio. Toda outra Issue no fluxo respeita o gate.
</HARD-GATE>
```

## Exemplos

### Correto

```bash
# 1. Eunomia cria Issue via gh CLI (sem template)
gh issue create --title "chore: ..." --body "..." --label "evolvability ♻️"
# → Issue #105 criada

# 2. Verificação pós-criação
TYPE=$(gh api repos/guardiatechnology/ahrena/issues/105 --jq '.type.name // empty')

# 3. Type vazio (CLI não aplica) — aplicar manualmente
[ -z "$TYPE" ] && gh api -X PATCH repos/guardiatechnology/ahrena/issues/105 -f type=Task

# 4. Re-verificar
gh api repos/guardiatechnology/ahrena/issues/105 --jq '.type.name'
# → "Task" ✓

# 5. Agora pode aplicar status: todo per lex-issue-status Eixo A
gh issue edit 105 --add-label "status: todo"
```

### Incorreto

```bash
# ❌ Pular verificação após gh issue create
gh issue create --title "feat: ..." --label "feature request ➕"
gh issue edit 106 --add-label "status: todo"
# Issue #106 fica sem type — viola HARD-GATE precondition (b) de lex-agent-planning

# ❌ Aplicar type incompatível com template
# Issue criada via template feature-request mas com `type=Task` manual
# Compatibilidade quebrada — viola Regra 2
```

## Validação Automatizada

- **Ferramenta:** `kata-contributing-issue` aplica esta verificação no Passo final; `kata-plan-task` invoca a verificação no Passo 3 do HARD-GATE de Eunomia; revisão de PR confirma alinhamento.
- **Momento:** imediatamente após `gh issue create` / MCP `create_issue` / UI submit; antes de qualquer label `status:*` ser aplicada.
- **Métrica:** 0 Issues no fluxo Issue-Driven sem `type` populado; 100% de Issues com type compatível com o template usado.

## Referências

- `lex-issue-quality` — exige Issue Type entre os requisitos base
- `lex-agent-planning` — HARD-GATE precondition (b) cita esta Lex
- `lex-issue-status` — Eixo A (status: todo) requer type populado
- `lex-issue-first` — Issue como ponto de origem; type é parte da qualidade da Issue
- `kata-plan-task`, `kata-create-subtasks`, `kata-contributing-issue` — invocam esta verificação
- `warrior-eunomia` — owner que dispara a verificação na criação de plano
- Issue Types nativos do GitHub: https://docs.github.com/en/issues/tracking-your-work-with-issues/configuring-issues/managing-issue-types-in-an-organization
