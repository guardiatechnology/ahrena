# Codex: Component Deployment — IaC, Tagging, Security

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — convenções internas do diretório `deployment/`

## Visão Geral

`deployment/` é o single source of IaC do bounded context. Materializa em AWS os components produtivos (`api`, `agents`, `jobs`, `ui`) e tudo que eles consomem (DB, queues, buckets, secrets, alarmes, dashboards). Não é "component produtivo" — não roda como aplicação — mas é obrigatório em todo bounded context, mesmo que mínimo. Este codex detalha estrutura, escolha de tooling IaC, tagging para cost allocation e a fronteira com Lexis AWS.

## Contexto

- **Domínio:** infraestrutura como código do bounded context
- **Público-alvo:** engenheiros de infra, Atlas quando delega IaC, revisores de PR de infra
- **Atualização:** mudança de tooling IaC (CDK ↔ Terraform), nova convenção de tagging, ADR de fronteira

## Stack canônico

| Camada | Ferramenta | Notas |
|--------|------------|-------|
| IaC primário | Um per bounded context: AWS CDK (Python ou TS) **ou** Terraform | Misturar IaC tools sem isolamento é proibido per `lex-aws-iac` |
| Linter IaC | `cdk-nag` (CDK) ou `tfsec` + `checkov` (Terraform) | Roda em CI |
| Estimativa de custo | `infracost` (Terraform) ou diff manual com Pricing Calculator (CDK) | Mudanças ≥ US$ 100/mês exigem ADR |
| Cost allocation | Tags obrigatórias per `lex-aws-cost` | Aplicadas globalmente via stack/module |
| Security | Per `lex-aws-security` — least privilege IAM, encryption in transit + at rest, no public defaults | — |

## Estrutura interna

```
deployment/
├── README.md
├── cdk/                        # se IaC=CDK
│   ├── app.py
│   ├── stacks/
│   │   ├── api_stack.py
│   │   ├── jobs_stack.py
│   │   ├── data_stack.py
│   │   └── monitoring_stack.py
│   ├── cdk.json
│   └── requirements.txt
│
# OU
│
├── terraform/                  # se IaC=Terraform
│   ├── main.tf
│   ├── modules/
│   │   ├── api/
│   │   ├── jobs/
│   │   └── data/
│   ├── environments/
│   │   ├── dev.tfvars
│   │   ├── staging.tfvars
│   │   └── prod.tfvars
│   └── backend.tf              # remote state com lock
│
├── policies/                   # IAM policies versionadas separadas
├── runbooks/                   # Linked em alarmes per lex-runbook-for-every-alert
└── tests/                      # Snapshot/integration tests (cdk-assertions, terraform-compliance)
```

Escolha CDK **ou** Terraform; não os dois no mesmo bounded context sem ADR.

## Padrões essenciais

1. **Remote state obrigatório.** Terraform: S3 + DynamoDB lock per `lex-aws-iac`. CDK: state gerenciado pelo CloudFormation.
2. **Tagging em todo recurso.** Mínimo: `Environment`, `Owner`, `Project`, `CostCenter`, `ManagedBy`, `Lifecycle` per `lex-aws-cost`. Aplicado globalmente (CDK `Tags.of`/Terraform `default_tags`).
3. **Least privilege IAM.** Roles dedicadas por function/handler; nada de `*:*` per `lex-aws-security`. Policies em `policies/` quando complexas.
4. **Encryption by default.** S3 SSE-KMS; RDS `storage_encrypted: true`; EBS `encrypted: true` per `lex-aws-security`.
5. **Public access bloqueado por default.** S3 `BlockPublicAccess`; RDS `publicly_accessible: false`; SGs restritivos.
6. **Alarmes com runbook.** Todo alarme CloudWatch que paga ser humano tem `runbook_url` apontando para `deployment/runbooks/` per `lex-runbook-for-every-alert`.
7. **Drift detection.** Plan automático nas PRs (`terraform plan` ou `cdk diff`); drift detection cron em produção.

## Fronteira com outros components

| Pode | Não pode |
|------|----------|
| Provisionar tudo que `components/{api,agents,jobs,ui}` consome | Hospedar lógica de aplicação |
| Definir secrets em Secrets Manager (referenciados pelos components) | Hardcoded valor de secret em IaC (per `lex-aws-security`) |
| Coordenar deploy/rollback entre components do mesmo bounded context | Modificar infra de outro bounded context |
| Configurar alarmes que monitoram components | Carregar regras de negócio |

## Anti-padrões

| Anti-padrão | Caminho correto |
|-------------|-----------------|
| Console changes em produção | IaC apenas; console só em incidente declarado per `lex-aws-iac` |
| Mix CDK + Terraform sem isolamento | Um per bounded context; ADR se houver exceção |
| Sem tags de cost allocation | Tags via default global; revisão de PR pega |
| Backup/snapshot manual | Backup plan no IaC (AWS Backup, RDS automated snapshots) |
| Alarme novo sem runbook linkado | Per `lex-runbook-for-every-alert` — bloqueia PR |
| Estimativa de custo ausente em mudança ≥ US$ 100/mês | Per `lex-aws-cost` — incluir Infracost output ou diff manual no PR |

## Referências

- `codex-component-architecture` — fronteiras gerais; deployment como obrigatório
- `lex-aws-iac` — IaC versionada, remote state, drift, segregação de tools
- `lex-aws-cost` — tagging, budgets, right-sizing, padrões a evitar
- `lex-aws-security` — IAM, encryption, secrets, public access, audit
- `lex-runbook-for-every-alert` — alarmes que paginam humano linkam runbook
- `lex-slo-required` — tier-1/2 declara SLO antes de go-live (vive em `docs/slo/`)
- `lex-data-retention` — políticas de retenção referenciadas no IaC (lifecycle S3, RDS retention)
- `codex-aws-services`, `codex-aws-well-architected`
- `references.component_template_repo.url` em `.ahrena/.directives` — layout exato do template externo
