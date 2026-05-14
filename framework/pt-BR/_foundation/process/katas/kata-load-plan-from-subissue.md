# Kata: Carregar Plano a partir da Sub-issue

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Materialização do cache local provider-specific (`.claude/plans/plan-{M}-{slug}.md` ou `.cursor/plans/plan-{M}-{slug}.md`) a partir do body canônico da sub-issue Plan, conforme o modelo hierárquico de `lex-agent-planning`

## Objetivo

Sincronizar o body da sub-issue Plan `{M}` (canonical per `lex-agent-planning`) para o cache local provider-specific. Operação idempotente: pode rodar quantas vezes for necessário e o resultado é determinístico. Roda no início de toda sessão que vai operar sobre um Plan, em cada handoff entre agentes, e em fresh clone do repo.

Este kata materializa cache local a partir de uma sub-issue Plan **já existente** no GitHub. Quando a sub-issue não existe (plan-arquivo orphan com `status: draft` no front-matter, `issue: TBD`, ou cenário plan-first), este kata NÃO se aplica diretamente — o agente DEVE primeiro acionar a **promoção plan-first** definida em `lex-agent-planning` (criar Issue parent via `kata-contributing-issue`, criar sub-issue Plan via `kata-decompose-issue-into-plans` ou `kata-plan-task`) e só depois invocar este kata com o número `{M}` da sub-issue recém-criada para materializar o cache.

## Quando Usar

- Início de sessão Claude Code ou Cursor (qualquer agente: Athena, Argos, Janus, etc.) antes de qualquer edição em `.claude/plans/plan-{M}-{slug}.md` ou `.cursor/plans/plan-{M}-{slug}.md`.
- Handoff entre agentes (ex.: Athena entrega para Argos em `to review → review`).
- Fresh clone do repo (cache local não existe).
- Suspeita de drift entre o cache local e o body da sub-issue Plan (ex.: outra sessão editou o body via UI do GitHub ou outro agente flushou em paralelo).

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `subissue_number` | Sim | Número `{M}` da sub-issue Plan |
| `owner/repo` | Não | Repo onde a sub-issue Plan vive. Default: repo corrente do worktree |
| `dest_path` | Não | Path do arquivo de cache. Default: resolvido pela detecção de provider (ver Passo 1) |

## Workflow

```
Progresso:
- [ ] 1. Resolver owner/repo + provider + path de destino
- [ ] 2. Confirmar a sub-issue Plan existe (guardrail plan-first)
- [ ] 3. Ler o body da sub-issue via MCP `get_issue` (preferido)
- [ ] 4. Fallback `gh issue view --json body`
- [ ] 5. Gravar body em `.claude/plans/plan-{M}-{slug}.md` ou `.cursor/plans/plan-{M}-{slug}.md`
- [ ] 6. Validar idempotência
```

### Passo 1: Resolver owner/repo + provider + path de destino

1. Se `owner/repo` foi passado, usar. Senão, derivar do worktree via `gh repo view --json owner,name`.
2. Detectar o runtime do agente:
   - Claude Code (CLI, VSCode, Desktop, claude.ai/code) → `.claude/plans/`
   - Cursor → `.cursor/plans/`
   - Outro → consultar `.ahrena/.directives` e perguntar ao usuário se ambíguo.
3. Resolver path de destino:
   - Se `dest_path` foi passado, usar.
   - Senão, path final: `<provider-dir>/plan-{M}-{slug}.md`.
4. Garantir que o diretório de destino existe (`mkdir -p`).

### Passo 2: Confirmar a sub-issue Plan existe

Este kata pressupõe que a sub-issue Plan `{M}` já existe no GitHub. Verificar:

```bash
# Preferido — via MCP
mcp.github.get_issue(owner=owner, repo=repo, issue_number=M)

# Fallback CLI
gh issue view {M} --repo {owner}/{repo} --json number,state,labels
```

Se a sub-issue NÃO existir (HTTP 404), **não falhar como erro fatal**. O cenário é válido (plan-arquivo orphan, caminho plan-first). O kata DEVE retornar status `PROMOTION_REQUIRED` com mensagem:

> "Sub-issue Plan #{M} não encontrada em {owner}/{repo}, ou plan-arquivo carrega `status: draft`/`issue: TBD`. Cenário plan-first válido. Acione a promoção per `lex-agent-planning`: `kata-contributing-issue` para criar Issue parent (se ainda não existir), depois `kata-decompose-issue-into-plans` ou `kata-plan-task` para criar a sub-issue Plan. Após promoção, retorne a este kata com o número da sub-issue para materializar o cache."

O agente invocador DEVE tratar `PROMOTION_REQUIRED` como sinal de fluxo (acionar promoção plan-first), não como falha fatal.

Se a sub-issue existir, prosseguir.

### Passo 3: Ler o body da sub-issue via MCP `get_issue` (preferido)

Per `lex-mcp` regra 1, se o servidor GitHub MCP estiver listado em `mcp.servers` e ativo:

```python
issue = mcp.github.get_issue(owner=owner, repo=repo, issue_number=M)
body = issue["body"]
```

Se sucesso, pular para Passo 5.

### Passo 4: Fallback `gh issue view --json body`

Per `lex-mcp` regra 4 (MCP indisponível), executar o fallback CLI documentado:

