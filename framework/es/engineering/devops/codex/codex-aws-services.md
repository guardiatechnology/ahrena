# Codex: Catálogo de Servicios AWS

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Guía de servicios AWS por caso de uso — cuándo usar, cuándo evitar, alternativas

## Visión General

AWS ofrece más de 200 servicios. Elegir el servicio correcto para un problema es parte central del trabajo del arquitecto de soluciones. Este Codex mapea casos de uso comunes a los servicios recomendados, con alternativas y trade-offs, sirviendo como referencia para `warrior-atlas` durante el diseño arquitectural y la revisión.

## Contexto

- **Dominio:** catálogo operacional de servicios AWS
- **Público objetivo:** `warrior-atlas`, agentes DevOps
- **Actualización:** cuando emergen nuevos servicios o cuando las prácticas cambian (ej.: Lambda SnapStart, Graviton, Serverless v3)

## Contenido

### Compute

| Caso de Uso | Servicio Recomendado | Alternativas | Cuándo Evitar |
|---|---|---|---|
| Web/API con tráfico variable o bajo | **Lambda** (con API Gateway o ALB) | Fargate, EC2 | Requisitos de long-running (>15min), warm-up muy sensible |
| Container workload constante y simple | **ECS Fargate** (con ALB) | EKS, ECS/EC2 | Cuando se necesita el ecosistema de Kubernetes o customizaciones pesadas |
| Kubernetes (workload complejo, multi-cloud) | **EKS** | Self-managed K8s, ECS | Equipos pequeños sin capacidad operacional K8s |
| Workload sustained/CPU-intensivo con costo optimizado | **EC2 (con Savings Plan)** | Fargate con SP, EKS on EC2 | Workload variable (serverless es mejor) |
| Batch processing | **AWS Batch** o **Step Functions + Lambda** | EMR (si Spark), ECS | Jobs simples que caben en cron (usar EventBridge) |
| ML training | **SageMaker Training Jobs** | EC2 con Deep Learning AMI | Batch corto y pequeño (SageMaker es overhead) |
| ML inference | **SageMaker Endpoints**, **Lambda** | EC2, ECS | Latencia crítica (Lambda tiene cold start) |
| Edge compute (latencia baja global) | **Lambda@Edge** o **CloudFront Functions** | — | Lógica pesada (límites de ejecución) |

**Graviton (ARM):** preferir para workloads compatibles — hasta 40% mejor costo-performance.

### Storage

| Caso de Uso | Servicio | Notas |
|---|---|---|
| Object storage (archivos, backups, estáticos) | **S3** (clases: Standard, IA, Glacier, Deep Archive) | Usar lifecycle policies; bloquear acceso público por defecto |
| Block storage para EC2 | **EBS** (gp3 > gp2; io2 para IOPS alta) | `encrypted: true` siempre |
| File storage compartido POSIX | **EFS** (General Purpose o Max I/O) | Usar cuando múltiples instancias necesitan el mismo filesystem |
| File storage Windows | **FSx for Windows** | SMB, Active Directory integrado |
| High-performance file (HPC, ML training) | **FSx for Lustre** | Integración con S3 |
| Backup gestionado | **AWS Backup** | Cross-region, cross-account, compliance reports |

**Tiering automático S3:** `Intelligent-Tiering` mueve objetos entre clases basado en acceso — ideal cuando el patrón de acceso es desconocido.

### Base de Datos

