# Codex: Component Jobs — Workers Assíncronos

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — convenções internas do diretório `components/jobs/`

## Visão Geral

`components/jobs/` hospeda os workers assíncronos do bounded context: handlers Lambda disparados por eventos (EventBridge, SQS, S3), Step Functions Tasks, jobs agendados (cron via EventBridge Scheduler). Não há FastAPI aqui — runtime é Lambda + AWS Lambda Powertools. Este codex detalha estrutura interna, contratos de input/output e a fronteira com `components/api/`.

## Contexto

- **Domínio:** processamento assíncrono dentro do bounded context
- **Público-alvo:** engenheiros backend, Apollo quando delega worker
- **Atualização:** nova convenção de orchestration (Step Functions), mudança major de Powertools, ADR de fronteira

## Stack canônico

| Camada | Ferramenta | Notas |
|--------|------------|-------|
| Gerenciamento de pacote | `uv` | Manifest próprio do component |
| Runtime | AWS Lambda + `aws-lambda-powertools` | Tracing, structured logging, metrics, idempotency, parameters, batch processing |
| Validação | Pydantic v2 | Schemas frozen |
| Cliente AWS | `boto3` | Clients reutilizáveis (sessão única) |
| Orquestração | AWS Step Functions | Quando workflow é multi-step com retry/fallback |
| Tipagem | mypy strict | per `lex-python-typing` |
| Idempotência | `aws_lambda_powertools.utilities.idempotency` | DynamoDB como store, TTL configurável |

## Estrutura interna

```
components/jobs/
├── pyproject.toml
├── src/
│   └── {context}_jobs/
│       ├── tasks/
│       │   ├── {task_name}/
│       │   │   ├── handler.py       # Lambda entry; aplica middleware + chama use case
│       │   │   ├── use_case.py      # Lógica de aplicação
│       │   │   └── schemas.py       # Pydantic input/output
│       │   └── ...
│       ├── middleware.py            # Powertools tracing + logging + idempotency
│       ├── errors.py                # Tipos de Error per lex-python-error-object
│       └── infra/
│           ├── aws.py               # boto3 clients, retry policy
│           └── eventbridge.py       # Publish helpers
└── tests/
    ├── unit/                        # use cases puros
    └── integration/                 # moto[lambda,stepfunctions,sqs]
```

Um diretório por task em `tasks/`. Handlers são thin (validate → call use case → format output). Use case carrega lógica.

## Padrões essenciais

1. **Idempotência via Powertools.** Tasks disparadas por SQS/EventBridge usam `@idempotent` com `event_key_jmespath` que isola a chave canônica (per `lex-idempotency`). Store em DynamoDB.
2. **Step Functions I/O explícito.** Quando o handler é Task de uma state machine, schemas Pydantic descrevem input e output esperados — a state machine confia em formato fixo.
3. **Tracing automático.** Powertools `Tracer` enabled em todo handler; correlation ID propagado quando origem traz `traceparent` ou equivalente per `lex-observability-required`.
4. **Logging via decorator.** Per `lex-logging-decorator` — `aws_lambda_powertools.Logger` configurado no bootstrap; nenhuma chamada `logger.info` inline em handler.
5. **Result type na fronteira.** Use cases retornam `Result[T, Error]` per `lex-python-result-type`; handler converte `Failure` em erro de Step Functions (raise para retry/fallback) ou em DLQ.
6. **Batch processing.** Para SQS/Kinesis, usar `BatchProcessor` de Powertools — falhas parciais isoladas, mensagens bem-sucedidas deletadas.

## Fronteira com outros components

| Pode | Não pode |
|------|----------|
| Ler/escrever no DB compartilhado do bounded context | Acessar tabelas privadas de outro bounded context |
| Publicar eventos (`lex-cloudevents`) — disparar próximo step | Chamar `components/api/` síncrono — usar evento ou consulta direta a DB |
| Ser disparado por evento de `components/api/` ou cron | Importar código de `components/api/` direto |
| Coordenar via Step Functions com outras tasks do mesmo component | Cross-bounded-context: usar EventBridge inter-context |

## Anti-padrões

| Anti-padrão | Caminho correto |
|-------------|-----------------|
| Handler chama API HTTP do próprio bounded context | Acessar DB direto ou consumir read model; HTTP é overhead injustificado |
| Sem `@idempotent` em handler de SQS/EventBridge | Per `lex-idempotency` — chave por evento, store em DynamoDB |
| Lógica de negócio dentro do handler | Mover para `use_case.py`; handler só orquestra middleware → use case → response |
| Cliente boto3 instanciado dentro do handler | Cliente em `infra/aws.py` reutilizado entre invocações (cold start otimizado) |
| Step Functions com input/output não validado | Pydantic schema em `schemas.py`; state machine documenta contrato |

## Referências

- `codex-component-architecture` — fronteiras gerais entre components
- `codex-python-architecture`, `codex-python-tooling`, `codex-python-observability`
- `lex-python-typing`, `lex-python-immutability`, `lex-python-error-object`, `lex-python-result-type`, `lex-python-error-handling`, `lex-python-testing`
- `lex-idempotency`, `codex-known-errors`
- `lex-observability-required`, `lex-logging-decorator`
- `lex-cloudevents`, `codex-cloudevents` — eventos saindo do worker
- `codex-aws-services`, `lex-aws-iac` — infraestrutura coberta em `components/deployment/`
- `references.component_template_repo.url` em `.ahrena/.directives`
