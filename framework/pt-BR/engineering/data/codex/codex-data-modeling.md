# Codex: Modelagem de Dados

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Padrões de modelagem de dados para persistência — entidades, value objects, aggregates, normalização, evolução de schema, escolha entre relacional e NoSQL

## Visão Geral

Este Codex é a referência para **decisões de modelagem de dados** em projetos Ahrena. Consultado por `warrior-demeter` ao desenhar schema novo, por `warrior-apollo` quando precisa decidir estrutura de tabela, e por `warrior-atlas` quando escolhe entre RDS, Aurora, DynamoDB.

## Contexto

- **Domínio:** design de modelo de dados — relacional, NoSQL, mistos
- **Público-alvo:** `warrior-demeter`, agentes que persistem dados, revisores de PR com migrations
- **Atualização:** quando padrões de DDD evoluem, novos serviços de DB são adotados, ou quando regulação muda (LGPD, GDPR)

## Conteúdo

### Entidade vs. Value Object vs. Aggregate

**Entidade**: tem identidade única (`entity_id`), muda ao longo do tempo.
- Ex.: `User`, `Refund`, `Account`.
- Tem primary key; participa de FKs.

**Value Object**: imutável, definido por seus valores.
- Ex.: `Money(amount, currency)`, `Address`, `Email`.
- Stored as embedded columns (`amount_cents` + `currency_code`) ou JSON.

**Aggregate**: boundary de consistência transacional.
- Ex.: `Order` (raiz) com `OrderItems`.
- Mudanças a partir de aggregate root; invariantes mantidas juntas.
- Mapa natural para transação de DB.

Regra: prefira **aggregates pequenos** — um aggregate grande reduz concorrência.

### Base de atributos em entidade Ahrena

Toda entidade persistente segue `codex-entities`:

| Campo | Tipo | Propósito |
|---|---|---|
| `entity_id` | UUID v4 | Identificador estável (nunca reusar) |
| `entity_type` | string | Polimorfismo e auditoria |
| `version` | int | Otimistic locking; incrementa em cada update |
| `created_at` | timestamp | Imutável após create |
| `updated_at` | timestamp | Atualizado a cada mudança |
| `created_by` | UUID (ref user) | Ator que criou |
| `updated_by` | UUID (ref user) | Ator da última mudança |

Deleção lógica: campo `discarded_at` (timestamp nullable) em vez de DELETE físico, exceto quando compliance exige purge.

### Normalização — quando e quanto

- **3NF** como default para OLTP: evita inconsistência, facilita UPDATE.
- **Denormalização seletiva** para read paths críticos:
  - Contadores (`total_refunds`) materializados com trigger ou job.
  - Views materializadas para reports.
  - Cache (Redis) para lookups frequentes.
- **OLAP**: snowflake/star schema; diferente do OLTP.
- **Avoid**: campos CSV em string, arrays abusivos, JSON onde coluna explícita caberia.

### Relacional vs. NoSQL

**Relacional (Postgres, Aurora) quando:**
- Transações ACID sobre múltiplas entidades.
- Queries ad-hoc com JOINs.
- Consistência forte é requisito.
- Domínio tem relações complexas.

**DynamoDB quando:**
- Access patterns conhecidos e estáveis.
- Escala massiva e previsível.
- Latência sub-10ms exigida.
- Domínio é chave-valor ou hierárquico simples.

**DocumentDB / MongoDB quando:**
- Schema evolui rapidamente (documentos flexíveis).
- Dados agregados por natureza (um doc contém o aggregate).
- Queries flexíveis sobre documentos.

**Time-series DB (Timestream, InfluxDB) quando:**
- Append-heavy, queries por janela temporal.
- Métricas, eventos, IoT.

Documentar a escolha em ADR (`kata-adr-write`) quando não trivial.

### Índices

- **Toda FK** tem índice (a menos que prova de que nunca é usada em query).
- **Queries frequentes** definem índices compostos; analisar `EXPLAIN`.
- **Índices em timestamps** para ranges (`created_at DESC`).
- **Índices parciais** para consultas filtradas (`WHERE status = 'active'`).
- **Limite**: 5-7 índices por tabela grande. Cada índice custa em writes.

Revisar índices trimestralmente: `pg_stat_user_indexes` para detectar não usados.

### Migrations (expand-contract)

Ver `lex-migrations-reversible`. Padrão típico:

1. **Expand**: ADD COLUMN nullable + código escreve em ambos (novo + velho).
2. **Backfill**: job migra dados históricos em batches.
3. **Cut-over**: código passa a ler só do novo.
4. **Contract**: DROP COLUMN antigo.

Migration destrutiva sem esse padrão = downtime.

### Particionamento

Quando tabela chega a ~100M+ rows ou contém séries temporais longas:

- **Range partitioning** por `created_at` (month/year): queries recentes rápidas; arquivo antigo em particionsseparadas.
- **Hash partitioning** por `tenant_id`: multi-tenant isolation.
- **List partitioning** por categoria fechada.

Postgres Partitioning nativo > particionamento em application layer.

### Soft delete vs. hard delete

**Soft delete** (`discarded_at` timestamp):
- Preserva histórico.
- Permite undo.
- Complica queries (todo WHERE filtra `discarded_at IS NULL`).

**Hard delete** (DELETE físico):
- Obrigatório para dados sujeitos a LGPD com deletion request.
- Exige plano de auditoria (CloudTrail, audit log separado).

Escolher em função do domínio — documentar decisão.

### Eventual consistency

Em sistemas distribuídos (CQRS, event sourcing, multi-region):

- Aceitar que read model fica eventualmente consistente.
- Declarar **consistency guarantees** por use case (read-after-write na mesma conta? ou é aceitável ler versão anterior por alguns segundos?).
- Evitar mix sem intenção: transação escreve e evento é lido sync → risco de race.

### LGPD / GDPR desde o design

- **Classificar dados** ao criar tabela: qual coluna contém PII?
- **Minimizar**: só persistir o necessário.
- **Criptografar em repouso** (default via KMS em RDS/Aurora).
- **Acesso auditado**: queries sobre PII logged.
- **Retenção**: declarada em `docs/data-retention.yaml` (`lex-data-retention`).
- **Exportação e exclusão**: endpoints prontos desde o dia 1.

## Referências

- `lex-migrations-reversible`, `lex-data-retention`
- `codex-entities` — base de entidades Ahrena
- `codex-migrations-strategy` — playbooks de migration
- `warrior-demeter`
- [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)
- [PostgreSQL Indexes](https://www.postgresql.org/docs/current/indexes.html)
