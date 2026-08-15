---
name: kata-flush-plan-to-subissue
description: "Flushar Plano para a Sub-issue. Sincronização do cache local provider-specific (.claude/plans/plan-{M}-{slug}.md ou .cursor/plans/plan-{M}-{slug}.md) para o body canônico da sub-issue Plan, conforme o modelo hierárquico de lex-agent-planning"
---

# Kata: Flushar Plano para a Sub-issue

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Sincronização do cache local provider-specific (`.claude/plans/plan-{M}-{slug}.md` ou `.cursor/plans/plan-{M}-{slug}.md`) para o body canônico da sub-issue Plan, conforme o modelo hierárquico de `lex-agent-planning`

## Workflow

```
Progresso:
- [ ] 1. Resolver provider + path de origem
- [ ] 2. Ler o cache local
- [ ] 3. Filtrar blocos `<!-- not-flushed -->`
- [ ] 4. Detectar drift remoto (preflight)
- [ ] 5. Gravar via MCP `update_issue` (preferido)
- [ ] 6. Fallback `gh issue edit --body-file`
- [ ] 7. Validar idempotência
```

### Passo 1: Resolver provider + path de origem

1. Se `source_path` foi passado, usar.
2. Senão, detectar o runtime do agente:
   - Claude Code → `.claude/plans/plan-{M}-{slug}.md`
   - Cursor → `.cursor/plans/plan-{M}-{slug}.md`
3. Se o arquivo não existe ou está vazio, abortar com mensagem orientando a rodar `kata-load-plan-from-subissue` primeiro.

### Passo 2: Ler o cache local

```bash
cat {source_path}
```

Validar que o conteúdo carrega o schema canônico mínimo (Summary, Plan section). Se faltar estrutura, abortar e orientar a sincronizar primeiro via `kata-load-plan-from-subissue`.

### Passo 3: Filtrar blocos `<!-- not-flushed -->`

Remover do conteúdo todos os blocos delimitados:

```
<!-- not-flushed -->
...qualquer conteúdo...
<!-- /not-flushed -->
```

O resultado é o **body candidato** para gravar na sub-issue. Implementação canônica via Python:

```python
import re
filtered = re.sub(
    r"<!-- not-flushed -->.*?<!-- /not-flushed -->",
    "",
    raw_content,
    flags=re.DOTALL,
)
# colapsa apenas linhas em branco triplas+ para duplas; preserva indentação
filtered = re.sub(r"\n\n\n+", "\n\n", filtered).strip() + "\n"
```

A filtragem é silenciosa por design — o body candidato não vaza em log de sessão.

### Passo 4: Detectar drift remoto (preflight)

Antes de gravar, **ler o body atual** da sub-issue e comparar com o último estado conhecido localmente:

1. `gh issue view {M} --repo {owner}/{repo} --json body --jq .body` → `remote_body_now`.
2. Comparar `remote_body_now` com `remote_body_at_last_load` (estado salvo localmente em `.claude/plans/.{M}.remote.last` ou similar — opcional; se ausente, ler na hora).
3. Se diferente, houve **edição remota desconhecida** (outra sessão flushou em paralelo ou edição via UI do GitHub).

Comportamento na detecção de drift:

| Cenário | Default (`force=false`) | Com `force=true` |
|---|---|---|
| Sem drift | Grava direto | Grava direto |
| Com drift | **Alerta** (não grava); oferece: (a) mostrar diff e abortar, (b) merge manual, (c) overwrite | Grava direto (sobrescreve mudanças remotas) |

Default `force=false` é mais conservador — protege contra perda de edições simultâneas.

### Passo 5: Gravar via MCP `update_issue` (preferido)

Per `lex-mcp` regra 1, se o servidor GitHub MCP estiver listado em `mcp.servers` e ativo:

```python
mcp.github.update_issue(
    owner=owner,
    repo=repo,
    issue_number=M,
    body=filtered_body,
)
```

