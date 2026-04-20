# Kata: Review AWS Architecture or IaC

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Systematic review of AWS architecture or IaC changes (Terraform, CDK, CloudFormation) against Lexis and the Well-Architected Framework

## Objective

Perform an AWS architecture review (design document or IaC diff), verifying adherence to applicable Lexis (`lex-aws-security`, `lex-aws-iac`, `lex-aws-cost`), to the 6 Well-Architected pillars, and to practices in the services catalog. Produces a structured report with findings categorized by severity, applicable in PR review or as a periodic review of existing infrastructure.

## When to Use

- IaC PR review before merge
- Architecture document review (before Gate 1 in the Issue-Driven flow)
- Periodic audit of an existing account/workload
- Preparation for a formal AWS Well-Architected Review

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Target | Yes | IaC PR (`git diff`) or `03-architecture.md` document or existing account/workload |
| Scope | Yes | Components to review — full review or focus on one pillar |
| Context | No | Original requirements, SLAs, applicable compliance |

## Workflow

```
Progress:
- [ ] 1. Gather target and context
- [ ] 2. Review Security (lex-aws-security)
- [ ] 3. Review IaC (lex-aws-iac)
- [ ] 4. Review Cost (lex-aws-cost)
- [ ] 5. Review Reliability
- [ ] 6. Review Performance
- [ ] 7. Review Operational Excellence
- [ ] 8. Consolidate report by severity
```

### Step 1: Gather target and context

Depending on the type:

- **IaC PR:** obtain `git diff`; identify resources created/modified/removed; stack (Terraform vs CDK vs CloudFormation).
- **Architecture document:** read `03-architecture.md`; extract components and choices.
- **Existing workload:** inventory via **Config**, **Resource Explorer**, tags.

Read original requirements when available to contextualize decisions.

### Step 2: Review Security

Against `lex-aws-security`:

- [ ] IAM roles with least privilege? No `*:*` or broad managed policies?
- [ ] Public access blocked on S3, RDS, ElastiCache?
- [ ] Encryption at rest enabled on S3/RDS/EBS/DynamoDB?
- [ ] Encryption in transit (TLS 1.2+) on ALB/API Gateway?
- [ ] Secrets via Secrets Manager/Parameter Store? No hardcoded?
- [ ] Multi-region CloudTrail enabled?
- [ ] Security Groups without `0.0.0.0/0` on administrative ports?
- [ ] KMS CMKs instead of AWS-managed where appropriate?
- [ ] Run `tfsec` / `cdk-nag` and capture findings

Severity example: public S3 without justification → **critical**; CloudTrail absence → **high**; AWS-managed KMS instead of CMK → **medium**.

### Step 3: Review IaC

Against `lex-aws-iac`:

- [ ] Everything as code (no manual console creation)?
- [ ] Remote state with locking? Never in Git?
- [ ] Separate environments (distinct workspaces/stacks)?
- [ ] Standardized tagging applied?
- [ ] Versioned modules (no `ref=main`)?
- [ ] Critical resources with `prevent_destroy` / `deletion_protection`?
- [ ] Secrets outside versioned IaC files?
- [ ] Pipeline with `plan` visible on PR + automated apply?

### Step 4: Review Cost

Against `lex-aws-cost`:

- [ ] Cost allocation tags present? (`CostCenter`, `Environment`, `Project`, `Owner`)
- [ ] Compute choices appropriate to the usage pattern? (Lambda vs Fargate vs EC2)
- [ ] Appropriate storage classes? (S3 Standard vs IA vs Glacier with lifecycle)
- [ ] Shared NAT Gateway when possible (not one per AZ without need)?
- [ ] Reserved/Savings Plan considered for sustained workload?
- [ ] CloudWatch Logs retention defined?
- [ ] Budget configured?
- [ ] Run `infracost` to estimate diff cost

### Step 5: Review Reliability

Against `codex-aws-well-architected` (Reliability Pillar):

