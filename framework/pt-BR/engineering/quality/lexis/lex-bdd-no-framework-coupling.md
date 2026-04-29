# Lexis: Testes BDD sem Acoplamento a Framework BDD

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Engenharia — Qualidade. Implementação de testes que validam cenários Gherkin.

## Propósito

Step-runners (behave, pytest-bdd, cucumber e similares) criam uma infraestrutura paralela de testes (step definitions, regex matchers, hooks) que diverge da suite real, dobra o custo de manutenção e treina o time a perseguir glue em vez de comportamento. O ganho prometido — "negócio lê os testes" — raramente paga o custo: na prática, ninguém de negócio lê o `.feature` rodando, e o time vive corrigindo regex em arquivos `steps/`.

Esta Lexis existe para que **cenários Gherkin permaneçam documentação black-box** (per `lex-bdd-spec-only-sources` e `lex-bdd-gherkin-format`) e **a suite de testes continue sendo a suite de testes** — uma só, padrão, com rastreabilidade explícita ao cenário via convenção de nome.

## Lei

> **Testes que validam um cenário Gherkin DEVEM ser testes regulares (unit/integração/E2E) escritos no framework de testes que o projeto já usa (pytest, vitest, jest, junit, go test, etc.). O uso de qualquer step-runner BDD (behave, pytest-bdd, cucumber, jest-cucumber, lettuce, godog, specflow, gauge) é PROIBIDO. Cada cenário mapeia para um ou mais testes-padrão via referência `SCN-{N}` no nome ou docstring do teste; o arquivo de cenários é documentação, não cola executável.**

## Regras

### 1. Onde o cenário vive

Os cenários ficam em **um** dos formatos a seguir, ambos como documentação não executada por runner:

- `docs/issues/issue-{n}/07-bdd-scenarios.md` (consolidado, formato preferido).
- `docs/issues/issue-{n}/scenarios/*.feature` (um arquivo por `Feature`, quando o volume justifica).

Nenhum runner consome esses arquivos. São apenas Markdown/feature lidos por humanos e pelo `kata-bdd-validate-implementation`.

### 2. Onde o teste vive

Os testes que validam cenários ficam **na suite normal** do projeto:

- `tests/unit/`, `tests/integration/`, `tests/e2e/` (ou equivalente da stack), seguindo `lex-test-pyramid`.
- **NÃO** ficam em `features/`, `steps/`, `step_definitions/` ou diretório paralelo dedicado a BDD.

### 3. Rastreabilidade obrigatória

Cada teste que valida um cenário **DEVE** referenciar o id `SCN-{N}` em pelo menos um destes lugares:

- Nome da função/`it`/`describe`:
  - Python: `def test_scn_1_cliente_agenda_transferencia_valida():`
  - JS/TS: `it("SCN-1 cliente agenda transferência válida", () => { ... })`
  - Go: `func TestSCN1ClienteAgendaTransferenciaValida(t *testing.T) { ... }`
- Ou docstring/JSDoc do teste, quando o nome ficaria pesado:

```python
def test_agendamento_com_saldo_insuficiente():
    """Valida SCN-2 (AC-2): cliente tenta agendar sem saldo."""
```

Um teste **PODE** validar mais de um cenário (ex.: `"Valida SCN-3 e SCN-4"`); um cenário **PODE** ser validado por mais de um teste (ex.: SCN-1 unitário + SCN-1 integração).

### 4. Dependências proibidas

Os manifestos do projeto (`pyproject.toml`, `requirements*.txt`, `package.json`, `go.mod`, `pom.xml`, `*.csproj`, etc.) **NÃO PODEM** declarar:

- `behave`, `pytest-bdd`, `lettuce`, `radish-bdd`
- `cucumber`, `cucumber-js`, `@cucumber/cucumber`, `jest-cucumber`
- `specflow`, `reqnroll`
- `godog`
- `gauge`
- Qualquer outro step-runner BDD

### 5. Artefatos proibidos

**NÃO PODEM** existir no repositório:

- `features/*.feature` lidos por runner (cenários como documentação ficam em `docs/issues/...`).
- Diretórios `steps/`, `step_definitions/`, `support/world.js` etc. com glue para cenários.
- Decoradores/anotações `@given`, `@when`, `@then`, `@step` ligados a cenários.
- Arquivos de configuração `behave.ini`, `cucumber.json`, `cypress-cucumber-preprocessor` etc.

