# Cry: Revisar Pull Request

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para despachar revisão multi-eixo em uma Pull Request aberta via `warrior-argos`

## Descrição

Este comando invoca `warrior-argos` para executar revisão multi-eixo estruturada em uma Pull Request aberta: coleta contexto do GitHub (PR diff, view, checks, Issue linkada) e Notion (PRD, Capability Spec) quando disponíveis; cria worktree isolado; executa os katas de revisão aplicáveis (Python, frontend, AWS, OpenAPI, CloudEvents, segurança); roda testes localmente; detecta breaking changes em contratos públicos; e consolida findings em um único review-comment idempotente publicado via `gh pr review --request-changes` (ou `--comment` quando não há findings). Nunca `--approve` — a aprovação permanece decisão humana.

## Uso

```
/cry-review-pr <PR#> [--repo owner/name]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `PR#` | Sim | Número da Pull Request a revisar | `142` |
| `--repo owner/name` | Não | Nome do repositório; se omitido, infere a partir do `git remote` atual | `--repo guardiatechnology/ahrena` |

## O que o Comando Faz

1. Invoca `warrior-argos` com o número da PR e o repositório opcional
2. Argos executa as Fases 0 → 4 (Coleta → Worktree → Revisão Multi-Eixo → Consolidação → Cleanup)
3. O reviewer recebe um único review-comment consolidado na PR com findings classificados como 🔴 BLOCKER ou 🟡 WARNING
4. Re-rodar no mesmo commit edita o review-comment existente (idempotente); re-rodar em commit novo cria uma review nova (audit trail preservado)

## Prompt Template

```
Contexto:
- Número da PR: {{PR#}}
- Repositório: {{repo}} (ou inferido a partir do `git remote`)

Tarefa:
Atue como `warrior-argos`. Execute a revisão multi-eixo completa de Pull Request conforme o fluxo definido pelo warrior:
- Fase 0: Coletar PR, Issue linkada, PRD/Capability Spec no Notion (quando disponíveis), `docs/issues/issue-{N}/` local, e o plan referenciado
- Fase 1: Criar worktree isolado via `kata-git-worktree`
- Fase 2: Executar katas de revisão aplicáveis ao diff (Python, frontend, AWS, API design, CloudEvents, segurança) somados aos eixos B (alinhamento com specs), C (testes locais), D (retrocompatibilidade), F (conformidade Lexis/Codex)
- Fase 3: Consolidar findings em um único review-comment com marker idempotente `<!-- argos-review-id:sha256(pr_number+commit_sha) -->`; publicar via `gh pr review --request-changes` (≥1 finding) ou `--comment` (0 findings); nunca `--approve`
- Fase 4: Remover o worktree

Formato de saída:
- Resumo das fases (artefatos coletados, stack detectada, eixos roteados)
- Corpo final do review-comment (também publicado na PR)
```

## Exemplo de Invocação

**Input:**

```
/cry-review-pr 142
```

**Output esperado:**

```
Argos aqui. Revisando PR #142 em guardiatechnology/ahrena.

Fase 0 — Coleta: Issue #138 ✅ | PRD no Notion ✅ | docs/issues/issue-138/ ✅
Fase 1 — Worktree: .worktrees/review-pr-142/ criado
Fase 2 — Stack detectada: Python + OpenAPI + CloudEvents + migrations
         Eixos roteados: A (python, api-design, events), B, C (pytest+mypy), D (oasdiff ✅, squawk ❌), E, F
Fase 3 — Findings: 🔴 2 BLOCKER, 🟡 4 WARNING → publicado como `--request-changes` (review id: a1b2c3d4)
Fase 4 — Worktree removido

URL da review: https://github.com/guardiatechnology/ahrena/pull/142#pullrequestreview-...
```

## Restrições

- O Cry dispara apenas a revisão; não aprova, não modifica o código-fonte da PR e não publica fix-up commits
- O reviewer que executa o cry DEVE ter `gh` autenticado e os MCP servers configurados (`github`, opcionalmente `notion`) conforme `.ahrena/.directives`
- Uma nova review é criada por novo commit de head; despachos subsequentes no mesmo commit editam o review-comment existente
- O Cry não executa automaticamente em toda PR aberta — exige despacho humano explícito (o reviewer humano decide qual PR revisar e quando)

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Invocação rápida com número da PR | Orquestração completa multi-passo |
| **Complexidade** | Baixa (um comando) | Alta (Argos executa 5 fases e 6 eixos) |
| **Configura agente?** | Sim (assume papel do Warrior Argos) | N/A (Argos é Warrior, não Kata) |
| **Exemplo** | `/cry-review-pr 142` | Argos invoca `kata-python-review`, `kata-events-review`, etc. |

## Warrior e Katas Associados

- **warrior-argos** — Revisor multi-eixo de Pull Request (orquestrador)
- Katas executados pelo Argos: `kata-mcp-github-read`, `kata-mcp-notion-read`, `kata-git-worktree`, `kata-python-review`, `kata-frontend-review`, `kata-aws-review`, `kata-api-design-review`, `kata-events-review`, `kata-security-review`, `kata-quality-gate`

## Referências

- `warrior-argos` — Warrior invocado por este Cry
- `lex-issue-first`, `lex-pr-quality`, `lex-issue-driven` — Leis aplicadas durante a revisão
- `lex-mcp` — Comportamento MCP quando GitHub ou Notion estão indisponíveis
- `cry-implement-issue` — Contraparte pré-PR (Gate 2 do `warrior-athena` no lado do autor)
