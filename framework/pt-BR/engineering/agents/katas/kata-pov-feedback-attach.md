# Kata: Anexar Loop de Feedback ao PoV

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents (estágio pré-operacional): definição de HITL leve OU 1 métrica objetiva como loop de feedback do PoV

## Objetivo

Produzir `docs/{context}/agents-pov/feedback.md` declarando o loop de feedback do PoV: **HITL leve** (humano aprova outputs críticos) **OU** **1 métrica objetiva** do ambiente (ex.: "query retorna resultado válido?"). Critic agent é opcional. Aplica Diretriz 04 de `lex-agent-construction-directives` (Loop de Feedback Explícito) no rigor mínimo viável: PoV não precisa do loop completo de produção, mas precisa de **alguma sinalização objetiva** se está acertando.

## Quando Usar

- Após `kata-pov-tools-select` e `kata-pov-observability-instrument` (value-metrics referenciadas)
- Quando o tier do PoV é definido (default: tier-3/4)
- Quando uma rodada de operação revela que o feedback declarado não está sendo coletado (re-execução)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `docs/{context}/agents-pov/overview.md` | Sim | Caso de uso primário e value metric |
| `docs/{context}/agents-pov/observability/value-metrics.md` | Sim | Métrica primária |
| `--tier <1\|2\|3\|4>` | Não | Default 3. Tier-1/2 exige loop mais rígido |

## Workflow

```
Progresso:
- [ ] 1. Decidir entre HITL leve ou métrica objetiva (ou ambos)
- [ ] 2. Especificar mecanismo escolhido
- [ ] 3. Definir cadência de coleta
- [ ] 4. Declarar pivot trigger (quando o feedback muda o PoV)
- [ ] 5. Persistir feedback.md
```

### Passo 1: Decidir entre HITL leve ou métrica objetiva

Critério de escolha:

| Cenário | Mecanismo |
|---|---|
| Output é decisão consequente (escreve em sistema externo, envia comunicação) | HITL leve obrigatório |
| Output é sugestão consultiva (humano valida antes de aplicar) | Métrica objetiva basta |
| Tier-1/2 declarado | HITL leve + métrica objetiva (ambos) |
| Tier-3/4 (default PoV) | Pelo menos 1 dos dois |

Se o caso de uso primário envolve **decisão consequente**, o kata força HITL leve mesmo em tier-3/4.

### Passo 2: Especificar mecanismo escolhido

**HITL leve:**

- Onde o humano aprova: UI do PoV (botão "aprovar/rejeitar"), comentário em PR, ou canal dedicado (Slack thread)
- O que é capturado: input do agent, output do agent, decisão humana (aprovar/rejeitar/editar), motivo (texto livre opcional)
- Latência aceitável: ≤ 24h por default

**Métrica objetiva:**

- Sinal binário do ambiente que indica acerto/erro (ex.: "lançamento sugerido foi efetivado no ERP em 7 dias")
- Como capturar: webhook, polling de DB, log de ação humana
- Janela de atribuição: declarada (default 7 dias)

### Passo 3: Definir cadência de coleta

- HITL leve: agregação diária + revisão semanal
- Métrica objetiva: agregação contínua + leitura semanal em `value-proof.md`
- Resultado da agregação é input para `kata-pov-value-track`

### Passo 4: Declarar pivot trigger

Condição declarada que, se atingida, força revisão do PoV (re-execução de `kata-pov-scope-define`):

- Default: "Aprovação humana < 50% por 2 semanas consecutivas" (HITL leve)
- Default: "Métrica objetiva < 30% do threshold por 2 semanas consecutivas"

Pivot trigger é **diferente** de critério de descontinuação (`overview.md::Critério de descontinuação`): pivot pede revisão; descontinuação encerra.

### Passo 5: Persistir feedback.md

Grava `docs/{context}/agents-pov/feedback.md` com seções: Mecanismo escolhido, Especificação técnica, Cadência, Pivot trigger, Referência cruzada para `observability/value-metrics.md`.

### Validação Final

- [ ] Pelo menos 1 mecanismo declarado (HITL leve OU métrica objetiva)
- [ ] Se tier-1/2: ambos declarados
- [ ] Pivot trigger tem condição quantificada (janela + threshold)
- [ ] Cadência declarada explicitamente
- [ ] Cross-link para `value-metrics.md` ativo

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `feedback.md` | Markdown | `docs/{context}/agents-pov/feedback.md` |

## Exemplo de Execução

### Input (overview.md, extrato)

```
Caso de uso: sugerir pareamento extrato↔lançamento. Sugestão consultiva (humano confirma antes de gravar).
Tier: 3 (default PoV).
```

### Output (feedback.md, extrato)

```markdown
## Mecanismo

Métrica objetiva (PoV é consultivo, tier-3).

## Especificação técnica

- Sinal: "operador aprovou ou ajustou a sugestão dentro de 7 dias?"
- Captura: log do botão "Aplicar sugestão" no front do PoV
- Janela: 7 dias por sugestão

## Cadência

- Agregação contínua em observability/value-metrics.md::reconciliation_auto_rate
- Revisão semanal em value-proof.md

## Pivot trigger

reconciliation_auto_rate < 30% por 2 semanas consecutivas → reescopo via kata-pov-scope-define.
```

## Restrições

- **Nunca** PoV sem feedback declarado. Sem feedback, value-proof vira documento de fachada.
- **Nunca** HITL latente (> 7 dias para captura humana) — invalida o ciclo curto que justifica PoV.
- **Nunca** pivot trigger qualitativo ("se ficar ruim"). Sempre janela + threshold.

---

**Modelo:** Este Kata aplica a Diretriz 04 (`lex-agent-construction-directives`) no rigor pré-operacional. Critic agent é opcional — fica para Mêtis quando agent for promovido.
