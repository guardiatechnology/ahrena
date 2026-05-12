# Kata: Flushar Plano para a Issue

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Sincronização do cache local `.plans/{N}.md` para o body canônico da Issue do GitHub, conforme o modelo de armazenamento em 3 camadas do ADR-002

## Objetivo

Persistir o conteúdo de `.plans/{N}.md` (working memory da IA) no body da Issue do GitHub (canonical), filtrando blocos locais marcados `<!-- not-flushed -->` ... `<!-- /not-flushed -->`. Operação idempotente. Disparada nos 3 gatilhos canônicos de `lex-agent-planning`: cada transição de label `status:`, cada Step concluído, e fim de sessão.

## Quando Usar

- Transição de label `status:` na Issue/PR (`todo → development`, `development → to review`, etc.).
- Step do plano marcado como concluído (`[ ]` → `[x]`).
- Fim de sessão Claude Code (heartbeat finaliza ou agente Athena/Argos/Janus sai).
- Handoff entre agentes (entrega antes do próximo agente entrar).
- Solicitação explícita do usuário ("flush plan", "atualiza a Issue").

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `issue_number` | Sim | Número da Issue (`{N}` em `{owner}/{repo}#{N}`) |
| `owner/repo` | Não | Repo onde a Issue vive. Default: repo corrente do worktree |
| `source_path` | Não | Path do arquivo de cache local. Default: `<paths.plans>/{N}.md` |
| `force` | Não | `true` força grava mesmo se houve edição remota desconhecida. Default: `false` (alerta + oferece merge manual) |

## Workflow

```
Progresso:
- [ ] 1. Ler `.plans/{N}.md`
- [ ] 2. Filtrar blocos `<!-- not-flushed -->`
- [ ] 3. Detectar drift remoto (preflight)
- [ ] 4. Gravar via MCP `update_issue` (preferido)
- [ ] 5. Fallback `gh issue edit --body-file`
- [ ] 6. Validar idempotência
```

### Passo 1: Ler `.plans/{N}.md`

Carregar o conteúdo do cache local:

```bash
cat .plans/{N}.md
```

Se o arquivo não existe ou está vazio, abortar com mensagem orientando a rodar `kata-load-plan-from-issue` primeiro.

### Passo 2: Filtrar blocos `<!-- not-flushed -->`

Remover do conteúdo todos os blocos delimitados:

```
<!-- not-flushed -->
...qualquer conteúdo...
<!-- /not-flushed -->
```

O resultado é o **body candidato** para gravar na Issue. Implementação canônica via Python:

```python
import re
filtered = re.sub(
    r"<!-- not-flushed -->.*?<!-- /not-flushed -->",
    "",
    raw_content,
    flags=re.DOTALL,
)
# remove linhas vazias dupladas que sobraram pós-filtro
filtered = re.sub(r"\n{3,}", "\n\n", filtered).strip() + "\n"
```

### Passo 3: Detectar drift remoto (preflight)

Antes de gravar, **ler o body atual** da Issue e comparar com o último estado conhecido localmente:

1. `gh issue view {N} --json body --jq .body` → `remote_body_now`.
2. Comparar `remote_body_now` com `remote_body_at_last_load` (estado salvo localmente em `.plans/.{N}.remote.last` ou similar — opcional; se ausente, ler na hora).
3. Se diferente, houve **edição remota desconhecida** (outra sessão ou edição via UI do GitHub).

Comportamento na detecção de drift:

| Cenário | Default | Com `force=true` |
|---|---|---|
| Sem drift | Grava direto | Grava direto |
| Com drift | **Alerta** (não grava); oferece: (a) mostrar diff e abortar, (b) merge manual, (c) overwrite | Grava direto (sobrescreve mudanças remotas) |

Default `force=false` é mais conservador — protege contra perda de edições simultâneas.

### Passo 4: Gravar via MCP `update_issue` (preferido)

Per `lex-mcp` regra 1, se o servidor GitHub MCP estiver listado em `mcp.servers` e ativo:

```python
mcp.github.update_issue(
    owner=owner,
    repo=repo,
    issue_number=N,
    body=filtered_body,
)
```

