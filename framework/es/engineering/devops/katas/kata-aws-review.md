# Kata: Revisar Arquitectura o IaC AWS

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Revisión sistemática de arquitectura AWS o cambios de IaC (Terraform, CDK, CloudFormation) contra Lexis y Well-Architected Framework

## Objetivo

Ejecutar revisión de arquitectura AWS (documento de diseño o diff de IaC), verificando adherencia a las Lexis aplicables (`lex-aws-security`, `lex-aws-iac`, `lex-aws-cost`), a los 6 pilares del Well-Architected y a las prácticas del catálogo de servicios. Produce reporte estructurado con hallazgos categorizados por severidad, aplicable en PR review o como revisión periódica de infraestructura existente.

## Cuándo Usar

- Revisión de PR de IaC antes del merge
- Revisión de documento de arquitectura (antes del Gate 1 en el flujo Issue-Driven)
- Auditoría periódica de cuenta/workload existente
- Preparación para AWS Well-Architected Review formal

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-----------|
| Objetivo | Sí | PR de IaC (`git diff`) o documento `03-architecture.md` o cuenta/workload existente |
| Alcance | Sí | Componentes a revisar — full review o foco en un pilar |
| Contexto | No | Requisitos originales, SLAs, compliance aplicable |

## Workflow

```
Progreso:
- [ ] 1. Recopilar objetivo y contexto
- [ ] 2. Revisar Security (lex-aws-security)
- [ ] 3. Revisar IaC (lex-aws-iac)
- [ ] 4. Revisar Cost (lex-aws-cost)
- [ ] 5. Revisar Reliability
- [ ] 6. Revisar Performance
- [ ] 7. Revisar Operational Excellence
- [ ] 8. Consolidar reporte por severidad
```

### Paso 1: Recopilar objetivo y contexto

Dependiendo del tipo:

- **PR de IaC:** obtener `git diff`; identificar recursos creados/modificados/removidos; stack (Terraform vs CDK vs CloudFormation).
- **Documento de arquitectura:** leer `03-architecture.md`; extraer componentes y elecciones.
- **Workload existente:** inventario vía **Config**, **Resource Explorer**, tags.

Leer requisitos originales cuando estén disponibles para contextualizar decisiones.

### Paso 2: Revisar Security

Contra `lex-aws-security`:

- [ ] ¿IAM roles con menor privilegio? ¿Sin `*:*` o policies managed amplias?
- [ ] ¿Acceso público bloqueado en S3, RDS, ElastiCache?
- [ ] ¿Cifrado en reposo habilitado en S3/RDS/EBS/DynamoDB?
- [ ] ¿Cifrado en tránsito (TLS 1.2+) en ALB/API Gateway?
- [ ] ¿Secretos vía Secrets Manager/Parameter Store? ¿Sin hardcoded?
- [ ] ¿CloudTrail habilitado multi-región?
- [ ] ¿Security Groups sin `0.0.0.0/0` en puertos administrativos?
- [ ] ¿KMS CMKs en vez de AWS-managed donde corresponde?
- [ ] Ejecutar `tfsec` / `cdk-nag` y capturar findings

Severidad de ejemplo: S3 público sin justificación → **crítica**; ausencia de CloudTrail → **alta**; KMS AWS-managed en vez de CMK → **media**.

### Paso 3: Revisar IaC

Contra `lex-aws-iac`:

- [ ] ¿Todo como código (ninguna creación manual en la consola)?
- [ ] ¿State remoto con lock? ¿Nunca en Git?
- [ ] ¿Ambientes separados (workspaces/stacks distintas)?
- [ ] ¿Tagging estandarizado aplicado?
- [ ] ¿Módulos versionados (sin `ref=main`)?
- [ ] ¿Recursos críticos con `prevent_destroy` / `deletion_protection`?
- [ ] ¿Secretos fuera de los archivos IaC versionados?
- [ ] ¿Pipeline con `plan` visible en PR + apply automatizado?

### Paso 4: Revisar Cost

Contra `lex-aws-cost`:

- [ ] ¿Tags de cost allocation presentes? (`CostCenter`, `Environment`, `Project`, `Owner`)
- [ ] ¿Elecciones de compute apropiadas al patrón de uso? (Lambda vs Fargate vs EC2)
- [ ] ¿Storage classes adecuadas? (S3 Standard vs IA vs Glacier con lifecycle)
- [ ] ¿NAT Gateway compartido cuando es posible (no uno por AZ sin necesidad)?
- [ ] ¿Reservado/Savings Plan considerado para workload sustained?
- [ ] ¿Retention en CloudWatch Logs definida?
- [ ] ¿Budget configurado?
- [ ] Ejecutar `infracost` para estimar el costo del diff

### Paso 5: Revisar Reliability

Contra `codex-aws-well-architected` (Pilar Reliability):

