---
name: cry-review-pr
description: "Revisar Pull Request. Atalho para despachar revisão multi-eixo em uma Pull Request aberta via warrior-argos"
---

# Cry: Revisar Pull Request

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para despachar revisão multi-eixo em uma Pull Request aberta via `warrior-argos`

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
- Fase 0: Coletar PR, Issue vinculada, PRD/Capability Spec no Notion (quando disponíveis), `.ahrena/issues/{N}/` local, e o plan referenciado
- Fase 1: Criar worktree isolado via `kata-git-worktree`
- Fase 2: Executar katas de revisão aplicáveis ao diff (Python, frontend, AWS, API design, CloudEvents, segurança) somados aos eixos B (alinhamento com specs), C (testes locais), D (retrocompatibilidade), F (conformidade Lexis/Codex)
- Fase 3: Consolidar findings em um único review-comment com marker idempotente `<!-- argos-review-id:sha256(pr_number+commit_sha) -->`; publicar via `gh pr review --request-changes` (≥1 finding) ou `--comment` (0 findings); nunca `--approve`
- Fase 4: Remover o worktree

Formato de saída:
- Resumo das fases (artefatos coletados, stack detectada, eixos roteados)
- Corpo final do review-comment (também publicado na PR)
```

## Restrições

- O Cry dispara apenas a revisão; não aprova, não modifica o código-fonte da PR e não publica fix-up commits
- O reviewer que executa o cry DEVE ter `gh` autenticado e os MCP servers configurados (`github`, opcionalmente `notion`) conforme `.ahrena/.directives`
- Uma nova review é criada por novo commit de head; despachos subsequentes no mesmo commit editam o review-comment existente
- O Cry não executa automaticamente em toda PR aberta — exige despacho humano explícito (o reviewer humano decide qual PR revisar e quando)

## Warrior e Katas Associados

- **warrior-argos** — Revisor multi-eixo de Pull Request (orquestrador)
- Katas executados pelo Argos: `kata-mcp-github-read`, `kata-mcp-notion-read`, `kata-git-worktree`, `kata-python-review`, `kata-frontend-review`, `kata-aws-review`, `kata-api-design-review`, `kata-events-review`, `kata-security-review`, `kata-quality-gate`