| Caso de Uso | Servicio | Cuándo preferir |
|---|---|---|
| Relacional transaccional (OLTP) | **Aurora** (MySQL o PostgreSQL compatible) | Alta disponibilidad, auto-scaling de storage, read replicas |
| Relacional simple / legacy | **RDS** (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server) | Paridad de features específica; costo más bajo que Aurora en small workloads |
| Serverless relacional | **Aurora Serverless v2** | Workload intermitente; evita provisionar instancia idle |
| NoSQL key-value / document con patrones conocidos | **DynamoDB** | Low latency, escala masiva, pricing predecible con provisioned |
| NoSQL document flexible | **DocumentDB** (MongoDB compatible) | Migración de MongoDB; queries flexibles |
| NoSQL wide-column | **Keyspaces** (Cassandra compatible) | Write-heavy, time-series |
| Graph | **Neptune** | Relaciones complejas, recomendaciones, fraud detection |
| Time-series | **Timestream** | IoT, métricas aplicacionales, costos optimizados para appends |
| Cache | **ElastiCache Redis** (primero) o **Memcached** | Low-latency, session storage, rate limiting |
| Data warehouse | **Redshift** (cluster) o **Redshift Serverless** | Analytics OLAP; petabyte scale |
| OLAP ad-hoc sobre S3 | **Athena** | Query SQL en datos S3 sin ETL; pay-per-query |
| Search (full-text) | **OpenSearch** | Logs, search en catálogos, monitoring |
| In-memory / transacciones extremas | **MemoryDB** | Durabilidad Redis con recovery rápido |

**Tip:** comenzar con Aurora Serverless v2 para workloads nuevas con tráfico incierto — flexibilidad con costo controlado.

### Messaging y Streaming

| Caso de Uso | Servicio | Notas |
|---|---|---|
| Cola de mensajes (point-to-point) | **SQS** (Standard o FIFO) | FIFO para garantía de orden y exactly-once |
| Pub/sub para fan-out (1:N) | **SNS** (con subscribers SQS, Lambda, HTTPS) | Combinado con SQS para durabilidad |
| Event bus desacoplado | **EventBridge** | Event-driven entre servicios; schema registry; rules con filtrado |
| Streaming de datos (high throughput, ordered) | **Kinesis Data Streams** | Analytics en tiempo real, custom consumers |
| Streaming gestionado (Kafka-compatible) | **MSK (Managed Streaming for Kafka)** | Migración de Kafka on-prem; ecosistema Kafka |
| Delivery de streams a S3/Redshift/OpenSearch | **Kinesis Data Firehose** | ETL ligero con transformación Lambda opcional |
| IoT ingestion | **IoT Core** | MQTT/HTTPS, device registry, rules |

**Patrón recomendado:** EventBridge como **event bus central** para comunicación entre bounded contexts (produce eventos CloudEvents — ver `warrior-kronos`).

### Network

| Caso de Uso | Servicio | Notas |
|---|---|---|
| VPC aislada | **VPC** con subnets públicas/privadas | Usar subnets privadas para workloads; públicas solo para NAT/ALB |
| Load balancer HTTP/HTTPS (L7) | **ALB** | WebSocket, HTTP/2, path-based routing, OIDC auth |
| Load balancer TCP/UDP (L4) | **NLB** | High performance, static IPs |
| Load balancer global cross-region | **Global Accelerator** | Anycast IPs, failover global |
| CDN + edge | **CloudFront** | Static assets, API caching, Origin Shield |
| DNS gestionado | **Route 53** | Health checks, failover, geolocation routing |
| Conectividad cross-VPC/account | **Transit Gateway** (scale) o VPC Peering (simple) | TGW para hub-and-spoke |
| Conectividad on-prem | **Direct Connect** (dedicado) o **Site-to-Site VPN** | DX para latencia/bandwidth predecible |
| API pública gestionada | **API Gateway** (REST, HTTP, WebSocket) | Throttling, auth, transformación |
| Endpoint privado para servicios AWS | **VPC Endpoints** (Gateway para S3/DynamoDB; Interface para otros) | Reduce NAT Gateway costs y mejora seguridad |

### Seguridad e Identidad

| Caso de Uso | Servicio |
|---|---|
| Gestión de identidad federada (SSO) | **IAM Identity Center** (ex-SSO) |
| Secretos rotables | **Secrets Manager** |
| Parámetros de configuración | **SSM Parameter Store** (SecureString para sensibles) |
| Gestión de claves de cifrado | **KMS** (CMK customer-managed recomendadas) |
| HSM dedicado | **CloudHSM** |
| WAF en ALB/CloudFront/API Gateway | **AWS WAF** |
| Protección DDoS | **Shield Standard** (free) + **Shield Advanced** para workloads críticos |
| Detección de amenazas | **GuardDuty** |
| Compliance tracking | **Config**, **Security Hub**, **Audit Manager** |
| Clasificación de datos sensibles | **Macie** |
| SIEM / investigación | **Security Lake** + CloudTrail + Athena |

