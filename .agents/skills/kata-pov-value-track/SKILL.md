---
name: kata-pov-value-track
description: "Rastrear Valor do PoV (value-proof.md). Engenharia — Agents (estágio pré-operacional): coleta estruturada de dados durante a operação do PoV para sustentar decisão go/no-go de promoção a operational-concrete"
---

# Kata: Rastrear Valor do PoV (value-proof.md)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents (estágio pré-operacional): coleta estruturada de dados durante a operação do PoV para sustentar decisão go/no-go de promoção a `operational-concrete`

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
- critério de descontinuação: {literal de pov.md}
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

- status: active | pivoting | closed | ready_for_dooc
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

1. **Critério de descontinuação** (de `pov.md`): se atingido, status → `closed`.
2. **Pivot trigger** (de `feedback.md`): se atingido, status → `pivoting` e recomenda re-execução de `kata-pov-scope-define`.
3. **Sucesso continuado** (métrica ≥ threshold por ≥ 7 dias e escopo estabilizado por 2 semanas): status pode avançar para `ready_for_dooc` — Mêtis pode rodar `cry-agent-design --from-pov`.

#### Pré-condição obrigatória — Boundary PII antes de `ready_for_dooc`

Antes de transicionar status para `ready_for_dooc` (e portanto antes de habilitar o handoff `cry-agent-design --from-pov` para Mêtis), o kata **DEVE** executar uma verificação de fronteira de PII sobre o diretório `docs/{context}/agents-pov/{agent}/`:

1. Para cada arquivo `.md` (e arquivos sob `observability/`) do PoV, grep contra os padrões declarados em `lex-data-retention` (CPF, CNPJ, email, telefone, conta bancária, token, secret, etc.).
2. Se houver **qualquer** ocorrência, o kata **REJEITA** a transição e retorna ao usuário com a lista de arquivos e linhas atingidas, recomendando re-execução de `kata-pov-context-curate` para reanonimização (`pov.md::Notas de anonimização`).
3. Apenas quando o grep retorna zero ocorrências o status pode ser flipado para `ready_for_dooc`.

Justificativa: o documento `pov.md` (e o context-pack) é entregue como input direto ao `warrior-mêtis` via `--from-pov` no ciclo `operational-concrete`. PII vazada no pacote PoV se propagaria para o design de produção sem nova revisão. O gate é executado neste kata porque ele é o único ponto em que a transição para o handoff é decidida.

### Passo 5: Atualizar status do PoV

Atualiza o bloco "Decisão atual" com:

- status (vocabulário fechado: `active`, `pivoting`, `closed`, `ready_for_dooc`)
- timestamp
- próximo ciclo agendado (cadência: semanal para tier-1/2, quinzenal para tier-3/4)

### Passo 6: Persistir o documento

1. Grava `docs/{context}/agents-pov/{agent}/value-proof.md` com o ciclo atual adicionado.
2. Registra o commit no histórico do PoV (responsável + cycle number).
3. Se status = `ready_for_dooc`, emite log dizendo "Pronto para Mêtis consumir via `cry-agent-design --from-pov docs/{context}/agents-pov/{agent}/`".

### Validação Final

- [ ] Todos os campos obrigatórios do schema presentes
- [ ] Pelo menos 1 ciclo registrado (na execução inicial é o ciclo zero — bootstrap)
- [ ] SHA da telemetria presente em cada ciclo (rastreabilidade)
- [ ] Sem PII
- [ ] Status atual coerente com leitura da métrica

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `value-proof.md` | Markdown (vivo) | `docs/{context}/agents-pov/{agent}/value-proof.md` |

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
