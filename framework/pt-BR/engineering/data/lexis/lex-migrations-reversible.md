# Lexis: Migrações Reversíveis ou com Plano de Rollback

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Migrações de schema de banco de dados (relacional ou NoSQL) em qualquer ambiente persistente

## Propósito

Migrações sem rollback viram bomba-relógio: quando o deploy correspondente falha ou regride, o schema avançou mas o código anterior não entende mais. A equipe fica presa — pode só avançar, nunca recuar. Pior: migrações destrutivas (DROP COLUMN, DROP TABLE) sem backup ou plano detalhado podem apagar dados irrecuperáveis em minutos.

Esta Lexis existe para garantir que **toda migração seja reversível automaticamente** (via `down` em Alembic, `migrate:rollback` em Django etc.) **OU tenha plano de rollback manual documentado** com verificação de backup antes de qualquer mudança destrutiva.

## Lei

> **Toda migração de schema DEVE ser reversível automaticamente pelo framework de migrações OU ter plano de rollback manual documentado e testado. Migrações destrutivas (DROP, ALTER que perde dados) DEVEM ter backup validado nos 24h anteriores e janela de manutenção declarada. Deploys de código DEVEM ser compatíveis com schema anterior E novo (expand-contract) em sistemas com rolling deploy.**

## Regras

### 1. Reversibilidade automática por padrão

Migrações aditivas (CREATE TABLE, ADD COLUMN NULLABLE, CREATE INDEX CONCURRENTLY) **DEVEM** ter `down` implementado:

```python
# Alembic
def upgrade():
    op.add_column("refund", sa.Column("notes", sa.String(500), nullable=True))

def downgrade():
    op.drop_column("refund", "notes")
```

Se o framework de migrações gera `down` automaticamente, aceitar; senão, escrever manualmente.

### 2. Migrações destrutivas: plano + backup

Para `DROP TABLE`, `DROP COLUMN`, `ALTER TYPE` com loss of data, `RENAME` em produção:

1. **Backup point-in-time** confirmado nas últimas 24h (via AWS Backup, pg_dump, etc.).
2. **Janela de manutenção** declarada com stakeholders quando tier-1.
3. **Plano de rollback manual** escrito:
   - Como restaurar a partir do backup.
   - Quanto tempo leva.
   - Qual é o ponto sem retorno (after this, rollback is only via restore-from-backup).
4. **Teste em staging** com volume representativo, medindo duração.

### 3. Expand-Contract para rolling deploys

Quando o sistema usa rolling deploy (N pods, deploy gradual):

- **Fase Expand**: migration adiciona estrutura nova mantendo a antiga. Deploy de código usa ambas.
- **Fase Contract**: migration remove estrutura antiga. Deploy usa apenas a nova.

Ex.: renomear coluna `status` → `state`:

| Passo | Migration | Código |
|---|---|---|
| 1 (expand) | `ADD COLUMN state` + trigger copia `status` → `state` | Lê de `state`, escreve em `state` E `status` |
| 2 | — | Lê e escreve apenas em `state` |
| 3 (contract) | `DROP COLUMN status` + trigger | — |

Um deploy atômico que muda schema + código simultaneamente **quebra** em rolling deploy.

### 4. Migrações de longa duração requerem estratégia

Queries que escaneiam tabelas grandes (> 1M rows) podem bloquear:

- `ADD COLUMN NOT NULL DEFAULT 'x'` em PostgreSQL lockeia tabela → usar `ADD COLUMN` nullable, backfill em batches, depois `SET NOT NULL`.
- `CREATE INDEX` sem `CONCURRENTLY` lockeia writes → sempre usar `CONCURRENTLY` (fora de transação).
- `ALTER COLUMN TYPE` (com rewrite) em tabela grande → avaliar pg_repack, tabelas shadow, ou aceitar janela.

Migration longa **DEVE** declarar estimativa de duração e estratégia em comentário no topo.

### 5. Sem DDL em transação compartilhada com DML

Nunca colocar DDL (CREATE, ALTER) e DML (INSERT, UPDATE) massivo na mesma migration. DDL pode ser reversível; DML de dados reais exige plano separado.

### 6. Teste de restore periódico

Backup sem teste de restore é backup inútil. **Trimestralmente** (ou por SOX/SOC 2):
- Executar restore em ambiente de staging a partir de backup de produção.
- Medir tempo; validar dados.
- Se falha → P0; backup strategy quebrada.

## Abrangência

- **Aplica-se a:** toda migração em ambiente compartilhado (staging, produção). Sandbox pessoal fica fora do enforce.
- **Agentes vinculados:** `warrior-demeter`, `warrior-apollo` (quando escreve migration), `warrior-atlas` (quando configura backup).
- **Exceções:** Nenhuma. Migrações em sandbox devem ainda seguir a estrutura mesmo sem enforcement.

## Consequências de Violação

1. **Lock inesperado em produção:** tabela lockeada 30min em horário de pico → downtime visível ao cliente.
2. **Perda de dados:** `DROP COLUMN` sem backup ou com backup antigo → dados irrecuperáveis.
3. **Deploy irreversível:** feature deploy quebra, mas schema avançou; não há como recuar; fix emergencial.
4. **Remediação:**
   - Audit trail: `pg_locks`, CloudTrail, logs do migration tool.
   - Restore de backup se dados perdidos.
   - Post-mortem blameless (`kata-postmortem-write`).
   - Ação corretiva: checklist em PR de migration; approval automatizado bloqueia até checklist preenchido.

## Validação Automatizada

- **Ferramenta:**
  - Lint em migrations (ex.: `squawk` para PostgreSQL): detecta patterns perigosos (`ADD COLUMN NOT NULL DEFAULT`, `CREATE INDEX` sem CONCURRENTLY).
  - Check em PR que `down` está implementado em toda migration.
  - Test run em CI: `upgrade` + `downgrade` em teste DB.
- **Momento:** em cada PR que contém migration; trimestral (restore test).
- **Métrica:** 100% de migrations com `down` ou plano documentado; 0 `ADD COLUMN NOT NULL DEFAULT` em tabelas > 10k rows sem estratégia multi-step.

## Referências

- `codex-data-modeling` — padrões de design prévio
- `codex-migrations-strategy` — playbooks detalhados
- `warrior-demeter` — conduz migrações complexas
- [Safer ActiveRecord Migrations](https://github.com/ankane/strong_migrations)
- [Alembic Best Practices](https://alembic.sqlalchemy.org/en/latest/tutorial.html#running-our-first-migration)
