# Lexis: Seguridad en AWS

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Seguridad en arquitectura e infraestructura AWS — IAM, cifrado, secretos, red, auditoría

## Propósito

AWS ofrece recursos extensos, pero la responsabilidad compartida coloca la seguridad de la configuración en manos del usuario. Un bucket S3 público, un role IAM excesivamente permisivo, o una credencial en `user-data` pueden exponer datos sensibles, generar costos no autorizados o violar compliance (LGPD, PCI-DSS, SOC 2). Los agentes IA que diseñan o revisan arquitectura AWS necesitan aplicar principios de seguridad como requisito, no como capa adicional.

Esta Lexis existe para garantizar que **el principio de menor privilegio sea aplicado en todo acceso IAM**, que **los datos sensibles sean cifrados en tránsito y en reposo**, que **los secretos sean gestionados vía Secrets Manager o Parameter Store** (nunca en código o variables de entorno plain-text), que **los recursos expuestos públicamente sean explícitos** y que **todas las acciones sensibles sean auditadas vía CloudTrail**.

## Ley

> **Toda configuración AWS DEBE aplicar el principio de menor privilegio en IAM, cifrar datos en tránsito (TLS 1.2+) y en reposo (SSE-KMS), gestionar secretos vía Secrets Manager o Parameter Store SecureString, habilitar CloudTrail con registro multi-región, y bloquear el acceso público por defecto en S3 y RDS.**

## Reglas

### 1. IAM con menor privilegio

El agente **DEBE**:

1. Crear roles y policies específicas por función; nunca usar `*:*` (admin total) excepto en emergencia documentada.
2. Usar **roles** para servicios (EC2, Lambda, ECS) en vez de crear users con access keys.
3. Usar **session tokens** (AssumeRole) para acceso humano, no access keys estáticas.
4. Evitar policies `AWS managed` amplias (`AmazonS3FullAccess`) — preferir policies inline estrechas o customer-managed.
5. Definir **condiciones** en las policies cuando sea posible: `aws:SourceIp`, `aws:PrincipalOrgID`, `aws:RequestTag`.

```json
// ❌ Excesivamente permisivo
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*"
}

// ✅ Menor privilegio
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::guardia-refunds-prod/*",
  "Condition": {
    "StringEquals": { "aws:PrincipalOrgID": "o-abc123" }
  }
}
```

### 2. Cifrado en tránsito y en reposo

**En tránsito:**

1. Todas las comunicaciones externas usan HTTPS/TLS 1.2+.
2. ALB/API Gateway configurados con políticas TLS modernas (sin TLS 1.0/1.1, sin RC4).
3. RDS y ElastiCache con `require_tls`.
4. Certificados vía ACM (renovación automática); nunca usar self-signed en producción.

**En reposo:**

1. **S3:** SSE-KMS (CMK customer-managed o AWS-managed como mínimo); bloquear PUT sin cifrado vía bucket policy.
2. **RDS/Aurora:** `storage_encrypted: true`, KMS key customer-managed preferentemente.
3. **EBS:** `encrypted: true` en todos los volúmenes.
4. **DynamoDB:** encryption at rest habilitada (por defecto; verificar en tablas existentes).
5. **SNS/SQS:** `kms_master_key_id` para datos sensibles.

### 3. Secretos vía Secrets Manager o Parameter Store

El agente **NO PUEDE**:

1. Almacenar credenciales, tokens o API keys en:
   - Código fuente
   - Variables de entorno plain-text en Lambda/ECS/EC2 `user-data`
   - `.env` commiteados
   - Archivos de configuración en S3 sin cifrado
2. Usar credenciales estáticas de larga duración cuando IAM roles sirven.

El agente **DEBE**:

1. Usar **AWS Secrets Manager** para credenciales de BD, tokens de terceros, claves de API — con rotación automática habilitada.
2. Usar **SSM Parameter Store SecureString** para configuraciones sensibles de menor criticidad (costo más bajo).
3. Inyectar secretos en runtime vía:
   - Lambda: integración directa con Secrets Manager (SDK) o extensión Lambda Secrets
   - ECS: `secrets` en el task definition (no `environment`)
   - EKS: External Secrets Operator o IRSA

