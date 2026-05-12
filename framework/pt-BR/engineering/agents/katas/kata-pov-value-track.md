# Kata: Rastrear Valor do PoV (value-proof.md)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents (estágio pré-operacional): coleta estruturada de dados durante a operação do PoV para sustentar decisão go/no-go de promoção a `operational-concrete`

## Objetivo

Produzir e manter `docs/{context}/agents-pov/value-proof.md` — documento **vivo** durante toda a operação do PoV. Define o schema canônico (campos obrigatórios + SHA da telemetria), critério go/no-go para promoção (insumo direto da DoOC), e cadência de revisão (`tier-1/2 semanal`; `tier-3/4 quinzenal`). Sem `value-proof.md` consistente, Mêtis não consegue rodar `kata-dooc-validate` itens 2 (leading provada) e 5 (observability ≥ 7 dias).

## Quando Usar

- Imediatamente após `kata-pov-feedback-attach` (template inicial)
- Em cada ciclo de revisão (semanal ou quinzenal, conforme tier) — atualização
- Quando o pivot trigger de `feedback.md` é atingido
- Antes de `cry-agent-design --from-pov` ser invocado por Mêtis

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `docs/{context}/agents-pov/overview.md` | Sim | Value metric leading + critério de descontinuação |
| `docs/{context}/agents-pov/observability/value-metrics.md` | Sim | Definições e thresholds |
| `docs/{context}/agents-pov/feedback.md` | Sim | Mecanismo de captura + pivot trigger |
| `--tier <1\|2\|3\|4>` | Não | Default 3. Determina cadência |
| `--cycle <N>` | Não | Número da rodada de revisão (1, 2, 3...) |

## Workflow

```
Progresso:
- [ ] 1. Inicializar value-proof.md com schema canônico (primeira execução)
- [ ] 2. A cada ciclo, registrar leitura da métrica primária com SHA da telemetria
- [ ] 3. Registrar observações qualitativas do ciclo
- [ ] 4. Avaliar critério de descontinuação e pivot trigger
- [ ] 5. Atualizar status do PoV (continuar / pivotar / descontinuar / promover)
- [ ] 6. Persistir o documento atualizado
```

### Passo 1: Inicializar value-proof.md (primeira execução)

Schema canônico (campos obrigatórios):

```markdown
# value-proof.md — PoV {context}

> Cadência: {semanal | quinzenal} (tier-{N})
> Stage: pre-operational

## Identificação

- context: {context}
- iniciado em: {ISO date}
- responsável: {pessoa / time}
- métrica primária: {nome} (referência: observability/value-metrics.md)
- threshold leading: {valor + janela}
- critério de descontinuação: {literal de overview.md}
- pivot trigger: {literal de feedback.md}

## Registro de ciclos

(seção viva — uma entrada por ciclo)

### Ciclo 1 — {ISO date}

- período observado: {start} → {end}
- valor da métrica primária: {número}
- SHA da telemetria de origem: {hash do snapshot de observability}
- observações qualitativas: {texto livre, 3-5 frases}
- decisão do ciclo: continuar | pivotar | descontinuar | promover
- justificativa: {texto livre}

## Decisão atual

- status: ativo | pivotando | encerrado | pronto-para-DoOC
- atualizado em: {ISO date}
- próximo ciclo agendado: {ISO date}
```

### Passo 2: Registrar leitura da métrica com SHA

A cada execução do kata em um ciclo:

1. Lê snapshot da telemetria (export de `observability/value-metrics.md` agregado).
2. Calcula SHA256 do snapshot (rastreabilidade — Risco 5 de plan-031 mitiga "value-proof de fachada").
3. Anexa ao registro do ciclo: valor da métrica + SHA + período observado.

### Passo 3: Registrar observações qualitativas

3-5 frases curtas por ciclo:

- O que funcionou (caso concreto, sem inventar)
- O que falhou (anti-padrão observado, link para context-pack se aplicável)
- Surpresas (caso fora do esperado)

Sem PII. Se um caso depende de detalhe sensível, anonimiza ou cita por ID opaco.

### Passo 4: Avaliar critério de descontinuação e pivot trigger

1. **Critério de descontinuação** (de `overview.md`): se atingido, status → `encerrado`.
2. **Pivot trigger** (de `feedback.md`): se atingido, status → `pivotando` e recomenda re-execução de `kata-pov-scope-define`.
3. **Sucesso continuado** (métrica ≥ threshold por ≥ 7 dias e escopo estabilizado por 2 semanas): status pode avançar para `pronto-para-DoOC` — Mêtis pode rodar `cry-agent-design --from-pov`.

### Passo 5: Atualizar status do PoV

Atualiza o bloco "Decisão atual" com:

- status (vocabulário fechado: `ativo`, `pivotando`, `encerrado`, `pronto-para-DoOC`)
- timestamp
- próximo ciclo agendado (cadência: semanal para tier-1/2, quinzenal para tier-3/4)

### Passo 6: Persistir o documento

1. Grava `docs/{context}/agents-pov/value-proof.md` com o ciclo atual adicionado.
2. Registra o commit no histórico do PoV (responsável + cycle number).
3. Se status = `pronto-para-DoOC`, emite log dizendo "Pronto para Mêtis consumir via `cry-agent-design --from-pov docs/{context}/agents-pov/`".

### Validação Final

- [ ] Todos os campos obrigatórios do schema presentes
- [ ] Pelo menos 1 ciclo registrado (na execução inicial é o ciclo zero — bootstrap)
- [ ] SHA da telemetria presente em cada ciclo (rastreabilidade)
- [ ] Sem PII
- [ ] Status atual coerente com leitura da métrica

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `value-proof.md` | Markdown (vivo) | `docs/{context}/agents-pov/value-proof.md` |

## Cadência (referência rápida)

| Tier do PoV | Cadência de revisão | Crítico para |
|---|---|---|
| 1, 2 | Semanal | PoV impacta receita ou compliance |
| 3, 4 (default) | Quinzenal | PoV consultivo / interno |

## Restrições

- **Nunca** valor de métrica sem SHA da telemetria — value-proof sem evidência é fachada.
- **Nunca** ciclo sem decisão explícita (`continuar | pivotar | descontinuar | promover`).
- **Nunca** PII em observações.
- **Nunca** status fora do vocabulário fechado.
- **Sempre** o documento é vivo: cada ciclo **adiciona** entrada; histórico é preservado.

---

**Modelo:** Este Kata é o insumo direto da DoOC (`lex-agent-construction-directives`). O schema é o contrato consumido por `kata-dooc-validate` (plan-032).
