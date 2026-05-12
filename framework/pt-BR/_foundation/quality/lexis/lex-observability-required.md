# Lexis: Observabilidade é Obrigatória

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Todo novo endpoint HTTP, consumer de evento, job agendado ou worker de longa execução em qualquer stack

## Propósito

Código sem observabilidade falha em silêncio. Quando um endpoint fica lento, um consumer de evento perde mensagens, ou um job de background entra em loop, engenheiros sem traces, métricas e logs estruturados ficam cegos — incidentes levam horas para diagnóstico, post-mortems viram chute e o impacto no usuário é estimado em vez de medido. Isso acontece mesmo com `codex-python-observability` existindo, porque instrumentação é tratada como opcional.

Esta Lexis existe para garantir que **toda nova superfície de runtime (endpoint, consumer, job) emita traces, métricas e logs estruturados desde o primeiro dia**, que **identificadores de correlação propaguem através de fronteiras de serviço** e que **o Gate 2 reprove implementações sem esses sinais**.

## Lei

> **Todo novo endpoint HTTP, consumer de evento, job agendado ou worker de longa execução DEVE emitir um trace distribuído (span), pelo menos uma métrica de latência e logs estruturados com correlation ID nos caminhos de sucesso e falha. Serviços que se comunicam via HTTP ou event bus DEVEM propagar o correlation ID (W3C Trace Context ou equivalente). Logs NÃO PODEM conter dados sensíveis (PII, segredos, números de cartão completos).**

## Regras

### 1. Três sinais por nova superfície de runtime

Para cada novo endpoint, consumer ou job, o agente **DEVE** instrumentar:

1. **Trace:** um span envolvendo a unidade de trabalho, com atributos (entity id, nome da operação, outcome).
2. **Métrica:** no mínimo, histograma de latência; contadores para erros/retries quando aplicável.
3. **Log:** estruturado (JSON) com `correlation_id`, `entity_type`, `entity_id`, `operation`, `outcome`.

Base neutra preferida: **OpenTelemetry SDK** (exporter OTLP); fallbacks específicos de plataforma (CloudWatch EMF, Datadog APM) aceitáveis quando OTel não está disponível no ambiente.

### 2. Propagação do correlation ID

O agente **DEVE**:

1. Aceitar header `traceparent` (W3C Trace Context) em HTTP inbound; gerar se ausente.
2. Propagar esse trace context em chamadas outbound (outros HTTP, publicação de eventos) via header `traceparent` ou metadata do envelope do evento.
3. Incluir `correlation_id` (trace id em minúsculas) em toda linha de log produzida durante a unidade de trabalho.

### 3. Dados sensíveis em logs

O agente **NÃO PODE** logar:

- Números de cartão completos, CVVs, PINs.
- Senhas, tokens de API, cookies de sessão.
- CPF/CNPJ completos — mascarar ou hash (últimos 4 dígitos aceitáveis quando identificador auditável é necessário).
- Corpos de email ou conteúdo de mensagens quando dados do usuário não são essenciais para debug.

Bibliotecas de logging DEVEM aplicar filtros de redaction; agentes DEVEM revisar statements de log gerados para vazamentos.

### 4. Caminhos de erro também são observados

O agente **DEVE** garantir:

1. Exceções não tratadas se propagam no trace como status de erro + exceção registrada.
2. Outcomes de erro esperados (falhas de validação, erros de negócio conhecidos) emitem contadores e são logados em `WARN` com `outcome=error` e código do erro.
3. Blocos `except: ...` que engolem erros sem pelo menos um log + métrica são proibidos (reforça `lex-python-error-handling`).

### 5. Enforcement no Gate 2

`kata-quality-gate` Check 3 **DEVE** verificar que instrumentação está presente para cada nova superfície de runtime declarada na tabela de componentes da Fase 3. Heurística (dependente do stack):

- Python: buscar `@trace`, `tracer.start_as_current_span`, `metric.observe`, uso de logger estruturado.
- Frontend (rotas de servidor): buscar middleware de tracing, inicialização de `sendBeacon`/APM SDK.
- Infraestrutura: X-Ray / OTel integration configurada onde os serviços rodam.

Ausência = ❌ `Check 3 — lex-observability-required`.

## Abrangência

- **Aplica-se a:** todo componente listado como novo endpoint/consumer/job no `.issues/{n}/03-architecture.md`.
- **Agentes vinculados:** todos os warriors que implementam código de runtime (Apollo, Hephaestus, Hera quando executa testes, etc.); verificado por `warrior-athena` no Gate 2.
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Incidentes às cegas:** mediana de tempo-para-diagnóstico infla de minutos para horas; impacto em cliente escala antes da detecção.
2. **Ficção no post-mortem:** sem logs e traces, narrativas de causa raiz são inferidas — frequentemente erradas, levando a incidentes recorrentes.
3. **Falha de compliance:** SOC 2 CC7 / ISO 27001 A.12.4 exigem explicitamente logging de atividade; auditorias falham.
4. **Remediação:** PR rejeitado pelo Gate 2 até adicionar instrumentação; backport de instrumentação antes da release.

## Validação Automatizada

- **Ferramenta:**
  - Regra de lint / análise estática escaneando chamadas de instrumentação nas superfícies novas declaradas.
  - Request sintético em staging — verificar que trace aparece no backend de tracing.
  - Checks de redaction de log (regex para padrões de credencial em linhas de log amostradas).
- **Momento:** Gate 2 (pré-PR); contínuo em produção via pipelines de log/métrica.
- **Métrica:** 100% dos novos endpoints/consumers com span + métrica + log estruturado; 0 eventos de vazamento de dados sensíveis.

## Referências

- `codex-python-observability` — padrões OpenTelemetry para Python
- `kata-quality-gate` — enforce desta Lexis no Check 3
- `lex-python-error-handling` — caminhos de erro também devem ser observados
- `lex-mcp` — ao usar MCP para auditoria, mesmo correlation id aplica
- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
