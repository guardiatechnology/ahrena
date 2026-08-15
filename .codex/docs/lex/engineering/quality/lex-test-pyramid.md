# Lexis: Pirâmide de Testes

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Distribuição de testes entre níveis (unit, integração, E2E) em qualquer stack para garantir feedback rápido, cobertura adequada e custo sustentável

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

## Validação Automatizada

- **Ferramenta:** contagem de testes por diretório convencional (`tests/unit`, `tests/integration`, `tests/e2e`); lint que flag testes E2E fora do diretório declarado.
- **Momento:** mensalmente em CI como relatório; no Gate 2 (via `kata-quality-gate` Check 3) para novas features.
- **Métrica:** distribuição ≈ 70/20/10 ±10pp; 0 testes flaky ativos; tempo de suite unit < 60s.
