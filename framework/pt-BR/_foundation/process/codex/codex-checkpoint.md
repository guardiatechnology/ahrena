# Codex: Checkpoint de Sessão

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Uso operacional do `.checkpoint` complementar a `lex-checkpoint` e `lex-agent-planning`

## Visão Geral

`.checkpoint` é um arquivo de **scratchpad de sessão** localizado na raiz do workspace, gitignored, que captura o contexto de janela de trabalho que NÃO cabe num plano único. Este Codex documenta como o `.checkpoint` se relaciona com `lex-agent-planning`, quando vale invocar, e como debugar inconsistências.

A Lei correspondente é `lex-checkpoint`. Os procedimentos operacionais são `kata-checkpoint-read` (início de sessão) e `kata-checkpoint-save` (sob demanda + fim de sessão). O atalho de usuário é `cry-checkpoint`.

## Contexto

- **Domínio:** continuidade de contexto entre sessões com agentes IA
- **Público-alvo:** Warriors, Katas, agentes genéricos, e usuários humanos que invocam `cry-checkpoint`
- **Atualização:** quando `lex-checkpoint` muda, ou quando o ecossistema de Katas/Cries em torno dele evolui

## Conteúdo

### Princípios

1. **Sessão, não task.** Plano (`lex-agent-planning`) é a fonte de verdade da task — committed, com Steps, Decisões, Riscos. Checkpoint cobre o que não cabe num plano único: foco da janela, hand-off entre múltiplos planos ativos, threads paralelas, scratchpad livre.
2. **Schema enxuto e canônico.** 4 seções fixas (Session focus, Active plans, Open threads, Notes). Nada além disso — campos que duplicariam plano (Activity, Progress, Decisions made, Next steps, Artifacts produced) estão proibidos.
3. **Gatilhos discretos.** Read no início de sessão; save sob demanda do usuário ou ao encerrar sessão com mudança de contexto. Sem auto-save por activity.
4. **Degradação graciosa.** `.checkpoint` ausente é cenário válido. Schema antigo gera warning de deprecation, não erro. Sobrescrita silenciosa ao próximo save.

### Quando vale a pena invocar

| Cenário | Ação |
|---------|------|
| Início de conversa nova com agente que tem `.checkpoint` salvo | `kata-checkpoint-read` (automático no boot) |
| Conversa exploratória sem plano formal, com decisões transversais | `cry-checkpoint` ao final para preservar Open threads e Notes |
| Múltiplos planos ativos em paralelo na sessão | `cry-checkpoint` para registrar Active plans com 1-line context |
| Pausa longa antes de retomar amanhã | `cry-checkpoint` antes de fechar |
| Task simples encapsulada em um único plano, sem threads paralelas | NÃO invocar — plano já cobre tudo |
| Mudança de plano (encerrei plan-N, começando plan-M) | Atualizar Active plans via `cry-checkpoint` |

### Quando NÃO usar

- **Para registrar progresso de task formal** — vai no plano (`lex-agent-planning`)
- **Para listar artefatos produzidos** — `git diff` + plano cobrem
- **Para versionar decisões arquiteturais** — ADR (`docs/adr/ADR-NNN-*.md`)
- **Para tracking de bug ativo** — Issue do GitHub
- **Para handoff entre desenvolvedores** — não funciona; `.checkpoint` é gitignored e per-machine

### Padrões e Convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| Nome do arquivo | `.checkpoint` (ponto-prefixado, sem extensão) | `.checkpoint` |
| Localização | raiz do workspace | `/path/to/repo/.checkpoint` |
| Encoding | UTF-8, line endings LF | — |
| Schema | 4 seções obrigatórias + frontmatter de 2 campos | Ver `lex-checkpoint` rule 3 |
| Active plans entries | `\`plan-NNN\` — slug; 1-linha de contexto ≤ 80 chars` | `` `plan-040` — reposicionamento; em redação `` |
| Open threads entries | 1-2 linhas em bullet | `- Avaliar absorção de Risks da sessão` |
| Notes | texto livre, sem schema | qualquer markdown |
| Tamanho típico | < 4 KB | — |

### Decisões Vigentes

| Decisão | Status | Origem |
|---------|--------|--------|
| Schema enxuto (4 seções) substitui schema antigo (8 campos) | Ativa | plan-040, issue #73 |
| Save sob demanda + fim de sessão (não automático por activity) | Ativa | plan-040 |
| Sem tool de migration dedicada — read detecta schema antigo, emite warning, save sobrescreve | Ativa | plan-040 |
| `Active plans` é hint opcional para outros agentes (ex: plan-026 observer); não fonte de scope | Ativa | plan-040 |

### Restrições Técnicas

- `.checkpoint` é **per-machine, per-developer** — não sincroniza entre máquinas, não é commitado
- Escrita é **last-write-wins** — múltiplos agentes simultâneos competem pelo arquivo (cenário raro)
- Read em schema antigo é **leitura silenciosa** — não tenta parsear nem migrar; só emite warning e prossegue
- Tamanho não tem limite hard, mas > 8 KB indica que conteúdo de plano vazou — auditar

## Troubleshooting

### `.checkpoint` ausente após várias sessões

- **Causa provável:** usuário nunca invocou `cry-checkpoint` e nenhuma sessão teve mudança de contexto fora do plano.
- **Ação:** comportamento esperado. Se há contexto a preservar, invocar `cry-checkpoint`.

### `kata-checkpoint-read` emite warning de schema antigo

- **Causa:** `.checkpoint` foi gravado antes da reescrita (issue #73).
- **Ação:** `rm .checkpoint` ou aguardar próxima invocação de save (sobrescreve com schema novo).

### Conteúdo do plano apareceu em Notes do checkpoint

- **Causa:** agente confundiu escopos.
- **Ação:** mover conteúdo para `## Steps` ou `## Decisões fechadas` do plano correspondente; remover de Notes.

### `Active plans` cresce indefinidamente

- **Causa:** planos done não foram removidos da lista.
- **Ação:** ao encerrar plano (status `done`), atualizar `Active plans` removendo a entrada via `cry-checkpoint`.

### Checkpoint inconsistente entre sessões paralelas (mesmo workspace)

- **Causa:** múltiplos agentes Claude Code/Cursor escrevendo simultaneamente.
- **Ação:** `.checkpoint` é per-workspace; sessões paralelas ativas no mesmo workspace são raras. Se ocorrer, last-write-wins resolve — usuário invoca `cry-checkpoint` na sessão que tem o estado correto para sobrescrever.

## Glossário

| Termo | Definição |
|-------|-----------|
| Session focus | 1-3 frases descrevendo o foco da janela de trabalho atual |
| Active plans | Lista de plan-IDs ativos na sessão com 1-line context cada |
| Open threads | Threads de conversa que não viraram plano formal mas devem ser retomadas |
| Notes | Scratchpad livre — texto, links, lembretes |
| Schema antigo | Estrutura pré-issue-#73 com Activity/Status/Progress/Decisions/Next steps/Artifacts produced |
| Schema novo | Estrutura canônica de 4 seções (Session focus, Active plans, Open threads, Notes) |

## Referências

- `lex-checkpoint` — Lei que define o schema e os gatilhos
- `lex-agent-planning` — Lei do plano (fonte de verdade da task)
- `kata-checkpoint-read` — procedimento de leitura ao iniciar sessão
- `kata-checkpoint-save` — procedimento de salvamento sob demanda + fim de sessão
- `cry-checkpoint` — atalho de usuário para `kata-checkpoint-save`
- Issue #73 — reposicionamento do `.checkpoint`
- Plano-040 — execução do reposicionamento