Se sucesso, atualizar `.plans/.{N}.remote.last` com o body recém-gravado, e pular para Passo 6.

### Passo 5: Fallback `gh issue edit --body-file`

Per `lex-mcp` regra 4 (MCP indisponível):

```bash
# Gravar body candidato em arquivo temporário
echo "$filtered_body" > /tmp/issue-{N}-body.md

# Gravar na Issue via gh
gh issue edit {N} --repo {owner}/{repo} --body-file /tmp/issue-{N}-body.md

# Limpar
rm /tmp/issue-{N}-body.md
```

Se `gh` falha:

1. Retry único após 5 segundos de backoff.
2. Se persistir, oferecer ao usuário (per `lex-mcp` regra 4 passos 3-4): (a) tentar de novo, (b) pausar, (c) abortar.

### Passo 6: Validar idempotência

Após gravar, executar `gh issue view {N} --json body --jq .body` e comparar com `filtered_body`. Resultado esperado: igual.

Se houver diferença, o flush falhou silenciosamente — abortar e investigar (normalmente: encoding, escaping de caracteres especiais, ou rate-limit silenciado pelo GitHub).

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Body atualizado | Markdown (sem blocos `<!-- not-flushed -->`) | Issue `{N}` no GitHub |
| `.plans/.{N}.remote.last` (opcional) | Markdown | Local cache do último estado remoto conhecido (preflight do próximo flush) |

## Exemplo de Execução

### Input de Exemplo

```
issue_number: 96
owner/repo: guardiatechnology/ahrena
source_path: (default) .plans/96.md
force: false
```

### `.plans/96.md` antes do flush

```markdown
## Summary
...

## Plan
### Steps
- [x] Step 1
- [x] Step 2
- [x] Step 3 — Rewrite lex-agent-planning (Just completed)
- [ ] Step 4
...

<!-- not-flushed -->
## Working notes
- 23:55 — terminou Step 3; cache aqui está mais novo que o body da Issue.

## Scratch
testando se update_issue MCP suporta body de >50KB. Sim, suporta (limite ~65KB).
<!-- /not-flushed -->
```

### Body gravado na Issue após flush

```markdown
## Summary
...

## Plan
### Steps
- [x] Step 1
- [x] Step 2
- [x] Step 3 — Rewrite lex-agent-planning (Just completed)
- [ ] Step 4
...
```

Blocos `<!-- not-flushed -->` ficam apenas no cache local. Quando outra sessão rodar `kata-load-plan-from-issue`, ela recebe o body sem os blocos — preserva-se a propriedade de que canonical = body da Issue.

## Restrições

- **Idempotente:** múltiplas execuções produzem o mesmo body se o `.plans/{N}.md` não mudou.
- **Preflight obrigatório (default):** sem `force=true`, drift remoto bloqueia o flush e exige decisão humana.
- **MCP > CLI:** preferir MCP `update_issue`; CLI `gh issue edit --body-file` é fallback per `lex-mcp` regra 4.
- **Não cria Issue:** se `{N}` não existe, falha imediato. Para criar, usar `kata-plan-task`.
- **Não toca labels nem assignees:** flush opera apenas no body. Labels (incluindo `status:*`) são responsabilidade do owner da transição (per `lex-agent-planning` e `lex-issue-status`).
- **Não loga conteúdo:** filtragem `<!-- not-flushed -->` é silenciosa por design — o body candidato não vaza em log de sessão.

## Referências

- `lex-agent-planning` — modelo de 3 camadas e cadência de flush (3 gatilhos canônicos)
- `lex-mcp` — preferência MCP + fallback CLI
- `lex-issue-status` — labels canônicos; flush é disparado em cada transição
- `codex-agent-planning` — manual operacional
- ADR-002 — decisão de arquitetura
- `kata-load-plan-from-issue` — operação inversa (Issue → cache)
- `kata-pr-prepare` — invoca `kata-flush-plan-to-issue` antes de abrir o PR
- `warrior-athena`, `warrior-argos`, `warrior-janus` — agentes que disparam flush em transições
