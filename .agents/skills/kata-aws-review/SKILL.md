---
name: kata-aws-review
description: "Revisar Arquitetura ou IaC AWS. Revisão sistemática de arquitetura AWS ou mudanças de IaC (Terraform, CDK, CloudFormation) contra Lexis e Well-Architected Framework"
---

# Kata: Revisar Arquitetura ou IaC AWS

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Revisão sistemática de arquitetura AWS ou mudanças de IaC (Terraform, CDK, CloudFormation) contra Lexis e Well-Architected Framework

## Workflow

```
Progresso:
- [ ] 1. Coletar alvo e contexto
- [ ] 2. Revisar Security (lex-aws-security)
- [ ] 3. Revisar IaC (lex-aws-iac)
- [ ] 4. Revisar Cost (lex-aws-cost)
- [ ] 5. Revisar Reliability
- [ ] 6. Revisar Performance
- [ ] 7. Revisar Operational Excellence
- [ ] 8. Consolidar relatório por severidade
```

### Passo 1: Coletar alvo e contexto

Dependendo do tipo:

- **PR de IaC:** obter `git diff`; identificar recursos criados/modificados/removidos; stack (Terraform vs CDK vs CloudFormation).
- **Documento de arquitetura:** ler `03-architecture.md`; extrair componentes e escolhas.
- **Workload existente:** inventário via **Config**, **Resource Explorer**, tags.

Ler requisitos originais quando disponíveis para contextualizar decisões.

### Passo 2: Revisar Security

Contra `lex-aws-security`:

- [ ] IAM roles com menor privilégio? Sem `*:*` ou policies managed amplas?
- [ ] Acesso público bloqueado em S3, RDS, ElastiCache?
- [ ] Criptografia em repouso habilitada em S3/RDS/EBS/DynamoDB?
- [ ] Criptografia em trânsito (TLS 1.2+) em ALB/API Gateway?
- [ ] Segredos via Secrets Manager/Parameter Store? Sem hardcoded?
- [ ] CloudTrail habilitado multi-região?
- [ ] Security Groups sem `0.0.0.0/0` em portas administrativas?
- [ ] KMS CMKs em vez de AWS-managed onde apropriado?
- [ ] Rodar `tfsec` / `cdk-nag` e capturar findings

Severidade exemplo: S3 público sem justificativa → **crítica**; ausência de CloudTrail → **alta**; KMS AWS-managed em vez de CMK → **média**.

### Passo 3: Revisar IaC

Contra `lex-aws-iac`:

- [ ] Tudo como código (nenhuma criação manual no console)?
- [ ] State remoto com lock? Nunca em Git?
- [ ] Ambientes separados (workspaces/stacks distintas)?
- [ ] Tagging padronizado aplicado?
- [ ] Módulos versionados (sem `ref=main`)?
- [ ] Recursos críticos com `prevent_destroy` / `deletion_protection`?
- [ ] Segredos fora dos arquivos IaC versionados?
- [ ] Pipeline com `plan` visível em PR + apply automatizado?

### Passo 4: Revisar Cost

Contra `lex-aws-cost`:

- [ ] Tags de cost allocation presentes? (`CostCenter`, `Environment`, `Project`, `Owner`)
- [ ] Escolhas de compute apropriadas ao padrão de uso? (Lambda vs Fargate vs EC2)
- [ ] Storage classes adequadas? (S3 Standard vs IA vs Glacier com lifecycle)
- [ ] NAT Gateway compartilhado quando possível (não um por AZ sem necessidade)?
- [ ] Reservado/Savings Plan considerado para workload sustained?
- [ ] Retention em CloudWatch Logs definida?
- [ ] Budget configurado?
- [ ] Rodar `infracost` para estimar custo do diff

### Passo 5: Revisar Reliability

Contra `codex-aws-well-architected` (Pilar Reliability):

