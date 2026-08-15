---
name: kata-feature-design-docs
description: "Criar e Atualizar Documentos de Design de Feature. Plataforma Guardia — produção dos documentos entities/, oas/ e events/ em docs/{context}/ durante o ciclo de design de feature"
---

# Kata: Criar e Atualizar Documentos de Design de Feature

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Plataforma Guardia — produção dos documentos `entities/`, `oas/` e `events/` em `docs/{context}/` durante o ciclo de design de feature

## Fluxo de Trabalho

```
Progresso:
- [ ] 1. Ler Lexis e Codex aplicáveis
- [ ] 2. Resolver path canônico
- [ ] 3. Garantir estrutura de pastas
- [ ] 4. Aplicar template da categoria
- [ ] 5. Verificar conformidade
- [ ] 6. Gravar ou atualizar arquivo
- [ ] 7. Atualizar referências cruzadas
- [ ] 8. Validação final
```

### Passo 1: Ler Lexis e Codex Aplicáveis

1. Consultar **`lex-feature-design-docs`** — estrutura `docs/{context}/{categoria}/` é obrigatória; categorias são fixas
2. Consultar **`codex-feature-design-docs`** — template específico da categoria que será produzida
3. Para `entities/`: consultar adicionalmente `lex-entities`, `lex-entity-naming`, `codex-entities`
4. Para `oas/`: consultar adicionalmente `codex-oas-structure`, `codex-restful-payload`, `codex-restful-headers`, `codex-restful-pagination`, `codex-restful-status-codes`
5. Para `events/`: consultar adicionalmente `lex-cloudevents`, `codex-cloudevents`, `lex-idempotency`, `lex-entity-naming`

### Passo 2: Resolver Path Canônico

1. Converter o Bounded Context para kebab-case:
   - `ScheduledPayments` → `scheduled-payments`
   - `BankingIntegration` → `banking-integration`
2. Compor o diretório base: `docs/{context-kebab}/`
3. Compor o path final por categoria:
   - `entities`: `docs/{context}/entities/{entity-name-kebab}.md` (1 arquivo por entidade)
   - `oas`: `docs/{context}/oas/openapi.yaml` (ou `openapi-{slug}.yaml` se múltiplas APIs)
   - `events`: `docs/{context}/events/events.md` (1 arquivo por contexto)

### Passo 3: Garantir Estrutura de Pastas

1. Verificar se `docs/{context}/` existe; criar se não existir
2. Verificar se a subpasta da categoria existe; criar se não existir
3. **Não criar** subpastas de categorias reservadas (`agents/`, `metrics/`) sem instrução explícita
4. **Não criar** categorias fora do conjunto canônico — fazer isso é violação de `lex-feature-design-docs`

### Passo 4: Aplicar Template da Categoria

Carregar o template correspondente do `codex-feature-design-docs` e preencher:

#### Categoria `entities`

1. Cabeçalho com **Classificação DDD**: Entity, Aggregate Root ou Value Object
2. **Bounded Context** e **entity_type** (snake_case) no cabeçalho
3. Seção **Por que existe** — 2 a 4 frases sobre o motivo de negócio
4. Seção **Campos** — tabela com colunas `Campo | Tipo | Tamanho | Obrigatório | Descrição`. Sempre incluir os campos da estrutura base (`entity_id`, `entity_type`, `version`, `created_at`, `updated_at`, `discarded_at`) e em seguida os campos de negócio
5. Seção **Regras de Negócio** — lista numerada (RN-1, RN-2, ...) em linguagem de domínio
6. Seção **Invariantes** — condições sempre verdadeiras
7. Seção **Relações** — tabela `Relação | Cardinalidade | Tipo | Entidade Alvo | Observação`
8. Seção **Erros** — tabela com `code`, `reason`, `message`, quando ocorre, conforme `lex-error-handling`
9. Seção **Referências** — links para `events/events.md`, `oas/openapi.yaml` e Lexis aplicáveis

#### Categoria `oas`

1. Estruturar OpenAPI 3.x conforme `codex-oas-structure`
2. `info.title`, `info.version`, `info.description` apontando para o Bounded Context
3. `tags` por entidade
4. `paths` ordenados por recurso, com operações na ordem `POST → GET (list) → GET (item) → PATCH → DELETE`
5. `components.schemas` reutilizáveis derivados das entidades em `docs/{context}/entities/`
6. `components.parameters` para paginação canônica (`page_size`, `page_token`)
7. `components.securitySchemes` (Bearer JWT) conforme `lex-auth`
8. Cabeçalhos obrigatórios (`Idempotency-Key`, `X-Grd-Trace-Id`) declarados em parâmetros reutilizáveis

