# Lexis: SLO Obrigatório para Serviços tier-1/2

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Service Level Objectives (SLO) para serviços tier-1 e tier-2 — definidos antes do go-live, medidos em produção, respeitados como contrato interno

## Propósito

Sem SLO, "disponibilidade" e "performance" são opinião. Clientes reclamam quando algo está ruim; engenharia debate o que "suficientemente bom" significa; priorização de confiabilidade vs. features vira política. SLO torna a discussão objetiva: contratos numéricos com clientes (internos ou externos) sobre o que é aceitável, error budget consumido como moeda para decisões.

Esta Lexis existe para garantir que **todo serviço tier-1 ou tier-2 tenha SLO explícito antes do primeiro deploy em produção**, que **SLO seja medido por SLI observáveis** e que **error budget consumido paute priorização entre confiabilidade e entrega de features**.

## Lei

> **Todo serviço tier-1 ou tier-2 DEVE ter SLO declarado e acordado antes do primeiro deploy em produção. SLO DEVE ser medido por SLI baseado em telemetria real (métricas, logs). Quando o error budget do período é consumido ≥ 80%, novas features DEVEM ser pausadas em favor de trabalho de confiabilidade até budget ser recuperado.**

## Regras

### 1. SLO declarado antes do go-live

Cada serviço novo de criticidade tier-1 ou tier-2 tem, no repositório:

```yaml
# docs/slo/{service}.yaml
service: refund-api
tier: 1
slos:
  - name: availability
    sli: "successful_http_requests / total_http_requests (excluding 4xx validation errors)"
    objective: 99.9%
    window: 30d
    error_budget_policy: "pause features if ≥80% consumed"
  - name: latency_p99
    sli: "http_request_duration_seconds{quantile=0.99} p99 in production"
    objective: 300ms
    window: 30d
  - name: freshness (for async processors)
    sli: "event_processing_lag_seconds"
    objective: "< 60s at p95"
    window: 7d
owners:
  - team: platform-payments
    escalation: "@payments-oncall"
```

### 2. SLI baseado em telemetria real

O SLI **DEVE**:
- Ser mensurável em produção via métrica existente ou criada para isso.
- Refletir experiência do usuário (usuários reclamam de 5xx e latência, não de CPU interno).
- Excluir causas não relacionadas ao serviço (ex.: 401 por credencial do cliente não conta contra disponibilidade).

### 3. Error budget como moeda

Para cada SLO:

- **Error budget** = 1 - SLO × window. Ex.: 99.9% em 30d → 43.2 minutos de downtime permitidos.
- **Consumido em tempo real** via dashboard dedicado.
- **≥ 80% consumido** → pausar novas features para esse serviço; priorizar confiabilidade (testes caóticos, reforço de retry, fix de bugs recorrentes).
- **100% consumido** = SLO violado no período → post-mortem obrigatório; pode acionar rollback de features recentes.

### 4. Revisão trimestral

SLO não é esculpido em pedra:

- **Revisar trimestralmente** com stakeholders (produto, engenharia, eventualmente cliente).
- Se SLO crônico (budget consumido > 3 períodos seguidos) → relaxar SLO ou investir em reliability estrutural.
- Se budget zerado cronicamente (nunca consome) → apertar SLO (cliente merece mais).

### 5. Tiers

| Tier | Critério | SLO típico | Error budget |
|---|---|---|---|
| 1 | Receita direta, segurança crítica (pagamento, auth) | 99.9%+ | 43min/mês |
| 2 | Importante (dashboards operacionais, integrações externas) | 99.5% | 3.6h/mês |
| 3 | Business-hours (BFF interno, admin tools) | 99% | 7h/mês |
| 4 | Interno best-effort (experimental, interno pequeno) | opcional | — |

### 6. Dashboards e alertas derivados

Do SLO deriva:

- **Dashboard de SLO**: gráfico de error budget ao longo do período; forecast de esgotamento.
- **Alertas burn-rate**: disparar quando budget consome mais rápido que linear (ex.: 2% do mês em 1h = burn rate 14x → page on-call).
- **Alertas de violação iminente**: 80% budget → warning; 100% → post-mortem.

## Abrangência

- **Aplica-se a:** todo serviço novo tier-1 ou tier-2; serviços existentes sem SLO têm até 90 dias para declarar após esta Lexis entrar em vigor.
- **Agentes vinculados:** `warrior-hestia`, `warrior-atlas` (quando infra nova), `warrior-athena` (enforce pré-deploy).
- **Exceções:** serviços tier-3 e tier-4 ficam com SLO opcional; experimentais (sandbox, prototype) ficam fora do enforce.

## Consequências de Violação

1. **Sem SLO:** discussão de priorização vira política; confiabilidade perde para novidade até quebrar em cliente.
2. **SLO fictício:** número atraente mas sem medição real; auditoria externa (SOC 2, ISO) detecta gap.
3. **Budget estourado ignorado:** equipe continua entregando features enquanto reliability degrada; cliente churn cresce silenciosamente.
4. **Remediação:**
   - Declarar SLO em `docs/slo/{service}.yaml` com revisão em squad.
   - Configurar dashboards (Grafana, Datadog SLO, CloudWatch).
   - Instituir cerimônia trimestral de review.

## Validação Automatizada

- **Ferramenta:** scanner simples de `docs/slo/*.yaml` vs. lista de serviços declarados (pode ser em `infra/` ou registry); alert se serviço tier-1/2 não tem SLO.
- **Momento:** pre-deploy (go-live checklist); trimestral (review).
- **Métrica:** 100% de serviços tier-1/2 com SLO documentado; 0 serviços tier-1 com error budget cronicamente zerado (>3 períodos).

## Referências

- `lex-runbook-for-every-alert` — alertas ligam a runbooks
- `lex-observability-required` — SLI vem da telemetria
- `codex-incident-response`
- `warrior-hestia`
- [Google SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/)
