# Lexis: Consciência de Custo em AWS

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Design e operação de infraestrutura AWS com atenção ao custo — tagging, right-sizing, monitoramento de gasto, prevenção de surpresas

## Propósito

AWS cobra pelo que é provisionado, não pelo que é usado — uma instância `r6i.4xlarge` ligada no fim de semana gera US$ 800/mês mesmo ociosa. Sem disciplina de custo, é trivial provisionar arquiteturas que funcionam mas sangram dinheiro: instâncias superdimensionadas, dados em S3 Standard quando deveriam estar em Glacier, DynamoDB em modo on-demand para workload previsível, NAT Gateways em cada AZ sem necessidade. Agentes IA que projetam AWS precisam incluir o eixo de custo junto com performance e segurança.

Esta Lexis existe para garantir que **todo recurso seja tagueado para cost allocation**, que **escolhas tenham consciência de custo explícita**, que **budgets e alarmes estejam configurados** e que **uso seja revisado periodicamente para right-sizing**.

## Lei

> **Toda arquitetura AWS DEVE ser projetada com consciência de custo explícita. Todo recurso DEVE ter tags de cost allocation (`CostCenter`, `Environment`, `Project`, `Owner`). Budgets com alertas DEVEM ser configurados por ambiente. Escolhas com impacto de custo >US$ 100/mês DEVEM ser documentadas com alternativas consideradas.**

## Regras

### 1. Tagging para cost allocation

Todo recurso taxável **DEVE** ter tags mínimas:

```hcl
tags = {
  CostCenter  = "engineering" | "product" | "marketing" | ...
  Environment = "dev" | "staging" | "prod"
  Project     = "ahrena" | "refund-service" | ...
  Owner       = "team-name@guardia.com"
}
```

1. **Cost allocation tags** habilitadas no Billing Console.
2. **Cost Explorer** configurado para detalhamento por tag.
3. **Reports mensais** por `CostCenter` e `Environment`.
4. Recursos **sem tags** em produção são bloqueados por SCP ou Config Rule.

### 2. Escolhas com consciência de custo

Ao escolher recursos, o agente **DEVE** considerar:

| Decisão | Questão de custo |
|---|---|
| Compute: EC2 vs. Lambda vs. Fargate vs. EKS | Qual é o padrão de uso? Sustained → EC2 reservado. Bursty/sparse → Lambda. Container consistent → Fargate. Orchestration complexa → EKS |
| Storage: S3 Standard vs. IA vs. Glacier vs. Deep Archive | Frequência de acesso? Standard para <30 dias; IA 30-90; Glacier >90 com retrieve esporádico; Deep Archive para compliance |
| DB: RDS on-demand vs. reserved; DynamoDB on-demand vs. provisioned | Workload previsível → reserved/provisioned (até 60% economia); imprevisível → on-demand |
| Network: NAT Gateway vs. NAT Instance vs. VPC Endpoints | NAT Gateway é caro (~US$ 32/mês/AZ + transfer); usar VPC endpoints para S3/DynamoDB; consolidar NAT quando tráfego permite |
| Data Transfer | Cross-AZ, cross-region e egress para internet têm custos distintos; evitar tráfego desnecessário entre AZs |

Decisões com impacto previsto **>US$ 100/mês** devem ser registradas (ADR quando estruturalmente relevante — ver `codex-issue-workflow`).

### 3. Budgets e alarmes

Cada conta/ambiente **DEVE** ter:

1. **AWS Budgets** configurado com:
   - Budget mensal por `Environment` (prod, staging, dev)
   - Alertas em 50%, 80%, 100% do limite
   - Alertas em 50%, 80%, 100% do **forecast** (previsão de mês fechado)
2. **Anomaly Detection** habilitado (AWS Cost Anomaly Detection).
3. **CloudWatch billing alarm** para spike geral (ex.: >20% vs mês anterior).
4. Alertas vão para canal do time responsável (Slack, email de on-call).

### 4. Right-sizing periódico

Rotina de revisão (trimestral no mínimo):

