# Kata: Triagem de Incidente

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Procedimento dos primeiros 15 minutos de um incidente — declarar severity, acionar papéis, orquestrar diagnóstico inicial, decidir mitigação

## Objetivo

Ao receber um alerta (ou report humano) de incidente em produção, executar procedimento estruturado de triagem nos primeiros 15 minutos: acknowledge do alerta, declaração de severity, abertura de war room, acionamento de papéis, diagnóstico inicial via runbook, e decisão entre mitigação rápida (rollback/feature flag) ou investigação aprofundada. Produz linha do tempo inicial e comunicação estruturada.

## Quando Usar

- Resposta a alerta sev-1 ou sev-2 disparando para on-call
- Report humano de degradação significativa em produção
- Incidente de segurança detectado (credencial vazada, intrusão suspeita)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Sinal inicial | Sim | Alerta (PagerDuty ticket), message Slack, report humano |
| Serviço afetado | Sim | Nome do serviço (para achar runbook e owner) |
| Canal de comunicação | Sim | Slack ou equivalente para war room |

## Workflow

```
Progresso:
- [ ] 1. Acknowledge em <5 min
- [ ] 2. Declarar severity
- [ ] 3. Abrir war room + acionar papéis
- [ ] 4. Consultar runbook do alerta
- [ ] 5. Diagnóstico inicial via dashboards/logs
- [ ] 6. Decidir mitigação vs. debug
- [ ] 7. Aplicar mitigação (se decidida) e verificar recovery
- [ ] 8. Comunicar status (interno + externo se aplicável)
- [ ] 9. Entregar linha do tempo inicial ao IC
```

### Passo 1: Acknowledge em <5 min

1. Abrir o alerta no sistema de paging (PagerDuty etc.), acknowledgeamento formal.
2. Registrar timestamp t+0 (quando alerta disparou).
3. Se on-call está em outra task: pausar, escalar para backup se necessário.

### Passo 2: Declarar severity

Consultar `codex-incident-response` §Severidade:

- SEV-1: produção tier-1 down OU dados corrompidos OU >30% usuários
- SEV-2: degradação significativa tier-1/2 OU >5% usuários
- SEV-3: parcial; workaround existe
- SEV-4: isolado; sem impacto imediato

Declarar severity no canal de incident (Slack) explicitamente:

```
🚨 SEV-2 declarada
Serviço: refund-api
Sintoma: p99 > 500ms sustained 5min, error rate 2%
```

### Passo 3: Abrir war room + acionar papéis

**SEV-1:**
- Criar Zoom/Meet dedicado (se configurado, link automático do sistema de incidente).
- Criar canal Slack `#inc-YYYY-MM-DD-{service}-{short-desc}`.
- Acionar: IC (incident commander), Technical Lead, Comms Lead, Scribe.

**SEV-2:**
- Canal Slack suficiente; war room em call opcional.
- Acionar: IC + Technical Lead (on-call pode acumular).

**SEV-3:**
- Canal Slack; on-call acumula todos os papéis.

Se on-call é o **Hestia-spawn** (agente IA): papel de Scribe/Comms é ideal (mantém timeline estruturado); decisões ficam com humano.

### Passo 4: Consultar runbook do alerta

1. Abrir `runbook_url` do alerta (ver `lex-runbook-for-every-alert`).
2. Ler Sintomas, Impacto, Diagnóstico.
3. Compartilhar link no canal:
   ```
   📘 Runbook: {url}
   ```

### Passo 5: Diagnóstico inicial

Conforme runbook:

1. **Dashboards**: abrir os links; capturar screenshots no canal Slack com timestamps.
2. **Logs**: query estruturada em CloudWatch Logs / Datadog / Loki; filtrar por correlation_id se disponível.
3. **Traces**: abrir APM/X-Ray; identificar operações lentas ou falhas.
4. **Hipóteses**: listar 2-3 em ordem de prevalência conforme runbook. Marcar qual está sendo testada.

Compartilhar achados no canal em tempo real — scribe garante que tudo tenha timestamp.

### Passo 6: Decidir mitigação vs. debug

Conforme `codex-incident-response` §Rollback vs. forward-fix:

| Situação | Ação |
|---|---|
| Deploy recente (< 2h) + sem migração de dados | Rollback |
| Problema em dados já persistidos | Forward-fix |
| Causa raiz clara e fix trivial | Forward-fix rápido |
| Causa raiz obscura + impacto alto | Rollback + investigação em staging |

Em dúvida: **rollback**. Mitigar primeiro, entender depois.

### Passo 7: Aplicar mitigação + verificar recovery

Executar ação decidida:

- **Rollback de deploy**: revert no pipeline, confirmar via dashboard.
- **Feature flag off**: via sistema de flags (LaunchDarkly, Unleash).
- **Scale up**: adicionar instâncias se saturação de recursos.
- **Bloquear input malicioso**: WAF rule, rate limit.

**Verificar recovery**: esperar 5-10 min observando:
- Error rate volta ao baseline.
- Latency p99 volta ao normal.
- Alertas cessam de disparar.

Se NÃO recupera em 10 min → escalar severity ou hipótese errada; voltar ao Passo 5.

### Passo 8: Comunicar status

**Interno** (canal do incidente):
```
✅ Mitigation applied — rolling back to v1.34.2
[15:42] Error rate dropping; p99 recovering
[15:47] Stable — monitoring for 10 min before declaring resolved
```

**Externo** (se SEV-1 ou SEV-2 com impacto a cliente):
- Atualizar status page em cada estado: Investigating → Identified → Monitoring → Resolved.
- Comms Lead escreve; IC aprova; ninguém mais publica.

**Executivo** (se SEV-1 ou duração >1h):
- Email/Slack DM a liderança a cada hora ou em mudança de estado.

### Passo 9: Entregar linha do tempo inicial

Antes de sair do "modo triage" e entrar em "modo investigação":

1. Consolidar timeline estruturado em documento central:
   ```markdown
   # Timeline — {service} {date}

   | Horário (UTC) | Evento |
   |---|---|
   | 14:32 | Alert dispara — p99 > 500ms |
   | 14:35 | On-call acknowledge, SEV-2 declarada |
   | 14:38 | War room aberto |
   | ... |
   ```

2. Este documento alimenta o post-mortem (`kata-postmortem-write`).

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Severity declarada + acionamentos | Mensagem estruturada | Canal do incidente |
| Timeline inicial | Markdown | Documento central (Notion, Google Docs, repo) |
| Mitigação aplicada + recovery confirmado | Observação em dashboards | Print/link no canal |
| Status page updates | Texto estruturado | statuspage.io ou equivalente |

## Restrições

- **Severity NÃO é opinião**: aplicar critérios de `codex-incident-response` objetivamente.
- **Não culpa durante incidente**: linguagem factual ("o deploy X causou degradação"), nunca ("o dev Y deployou bug"). Post-mortem blameless começa aqui.
- **Comms tem um dono**: Comms Lead é o único que publica externamente; evita contradições.
- **Mitigação vem antes de entendimento completo**: restaurar serviço > descobrir porque; debug depois.

## Referências

- `codex-incident-response` — severity, papéis, comms templates
- `lex-runbook-for-every-alert` — runbook é base do Passo 4
- `lex-slo-required` — incidente consome error budget
- `kata-postmortem-write` — procedimento após incidente
- `warrior-hestia`