- [ ] Multi-AZ enabled on RDS, ECS service, ElastiCache, NAT Gateway?
- [ ] Auto-scaling configured with adequate metrics?
- [ ] Health checks on ALB + Route 53?
- [ ] Automated backup via AWS Backup? Retention consistent with RPO?
- [ ] DR plan: multi-region if tier-1? RTO/RPO documented and tested?
- [ ] Dead-letter queues in queues and Lambda to avoid silent loss?
- [ ] Circuit breakers or retries with backoff on external integrations?

### Step 6: Review Performance

Against `codex-aws-well-architected` (Performance Pillar):

- [ ] Chosen service is the right one for the traffic pattern?
- [ ] Right-sized instances (not over/undersized)?
- [ ] Cache (CloudFront, ElastiCache) to reduce latency and backend load?
- [ ] VPC Endpoints for S3/DynamoDB to avoid NAT Gateway and improve latency?
- [ ] Reactive auto-scaling (e.g., target tracking) instead of fixed?
- [ ] Graviton (ARM) considered for compatible workloads?

### Step 7: Review Operational Excellence

- [ ] Logs, metrics, traces configured (CloudWatch, X-Ray)?
- [ ] CloudWatch alarms for critical events (high error rate, latency breach)?
- [ ] Operational dashboards created?
- [ ] Runbooks documented for predictable incidents?
- [ ] Deploy with blue/green or canary (CodeDeploy, ECS deployment controllers)?
- [ ] Automatic rollback on health check failure?

### Step 8: Consolidate report by severity

Structure findings:

```markdown
# AWS Architecture Review — {target}

- **Date:** {YYYY-MM-DD}
- **Scope:** {components or diff}
- **Findings:** {C} critical, {H} high, {M} medium, {L} low

## Summary by Pillar

| Pillar | Critical | High | Medium | Low |
|---|:-:|:-:|:-:|:-:|
| Security | 0 | 1 | 2 | 1 |
| Reliability | 0 | 0 | 1 | 0 |
| Performance | 0 | 0 | 0 | 2 |
| Cost | 0 | 1 | 3 | 2 |
| Operational | 0 | 0 | 1 | 0 |
| Sustainability | 0 | 0 | 0 | 1 |

## Critical Findings

### A-1: S3 bucket public without justification
- **Pillar:** Security
- **Location:** `infra/modules/assets/main.tf:42`
- **Problem:** `block_public_acls = false` and `block_public_policy = false`; bucket stores internal data
- **Recommendation:** enable `Block Public Access` and move public assets to a dedicated bucket with an explicit policy
- **Reference:** `lex-aws-security` §4

## High Findings

### A-2: ...

## Medium Findings

### A-3: ...

## Additional Recommendations (non-blocking)

- ...

## Positive Highlights

{2-3 well-executed points}

## Cost Estimate (Infracost)

Net change: +US$ 420/month
- +Aurora Serverless v2 baseline: +US$ 280
- +ALB: +US$ 22
- +NAT Gateway (new AZ): +US$ 32
- +Estimated data transfer: +US$ 86
```

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Review report | Structured Markdown | Response to user or `docs/reviews/{date}-aws-review.md` |
| PR comments | Inline comments via GitHub MCP | PR (optional) |
| Improvement plan | Prioritized action list | Part of the report |

## Restrictions

- **Review ≠ modification:** this kata reports; corrections are made by DevOps/the responsible team in a new iteration.
- **Objective severity:** critical = violates Lexis or causes immediate risk; high = contrary to Well-Architected; medium/low = incremental improvement.
- **Concrete evidence:** each finding has a location (file:line or resource) and a reference to Lexis/Codex.
- **Constructive tone:** point out problem + solution; it is not a punitive audit.

## References

- `lex-aws-security`, `lex-aws-iac`, `lex-aws-cost`
- `codex-aws-well-architected` — 6 pillars in detail
- `codex-aws-services` — catalog for comparing choices
- `kata-quality-gate` — integrates into the Issue-Driven flow
- `kata-mcp-github-read` — to review a remote PR
