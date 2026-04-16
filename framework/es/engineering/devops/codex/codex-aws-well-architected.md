# Codex: AWS Well-Architected Framework

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Seis pilares del AWS Well-Architected Framework — referencia para diseñar y revisar arquitecturas AWS

## Visión General

El **AWS Well-Architected Framework** es el conjunto de principios, mejores prácticas y preguntas estructurales que AWS publica para guiar el diseño de workloads en la nube. Este Codex resume los 6 pilares, sus cuestiones clave y los trade-offs comunes, sirviendo como referencia para `warrior-atlas` al diseñar o revisar arquitecturas.

## Contexto

- **Dominio:** arquitectura de soluciones AWS
- **Público objetivo:** `warrior-atlas`, agentes DevOps, revisores de arquitectura
- **Actualización:** cuando AWS actualiza el framework (revisiones anuales) o cuando nuevos servicios cambian prácticas establecidas

## Contenido

### Los 6 pilares

1. **Operational Excellence** — Ejecutar y monitorear sistemas para entregar valor de negocio
2. **Security** — Proteger información, sistemas y activos
3. **Reliability** — Los workloads se ejecutan conforme a lo esperado, consistentemente y a escala
4. **Performance Efficiency** — Uso eficiente de recursos computacionales
5. **Cost Optimization** — Evitar costos innecesarios
6. **Sustainability** — Minimizar impacto ambiental

### Pilar 1 — Operational Excellence

**Principios de diseño:**

- Operaciones como código (IaC, automatización de runbooks)
- Hacer cambios frecuentes, pequeños y reversibles
- Refinar procedimientos operacionales con frecuencia
- Anticipar fallas (game days, chaos engineering)
- Aprender de las fallas (post-mortem sin blame)

**Preguntas clave:**

1. ¿Cómo entiende la organización su workload en producción? (métricas, logs, traces)
2. ¿Cómo responde a eventos (alerts) e incidentes?
3. ¿Cómo evoluciona los procedimientos operacionales?

**Prácticas esenciales:**

- **IaC** vía Terraform/CDK (ver `lex-aws-iac`)
- **CI/CD** con pipelines automatizados, blue/green o canary deploys
- **Observabilidad** completa: métricas (CloudWatch), logs (CloudWatch Logs), traces (X-Ray / OpenTelemetry)
- **Runbooks** versionados para incidents frecuentes
- **Game days** cuatrimestrales para ejercitar failure scenarios

### Pilar 2 — Security

**Principios de diseño:**

- Implementar identidad fuerte (MFA, least privilege)
- Habilitar rastreabilidad (CloudTrail, Config)
- Aplicar seguridad en todas las capas (defense in depth)
- Automatizar mejores prácticas de seguridad
- Proteger datos en tránsito y en reposo
- Mantener a las personas alejadas de los datos (acceso programático)
- Prepararse para eventos de seguridad (IR plan)

**Preguntas clave:**

1. ¿Cómo opera su workload de forma segura?
2. ¿Cómo gestiona identidades para personas y máquinas?
3. ¿Cómo detecta e investiga eventos de seguridad?
4. ¿Cómo protege su infraestructura (red, compute)?
5. ¿Cómo clasifica y protege datos?

**Prácticas esenciales:**

- **AWS Organizations** con SCPs y OUs separadas
- **IAM** con roles + Identity Center (SSO) para humanos; IRSA para workloads Kubernetes
- **KMS** para claves gestionadas; rotación automática
- **Secrets Manager** / **Parameter Store SecureString** para secretos
- **VPC** con subnets privadas; Security Groups específicos; WAF para APIs públicas
- **CloudTrail + GuardDuty + Security Hub + Macie** — detección y compliance

> Ver `lex-aws-security` para reglas inviolables.

### Pilar 3 — Reliability

**Principios de diseño:**

- Automatizar recuperación de fallas
- Probar procedimientos de recuperación
- Escalar horizontalmente para aumentar disponibilidad
- Dejar de adivinar capacidad (auto-scaling)
- Gestionar cambios vía automatización

**Preguntas clave:**

1. ¿Cómo entiende demanda y capacidad?
2. ¿Cómo maneja fallas de componente?
3. ¿Cómo se recupera de desastres?

**Prácticas esenciales:**

- **Multi-AZ** como estándar para producción (RDS, ElastiCache, ECS, EKS)
- **Multi-Region** para workloads tier-1 (RPO/RTO definidos explícitamente)
- **Auto-scaling** por métricas relevantes (CPU, custom metrics, target tracking)
- **Health checks** en ALB/NLB + Route 53; failover automático
- **Backup** vía AWS Backup con RPO definido; pruebas de restore periódicas
- **Circuit breakers** y graceful degradation en capas de servicio
- **Chaos engineering** (AWS Fault Injection Simulator) para validar resiliencia

**RTO/RPO de referencia por criticidad:**

