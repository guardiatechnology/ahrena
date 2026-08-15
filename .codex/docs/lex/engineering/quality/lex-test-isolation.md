# Lexis: Isolamento de Testes

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Garantia de que cada teste roda de estado conhecido, independente de ordem e paralelizável sem race condition

## Lei

> **Todo teste DEVE começar de estado conhecido, NÃO DEVE depender da ordem de execução, e DEVE ser capaz de rodar em paralelo com outros do mesmo tipo sem race condition. Dependências externas não determinísticas (relógio, rede, random, UUID) DEVEM ser parametrizadas ou mockadas. Testes flaky DEVEM ser corrigidos imediatamente ou desabilitados — nunca ignorados com retry.**

## Regras

### 1. Estado inicial conhecido

Cada teste **DEVE**:

- Começar com fixtures/factories explícitas — nunca depender de dados de teste anterior.
- Limpar estado após execução (truncate de tabelas, reset de caches, unmount de componentes).
- Usar transações + rollback quando possível (teste confirma, framework reverte).

**Antipattern:** `test_create_user` confia que `test_delete_user` não rodou ainda.

### 2. Independência de ordem

Rodar a suite em ordem **aleatória** (`pytest --randomly`, Jest `testSequencer: 'random'`) **DEVE** produzir o mesmo resultado. Falhas que aparecem só em ordem específica indicam acoplamento via estado compartilhado.

### 3. Paralelismo seguro

Testes do mesmo nível **DEVEM** ser paralelizáveis (`pytest -n auto`, Jest default). Se testes compartilham recurso (banco, porta, arquivo), **DEVEM** usar identificador único por worker (`pytest-xdist` worker id, schema por worker).

### 4. Mocks para não determinismo

| Fonte de não determinismo | Estratégia |
|---|---|
| Relógio (`datetime.now()`, `Date.now()`) | Injetar clock; fixar em teste com `freeze_time` |
| UUID / random | Seed fixo ou injeção |
| Rede externa (APIs pagas, serviços sem sandbox) | VCR / MSW / fixture; validar contrato separadamente |
| Filesystem compartilhado | `tempfile` / container por teste |
| Variáveis de ambiente | Set/unset em fixture setup/teardown |

### 5. Flaky = bug crítico

Um teste flaky:
- **DEVE** ser corrigido na sprint em que foi detectado.
- Enquanto aberto, **DEVE** ser marcado (`@pytest.mark.flaky` com motivo + ticket) e ter visibilidade.
- Nunca "tratar com retry" (`pytest-rerunfailures`) sem investigar causa raiz — retry é anestesia, não cura.

Exceções válidas para retry:
- Teste E2E contra serviço externo com latência real e acordo de SLA conhecido.
- Documentar o retry com comentário justificando.

### 6. Tempo de suite monitorado

- **Unit**: cada teste < 1s; suite total < 60s em máquina dev.
- **Integration**: cada teste < 10s; suite total < 5min em CI.
- **E2E**: cada jornada < 2min; suite total < 15min em CI.

Testes que excedem o budget do nível **DEVEM** ser movidos para nível superior (unit → integration) ou otimizados.

## Validação Automatizada

- **Ferramenta:**
  - `pytest --randomly-seed=random` (detecta dependência de ordem)
  - `pytest -n auto` / Jest paralelismo (detecta race conditions)
  - Rastreamento histórico de flakes no CI (GitHub Actions, CircleCI insights).
- **Momento:** toda execução de CI; relatório semanal de flakes.
- **Métrica:** 0 flaky ativos (sem ticket); >99% de determinismo na suite.
