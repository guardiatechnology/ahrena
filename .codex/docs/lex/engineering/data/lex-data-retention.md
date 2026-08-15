# Lexis: Política de Retenção de Dados

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Armazenamento persistente de dados pessoais, transacionais, logs e artefatos — política de retenção definida por classe e enforced

## Lei

> **Toda classe de dado persistente DEVE ter política de retenção declarada em `docs/data-retention.yaml` com valor, justificativa legal/negócio, e mecanismo de enforcement. Dados pessoais DEVEM ser deletáveis por requisição do titular (LGPD Art. 18 / GDPR Art. 17) dentro do prazo legal. Logs que contêm PII DEVEM ter retenção específica, nunca `indefinite`.**

## Regras

### 1. Política declarada por classe

Estrutura em `docs/data-retention.yaml`:

```yaml
classes:
  - name: transactional-core
    description: "Transações de pagamento, refunds, ledger"
    retention: "7 years"
    legal_basis: "Lei 12.846/2013 (BR), SOX 17 CFR 240.17a-4 (if US)"
    storage: "Postgres primary; S3 Glacier after 1y for archive"
    enforcement: "postgres lifecycle job + S3 lifecycle policy"

  - name: pii-customer
    description: "Nome, CPF, email, telefone do cliente"
    retention: "while active + 5 years after last transaction"
    legal_basis: "LGPD Art. 16 — tratamento durante necessidade + defesa de direitos"
    deletion_policy: "upon user request OR auto after 5y inactivity"
    erasure_sla: "15 days from request (LGPD)"
    storage: "Postgres customer schema"

  - name: operational-logs
    description: "Logs de aplicação sem PII"
    retention: "90 days"
    storage: "CloudWatch Logs"

  - name: audit-logs
    description: "CloudTrail, application audit logs"
    retention: "7 years (SOC 2 / SOX)"
    storage: "S3 bucket imutável (Object Lock)"

  - name: cache
    description: "Redis / Memcached"
    retention: "ephemeral, TTL 24h default"
    storage: "ElastiCache"
```

### 2. Enforcement automatizado

Para cada classe, **DEVE** existir mecanismo automático de expiração:

- **Postgres**: `DELETE ... WHERE created_at < NOW() - INTERVAL 'X'` em cron/job.
- **S3**: Lifecycle policy com transição e expiration.
- **CloudWatch Logs**: `retentionInDays` no log group.
- **Redis**: TTL por key.

Retenção sem enforcement é política de prateleira.

### 3. Direito ao esquecimento (LGPD / GDPR)

O sistema **DEVE** suportar, para dados pessoais:

- **Exportação** (LGPD Art. 18 inciso VI): formato estruturado (JSON) consumível.
- **Exclusão** (LGPD Art. 18 inciso VI): anonimização ou hard delete.
  - Se apagar viola outro requisito (ex.: ledger precisa permanecer): anonimizar PII mantendo estrutura transacional.
- **SLA**: respeitado em todas as fontes (DB, backups de longo prazo, logs, analytics, caches).

Exclusão em backups é complexa: documentar política (ex.: "PII em backup é criptografado; chaves destruídas na expiração do backup") com legal.

### 4. Retenção de PII em logs

Logs **DEVEM** não conter PII quando possível (ver `lex-observability-required`). Se contêm:
- Retenção máxima: 90 dias (ou prazo legal mais curto aplicável).
- Redaction aplicada antes de persistir quando viável.

Logs em sistemas de terceiros (Datadog, Splunk) seguem a mesma regra.

### 5. Sem `retention: indefinite` sem justificativa

Categoria válida apenas para:
- **Audit logs exigidos por lei** (SOX 7 anos é "indefinite" do ponto de vista do app).
- **Dados de sistema** sem PII e com custo controlado (config, feature flags history).

Todo outro caso exige justificativa legal/negócio explícita.

### 6. Auditoria trimestral

Trimestralmente:
- Verificar que enforcement funcionou (amostras deletadas no prazo).
- Revisar crescimento de cada classe (storage = custo).
- Revalidar legal basis (mudanças em LGPD, contratos, políticas internas).

## Validação Automatizada

- **Ferramenta:**
  - Linter valida que `docs/data-retention.yaml` existe e lista todas as classes declaradas em schema de DB.
  - Check mensal: tamanho de cada classe vs. crescimento esperado.
  - Teste de end-to-end: criar usuário sintético, solicitar exclusão, verificar remoção em todas as fontes dentro do SLA.
- **Momento:** pre-deploy de novo domínio de dado; mensal/trimestral.
- **Métrica:** 100% de classes documentadas; 100% de requisições de exclusão dentro do SLA; crescimento mensal compatível com baseline.
