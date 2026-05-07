# Kata: Promoção de Insight Aprovado a Idea

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Product Discovery — promoção de insight com `status: approved` em Idea sob `docs/discovery/{topic}/ideas/`

## Objetivo

Padronizar como `warrior-phanes` lê um insight aprovado e produz uma Idea no schema canônico (`problem`, `hypothesis`, `target_user`, `success_metric`, `effort_estimate`, `linked_insights[]`), atualizando o insight de origem para `status: promoted` com `idea_ref` apontando para a Idea criada. A operação é regida pelo HARD-GATE 1 da `lex-discovery-flow` — qualquer precondição não atendida bloqueia a promoção.

## Quando Usar

- Quando `cry-ideation` é invocado com o `insight_path` de um insight cujo `status` é `approved`
- Quando o usuário pede explicitamente que `warrior-phanes` promova um ou mais insights aprovados a uma Idea (caso múltiplos insights compartilharem o mesmo problema, eles podem ser combinados em uma única Idea via `linked_insights[]`)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `insight_path` | Sim | Path canônico do insight a promover. Pode ser uma string ou um array (quando múltiplos insights formam uma Idea única) |
| `language` | Não | Sobrescreve `language.default` do `.directives` (default: pt-BR) |
| `additional_context` | Não | Contexto extra fornecido pelo humano (ex: dados de telemetria, hipótese refinada) que ajuda a montar `success_metric` ou `effort_estimate` |

## Workflow

```
Progresso:
- [ ] 1. Validação preflight de input (HG1 a, d)
- [ ] 2. Leitura dos insights de origem
- [ ] 3. Síntese dos 5 campos de conteúdo obrigatórios
- [ ] 4. Validação preflight de output (HG1 b, c) — antes da escrita
- [ ] 5. Geração do arquivo da Idea
- [ ] 6. Atualização do(s) insight(s) de origem
- [ ] 7. Validação pós-escrita (HG1 e) com rollback
- [ ] 8. Validação final integral
```

### Passo 1: Validação preflight de input (HG1 a, d)

Para cada insight em `insight_path`, verificar **antes de qualquer leitura ou síntese**:

- [ ] (a) `insight.status == approved` (lê o front-matter; se diferente de `approved`, abortar e informar o humano)
- [ ] (d) Todos os insights em `insight_path` têm o mesmo `topic` (se divergir, abortar; uma Idea não pode misturar topics)

Se qualquer (a) ou (d) falhar, **interromper imediatamente** e informar o humano com:

- Quais insights falharam em qual precondição
- Que ação humana destrava (ex: aprovar o insight, separar em Ideas distintas por topic)

Phanes **NÃO** muda status de insight para `approved` — isso é prerrogativa humana per HARD-GATE 2 da `lex-discovery-flow`.

### Passo 2: Leitura dos insights de origem

Ler integralmente o(s) arquivo(s) de insight, capturando:

1. Front-matter (`id`, `topic`, `tags`, `source_refs`)
2. Corpo: **Observação**, **Fonte**, **Implicação inicial**, **Perguntas em aberto**
3. Histórico de mudanças relevantes (git log do arquivo) — útil para entender o que foi refinado e por quê

Acumular o conteúdo como base para a síntese da Idea.

### Passo 3: Síntese dos 5 campos de conteúdo obrigatórios

Para cada campo obrigatório, aplicar a heurística:

| Campo | Heurística |
|-------|------------|
| `problem` | Reescrever a "Observação" do insight como problema concreto em 1 frase, com magnitude quando o insight tiver dado quantitativo. Sem solução embutida |
| `hypothesis` | Estrutura "Se X, então Y, medido por Z". X = solução conceitual; Y = efeito esperado; Z = critério mensurável. Quando o insight não tiver evidência suficiente para fixar Y/Z, marcar com placeholder explícito (ex: "Y a confirmar via experimento") em vez de inventar número |
| `target_user` | Extrair do insight a persona específica (papel + contexto). Evitar "todos os usuários"; quando o insight não nomear, usar a persona da fonte primária |
| `success_metric` | Métrica leading ou lagging com `baseline` (do insight) e `meta` (proposta inicial baseada em ganho conservador, e.g.: -50% do baseline). Quando o insight não tiver baseline, declarar a necessidade de baseline antes da implementação |
| `effort_estimate` | T-shirt size (`XS`, `S`, `M`, `L`, `XL`) com 1 frase entre parênteses justificando: dependências externas, modelo a ser construído, integrações |