- [ ] ¿Multi-AZ habilitado en RDS, ECS service, ElastiCache, NAT Gateway?
- [ ] ¿Auto-scaling configurado con métricas adecuadas?
- [ ] ¿Health checks en ALB + Route 53?
- [ ] ¿Backup automatizado vía AWS Backup? ¿Retención coherente con RPO?
- [ ] DR plan: ¿multi-region si es tier-1? ¿RTO/RPO documentados y probados?
- [ ] ¿Dead-letter queues en colas y Lambda para evitar pérdida silenciosa?
- [ ] ¿Circuit breakers o retries con backoff en integraciones externas?

### Paso 6: Revisar Performance

Contra `codex-aws-well-architected` (Pilar Performance):

- [ ] ¿El servicio elegido es el correcto para el patrón de tráfico?
- [ ] ¿Instancias right-sized (no sobre/sub-dimensionadas)?
- [ ] ¿Cache (CloudFront, ElastiCache) para reducir latencia y carga en el backend?
- [ ] ¿VPC Endpoints para S3/DynamoDB para evitar NAT Gateway y mejorar latencia?
- [ ] ¿Auto-scaling reactivo (ej.: target tracking) en vez de fijo?
- [ ] ¿Graviton (ARM) considerado para workloads compatibles?

### Paso 7: Revisar Operational Excellence

- [ ] ¿Logs, métricas, traces configurados (CloudWatch, X-Ray)?
- [ ] ¿Alarmas CloudWatch para eventos críticos (high error rate, latency breach)?
- [ ] ¿Dashboards operacionales creados?
- [ ] ¿Runbooks documentados para incidents predecibles?
- [ ] ¿Deploy con blue/green o canary (CodeDeploy, ECS deployment controllers)?
- [ ] ¿Rollback automático en caso de health check failure?

### Paso 8: Consolidar reporte por severidad

Estructurar hallazgos:

```markdown
# AWS Architecture Review — {objetivo}

- **Fecha:** {YYYY-MM-DD}
- **Alcance:** {componentes o diff}
- **Hallazgos:** {C} críticos, {A} altos, {M} medios, {B} bajos

## Resumen por Pilar

| Pilar | Críticos | Altos | Medios | Bajos |
|---|:-:|:-:|:-:|:-:|
| Security | 0 | 1 | 2 | 1 |
| Reliability | 0 | 0 | 1 | 0 |
| Performance | 0 | 0 | 0 | 2 |
| Cost | 0 | 1 | 3 | 2 |
| Operational | 0 | 0 | 1 | 0 |
| Sustainability | 0 | 0 | 0 | 1 |

## Hallazgos Críticos

### A-1: S3 bucket público sin justificación
- **Pilar:** Security
- **Ubicación:** `infra/modules/assets/main.tf:42`
- **Problema:** `block_public_acls = false` y `block_public_policy = false`; el bucket almacena datos internos
- **Recomendación:** habilitar `Block Public Access` y mover assets públicos a un bucket dedicado con política explícita
- **Referencia:** `lex-aws-security` §4

## Hallazgos Altos

### A-2: ...

## Hallazgos Medios

### A-3: ...

## Recomendaciones Adicionales (no bloqueantes)

- ...

## Resumen Positivo

{2-3 puntos bien ejecutados}

## Estimación de Costo (Infracost)

Cambio neto: +US$ 420/mes
- +Aurora Serverless v2 baseline: +US$ 280
- +ALB: +US$ 22
- +NAT Gateway (new AZ): +US$ 32
- +Data transfer estimado: +US$ 86
```

## Salidas

| Salida | Formato | Destino |
|-------|---------|---------|
| Reporte de revisión | Markdown estructurado | Respuesta al usuario o `docs/reviews/{fecha}-aws-review.md` |
| Comentarios en PR | Inline comments vía GitHub MCP | PR (opcional) |
| Plan de mejora | Lista priorizada de acciones | Parte del reporte |

## Restricciones

- **Revisión ≠ modificación:** este kata reporta; las correcciones son hechas por el DevOps/equipo responsable en una nueva iteración.
- **Severidad objetiva:** crítico = viola Lexis o causa riesgo inmediato; alto = contra Well-Architected; medio/bajo = mejora incremental.
- **Evidencia concreta:** cada hallazgo tiene ubicación (archivo:línea o recurso) y referencia a Lexis/Codex.
- **Tono constructivo:** señalar problema + solución; no es auditoría punitiva.

## Referencias

- `lex-aws-security`, `lex-aws-iac`, `lex-aws-cost`
- `codex-aws-well-architected` — 6 pilares detallados
- `codex-aws-services` — catálogo para comparar elecciones
- `kata-quality-gate` — integra al flujo Issue-Driven
- `kata-mcp-github-read` — para revisar PR remoto
