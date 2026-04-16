# Lexis: AWS Security

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Security in AWS architecture and infrastructure — IAM, encryption, secrets, network, audit

## Purpose

AWS offers extensive resources, but the shared responsibility model places configuration security in the user's hands. A public S3 bucket, an overly permissive IAM role, or a credential in `user-data` can expose sensitive data, generate unauthorized costs, or violate compliance (LGPD, PCI-DSS, SOC 2). AI agents that design or review AWS architecture must apply security principles as a requirement, not as an additional layer.

This Lexis exists to ensure that **least privilege is applied across all IAM access**, that **sensitive data is encrypted in transit and at rest**, that **secrets are managed via Secrets Manager or Parameter Store** (never in code or plain-text environment variables), that **publicly exposed resources are explicit**, and that **all sensitive actions are audited via CloudTrail**.

## Law

> **Every AWS configuration MUST apply least privilege in IAM, encrypt data in transit (TLS 1.2+) and at rest (SSE-KMS), manage secrets via Secrets Manager or Parameter Store SecureString, enable CloudTrail with multi-region logging, and block public access by default in S3 and RDS.**

## Rules

### 1. IAM with least privilege

The agent **MUST**:

1. Create roles and policies specific to each function; never use `*:*` (full admin) except in a documented emergency.
2. Use **roles** for services (EC2, Lambda, ECS) instead of creating users with access keys.
3. Use **session tokens** (AssumeRole) for human access, not static access keys.
4. Avoid broad `AWS managed` policies (`AmazonS3FullAccess`) — prefer narrow inline policies or customer-managed.
5. Define **conditions** on policies whenever possible: `aws:SourceIp`, `aws:PrincipalOrgID`, `aws:RequestTag`.

```json
// ❌ Overly permissive
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*"
}

// ✅ Least privilege
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::guardia-refunds-prod/*",
  "Condition": {
    "StringEquals": { "aws:PrincipalOrgID": "o-abc123" }
  }
}
```

### 2. Encryption in transit and at rest

**In transit:**

1. All external communications use HTTPS/TLS 1.2+.
2. ALB/API Gateway configured with modern TLS policies (no TLS 1.0/1.1, no RC4).
3. RDS and ElastiCache with `require_tls`.
4. Certificates via ACM (automatic renewal); never use self-signed in production.

**At rest:**

1. **S3:** SSE-KMS (customer-managed CMK or AWS-managed at minimum); block PUT without encryption via bucket policy.
2. **RDS/Aurora:** `storage_encrypted: true`, customer-managed KMS key preferably.
3. **EBS:** `encrypted: true` on all volumes.
4. **DynamoDB:** encryption at rest enabled (default; verify on existing tables).
5. **SNS/SQS:** `kms_master_key_id` for sensitive data.

### 3. Secrets via Secrets Manager or Parameter Store

The agent **CANNOT**:

1. Store credentials, tokens, or API keys in:
   - Source code
   - Plain-text environment variables in Lambda/ECS/EC2 `user-data`
   - Committed `.env` files
   - Configuration files in S3 without encryption
2. Use long-lived static credentials when IAM roles suffice.

The agent **MUST**:

1. Use **AWS Secrets Manager** for DB credentials, third-party tokens, API keys — with automatic rotation enabled.
2. Use **SSM Parameter Store SecureString** for lower-criticality sensitive configurations (lower cost).
3. Inject secrets at runtime via:
   - Lambda: direct integration with Secrets Manager (SDK) or Lambda Secrets extension
   - ECS: `secrets` in task definition (not `environment`)
   - EKS: External Secrets Operator or IRSA

### 4. Block public access by default

The agent **MUST**:

1. **S3:** apply `BlockPublicAccess` on all accounts; public buckets (static sites) are an explicit, documented exception.
2. **RDS/Aurora:** `publicly_accessible: false` always; access via private VPC.
3. **EC2:** restricted security groups; never `0.0.0.0/0` on administrative ports (22, 3389).
4. **Lambda URLs:** use AUTH_TYPE `AWS_IAM` whenever possible; if public, document the rationale.

### 5. Auditing via CloudTrail

The AWS account **MUST** have:

1. **CloudTrail multi-region enabled**, with logs in an encrypted, immutable S3 bucket (Object Lock).
2. **AWS Config** enabled to track resource changes.
3. **GuardDuty** enabled for threat detection.
4. **CloudWatch alarms** for critical events: root login, IAM policy changes, broad security group changes, CloudTrail disabling.
5. Logs retained for at least 1 year (compliance) — typically 7 years for regulated sectors (financial).

### 6. Account and network segregation

For production architectures:

1. **AWS Organizations** with separate OUs (prod, staging, dev, security, log-archive).
2. **SCPs (Service Control Policies)** to restrict destructive actions and unused regions.
3. **Separate VPCs** per environment; cross-VPC communication via peering, PrivateLink, or Transit Gateway with ACLs.
4. **Private subnets** for workloads; public subnets only for NAT/ALB.

### 7. Compliance and DLP

For regulated data (PII, financial, health):

1. **Macie** for PII detection in S3.
2. **VPC Flow Logs** and **S3 Access Logs** enabled.
3. **KMS CMKs** with specific key policies; annual rotation.
4. **Automated backups** with `aws backup` plans; retention according to defined RTO/RPO.

## Applicability

- **Applies to:** all AWS infrastructure designed or reviewed (IaC in Terraform/CDK/CloudFormation, manual console changes when exceptionally authorized)
- **Bound agents:** `warrior-atlas` and any other agent that creates/modifies AWS resources
- **Exceptions:** None. Lexis do not admit exceptions.

## Consequences of Violation

1. **Data breach:** a public S3 bucket or permissive IAM can expose customer data — regulatory risk (LGPD fines up to 2% of revenue) and reputational damage
2. **Compromised account:** access keys in code are a target for bots; within hours, an attacker can provision resources and generate millions in cost
3. **Compliance failure:** SOC 2, PCI-DSS, ISO 27001 audit fails — impact on certifications and enterprise contracts
4. **Remediation:**
   - Rotate compromised credentials immediately
   - Review CloudTrail logs to identify suspicious access
   - Apply IAM Access Analyzer to identify broad policies
   - Run Trusted Advisor, Security Hub, IAM Access Analyzer

## Automated Validation

- **Tools:**
  - **Terraform:** `tfsec`, `checkov`, `terrascan`
  - **CDK:** `cdk-nag`
  - **AWS:** IAM Access Analyzer, Security Hub, Config Rules, GuardDuty
  - **CI:** run the above scanners on every IaC PR
- **When:** every infra PR; weekly in existing environments (drift detection)
- **Metric:** 0 critical or high findings in tfsec/cdk-nag; Security Hub score ≥ 80

## References

- `codex-aws-well-architected` — Security Pillar in detail
- `codex-aws-services` — service catalog and recommendations
- `lex-aws-iac` — everything as code
- [AWS Security Best Practices](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
