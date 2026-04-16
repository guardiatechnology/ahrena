# Codex: Estratégia de Testes

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Estratégia de testes aplicada no framework Ahrena — níveis, escopos, ferramentas, quando usar cada um, anti-patterns

## Visão Geral

Este Codex é a referência operacional para **decisões de estratégia de testes** em projetos Ahrena. Consultado por `warrior-hera` ao desenhar plano de testes para uma feature, por `warrior-apollo` e `warrior-hephaestus` durante implementação quando há dúvida sobre em que nível testar algo, e por revisores de código no Gate 2.

## Contexto

- **Domínio:** estratégia de testes (o que testar, onde testar, como testar, quando NÃO testar)
- **Público-alvo:** `warrior-hera`, agentes que implementam código de produção, revisores
- **Atualização:** quando novos frameworks de teste emergem, quando padrões de arquitetura mudam (ex.: microserviços alteram o que é "integração")

## Conteúdo

### Os 4 níveis

| Nível | Escopo | Ferramentas | Tempo-alvo por teste |
|---|---|---|---|
| **Unit** | Função pura, classe isolada, componente sem I/O | pytest, Jest, Vitest, Go testing | < 100ms |
| **Integration** | Múltiplos componentes + infra real (BD, fila) | pytest + testcontainers, Jest + MSW + Postgres | < 10s |
| **E2E (API)** | Request HTTP real → sistema → response | pytest + httpx, Supertest, Pact | < 30s |
| **E2E (UI)** | Navegador real → UI → backend → UI | Playwright, Cypress | < 2min |

### Quando usar cada nível

**Unit**: lógica de domínio, utilities, funções puras, componentes de apresentação sem I/O.
- Regra: se escrever o teste requer mockar mais de 1 colaborador, provavelmente é integration, não unit.

**Integration**: qualquer caminho que toca persistência, fila, cache, API externa (mesmo em container).
- Regra: teste o que produção realmente usa (Postgres 16, não SQLite; Redis real, não in-memory).

**E2E (API)**: contrato externo visível ao consumidor; fluxos entre múltiplos endpoints.
- Regra: um por endpoint principal; mais um por fluxo multi-endpoint (ex.: create + list + delete).

**E2E (UI)**: jornadas críticas de negócio; comportamentos que só se manifestam no navegador (roteamento, autenticação end-to-end, eventos do DOM).
- Regra: ≤ 1 E2E UI por jornada (login, checkout, onboarding); NÃO um por tela.

### Decision tree

```
Algo novo para testar?
│
├── É função pura / lógica de domínio?
│   → Unit test
│
├── Envolve BD, fila, cache, ou integração real?
│   ├── Cross-service ou exige deploy completo?
│   │   → E2E (API)
│   └── Isolável com container?
│       → Integration
│
├── É jornada de usuário crítica e visual?
│   → E2E (UI), 1 por jornada
│
└── É variação estética ou CSS?
    → Visual regression test (ou inspeção manual)
```

### Ferramentas por stack

**Python (Apollo):**
- Unit: `pytest` + `pytest-mock`
- Property-based: `hypothesis`
- Integration: `pytest` + `testcontainers-python` + Postgres real
- E2E API: `pytest` + `httpx` ou `requests-mock` para externos
- Benchmarks: `pytest-benchmark`
- Coverage: `pytest-cov`

**Frontend (Hephaestus):**
- Unit/Component: `vitest` ou `jest` + `@testing-library/react`
- Integration: `vitest` + `msw` (mock de API)
- E2E: `playwright` (preferido) ou `cypress`
- Visual regression: `chromatic` (Storybook) ou `playwright-visual`
- Acessibilidade: `jest-axe`, `@axe-core/playwright`

**Backend infra (IaC):**
- Unit: validação de módulo Terraform (`terraform validate`, `terraform test`)
- Integration: aplicar em account sandbox + assert via AWS SDK
- Policy: `opa test`, `conftest`

### Estratégias para fronteiras

**APIs externas pagas (Stripe, Twilio):**
- Unit: mock completo.
- Integration: sandbox do provider quando disponível + contract test (Pact).
- Produção: teste de smoke canário pós-deploy.

**Webhooks recebidos:**
- Integration: enviar payload real do provider (capturado em VCR) para endpoint.
- Validar idempotência: enviar 2x, esperar 1 efeito.

**Eventos assíncronos:**
- Integration: publicar evento, esperar consumer processar (timeout controlado).
- Validar side effects (BD atualizado, evento downstream publicado).

### Anti-patterns a evitar

| Anti-pattern | Por que é ruim |
|---|---|
| Mockar BD em teste de repositório | Mascara bugs de query/migration; teste não prova nada real |
| Snapshot gigante sem revisão | Diff aceito cegamente; snapshot vira noise |
| Um E2E por endpoint | Suite explode; CI vira maratona; ROI cai |
| Retry em teste flaky | Não cura; mascara; ensina a ignorar sinais |
| `test.only` commitado | Rodamos só 1 teste no CI sem perceber; cobertura cai sem warning |
| Assert sobre implementação (`expect(foo.state).toBe(...)`)| Quebra a cada refactor sem regressão real |

### Cobertura

- **Cobertura ≥ threshold** (80% default) é condição necessária, não suficiente.
- Cobertura 100% de linha **não** significa testado: pode ser "foi executado mas sem assertion".
- Preferir `branch coverage` sobre `line coverage` quando disponível.
- Cobertura é **sinal**, não métrica-alvo. Features críticas (pagamento, auth) devem ter cobertura de fato (mutation testing com `mutmut`, `stryker` para validar qualidade dos asserts).

### Quando NÃO testar

- **Código trivial sem lógica** (getter/setter puro, `return x + 1`): teste adiciona ruído sem valor.
- **Wrappers finos de biblioteca** (`def create_uuid(): return uuid.uuid4()`): testa a biblioteca, não o código.
- **Configuração estática** (constantes, labels): testar só se muda frequentemente.
- **Código gerado**: confiar no gerador (OpenAPI client, Prisma schema).

Registrar decisão de "não testar" em comentário local ou em review — documentação > ausência silenciosa.

## Referências

- `lex-test-pyramid` — distribuição 70/20/10
- `lex-test-isolation` — determinismo e paralelismo
- `lex-python-testing`, `lex-frontend-testing` — regras por stack
- `warrior-hera` — executa estratégia
- `kata-test-plan-design` — procedimento de desenho
- `kata-quality-gate` — valida no Gate 2
- [Growing Object-Oriented Software, Guided by Tests (GOOS)](http://www.growing-object-oriented-software.com/)
