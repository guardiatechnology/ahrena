---
name: kata-python-implement
description: "Implementação de Feature Python. Engineering — Backend: implementação end-to-end de um feature Python do requisito ao código testado, tipado e revisado"
---

# Kata: Implementação de Feature Python

> **Prefix:** `kata-` | **Type:** Habilidade Repetível | **Scope:** Engineering — Backend: implementação end-to-end de um feature Python do requisito ao código testado, tipado e revisado

## Workflow

```
Progress:
- [ ] 1. Entender o requisito e clarificar ambiguidades
- [ ] 2. Identificar camadas e arquivos afetados
- [ ] 3. Projetar interfaces (Protocols) e modelos de dados
- [ ] 4. Implementar lógica de domínio com testes unitários
- [ ] 5. Implementar adaptadores de infraestrutura com testes de integração
- [ ] 6. Implementar camada HTTP com testes de endpoint
- [ ] 7. Validação final (lint, tipos, testes)
```

### Step 1: Entender o Requisito e Clarificar Ambiguidades

1. Ler a descrição do feature e qualquer spec OAS ou documento de design referenciado
2. Identificar ambiguidades, casos extremos e suposições não declaradas
3. **Fazer perguntas esclarecedoras ao usuário** — ex.: comportamento esperado em erro? paginação necessária? requisitos de idempotência? padrões existentes a seguir?
4. Aguardar respostas antes de prosseguir. Repetir se surgirem novas ambiguidades
5. Resumir o requisito entendido em 2-3 frases para confirmação

### Step 2: Identificar Camadas e Arquivos Afetados

1. Mapear o feature para a arquitetura (codex-python-architecture):
   - **Domain:** novas entidades, value objects, exceções, ports, casos de uso?
   - **Infrastructure/Database:** novos modelos ORM, métodos de repositório, migrações?
   - **Infrastructure/HTTP:** novas rotas, schemas Pydantic, dependências?
   - **Shared:** nova instrumentação de telemetria?
2. Listar arquivos existentes que serão modificados e novos arquivos que serão criados
3. Verificar padrões existentes no codebase que este feature deve seguir

### Step 3: Projetar Interfaces e Modelos de Dados

1. Definir ou atualizar **entidades de domínio** como frozen dataclasses (lex-python-immutability)
2. Definir ou atualizar interfaces **Protocol** para quaisquer novos ports (repositórios, serviços externos)
3. Definir **modelos Pydantic** para schemas de request/response na fronteira HTTP
4. Todas as definições DEVEM ter type hints completos (lex-python-typing)
5. Apresentar o design de interface ao usuário se o feature for complexo; caso contrário, prosseguir

### Step 4: Implementar Lógica de Domínio com Testes Unitários

1. Implementar classes de **caso de uso** que orquestram a lógica de domínio
2. Escrever **testes unitários** para cada caminho de comportamento: happy path, casos extremos, casos de erro
3. Usar `pytest.parametrize` para múltiplos cenários sobre a mesma lógica
4. Usar **Hypothesis** para invariantes de domínio quando aplicável
5. Código de domínio NÃO DEVE importar de infraestrutura (codex-python-architecture)
6. Executar testes unitários para confirmar que passam

### Step 5: Implementar Adaptadores de Infraestrutura com Testes de Integração

1. Implementar métodos de **repositório** usando padrões async do SQLAlchemy 2.0 (codex-python-sqlalchemy)
2. Criar **migração Alembic** se mudanças de schema forem necessárias
3. Escrever **testes de integração** contra banco de dados real — sem mocks para BD (lex-python-testing)
4. Implementar quaisquer clientes de serviço externo com tratamento adequado de erros
5. Mapear entre modelos ORM e entidades de domínio no repositório
6. Executar testes de integração para confirmar que passam

### Step 6: Implementar Camada HTTP com Testes de Endpoint

1. Criar ou atualizar **router FastAPI** com o novo endpoint (codex-python-fastapi)
2. Conectar **injeção de dependências** para casos de uso e repositórios
3. Adicionar **exception handlers** se novas exceções de domínio foram introduzidas
4. Escrever **testes HTTP** verificando códigos de status, estrutura de response, payloads de erro
5. Adicionar spans customizados de **OpenTelemetry** para operações críticas do negócio se necessário (codex-python-observability)
6. Executar testes HTTP para confirmar que passam

### Step 7: Validação Final

Antes de entregar, verificar:

- [ ] Ruff passa sem erros (`ruff check .` e `ruff format --check .`)
- [ ] mypy strict passa sem erros (`mypy .`)
- [ ] Todos os testes passam (`pytest`)
- [ ] Novo código tem type hints completos (lex-python-typing)
- [ ] Sem segredos hardcoded ou entrada não validada (lex-python-security)
- [ ] Tratamento de erros usa exceções específicas (lex-python-error-handling)
- [ ] Dataclasses de domínio são frozen (lex-python-immutability)
- [ ] Mocks usados apenas nas fronteiras do sistema (lex-python-testing)
- [ ] Migração é reversível (tem `downgrade()`)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Implementação | Arquivos fonte Python | Diretórios de camada apropriados conforme codex-python-architecture |
| Testes | Arquivos de teste Python | `tests/unit/`, `tests/integration/`, `tests/property/` |
| Migração | Arquivo de migração Alembic | `alembic/versions/` (se houver mudanças de schema) |

## Execution Example

### Example Input

```
Feature: Adicionar endpoint para cancelar uma transação (soft delete). Setar discarded_at, emitir evento de cancelação.
Context: Seguir padrões existentes de transações. Spec OAS existe em docs/oas/transactions.yaml.
```

### Example Output (summary)

1. Domain: exceção `TransactionCancelledError`; método `cancel()` no caso de uso `TransactionService`
2. Repository: `SqlAlchemyTransactionRepository.soft_delete()` — seta `discarded_at` e incrementa `version`
3. Route: `DELETE /v1/transactions/{entity_id}` → 204; 404 se não encontrado; 409 se já cancelado
4. Tests: 8 testes (unitário: lógica de cancelamento, já cancelado, não encontrado; integração: soft delete no BD; HTTP: 204, 404, 409, auth ausente)
5. Migration: nenhuma (sem mudança de schema — coluna `discarded_at` já existe)

## Constraints

- Esta Kata produz código de implementação com testes — não design de API (kata-api-design-oas cuida disso)
- Seguir padrões do codebase existente sobre ideais teóricos
- Não refatorar código não relacionado durante a implementação do feature
- Escalar para humano quando decisões arquiteturais são necessárias (novo bounded context, novo limite de serviço)
