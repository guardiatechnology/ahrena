# Codex: Custo de tokens em Pull Requests (Claude Code)

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Computação e estampagem de custo de assistência IA (Claude Code) em Pull Requests

## Visão Geral

Este Codex é a referência para computar tokens consumidos e custo estimado em USD durante o desenvolvimento que originou um Pull Request, e estampar esses números no body da PR. A computação parte dos logs JSONL persistidos pelo Claude Code em `~/.claude/projects/<project-hash>/`, agregados pela ferramenta open-source [`ccusage`](https://github.com/ryoppippi/ccusage). O bloco resultante é inserido no body da PR delimitado por marcadores HTML que garantem idempotência. É consultado por `kata-pr-cost-stamp` (que computa e atualiza a PR) e por `kata-contributing-pr` (que invoca o stamp como step opcional).

## Contexto

- **Domínio:** observabilidade financeira de assistência IA em Pull Requests do framework Ahrena e dos projetos consumidores.
- **Público-alvo:** agentes de IA que executam `kata-pr-cost-stamp`; mantenedores que revisam custos por PR; tech leads avaliando ROI da automação.
- **Atualização:** quando o formato de saída do `ccusage` mudar de major; quando a tabela de preços do Anthropic for revisada; quando novas dimensões (ex.: por usuário, por epic) forem adicionadas ao bloco.

## Conteúdo

### Princípios

1. **Opt-in por projeto.** A funcionalidade é desativada por padrão. O projeto declara `pr_cost_tracking.enabled: true` em `.ahrena/.directives` para ativar. Não há Lexis impondo o uso — custo é dado interno e cada time decide expor.
2. **Fonte única de preço.** A tabela de USD por modelo é a do `ccusage`, que reflete o pricing público da Anthropic. O kata nunca hardcoda valores; auditoria trimestral confirma se o `ccusage` continua atualizado.
3. **Idempotência por marcadores HTML.** O bloco é delimitado por `<!-- ahrena:cost-stamp:start -->` e `<!-- ahrena:cost-stamp:end -->`. Re-executar o kata sobre a mesma PR substitui o conteúdo entre os marcadores; nunca duplica.
4. **Não-bloqueante.** Falha do stamp (rede, ferramenta indisponível, parsing) não impede a PR. O kata loga o erro e continua.
5. **Estimativa, não fatura.** O número exibido é estimativa baseada em pricing público; a fatura real vem do console Anthropic. O bloco declara isso explicitamente.

### Fonte de dados

| Item | Detalhe |
|------|---------|
| Local dos logs | `~/.claude/projects/<project-hash>/*.jsonl` |
| Granularidade | uma linha JSONL por turno; cada turno traz `usage.input_tokens`, `usage.output_tokens`, `usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens`, `model`, `cwd`, `sessionId`, `timestamp` |
| Hash do projeto | derivado pelo Claude Code a partir do path absoluto do projeto; o `ccusage` traduz o hash de volta para o nome do projeto via `--project` ou `--instances` |
| Janela temporal | `[branch_creation_date, now]` por padrão. A subchave `pr_cost_tracking.window_override_days` está reservada para iteração futura; o kata não a consome nesta versão. |

### Ferramentas suportadas

| Ferramenta | Quando usar | Comando base |
|------------|-------------|--------------|
| `ccusage` (preferida) | Sempre que `npx`/`node` estiverem disponíveis | `npx ccusage@latest daily --project=<project-id> --since <YYYYMMDD> --json` |
| `scripts/pr-cost-stamp.sh` (fallback) | Ambientes sem Node (ex.: runners minimalistas) | parsing direto dos JSONL com `jq` |

O kata tenta `ccusage` primeiro. Falha de execução (não falha de dados) cai para o fallback. Falha do fallback emite warning e segue sem stamp.

### Filtro por projeto

Os subcomandos `daily`, `weekly`, `monthly` e `blocks` do `ccusage` aceitam `--project <id>` e `--instances` (breakdown por projeto). O `<id>` é o identificador derivado do caminho absoluto do projeto, com `/` substituído por `-` e prefixo `-` (ex.: `/Users/foo/repo` → `-Users-foo-repo`). Use a forma `--project=<id>` para preservar o prefixo `-` na linha de comando.

O subcomando `session` não aceita `--project` e por isso não é usado por este Codex.

O kata usa `--project=<id>` como filtro primário; o filtro por `cwd` na linha JSONL permanece como complemento documentado, útil quando o usuário trabalha em múltiplos clones do mesmo repositório com nomes idênticos.

### Formato do bloco

```markdown
<!-- ahrena:cost-stamp:start -->
## AI Assistance Cost (Claude Code)

| Métrica | Valor |
|---|---|
| Sessões | 3 |
| Tokens de input | 245.892 |
| Tokens de output | 18.432 |
| Cache reads | 1.245.888 |
| Cache writes | 89.234 |
| Custo estimado | $4.32 USD |
| Modelos | claude-opus-4-7 (78%), claude-sonnet-4-6 (22%) |

_Computado por `kata-pr-cost-stamp` em 2026-05-09T01:30:00Z. Janela: 2026-05-07 → agora. Fonte: ccusage 1.x._
_Estimativa baseada em pricing público da Anthropic; a fatura real vem do console._
<!-- ahrena:cost-stamp:end -->
```

Regras do bloco:

- Marcadores HTML em linhas próprias, sem indentação; o regex de upsert depende disso.
- Cabeçalho fixo `## AI Assistance Cost (Claude Code)` para discoverabilidade.
- Tabela com colunas idênticas em todas as línguas; rótulos traduzidos.
- Linha de procedência (timestamp UTC, janela, versão da ferramenta) sempre presente.
- Disclaimer de estimativa sempre presente.

### Idempotência

O kata aplica upsert por meio dos marcadores HTML:

1. Lê o body atual da PR via `gh pr view --json body`.
2. Procura o intervalo `<!-- ahrena:cost-stamp:start --> ... <!-- ahrena:cost-stamp:end -->`.
3. Se existe → substitui o intervalo pelo bloco recém-gerado.
4. Se não existe → anexa o bloco ao final do body, separado por linha em branco.
5. Atualiza a PR via `gh pr edit --body`.

Re-executar o kata 2x consecutivas produz exatamente o mesmo body se nenhuma sessão nova ocorreu no intervalo.

### Privacidade

- **Repositórios públicos:** o body da PR é público assim que a PR é aberta. Custo absoluto em USD pode ser sensível; cada time decide se expõe. O kata respeita o opt-in do `.directives`; nada é estampado por padrão.
- **Mascaramento opcional:** `pr_cost_tracking.mask_absolute_cost: true` substitui o valor absoluto por uma faixa qualitativa (`< $1`, `$1–$10`, `$10–$50`, `> $50`). Configuração ainda não implementada nesta primeira iteração — declarada para iteração futura.
- **Sem PII:** nenhum conteúdo da sessão (mensagens, prompts, código) é estampado. Apenas agregados numéricos.

### Limitações conhecidas

| Limitação | Mitigação |
|-----------|-----------|
| Sessões cross-machine não capturadas (apenas a máquina onde roda o kata conta) | Codex documenta; agregação cross-machine é fora de escopo desta iteração |
| Janela heurística `[branch_creation_date, now]` inclui sessões off-topic no mesmo projeto | Filtro por `--project` reduz; `cwd` complementa; futura iteração pode usar `sessionId` rastreado por hooks |
| Stacked PRs com camadas sobrepostas | Cada camada usa sua janela `[branch_checkout_time, now]`; aceitar imprecisão; codex documenta |
| Variação de pricing entre versões do `ccusage` | Smoke test de regressão em CI; pinning de versão mínima testada via `ccusage@<min-version>` |

### Decisões vigentes

| Aspecto | Decisão |
|---------|---------|
| Backend primário | `ccusage` via `npx ccusage@latest` |
| Filtro de projeto | flag nativa `--project <repo-name>` |
| Fallback | `scripts/pr-cost-stamp.sh` com `jq` |
| Adoção | opt-in via `pr_cost_tracking.enabled` no `.directives` |
| Trigger | step opcional em `kata-contributing-pr` |
| Idempotência | marcadores HTML `ahrena:cost-stamp:start/end` |
| Privacidade | sem mascaramento na primeira iteração; flag prevista para depois |

## Glossário

| Termo | Definição |
|-------|-----------|
| Stamp | bloco markdown delimitado por marcadores HTML, inserido no body da PR pelo `kata-pr-cost-stamp` |
| Janela de stamp | intervalo `[branch_creation_date, now]` no qual sessões Claude Code são consideradas para o cálculo |
| Cache reads / cache writes | tokens lidos do cache / gravados no cache prompt da Anthropic; pricing distinto dos tokens regulares |
| ccusage | CLI open-source que parseia os logs JSONL do Claude Code e calcula custo agregado |
| Upsert | operação que insere o bloco caso não exista ou substitui o existente entre os marcadores |

## Referências

- `lex-directives` — leitura obrigatória do `.ahrena/.directives` antes de qualquer execução
- `kata-pr-cost-stamp` — procedimento que aplica este Codex
- `kata-contributing-pr` — step opcional que invoca o stamp
- `ccusage` — https://github.com/ryoppippi/ccusage
- Anthropic pricing — https://www.anthropic.com/pricing
