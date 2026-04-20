# Lexis: Pirâmide de Testes

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Distribuição de testes entre níveis (unit, integração, E2E) em qualquer stack para garantir feedback rápido, cobertura adequada e custo sustentável

## Propósito

Pipelines dominados por testes E2E lentos matam o ciclo de dev (feedback em minutos em vez de segundos); suites dominadas por mocks unit dão falsa segurança (testes passam, integração explode em prod). A pirâmide de testes distribui rigor pelos níveis onde cada tipo funciona melhor — unit rápido e barato na base, E2E caro mas essencial no topo.

Esta Lexis existe para garantir que **cada projeto tenha distribuição de testes proporcional à pirâmide**, que **testes E2E sejam restritos a jornadas críticas**, e que **testes de integração cubram as fronteiras reais (BD, fila, API externa)**.

## Lei

> **Toda suite de testes DEVE respeitar a proporção aproximada 70% unit / 20% integração / 10% E2E. Testes E2E DEVEM cobrir apenas jornadas críticas declaradas (login, checkout, onboarding) — nunca CRUD exaustivo. Testes de integração DEVEM usar fronteiras reais (banco real, filas reais em container) e mocks DEVEM ser limitados a serviços externos não gratuitos ou não determinísticos.**

## Regras

### 1. Proporção 70/20/10

Medida por **número de testes** (não por tempo). Tolerância: ±10 pontos percentuais em projetos pequenos (<50 testes totais).

Se a proporção inverte (ex.: 30% unit / 60% E2E) → **suite está desbalanceada**; refatorar antes de adicionar mais testes.

### 2. E2E só para jornadas críticas

Uma jornada E2E:
- Representa uma transação de valor real ao usuário final (pagar, reservar, enviar).
- Cruza múltiplos bounded contexts ou UI + backend + dados.
- Tem custo real de falha (receita perdida, dados corrompidos).

Casos que **NÃO** merecem E2E:
- Validação de formulário (teste unitário de componente basta).
- CRUD padrão (teste de integração no endpoint + unit no domínio).
- Variações estéticas ou layout.

### 3. Integração usa fronteiras reais

O agente **DEVE**:

- Usar **banco de dados real** em container (PostgreSQL, MySQL) — não SQLite in-memory em projetos que rodam PostgreSQL em prod.
- Usar **filas reais** em container (Redis, RabbitMQ, Kafka) — não mocks de biblioteca.
- Usar **containers com versão igual à de produção** (`postgres:16` não `postgres:latest`).

O agente **PODE** mockar:
- APIs externas pagas (Stripe, providers de SMS).
- Serviços que não têm sandbox público.
- Tempo/clock para testes determinísticos.

### 4. Isolamento entre testes

Testes do mesmo nível **NÃO DEVEM** compartilhar estado mutável. Cada teste:
- Começa de estado conhecido (fixtures, truncate, transação isolada).
- Não depende da ordem de execução.
- Pode rodar em paralelo sem race condition.

Testes flaky = bug: ou no teste, ou no sistema. Nunca tolerar retry como solução.

### 5. Pirâmide adaptada por contexto

Exceções à 70/20/10 permitidas com justificativa documentada:

- **Projetos de integração puros** (ETL, glue code): pirâmide invertida natural (mais integração); documentar.
- **Bibliotecas puras** (sem I/O): 90%+ unit é aceitável.
- **Apps mobile**: UI tests (Espresso/XCUITest) substituem parcialmente E2E; proporção ajustada.

Documentar desvio em ADR quando estrutural.

## Abrangência

- **Aplica-se a:** toda suite de testes em todos os projetos Ahrena.
- **Agentes vinculados:** `warrior-hera`, `warrior-apollo`, `warrior-hephaestus`.
- **Exceções:** Nenhuma. Lexis não admitem exceções (desvios documentados são contextuais, não violações).

## Consequências de Violação

1. **Pipeline lento:** 80% E2E = build de 30+ min; dev desliga o CI local, regressões escapam.
2. **Falsa segurança:** 90% unit com mocks = prod quebra em produção em integrações não testadas.
3. **Testes flaky toleradas:** equipe aprende a ignorar red builds; cobertura vira teatro.
4. **Remediação:** auditar distribuição; migrar testes no nível errado (E2E → integração quando possível); declarar jornadas E2E legítimas explicitamente.

## Validação Automatizada

- **Ferramenta:** contagem de testes por diretório convencional (`tests/unit`, `tests/integration`, `tests/e2e`); lint que flag testes E2E fora do diretório declarado.
- **Momento:** mensalmente em CI como relatório; no Gate 2 (via `kata-quality-gate` Check 3) para novas features.
- **Métrica:** distribuição ≈ 70/20/10 ±10pp; 0 testes flaky ativos; tempo de suite unit < 60s.

## Referências

- `lex-frontend-testing`, `lex-python-testing` — regras por stack
- `codex-test-strategy` — estratégia detalhada (níveis, escopos)
- `warrior-hera` — QA/Test Strategy specialist
- [Test Pyramid — Martin Fowler](https://martinfowler.com/bliki/TestPyramid.html)
