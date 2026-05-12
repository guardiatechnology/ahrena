# Kata: Definir Escopo de PoV

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents (estágio pré-operacional): delimitação do escopo de um PoV de agent antes de qualquer instrumentação ou implementação

## Objetivo

Produzir `docs/{context}/agents-pov/overview.md` com escopo **muito estreito** (1 caso de uso primário), critério explícito de descontinuação ("se em N semanas a métrica de valor não atingir X, encerra") e declaração explícita de `stage: pre-operational`. Aplica a Diretriz 05 de `lex-agent-construction-directives` (Escopo Restrito) na ótica de PoV: domínio estreito + feedback rápido = curva de aprendizado íngreme. Sem esse arquivo, nenhum outro kata do ciclo PoV pode rodar.

## Quando Usar

- Quando `cry-pov --context <name> --kind <skill|subagent|plugin> --problem <description> --value-metric <description>` é invocado
- Quando `warrior-claudionor` precisa formalizar escopo antes de delegar implementação
- Quando um PoV existente perdeu foco e exige reescopo (re-execução do kata)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `--context <name>` | Sim | Bounded context em kebab-case (ex.: `reconciliation`, `fiscal-classification`) |
| `--problem <description>` | Sim | Problema do cliente em 1 frase. Sem genericidades ("automatizar coisas") |
| `--value-metric <description>` | Sim | Métrica leading que se quer mover, com janela e threshold |
| `--kind <skill\|subagent\|plugin>` | Sim | Qual artefato Anthropic será spawnado |
| `--out-of-scope` | Não | Lista explícita do que está fora; se ausente, é derivada do problema |
| `--discontinuation-criterion` | Não | Sobrescreve o default (4 semanas, valor < 50% da meta declarada) |

## Workflow

```
Progresso:
- [ ] 1. Validar inputs e resolver paths
- [ ] 2. Redigir bloco "Problema do cliente"
- [ ] 3. Definir caso de uso primário e o que está fora
- [ ] 4. Declarar persona + stage explícito
- [ ] 5. Definir critério de descontinuação
- [ ] 6. Escrever overview.md e validar
```

### Passo 1: Validar inputs e resolver paths

1. Confirma que `--context`, `--problem`, `--value-metric` e `--kind` estão preenchidos. Sem qualquer um deles, aborta com mensagem clara.
2. Resolve `docs/{context}/agents-pov/` a partir do `{context}` informado. Se o diretório já existe e contém `overview.md`, alerta o usuário e exige confirmação (`--force`) — sobrescrever PoV existente é decisão consciente.
3. Cria o diretório se inexistente.

### Passo 2: Redigir bloco "Problema do cliente"

1. Cita o problema literal do cliente (do `--problem`), sem reescrever.
2. Adiciona 2-3 frases de contexto de negócio (quem sofre, onde aparece, qual workaround atual). Se o usuário não forneceu, pergunta.
3. Resultado é a primeira seção de `overview.md`.

### Passo 3: Definir caso de uso primário e o que está fora

1. Identifica **1 caso de uso primário** — aquele que, se resolvido, basta para provar valor. Múltiplos casos = escopo amplo demais; reescopo até sobrar 1.
2. Lista o que está **fora** (mínimo de 3 itens). Se `--out-of-scope` foi passado, expande-o; se não, deriva do problema.
3. Sinaliza explicitamente em `overview.md` cada caso de uso que **não** é endereçado neste PoV (referências futuras vão para outro PoV ou para Mêtis).

### Passo 4: Declarar persona + stage explícito

1. Define persona do PoV em 1 frase (ex.: "Assistente que sugere lançamentos contábeis para reconciliação automática de extrato bancário").
2. **Declara literalmente `stage: pre-operational` no bloco persona** — pré-condição da DoOC item 9 (`lex-agent-construction-directives`). Sem essa linha, kata aborta.

### Passo 5: Definir critério de descontinuação

1. Default: "Se em 4 semanas o valor medido for < 50% do threshold declarado em `--value-metric`, o PoV é encerrado e o aprendizado é arquivado em `value-proof.md`."
2. Se `--discontinuation-criterion` foi passado, usa o valor do usuário desde que contenha: janela temporal, métrica, threshold.
3. Resultado vira a seção "Critério de descontinuação" de `overview.md`.

### Passo 6: Escrever overview.md e validar

1. Gera `docs/{context}/agents-pov/overview.md` com seções: Problema do cliente, Caso de uso primário, Fora de escopo, Persona, Stage, Value metric leading (cópia literal do `--problem` e `--value-metric`), Critério de descontinuação, Próximos passos.
2. Próximos passos sempre listam os 6 katas seguintes a executar: `kata-pov-system-prompt`, `kata-pov-tools-select`, `kata-pov-context-curate`, `kata-pov-observability-instrument`, `kata-pov-feedback-attach`, `kata-pov-value-track`.
3. Aplica `kata-artifact-self-review` ao arquivo gerado antes de entregar.

### Validação Final

- [ ] `overview.md` existe em `docs/{context}/agents-pov/`
- [ ] Contém literalmente `stage: pre-operational` no bloco persona
- [ ] Caso de uso primário é exatamente 1
- [ ] Critério de descontinuação tem janela + métrica + threshold
- [ ] Próximos passos listam os 6 katas POV restantes

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `overview.md` | Markdown | `docs/{context}/agents-pov/overview.md` |

## Exemplo de Execução

### Input

```
cry-pov --context reconciliation \
        --kind skill \
        --problem "Time contábil gasta 3h/dia conciliando extrato bancário com lançamentos do ERP" \
        --value-metric "% de reconciliação automática ≥ 60% em 4 semanas"
```

### Output (extrato)

```markdown
# PoV — reconciliation

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

## Restrições

- **Nunca** escopo com mais de 1 caso de uso primário. Se o problema do cliente cobre mais, divida em múltiplos PoVs.
- **Nunca** PoV sem critério de descontinuação — zumbi é risco declarado em plan-031.
- **Nunca** persona sem `stage: pre-operational` declarado — bloqueia DoOC item 9.
- O kata **não** delega para Hephaestus ou Apollo; é trabalho 100% de escopo, anterior à implementação.

---

**Modelo:** Este Kata aplica a Diretriz 05 (`lex-agent-construction-directives`) ao ciclo PoV. Foco em estreito + crítério de saída evita zumbis. Consumido por `warrior-claudionor` como primeiro passo de `cry-pov`.
