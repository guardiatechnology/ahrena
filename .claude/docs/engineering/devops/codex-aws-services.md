# Codex: AWS Services Catalog

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Guide to AWS services by use case — when to use, when to avoid, alternatives

## Content

### Compute

| Use Case | Recommended Service | Alternatives | When to Avoid |
|---|---|---|---|
| Web/API with variable or low traffic | **Lambda** (with API Gateway or ALB) | Fargate, EC2 | Long-running requirements (>15min), very warm-up-sensitive |
| Constant, simple container workload | **ECS Fargate** (with ALB) | EKS, ECS/EC2 | When you need the Kubernetes ecosystem or heavy customization |
| Kubernetes (complex workload, multi-cloud) | **EKS** | Self-managed K8s, ECS | Small teams without K8s operational capacity |
| Sustained/CPU-intensive workload with optimized cost | **EC2 (with Savings Plan)** | Fargate with SP, EKS on EC2 | Variable workload (serverless is better) |
| Batch processing | **AWS Batch** or **Step Functions + Lambda** | EMR (if Spark), ECS | Simple jobs that fit in cron (use EventBridge) |
| ML training | **SageMaker Training Jobs** | EC2 with Deep Learning AMI | Short, small batch (SageMaker is overhead) |
| ML inference | **SageMaker Endpoints**, **Lambda** | EC2, ECS | Latency-critical (Lambda has cold start) |
| Edge compute (low global latency) | **Lambda@Edge** or **CloudFront Functions** | — | Heavy logic (execution limits) |

**Graviton (ARM):** prefer for compatible workloads — up to 40% better cost-performance.

### Storage

| Use Case | Service | Notes |
|---|---|---|
| Object storage (files, backups, static) | **S3** (classes: Standard, IA, Glacier, Deep Archive) | Use lifecycle policies; block public access by default |
| Block storage for EC2 | **EBS** (gp3 > gp2; io2 for high IOPS) | `encrypted: true` always |
| POSIX shared file storage | **EFS** (General Purpose or Max I/O) | Use when multiple instances need the same filesystem |
| Windows file storage | **FSx for Windows** | SMB, Active Directory integrated |
| High-performance file (HPC, ML training) | **FSx for Lustre** | S3 integration |
| Managed backup | **AWS Backup** | Cross-region, cross-account, compliance reports |

**S3 automatic tiering:** `Intelligent-Tiering` moves objects between classes based on access — ideal when the access pattern is unknown.

### Databases

| Use Case | Service | When to prefer |
|---|---|---|
| Transactional relational (OLTP) | **Aurora** (MySQL or PostgreSQL compatible) | High availability, storage auto-scaling, read replicas |
| Simple/legacy relational | **RDS** (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server) | Specific feature parity; lower cost than Aurora on small workloads |
| Serverless relational | **Aurora Serverless v2** | Intermittent workload; avoids provisioning an idle instance |
| NoSQL key-value / document with known patterns | **DynamoDB** | Low latency, massive scale, predictable pricing with provisioned |
| Flexible NoSQL document | **DocumentDB** (MongoDB compatible) | Migration from MongoDB; flexible queries |
| NoSQL wide-column | **Keyspaces** (Cassandra compatible) | Write-heavy, time-series |
| Graph | **Neptune** | Complex relationships, recommendations, fraud detection |
| Time-series | **Timestream** | IoT, application metrics, costs optimized for appends |
| Cache | **ElastiCache Redis** (first) or **Memcached** | Low-latency, session storage, rate limiting |
| Data warehouse | **Redshift** (cluster) or **Redshift Serverless** | OLAP analytics; petabyte scale |
| Ad-hoc OLAP over S3 | **Athena** | SQL queries on S3 data without ETL; pay-per-query |
| Search (full-text) | **OpenSearch** | Logs, catalog search, monitoring |
| In-memory / extreme transactions | **MemoryDB** | Redis durability with fast recovery |

**Tip:** start with Aurora Serverless v2 for new workloads with uncertain traffic — flexibility with controlled cost.

### Messaging and Streaming

| Use Case | Service | Notes |
|---|---|---|
| Message queue (point-to-point) | **SQS** (Standard or FIFO) | FIFO for order guarantee and exactly-once |
| Pub/sub for fan-out (1:N) | **SNS** (with SQS, Lambda, HTTPS subscribers) | Combined with SQS for durability |
| Decoupled event bus | **EventBridge** | Event-driven between services; schema registry; rules with filtering |
| Data streaming (high throughput, ordered) | **Kinesis Data Streams** | Real-time analytics, custom consumers |
| Managed streaming (Kafka-compatible) | **MSK (Managed Streaming for Kafka)** | Migration from on-prem Kafka; Kafka ecosystem |
| Stream delivery to S3/Redshift/OpenSearch | **Kinesis Data Firehose** | Light ETL with optional Lambda transformation |
| IoT ingestion | **IoT Core** | MQTT/HTTPS, device registry, rules |

**Recommended pattern:** EventBridge as **central event bus** for communication between bounded contexts (produces CloudEvents — see `warrior-kronos`).

