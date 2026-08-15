# Codex: Arquitetura por Components em Bounded Contexts Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — estrutura física de bounded contexts (api, agents, jobs, ui, deployment)

## Estrutura Canônica do Bounded Context

```
{bounded-context}/
├── components/
│   ├── api/                # Hexagonal API (FastAPI ou Lambda + Powertools)
│   ├── agents/             # Orchestrator + Specialists (LLM)
│   ├── jobs/               # Workers assíncronos (Lambda + Step Functions)
│   └── ui/                 # Next.js app + widgets exportados (tsup)
├── deployment/             # IaC (CDK/Terraform), tagging, secrets, monitoring
└── docs/                   # Documentação de design (entities/oas/events/...)
```

`docs/` é governado por `lex-feature-design-docs` e `codex-feature-design-docs`. **Documentação** (`docs/{context}/agents/`) é eixo distinto de **estrutura física** (`components/agents/`) — ver nota em "Fronteira agents: pre-req-A vs pre-req-C" abaixo.

### Convenções gerais

| Item | Regra |
|------|-------|
| `{bounded-context}` | kebab-case do nome do contexto (PascalCase DDD → kebab-case). Ex.: `ScheduledPayments` → `scheduled-payments` |
| Subpasta de component | `api`, `agents`, `jobs`, `ui` — em singular, kebab-case, sempre dentro de `components/` |
| `deployment/` | Single source of IaC do bounded context. Não é "component" produtivo (não roda como aplicação) |
| `docs/` | Estrutura fixa per `codex-feature-design-docs` — `entities/`, `oas/`, `events/`, `agents/`, `metrics/` |
| 1 component = 1 unidade | Um manifest de dependências, uma suíte de testes, uma unidade de deploy. Exceção requer ADR |

### Quando criar cada component

| Component | Crie quando | Não crie se |
|-----------|-------------|-------------|
| `api/` | Há endpoints HTTP/REST públicos ou para outros bounded contexts | Bounded context é puramente reativo a eventos sem API |
| `agents/` | Há um agente LLM (Orchestrator) que decompõe tarefas para Specialists | Não há LLM no caminho crítico |
| `jobs/` | Há trabalho assíncrono disparado por eventos, cron, ou Step Functions | Toda a lógica cabe em sync HTTP request |
| `ui/` | Há interface humana (Next.js app, widgets embarcáveis) | Bounded context é backend-only |
| `deployment/` | **Sempre.** Todo bounded context tem IaC mínima (mesmo que só tagging) | — |

Não há obrigação de criar todos os 4 components produtivos. Bounded contexts pequenos podem ter apenas `api/` e `deployment/`.

## Fronteiras entre Components

Decisões de fronteira evitam que código vaze para o component errado:

| Decisão | Regra |
|---------|-------|
| Banco de dados compartilhado | `api/` e `jobs/` MAY ler/escrever no mesmo schema. `agents/` MAY consultar via porta dedicada (read model). `ui/` NÃO acessa DB direto — sempre via `api/` |
| Chamadas síncronas | `ui/` chama `api/` (HTTP). `agents/` chama `api/` quando precisa de dados canônicos. `jobs/` NUNCA chama `api/` síncrono — usa evento ou consulta direta |
| Disparar evento | Qualquer component MAY publicar evento per `lex-cloudevents`. Idempotência via `lex-idempotency` |
| Manifest de dependências | Cada component tem o seu (`pyproject.toml`, `package.json`). Compartilhar deps cross-component é evitado; quando necessário, vira biblioteca interna (`libs/`) com ADR |
| Suíte de testes | Cada component testa o seu code. Testes E2E que cruzam components vivem em `deployment/tests/` ou `tests/e2e/` na raiz do bounded context |
| Deploy independente | `api/`, `agents/`, `jobs/`, `ui/` são deployáveis separadamente. Coordenação cross-component em release vive em `deployment/` |

### Fronteira `agents/`: pre-req-A vs pre-req-C

Existe ambiguidade aparente entre dois eixos chamados "agents". Eles cobrem coisas diferentes:

| Eixo | Onde vive | O que descreve | Governança |
|------|-----------|----------------|------------|
| **Estrutura física** | `components/agents/` | Implementação: pastas, módulos, código do Orchestrator + Specialists, tools, infra Bedrock | Este codex (`codex-component-agents`) |
| **Estrutura documental** | `docs/{context}/agents/` | Documentação do agente: system prompt, capabilities, memory schema, feedback loop, métricas | `codex-feature-design-docs` (categoria `agents/`, pré-aberta para pre-req-C) |

Resumo: `components/agents/` é **código**; `docs/{context}/agents/` é **especificação**. Um implementa o que o outro define.

## 5 Codex-filhos

Para cada component produtivo + deployment, existe um codex especializado que detalha stack, estrutura interna, padrões e fronteiras. Consulte o filho ao implementar dentro do component correspondente.

| Codex-filho | Cobre | Stack principal |
|-------------|-------|-----------------|
| `codex-component-api` | `components/api/` | FastAPI + uv + ports/adapters; Powertools quando rodando em Lambda |
| `codex-component-agents` | `components/agents/` | Orchestrator + Specialists; tools determinísticos vs LLM; memory layer |
| `codex-component-jobs` | `components/jobs/` | Lambda Powertools + Step Functions; idempotência via `lex-idempotency` |
| `codex-component-ui` | `components/ui/` | Next.js + tsup (widgets); consumo de `@guardia/design-system` |
| `codex-component-deployment` | `deployment/` | IaC per `lex-aws-iac`; tagging per `lex-aws-cost`; security per `lex-aws-security` |

Hierarquia: o codex-mãe (este) define fronteiras e lista os filhos. Filhos detalham o interior de cada component, **não referenciam o codex-mãe nem outros filhos** (compõem por leitura sequencial quando necessário).

## Referência externa via diretiva

O repositório template externo é apontado por `references.component_template_repo.url` em `.ahrena/.directives`. Esta diretiva é a source-of-truth viva — quando o template externo evolui (nova versão, nova convenção), a diretiva é atualizada e o codex permanece estável.

Como consumir:

1. Agente lê `.ahrena/.directives` per `lex-directives`.
2. Encontra `references.component_template_repo.url`.
3. Quando precisar inspecionar layout exato (ex.: nome de arquivo de manifest, ordem de imports padrão), consulta o repo apontado.

Codex e Lexis nunca usam o nome do repo hardcoded. ADR é exigido para mudar a URL apontada.

## Anti-padrões

| Anti-padrão | Por que é problema | Caminho correto |
|-------------|-------------------|-----------------|
| Importar código de `api/` em `jobs/` direto via path relativo | Acopla components que deveriam ser independentes | Extrair lógica para `libs/` interna com ADR, ou comunicar via evento |
| Criar componentes top-level fora de `components/` | Quebra a convenção; agentes e ferramentas esperam o layout fixo | Sempre criar dentro de `components/{name}/` |
| Documentar agent dentro de `components/agents/README.md` | Mistura código e especificação; revisão fica fragmentada | Especificação em `docs/{context}/agents/`; código em `components/agents/` |
| URL do repo template hardcoded no codex | Acopla o codex a um repo que pode mudar | Apontar para `references.component_template_repo.url` no `.directives` |
| Component sem `deployment/` correspondente | Não dá para subir em produção sem IaC | `deployment/` é obrigatório mesmo que mínimo |
