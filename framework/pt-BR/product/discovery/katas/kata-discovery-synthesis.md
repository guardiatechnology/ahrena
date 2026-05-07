# Kata: Síntese de Insights de Discovery

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Product Discovery — leitura de fontes heterogêneas e produção de insights estruturados sob `docs/discovery/{topic}/insights/`

## Objetivo

Padronizar como `warrior-pitia` lê fontes (APIs, OpenAPI, Notion, Figma, transcrições, processos legados, telas) e produz insights de Product Discovery em formato canônico, com `status: proposed` e referências às fontes consultadas. O insight é unidade indivisível de descoberta — um insight por arquivo, com front-matter conforme `codex-discovery-artifacts`.

## Quando Usar

- Quando `cry-discovery` é invocado com um `topic` e uma lista de `source_refs[]`
- Quando o usuário pede explicitamente que `warrior-pitia` estude um conjunto de fontes para um topic existente
- Quando `warrior-pitia` está em estado `refining` e precisa devolver uma v2 de um insight (transição `refining → under_review`)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `topic` | Sim | Tema da iniciativa de Discovery em kebab-case (ex: `accountant-onboarding`). Cria o diretório `docs/discovery/{topic}/` se não existir |
| `source_refs[]` | Sim (≥1) | Lista de URLs ou paths das fontes a serem estudadas. Pode incluir Notion, Figma, OpenAPI, transcrições em `docs/transcripts/`, repositórios em GitHub |
| `language` | Não | Sobrescreve `language.default` do `.directives` (default: pt-BR) |
| `mode` | Não | `new` (default — cria insights novos) ou `refine` (atualiza insight existente em `status: refining`) |
| `target_insight_id` | Condicional | Obrigatório se `mode == refine` — id do insight a ser atualizado |
| `feedback` | Condicional | Obrigatório se `mode == refine` — texto do feedback humano que motivou o refinamento |

## Workflow

```
Progresso:
- [ ] 1. Leitura das diretivas e codex
- [ ] 2. Leitura das fontes via MCP ou Read
- [ ] 3. Identificação de candidatos a insight
- [ ] 4. Aplicação do schema canônico
- [ ] 5. Geração do(s) arquivo(s)
- [ ] 6. Validação final
```

### Passo 1: Leitura das diretivas e codex

1. Ler `.ahrena/.directives` para confirmar `language.default` e `naming.casing`
2. Ler `codex-discovery-artifacts` para internalizar:
   - Endereçamento `docs/discovery/{topic}/insights/{NNN}-{slug}.md`
   - Schema completo do front-matter
   - Máquina de estados e transições válidas
3. Ler `lex-discovery-flow` para internalizar os HARD-GATEs aplicáveis (especialmente HARD-GATE 2: criação inicial é da própria Pítia, mas qualquer transição posterior exige direção humana)

### Passo 2: Leitura das fontes via MCP ou Read

Para cada item em `source_refs[]`, acionar a ferramenta apropriada:

| Tipo de fonte | Ferramenta | Kata associado |
|---------------|------------|----------------|
| URL Notion | MCP `notion-fetch` ou `notion-search` | `kata-mcp-notion-read` |
| URL Figma | MCP Figma `get_design_context` ou `get_metadata` | `kata-mcp-figma-extract` |
| URL GitHub (repo, issue, PR, OpenAPI) | MCP `gh-*` ou `Read` para arquivos locais | `kata-mcp-github-read` |
| Path local (`docs/transcripts/...`, OpenAPI YAML, processo) | `Read` direto | — |

Quando o MCP correspondente não estiver listado em `mcp.servers` do `.directives`, seguir `lex-mcp` regra 4 (oferecer escolha entre fallback CLI, pausar, ou abortar).

Acumular o conteúdo lido como evidência. Quando o conteúdo for extenso, salvar trechos relevantes citados literalmente (com aspas) no corpo do insight.

### Passo 3: Identificação de candidatos a insight

Para cada candidato a insight, verificar:

1. **Unidade indivisível:** o insight expressa **uma** observação. Se o conteúdo cobre 2 dores distintas, são 2 insights separados.
2. **Acionável conceitualmente:** o insight aponta para uma implicação para o negócio, mesmo que ainda não proponha solução.
3. **Rastreável:** as `source_refs[]` no front-matter cobrem todas as fontes que sustentam essa observação.
4. **Sem solução embutida:** se o texto começa a propor solução, mover a parte de solução para "Implicação inicial" como hipótese, não como decisão. A formação de Idea é responsabilidade de `warrior-phanes`.

### Passo 4: Aplicação do schema canônico

Para cada candidato confirmado, montar o front-matter conforme `codex-discovery-artifacts`:

- `id`: `{topic}/insights/{NNN}-{slug}` — `{NNN}` é o próximo número sequencial dentro do topic (ler `docs/discovery/{topic}/insights/` e incrementar)
- `topic`: idêntico ao `topic` de input
- `status`: `proposed` (sempre, na criação inicial)
- `source_refs`: lista das fontes efetivamente consultadas (não copiar input cru — apenas as que realmente sustentam ESTE insight)
- `tags`: opcionais; usar quando ajudam a agregar com outros insights
- `created_at`, `updated_at`: timestamp ISO 8601 corrente
- Campos condicionais (`merged_into`, `idea_ref`, `rejected_reason`, `awaiting_evidence_reason`): `null` na criação

Estruturar o corpo Markdown nas 4 seções: **Observação**, **Fonte**, **Implicação inicial**, **Perguntas em aberto**.

