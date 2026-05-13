# Lexis: Conciencia de Costo en AWS

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Diseño y operación de infraestructura AWS con atención al costo — tagging, right-sizing, monitoreo de gasto, prevención de sorpresas

## Propósito

AWS cobra por lo que se provisiona, no por lo que se usa — una instancia `r6i.4xlarge` encendida el fin de semana genera US$ 800/mes incluso ociosa. Sin disciplina de costo, es trivial provisionar arquitecturas que funcionan pero sangran dinero: instancias sobredimensionadas, datos en S3 Standard cuando deberían estar en Glacier, DynamoDB en modo on-demand para workload predecible, NAT Gateways en cada AZ sin necesidad. Los agentes IA que diseñan AWS necesitan incluir el eje de costo junto con performance y seguridad.

Esta Lexis existe para garantizar que **todo recurso sea tagueado para cost allocation**, que **las elecciones tengan conciencia de costo explícita**, que **los budgets y alarmas estén configurados** y que **el uso sea revisado periódicamente para right-sizing**.

## Ley

> **Toda arquitectura AWS DEBE ser diseñada con conciencia de costo explícita. Todo recurso DEBE tener tags de cost allocation (`CostCenter`, `Environment`, `Project`, `Owner`). Los budgets con alertas DEBEN ser configurados por ambiente. Las elecciones con impacto de costo >US$ 100/mes DEBEN ser documentadas con alternativas consideradas.**

## Reglas

### 1. Tagging para cost allocation

Todo recurso taxable **DEBE** tener tags mínimos:

```hcl
tags = {
  CostCenter  = "engineering" | "product" | "marketing" | ...
  Environment = "dev" | "staging" | "prod"
  Project     = "ahrena" | "refund-service" | ...
  Owner       = "team-name@guardia.com"
}
```

1. **Cost allocation tags** habilitados en Billing Console.
2. **Cost Explorer** configurado para desglose por tag.
3. **Reports mensuales** por `CostCenter` y `Environment`.
4. Los recursos **sin tags** en producción son bloqueados por SCP o Config Rule.

### 2. Elecciones con conciencia de costo

Al elegir recursos, el agente **DEBE** considerar:

| Decisión | Cuestión de costo |
|---|---|
| Compute: EC2 vs. Lambda vs. Fargate vs. EKS | ¿Cuál es el patrón de uso? Sustained → EC2 reservado. Bursty/sparse → Lambda. Container consistent → Fargate. Orchestration compleja → EKS |
| Storage: S3 Standard vs. IA vs. Glacier vs. Deep Archive | ¿Frecuencia de acceso? Standard para <30 días; IA 30-90; Glacier >90 con retrieve esporádico; Deep Archive para compliance |
| DB: RDS on-demand vs. reserved; DynamoDB on-demand vs. provisioned | Workload predecible → reserved/provisioned (hasta 60% de ahorro); impredecible → on-demand |
| Network: NAT Gateway vs. NAT Instance vs. VPC Endpoints | NAT Gateway es caro (~US$ 32/mes/AZ + transfer); usar VPC endpoints para S3/DynamoDB; consolidar NAT cuando el tráfico lo permite |
| Data Transfer | Cross-AZ, cross-region y egress a internet tienen costos distintos; evitar tráfico innecesario entre AZs |

Las decisiones con impacto previsto **>US$ 100/mes** deben ser registradas (ADR cuando es estructuralmente relevante — ver `codex-issue-workflow`).

### 3. Budgets y alarmas

Cada cuenta/ambiente **DEBE** tener:

1. **AWS Budgets** configurado con:
   - Budget mensual por `Environment` (prod, staging, dev)
   - Alertas al 50%, 80%, 100% del límite
   - Alertas al 50%, 80%, 100% del **forecast** (previsión de mes cerrado)
2. **Anomaly Detection** habilitado (AWS Cost Anomaly Detection).
3. **CloudWatch billing alarm** para spike general (ej.: >20% vs mes anterior).
4. Las alertas van al canal del equipo responsable (Slack, email de on-call).

### 4. Right-sizing periódico

Rutina de revisión (trimestral como mínimo):