A síntese é proposição inicial — `warrior-prometheus` posteriormente refina ao transformar em PRD.

### Passo 4: Validação preflight de output (HG1 b, c) — ANTES da escrita

Sobre a Idea sintetizada (em memória, antes de gravar arquivo), verificar:

- [ ] (b) `linked_insights[]` da Idea tem pelo menos 1 entrada (será preenchido pelos `id` dos insights lidos no Passo 2)
- [ ] (c) Os 5 campos de conteúdo obrigatórios — `problem`, `hypothesis`, `target_user`, `success_metric`, `effort_estimate` — têm texto substantivo (não placeholder cru como "TBD" ou string vazia). Se a heurística do Passo 3 não conseguiu produzir conteúdo para algum campo, **interromper** e informar o humano qual evidência adicional destrava

Se qualquer (b) ou (c) falhar, **abortar antes de gravar** — nenhum arquivo é criado, nenhum insight é atualizado.

### Passo 5: Geração do arquivo da Idea

1. Determinar `{NNN}`: próximo sequencial dentro de `docs/discovery/{topic}/ideas/`
2. Determinar `{slug}`: kebab-case curto resumindo a Idea (não copiar do insight; pode ser distinto)
3. Compor `id`: `{topic}/ideas/{NNN}-{slug}`
4. Montar front-matter conforme `codex-discovery-artifacts`
5. Estruturar o corpo Markdown nas 3 seções: **Síntese**, **Insights de origem** (lista enumerada referenciando `linked_insights[]`), **Próximos passos** (sugestões de validação adicional, sem decisão de prioridade)
6. Criar diretórios intermediários se necessário e gravar o arquivo

### Passo 6: Atualização do(s) insight(s) de origem

Para cada insight em `linked_insights[]`:

1. Atualizar `status` para `promoted`
2. Preencher `idea_ref` com o `id` da Idea criada
3. Atualizar `updated_at` para o timestamp atual
4. Manter o resto do arquivo intocado (corpo do insight permanece como auditoria)

Esta atualização é **a única transição de status que `warrior-phanes` executa autonomamente** — autorizada por HARD-GATE 1 (e), com a precondição de a Idea ter sido criada com sucesso no Passo 5.

### Passo 7: Validação pós-escrita (HG1 e) com rollback

Após o Passo 6, verificar que **todos** os insights em `linked_insights[]` foram atualizados:

- [ ] Cada insight de origem tem `status: promoted` persistido em disco
- [ ] Cada insight de origem tem `idea_ref` apontando para o `id` da Idea criada
- [ ] Cada insight de origem tem `updated_at` atualizado

Se qualquer insight ficou sem atualizar (erro de gravação, permissão, conflito), executar **rollback transacional**:

1. Deletar o arquivo da Idea criado no Passo 5 (`docs/discovery/{topic}/ideas/{NNN}-{slug}.md`)
2. Reverter quaisquer atualizações parciais nos insights que conseguiram persistir (restaurar `status` original, `idea_ref: null`, `updated_at` anterior)
3. Reportar ao humano qual operação falhou e qual o estado restaurado

O objetivo do rollback é manter a invariante: *Idea existe ⇔ todos os seus `linked_insights[]` estão `promoted` com `idea_ref` correto*. Não pode haver Idea órfã nem insight `promoted` sem Idea.

### Passo 8: Validação final integral

Antes de entregar (após Passo 7 ter passado limpo):

- [ ] HARD-GATE 1 (a): `status == approved` em todos os insights de origem (validado em Passo 1)
- [ ] HARD-GATE 1 (b): `linked_insights[]` da Idea tem pelo menos 1 entrada (validado em Passo 4)
- [ ] HARD-GATE 1 (c): Os 5 campos de conteúdo obrigatórios da Idea têm texto substantivo (validado em Passo 4)
- [ ] HARD-GATE 1 (d): `topic` da Idea coincide com o `topic` de TODOS os `linked_insights[]` (validado em Passo 1)
- [ ] HARD-GATE 1 (e): Todos os insights de origem foram atualizados para `status: promoted` com `idea_ref` correto (validado em Passo 7)
- [ ] O `id` da Idea é único dentro do topic
- [ ] O conteúdo respeita `lex-tone` e o idioma confere com `language.default`
- [ ] Nenhum insight teve campo além de `status`, `idea_ref` e `updated_at` modificado

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Idea nova | Markdown com front-matter YAML | `docs/discovery/{topic}/ideas/{NNN}-{slug}.md` |
| Insight(s) atualizado(s) | Markdown com front-matter YAML atualizado (mesmo path original) | `docs/discovery/{topic}/insights/{NNN}-{slug}.md` |
| Resumo da execução | Mensagem ao humano | Sessão atual — confirma a Idea criada, lista os insights promovidos, e flagga campos da Idea que dependem de validação adicional |

