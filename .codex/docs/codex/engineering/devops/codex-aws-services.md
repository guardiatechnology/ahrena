# Codex: Catálogo de Serviços AWS

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Guia de serviços AWS por caso de uso — quando usar, quando evitar, alternativas

## Conteúdo

### Compute

| Caso de Uso | Serviço Recomendado | Alternativas | Quando Evitar |
|---|---|---|---|
| Web/API com tráfego variável ou baixo | **Lambda** (com API Gateway ou ALB) | Fargate, EC2 | Requisitos de long-running (>15min), warm-up muito sensível |
| Container workload constante e simples | **ECS Fargate** (com ALB) | EKS, ECS/EC2 | Quando precisa de Kubernetes ecossystem ou customizações pesadas |
| Kubernetes (workload complexo, multi-cloud) | **EKS** | Self-managed K8s, ECS | Times pequenos sem capacidade operacional K8s |
| Workload sustained/CPU-intensivo com custo otimizado | **EC2 (com Savings Plan)** | Fargate com SP, EKS on EC2 | Workload variável (serverless é melhor) |
| Batch processing | **AWS Batch** ou **Step Functions + Lambda** | EMR (se Spark), ECS | Jobs simples que cabem em cron (use EventBridge) |
| ML training | **SageMaker Training Jobs** | EC2 com Deep Learning AMI | Batch curto e pequeno (SageMaker é overhead) |
| ML inference | **SageMaker Endpoints**, **Lambda** | EC2, ECS | Latência crítica (Lambda tem cold start) |
| Edge compute (latência baixa global) | **Lambda@Edge** ou **CloudFront Functions** | — | Lógica pesada (limites de execução) |

**Graviton (ARM):** preferir para workloads compatíveis — até 40% melhor custo-performance.

### Storage

| Caso de Uso | Serviço | Notas |
|---|---|---|
| Object storage (arquivos, backups, estáticos) | **S3** (classes: Standard, IA, Glacier, Deep Archive) | Use lifecycle policies; bloquear acesso público por padrão |
| Block storage para EC2 | **EBS** (gp3 > gp2; io2 para IOPS alta) | `encrypted: true` sempre |
| File storage compartilhado POSIX | **EFS** (General Purpose ou Max I/O) | Use quando múltiplas instâncias precisam do mesmo filesystem |
| File storage Windows | **FSx for Windows** | SMB, Active Directory integrado |
| High-performance file (HPC, ML training) | **FSx for Lustre** | Integração com S3 |
| Backup gerenciado | **AWS Backup** | Cross-region, cross-account, compliance reports |

**Tiering automático S3:** `Intelligent-Tiering` move objetos entre classes baseado em acesso — ideal quando padrão de acesso é desconhecido.

### Banco de Dados

| Caso de Uso | Serviço | Quando preferir |
|---|---|---|
| Relacional transacional (OLTP) | **Aurora** (MySQL ou PostgreSQL compatible) | Alta disponibilidade, auto-scaling de storage, read replicas |
| Relacional simples / legado | **RDS** (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server) | Feature paridade específica; custo mais baixo que Aurora em small workloads |
| Serverless relacional | **Aurora Serverless v2** | Workload intermitente; evita provisionar instância idle |
| NoSQL key-value / document com padrões conhecidos | **DynamoDB** | Low latency, escala massiva, pricing previsível com provisioned |
| NoSQL document flexível | **DocumentDB** (MongoDB compatible) | Migração de MongoDB; queries flexíveis |
| NoSQL wide-column | **Keyspaces** (Cassandra compatible) | Write-heavy, time-series |
| Graph | **Neptune** | Relacionamentos complexos, recomendações, fraud detection |
| Time-series | **Timestream** | IoT, métricas aplicacionais, custos otimizados para appends |
| Cache | **ElastiCache Redis** (primeiro) ou **Memcached** | Low-latency, session storage, rate limiting |
| Data warehouse | **Redshift** (cluster) ou **Redshift Serverless** | Analytics OLAP; petabyte scale |
| OLAP ad-hoc sobre S3 | **Athena** | Query SQL em dados S3 sem ETL; pay-per-query |
| Search (full-text) | **OpenSearch** | Logs, search em catálogos, monitoring |
| In-memory / transações extremas | **MemoryDB** | Durabilidade Redis com recovery rápido |

**Dica:** começar com Aurora Serverless v2 para workloads novas com tráfego incerto — flexibilidade com custo controlado.

### Messaging e Streaming

| Caso de Uso | Serviço | Notas |
|---|---|---|
| Fila de mensagens (point-to-point) | **SQS** (Standard ou FIFO) | FIFO para garantia de ordem e exactly-once |
| Pub/sub para fan-out (1:N) | **SNS** (com subscribers SQS, Lambda, HTTPS) | Combinado com SQS para durabilidade |
| Event bus desacoplado | **EventBridge** | Event-driven entre serviços; schema registry; rules com filtragem |
| Streaming de dados (high throughput, ordered) | **Kinesis Data Streams** | Analytics em tempo real, custom consumers |
| Streaming gerenciado (Kafka-compatible) | **MSK (Managed Streaming for Kafka)** | Migração de Kafka on-prem; ecossistema Kafka |
| Delivery de streams para S3/Redshift/OpenSearch | **Kinesis Data Firehose** | ETL leve com transformação Lambda opcional |
| IoT ingestion | **IoT Core** | MQTT/HTTPS, device registry, rules |

**Padrão recomendado:** EventBridge como **event bus central** para comunicação entre bounded contexts (produz eventos CloudEvents — ver `warrior-kronos`).