### Observabilidad

| Caso de Uso | Servicio | Alternativas Externas |
|---|---|---|
| Métricas | **CloudWatch Metrics** | Datadog, New Relic |
| Logs | **CloudWatch Logs** | Datadog, Splunk |
| Tracing distribuido | **X-Ray** | Jaeger, Datadog APM |
| Dashboards | **CloudWatch Dashboards** o **Amazon Managed Grafana** | Grafana OSS |
| Alarms | **CloudWatch Alarms** → SNS → PagerDuty | PagerDuty, Opsgenie |
| Logs agregados multi-cuenta | **CloudWatch Cross-Account Observability** | Datadog, Splunk |

**Patrón recomendado:** OpenTelemetry SDK en la aplicación → X-Ray/CloudWatch como sink estándar AWS, o externo si el equipo ya lo usa.

### CI/CD

| Caso de Uso | Servicio | Alternativas |
|---|---|---|
| Pipeline nativo AWS | **CodePipeline** + **CodeBuild** + **CodeDeploy** | GitHub Actions (más popular) |
| Build aislado | **CodeBuild** | GitHub Actions, Buildkite |
| Deploy EC2/Lambda/ECS | **CodeDeploy** | Feature flags (LaunchDarkly) |
| Registry de container | **ECR** | — |
| IaC pipeline | **CodePipeline + CodeBuild con Terraform** o **CDK Pipelines** | Atlantis, Spacelift |

**Recomendación:** muchos equipos prefieren **GitHub Actions** por la integración natural con el repositorio; CodePipeline tiene sentido cuando compliance exige todo en AWS.

### Elección de Región

Factores de decisión:

1. **Latencia al usuario final** — región más cercana
2. **Disponibilidad de servicio** — no todo servicio está en toda región (ej.: Bedrock, Outposts)
3. **Costo** — varía por región (us-east-1 generalmente más barato)
4. **Compliance** — residencia de datos (LGPD puede exigir Brasil; GDPR puede exigir EU)
5. **Sustainability** — regiones con carbono bajo (`eu-west-2` London, `us-west-2` Oregon)

**Para Guardia (Brasil):** **sa-east-1** (São Paulo) para producción con datos sensibles de clientes; `us-east-1` para workloads globales o servicios no disponibles en São Paulo.

### Anti-patterns a evitar

| Anti-pattern | Problema | Alternativa |
|---|---|---|
| Usar EC2 para cada workload (legacy on-prem mindset) | Alto costo operacional, subutilización | Lambda, Fargate, servicios gestionados |
| Endpoint público en RDS/ElastiCache | Riesgo de seguridad | VPC privada + VPC Endpoints o bastion |
| NAT Gateway en single AZ para workload multi-AZ | Single point of failure | NAT Gateway por AZ (o aceptar costo + SLA) |
| CloudWatch Logs sin retención configurada | Costo explota con volumen | Definir retención (7/30/90 días) por log group |
| Security groups con `0.0.0.0/0` en puerto administrativo (22, 3389) | Superficie de ataque | Session Manager (SSM) para shell; sin SSH directo |
| Access keys IAM para humanos | Leak risk; hard rotation | IAM Identity Center (SSO) + AssumeRole temporal |
| Custom code para alta disponibilidad | Reinventar la rueda; bugs | Servicios gestionados con Multi-AZ built-in |

## Referencias

- `lex-aws-security`, `lex-aws-iac`, `lex-aws-cost` — Lexis aplicables
- `codex-aws-well-architected` — 6 pilares
- [AWS Documentation](https://docs.aws.amazon.com/)
- [AWS Architecture Center](https://aws.amazon.com/architecture/)
- [This is my architecture (YouTube series)](https://aws.amazon.com/this-is-my-architecture/)
