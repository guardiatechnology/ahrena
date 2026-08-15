---
name: kata-pov-scope-define
description: "Definir Escopo de PoV. Engenharia — Agents (estágio pré-operacional): delimitação do escopo de um PoV de agent antes de qualquer instrumentação ou implementação"
---

# Kata: Definir Escopo de PoV

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents (estágio pré-operacional): delimitação do escopo de um PoV de agent antes de qualquer instrumentação ou implementação

## Workflow

```
Progresso:
- [ ] 1. Validar inputs e resolver paths (incluindo {agent})
- [ ] 2. Redigir bloco "Problema do cliente"
- [ ] 3. Definir caso de uso primário e o que está fora
- [ ] 4. Declarar persona + stage explícito
- [ ] 5. Definir critério de descontinuação
- [ ] 6. Escrever pov.md e scope.md e validar
```

### Passo 1: Validar inputs e resolver paths

1. Confirma que `--context`, `--agent`, `--problem`, `--value-metric` e `--kind` estão preenchidos. Sem qualquer um deles, aborta com mensagem clara.
2. Resolve `docs/{context}/agents-pov/{agent}/` a partir do `{context}` e `{agent}` informados. Se o diretório já existe e contém `pov.md` ou `scope.md`, alerta o usuário e exige confirmação (`--force`) — sobrescrever PoV existente é decisão consciente.
3. Cria o diretório se inexistente.

### Passo 2: Redigir bloco "Problema do cliente"

1. Cita o problema literal do cliente (do `--problem`), sem reescrever.
2. Adiciona 2-3 frases de contexto de negócio (quem sofre, onde aparece, qual workaround atual). Se o usuário não forneceu, pergunta.
3. Resultado é a primeira seção de `pov.md`.

### Passo 3: Definir caso de uso primário e o que está fora

1. Identifica **1 caso de uso primário** — aquele que, se resolvido, basta para provar valor. Múltiplos casos = escopo amplo demais; reescopo até sobrar 1.
2. Lista o que está **fora** (mínimo de 3 itens). Se `--out-of-scope` foi passado, expande-o; se não, deriva do problema.
3. Sinaliza explicitamente em `pov.md` e em `scope.md` cada caso de uso que **não** é endereçado neste PoV (referências futuras vão para outro PoV ou para Mêtis).

### Passo 4: Declarar persona + stage explícito

1. Define persona do PoV em 1 frase (ex.: "Assistente que sugere lançamentos contábeis para reconciliação automática de extrato bancário").
2. **Declara literalmente `stage: pre-operational` no bloco persona** — pré-condição da DoOC item 9 (`lex-agent-construction-directives`). Sem essa linha, kata aborta.

### Passo 5: Definir critério de descontinuação

1. Default: "Se em 4 semanas o valor medido for < 50% do threshold declarado em `--value-metric`, o PoV é encerrado e o aprendizado é arquivado em `value-proof.md`."
2. Se `--discontinuation-criterion` foi passado, usa o valor do usuário desde que contenha: janela temporal, métrica, threshold.
3. Resultado vira a seção "Critério de descontinuação" de `pov.md` (e referenciada por `scope.md`).

### Passo 6: Escrever pov.md e scope.md e validar

Os dois arquivos são complementares e separados por intenção:

- **`pov.md`** — visão geral consumida por humanos e por `cry-agent-design --from-pov` (Mêtis). Seções: Problema do cliente, Caso de uso primário, Fora de escopo, Persona, Stage, Value metric leading (cópia literal do `--problem` e `--value-metric`), Critério de descontinuação, Próximos passos.
- **`scope.md`** — escopo **estabilizado** consumido pela DoOC item d (codex-agent-design-docs § 14, "Evidence: SHA do commit em `docs/{context}/agents-pov/{agent}/scope.md` + data ≥ 2 semanas atrás"). Seções: Caso de uso primário (cópia literal de `pov.md`), Fora de escopo (cópia literal), Stage (`stage: pre-operational`), Notas de estabilização (data de início do PoV; quem confirma estabilização). Não duplica o problema do cliente nem o value metric — referencia `pov.md`.

Passos concretos:

1. Gera `docs/{context}/agents-pov/{agent}/pov.md` com as 8 seções listadas acima.
2. Gera `docs/{context}/agents-pov/{agent}/scope.md` com as 4 seções listadas acima. A separação física entre `pov.md` e `scope.md` é o que permite a Mêtis calcular o SHA do `scope.md` independentemente do `pov.md` para o item d da DoOC.
3. Próximos passos em `pov.md` sempre listam os 6 katas seguintes a executar: `kata-pov-system-prompt`, `kata-pov-tools-select`, `kata-pov-context-curate`, `kata-pov-observability-instrument`, `kata-pov-feedback-attach`, `kata-pov-value-track`.
4. Aplica `kata-artifact-self-review` aos dois arquivos antes de entregar.