#### Categoria `events`

1. Cabeçalho com Bounded Context e segmento `{module}` do CloudEvents
2. Seção **Visão Geral**
3. Seção **Catálogo** — tabela `entity_type | event_name | type completo | Publicador | Consumidores`
4. **Uma seção por entidade** que emite eventos:
   - Subseção **Ciclo de Vida** com `mermaid` `stateDiagram-v2` cobrindo todos os estados possíveis e transições
   - Subseção **Eventos** — para cada evento:
     - Bloco JSON com payload completo conforme `codex-cloudevents` (`specversion`, `id`, `source`, `type`, `subject`, `time`, `datacontenttype`, `idempotencykey`, `data`)
     - Tabela de campos do `data`: `Campo | Tipo | Obrigatório | Descrição`
     - Linhas finais com **Idempotência** e **Trigger** (Use Case que dispara)
5. Seção **Referências**

### Passo 5: Verificar Conformidade

Antes de gravar:

- [ ] Path está exatamente em `docs/{context}/{categoria}/...`?
- [ ] Nome de arquivo respeita as convenções (`{entity-name}.md`, `openapi.yaml`, `events.md`)?
- [ ] Categoria pertence ao conjunto canônico (`entities`, `oas`, `events`)?
- [ ] Conteúdo segue o template correspondente do `codex-feature-design-docs`?
- [ ] Para `entities`: todas as 7 seções obrigatórias estão presentes (Classificação DDD, Por que existe, Campos, Regras de Negócio, Invariantes, Relações, Erros, Referências)?
- [ ] Para `entities`: a tabela de Campos inclui a estrutura base do `lex-entities`?
- [ ] Para `oas`: arquivo é YAML válido e segue `codex-oas-structure`?
- [ ] Para `events`: cada entidade tem `stateDiagram-v2` e cada evento tem payload CloudEvents completo?
- [ ] Para `events`: todos os tipos seguem `event.guardia.{module}.{entity_type}.{event_name}` em snake_case (lex-entity-naming)?

### Passo 6: Gravar ou Atualizar Arquivo

1. Em **`create`**: gravar o arquivo no path resolvido
2. Em **`update`**:
   - Ler o arquivo existente
   - Identificar seções que mudaram (novos campos, novos eventos, novos endpoints) e seções estáveis (descrições, referências cruzadas)
   - Mesclar preservando comentários humanos quando possível; substituir tabelas e blocos canônicos pelas versões novas
   - Não silenciosamente remover seção que existia — sinalizar mudança ao usuário se a remoção for intencional
3. Não gravar arquivo vazio ou com placeholders `{...}` não preenchidos

### Passo 7: Atualizar Referências Cruzadas

Quando a categoria afeta outra:

| Mudança | Atualizar |
|---------|-----------|
| Novo evento de uma entidade | `entities/{entity}.md` (seção Referências) e `events/events.md` (catálogo) |
| Novo campo em entidade | `oas/openapi.yaml` (schema) e `events/events.md` (payload se relevante) |
| Novo endpoint REST | `entities/{entity}.md` (seção Referências) |
| Renomeação de entidade | nome do arquivo, `entity_type`, schemas OAS, segmento `{entity_type}` em todos os tipos CloudEvents |

### Passo 8: Validação Final

- [ ] Arquivo gravado em path canônico (`docs/{context}/{categoria}/...`)
- [ ] Conformidade com template do `codex-feature-design-docs` confirmada
- [ ] Referências cruzadas atualizadas onde aplicável
- [ ] Lexis aplicáveis (`lex-feature-design-docs`, `lex-entities`, `lex-entity-naming`, `lex-cloudevents`, `lex-idempotency`, `lex-error-handling`) respeitadas
- [ ] Idioma confere com `language.default` em `.ahrena/.directives`

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Arquivo de entidade | Markdown | `docs/{context}/entities/{entity-name}.md` |
| Especificação OpenAPI | YAML | `docs/{context}/oas/openapi.yaml` |
| Documento de eventos | Markdown | `docs/{context}/events/events.md` |

## Exemplo de Execução

### Input