| Tier | RTO | RPO | Arquitectura típica |
|---|---|---|---|
| Tier 1 (crítico, financiero) | <1h | <5min | Multi-region active-active |
| Tier 2 (importante) | <4h | <1h | Multi-AZ + backup cross-region |
| Tier 3 (business-hours) | <24h | <24h | Multi-AZ; backup diario |
| Tier 4 (interno) | <72h | <24h | Single-AZ con backup |

### Pilar 4 — Performance Efficiency

**Principios de diseño:**

- Democratizar tecnologías avanzadas (usar servicios gestionados)
- Globalizar en minutos (CloudFront, multi-region)
- Usar arquitecturas serverless para reducir operación
- Experimentar con frecuencia
- Considerar la simpatía mecánica (elegir el servicio correcto para el problema)

**Preguntas clave:**

1. ¿Cómo selecciona la arquitectura de compute/storage/DB/network?
2. ¿Cómo evoluciona conforme surgen nuevas tecnologías?
3. ¿Cómo monitorea recursos para garantizar performance?

**Elecciones comunes por workload:**

| Workload | Elección recomendada |
|---|---|
| API HTTP con tráfico variable | API Gateway + Lambda (serverless) o ECS Fargate + ALB |
| API HTTP con tráfico alto sustained | ECS on EC2 (con RI) o EKS |
| Procesamiento de eventos asíncrono | SQS + Lambda o Kinesis + Lambda |
| Stream processing pesado | Kinesis Data Analytics, MSK (Kafka gestionado), Glue Streaming |
| Batch processing | Batch, Step Functions + Lambda, EMR |
| ML training/inference | SageMaker |
| BD relacional transaccional | Aurora (MySQL/PostgreSQL-compatible) > RDS > self-managed |
| BD NoSQL con patrones conocidos | DynamoDB |
| Full-text search | OpenSearch; si es pequeño, RDS con extensiones |
| Cache | ElastiCache (Redis/Memcached) |
| Entrega global de assets | CloudFront + S3 |

### Pilar 5 — Cost Optimization

> Ver `lex-aws-cost` para reglas inviolables y prácticas detalladas.

**Principios de diseño:**

- Implementar cloud financial management
- Adoptar modelo de consumo (pay for what you use)
- Medir eficiencia general
- Dejar de gastar en heavy lifting no diferenciado (usar servicios gestionados)
- Analizar y atribuir gastos

**Prácticas esenciales:**

- Tagging completo + Cost Explorer
- Budgets + Anomaly Detection
- Savings Plans y Reserved Instances para workload predecible
- Spot para cargas tolerantes
- Right-sizing trimestral vía Compute Optimizer + Trusted Advisor
- Lifecycle policies en S3; retention en logs
- Auto-shutdown de dev/staging fuera de horario

### Pilar 6 — Sustainability

**Principios de diseño:**

- Comprender el impacto
- Establecer metas de sustentabilidad
- Maximizar utilización (consolidar workloads)
- Anticipar y adoptar ofertas más eficientes
- Usar servicios gestionados (operan con mayor eficiencia que equivalentes self-hosted)
- Reducir impacto downstream (comprimir, paginar, etc.)

**Prácticas esenciales:**

- **Regiones con baja intensidad de carbono:** preferir regiones AWS alimentadas por energía renovable (ver Customer Carbon Footprint Tool)
- **ARM (Graviton)** para instancias EC2/Lambda/RDS — ~40% más eficiente en energía
- **Serverless** reduce waste de compute ocioso
- **Datos:** lifecycle agresivo para archivos antiguos; eliminar datos no usados
- **Imágenes y assets:** formatos modernos (WebP, AVIF); CDN para reducir transferencia

### Trade-offs comunes

Diseñar es balancear pilares. Trade-offs típicos:

| Trade-off | Ejemplo |
|---|---|
| Reliability ↔ Cost | Multi-region duplica costo; justificado solo para workload crítico |
| Performance ↔ Cost | Una instancia mayor es más rápida pero cuesta más; right-sizing busca el punto óptimo |
| Security ↔ Operational simplicity | Más capas de security (WAF, Shield, GuardDuty) aumentan operación |
| Sustainability ↔ Performance | Graviton es más eficiente pero puede requerir compatibility testing |

La arquitectura **DEBE documentar el trade-off elegido** — típicamente vía ADR cuando es estructural (`kata-adr-write`).

### Well-Architected Tool

AWS ofrece la **Well-Architected Tool** (gratis) que guía la revisión de workloads respondiendo a las preguntas de los 6 pilares y generando plan de mejora. Recomendado:

1. Ejecutar review en workloads nuevos (tras go-live) y tier-1 anualmente.
2. Ejecutar **Well-Architected Lenses** específicos: Serverless, SaaS, Machine Learning, Financial Services.
3. Registrar high-risk issues (HRIs) y tratarlos como deuda prioritaria.

## Referencias

- `lex-aws-security` — Pilar de Seguridad como leyes
- `lex-aws-cost` — Pilar de Costo como leyes
- `lex-aws-iac` — Pilar de Operational Excellence
- `codex-aws-services` — servicios y elecciones por caso de uso
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Well-Architected Tool](https://aws.amazon.com/well-architected-tool/)