### Validação Final

- [ ] `pov.md` existe em `docs/{context}/agents-pov/{agent}/`
- [ ] `scope.md` existe em `docs/{context}/agents-pov/{agent}/`
- [ ] Ambos contêm literalmente `stage: pre-operational` no bloco persona / stage
- [ ] Caso de uso primário é exatamente 1 e idêntico nos dois arquivos
- [ ] Critério de descontinuação tem janela + métrica + threshold em `pov.md`
- [ ] `scope.md` cita explicitamente a data de início do PoV (insumo da janela de 2 semanas exigida pela DoOC item d)
- [ ] Próximos passos listam os 6 katas POV restantes em `pov.md`

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `pov.md` | Markdown | `docs/{context}/agents-pov/{agent}/pov.md` |
| `scope.md` | Markdown | `docs/{context}/agents-pov/{agent}/scope.md` |

## Exemplo de Execução

### Input

```
cry-pov --context reconciliation \
        --agent rec-pov-classifier \
        --kind skill \
        --problem "Time contábil gasta 3h/dia conciliando extrato bancário com lançamentos do ERP" \
        --value-metric "% de reconciliação automática ≥ 60% em 4 semanas"
```

### Output (extratos)

**`docs/reconciliation/agents-pov/rec-pov-classifier/pov.md`** (extrato):

```markdown
# PoV — reconciliation / rec-pov-classifier

## Problema do cliente

Time contábil gasta 3h/dia conciliando extrato bancário com lançamentos do ERP.
Hoje fazem manualmente em planilha; erros geram lançamentos duplicados.

## Caso de uso primário

Dado um extrato bancário e a lista de lançamentos do ERP da mesma janela,
sugerir o pareamento mais provável por valor + data + descrição similar.

## Fora de escopo

- Criação automática de lançamentos no ERP (apenas sugestão)
- Reconciliação multi-conta cruzada
- Detecção de fraude

## Persona

Assistente que sugere pareamentos extrato↔lançamento contábil.
**stage: pre-operational**

## Value metric leading

% de reconciliação automática ≥ 60% em 4 semanas (medido em sandbox real).

## Critério de descontinuação

Se em 4 semanas o valor medido for < 30% (50% do threshold), o PoV é encerrado;
aprendizado arquivado em value-proof.md.

## Próximos passos

1. kata-pov-system-prompt
2. kata-pov-tools-select
3. kata-pov-context-curate
4. kata-pov-observability-instrument
5. kata-pov-feedback-attach
6. kata-pov-value-track
```

**`docs/reconciliation/agents-pov/rec-pov-classifier/scope.md`** (extrato):

```markdown
# Scope — reconciliation / rec-pov-classifier

> Documento de escopo estabilizado. Consumido pela DoOC item d (codex-agent-design-docs).

## Caso de uso primário

Dado um extrato bancário e a lista de lançamentos do ERP da mesma janela,
sugerir o pareamento mais provável por valor + data + descrição similar.

## Fora de escopo

- Criação automática de lançamentos no ERP (apenas sugestão)
- Reconciliação multi-conta cruzada
- Detecção de fraude

## Stage

stage: pre-operational

## Notas de estabilização

- PoV iniciado em: {data ISO da criação}
- Confirmador da estabilização: {responsável; preenchido por `kata-pov-value-track` quando escopo está parado há ≥ 14 dias}
- Referência cruzada: ver `pov.md` para problema do cliente, value metric e critério de descontinuação.
```

## Restrições

- **Nunca** escopo com mais de 1 caso de uso primário. Se o problema do cliente cobre mais, divida em múltiplos PoVs.
- **Nunca** PoV sem critério de descontinuação — zumbi é risco declarado em plan-031.
- **Nunca** persona sem `stage: pre-operational` declarado — bloqueia DoOC item 9.
- **Nunca** produzir somente `pov.md` sem `scope.md` (ou vice-versa); os dois são contrato com a DoOC.
- O kata **não** delega para Hephaestus ou Apollo; é trabalho 100% de escopo, anterior à implementação.

---

**Modelo:** Este Kata aplica a Diretriz 05 (`lex-agent-construction-directives`) ao ciclo PoV. Foco em estreito + critério de saída evita zumbis. O par `pov.md` + `scope.md` é o contrato canônico declarado em `codex-agent-design-docs` § 14. Consumido por `warrior-claudionor` como primeiro passo de `cry-pov`.
