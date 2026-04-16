# Codex: AWS Well-Architected Framework

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** The six pillars of the AWS Well-Architected Framework — reference for designing and reviewing AWS architectures

## Overview

The **AWS Well-Architected Framework** is the set of principles, best practices, and structural questions that AWS publishes to guide the design of cloud workloads. This Codex summarizes the 6 pillars, their key questions, and common trade-offs, serving as a reference for `warrior-atlas` when designing or reviewing architectures.

## Context

- **Domain:** AWS solutions architecture
- **Target audience:** `warrior-atlas`, DevOps agents, architecture reviewers
- **Update:** when AWS updates the framework (annual revisions) or when new services change established practices

## Content

### The 6 pillars

1. **Operational Excellence** — Run and monitor systems to deliver business value
2. **Security** — Protect information, systems, and assets
3. **Reliability** — Workloads run as expected, consistently and at scale
4. **Performance Efficiency** — Efficient use of computing resources
5. **Cost Optimization** — Avoid unnecessary costs
6. **Sustainability** — Minimize environmental impact

### Pillar 1 — Operational Excellence

**Design principles:**

- Operations as code (IaC, runbook automation)
- Make frequent, small, reversible changes
- Refine operational procedures frequently
- Anticipate failure (game days, chaos engineering)
- Learn from failure (blameless post-mortems)

**Key questions:**

1. How does the organization understand its workload in production? (metrics, logs, traces)
2. How does it respond to events (alerts) and incidents?
3. How does it evolve operational procedures?

**Essential practices:**

- **IaC** via Terraform/CDK (see `lex-aws-iac`)
- **CI/CD** with automated pipelines, blue/green or canary deploys
- **Full observability:** metrics (CloudWatch), logs (CloudWatch Logs), traces (X-Ray / OpenTelemetry)
- **Versioned runbooks** for frequent incidents
- **Quarterly game days** to exercise failure scenarios

### Pillar 2 — Security

**Design principles:**

- Implement strong identity (MFA, least privilege)
- Enable traceability (CloudTrail, Config)
- Apply security at all layers (defense in depth)
- Automate security best practices
- Protect data in transit and at rest
- Keep people away from data (programmatic access)
- Prepare for security events (IR plan)

**Key questions:**

1. How do you operate your workload securely?
2. How do you manage identities for people and machines?
3. How do you detect and investigate security events?
4. How do you protect your infrastructure (network, compute)?
5. How do you classify and protect data?

**Essential practices:**

- **AWS Organizations** with SCPs and separate OUs
- **IAM** with roles + Identity Center (SSO) for humans; IRSA for Kubernetes workloads
- **KMS** for managed keys; automatic rotation
- **Secrets Manager** / **Parameter Store SecureString** for secrets
- **VPC** with private subnets; specific Security Groups; WAF for public APIs
- **CloudTrail + GuardDuty + Security Hub + Macie** — detection and compliance

> See `lex-aws-security` for inviolable rules.

### Pillar 3 — Reliability

**Design principles:**

- Automate recovery from failure
- Test recovery procedures
- Scale horizontally to increase availability
- Stop guessing capacity (auto-scaling)
- Manage changes through automation

**Key questions:**

1. How do you understand demand and capacity?
2. How do you handle component failures?
3. How do you recover from disasters?

**Essential practices:**

- **Multi-AZ** as standard for production (RDS, ElastiCache, ECS, EKS)
- **Multi-Region** for tier-1 workloads (RPO/RTO defined explicitly)
- **Auto-scaling** on relevant metrics (CPU, custom metrics, target tracking)
- **Health checks** on ALB/NLB + Route 53; automatic failover
- **Backup** via AWS Backup with defined RPO; periodic restore tests
- **Circuit breakers** and graceful degradation across service layers
- **Chaos engineering** (AWS Fault Injection Simulator) to validate resilience

**RTO/RPO reference by criticality:**

| Tier | RTO | RPO | Typical architecture |
|---|---|---|---|
| Tier 1 (critical, financial) | <1h | <5min | Multi-region active-active |
| Tier 2 (important) | <4h | <1h | Multi-AZ + cross-region backup |
| Tier 3 (business-hours) | <24h | <24h | Multi-AZ; daily backup |
| Tier 4 (internal) | <72h | <24h | Single-AZ with backup |