1. **Compute Optimizer:** identifica instâncias EC2, EBS, Lambda sub/super-dimensionadas.
2. **Trusted Advisor Cost Optimization:** lista RIs/Savings Plans subutilizados, instâncias ociosas, IPs elásticos não associados.
3. **Unused resources:** volumes EBS não anexados, snapshots antigos, load balancers sem targets, NAT Gateways em VPCs sem tráfego.
4. **Logs e backups:** CloudWatch Logs com retenção indefinida acumulam custo; definir retenção por ambiente.

### 5. Reserved Instances / Savings Plans / Spot

Para workload previsível e sustained:

1. **Savings Plans** (preferencial por flexibilidade) — compute, EC2 Instance, SageMaker.
2. **Reserved Instances** para RDS, ElastiCache, DynamoDB, Redshift.
3. **Spot Instances** para cargas tolerantes a interrupção (batch, ML training, CI).

Cobertura-alvo: **70%+** do compute sustained em Savings Plans/RIs.

### 6. Patterns a evitar (cost smells)

| Pattern | Por que evitar |
|---|---|
| NAT Gateway por AZ sem justificativa | Cada um custa ~US$ 32/mês + transfer; consolidar se uma AZ suporta |
| Log retention infinita no CloudWatch | CW Logs custa por GB armazenado; mover para S3 com lifecycle para Glacier |
| DynamoDB on-demand para workload alto e constante | On-demand é ~7x mais caro que provisioned para workload previsível |
| S3 sem lifecycle policy | Buckets crescem indefinidamente; definir transições para IA/Glacier |
| Elastic IPs não associados | Cobrados por hora quando não usados (~US$ 3.6/mês cada) |
| Snapshots EBS sem retention policy | Acumulam mensalmente; definir política (ex.: diários 7 dias, semanais 4 sem, mensais 12 meses) |
| ALB/NLB sem targets | Cobrados mensalmente mesmo sem tráfego |
| Cross-region replication sem necessidade real | Cada GB replicado é cobrado 2x (origem + destino) |
| Dev/staging idênticos a prod em tamanho | Dev/staging devem ser minimamente dimensionados; auto-stop fora do horário comercial |

### 7. Estimativa antes de provisionar

Antes de provisionar arquitetura nova ou expandir existente significativamente:

1. Estimar custo mensal via **AWS Pricing Calculator**.
2. Comparar com o budget do ambiente.
3. Se exceder em >20% o budget atual: justificar ou redesenhar.
4. Incluir estimativa no `docs/issues/issue-{n}/03-architecture.md` quando no fluxo Issue-Driven.

## Abrangência

- **Aplica-se a:** todo provisionamento e redesign de infraestrutura AWS
- **Agentes vinculados:** `warrior-atlas`, agentes DevOps
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Gastos inesperados:** custo mensal dobra sem justificativa; impacto em unit economics e investimentos
2. **Alocação errada:** sem tags, impossível atribuir custo a produto/time; decisões de priorização ficam cegas
3. **Surpresas em faturas:** sem budgets, spike de custo só é detectado no fechamento do mês
4. **Remediação:**
   - Executar Cost Explorer + Trusted Advisor imediatamente
   - Identificar top 10 contribuintes de custo; right-size ou desligar
   - Aplicar tags retroativamente e ativar cost allocation
   - Configurar budgets com alertas agressivos

## Validação Automatizada

- **Ferramenta:**
  - **Pricing Calculator** (manual ou integrado ao CI)
  - **Infracost** (custo estimado em PR de Terraform)
  - **AWS Cost Explorer + Anomaly Detection**
  - **Trusted Advisor** (requer Business/Enterprise Support)
  - **Compute Optimizer** (free)
- **Momento:** cada PR de infra (Infracost); diariamente (anomaly); mensalmente (review manual)
- **Métrica:** 100% de recursos com cost allocation tags; budgets em todas as contas; desvio mensal <15% do previsto

## Referências

- `codex-aws-well-architected` — Pilar de Otimização de Custo
- `codex-aws-services` — guia de escolha por caso de uso
- `lex-aws-iac` — tagging via IaC
- [AWS Pricing Calculator](https://calculator.aws)
- [AWS Well-Architected Cost Optimization Pillar](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html)