```
Bounded Context: ScheduledPayments
Categoria: entities
Operação: create
Conteúdo:
  Entidade: ScheduledTransfer (Aggregate Root)
  entity_type: scheduled_transfer
  Por que existe: separa intenção de execução de transferências bancárias com aprovação obrigatória
  Campos de negócio: scheduled_date (date), amount (integer cents), currency (ISO 4217), source_account_id (UUID), target_account_id (UUID), status (enum), approver_id (UUID, nullable)
  Regras: agendamento até 90 dias úteis no futuro; só admin aprova; não permite execução sem approval
```

### Output Resumido

Arquivo `docs/scheduled-payments/entities/scheduled-transfer.md`:

```markdown
# Entity: ScheduledTransfer

> **Classificação DDD:** Aggregate Root
> **Bounded Context:** scheduled-payments
> **entity_type:** `scheduled_transfer`

## Por que existe

Representa uma transferência bancária ordenada por um contador para execução em data futura. Existe para separar a intenção (agendamento) da execução (processamento) e permitir o ciclo de aprovação obrigatória por supervisor antes que valores se movam.

## Campos

| Campo | Tipo | Tamanho | Obrigatório | Descrição |
|-------|------|---------|:-----------:|-----------|
| `entity_id` | UUID v7 | 36 | Sim | Identificador único |
| `entity_type` | string | — | Sim | Sempre `scheduled_transfer` |
| `version` | integer | — | Sim | Versão otimista |
| `created_at` | datetime | — | Sim | Criação |
| `updated_at` | datetime | — | Sim | Última atualização |
| `discarded_at` | datetime | — | Não | Soft delete |
| `scheduled_date` | date | — | Sim | Data agendada (≤ 90 dias úteis no futuro) |
| `amount` | integer | — | Sim | Valor em centavos |
| `currency` | string | 3 | Sim | ISO 4217 |
| `source_account_id` | UUID v7 | 36 | Sim | Conta de origem |
| `target_account_id` | UUID v7 | 36 | Sim | Conta de destino |
| `status` | enum<requested,approved,executed,failed,cancelled> | — | Sim | Estado atual |
| `approver_id` | UUID v7 | 36 | Não | Supervisor que aprovou |

## Regras de Negócio

1. **RN-1 — Janela de agendamento:** `scheduled_date` deve ser dia útil em até 90 dias no futuro.
2. **RN-2 — Aprovação obrigatória:** Transição `requested → approved` exige `approver_id` com perfil supervisor.
3. **RN-3 — Execução condicionada:** Transição para `executed` só ocorre a partir de `approved`.

## Invariantes

- **INV-1:** `amount > 0`.
- **INV-2:** `status` segue exatamente as transições do diagrama em `events/events.md`.
- **INV-3:** Após `executed`, a entidade é imutável exceto `updated_at`.

## Relações

| Relação | Cardinalidade | Tipo | Entidade Alvo | Observação |
|---------|---------------|------|---------------|------------|
| references | N..1 | referência | `Account` | source e target |
| owns | 1..N | composição | `TransferApproval` | trilha de aprovação |

## Erros

| Code | Reason | Mensagem | Quando ocorre |
|------|--------|----------|---------------|
| `ERR400_INVALID_PARAMETER` | `INVALID_SCHEDULED_DATE` | "scheduled_date must be a future business day within 90 days" | RN-1 |
| `ERR403_FORBIDDEN` | `APPROVER_NOT_AUTHORIZED` | "approver does not have supervisor role" | RN-2 |
| `ERR409_CONFLICT` | `INVALID_STATE_TRANSITION` | "transfer cannot move from {from} to {to}" | INV-2 |

## Restrições

- Este Kata **não** decide o conteúdo do design — entrega o documento conforme o input já produzido pelo warrior responsável (Theseus, Daedalus, Kronos)
- **Nunca** salvar fora de `docs/{context}/{categoria}/` — viola `lex-feature-design-docs`
- **Nunca** usar paths configuráveis como `paths.domain`, `paths.oas`, `paths.events` — esses paths não existem mais em `.ahrena/.directives`
- **Nunca** misturar duas categorias em um mesmo arquivo (ex.: payload de evento dentro de `entities/{e}.md`)
- Quando `update` apaga uma seção que existia, **sinalizar ao usuário** antes de gravar
- Idioma do documento conforme `language.default` em `.ahrena/.directives`