Se sucesso, atualizar `.claude/plans/.{M}.remote.last` (ou equivalente no Cursor) com o body recém-gravado, e pular para Passo 7.

### Passo 6: Fallback `gh issue edit --body-file`

Per `lex-mcp` regra 4 (MCP indisponível):

```bash
# Gravar body candidato em arquivo temporário
echo "$filtered_body" > /tmp/subissue-{M}-body.md

# Gravar na sub-issue via gh
gh issue edit {M} --repo {owner}/{repo} --body-file /tmp/subissue-{M}-body.md

# Limpar
rm /tmp/subissue-{M}-body.md
```

Se `gh` falha:

1. Retry único após 5 segundos de backoff.
2. Se persistir, oferecer ao usuário (per `lex-mcp` regra 4 passos 3-4): (a) tentar de novo, (b) pausar, (c) abortar.

### Passo 7: Validar idempotência

Após gravar, executar `gh issue view {M} --json body --jq .body` e comparar com `filtered_body`. Resultado esperado: igual.

Se houver diferença, o flush falhou silenciosamente — abortar e investigar (normalmente: encoding, escaping de caracteres especiais, ou rate-limit silenciado pelo GitHub).

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Body atualizado | Markdown (sem blocos `<!-- not-flushed -->`) | Sub-issue `{M}` no GitHub |
| `.claude/plans/.{M}.remote.last` (opcional) | Markdown | Cache local do último estado remoto conhecido (preflight do próximo flush) |

## Exemplo de Execução

### Input de Exemplo

```
subissue_number: 201
owner/repo: guardiatechnology/example-repo
source_path: (default; provider Claude Code) .claude/plans/plan-201.md
force: false
```

### `.claude/plans/plan-201.md` antes do flush

```markdown
## Summary

Refatorar o agregado Ledger para event sourcing, separando comandos
(write-side) de leitura (read-side projection).

Parent: #200

## Plan
### Steps
- [x] Step 1 — Modelar LedgerEvent base class
- [x] Step 2 — Reescrever Ledger.apply() como event projection (just completed)
- [ ] Step 3 — Repository persistindo events em vez de state
...

<!-- not-flushed -->
## Working notes
- 15:10 — terminou Step 2; cache aqui está mais novo que o body da sub-issue.

## Scratch
discriminated union vs class hierarchy: ficou class hierarchy mais legível.
<!-- /not-flushed -->
```

### Body gravado na sub-issue após flush

```markdown
## Summary

Refatorar o agregado Ledger para event sourcing, separando comandos
(write-side) de leitura (read-side projection).

Parent: #200

## Plan
### Steps
- [x] Step 1 — Modelar LedgerEvent base class
- [x] Step 2 — Reescrever Ledger.apply() como event projection (just completed)
- [ ] Step 3 — Repository persistindo events em vez de state
...
```

Blocos `<!-- not-flushed -->` ficam apenas no cache local. Quando outra sessão rodar `kata-load-plan-from-subissue`, ela recebe o body sem os blocos — preserva-se a propriedade de que canonical = body da sub-issue.

## Restrições

- **Idempotente:** múltiplas execuções produzem o mesmo body se o cache local não mudou.
- **Preflight obrigatório (default):** sem `force=true`, drift remoto bloqueia o flush e exige decisão humana.
- **MCP > CLI:** preferir MCP `update_issue`; CLI `gh issue edit --body-file` é fallback per `lex-mcp` regra 4.
- **Não cria sub-issue:** se `{M}` não existe, falha imediato. Para criar, usar `kata-plan-task` ou `kata-decompose-issue-into-plans`.
- **Não toca labels nem assignees:** flush opera apenas no body. Labels (incluindo `status:*`) são responsabilidade do owner da transição (per `lex-agent-planning` e `lex-issue-status`).
- **Não loga conteúdo filtrado:** o body candidato não aparece em logs de sessão.
- **Preserva indentação:** a regex de colapso de linhas vazias atua apenas em sequências `\n\n\n+`; nunca em espaços horizontais (que destruiriam indentação Markdown de listas e code blocks).
