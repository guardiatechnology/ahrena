# Lexis: Infrastructure as Code (IaC) in AWS

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All provisioning and modification of AWS infrastructure through versioned code (Terraform, AWS CDK, CloudFormation, Pulumi)

## Purpose

Manual changes in the AWS console are invisible, unversioned, hard to audit, and impossible to reproduce across environments. A "quick" console change becomes technical debt: no one knows the real state, environments diverge, rollback requires memory, and disasters become untraceable accidents. For AI agents, accepting manual changes as standard is building on an unstable foundation.

This Lexis exists to ensure that **all AWS infrastructure is defined as versioned code**, that **changes go through a reviewed pull request**, that **environments are reproducible**, and that **manual drift is detected and blocked**.

## Law

> **Every provisioning or modification of AWS resources MUST be done via IaC versioned in Git, applied through a CI/CD pipeline. Console changes are permitted only for (a) read-only investigation, (b) critical incident response with retroactive registration in IaC within 24h. Secrets and sensitive values MUST NOT be in plain text in versioned IaC.**

## Rules

### 1. One IaC tool per project

The project **MUST** adopt **one** primary IaC tool and keep it consistent. Valid choices:

| Tool | When to prefer |
|---|---|
| **Terraform** | Multi-cloud; provider ecosystem; teams familiar with HCL |
| **AWS CDK** | AWS-only; teams strong in TS/Python; want high-level abstractions |
| **Pulumi** | Multi-cloud; want a full programming language |
| **CloudFormation** | AWS-only; want AWS-native with no external dependency |

Mixing tools without clear isolation (e.g., Terraform and CDK managing the same resources) **is prohibited**.

### 2. Remote state with locking

The agent **MUST**:

1. **Terraform:** state in S3 with DynamoDB lock; never on local filesystem in production; S3 bucket with versioning + encryption.
2. **CDK:** stacks with stack outputs in CloudFormation; state managed by AWS.
3. **Pulumi:** state in Pulumi Service or S3 backend.
4. **No state in Git repository** — states contain sensitive data.

### 3. Separate environments per workspace/stack

Each environment (dev, staging, prod) **MUST** have isolated state:

- **Terraform:** workspaces or separate directories + distinct backends
- **CDK:** distinct stacks (`Stack-dev`, `Stack-prod`) or separate accounts
- **Pulumi:** distinct stacks per environment

**Never** share state across environments.

### 4. Reusable, versioned modules

For common components (VPC, ECS cluster, RDS, ALB):

1. Extract into **versioned modules** (semver tags).
2. Consume by pinnable version, not `HEAD`.
3. Document inputs/outputs and usage examples.

```hcl
module "vpc" {
  source  = "git::https://github.com/guardia/terraform-modules.git//vpc?ref=v2.3.0"
  cidr    = "10.0.0.0/16"
  ...
}
```

### 5. CI/CD pipelines to apply changes

Every IaC change **MUST** go through:

1. **Automatic plan** on the PR (`terraform plan`, `cdk diff`, `pulumi preview`) — visible in the PR for review.
2. **Linting and security scanners** (tfsec, checkov, cdk-nag) — see `lex-aws-security`.
3. **Human approval** for production apply (`terraform apply` via pipeline after merge + manual approval).
4. **Automatic apply in dev/staging** after merge (for fast iteration).

### 6. No manual drift

1. **Automated drift detection:** run `terraform plan` daily in production; alert if divergence exists.
2. **Restrictive IAM policies** for humans in production: limit `Update*`, `Delete*`, `Create*` via SCPs.
3. **Break-glass access:** temporary role with MFA + full logging, for emergencies.
4. Manual changes made during an emergency **MUST** be registered in IaC within 24h.

### 7. Consistent tagging

Every resource **MUST** receive standard tags:

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

Tags are the foundation for: cost allocation (`lex-aws-cost`), compliance, automation.

### 8. Secrets outside of IaC

The agent **CANNOT**:

1. Hardcode secrets in `.tf`, `.ts`, `.py` IaC files.
2. Commit secrets in `terraform.tfvars`.
3. Use secrets in `CfnParameter` without `NoEcho: true`.

The agent **MUST**:

1. Create the `aws_secretsmanager_secret` resource via IaC; populate the **value** outside IaC (via CLI, authorized pipeline step).
2. Reference secrets at runtime (`secretsmanager_secret_version.arn`); do not return the value as an output.

### 9. Critical resources with delete protection

Stateful or critical resources **MUST** have protection:

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

## Applicability

- **Applies to:** all AWS infrastructure in all environments
- **Bound agents:** `warrior-atlas`, DevOps agents
- **Exceptions:**
  - Experimental resources in a sandbox account may be manual, if they do not persist data and are destroyed within 7 days
  - Read-only console actions for investigation (no state change)

## Consequences of Violation

1. **Invisible drift:** real environment differs from code; deploys fail or surprise
2. **Loss of knowledge:** manual change disappears when the person leaves; impossible to reproduce
3. **Compliance failure:** SOC 2, ISO 27001 require a change trail; unlogged console access is a failed audit
4. **Remediation:**
   - Run `terraform plan` to detect drift; import or adjust code
   - Apply SCPs restricting manual changes in production
   - Audit CloudTrail to detect who made recent manual changes

## Automated Validation

- **Tools:**
  - **Linting:** `terraform fmt`, `terraform validate`, `tflint`
  - **Plan on PRs:** `atlantis`, GitHub Actions, CodeBuild
  - **Drift:** cronjob with `terraform plan` in production alerting on diffs
  - **Policy:** OPA/Sentinel for organizational rules (e.g., "every S3 must have encryption")
- **When:** every PR; daily (drift); CI/CD pipeline
- **Metric:** 100% of resources in IaC; 0 unresolved drift >24h

## References

- `lex-aws-security` — security as part of IaC
- `lex-aws-cost` — tagging for cost allocation
- `codex-aws-well-architected` — Operational Excellence Pillar
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS CDK Best Practices](https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html)