### Passo 5: Geração do(s) arquivo(s)

1. Criar diretórios intermediários se necessário (`docs/discovery/{topic}/insights/`)
2. Escrever um arquivo por insight identificado
3. Quando `mode == refine`:
   - Não criar arquivo novo — atualizar o existente identificado por `target_insight_id`
   - Atualizar `updated_at` para o timestamp atual
   - Reescrever as 4 seções do corpo incorporando o `feedback` recebido
   - Após persistir a v2, atualizar `status: under_review` — esta transição é autorizada per HARD-GATE 2 da `lex-discovery-flow` (precondição (d) cumprida: v2 redigida com `updated_at` atualizado), executada por Pítia para fechar o ciclo `refining → under_review` iniciado pela direção humana original
   - Registrar em mensagem ao humano que a v2 está pronta para nova avaliação

### Passo 6: Validação final

Antes de entregar:

- [ ] Cada insight criado tem `id` único, `topic` correto e `source_refs[]` com pelo menos 1 entrada
- [ ] Em `mode == new`: cada insight criado tem `status: proposed`
- [ ] Em `mode == refine`: o insight atualizado tem `status: under_review` (Pítia fechou o ciclo per HG2 precondição (d)) e `updated_at` atualizado
- [ ] As 4 seções do corpo (Observação, Fonte, Implicação inicial, Perguntas em aberto) estão preenchidas — sem placeholders como "TBD"
- [ ] Nenhum insight propõe solução; toda hipótese de solução está na seção "Perguntas em aberto" como pergunta
- [ ] O conteúdo respeita `lex-tone` (direto, estratégico, sem buzzwords) e o idioma confere com `language.default`

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Insight novo | Markdown com front-matter YAML | `docs/discovery/{topic}/insights/{NNN}-{slug}.md` |
| Insight atualizado (modo refine) | Markdown com front-matter YAML (mesmo path) | `docs/discovery/{topic}/insights/{NNN}-{slug}.md` |
| Resumo da execução | Mensagem ao humano | Sessão atual — lista os arquivos criados/atualizados e aponta as `Perguntas em aberto` que pedem evidência |

## Exemplo de Execução

### Input de Exemplo

```
topic: scheduled-payments-research
source_refs:
  - https://www.notion.so/guardia/interview-accountant-2026-05-04-abc123
  - docs/transcripts/process-walkthrough-erp-x.md
  - https://github.com/guardiatechnology/erp-x-spec/blob/main/openapi.yaml
mode: new
```

### Output de Exemplo

Arquivo gerado: `docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md`

```markdown
---
id: "scheduled-payments-research/insights/001-manual-reconciliation-bottleneck"
topic: "scheduled-payments-research"
status: proposed
source_refs:
  - "https://www.notion.so/guardia/interview-accountant-2026-05-04-abc123"
  - "docs/transcripts/process-walkthrough-erp-x.md"
tags:
  - reconciliation
  - manual-process
created_at: "2026-05-06T11:00:00Z"
updated_at: "2026-05-06T11:00:00Z"
merged_into: null
idea_ref: null
rejected_reason: null
awaiting_evidence_reason: null
---

# Insight: Conciliação manual ERP × extrato é o maior gargalo operacional

## Observação

Contadores em escritórios de médio porte gastam, em média, 4h por semana conciliando manualmente lançamentos divergentes entre o ERP e o extrato bancário. A divergência mais frequente é diferença de data de competência vs. caixa, seguida de duplicação de baixas.

## Fonte

- Entrevista com contador X (2026-05-04): "passo praticamente toda terça-feira só conciliando — nada do que faço aqui agrega valor"
- Walkthrough do processo no ERP X: 7 telas para conciliar 1 lançamento divergente

## Implicação inicial

Reduzir o tempo gasto em conciliação manual libera capacidade do contador para análise — atividade percebida como de maior valor por ele e pelo escritório.

## Perguntas em aberto

- Qual a distribuição real do tempo gasto entre os tipos de divergência (data, duplicação, valor, contraparte)?
- Qual a taxa de aceitação esperada de uma sugestão automática com confiança ≥ 90%?
- Quais ERPs além do X concentram a base de clientes-alvo?
```

## Restrições

- Nunca propor solução no insight; solução é responsabilidade de Phanes via Idea
- Nunca consolidar múltiplos insights em um arquivo único — um insight por arquivo
- As únicas transições de `status` que Pítia executa autonomamente são: `[*] → proposed` (modo new, criação inicial) e `refining → under_review` (modo refine, fechamento do ciclo após reescrita da v2 — HG2 precondição (d) cumprida). Demais transições exigem direção humana explícita per HARD-GATE 2 da `lex-discovery-flow`
- Nunca embutir referência a `idea_ref` na criação inicial; esse campo é preenchido por Phanes
- Sempre citar trecho literal (com aspas) ao referenciar entrevista ou doc — evita interpretação em segundo nível

## Referências

- `lex-discovery-flow` — lei aplicável, com os HARD-GATEs que governam status
- `codex-discovery-artifacts` — schema completo, máquina de estados, endereçamento
- `kata-mcp-notion-read`, `kata-mcp-figma-extract`, `kata-mcp-github-read` — procedimentos de leitura via MCP
- `lex-mcp` — fallback quando MCP indisponível
- `lex-tone`, `codex-tone` — estilo de redação
- `warrior-pitia` — agente que executa este Kata