### 6. Projetos legados

Projetos pré-existentes com framework BDD entrincheirado **DEVEM**:

1. Registrar ADR com plano de remoção (per `kata-adr-write`).
2. Congelar criação de novos cenários executados pelo runner.
3. Migrar incrementalmente para testes-padrão com referência `SCN-{N}`.

Para código novo (PRs após esta Lexis vigorar), o Gate 3 bloqueia importações dos runners proibidos.

### 7. Onde mora o estilo do teste

A escolha do nível (unit/integração/E2E) e do estilo (mock, fixture, container) segue `lex-test-pyramid`, `lex-test-isolation`, `lex-python-testing`, `lex-frontend-testing` e a Codex aplicável. Esta Lexis não impõe nível — apenas exige que, qualquer que seja o teste escolhido, ele seja **um teste regular do framework do projeto** com referência `SCN-{N}`.

## Abrangência

- **Aplica-se a:** todo teste adicionado ou alterado durante a Fase 8 do fluxo Issue-Driven, e a todo teste novo criado em projetos sob esta Lexis.
- **Agentes vinculados:** `warrior-themis` (mapeia cenário↔teste), `warrior-apollo`/`warrior-hephaestus`/`warrior-iris` (quando implementam testes para preencher gap detectado).
- **Exceções:** Nenhuma. Projetos legados registram ADR de remoção; código novo não importa runner BDD.

## Consequências de Violação

1. **Gate 3 falha:** `kata-quality-gate` Check 8 detecta dependência de step-runner ou diretório `features/` executado, e bloqueia o PR.
2. **Teste não rastreável:** teste sem referência `SCN-{N}` correspondente não conta como cobertura BDD; cenário fica como gap em `08-bdd-validation-report.md`.
3. **Dívida de manutenção visível:** ADR de remoção mantém o débito explícito até a migração concluir.

## Exemplos

### Correto

```python
# tests/integration/test_transfer_scheduling.py
import pytest

@pytest.mark.asyncio
async def test_scn_1_cliente_agenda_transferencia_valida(client, db_session):
    """Valida SCN-1 (AC-1): cliente com saldo agenda transferência válida."""
    customer = await create_active_customer(db_session, balance=1000_00)
    response = await client.post("/v1/transfers", json={
        "amount": 100_00, "scheduled_for": "2026-04-30"
    })
    assert response.status_code == 201
    assert response.json()["data"]["status"] == "scheduled"
```

```
docs/issues/issue-42/07-bdd-scenarios.md   # cenário SCN-1 documentado
tests/integration/test_transfer_scheduling.py   # teste padrão com referência
pyproject.toml   # sem behave / pytest-bdd
```

### Incorreto

```
# pyproject.toml
[project.optional-dependencies]
test = ["pytest-bdd>=7.0"]   # ❌ runner BDD proibido

# features/transfer.feature   # ❌ feature consumida por runner

# tests/steps/transfer_steps.py
from pytest_bdd import given, when, then, scenario

@scenario("../../features/transfer.feature", "Cliente agenda transferência válida")
def test_agenda(): pass

@given("o saldo disponível é R$ 1.000,00")
def saldo_mil(db): ...   # ❌ glue paralelo

@when("o cliente agenda uma transferência de R$ 100,00 para amanhã")
def agenda(client): ...   # ❌ regex matchers
```

## Validação Automatizada

- **Ferramenta:** lint de dependências varrendo `pyproject.toml`/`requirements*.txt`/`package.json`/`go.mod`/etc. contra a lista proibida; lint de testes garantindo referência `SCN-{N}`; `kata-bdd-validate-implementation` produz `08-bdd-validation-report.md` com o mapeamento; `kata-quality-gate` Check 8 falha o gate em violação.
- **Momento:** Fase 8 do fluxo Issue-Driven (pré-PR), CI em todo PR que adicione/altere testes ou manifestos.
- **Métrica:** 0 dependências de step-runner BDD; 100% dos cenários com pelo menos um teste referenciando `SCN-{N}`.

## Referências

- `lex-bdd-spec-only-sources` — fontes permitidas para derivar cenários
- `lex-bdd-gherkin-format` — formato declarativo dos cenários
- `lex-test-pyramid` — distribuição de níveis de teste
- `lex-test-isolation` — independência entre testes
- `kata-bdd-validate-implementation` — procedimento de validação cenário↔teste
- `warrior-themis` — agente que orquestra a validação