### Network

| Use Case | Service | Notes |
|---|---|---|
| Isolated VPC | **VPC** with public/private subnets | Use private subnets for workloads; public only for NAT/ALB |
| HTTP/HTTPS load balancer (L7) | **ALB** | WebSocket, HTTP/2, path-based routing, OIDC auth |
| TCP/UDP load balancer (L4) | **NLB** | High performance, static IPs |
| Global cross-region load balancer | **Global Accelerator** | Anycast IPs, global failover |
| CDN + edge | **CloudFront** | Static assets, API caching, Origin Shield |
| Managed DNS | **Route 53** | Health checks, failover, geolocation routing |
| Cross-VPC/account connectivity | **Transit Gateway** (scale) or VPC Peering (simple) | TGW for hub-and-spoke |
| On-prem connectivity | **Direct Connect** (dedicated) or **Site-to-Site VPN** | DX for predictable latency/bandwidth |
| Managed public API | **API Gateway** (REST, HTTP, WebSocket) | Throttling, auth, transformation |
| Private endpoint for AWS services | **VPC Endpoints** (Gateway for S3/DynamoDB; Interface for others) | Reduces NAT Gateway costs and improves security |

### Security and Identity

| Use Case | Service |
|---|---|
| Federated identity management (SSO) | **IAM Identity Center** (former SSO) |
| Rotatable secrets | **Secrets Manager** |
| Configuration parameters | **SSM Parameter Store** (SecureString for sensitive) |
| Encryption key management | **KMS** (customer-managed CMKs recommended) |
| Dedicated HSM | **CloudHSM** |
| WAF on ALB/CloudFront/API Gateway | **AWS WAF** |
| DDoS protection | **Shield Standard** (free) + **Shield Advanced** for critical workloads |
| Threat detection | **GuardDuty** |
| Compliance tracking | **Config**, **Security Hub**, **Audit Manager** |
| Sensitive data classification | **Macie** |
| SIEM / investigation | **Security Lake** + CloudTrail + Athena |

### Observability

| Use Case | Service | External Alternatives |
|---|---|---|
| Metrics | **CloudWatch Metrics** | Datadog, New Relic |
| Logs | **CloudWatch Logs** | Datadog, Splunk |
| Distributed tracing | **X-Ray** | Jaeger, Datadog APM |
| Dashboards | **CloudWatch Dashboards** or **Amazon Managed Grafana** | Grafana OSS |
| Alarms | **CloudWatch Alarms** → SNS → PagerDuty | PagerDuty, Opsgenie |
| Aggregated multi-account logs | **CloudWatch Cross-Account Observability** | Datadog, Splunk |

**Recommended pattern:** OpenTelemetry SDK in the application → X-Ray/CloudWatch as default AWS sink, or external if the team already uses one.

### CI/CD

| Use Case | Service | Alternatives |
|---|---|---|
| Native AWS pipeline | **CodePipeline** + **CodeBuild** + **CodeDeploy** | GitHub Actions (more popular) |
| Isolated build | **CodeBuild** | GitHub Actions, Buildkite |
| EC2/Lambda/ECS deploy | **CodeDeploy** | Feature flags (LaunchDarkly) |
| Container registry | **ECR** | — |
| IaC pipeline | **CodePipeline + CodeBuild with Terraform** or **CDK Pipelines** | Atlantis, Spacelift |

**Recommendation:** many teams prefer **GitHub Actions** for natural integration with the repository; CodePipeline makes sense when compliance requires everything in AWS.

### Region Selection

Decision factors:

1. **Latency to end users** — closest region
2. **Service availability** — not every service is in every region (e.g., Bedrock, Outposts)
3. **Cost** — varies by region (us-east-1 generally cheaper)
4. **Compliance** — data residency (LGPD may require Brazil; GDPR may require EU)
5. **Sustainability** — low-carbon regions (`eu-west-2` London, `us-west-2` Oregon)

**For Guardia (Brazil):** **sa-east-1** (São Paulo) for production with sensitive customer data; `us-east-1` for global workloads or services unavailable in São Paulo.

### Anti-patterns to avoid

| Anti-pattern | Problem | Alternative |
|---|---|---|
| Using EC2 for every workload (legacy on-prem mindset) | High operational cost, underutilization | Lambda, Fargate, managed services |
| Public endpoint on RDS/ElastiCache | Security risk | Private VPC + VPC Endpoints or bastion |
| NAT Gateway in a single AZ for a multi-AZ workload | Single point of failure | NAT Gateway per AZ (or accept cost + SLA) |
| CloudWatch Logs without configured retention | Cost explodes with volume | Define retention (7/30/90 days) per log group |
| Security groups with `0.0.0.0/0` on administrative ports (22, 3389) | Attack surface | Session Manager (SSM) for shell; no direct SSH |
| IAM access keys for humans | Leak risk; hard rotation | IAM Identity Center (SSO) + temporary AssumeRole |
| Custom code for high availability | Reinventing the wheel; bugs | Managed services with built-in Multi-AZ |
