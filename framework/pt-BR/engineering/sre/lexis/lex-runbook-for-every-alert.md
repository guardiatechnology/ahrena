# Lexis: Todo Alerta tem Runbook

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Alertas de monitoramento que acionam humanos (page, Slack on-call) — cada um precisa de runbook ligado

## Propósito

Alertas sem runbook são crueldade operacional: acordam engenheiros às 3h da manhã sem indicação do que fazer. O on-call gasta tempo descobrindo o que o alerta significa, onde ver dashboards, quais passos de mitigação aplicar — tempo em que o incidente se agrava. Pior: alertas recorrentes sem runbook normalizam "ignorar alerta até dar mesmo pau", destruindo o valor do sistema de monitoramento.

Esta Lexis existe para garantir que **todo alerta que aciona um humano tenha runbook versionado e linkado**, que **runbooks tenham passos acionáveis**, e que **alertas sem runbook sejam silenciados ou removidos até terem um**.

## Lei

> **Todo alerta que aciona um humano (page, on-call) DEVE ter runbook versionado em `docs/runbooks/{service}-{alert-name}.md`, linkado diretamente no annotation do alerta. O runbook DEVE conter: sintomas, impacto no usuário, diagnóstico inicial (dashboards e queries), ações de mitigação, passos de escalação. Alertas sem runbook DEVEM ser silenciados ou removidos.**

## Regras

### 1. Estrutura mínima do runbook

```markdown
# Runbook: {service} — {alert-name}

- **Severity:** P1 | P2 | P3
- **Owner:** team-{name} (on-call: @handle)
- **Last reviewed:** YYYY-MM-DD

## Sintomas (o que o alerta indica)

{descrição objetiva: métrica, threshold, duração}

## Impacto no usuário

{quem sente o problema, o que não consegue fazer}

## Diagnóstico

1. Dashboard: {link}
2. Logs: `{query or link to log aggregator}`
3. Traces: {link to APM/tracing para serviço}
4. Hipóteses comuns em ordem de prevalência:
   - Hipótese A: causa → sinal típico
   - Hipótese B: causa → sinal típico

## Mitigação

### Mitigação rápida (rollback, feature flag)
1. Passo 1
2. Passo 2

### Mitigação profunda (fix real)
1. Identificar causa raiz
2. Fixar e deploy
3. Verificar recovery nos dashboards

## Escalação

Se mitigação não resolve em 15 min:
- Acionar @team-escalation-list
- Abrir incident sev-X conforme `codex-incident-response`

## Histórico (últimos 3 incidentes relacionados)

- {link 1}
- {link 2}
- {link 3}
```

### 2. Link obrigatório no alert config

Todo alert config (Prometheus, CloudWatch, Datadog) **DEVE** ter annotation:

```yaml
annotations:
  runbook_url: "https://github.com/guardiafinance/{repo}/blob/main/docs/runbooks/refund-api-p99-breach.md"
  summary: "refund-api p99 > 300ms for 5 min"
```

### 3. Runbook revisado trimestralmente

Cada runbook tem `Last reviewed: YYYY-MM-DD`:
- Se > 6 meses sem revisar → warning no CI/dashboard.
- Revisão mínima: confirmar links ainda funcionam, hipóteses ainda relevantes, donos corretos.
- Incidente relacionado → runbook **DEVE** ser atualizado no post-mortem.

### 4. Alert sem runbook = silenciar ou remover

Novo alert criado sem runbook pareado:
- Bloqueado no PR do alert config (lint rule).
- Alerts existentes sem runbook: listados mensalmente em report; fix em 30 dias ou silenciar.

Silenciar não é solução permanente. Silenciado por >60 dias → remover.

### 5. Sem alertas que ninguém entende

Regra de ouro: **on-call deve conseguir agir com o runbook mesmo sem ter familiaridade profunda com o serviço**. Runbook escrito para "você daqui 6 meses" ou "o novo on-call".

Se o runbook requer conhecimento tribal exclusivo, está incompleto.

## Abrangência

- **Aplica-se a:** todo alert que page/notifica humano em qualquer canal (PagerDuty, Opsgenie, Slack on-call).
- **Agentes vinculados:** `warrior-hestia` (ownership), `warrior-atlas` (quando configura alarmes via IaC).
- **Exceções:** alerts informacionais (dashboard only, sem notification ativa) ficam fora do escopo — mas recomendado ter documentação mesmo assim.

## Consequências de Violação

1. **Tempo de resolução infla:** on-call gasta 30min descobrindo o que alerta significa antes de agir.
2. **Alert fatigue:** alertas recorrentes sem runbook viram ruído; real emergency perde urgência.
3. **Falha de compliance:** auditoria SOC 2 CC7.3 exige procedimentos de incident response; sem runbook, falha.
4. **Remediação:**
   - Inventário de alerts existentes; cada um recebe ticket de runbook em 30 dias.
   - Alerts críticos (P1) sem runbook: silenciar até documentar.
   - CI lint bloqueia merge de alert config sem `runbook_url`.

## Validação Automatizada

- **Ferramenta:**
  - Lint em arquivos de alert config (Prometheus rules, Terraform CloudWatch): require `annotations.runbook_url`.
  - Cronjob verifica que URL no `runbook_url` existe (não 404).
  - Dashboard: alerts ativos vs. runbooks existentes → gap report.
- **Momento:** em cada PR que adiciona/modifica alert; semanalmente (URL health).
- **Métrica:** 100% de alerts ativos com `runbook_url` válido; 0 alerts silenciados há > 60 dias sem deleção.

## Referências

- `lex-slo-required` — burn-rate alerts derivados de SLO precisam de runbook igual
- `lex-observability-required`
- `codex-incident-response` — procedimentos maiores; runbook é o passo inicial
- `warrior-hestia`
- [Google SRE Book — Effective Alerting](https://sre.google/sre-book/monitoring-distributed-systems/)