1. **Compute Optimizer:** identifica instancias EC2, EBS, Lambda sub/super-dimensionadas.
2. **Trusted Advisor Cost Optimization:** lista RIs/Savings Plans subutilizados, instancias ociosas, IPs elásticos no asociados.
3. **Unused resources:** volúmenes EBS no anexados, snapshots antiguos, load balancers sin targets, NAT Gateways en VPCs sin tráfico.
4. **Logs y backups:** CloudWatch Logs con retención indefinida acumulan costo; definir retención por ambiente.

### 5. Reserved Instances / Savings Plans / Spot

Para workload predecible y sustained:

1. **Savings Plans** (preferencial por flexibilidad) — compute, EC2 Instance, SageMaker.
2. **Reserved Instances** para RDS, ElastiCache, DynamoDB, Redshift.
3. **Spot Instances** para cargas tolerantes a interrupción (batch, ML training, CI).

Cobertura-objetivo: **70%+** del compute sustained en Savings Plans/RIs.

### 6. Patterns a evitar (cost smells)

| Pattern | Por qué evitar |
|---|---|
| NAT Gateway por AZ sin justificación | Cada uno cuesta ~US$ 32/mes + transfer; consolidar si una AZ lo soporta |
| Log retention infinita en CloudWatch | CW Logs cuesta por GB almacenado; mover a S3 con lifecycle para Glacier |
| DynamoDB on-demand para workload alto y constante | On-demand es ~7x más caro que provisioned para workload predecible |
| S3 sin lifecycle policy | Los buckets crecen indefinidamente; definir transiciones para IA/Glacier |
| Elastic IPs no asociados | Cobrados por hora cuando no se usan (~US$ 3.6/mes cada uno) |
| Snapshots EBS sin retention policy | Acumulan mensualmente; definir política (ej.: diarios 7 días, semanales 4 sem, mensuales 12 meses) |
| ALB/NLB sin targets | Cobrados mensualmente incluso sin tráfico |
| Cross-region replication sin necesidad real | Cada GB replicado es cobrado 2x (origen + destino) |
| Dev/staging idénticos a prod en tamaño | Dev/staging deben estar mínimamente dimensionados; auto-stop fuera del horario comercial |

### 7. Estimación antes de provisionar

Antes de provisionar arquitectura nueva o expandir existente significativamente:

1. Estimar costo mensual vía **AWS Pricing Calculator**.
2. Comparar con el budget del ambiente.
3. Si excede en >20% el budget actual: justificar o rediseñar.
4. Incluir estimación en `.ahrena/issues/{n}/03-architecture.md` cuando esté en el flujo Issue-Driven.

## Alcance

- **Se aplica a:** todo provisionamiento y rediseño de infraestructura AWS
- **Agentes vinculados:** `warrior-atlas`, agentes DevOps
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Gastos inesperados:** costo mensual se duplica sin justificación; impacto en unit economics e inversiones
2. **Asignación errada:** sin tags, imposible atribuir costo a producto/equipo; las decisiones de priorización quedan ciegas
3. **Sorpresas en facturas:** sin budgets, el spike de costo solo es detectado al cierre del mes
4. **Remediación:**
   - Ejecutar Cost Explorer + Trusted Advisor inmediatamente
   - Identificar top 10 contribuyentes de costo; right-size o apagar
   - Aplicar tags retroactivamente y activar cost allocation
   - Configurar budgets con alertas agresivas

## Validación Automatizada

- **Herramienta:**
  - **Pricing Calculator** (manual o integrado al CI)
  - **Infracost** (costo estimado en PR de Terraform)
  - **AWS Cost Explorer + Anomaly Detection**
  - **Trusted Advisor** (requiere Business/Enterprise Support)
  - **Compute Optimizer** (free)
- **Momento:** cada PR de infra (Infracost); diariamente (anomaly); mensualmente (review manual)
- **Métrica:** 100% de recursos con cost allocation tags; budgets en todas las cuentas; desviación mensual <15% de lo previsto

## Referencias

- `codex-aws-well-architected` — Pilar de Optimización de Costo
- `codex-aws-services` — guía de elección por caso de uso
- `lex-aws-iac` — tagging vía IaC
- [AWS Pricing Calculator](https://calculator.aws)
- [AWS Well-Architected Cost Optimization Pillar](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html)