### Pillar 4 — Performance Efficiency

**Design principles:**

- Democratize advanced technologies (use managed services)
- Go global in minutes (CloudFront, multi-region)
- Use serverless architectures to reduce operations
- Experiment frequently
- Consider mechanical sympathy (choose the right service for the problem)

**Key questions:**

1. How do you select the compute/storage/DB/network architecture?
2. How do you evolve as new technologies emerge?
3. How do you monitor resources to ensure performance?

**Common choices by workload:**

| Workload | Recommended choice |
|---|---|
| HTTP API with variable traffic | API Gateway + Lambda (serverless) or ECS Fargate + ALB |
| HTTP API with high sustained traffic | ECS on EC2 (with RI) or EKS |
| Asynchronous event processing | SQS + Lambda or Kinesis + Lambda |
| Heavy stream processing | Kinesis Data Analytics, MSK (managed Kafka), Glue Streaming |
| Batch processing | Batch, Step Functions + Lambda, EMR |
| ML training/inference | SageMaker |
| Transactional relational DB | Aurora (MySQL/PostgreSQL-compatible) > RDS > self-managed |
| NoSQL DB with known patterns | DynamoDB |
| Full-text search | OpenSearch; if small, RDS with extensions |
| Cache | ElastiCache (Redis/Memcached) |
| Global asset delivery | CloudFront + S3 |

### Pillar 5 — Cost Optimization

> See `lex-aws-cost` for inviolable rules and detailed practices.

**Design principles:**

- Implement cloud financial management
- Adopt a consumption model (pay for what you use)
- Measure overall efficiency
- Stop spending on undifferentiated heavy lifting (use managed services)
- Analyze and attribute expenses

**Essential practices:**

- Complete tagging + Cost Explorer
- Budgets + Anomaly Detection
- Savings Plans and Reserved Instances for predictable workloads
- Spot for tolerant loads
- Quarterly right-sizing via Compute Optimizer + Trusted Advisor
- Lifecycle policies on S3; log retention
- Auto-shutdown of dev/staging outside hours

### Pillar 6 — Sustainability

**Design principles:**

- Understand impact
- Establish sustainability goals
- Maximize utilization (consolidate workloads)
- Anticipate and adopt more efficient offerings
- Use managed services (they operate more efficiently than self-hosted equivalents)
- Reduce downstream impact (compress, paginate, etc.)

**Essential practices:**

- **Low-carbon-intensity regions:** prefer AWS regions powered by renewable energy (see Customer Carbon Footprint Tool)
- **ARM (Graviton)** for EC2/Lambda/RDS instances — ~40% more energy efficient
- **Serverless** reduces idle compute waste
- **Data:** aggressive lifecycle for old files; remove unused data
- **Images and assets:** modern formats (WebP, AVIF); CDN to reduce transfer

### Common trade-offs

Designing is balancing pillars. Typical trade-offs:

| Trade-off | Example |
|---|---|
| Reliability ↔ Cost | Multi-region doubles cost; justified only for critical workloads |
| Performance ↔ Cost | A larger instance is faster but costs more; right-sizing seeks the optimal point |
| Security ↔ Operational simplicity | More security layers (WAF, Shield, GuardDuty) increase operations |
| Sustainability ↔ Performance | Graviton is more efficient but may require compatibility testing |

The architecture **MUST document the chosen trade-off** — typically via ADR when structural (`kata-adr-write`).

### Well-Architected Tool

AWS offers the **Well-Architected Tool** (free) that guides workload review by answering the questions from the 6 pillars and generating an improvement plan. Recommended:

1. Run a review on new workloads (after go-live) and tier-1 annually.
2. Run specific **Well-Architected Lenses**: Serverless, SaaS, Machine Learning, Financial Services.
3. Register high-risk issues (HRIs) and treat them as priority debt.

## References

- `lex-aws-security` — Security Pillar as laws
- `lex-aws-cost` — Cost Pillar as laws
- `lex-aws-iac` — Operational Excellence Pillar
- `codex-aws-services` — services and choices by use case
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Well-Architected Tool](https://aws.amazon.com/well-architected-tool/)