```bash
gh issue view {M} --repo {owner}/{repo} --json body --jq .body > {dest_path}
```

Se `gh` também falha:

1. Retry único após 5 segundos de backoff.
2. Se persistir, oferecer ao usuário: (a) tentar novamente com outro comando, (b) pausar para investigação, (c) abortar.

### Passo 5: Gravar body em `.claude/plans/plan-{M}-{slug}.md` ou `.cursor/plans/plan-{M}-{slug}.md`

1. Se o cache local já existe e tem conteúdo, **preservar blocos `<!-- not-flushed -->` ... `<!-- /not-flushed -->`** existentes:
   - Extrair todos os blocos `<!-- not-flushed -->` do arquivo atual.
   - Substituir o corpo principal pelo body novo da sub-issue.
   - Apender os blocos `<!-- not-flushed -->` no final.
2. Se o cache local não existe, gravar o body diretamente (sem blocos `<!-- not-flushed -->` ainda).

A preservação de blocos locais permite re-load sem perder scratch da IA — re-load é só re-sincronizar o conteúdo canônico.

### Passo 6: Validar idempotência

Após gravar, executar uma segunda chamada (read-only) e comparar:

```bash
# Comparação canônica (após filtrar blocos não-flushados de ambos os lados)
diff <(strip-not-flushed {dest_path}) <(gh issue view {M} --json body --jq .body)
```

Resultado esperado: nenhuma diferença.

Se houver diferença que não seja em blocos `<!-- not-flushed -->`, o re-load falhou silenciosamente — abortar e investigar.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Cache local | Markdown (superset do body da sub-issue + blocos `<!-- not-flushed -->` preservados) | `.claude/plans/plan-{M}-{slug}.md` ou `.cursor/plans/plan-{M}-{slug}.md` |

## Exemplo de Execução

### Input de Exemplo

```
subissue_number: 201
owner/repo: guardiatechnology/example-repo
dest_path: (default; provider detectado: Claude Code) .claude/plans/plan-201.md
```

### Output de Exemplo

`.claude/plans/plan-201.md` (logo após primeiro load, sem blocos não-flushados ainda):

```markdown
## Summary

Refatorar o agregado Ledger para event sourcing, separando comandos
(write-side) de leitura (read-side projection).

Parent: #200

## Plan

### Objective
Entregar a primeira fatia executável da User Story #200: Ledger
reescrito como aggregate event-sourced, com factory + repository.

### Steps
- [ ] Step 1 — Modelar LedgerEvent base class
- [ ] Step 2 — Reescrever Ledger.apply() como event projection
- [ ] Step 3 — Repository persistindo events em vez de state
- [ ] Step 4 — Migration helper para legacy state → events
- [ ] Step 5 — Testes de aggregate

### Dependencies
None

### Risks
- migration helper pode falhar em datasets com inconsistência
  histórica — mitigado por dry-run + checksum.

### Open Questions
None
```

Após algumas edições da IA no cache local, o arquivo carrega blocos não-flushados:

```markdown
## Summary
...
(conteúdo do body — espelhado)
...

<!-- not-flushed -->
## Working notes
- 14:32 — começou Step 1; LedgerEvent vai herdar de DomainEvent base.

## Next actions
1. Step 2 — apply() recebe LedgerEvent, retorna novo state imutável.
2. Step 3 — repository.save() chama event_store.append().

## Scratch
considerando usar discriminated union em vez de class hierarchy.
<!-- /not-flushed -->
```

## Restrições

- **Idempotente:** múltiplas execuções produzem o mesmo cache local para o mesmo estado do body da sub-issue.
- **Não flusha:** este kata é one-way (sub-issue → cache). Para gravar de volta, usar `kata-flush-plan-to-subissue`.
- **Preserva blocos locais:** blocos `<!-- not-flushed -->` ... `<!-- /not-flushed -->` existentes no cache local são preservados; só o conteúdo canônico é re-sincronizado.
- **Promoção plan-first:** se a sub-issue Plan `{M}` não existir, o kata retorna `PROMOTION_REQUIRED` (não erro fatal) orientando o agente invocador a acionar `kata-contributing-issue` + `kata-decompose-issue-into-plans` (ou `kata-plan-task`) antes de retornar.
- **MCP > CLI:** preferir MCP `get_issue` quando o servidor estiver listado e ativo; CLI `gh issue view` é fallback documentado per `lex-mcp` regra 4.
- **Não cria sub-issue:** se a sub-issue `{M}` não existe, o kata falha; criação é responsabilidade de `kata-plan-task` ou `kata-decompose-issue-into-plans`.
- **Provider-specific:** Claude Code → `.claude/plans/`; Cursor → `.cursor/plans/`. Não há cache compartilhado entre providers.

## Referências

- `lex-agent-planning` — modelo hierárquico Issue → Plan → PR; cadência de load/flush; guardrail plan-first
- `lex-mcp` — preferência MCP + fallback CLI
- `codex-agent-planning` — manual operacional
- `kata-flush-plan-to-subissue` — operação inversa (cache → sub-issue)
- `kata-plan-task` — criação inicial da sub-issue Plan (precondition deste kata)
- `kata-decompose-issue-into-plans` — decomposição de Issue parent em N sub-issues Plan