- [ ] Multi-AZ habilitado em RDS, ECS service, ElastiCache, NAT Gateway?
- [ ] Auto-scaling configurado com métricas adequadas?
- [ ] Health checks em ALB + Route 53?
- [ ] Backup automatizado via AWS Backup? Retenção coerente com RPO?
- [ ] DR plan: multi-region se tier-1? RTO/RPO documentados e testados?
- [ ] Dead-letter queues em filas e Lambda para evitar perda silenciosa?
- [ ] Circuit breakers ou retries com backoff nas integrações externas?

### Passo 6: Revisar Performance

Contra `codex-aws-well-architected` (Pilar Performance):

- [ ] Serviço escolhido é o certo para o padrão de tráfego?
- [ ] Instâncias right-sized (não super/sub-dimensionadas)?
- [ ] Cache (CloudFront, ElastiCache) para reduzir latência e carga no backend?
- [ ] VPC Endpoints para S3/DynamoDB para evitar NAT Gateway e melhorar latência?
- [ ] Auto-scaling reativo (ex.: target tracking) em vez de fixo?
- [ ] Graviton (ARM) considerado para workloads compatíveis?

### Passo 7: Revisar Operational Excellence

- [ ] Logs, métricas, traces configurados (CloudWatch, X-Ray)?
- [ ] Alarmes CloudWatch para eventos críticos (high error rate, latency breach)?
- [ ] Dashboards operacionais criados?
- [ ] Runbooks documentados para incidents previsíveis?
- [ ] Deploy com blue/green ou canary (CodeDeploy, ECS deployment controllers)?
- [ ] Rollback automático em caso de health check failure?

### Passo 8: Consolidar relatório por severidade

Estruturar achados:

```markdown
# AWS Architecture Review — {alvo}

- **Data:** {YYYY-MM-DD}
- **Escopo:** {componentes ou diff}
- **Achados:** {C} críticos, {A} altos, {M} médios, {B} baixos

## Resumo por Pilar

| Pilar | Críticos | Altos | Médios | Baixos |
|---|:-:|:-:|:-:|:-:|
| Security | 0 | 1 | 2 | 1 |
| Reliability | 0 | 0 | 1 | 0 |
| Performance | 0 | 0 | 0 | 2 |
| Cost | 0 | 1 | 3 | 2 |
| Operational | 0 | 0 | 1 | 0 |
| Sustainability | 0 | 0 | 0 | 1 |

## Achados Críticos

### A-1: S3 bucket público sem justificativa
- **Pilar:** Security
- **Local:** `infra/modules/assets/main.tf:42`
- **Problema:** `block_public_acls = false` e `block_public_policy = false`; bucket armazena dados internos
- **Recomendação:** habilitar `Block Public Access` e mover assets públicos para bucket dedicado com política explícita
- **Referência:** `lex-aws-security` §4

## Achados Altos

### A-2: ...

## Achados Médios

### A-3: ...

## Recomendações Adicionais (não bloqueantes)

- ...

## Resumo Positivo

{2-3 pontos bem executados}

## Estimativa de Custo (Infracost)

Mudança líquida: +US$ 420/mês
- +Aurora Serverless v2 baseline: +US$ 280
- +ALB: +US$ 22
- +NAT Gateway (new AZ): +US$ 32
- +Data transfer estimado: +US$ 86
```

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Relatório de revisão | Markdown estruturado | Resposta ao usuário ou `docs/reviews/{data}-aws-review.md` |
| Comentários em PR | Inline comments via GitHub MCP | PR (opcional) |
| Plano de melhoria | Lista priorizada de ações | Parte do relatório |

## Restrições

- **Revisão ≠ modificação:** este kata reporta; correções são feitas pelo DevOps/time responsável em nova iteração.
- **Severidade objetiva:** crítico = viola Lexis ou causa risco imediato; alto = contra Well-Architected; médio/baixo = melhoria incremental.
- **Evidência concreta:** cada achado tem local (arquivo:linha ou recurso) e referência a Lexis/Codex.
- **Tom construtivo:** apontar problema + solução; não é auditoria punitiva.