### 4. Bloquear acceso público por defecto

El agente **DEBE**:

1. **S3:** aplicar `BlockPublicAccess` en todas las cuentas; buckets públicos (sitios estáticos) son excepción explícita y documentada.
2. **RDS/Aurora:** `publicly_accessible: false` siempre; acceso vía VPC privada.
3. **EC2:** security groups restringidos; nunca `0.0.0.0/0` en puerto administrativo (22, 3389).
4. **Lambda URLs:** usar AUTH_TYPE `AWS_IAM` cuando sea posible; si es pública, documentar justificación.

### 5. Auditoría vía CloudTrail

La cuenta AWS **DEBE** tener:

1. **CloudTrail multi-región habilitado**, con logs en bucket S3 cifrado e inmutable (Object Lock).
2. **AWS Config** habilitado para rastrear cambios de recursos.
3. **GuardDuty** habilitado para detección de amenazas.
4. **CloudWatch alarms** para eventos críticos: root login, IAM policy changes, security group changes amplios, disabling de CloudTrail.
5. Logs retenidos por al menos 1 año (compliance) — normalmente 7 años para sectores regulados (financiero).

### 6. Segregación de cuentas y redes

Para arquitecturas de producción:

1. **AWS Organizations** con OUs separadas (prod, staging, dev, security, log-archive).
2. **SCPs (Service Control Policies)** para restringir acciones destructivas y regiones no usadas.
3. **VPCs separadas** por ambiente; comunicación cross-VPC vía peering, PrivateLink o Transit Gateway con ACLs.
4. **Subnets privadas** para workloads; subnets públicas solo para NAT/ALB.

### 7. Compliance y DLP

Para datos regulados (PII, financiero, salud):

1. **Macie** para detección de PII en S3.
2. **VPC Flow Logs** y **S3 Access Logs** habilitados.
3. **KMS CMKs** con key policies específicas; rotación anual.
4. **Backup automatizado** con `aws backup` plans; retención conforme a RTO/RPO definidos.

## Alcance

- **Se aplica a:** toda infraestructura AWS diseñada o revisada (IaC en Terraform/CDK/CloudFormation, cambios manuales vía consola cuando excepcionalmente autorizados)
- **Agentes vinculados:** `warrior-atlas` y cualquier otro agente que cree/modifique recursos AWS
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Breach de datos:** bucket S3 público o IAM permisivo pueden exponer datos de clientes — riesgo regulatorio (LGPD multa hasta 2% de la facturación) y de reputación
2. **Cuenta comprometida:** access keys en código son blanco de bots; en horas, un atacante puede provisionar recursos y generar millones en costo
3. **Falla de compliance:** auditoría SOC 2, PCI-DSS, ISO 27001 falla — impacto en certificaciones y contratos enterprise
4. **Remediación:**
   - Rotar credenciales comprometidas inmediatamente
   - Revisar logs CloudTrail para identificar accesos sospechosos
   - Aplicar IAM Access Analyzer para identificar policies amplias
   - Ejecutar Trusted Advisor, Security Hub, IAM Access Analyzer

## Validación Automatizada

- **Herramienta:**
  - **Terraform:** `tfsec`, `checkov`, `terrascan`
  - **CDK:** `cdk-nag`
  - **AWS:** IAM Access Analyzer, Security Hub, Config Rules, GuardDuty
  - **CI:** ejecutar los scanners anteriores en cada PR de IaC
- **Momento:** cada PR de infra; semanalmente en ambientes existentes (drift detection)
- **Métrica:** 0 findings críticos o altos en tfsec/cdk-nag; Security Hub score ≥ 80

## Referencias

- `codex-aws-well-architected` — Pilar de Seguridad detallado
- `codex-aws-services` — catálogo de servicios y recomendaciones
- `lex-aws-iac` — todo como código
- [AWS Security Best Practices](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
