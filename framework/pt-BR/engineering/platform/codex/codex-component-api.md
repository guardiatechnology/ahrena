# Codex: Component API — Convenções Hexagonais

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — convenções internas do diretório `components/api/`

## Visão Geral

`components/api/` expõe os endpoints HTTP/REST do bounded context. Segue arquitetura hexagonal (ports + adapters), Python como linguagem principal, FastAPI como framework HTTP em deploys persistentes (ECS/Fargate, container EC2) e Lambda + AWS Lambda Powertools quando o deploy é serverless. Este codex detalha a estrutura interna, as convenções de dependência e o que pertence (e o que não pertence) aqui dentro. A fronteira com outros components vive em `codex-component-architecture`.

## Contexto

- **Domínio:** API HTTP do bounded context
- **Público-alvo:** engenheiros backend, agentes de implementação Python (Apollo), revisores de PR
- **Atualização:** mudança de stack (versão major FastAPI, Powertools), nova convenção de adapter, ADR de fronteira

## Stack canônico

| Camada | Ferramenta | Notas |
|--------|------------|-------|
| Gerenciamento de pacote | `uv` | Lock determinístico; manifest `pyproject.toml` próprio do component |
| Framework HTTP (persistente) | FastAPI | Routers organizados por agregado, dependências via DI nativa |
| Runtime serverless | AWS Lambda + Powertools | `aws-lambda-powertools` para tracing, logging, métricas, idempotência |
| Validação de payload | Pydantic v2 | Modelos `frozen` per `lex-python-immutability` |
| Cliente HTTP saída | `httpx` async | Timeouts explícitos, retry com backoff |
| Tipagem | mypy strict per `lex-python-typing` | — |
| Erros | `lex-python-error-object`, `lex-error-handling` | `Result[T, Error]` per `lex-python-result-type` |

Convenções Python detalhadas: ver `codex-python-architecture`, `codex-python-fastapi`, `codex-python-logging`.

## Estrutura interna

```
components/api/
├── pyproject.toml
├── src/
│   └── {context}_api/
│       ├── adapters/
│       │   ├── inbound/         # Controllers FastAPI (routers), handlers Lambda
│       │   └── outbound/        # Clientes HTTP, DB repositories, publishers de eventos
│       ├── application/
│       │   ├── ports/           # Interfaces (Protocol/ABC) consumidas pelos use cases
│       │   └── use_cases/       # Lógica de aplicação, orquestra domínio
│       ├── domain/              # Entities, value objects, regras de negócio puras
│       ├── infra/               # Bootstrap de logger, tracer, db, secrets
│       └── main.py              # FastAPI app factory ou Lambda entry
└── tests/
    ├── unit/                    # domain + use cases
    ├── integration/             # adapters reais (DB, HTTP)
    └── e2e/                     # API end-to-end com testcontainers
```

A linha entre `adapters/inbound/` e `application/use_cases/` é estrita: controllers traduzem HTTP → comando de use case e use case → HTTP response. Lógica de negócio mora em `domain/` ou `application/use_cases/`.

## Padrões essenciais

1. **Idempotência em mutations.** Toda rota mutativa (POST, PATCH, DELETE) exige header `Idempotency-Key` per `lex-idempotency`. Em Lambda, usar o middleware oficial de Powertools.
2. **Trace propagation.** `X-Grd-Trace-Id` aceito no inbound e propagado nos outbound clients per `codex-restful-headers` e `lex-observability-required`.
3. **Result type em fronteira.** Use cases retornam `Result[T, Error]`. Controllers convertem `Failure` em response per `lex-error-handling` (array `errors` com `code`, `reason`, `message`).
4. **Paginação canônica.** Listings consomem `page_size` + `page_token` per `codex-restful-pagination`.
5. **OpenAPI como contrato.** O `openapi.yaml` em `docs/{context}/oas/` é a verdade per `lex-feature-design-docs`. Controllers respeitam o contrato; CI valida diff.
6. **Logging via decorator.** Per `lex-logging-decorator` — chamadas `logger.info` inline em código de aplicação são proibidas; usar wrapper centralizado.

## Fronteira com outros components

| Pode | Não pode |
|------|----------|
| Ler/escrever no DB compartilhado do bounded context | Acessar tabelas privadas de outro bounded context |
| Publicar eventos via `lex-cloudevents` | Importar código de `components/jobs/` ou `components/agents/` direto |
| Ser chamado por `components/ui/` via HTTP | Chamar `components/jobs/` síncrono (use evento) |
| Ser chamado por `components/agents/` via porta read-only | Hospedar lógica que pertence a domain de outro bounded context |

## Anti-padrões

| Anti-padrão | Caminho correto |
|-------------|-----------------|
| Lógica de negócio em controller (router function) | Mover para `application/use_cases/`; controller só traduz |
| Pydantic model exposto direto como entidade de domínio | Modelo HTTP em `adapters/inbound/`, entidade pura em `domain/` |
| Cliente DB instanciado dentro de use case | Injetar via port; adapter outbound implementa |
| Sem `Idempotency-Key` em POST | Header obrigatório; CI/lint pega |
| Bare `except` ou raise de exceção em fluxo esperado | Per `lex-python-error-handling` + `lex-python-result-type` |

## Referências

- `codex-component-architecture` — fronteiras gerais entre components
- `codex-python-architecture`, `codex-python-fastapi`, `codex-python-tooling` — convenções Python transversais
- `lex-python-typing`, `lex-python-immutability`, `lex-python-error-object`, `lex-python-result-type`, `lex-python-error-handling`, `lex-python-security`, `lex-python-testing`
- `lex-restful-apis`, `codex-restful-payload`, `codex-restful-headers`, `codex-restful-pagination`, `codex-restful-status-codes`, `codex-restful-sorting`, `codex-oas-structure`
- `lex-idempotency`, `lex-error-handling`, `codex-known-errors`
- `lex-observability-required`, `lex-logging-decorator`
- `lex-feature-design-docs`, `codex-feature-design-docs` — `docs/{context}/oas/openapi.yaml` como contrato
- `references.component_template_repo.url` em `.ahrena/.directives` — layout exato do template externo
