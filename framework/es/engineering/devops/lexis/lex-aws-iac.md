# Lexis: Infraestructura como Código (IaC) en AWS

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Toda provisión y cambio de infraestructura AWS a través de código versionado (Terraform, AWS CDK, CloudFormation, Pulumi)

## Propósito

Los cambios manuales en la consola AWS son invisibles, no versionados, difíciles de auditar e imposibles de reproducir entre ambientes. Un cambio "rápido" en la consola se convierte en deuda técnica: nadie sabe el estado real, los ambientes divergen, el rollback requiere memoria, y los desastres se vuelven accidentes sin rastro. Para los agentes IA, aceptar cambios manuales como estándar es construir una base inestable.

Esta Lexis existe para garantizar que **toda infraestructura AWS sea definida como código versionado**, que **los cambios pasen por pull request revisado**, que **los ambientes sean reproducibles** y que **el drift manual sea detectado y bloqueado**.

## Ley

> **Toda provisión o modificación de recursos AWS DEBE ser realizada vía IaC versionado en Git, aplicada a través de pipeline de CI/CD. Los cambios en la consola son permitidos solo para (a) investigación sin escritura, (b) respuesta a incidente crítico con registro retroactivo en IaC dentro de 24h. Los secretos y valores sensibles NO DEBEN estar en texto claro en IaC versionado.**

## Reglas

### 1. Una herramienta de IaC por proyecto

El proyecto **DEBE** adoptar **una** herramienta IaC principal y mantenerla consistente. Opciones válidas:

| Herramienta | Cuándo preferir |
|---|---|
| **Terraform** | Multi-cloud; ecosistema de providers; equipos familiarizados con HCL |
| **AWS CDK** | AWS-only; equipos fuertes en TS/Python; quieren abstracciones de alto nivel |
| **Pulumi** | Multi-cloud; quieren lenguaje de programación full |
| **CloudFormation** | AWS-only; quieren AWS-native sin dependencia externa |

Mezclar herramientas sin aislamiento claro (ej.: Terraform y CDK gestionando los mismos recursos) **está prohibido**.

### 2. State remoto y con lock

El agente **DEBE**:

1. **Terraform:** state en S3 con DynamoDB lock; nunca en local filesystem en producción; S3 bucket con versionamiento + encryption.
2. **CDK:** stacks con stack outputs en CloudFormation; state gestionado por AWS.
3. **Pulumi:** state en Pulumi Service o S3 backend.
4. **Ningún state en repositorio Git** — los states contienen datos sensibles.

### 3. Ambientes separados por workspace/stack

Cada ambiente (dev, staging, prod) **DEBE** tener state aislado:

- **Terraform:** workspaces o directorios separados + backends distintos
- **CDK:** stacks distintas (`Stack-dev`, `Stack-prod`) o accounts separadas
- **Pulumi:** stacks distintas por ambiente

**Nunca** compartir state entre ambientes.

### 4. Módulos reutilizables con versionamiento

Para componentes comunes (VPC, ECS cluster, RDS, ALB):

1. Extraer en **módulos versionados** (tags semver).
2. Consumir por versión pinnable, no `HEAD`.
3. Documentar inputs/outputs y ejemplos de uso.

```hcl
module "vpc" {
  source  = "git::https://github.com/guardia/terraform-modules.git//vpc?ref=v2.3.0"
  cidr    = "10.0.0.0/16"
  ...
}
```

### 5. Pipelines de CI/CD para aplicar cambios

Todo cambio de IaC **DEBE** pasar por:

1. **Plan** automático en el PR (`terraform plan`, `cdk diff`, `pulumi preview`) — visible en el PR para revisión.
2. **Linting y scanners de seguridad** (tfsec, checkov, cdk-nag) — ver `lex-aws-security`.
3. **Aprobación humana** para apply en producción (`terraform apply` vía pipeline tras merge + approval manual).
4. **Apply en dev/staging automático** tras merge (para iteración rápida).

### 6. Sin drift manual

1. **Drift detection** automatizado: ejecutar `terraform plan` diariamente en producción; alertar si hay divergencia.
2. **IAM policies restrictivas** para humanos en producción: limitar `Update*`, `Delete*`, `Create*` vía SCPs.
3. **Acceso break-glass**: role temporal con MFA + logging completo, para emergencias.
4. Los cambios manuales realizados en emergencia **DEBEN** ser registrados en IaC en hasta 24h.

### 7. Tagging consistente

Todo recurso **DEBE** recibir tags estándar:

```hcl
tags = {
  Environment = "prod"         # dev | staging | prod
  Owner       = "platform-team"
  Project     = "ahrena"
  CostCenter  = "engineering"
  ManagedBy   = "terraform"
  Lifecycle   = "persistent"   # persistent | temporary
}
```

Los tags son base para: cost allocation (`lex-aws-cost`), compliance, automatización.

### 8. Secretos fuera del IaC

El agente **NO PUEDE**:

1. Hardcoded secrets en archivos `.tf`, `.ts`, `.py` del IaC.
2. Secretos en `terraform.tfvars` commiteados.
3. Secretos en `CfnParameter` sin `NoEcho: true`.

El agente **DEBE**:

1. Crear el recurso `aws_secretsmanager_secret` vía IaC; poblar el **valor** fuera del IaC (vía CLI, pipeline step autorizado).
2. Referenciar secretos en runtime (`secretsmanager_secret_version.arn`); no retornar valor como output.

### 9. Recursos críticos con protección de delete

Los recursos stateful o críticos **DEBEN** tener protección:

```hcl
resource "aws_s3_bucket" "data" {
  # ...
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_db_instance" "main" {
  # ...
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "guardia-prod-final-${formatdate("YYYY-MM-DD", timestamp())}"
}
```

## Alcance

- **Se aplica a:** toda infraestructura AWS en todos los ambientes
- **Agentes vinculados:** `warrior-atlas`, agentes DevOps
- **Excepciones:**
  - Recursos experimentales en cuenta sandbox pueden ser manuales, si no persisten datos y son destruidos en 7 días
  - Acciones read-only en la consola para investigación (sin cambio de estado)

## Consecuencias de Violación

1. **Drift invisible:** el ambiente real difiere del código; los deploys fallan o sorprenden
2. **Pérdida de conocimiento:** el cambio manual desaparece cuando la persona se va; imposible de reproducir
3. **Falla de compliance:** SOC 2, ISO 27001 exigen trail de cambio; consola sin log es auditoría fallida
4. **Remediación:**
   - Ejecutar `terraform plan` para detectar drift; importar o ajustar código
   - Aplicar SCPs restringiendo cambios manuales en producción
   - Auditoría de CloudTrail para detectar quién hizo cambios manuales recientes

## Validación Automatizada

- **Herramienta:**
  - **Linting:** `terraform fmt`, `terraform validate`, `tflint`
  - **Plan en PRs:** `atlantis`, GitHub Actions, CodeBuild
  - **Drift:** cronjob con `terraform plan` en producción alertando diffs
  - **Policy:** OPA/Sentinel para reglas organizacionales (ej.: "todo S3 debe tener encryption")
- **Momento:** cada PR; diario (drift); CI/CD pipeline
- **Métrica:** 100% de los recursos en IaC; 0 drift no resuelto en >24h

## Referencias

- `lex-aws-security` — seguridad como parte del IaC
- `lex-aws-cost` — tagging para cost allocation
- `codex-aws-well-architected` — Pilar de Excelencia Operacional
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS CDK Best Practices](https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html)
