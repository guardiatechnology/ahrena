# Lexis: Segurança em AWS

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Segurança em arquitetura e infraestrutura AWS — IAM, criptografia, segredos, rede, auditoria

## Lei

> **Toda configuração AWS DEVE aplicar princípio de menor privilégio no IAM, criptografar dados em trânsito (TLS 1.2+) e em repouso (SSE-KMS), gerenciar segredos via Secrets Manager ou Parameter Store SecureString, habilitar CloudTrail no registro multi-região, e bloquear acesso público por padrão em S3 e RDS.**

## Regras

### 1. IAM com menor privilégio

O agente **DEVE**:

1. Criar roles e policies específicas por função; nunca usar `*:*` (admin total) exceto em emergência documentada.
2. Usar **roles** para serviços (EC2, Lambda, ECS) em vez de criar users com access keys.
3. Usar **session tokens** (AssumeRole) para acesso humano, não access keys estáticas.
4. Evitar policies `AWS managed` amplas (`AmazonS3FullAccess`) — preferir policies inline estreitas ou customer-managed.
5. Definir **condições** nas policies quando possível: `aws:SourceIp`, `aws:PrincipalOrgID`, `aws:RequestTag`.

```json
// ❌ Excessivamente permissivo
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*"
}

// ✅ Menor privilégio
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::guardia-refunds-prod/*",
  "Condition": {
    "StringEquals": { "aws:PrincipalOrgID": "o-abc123" }
  }
}
```

### 2. Criptografia em trânsito e em repouso

**Em trânsito:**

1. Todas as comunicações externas usam HTTPS/TLS 1.2+.
2. ALB/API Gateway configurados com políticas TLS modernas (sem TLS 1.0/1.1, sem RC4).
3. RDS e ElastiCache com `require_tls`.
4. Certificados via ACM (renovação automática); nunca usar self-signed em produção.

**Em repouso:**

1. **S3:** SSE-KMS (CMK customer-managed ou AWS-managed no mínimo); bloquear PUT sem criptografia via bucket policy.
2. **RDS/Aurora:** `storage_encrypted: true`, KMS key customer-managed preferencialmente.
3. **EBS:** `encrypted: true` em todos os volumes.
4. **DynamoDB:** encryption at rest habilitada (padrão; verificar em tabelas existentes).
5. **SNS/SQS:** `kms_master_key_id` para dados sensíveis.

### 3. Segredos via Secrets Manager ou Parameter Store

O agente **NÃO PODE**:

1. Armazenar credenciais, tokens ou API keys em:
   - Código-fonte
   - Variáveis de ambiente plain-text em Lambda/ECS/EC2 `user-data`
   - `.env` commitados
   - Arquivos de configuração no S3 sem criptografia
2. Usar credenciais estáticas de longa duração quando IAM roles servem.

O agente **DEVE**:

1. Usar **AWS Secrets Manager** para credenciais de BD, tokens de terceiros, chaves de API — com rotação automática habilitada.
2. Usar **SSM Parameter Store SecureString** para configurações sensíveis de menor criticidade (custo mais baixo).
3. Injetar segredos em runtime via:
   - Lambda: integração direta com Secrets Manager (SDK) ou extensão Lambda Secrets
   - ECS: `secrets` no task definition (não `environment`)
   - EKS: External Secrets Operator ou IRSA

### 4. Bloquear acesso público por padrão

O agente **DEVE**:

1. **S3:** aplicar `BlockPublicAccess` em todas as contas; buckets públicos (sites estáticos) são exceção explícita e documentada.
2. **RDS/Aurora:** `publicly_accessible: false` sempre; acesso via VPC privada.
3. **EC2:** security groups restritos; nunca `0.0.0.0/0` em porta administrativa (22, 3389).
4. **Lambda URLs:** usar AUTH_TYPE `AWS_IAM` quando possível; se pública, documentar justificativa.

### 5. Auditoria via CloudTrail

A conta AWS **DEVE** ter:

1. **CloudTrail multi-região habilitado**, com logs em bucket S3 criptografado e imutável (Object Lock).
2. **AWS Config** habilitado para rastrear mudanças de recursos.
3. **GuardDuty** habilitado para detecção de ameaças.
4. **CloudWatch alarms** para eventos críticos: root login, IAM policy changes, security group changes amplas, disabling de CloudTrail.
5. Logs retidos por pelo menos 1 ano (compliance) — normalmente 7 anos para setores regulados (financeiro).

### 6. Segregação de contas e redes

Para arquiteturas de produção:

1. **AWS Organizations** com OUs separadas (prod, staging, dev, security, log-archive).
2. **SCPs (Service Control Policies)** para restringir ações destrutivas e regiões não usadas.
3. **VPCs separadas** por ambiente; comunicação cross-VPC via peering, PrivateLink ou Transit Gateway com ACLs.
4. **Subnets privadas** para workloads; subnets públicas apenas para NAT/ALB.

### 7. Compliance e DLP

Para dados regulados (PII, financeiro, saúde):

1. **Macie** para detecção de PII em S3.
2. **VPC Flow Logs** e **S3 Access Logs** habilitados.
3. **KMS CMKs** com key policies específicas; rotação anual.
4. **Backup automatizado** com `aws backup` plans; retenção conforme RTO/RPO definidos.

## Validação Automatizada

- **Ferramenta:**
  - **Terraform:** `tfsec`, `checkov`, `terrascan`
  - **CDK:** `cdk-nag`
  - **AWS:** IAM Access Analyzer, Security Hub, Config Rules, GuardDuty
  - **CI:** rodar os scanners acima em cada PR de IaC
- **Momento:** cada PR de infra; semanalmente em ambientes existentes (drift detection)
- **Métrica:** 0 findings críticos ou altos em tfsec/cdk-nag; Security Hub score ≥ 80
