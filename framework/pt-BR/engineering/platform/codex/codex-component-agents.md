# Codex: Component Agents — Orchestrator + Specialists

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — convenções internas do diretório `components/agents/`

## Visão Geral

`components/agents/` hospeda os agentes LLM do bounded context. A convenção é **Orchestrator + Specialists**: um agente coordenador decompõe a tarefa do usuário em subtarefas e despacha para agentes especializados, cada um com seu próprio prompt, conjunto de tools e contrato de input/output. Este codex detalha estrutura física, padrões de tool registry, memory layer e a fronteira com `docs/{context}/agents/` (especificação) e `components/api/` (read model).

## Contexto

- **Domínio:** estrutura física de agentes LLM (código, não especificação)
- **Público-alvo:** engenheiros AI, Apollo quando delega implementação agentic, Métis (apollo-agents)
- **Atualização:** mudança de SDK de agents, nova convenção de tool, ADR sobre memory backend

## Fronteira pre-req-A vs pre-req-C

| Eixo | Onde | O que define | Governança |
|------|------|--------------|------------|
| **Físico** (este codex) | `components/agents/` | Pastas, módulos, código do Orchestrator, código dos Specialists, registry de tools, infra Bedrock | `codex-component-agents` |
| **Documental** | `docs/{context}/agents/` | System prompt, capabilities, memory schema, feedback loop, métricas | `codex-feature-design-docs` (categoria `agents/`, definição completa em pre-req-C) |

System prompt é **especificação documental** em `docs/{context}/agents/system-prompt.md`. Quando `lex-system-prompt` (pre-req-B) for entregue, ele governará o conteúdo daquele arquivo. Este codex só governa o **layout físico** que carrega/executa o agente.

## Estrutura interna

```
components/agents/
├── pyproject.toml
├── src/
│   └── {context}_agents/
│       ├── orchestrator/
│       │   ├── agent.py             # Loop principal, decomposição de tarefa
│       │   ├── prompt_loader.py     # Carrega prompt de docs/{context}/agents/
│       │   └── routing.py           # Decide qual Specialist invocar
│       ├── specialists/
│       │   ├── {specialist_name}/
│       │   │   ├── agent.py         # Agente focado
│       │   │   └── prompt_loader.py
│       │   └── ...
│       ├── tools/
│       │   ├── deterministic/       # Tools puros (cálculo, validação, formatação)
│       │   └── ml/                  # Tools que chamam outros modelos ou serviços
│       ├── memory/                  # Backend de memory (Redis, DynamoDB, etc.)
│       ├── feedback/                # Coleta de feedback do usuário e auto-avaliação
│       └── infra/
│           ├── bedrock.py           # Cliente boto3 + retry policy
│           └── streaming.py         # SSE/streaming responses
└── tests/
```

`orchestrator/` é singular por bounded context. `specialists/` aceita múltiplos subdirectórios — um por specialist. `tools/` separa deterministic (testável com unit test puro) de ml (mock obrigatório).

## Padrões essenciais

1. **System prompt fora do código.** Prompts vivem em `docs/{context}/agents/`; código carrega via `prompt_loader.py`. Trocar prompt não exige rebuild.
2. **Tool registry tipado.** Cada tool tem schema (Pydantic) de input e output. Orchestrator descobre tools via registry, não via import direto.
3. **Memory layer abstrato.** Use case do agente consome `MemoryPort` (Protocol). Implementação concreta (Redis, DynamoDB) vive em `memory/`.
4. **Tracing por turno.** Cada tool call e cada invocação de Specialist gera span próprio per `lex-observability-required`. Correlation ID propagado.
5. **Streaming opcional.** Quando o Orchestrator stream-a a resposta, usar SSE; quando bufferiza, retornar JSON direto.
6. **Feedback loop.** Toda interação registra eventos de feedback (thumbs, retry, abandono) para o futuro componente de aprendizado (escopo pre-req-C).

## Fronteira com outros components

| Pode | Não pode |
|------|----------|
| Chamar `components/api/` via porta read-only para dados canônicos | Modificar DB do bounded context diretamente |
| Publicar eventos (`lex-cloudevents`) — ex.: agent.suggestion.created | Importar código de `components/jobs/` ou `components/ui/` |
| Consumir `docs/{context}/agents/system-prompt.md` como input de runtime | Hospedar a especificação do agente no próprio component |
| Disparar Lambda `components/jobs/` via evento async | Chamar `components/jobs/` síncrono |

## Anti-padrões

| Anti-padrão | Caminho correto |
|-------------|-----------------|
| System prompt hardcoded em `agent.py` | Mover para `docs/{context}/agents/`, carregar via loader |
| Tool importado direto, sem registry | Registrar no tool registry com schema; Orchestrator descobre |
| Orchestrator acessa DB direto | Consumir via porta de `components/api/` ou read model dedicado |
| Specialist invoca outro Specialist | Specialists não se conhecem; sempre via Orchestrator |
| Memory implementado direto com cliente Redis em `agent.py` | Abstrair em `MemoryPort`; implementação em `memory/` |

## Referências

- `codex-component-architecture` — fronteiras gerais; fronteira `agents/` físico vs documental
- `codex-feature-design-docs` § categoria `agents/` (reservada) — onde vive a especificação (escopo pre-req-C)
- `lex-system-prompt` *(a ser entregue em pre-req-B; placeholder)* — governará o conteúdo do system prompt em `docs/{context}/agents/system-prompt.md`
- `codex-python-architecture`, `codex-python-tooling`, `codex-python-observability` — convenções Python transversais
- `lex-python-typing`, `lex-python-immutability`, `lex-python-result-type`
- `lex-observability-required`, `lex-logging-decorator`
- `lex-cloudevents`, `lex-idempotency` — eventos saindo do agente
- `references.component_template_repo.url` em `.ahrena/.directives`
