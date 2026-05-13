# Lexis: AWS Cost Awareness

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Design and operation of AWS infrastructure with attention to cost — tagging, right-sizing, spend monitoring, surprise prevention

## Purpose

AWS charges for what is provisioned, not what is used — an `r6i.4xlarge` instance left on over the weekend generates US$ 800/month even while idle. Without cost discipline, it is trivial to provision architectures that work but bleed money: oversized instances, data in S3 Standard when it should be in Glacier, DynamoDB on-demand for a predictable workload, NAT Gateways in every AZ without need. AI agents designing on AWS must include the cost axis alongside performance and security.

This Lexis exists to ensure that **every resource is tagged for cost allocation**, that **choices have explicit cost awareness**, that **budgets and alarms are configured**, and that **usage is periodically reviewed for right-sizing**.

## Law

> **Every AWS architecture MUST be designed with explicit cost awareness. Every resource MUST have cost allocation tags (`CostCenter`, `Environment`, `Project`, `Owner`). Budgets with alerts MUST be configured per environment. Choices with cost impact >US$ 100/month MUST be documented with alternatives considered.**

## Rules

### 1. Tagging for cost allocation

Every taxable resource **MUST** have minimum tags:

```hcl
tags = {
  CostCenter  = "engineering" | "product" | "marketing" | ...
  Environment = "dev" | "staging" | "prod"
  Project     = "ahrena" | "refund-service" | ...
  Owner       = "team-name@guardia.com"
}
```

1. **Cost allocation tags** enabled in the Billing Console.
2. **Cost Explorer** configured for breakdown by tag.
3. **Monthly reports** by `CostCenter` and `Environment`.
4. Resources **without tags** in production are blocked by SCP or Config Rule.

### 2. Cost-aware choices

When choosing resources, the agent **MUST** consider:

| Decision | Cost question |
|---|---|
| Compute: EC2 vs. Lambda vs. Fargate vs. EKS | What is the usage pattern? Sustained → reserved EC2. Bursty/sparse → Lambda. Consistent container → Fargate. Complex orchestration → EKS |
| Storage: S3 Standard vs. IA vs. Glacier vs. Deep Archive | Access frequency? Standard for <30 days; IA 30-90; Glacier >90 with sporadic retrieval; Deep Archive for compliance |
| DB: RDS on-demand vs. reserved; DynamoDB on-demand vs. provisioned | Predictable workload → reserved/provisioned (up to 60% savings); unpredictable → on-demand |
| Network: NAT Gateway vs. NAT Instance vs. VPC Endpoints | NAT Gateway is expensive (~US$ 32/month/AZ + transfer); use VPC endpoints for S3/DynamoDB; consolidate NAT when traffic allows |
| Data Transfer | Cross-AZ, cross-region, and egress to the internet have distinct costs; avoid unnecessary traffic between AZs |

Decisions with predicted impact **>US$ 100/month** must be registered (ADR when structurally relevant — see `codex-issue-workflow`).

### 3. Budgets and alarms

Each account/environment **MUST** have:

1. **AWS Budgets** configured with:
   - Monthly budget per `Environment` (prod, staging, dev)
   - Alerts at 50%, 80%, 100% of the limit
   - Alerts at 50%, 80%, 100% of the **forecast** (end-of-month prediction)
2. **Anomaly Detection** enabled (AWS Cost Anomaly Detection).
3. **CloudWatch billing alarm** for general spikes (e.g., >20% vs. previous month).
4. Alerts go to the responsible team's channel (Slack, on-call email).

### 4. Periodic right-sizing

Review routine (quarterly at minimum):

1. **Compute Optimizer:** identifies under/over-sized EC2, EBS, Lambda instances.
2. **Trusted Advisor Cost Optimization:** lists underutilized RIs/Savings Plans, idle instances, unassociated elastic IPs.
3. **Unused resources:** unattached EBS volumes, old snapshots, load balancers with no targets, NAT Gateways in VPCs with no traffic.
4. **Logs and backups:** CloudWatch Logs with indefinite retention accumulate cost; define retention per environment.

### 5. Reserved Instances / Savings Plans / Spot

For predictable, sustained workloads:

1. **Savings Plans** (preferred for flexibility) — compute, EC2 Instance, SageMaker.
2. **Reserved Instances** for RDS, ElastiCache, DynamoDB, Redshift.
3. **Spot Instances** for interruption-tolerant loads (batch, ML training, CI).

Target coverage: **70%+** of sustained compute in Savings Plans/RIs.

### 6. Patterns to avoid (cost smells)

| Pattern | Why avoid |
|---|---|
| NAT Gateway per AZ without justification | Each costs ~US$ 32/month + transfer; consolidate if one AZ can support |
| Infinite log retention in CloudWatch | CW Logs charges per GB stored; move to S3 with lifecycle to Glacier |
| DynamoDB on-demand for high, constant workload | On-demand is ~7x more expensive than provisioned for a predictable workload |
| S3 without lifecycle policy | Buckets grow indefinitely; define transitions to IA/Glacier |
| Unassociated Elastic IPs | Charged per hour when unused (~US$ 3.6/month each) |
| EBS snapshots without retention policy | Accumulate monthly; define a policy (e.g., daily 7 days, weekly 4 weeks, monthly 12 months) |
| ALB/NLB with no targets | Charged monthly even without traffic |
| Cross-region replication without real need | Each GB replicated is charged 2x (source + destination) |
| Dev/staging identical to prod in size | Dev/staging should be minimally sized; auto-stop outside business hours |

### 7. Estimate before provisioning

Before provisioning a new architecture or significantly expanding an existing one:

1. Estimate monthly cost via **AWS Pricing Calculator**.
2. Compare with the environment's budget.
3. If it exceeds the current budget by >20%: justify or redesign.
4. Include the estimate in `.ahrena/issues/{n}/03-architecture.md` when in the Issue-Driven flow.

## Applicability

- **Applies to:** all AWS infrastructure provisioning and redesign
- **Bound agents:** `warrior-atlas`, DevOps agents
- **Exceptions:** None. Lexis do not admit exceptions.

## Consequences of Violation

1. **Unexpected spending:** monthly cost doubles without justification; impact on unit economics and investments
2. **Wrong allocation:** without tags, impossible to attribute cost to product/team; prioritization decisions go blind
3. **Invoice surprises:** without budgets, cost spikes are only detected at month close
4. **Remediation:**
   - Run Cost Explorer + Trusted Advisor immediately
   - Identify top 10 cost contributors; right-size or shut down
   - Apply tags retroactively and activate cost allocation
   - Configure budgets with aggressive alerts

## Automated Validation

- **Tools:**
  - **Pricing Calculator** (manual or integrated into CI)
  - **Infracost** (estimated cost in Terraform PRs)
  - **AWS Cost Explorer + Anomaly Detection**
  - **Trusted Advisor** (requires Business/Enterprise Support)
  - **Compute Optimizer** (free)
- **When:** every infra PR (Infracost); daily (anomaly); monthly (manual review)
- **Metric:** 100% of resources with cost allocation tags; budgets in all accounts; monthly variance <15% of forecast

## References

- `codex-aws-well-architected` — Cost Optimization Pillar
- `codex-aws-services` — selection guide by use case
- `lex-aws-iac` — tagging via IaC
- [AWS Pricing Calculator](https://calculator.aws)
- [AWS Well-Architected Cost Optimization Pillar](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html)