## Exemplo de Execução

### Input de Exemplo

```
insight_path:
  - docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md
additional_context: |
  Cliente piloto disponível: escritório Y, com 80 contadores ativos
```

### Output de Exemplo

Arquivo gerado: `docs/discovery/scheduled-payments-research/ideas/001-auto-reconcile-erp-bank.md`

```markdown
---
id: "scheduled-payments-research/ideas/001-auto-reconcile-erp-bank"
topic: "scheduled-payments-research"
problem: "Contadores em escritórios médios gastam em média 4h/semana conciliando manualmente lançamentos divergentes entre o ERP e o extrato bancário, sem percepção de valor agregado pela atividade."
hypothesis: "Se o sistema sugerir conciliação automática com confiança ≥ 90% para divergências de data e duplicação, contadores aceitarão a sugestão em ≥ 70% dos casos, reduzindo o tempo manual em ≥ 60%."
target_user: "Contador operacional em escritórios com 50–500 clientes ativos, integrado ao ERP X"
success_metric: "Tempo médio de conciliação por mês por cliente — baseline 4h (entrevista 2026-05-04) → meta 1.5h em 90 dias após release"
effort_estimate: "M (2–4 sprints; depende de modelo de matching e integração com webhooks do ERP X)"
linked_insights:
  - "scheduled-payments-research/insights/001-manual-reconciliation-bottleneck"
created_at: "2026-05-10T15:00:00Z"
updated_at: "2026-05-10T15:00:00Z"
---

# Idea: Sugestão automática de conciliação ERP × extrato bancário

## Síntese

Contadores em escritórios médios passam horas semanais conciliando manualmente lançamentos divergentes; oferecer sugestão automática para os dois tipos de divergência mais frequentes (data e duplicação) pode reduzir tempo manual em pelo menos 60%, validável com piloto em escritório com base de clientes do ERP X.

## Insights de origem

1. **scheduled-payments-research/insights/001-manual-reconciliation-bottleneck** — 4h/semana de conciliação manual; gargalo declarado por contadores entrevistados; ERP X requer 7 telas para resolver 1 divergência.

## Próximos passos

- Confirmar baseline com mais 3 entrevistas em escritórios diferentes (validar que 4h/semana é mediana, não outlier)
- Coletar amostra de 200 divergências reais para treinar/avaliar modelo de matching
- Mapear webhooks disponíveis no ERP X (lacuna identificada na entrevista, mas não validada com produto do ERP)
```

E o insight de origem atualizado:

```markdown
# (mesmo conteúdo do corpo)
---
status: promoted
idea_ref: "scheduled-payments-research/ideas/001-auto-reconcile-erp-bank"
updated_at: "2026-05-10T15:00:00Z"
# (demais campos inalterados)
---
```

## Restrições

- Nunca alterar `status` de um insight para `approved` — a aprovação é prerrogativa humana per HARD-GATE 2 da `lex-discovery-flow`
- Nunca produzir Idea sem ter validado integralmente as 5 precondições do HARD-GATE 1
- Nunca misturar `topics` distintos em uma única Idea — `topic` da Idea deve coincidir com o `topic` de todos os `linked_insights[]`
- Nunca preencher os 5 campos obrigatórios com placeholders crus como "TBD"; quando faltar evidência, declarar explicitamente que falta evidência (ex: "baseline a confirmar via 3 entrevistas adicionais")
- Nunca alterar campos do insight de origem além de `status`, `idea_ref` e `updated_at`

## Referências

- `lex-discovery-flow` — lei aplicável; HARD-GATE 1 é a precondição central deste Kata
- `codex-discovery-artifacts` — schema completo, máquina de estados, transição `approved → promoted`
- `kata-discovery-synthesis` — Kata complementar (produção de insights upstream)
- `lex-tone`, `codex-tone` — estilo de redação
- `warrior-phanes` — agente que executa este Kata