### Network

| Caso de Uso | Serviço | Notas |
|---|---|---|
| VPC isolada | **VPC** com subnets públicas/privadas | Use subnets privadas para workloads; públicas só para NAT/ALB |
| Load balancer HTTP/HTTPS (L7) | **ALB** | WebSocket, HTTP/2, path-based routing, OIDC auth |
| Load balancer TCP/UDP (L4) | **NLB** | High performance, static IPs |
| Load balancer global cross-region | **Global Accelerator** | Anycast IPs, failover global |
| CDN + edge | **CloudFront** | Static assets, API caching, Origin Shield |
| DNS gerenciado | **Route 53** | Health checks, failover, geolocation routing |
| Conectividade cross-VPC/account | **Transit Gateway** (scale) ou VPC Peering (simples) | TGW para hub-and-spoke |
| Conectividade on-prem | **Direct Connect** (dedicado) ou **Site-to-Site VPN** | DX para latência/bandwidth previsível |
| API pública gerenciada | **API Gateway** (REST, HTTP, WebSocket) | Throttling, auth, transformação |
| Privado endpoint para serviços AWS | **VPC Endpoints** (Gateway para S3/DynamoDB; Interface para outros) | Reduz NAT Gateway costs e melhora segurança |

### Segurança e Identidade

| Caso de Uso | Serviço |
|---|---|
| Gerenciamento de identidade federada (SSO) | **IAM Identity Center** (ex-SSO) |
| Segredos rotáveis | **Secrets Manager** |
| Parâmetros de configuração | **SSM Parameter Store** (SecureString para sensíveis) |
| Gestão de chaves de criptografia | **KMS** (CMK customer-managed recomendadas) |
| HSM dedicado | **CloudHSM** |
| WAF em ALB/CloudFront/API Gateway | **AWS WAF** |
| Proteção DDoS | **Shield Standard** (free) + **Shield Advanced** para workloads críticos |
| Detecção de ameaças | **GuardDuty** |
| Compliance tracking | **Config**, **Security Hub**, **Audit Manager** |
| Classificação de dados sensíveis | **Macie** |
| SIEM / investigação | **Security Lake** + CloudTrail + Athena |

### Observabilidade

| Caso de Uso | Serviço | Alternativas Externas |
|---|---|---|
| Métricas | **CloudWatch Metrics** | Datadog, New Relic |
| Logs | **CloudWatch Logs** | Datadog, Splunk |
| Tracing distribuído | **X-Ray** | Jaeger, Datadog APM |
| Dashboards | **CloudWatch Dashboards** ou **Amazon Managed Grafana** | Grafana OSS |
| Alarms | **CloudWatch Alarms** → SNS → PagerDuty | PagerDuty, Opsgenie |
| Logs agregados multi-conta | **CloudWatch Cross-Account Observability** | Datadog, Splunk |

**Padrão recomendado:** OpenTelemetry SDK na aplicação → X-Ray/CloudWatch como sink padrão AWS, ou externo se time já usa.

### CI/CD

| Caso de Uso | Serviço | Alternativas |
|---|---|---|
| Pipeline nativo AWS | **CodePipeline** + **CodeBuild** + **CodeDeploy** | GitHub Actions (mais popular) |
| Build isolado | **CodeBuild** | GitHub Actions, Buildkite |
| Deploy EC2/Lambda/ECS | **CodeDeploy** | Feature flags (LaunchDarkly) |
| Registry de container | **ECR** | — |
| IaC pipeline | **CodePipeline + CodeBuild com Terraform** ou **CDK Pipelines** | Atlantis, Spacelift |

**Recomendação:** muitos times preferem **GitHub Actions** pela integração natural com o repositório; CodePipeline faz sentido quando compliance exige tudo em AWS.

### Escolha de Região

Fatores de decisão:

1. **Latência ao usuário final** — região mais próxima
2. **Disponibilidade de serviço** — nem todo serviço está em toda região (ex.: Bedrock, Outposts)
3. **Custo** — varia por região (us-east-1 geralmente mais barato)
4. **Compliance** — residência de dados (LGPD pode exigir Brasil; GDPR pode exigir EU)
5. **Sustainability** — regiões com carbono baixo (`eu-west-2` London, `us-west-2` Oregon)

**Para Guardia (Brasil):** **sa-east-1** (São Paulo) para produção com dados sensíveis de clientes; `us-east-1` para workloads globais ou serviços indisponíveis em São Paulo.

### Anti-patterns a evitar

| Anti-pattern | Problema | Alternativa |
|---|---|---|
| Usar EC2 para cada workload (legado on-prem mindset) | Alto custo operacional, underutilização | Lambda, Fargate, serviços gerenciados |
| Endpoint público em RDS/ElastiCache | Risco de segurança | VPC privada + VPC Endpoints ou bastion |
| NAT Gateway em single AZ para workload multi-AZ | Single point of failure | NAT Gateway por AZ (ou aceitar custo + SLA) |
| CloudWatch Logs sem retenção configurada | Custo explode com volume | Definir retenção (7/30/90 dias) por log group |
| Security groups com `0.0.0.0/0` em porta administrativa (22, 3389) | Superfície de ataque | Session Manager (SSM) para shell; sem SSH direto |
| Access keys IAM para humanos | Leak risk; hard rotation | IAM Identity Center (SSO) + AssumeRole temporário |
| Custom code para alta disponibilidade | Reinventar roda; bugs | Serviços gerenciados com Multi-AZ built-in |
