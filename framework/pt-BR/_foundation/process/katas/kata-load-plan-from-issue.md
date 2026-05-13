# Kata: Carregar Plano a partir da Issue

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Materialização do cache local `.plans/{N}.md` a partir do body canônico da Issue do GitHub, conforme o modelo de armazenamento em 3 camadas do

## Objetivo

Sincronizar o conteúdo do body de uma Issue (canonical per `lex-agent-planning`) para o cache local `.plans/{N}.md` da IA. Operação idempotente: pode rodar quantas vezes for necessário e o resultado é determinístico. Roda no início de toda sessão que vai operar sobre um plano e em cada handoff entre agentes.

## Quando Usar

- Início de sessão Claude Code (qualquer agente: Athena, Argos, Janus, etc.) antes de qualquer edição em `.plans/{N}.md`.
- Handoff entre agentes (ex.: Athena entrega para Argos no `to review → review`).
- Fresh clone do repo (cache local não existe).
- Suspeita de drift entre `.plans/{N}.md` e o body da Issue (ex.: outra sessão editou o body via UI do GitHub).

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `issue_number` | Sim | Número da Issue (`{N}` em `{owner}/{repo}#{N}`) |
| `owner/repo` | Não | Repo onde a Issue vive. Default: repo corrente do worktree |
| `dest_path` | Não | Path do arquivo de cache. Default: `<paths.plans>/{N}.md` (resolução em `lex-agent-planning`) |

## Workflow

```
Progresso:
- [ ] 1. Resolver owner/repo + path de destino
- [ ] 2. Tentar MCP `get_issue` (preferido)
- [ ] 3. Fallback `gh issue view --json body`
- [ ] 4. Gravar body em `.plans/{N}.md`
- [ ] 5. Validar idempotência
```

### Passo 1: Resolver owner/repo + path de destino

1. Se `owner/repo` foi passado, usar. Senão, derivar do worktree via `gh repo view --json owner,name`.
2. Resolver path de destino:
   - Se `dest_path` foi passado, usar.
   - Senão, ler `paths.plans` em `.ahrena/.directives` (default `.plans/`).
   - Path final: `<paths.plans>/{N}.md`.
3. Garantir que o diretório de destino existe (`mkdir -p`).

### Passo 2: Tentar MCP `get_issue` (preferido)

Per `lex-mcp` regra 1, se o servidor GitHub MCP estiver listado em `mcp.servers` e ativo:

```python
issue = mcp.github.get_issue(owner=owner, repo=repo, issue_number=N)
body = issue["body"]
```

Se sucesso, pular para Passo 4.

### Passo 3: Fallback `gh issue view --json body`

Per `lex-mcp` regra 4 (MCP indisponível), executar o fallback CLI documentado:

```bash
gh issue view {N} --repo {owner}/{repo} --json body --jq .body > .plans/{N}.md
```

Se `gh` também falha:

1. Retry único após 5 segundos de backoff.
2. Se persistir, oferecer ao usuário: (a) tentar novamente com outro comando, (b) pausar para investigação, (c) abortar.

### Passo 4: Gravar body em `.plans/{N}.md`

1. Se `.plans/{N}.md` já existe e tem conteúdo, **preservar blocos `<!-- not-flushed -->` ... `<!-- /not-flushed -->`** existentes:
   - Extrair todos os blocos `<!-- not-flushed -->` do arquivo atual.
   - Substituir o corpo principal pelo body novo da Issue.
   - Apender os blocos `<!-- not-flushed -->` no final.
2. Se `.plans/{N}.md` não existe, gravar o body diretamente (sem blocos `<!-- not-flushed -->` ainda).

A preservação de blocos locais permite re-load sem perder scratch da IA — re-load é só re-sincronizar o conteúdo canônico.

### Passo 5: Validar idempotência

Após gravar, executar uma segunda chamada (read-only) e comparar:

```bash
# Comparação canônica (após filtrar blocos não-flushados de ambos os lados)
diff <(strip-not-flushed .plans/{N}.md) <(gh issue view {N} --json body --jq .body)
```

Resultado esperado: nenhuma diferença.

Se houver diferença que não seja em blocos `<!-- not-flushed -->`, o re-load falhou silenciosamente — abortar e investigar.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `{N}.md` | Markdown (superset do body da Issue + blocos `<!-- not-flushed -->` preservados) | `<paths.plans>/{N}.md` |

## Exemplo de Execução

### Input de Exemplo

```
issue_number: 96
owner/repo: guardiatechnology/ahrena
dest_path: (default) .plans/96.md
```

### Output de Exemplo

`.plans/96.md` (logo após primeiro load, sem blocos não-flushados ainda):

```markdown
## Summary

**As** an Ahrena framework contributor,
**I want** to migrate plan storage to a 3-layer model,
**So that** plans live where they belong.

## Plan

### Objective
Refatorar a camada de armazenamento do plano para que o conteúdo viva em
três camadas com papéis claros: Issue body (canonical) + .plans/ (cache IA)
+ .ahrena/issues/ (Phase artifacts).

### Steps
- [x] Step 1 — Open Issue + branch + worktree
- [x] Step 2
- [ ] Step 3 — Rewrite lex-agent-planning (3 langs)
...

### Risks
- .plans/ perdida em fresh clone — mitigado por kata-load-plan-from-issue.
...
```

Após algumas edições da IA no cache local, o arquivo carrega blocos não-flushados:

```markdown
## Summary
...
(conteúdo do body — espelhado)
...

<!-- not-flushed -->
## Working notes
- 23:30 — começou Step 3; lex-agent-planning rewrite em pt-BR

## Next actions
1. Step 3.5 (split lex-issue-status)
2. Steps 6-8 (katas)

## Scratch
gh issue develop registra branch como "Development" na sidebar — não esquecer.
<!-- /not-flushed -->
```

## Restrições

- **Idempotente:** múltiplas execuções produzem o mesmo `.plans/{N}.md` para o mesmo estado do body da Issue.
- **Não flusha:** este kata é one-way (Issue → cache). Para gravar de volta, usar `kata-flush-plan-to-issue`.
- **Preserva blocos locais:** blocos `<!-- not-flushed -->` ... `<!-- /not-flushed -->` existentes no `.plans/{N}.md` são preservados; só o conteúdo canônico é re-sincronizado.
- **MCP > CLI:** preferir MCP `get_issue` quando o servidor estiver listado e ativo; CLI `gh issue view` é fallback documentado per `lex-mcp` regra 4.
- **Não cria Issue:** se a Issue `{N}` não existe, o kata falha com mensagem clara. Para criar Issue, usar `kata-plan-task` (Eunomia top-level) ou `kata-create-subtasks` (Eunomia subtask).

## Referências

- `lex-agent-planning` — modelo de 3 camadas e cadência de load/flush
- `lex-mcp` — preferência MCP + fallback CLI
- `codex-agent-planning` — manual operacional
- `kata-flush-plan-to-issue` — operação inversa (cache → Issue)
- `kata-plan-task` — criação inicial do plano (preenche body da Issue)
